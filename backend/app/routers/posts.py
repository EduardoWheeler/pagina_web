import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.app.core.deps import CurrentArtist
from backend.app.core.exceptions import (
    CustomHTTPException,
    DatabaseTransactionError,
    NotFoundError,
    ValidationError,
)
from backend.app.core.uploads import delete_static_file, save_image
from backend.app.database.session import get_db
from backend.app.models.models import Publication, Tag
from backend.app.schemas.schemas import PublicationResponse

router = APIRouter(prefix="/posts", tags=["Publications"])

BASE_DIR = Path(__file__).resolve().parents[3]
POSTS_MEDIA_DIR = BASE_DIR / "frontend" / "static" / "uploads"
MEDIA_URL_PREFIX = "/static/uploads/"
MAX_GALLERY_FILES = 10
POSTS_MEDIA_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/", response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
def create_publication(
    current: CurrentArtist,
    title: str = Form(..., min_length=2, max_length=200),
    publication_type: str = Form(..., min_length=2, max_length=50),
    description: Optional[str] = Form(None, max_length=5000),
    genre_programming: Optional[str] = Form(None, max_length=50),
    tag_ids: Optional[str] = Form(None),
    cover: Optional[UploadFile] = File(None),
    gallery: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
):
    # El autor es SIEMPRE el artista autenticado (nunca un id enviado por el cliente).
    gallery_files = [f for f in (gallery or []) if f.filename]
    if len(gallery_files) > MAX_GALLERY_FILES:
        raise ValidationError(f"La galería admite como máximo {MAX_GALLERY_FILES} imágenes.")

    saved: list[str] = []  # URLs escritas; se borran si algo falla
    try:
        cover_url = None
        if cover is not None and cover.filename:
            name = save_image(cover, POSTS_MEDIA_DIR, f"cover_{current.id}", label="La portada")
            cover_url = f"{MEDIA_URL_PREFIX}{name}"
            saved.append(cover_url)

        gallery_urls = []
        for index, item in enumerate(gallery_files, start=1):
            name = save_image(item, POSTS_MEDIA_DIR, f"gal_{current.id}", label=f"La imagen {index} de la galería")
            url = f"{MEDIA_URL_PREFIX}{name}"
            gallery_urls.append(url)
            saved.append(url)

        publication = Publication(
            title=title.strip(),
            description=(description or "").strip() or None,
            publication_type=publication_type.strip(),
            genre_programming=(genre_programming or "").strip() or None,
            cover_image=cover_url,
            gallery_images=json.dumps(gallery_urls) if gallery_urls else None,
            artist_id=current.id,
        )

        if tag_ids:
            try:
                parsed = json.loads(tag_ids)
                ids = [int(i) for i in parsed] if isinstance(parsed, list) else []
            except (ValueError, TypeError):
                raise ValidationError("tag_ids debe ser una lista JSON de enteros.")
            if ids:
                publication.tags = db.query(Tag).filter(Tag.id.in_(ids)).all()

        db.add(publication)
        db.commit()
        db.refresh(publication)
        return publication
    except CustomHTTPException:
        db.rollback()
        for url in saved:
            delete_static_file(url, MEDIA_URL_PREFIX, POSTS_MEDIA_DIR)
        raise
    except Exception:
        db.rollback()
        for url in saved:
            delete_static_file(url, MEDIA_URL_PREFIX, POSTS_MEDIA_DIR)
        raise DatabaseTransactionError("Error al crear la publicación en la base de datos.")

@router.get("/", response_model=List[PublicationResponse])
def get_all_publications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    publication_type: Optional[str] = Query(None, max_length=50),
    genre_programming: Optional[str] = Query(None, max_length=50),
    search: Optional[str] = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    query = db.query(Publication)

    if publication_type:
        query = query.filter(Publication.publication_type == publication_type)
    if genre_programming:
        query = query.filter(Publication.genre_programming == genre_programming)
    if search:
        # autoescape: los caracteres % y _ del usuario se tratan como texto literal
        query = query.filter(
            Publication.title.icontains(search, autoescape=True)
            | Publication.description.icontains(search, autoescape=True)
        )

    return (
        query.order_by(Publication.created_at.desc(), Publication.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@router.get("/{publication_id}", response_model=PublicationResponse)
def get_publication(publication_id: int, db: Session = Depends(get_db)):
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise NotFoundError("Publicación no encontrada.")
    return publication
