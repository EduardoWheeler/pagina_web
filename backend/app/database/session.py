from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.app.core.config import settings

# URL.create escapa correctamente caracteres especiales en la contraseña
DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
    query={"charset": "utf8mb4"},
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependencia de FastAPI para la gestión de sesiones de base de datos."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
