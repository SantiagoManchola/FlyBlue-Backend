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
async def crear_vuelo(vuelo: VueloCreate, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_admin)):
    ciudad_origen = await crud.get_ciudad_by_id(db, ciudad_id=vuelo.id_origen)
    ciudad_destino = await crud.get_ciudad_by_id(db, ciudad_id=vuelo.id_destino)
    if not ciudad_origen or not ciudad_destino:
        raise HTTPException(status_code=404, detail="Ciudad de origen o destino no encontrada")

    codigo = f"{ciudad_origen.codigo}-{ciudad_destino.codigo}-{vuelo.fecha_salida.strftime('%Y%m%d')}"

    # se crea un nuevo objeto VueloCreate que incluya el código, aunque el schema no lo pida
    # Mejor aún, modificamos crud.create_vuelo para aceptar el código

    # --- Modificación a crud.create_vuelo ---
    # Mas bien, Por simplicidad, lo asignaré al modelo VueloCreate (aunque no esté en el schema)
    # Una mejor práctica sería tener 'codigo' en VueloCreate pero opcional

    nuevo_vuelo_data = vuelo.dict()
    nuevo_vuelo_data['codigo'] = codigo

    # Aqui vuelvo a crear el objeto Vuelo con el código
    # Esto es un hack. Lo ideal sería que VueloCreate acepte 'codigo' o que crud.create_vuelo lo acepte.
    # Vamos a asumir que models.Vuelo acepta los campos

    nuevo_vuelo = models.Vuelo(
        codigo=codigo,
        id_origen=vuelo.id_origen,
        id_destino=vuelo.id_destino,
        fecha_salida=vuelo.fecha_salida.replace(tzinfo=None),
        fecha_llegada=vuelo.fecha_llegada.replace(tzinfo=None),
        precio_base=vuelo.precio_base
    )
    db.add(nuevo_vuelo)
    await db.commit()
    await db.refresh(nuevo_vuelo)

    return {
        "message": "Vuelo creado exitosamente",
        "id_vuelo": nuevo_vuelo.id_vuelo,
        "codigo": nuevo_vuelo.codigo,
        "precio_base": float(nuevo_vuelo.precio_base)
    }