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