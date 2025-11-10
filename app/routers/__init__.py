# app/routers/__init__.py
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Usuario, Vuelo, Asiento, Ciudad, Equipaje
from app.schemas import VueloResponse, AsientosResponse, EquipajeResponse, CiudadResponse, VueloBusquedaResponse
from app.security import require_user
from datetime import datetime
from app import crud

from app.routers import admin, cliente, auth

api_v1 = APIRouter(prefix="/v1")

# Incluir los routers modulares
api_v1.include_router(admin.router)
api_v1.include_router(cliente.router)
api_v1.include_router(auth.router)

# --- Endpoints Públicos (requieren autenticación de usuario) ---

@api_v1.get("/vuelos/{id_vuelo}", response_model=VueloResponse)
async def obtener_vuelo_por_id(id_vuelo: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    vuelo = await crud.get_vuelo_by_id(db, vuelo_id=id_vuelo)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")

    asientos_totales = await crud.count_total_asientos(db, id_vuelo=id_vuelo)
    asientos_disponibles = await crud.count_asientos_disponibles(db, id_vuelo=id_vuelo)

    return VueloResponse(
        id=vuelo.id_vuelo,
        codigo=vuelo.codigo,
        fecha_salida=vuelo.fecha_salida,
        fecha_llegada=vuelo.fecha_llegada,
        ciudad_salida=vuelo.origen.nombre if vuelo.origen else "Desconocida",
        ciudad_llegada=vuelo.destino.nombre if vuelo.destino else "Desconocida",
        precio_base=float(vuelo.precio_base),
        asientos_totales=asientos_totales,
        asientos_disponibles=asientos_disponibles,
    )

@api_v1.get("/vuelos/{id_vuelo}/asientos", response_model=AsientosResponse)
async def obtener_asientos_por_id_vuelo(id_vuelo: int, db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    vuelo = await crud.get_vuelo_by_id(db, vuelo_id=id_vuelo)
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")

    asientos = await crud.get_asientos_by_vuelo_id(db, vuelo_id=id_vuelo)
    return AsientosResponse(asientos=asientos)

@api_v1.get("/equipajes", response_model=list[EquipajeResponse])
async def obtener_equipajes(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    equipajes = await crud.get_all_equipajes(db)
    if not equipajes:
        raise HTTPException(status_code=404, detail="Equipaje no encontrado")
    return equipajes

@api_v1.get("/ciudades", response_model=list[CiudadResponse])
async def obtener_ciudades(db: AsyncSession = Depends(get_db), current_user: Usuario = Depends(require_user)):
    ciudades = await crud.get_all_ciudades(db)
    if not ciudades:
        raise HTTPException(status_code=404, detail="No se encontraron ciudades")
    return ciudades

@api_v1.get("/vuelos", response_model=list[VueloBusquedaResponse])
async def buscar_vuelos(
        origen: int = Query(..., description="ID de la ciudad de origen"),
        destino: int = Query(..., description="ID de la ciudad de destino"),
        fecha: datetime = Query(..., description="Fecha de salida (YYYY-MM-DD)"),
        db: AsyncSession = Depends(get_db),
        current_user: Usuario = Depends(require_user)
):
    vuelos = await crud.search_vuelos(db, origen_id=origen, destino_id=destino, fecha=fecha)
    return vuelos