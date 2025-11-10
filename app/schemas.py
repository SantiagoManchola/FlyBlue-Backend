
from pydantic import BaseModel, EmailStr
from datetime import datetime

class VueloResponse(BaseModel):
    id: int
    codigo: str
    fecha_salida: datetime
    fecha_llegada: datetime
    ciudad_salida: str
    ciudad_llegada: str
    precio_base: float
    asientos_totales: int
    asientos_disponibles: int
    model_config = {"from_attributes": True}

class AsientoResponse(BaseModel):
    id_asiento: int
    id_vuelo: int
    fila: int
    columna: str
    disponible: bool
    model_config = {"from_attributes": True}

class AsientosResponse(BaseModel):
    asientos: list['AsientoResponse']
    model_config = {"from_attributes": True}

class EquipajeResponse(BaseModel):
    id_equipaje: int
    tipo: str
    precio: float
    descripcion: str
    peso_maximo: int
    model_config = {"from_attributes": True}

class CiudadResponse(BaseModel):
    id_ciudad: int
    nombre: str
    codigo: str
    model_config = {"from_attributes": True}

class VueloBusquedaResponse(BaseModel):
    id_vuelo: int
    codigo: str
    fecha_salida: datetime
    fecha_llegada: datetime
    precio_base: float
    model_config = {"from_attributes": True}

class UsuarioBase(BaseModel):
    correo: EmailStr

class UsuarioCreate(UsuarioBase):
    nombre: str
    correo: EmailStr
    contraseña: str

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    nombre: str
    model_config = {"from_attributes": True}

class LoginRequest(BaseModel):
    correo: str
    contraseña: str

class LoginResponse(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    token: str

class ReservaRequest(BaseModel):
    id_usuario: int
    id_vuelo: int
    id_asiento: int
    id_equipaje: int
    model_config = {"from_attributes": True}

class ReservaResponse(BaseModel):
    id_reserva: int
    vuelo: str
    fecha_salida: datetime
    total: float
    model_config = {"from_attributes": True}

class CiudadCreate(BaseModel):
    nombre: str
    codigo: str

class EquipajeCreate(BaseModel):
    tipo: str
    precio: float
    descripcion: str
    peso_maximo: int

class VueloCreate(BaseModel):
    id_origen: int
    id_destino: int
    fecha_salida: datetime
    fecha_llegada: datetime
    precio_base: float