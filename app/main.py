from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal, get_db, create_tables
from app.models import *
from app.routers import api_v1
#from app.schemas 
import time

# Crear tablas al iniciar la aplicación
create_tables()

app = FastAPI(
    title="API Sistema de Vuelos",
    version="1.0",
    description="API con prefijo /v1 y routers modulares"
)


app.include_router(api_v1)

@app.get("/")
def read_root():
    return {"mensaje": "up"}

