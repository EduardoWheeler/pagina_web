from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Artist, Register
from backend.app.schemas.schemas import UserCreate, UserLogin, UserResponse
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.core.exceptions import (
    CustomHTTPException,
    DatabaseTransactionError,
    UnauthorizedError,
    ValidationError,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_artist(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_register = db.query(Register).filter(Register.email == user_data.email).first()
    if existing_register:
        raise ValidationError("El correo electrónico ya está registrado.")
    
    try:
        hashed_pwd = hash_password(user_data.password)
        new_register = Register(
            email=user_data.email,
            hashed_password=hashed_pwd
        )
        db.add(new_register)
        db.flush()
        
        new_artist = Artist(
            name=user_data.name,
            register_id=new_register.id
        )
        db.add(new_artist)
        db.commit()
        db.refresh(new_artist)
        
        return {
            "id": new_artist.id,
            "name": new_artist.name,
            "email": new_register.email
        }
    except CustomHTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise DatabaseTransactionError("Error al registrar el usuario en la base de datos.")

@router.post("/login", status_code=status.HTTP_200_OK)
def login_artist(credentials: UserLogin, db: Session = Depends(get_db)):
    register_record = db.query(Register).filter(Register.email == credentials.email).first()
    if not register_record or not verify_password(credentials.password, register_record.hashed_password):
        raise UnauthorizedError("Correo electrónico o contraseña incorrectos.")
    
    artist = db.query(Artist).filter(Artist.register_id == register_record.id).first()
    if not artist:
        try:
            artist = Artist(
                name=register_record.email.split("@")[0],
                register_id=register_record.id
            )
            db.add(artist)
            db.commit()
            db.refresh(artist)
        except Exception:
            db.rollback()
            raise DatabaseTransactionError("Error al asociar el perfil de artista.")
    
    access_token = create_access_token(data={"sub": register_record.email, "artist_id": artist.id})
    
    return {
        "message": "Inicio de sesión exitoso",
        "access_token": access_token,
        "token_type": "bearer",
        "id": artist.id,
        "name": artist.name
    }
