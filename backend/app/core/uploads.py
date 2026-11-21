"""Guardado seguro de imágenes: formato verificado por bytes, nombre generado por el servidor."""
import uuid
from pathlib import Path

from fastapi import UploadFile

from backend.app.core.exceptions import FileTooLargeError, ValidationError

MAX_BYTES = 5 * 1024 * 1024  # 5 MB

def detect_extension(data: bytes) -> str | None:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"
    return None

def save_image(upload: UploadFile, directory: Path, prefix: str, label: str = "La imagen") -> str:
    """Valida y guarda la imagen. Devuelve el nombre de archivo generado."""
    data = upload.file.read(MAX_BYTES + 1)
    if not data:
        raise ValidationError(f"{label} está vacío.")
    if len(data) > MAX_BYTES:
        raise FileTooLargeError(f"{label} supera el máximo de {MAX_BYTES // (1024 * 1024)} MB.")
    extension = detect_extension(data)
    if extension is None:
        raise ValidationError(f"{label} debe ser una imagen PNG, JPG o WEBP.")

    directory.mkdir(parents=True, exist_ok=True)
    name = f"{prefix}_{uuid.uuid4().hex}{extension}"
    (directory / name).write_bytes(data)
    return name

def delete_static_file(url: str | None, url_prefix: str, directory: Path) -> None:
    """Borra un archivo propio a partir de su URL, solo si está dentro de `directory`."""
    if not url or not url.startswith(url_prefix):
        return
    root = directory.resolve()
    target = (root / url[len(url_prefix):]).resolve()
    if root in target.parents:
        target.unlink(missing_ok=True)
