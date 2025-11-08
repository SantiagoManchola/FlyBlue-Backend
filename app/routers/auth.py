from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.utils.security import hash_password, verify_password
from app.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, LoginResponse
from app.models import Usuario
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/registro")
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    # 1. Validar si el correo ya existe
    existente = db.query(Usuario).filter(Usuario.correo == usuario.correo).first()
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # 2. Crear el usuario con la contraseña encriptada
    hashed_password = hash_password(usuario.contraseña)
    nuevo_usuario = Usuario(
        nombre=usuario.nombre,
        correo=usuario.correo,
        contraseña=hashed_password,
        rol=usuario.rol
    )

    # 3. Guardar en la base de datos
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {"message": "Usuario registrado exitosamente"}

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Buscar el usuario por correo
    usuario = db.query(Usuario).filter(Usuario.correo == request.correo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    # Verificar la contraseña
    if not verify_password(request.contraseña, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Si todo está bien, devolver datos básicos
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "rol": usuario.rol
    }
