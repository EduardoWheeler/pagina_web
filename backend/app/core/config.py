from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] es la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    # Sin valores por defecto para credenciales: se leen de .env o del entorno
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str = "db_artista"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def _validate_secret_key(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError(
                "SECRET_KEY debe tener al menos 32 caracteres. "
                'Genérala con: python -c "import secrets; print(secrets.token_hex(32))"'
            )
        return value

settings = Settings()  # type: ignore[call-arg]
