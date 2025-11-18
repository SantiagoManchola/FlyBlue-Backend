from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import engine
from app.models import Base
from app.routers import api_v1
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Al iniciar: Conectar y crear tablas
    print("Iniciando aplicación y conectando a la base de datos...")
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Descomentar solo para pruebas
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas/verificadas.")
    yield
    # Al apagar: (opcional)
    print("Aplicación apagándose.")

app = FastAPI(
    title="API Sistema de Vuelos (FlyBlue)",
    version="1.0.0",
    description="API asíncrona para gestionar reservas de vuelos.",
    lifespan=lifespan
)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Permite todos los orígenes
    allow_credentials=True,    # Permite cookies/autenticación
    allow_methods=["*"],         # Permite todos los métodos (GET, POST, PUT, etc.)
    allow_headers=["*"],         # Permite todos los encabezados (incluyendo Authorization)
)

# Incluir todos los routers de /v1
app.include_router(api_v1)

@app.get("/")
def read_root():
    return {"mensaje": "API de FlyBlue está activa", "status": "200"}

@app.get("/qwert")
def read_root():
    return {"mensaje": "flujo CI/CD 100% funcioanl OSTOS yea jajaj YEAH", "status": "200"}