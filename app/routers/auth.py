from fastapi import APIRouter, HTTPException, Depends
from app.database import get_db
from app.utils.security import verify_password
from app.schemas import UsuarioCreate, UsuarioResponse, LoginRequest, LoginResponse
from app.models import Usuario
from app.security import create_access_token, require_user
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register")
async def registrar_usuario(usuario: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    existente = await crud.get_user_by_email(db, email=usuario.correo)
    if existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    await crud.create_user(db, usuario=usuario)
    return {"message": "Usuario registrado exitosamente"}

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    usuario = await crud.get_user_by_email(db, email=request.correo)
    if not usuario:
        raise HTTPException(status_code=404, detail="Correo no registrado")

    if not verify_password(request.contraseña, usuario.contraseña):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    access_token = create_access_token(data={"sub": str(usuario.id_usuario), "rol": usuario.rol})

    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "token": access_token
    }

@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_profile(current_user: Usuario = Depends(require_user)):
    return {
        "id_usuario": current_user.id_usuario,
        "nombre": current_user.nombre,
        "correo": current_user.correo
    }