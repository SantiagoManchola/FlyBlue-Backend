from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("La contraseña debe ser una cadena de texto.")
    password = password.strip()  # eliminar espacios
    if password == "":
        raise ValueError("La contraseña no puede estar vacía.")
    
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)