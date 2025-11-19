from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Usuario
from app.schemas import CiudadCreate, EquipajeCreate, VueloCreate
from app.security import require_admin
from app import crud, models

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/ciudades")
async def crear_ciudad(ciudad: CiudadCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    nueva_ciudad = await crud.create_ciudad(db, ciudad=ciudad)
    return {
        "message": "Ciudad creada exitosamente",
        "id_ciudad": nueva_ciudad.id_ciudad,
        "nombre": nueva_ciudad.nombre,
        "codigo": nueva_ciudad.codigo
    }

@router.post("/equipajes")
async def crear_equipaje(equipaje: EquipajeCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    nuevo_equipaje = await crud.create_equipaje(db, equipaje=equipaje)
    return {
        "message": "Equipaje creado exitosamente",
        "id_equipaje": nuevo_equipaje.id_equipaje,
        "tipo": nuevo_equipaje.tipo,
        "descripcion": nuevo_equipaje.descripcion,
        "peso_maximo": nuevo_equipaje.peso_maximo,
        "precio": float(nuevo_equipaje.precio),
    }

@router.post("/vuelos")
async def crear_vuelo(
    vuelo: VueloCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Usuario = Depends(require_admin)
):
    # 1. Validar ciudades
    ciudad_origen = await crud.get_ciudad_by_id(db, ciudad_id=vuelo.id_origen)
    ciudad_destino = await crud.get_ciudad_by_id(db, ciudad_id=vuelo.id_destino)
    
    if not ciudad_origen or not ciudad_destino:
        raise HTTPException(status_code=404, detail="Ciudad de origen o destino no encontrada")

    # 2. Generar código de vuelo
    codigo = f"{ciudad_origen.codigo}-{ciudad_destino.codigo}-{vuelo.fecha_salida.strftime('%Y%m%d')}"

    # 3. Crear instancia del Vuelo
    nuevo_vuelo = models.Vuelo(
        codigo=codigo,
        id_origen=vuelo.id_origen,
        id_destino=vuelo.id_destino,
        fecha_salida=vuelo.fecha_salida.replace(tzinfo=None),
        fecha_llegada=vuelo.fecha_llegada.replace(tzinfo=None),
        precio_base=vuelo.precio_base
    )
    
    db.add(nuevo_vuelo)
    
    # ⚠️ IMPORTANTE: Usamos flush() para que la BD asigne el id_vuelo 
    # sin cerrar la transacción todavía.
    await db.flush() 

    # 4. Generar los 60 asientos (12 filas x 5 columnas)
    asientos_lista = []
    columnas_validas = ['A', 'B', 'C', 'D', 'E']
    total_filas = 20  # 20 * 5 = 100 asientos

    for numero_fila in range(1, total_filas + 1):
        for letra_columna in columnas_validas:
            nuevo_asiento = models.Asiento(
                id_vuelo=nuevo_vuelo.id_vuelo, # Usamos el ID recién generado
                fila=numero_fila,
                columna=letra_columna,
                disponible=True
            )
            asientos_lista.append(nuevo_asiento)

    # 5. Añadir todos los asientos a la sesión de golpe
    db.add_all(asientos_lista)

    # 6. Confirmar todo (Vuelo + 60 Asientos) en una sola transacción
    await db.commit()
    await db.refresh(nuevo_vuelo)

    return {
        "message": f"Vuelo creado exitosamente con {len(asientos_lista)} asientos.",
        "id_vuelo": nuevo_vuelo.id_vuelo,
        "codigo": nuevo_vuelo.codigo,
        "precio_base": float(nuevo_vuelo.precio_base)
    }