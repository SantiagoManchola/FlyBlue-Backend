from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.schemas import ReservaRequest, ReservaResponse
from app.models import Usuario
from app.security import require_user
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud

router = APIRouter(
    prefix="/cliente",
    tags=["cliente"]
)

@router.post("/reservas")
async def crear_reserva(reserva: ReservaRequest, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    # Verificar que el usuario solo pueda crear reservas para sí mismo
    if current_user.rol != "admin" and current_user.id_usuario != reserva.id_usuario:
        raise HTTPException(status_code=403, detail="No puedes crear reservas para otro usuario")

    vuelo = await crud.get_vuelo_by_id(db, vuelo_id=reserva.id_vuelo)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")

    asiento = await crud.get_asiento_by_id(db, asiento_id=reserva.id_asiento)
    if not asiento or not asiento.disponible:
        raise HTTPException(status_code=400, detail="Asiento no disponible")

    equipaje = await crud.get_equipaje_by_id(db, equipaje_id=reserva.id_equipaje)
    if not equipaje:
        raise HTTPException(status_code=404, detail="Equipaje no encontrado")

    total = float(vuelo.precio_base) + float(equipaje.precio)

    nueva_reserva = await crud.create_reserva(db, reserva=reserva, total=total)

    return {"message": "reserva creada exitosamente", "id_reserva": nueva_reserva.id_reserva}

@router.get("/reservas/{id_usuario}", response_model=list[ReservaResponse])
async def obtener_reservas(id_usuario: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    if current_user.rol != "admin" and current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No puedes ver reservas de otro usuario")

    reservas_db = await crud.get_reservas_by_user_id(db, usuario_id=id_usuario)
    if not reservas_db:
        raise HTTPException(status_code=404, detail="No se encontraron reservas para este usuario")

    # Formatear la respuesta
    reservas = []
    for r in reservas_db:
        vuelo_str = f"{r.vuelo.origen.codigo}-{r.vuelo.destino.codigo}-{r.vuelo.fecha_salida.strftime('%Y-%m-%d %H:%M')}"
        reservas.append(
            ReservaResponse(
                id_reserva=r.id_reserva,
                vuelo=vuelo_str,
                fecha_salida=r.vuelo.fecha_salida,
                total=float(r.total)
            )
        )
    return reservas

@router.post("/reservas/{reserva_id}/pago")
async def procesar_pago(reserva_id: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    reserva = await crud.get_reserva_by_id_and_user(db, reserva_id=reserva_id, usuario_id=current_user.id_usuario)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada o no pertenece al usuario")

    if reserva.pago:
        raise HTTPException(status_code=400, detail="El pago ya ha sido registrado para esta reserva")

    pago = await crud.create_pago(db, reserva=reserva)
    return {"message": f"Pago procesado exitosamente para la reserva {reserva_id}", "id_pago": pago.id_pago}