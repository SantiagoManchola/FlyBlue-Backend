
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func
from app import models, schemas
from app.utils.security import hash_password
from datetime import datetime, timedelta


# --- Funciones de Auth ---

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.correo == email))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, usuario: schemas.UsuarioCreate):
    hashed_password = hash_password(usuario.contraseña)
    nuevo_usuario = models.Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        contraseña=hashed_password,
        rol="usuario"
    )
    db.add(nuevo_usuario)
    await db.commit()
    await db.refresh(nuevo_usuario)
    return nuevo_usuario
async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Usuario).filter(models.Usuario.id_usuario == user_id))
    return result.scalar_one_or_none()
# --- Funciones de Admin ---

async def create_ciudad(db: AsyncSession, ciudad: schemas.CiudadCreate):
    nueva_ciudad = models.Ciudad(**ciudad.dict())
    db.add(nueva_ciudad)
    await db.commit()
    await db.refresh(nueva_ciudad)
    return nueva_ciudad

async def create_equipaje(db: AsyncSession, equipaje: schemas.EquipajeCreate):
    nuevo_equipaje = models.Equipaje(**equipaje.dict())
    db.add(nuevo_equipaje)
    await db.commit()
    await db.refresh(nuevo_equipaje)
    return nuevo_equipaje

async def get_ciudad_by_id(db: AsyncSession, ciudad_id: int):
    result = await db.execute(select(models.Ciudad).filter(models.Ciudad.id_ciudad == ciudad_id))
    return result.scalar_one_or_none()

async def create_vuelo(db: AsyncSession, vuelo: schemas.VueloCreate):
    nuevo_vuelo = models.Vuelo(**vuelo.dict())
    db.add(nuevo_vuelo)
    await db.commit()
    await db.refresh(nuevo_vuelo)
    return nuevo_vuelo

# --- Funciones de Cliente/Públicas ---

async def get_vuelo_by_id(db: AsyncSession, vuelo_id: int):
    result = await db.execute(
        select(models.Vuelo)
        .options(selectinload(models.Vuelo.origen), selectinload(models.Vuelo.destino))
        .filter(models.Vuelo.id_vuelo == vuelo_id)
    )
    return result.scalar_one_or_none()

async def count_total_asientos(db: AsyncSession, vuelo_id: int):
    result = await db.execute(
        select(func.count(models.Asiento.id_asiento))
        .filter(models.Asiento.id_vuelo == vuelo_id)
    )
    return result.scalar_one()

async def count_asientos_disponibles(db: AsyncSession, vuelo_id: int):
    result = await db.execute(
        select(func.count(models.Asiento.id_asiento))
        .filter(models.Asiento.id_vuelo == vuelo_id, models.Asiento.disponible == True)
    )
    return result.scalar_one()

async def get_asientos_by_vuelo_id(db: AsyncSession, vuelo_id: int):
    result = await db.execute(select(models.Asiento).filter(models.Asiento.id_vuelo == vuelo_id))
    return result.scalars().all()

async def get_all_equipajes(db: AsyncSession):
    result = await db.execute(select(models.Equipaje))
    return result.scalars().all()

async def get_all_ciudades(db: AsyncSession):
    result = await db.execute(select(models.Ciudad))
    return result.scalars().all()

async def search_vuelos(db: AsyncSession, origen_id: int, destino_id: int, fecha: datetime):
    fecha_inicio = fecha.date()
    fecha_fin = fecha_inicio + timedelta(days=1)

    result = await db.execute(
        select(models.Vuelo)
        .filter(
            models.Vuelo.id_origen == origen_id,
            models.Vuelo.id_destino == destino_id,
            models.Vuelo.fecha_salida >= fecha_inicio,
            models.Vuelo.fecha_salida < fecha_fin
        )
    )
    return result.scalars().all()

async def get_asiento_by_id(db: AsyncSession, asiento_id: int):
    result = await db.execute(select(models.Asiento).filter(models.Asiento.id_asiento == asiento_id))
    return result.scalar_one_or_none()

async def get_equipaje_by_id(db: AsyncSession, equipaje_id: int):
    result = await db.execute(select(models.Equipaje).filter(models.Equipaje.id_equipaje == equipaje_id))
    return result.scalar_one_or_none()

async def create_reserva(db: AsyncSession, reserva: schemas.ReservaRequest, total: float):
    # Marcar asiento como no disponible
    asiento = await get_asiento_by_id(db, reserva.id_asiento)
    if asiento:
        asiento.disponible = False
        db.add(asiento)

    nueva_reserva = models.Reserva(
        id_usuario=reserva.id_usuario,
        id_vuelo=reserva.id_vuelo,
        id_asiento=reserva.id_asiento,
        id_equipaje=reserva.id_equipaje,
        total=total
    )
    db.add(nueva_reserva)
    await db.commit()
    await db.refresh(nueva_reserva)
    return nueva_reserva

async def get_reservas_by_user_id(db: AsyncSession, usuario_id: int):
    result = await db.execute(
        select(models.Reserva)
        .options(
            selectinload(models.Reserva.vuelo).selectinload(models.Vuelo.origen),
            selectinload(models.Reserva.vuelo).selectinload(models.Vuelo.destino)
        )
        .filter(models.Reserva.id_usuario == usuario_id)
    )
    return result.scalars().all()

async def get_reserva_by_id_and_user(db: AsyncSession, reserva_id: int, usuario_id: int):
    result = await db.execute(
        select(models.Reserva)
        .filter(
            models.Reserva.id_reserva == reserva_id,
            models.Reserva.id_usuario == usuario_id
        )
    )
    return result.scalar_one_or_none()

async def create_pago(db: AsyncSession, reserva: models.Reserva):
    pago = models.Pago(
        id_reserva=reserva.id_reserva,
        monto=float(reserva.total),
        estado="pagado",
        fecha=datetime.utcnow()
    )
    db.add(pago)
    await db.commit()
    await db.refresh(pago)
    return pago