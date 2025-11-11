from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import Usuario
from app.security.jwt_handler import verify_token
from app import crud

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: AsyncSession = Depends(get_db)):
    
    # 1. user_id_str ES UN STRING (ej: "1")
    user_id_str = verify_token(credentials.credentials)
    
    try:
        # 2. Convertir el ID a entero:
        user_id_int = int(user_id_str)
    except ValueError:
        # Si el token tiene un 'sub' que no es un número:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido (ID de usuario no válido)"
        )

    # 3. Pasamos el ID entero a la función del CRUD
    user = await crud.get_user_by_id(db, user_id=user_id_int)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

async def require_admin(current_user: Usuario = Depends(get_current_user)):
    if current_user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    return current_user

async def require_user(current_user: Usuario = Depends(get_current_user)):
    return current_user