from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.deps import CurrentArtist
from backend.app.core.exceptions import (
    DatabaseTransactionError,
    ForbiddenError,
    NotFoundError,
)
from backend.app.core.uploads import delete_static_file, save_image
from backend.app.database.session import get_db
from backend.app.models.models import Artist, Publication
from backend.app.schemas.schemas import ArtistUpdate

router = APIRouter(prefix="/artists", tags=["Artists"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "frontend" / "static" / "avatars"
AVATAR_URL_PREFIX = "/static/avatars/"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _public(artist: Artist) -> dict:
    """Datos públicos: nunca se expone el correo electrónico."""
    return {
        "id": artist.id,
        "name": artist.name,
        "bio": artist.bio,
        "avatar": artist.avatar,
        "redes": artist.redes,
        "links": artist.links,
    }

def _ensure_owner(current: Artist, artist_id: int) -> None:
    if current.id != artist_id:
        raise ForbiddenError("Solo puedes modificar tu propio perfil.")

@router.get("/", response_model=List[dict])
def get_all_artists(db: Session = Depends(get_db)):
    return [_public(a) for a in db.query(Artist).order_by(Artist.name, Artist.id).all()]

@router.get("/{artist_id}")
def get_artist_by_id(artist_id: int, db: Session = Depends(get_db)):
    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise NotFoundError("Artista no encontrado.")
    count = db.query(func.count(Publication.id)).filter(Publication.artist_id == artist_id).scalar() or 0
    return {**_public(artist), "publications_count": count}

@router.put("/{artist_id}/avatar", status_code=status.HTTP_200_OK)
def upload_artist_avatar(
    artist_id: int,
    current: CurrentArtist,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
):
    _ensure_owner(current, artist_id)
    previous = current.avatar
    file_name = save_image(file, UPLOAD_DIR, f"artist_{artist_id}", label="El avatar")
    new_url = f"{AVATAR_URL_PREFIX}{file_name}"

    try:
        current.avatar = new_url
        db.commit()
        db.refresh(current)
    except Exception:
        db.rollback()
        delete_static_file(new_url, AVATAR_URL_PREFIX, UPLOAD_DIR)
        raise DatabaseTransactionError("Error al actualizar la ruta del avatar en la base de datos.")

    delete_static_file(previous, AVATAR_URL_PREFIX, UPLOAD_DIR)  # solo tras confirmar el cambio
    return {"message": "Avatar actualizado exitosamente", "avatar": current.avatar}

@router.put("/{artist_id}", status_code=status.HTTP_200_OK)
def update_artist_profile(
    artist_id: int,
    profile_data: ArtistUpdate,
    current: CurrentArtist,
    db: Session = Depends(get_db),
):
    _ensure_owner(current, artist_id)

    if profile_data.name is not None:
        current.name = profile_data.name
    if profile_data.bio is not None:
        current.bio = profile_data.bio
    if profile_data.redes is not None:
        current.redes = profile_data.redes
    if profile_data.links is not None:
        current.links = profile_data.links

    try:
        db.commit()
        db.refresh(current)
    except Exception:
        db.rollback()
        raise DatabaseTransactionError("Error al actualizar el perfil en la base de datos.")

    return {"message": "Perfil actualizado exitosamente", **_public(current)}
