from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Ciudad, Usuario, Equipaje, Vuelo
from app.schemas import CiudadCreate, EquipajeCreate, VueloCreate
from app.security import require_admin
from datetime import datetime

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/ciudades")
def crear_ciudad(ciudad: CiudadCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):

    # 2️⃣ Crear la ciudad
    nueva_ciudad = Ciudad(
        nombre=ciudad.nombre,
        codigo=ciudad.codigo
    )
    db.add(nueva_ciudad)
    db.commit()
    db.refresh(nueva_ciudad)

    return {
        "message": "Ciudad creada exitosamente",
        "id_ciudad": nueva_ciudad.id_ciudad,
        "nombre": nueva_ciudad.nombre,
        "codigo": nueva_ciudad.codigo
    }

@router.post("/equipajes")
def crear_equipaje(equipaje: EquipajeCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):

    # Crear equipaje
    nuevo_equipaje = Equipaje(tipo=equipaje.tipo, precio=equipaje.precio, descripcion=equipaje.descripcion, peso_maximo=equipaje.peso_maximo)
    db.add(nuevo_equipaje)
    db.commit()
    db.refresh(nuevo_equipaje)

    return {
        "message": "Equipaje creado exitosamente",
        "id_equipaje": nuevo_equipaje.id_equipaje,
        "tipo": nuevo_equipaje.tipo,
        "descripcion": nuevo_equipaje.descripcion,
        "peso_maximo": nuevo_equipaje.peso_maximo,
        "precio": float(nuevo_equipaje.precio),
    }

@router.post("/vuelos")
def crear_vuelo(vuelo: VueloCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(require_admin)):

    # Obtener ciudades
    ciudad_origen = db.query(Ciudad).filter(Ciudad.id_ciudad == vuelo.id_origen).first()
    ciudad_destino = db.query(Ciudad).filter(Ciudad.id_ciudad == vuelo.id_destino).first()
    if not ciudad_origen or not ciudad_destino:
        raise HTTPException(status_code=404, detail="Ciudad de origen o destino no encontrada")

    # Generar código automáticamente
    codigo = f"{ciudad_origen.codigo}-{ciudad_destino.codigo}-{vuelo.fecha_salida.strftime('%Y%m%d')}"

    # Crear vuelo
    nuevo_vuelo = Vuelo(
        codigo=codigo,
        id_origen=vuelo.id_origen,
        id_destino=vuelo.id_destino,
        fecha_salida=vuelo.fecha_salida,
        fecha_llegada=vuelo.fecha_llegada,
        precio_base=vuelo.precio_base
    )
    db.add(nuevo_vuelo)
    db.commit()
    db.refresh(nuevo_vuelo)

    return {
        "message": "Vuelo creado exitosamente",
        "id_vuelo": nuevo_vuelo.id_vuelo,
        "codigo": nuevo_vuelo.codigo,
        "precio_base": float(nuevo_vuelo.precio_base)
    }