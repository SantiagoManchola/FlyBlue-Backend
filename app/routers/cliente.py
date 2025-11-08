from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.schemas import ReservaRequest,ReservaResponse,UsuarioResponse
from app.models import *
from app.security import require_user
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(
    prefix="/cliente",
    tags=["cliente"]
)

@router.post("/reservas")
def crear_reserva(reserva: ReservaRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(require_user)):
    # Buscar vuelo
    vuelo = db.query(Vuelo).filter(Vuelo.id_vuelo == reserva.id_vuelo).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")

    # Buscar asiento
    asiento = db.query(Asiento).filter(Asiento.id_asiento == reserva.id_asiento).first()
    if not asiento or not asiento.disponible:
        raise HTTPException(status_code=400, detail="Asiento no disponible")

    # Buscar equipaje
    equipaje = db.query(Equipaje).filter(Equipaje.id_equipaje == reserva.id_equipaje).first()
    if not equipaje:
        raise HTTPException(status_code=404, detail="Equipaje no encontrado")

    # Calcular total
    total = float(vuelo.precio_base) + float(equipaje.precio)

    # Verificar que el usuario solo pueda crear reservas para sí mismo
    if current_user.rol != "admin" and current_user.id_usuario != reserva.id_usuario:
        raise HTTPException(status_code=403, detail="No puedes crear reservas para otro usuario")
    
    # Crear reserva
    nueva_reserva = Reserva(
        id_usuario=reserva.id_usuario,
        id_vuelo=reserva.id_vuelo,
        id_asiento=reserva.id_asiento,
        id_equipaje=reserva.id_equipaje,
        total=total
    )

    # Marcar asiento como no disponible
    asiento.disponible = False

    # Guardar en DB
    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)

    return {"message": "reserva creada exitosamente", "id_reserva": nueva_reserva.id_reserva}

@router.get("/reservas/{id_usuario}", response_model=list[ReservaResponse])
def obtener_reservas(id_usuario: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_user)):
    # Verificar que el usuario solo pueda ver sus propias reservas
    if current_user.rol != "admin" and current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No puedes ver reservas de otro usuario")
    
    reservas_db = db.query(Reserva).filter(Reserva.id_usuario == id_usuario).all()

    if not reservas_db:
        return HTTPException(status_code=404, detail="No se encontraron reservas para este usuario")

    reservas = []
    for r in reservas_db:
        vuelo = db.query(Vuelo).filter(Vuelo.id_vuelo == r.id_vuelo).first()
        origen = db.query(Ciudad).filter(Ciudad.id_ciudad == vuelo.id_origen).first()
        destino = db.query(Ciudad).filter(Ciudad.id_ciudad == vuelo.id_destino).first()
        vuelo_str = f"{origen.codigo}-{destino.codigo}-{vuelo.fecha_salida.strftime('%Y-%m-%d %H:%M')}"
        reservas.append(
            ReservaResponse(
                id_reserva=r.id_reserva,
                vuelo=vuelo_str,
                fecha_salida=vuelo.fecha_salida,
                total=float(r.total)
            )
        )

    return reservas

@router.post("/reservas/{reserva_id}/pago")
def procesar_pago(reserva_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_user)):
    reserva = db.query(Reserva).filter(
        Reserva.id_reserva == reserva_id,
        Reserva.id_usuario == current_user.id_usuario
    ).first()
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada o no pertenece al usuario")

    # Verificar si ya existe un pago
    if reserva.pago:
        raise HTTPException(status_code=400, detail="El pago ya ha sido registrado para esta reserva")

    # Simular procesamiento de pago
    pago = Pago(
        id_reserva=reserva.id_reserva,
        monto=float(reserva.total),   # convertir DECIMAL a float
        estado="pagado",             # aquí iría lógica real de pago
        fecha=datetime.utcnow()
    )

    db.add(pago)
    db.commit()
    db.refresh(pago)

    return {"message": f"Pago procesado exitosamente para la reserva {reserva_id}", "id_pago": pago.id_pago}
