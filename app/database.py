
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import ssl

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Función para detectar si estamos en Azure
def is_azure_environment():
    return DATABASE_URL and "postgres.database.azure.com" in DATABASE_URL

if is_azure_environment():
    # Configuración para Azure PostgreSQL con SSL (Obligatorio en Azure)
    print("MODO AZURE: Aplicando configuración SSL para la base de datos.")
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        connect_args={
            "ssl": ssl.create_default_context(cafile="/etc/ssl/certs/ca-certificates.crt")
        }
    )
else:
    # Configuración Local (sin SSL)
    print("MODO LOCAL: Usando conexión estándar.")
    engine = create_async_engine(DATABASE_URL, echo=True)

# Creamos la fábrica de sesiones asíncronas
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """
    Dependencia de FastAPI para obtener una sesión de BD asíncrona.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()