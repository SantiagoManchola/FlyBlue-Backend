from sqlalchemy import (Column,Integer,String,Boolean,DateTime,DECIMAL,ForeignKey,CheckConstraint)
from sqlalchemy.orm import relationship
from app.database import Base


# 1️⃣ USUARIO
class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contraseña = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("rol IN ('usuario', 'admin')"),
    )

    reservas = relationship("Reserva", back_populates="usuario", cascade="all, delete")


# 2️⃣ CIUDAD
class Ciudad(Base):
    __tablename__ = "ciudad"

    id_ciudad = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(10), nullable=False)

    vuelos_origen = relationship("Vuelo", foreign_keys="Vuelo.id_origen", back_populates="origen")
    vuelos_destino = relationship("Vuelo", foreign_keys="Vuelo.id_destino", back_populates="destino")


# 3️⃣ VUELO
class Vuelo(Base):
    __tablename__ = "vuelo"

    id_vuelo = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), nullable=False)
    id_origen = Column(Integer, ForeignKey("ciudad.id_ciudad", ondelete="CASCADE"), nullable=False)
    id_destino = Column(Integer, ForeignKey("ciudad.id_ciudad", ondelete="CASCADE"), nullable=False)
    fecha_salida = Column(DateTime, nullable=False)
    fecha_llegada = Column(DateTime, nullable=False)
    precio_base = Column(DECIMAL(10, 2), nullable=False)
    asientos_totales = Column(Integer, nullable=True)
    asientos_disponibles = Column(Integer, nullable=True)

    origen = relationship("Ciudad", foreign_keys=[id_origen], back_populates="vuelos_origen")
    destino = relationship("Ciudad", foreign_keys=[id_destino], back_populates="vuelos_destino")
    asientos = relationship("Asiento", back_populates="vuelo", cascade="all, delete")
    reservas = relationship("Reserva", back_populates="vuelo", cascade="all, delete")


# 4️⃣ ASIENTO
class Asiento(Base):
    __tablename__ = "asiento"

    id_asiento = Column(Integer, primary_key=True, index=True)
    id_vuelo = Column(Integer, ForeignKey("vuelo.id_vuelo", ondelete="CASCADE"), nullable=False)
    fila = Column(Integer, nullable=False)
    columna = Column(String(1), nullable=False)
    disponible = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("columna IN ('A', 'B', 'C', 'D', 'E')"),
    )

    vuelo = relationship("Vuelo", back_populates="asientos")
    reservas = relationship("Reserva", back_populates="asiento")


# 5️⃣ EQUIPAJE
class Equipaje(Base):
    __tablename__ = "equipaje"

    id_equipaje = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)
    precio = Column(DECIMAL(10, 2), nullable=False)
    descripcion = Column(String(20), nullable=False)
    peso_maximo = Column(Integer, nullable=False)
    

    reservas = relationship("Reserva", back_populates="equipaje")


# 6️⃣ RESERVA
class Reserva(Base):
    __tablename__ = "reserva"

    id_reserva = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario", ondelete="CASCADE"), nullable=False)
    id_vuelo = Column(Integer, ForeignKey("vuelo.id_vuelo", ondelete="CASCADE"), nullable=False)
    id_asiento = Column(Integer, ForeignKey("asiento.id_asiento", ondelete="SET NULL"))
    id_equipaje = Column(Integer, ForeignKey("equipaje.id_equipaje"))
    total = Column(DECIMAL(10, 2), nullable=False)

    usuario = relationship("Usuario", back_populates="reservas")
    vuelo = relationship("Vuelo", back_populates="reservas")
    asiento = relationship("Asiento", back_populates="reservas")
    equipaje = relationship("Equipaje", back_populates="reservas")
    pago = relationship("Pago", back_populates="reserva", cascade="all, delete", uselist=False)


# 7️⃣ PAGO
class Pago(Base):
    __tablename__ = "pago"

    id_pago = Column(Integer, primary_key=True, index=True)
    id_reserva = Column(Integer, ForeignKey("reserva.id_reserva", ondelete="CASCADE"), nullable=False)
    monto = Column(DECIMAL(10, 2), nullable=False)
    estado = Column(String(20), nullable=False)
    fecha = Column(DateTime)

    __table_args__ = (
        CheckConstraint("estado IN ('pagado', 'fallido')"),
    )

    reserva = relationship("Reserva", back_populates="pago")
