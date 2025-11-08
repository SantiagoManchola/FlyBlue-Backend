from fastapi import APIRouter
from fastapi import APIRouter, Query
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models import Ciudad, Usuario, Equipaje, Vuelo
from app.schemas import CiudadCreate, EquipajeCreate, VueloCreate
from datetime import datetime

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.post("/admin/ciudades")
def crear_ciudad(ciudad: CiudadCreate, id_usuario: int, db: Session = Depends(get_db)):
    # 1️⃣ Verificar que el usuario exista y sea admin
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")

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

@router.post("/admin/equipajes")
def crear_equipaje(equipaje: EquipajeCreate, id_usuario: int, db: Session = Depends(get_db)):
    # Verificar admin
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")

    # Crear equipaje
    nuevo_equipaje = Equipaje(tipo=equipaje.tipo, precio=equipaje.precio)
    db.add(nuevo_equipaje)
    db.commit()
    db.refresh(nuevo_equipaje)

    return {
        "message": "Equipaje creado exitosamente",
        "id_equipaje": nuevo_equipaje.id_equipaje,
        "tipo": nuevo_equipaje.tipo,
        "precio": float(nuevo_equipaje.precio)
    }

@router.post("/admin/vuelos")
def crear_vuelo(id_usuario: int, id_origen: int, id_destino: int, fecha_salida: datetime,
                 fecha_llegada: datetime, precio_base: float, db: Session = Depends(get_db)):
    # Verificar admin
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.rol != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos de administrador")

    # Obtener ciudades
    ciudad_origen = db.query(Ciudad).filter(Ciudad.id_ciudad == id_origen).first()
    ciudad_destino = db.query(Ciudad).filter(Ciudad.id_ciudad == id_destino).first()
    if not ciudad_origen or not ciudad_destino:
        raise HTTPException(status_code=404, detail="Ciudad de origen o destino no encontrada")

    # Generar código automáticamente
    codigo = f"{ciudad_origen.codigo}-{ciudad_destino.codigo}-{fecha_salida.strftime('%Y%m%d')}"

    # Crear vuelo
    nuevo_vuelo = Vuelo(
        codigo=codigo,
        id_origen=id_origen,
        id_destino=id_destino,
        fecha_salida=fecha_salida,
        fecha_llegada=fecha_llegada,
        precio_base=precio_base
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