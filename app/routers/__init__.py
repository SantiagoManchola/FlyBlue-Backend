from fastapi import APIRouter, Query
from app.routers import admin, cliente, auth
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db
from app.models import *
from app.schemas import *


api_v1 = APIRouter(prefix="/v1")


api_v1.include_router(admin.router)
api_v1.include_router(cliente.router)
api_v1.include_router(auth.router)

#Paths

@api_v1.get("/vuelos/{id_vuelo}")
def obtener_vuelo_por_id(id_vuelo: int, db: Session = Depends(get_db)):
    vuelo = db.query(Vuelo).filter(Vuelo.id_vuelo == id_vuelo).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")

   
    ciudad_origen = db.query(Ciudad).filter(Ciudad.id_ciudad == vuelo.id_origen).first()
    ciudad_destino = db.query(Ciudad).filter(Ciudad.id_ciudad == vuelo.id_destino).first()
    asientos_totales = contar_total_asientos(id_vuelo,db)
    asientos_disponibles = contar_asientos_disponibles(id_vuelo,db)
    #Revisar lo de asientos disponibles y totales en la base de datos
    return VueloResponse(
        id=vuelo.id_vuelo,
        codigo=vuelo.codigo,
        fecha_salida=vuelo.fecha_salida,
        fecha_llegada=vuelo.fecha_llegada,
        ciudad_salida=ciudad_origen.nombre if ciudad_origen else "Desconocida",
        ciudad_llegada=ciudad_destino.nombre if ciudad_destino else "Desconocida",
        precio_base=float(vuelo.precio_base),
        asientos_totales=asientos_totales,
        asientos_disponibles=asientos_disponibles,
    )

@api_v1.get("/{id_vuelo}/asientos",response_model=AsientosResponse)
def obtener_asientos_por_id_vuelo(id_vuelo: int, db: Session = Depends(get_db)):
    vuelo = db.query(Vuelo).filter(Vuelo.id_vuelo == id_vuelo).first()
    if not vuelo:
        raise HTTPException(status_code=404, detail="Vuelo no encontrado")
    
    asientos = db.query(Asiento).filter(Asiento.id_vuelo == id_vuelo).all()
    return AsientosResponse(asientos=asientos)


@api_v1.get("/equipajes",response_model=list[EquipajeResponse])
def obtener_equipajes(db: Session = Depends(get_db)):
    equipaje = db.query(Equipaje).all()
    if not equipaje:
        raise HTTPException(status_code=404, detail="Equipaje no encontrado")
    
    return equipaje

@api_v1.get("/ciudades",response_model=list[CiudadResponse])
def obtener_ciudades(db: Session = Depends(get_db)):
    ciudades = db.query(Ciudad).all()
    if not ciudades:
        raise HTTPException(status_code=404, detail="No se encontraron ciudades")
    
    return ciudades

@api_v1.get("/vuelos",response_model=list[VueloBusquedaResponse])
def buscar_vuelos(
    origen: int = Query(..., description="ID de la ciudad de origen"),
    destino: int = Query(..., description="ID de la ciudad de destino"),
    fecha: datetime = Query(..., description="Fecha de salida (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    # Filtrar vuelos que coincidan con origen, destino y fecha (solo el día)
    vuelos = (
        db.query(Vuelo)
        .filter(
            Vuelo.id_origen == origen,
            Vuelo.id_destino == destino,
            Vuelo.fecha_salida.between(f"{fecha.date()} 00:00:00", f"{fecha.date()} 23:59:59")
        )
        .all()
    )

    return vuelos

#Funciones auxiliares
def contar_total_asientos(id_vuelo: int,db: Session):
    return db.query(Asiento).filter(Asiento.id_vuelo == id_vuelo).count()
def contar_asientos_disponibles(id_vuelo: int,db: Session):
    return db.query(Asiento).filter(Asiento.id_vuelo == id_vuelo, Asiento.disponible == True).count()


