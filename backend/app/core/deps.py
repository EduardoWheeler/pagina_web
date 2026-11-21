"""Dependencias de FastAPI: sesión de BD y artista autenticado."""
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.exceptions import UnauthorizedError
from backend.app.core.security import verify_access_token
from backend.app.database.session import get_db
from backend.app.models.models import Artist, Register

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_artist(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Artist:
    if credentials is None:
        raise UnauthorizedError("Autenticación requerida.")

    payload = verify_access_token(credentials.credentials)
    email = payload.get("sub")
    if not email:
        raise UnauthorizedError("Token de acceso inválido.")

    artist = (
        db.query(Artist)
        .join(Register, Register.id == Artist.register_id)
        .filter(Register.email == email)
        .first()
    )
    if artist is None:
        raise UnauthorizedError("La cuenta asociada al token ya no existe.")
    return artist

CurrentArtist = Annotated[Artist, Depends(get_current_artist)]
