import re
import bcrypt
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import status
from backend.app.core.config import settings
from backend.app.core.exceptions import UnauthorizedError, ValidationError

def hash_password(password: str) -> str:
    if not validar_fortaleza_contrasena(password):
        raise ValidationError("La contraseña no cumple con los requisitos de seguridad mínimos.")
    pwd_bytes = password.encode('utf-8')
    if len(pwd_bytes) > 72:  # límite real de bcrypt
        raise ValidationError("La contraseña no puede superar los 72 bytes.")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except (ValueError, TypeError):
        return False

def validar_fortaleza_contrasena(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise UnauthorizedError("Token de acceso inválido o expirado.")
