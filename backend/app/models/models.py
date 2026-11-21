from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Index, DateTime
from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

publication_tags = Table(
    "publication_tags",
    Base.metadata,
    Column("publication_id", Integer, ForeignKey("publications.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class Register(Base):
    __tablename__ = "registers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    artist = relationship("Artist", back_populates="register", uselist=False, cascade="all, delete-orphan")

class Artist(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False, index=True)
    bio = Column(Text, nullable=True)
    avatar = Column(String(255), nullable=True)
    redes = Column(Text, nullable=True)
    links = Column(Text, nullable=True)
    register_id = Column(Integer, ForeignKey("registers.id", ondelete="CASCADE"), unique=True, nullable=False)
    register = relationship("Register", back_populates="artist")
    publications = relationship("Publication", back_populates="artist", cascade="all, delete-orphan")

class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    publication_type = Column(String(50), nullable=False, index=True)
    genre_programming = Column(String(50), nullable=True, index=True)
    cover_image = Column(String(255), nullable=True)
    gallery_images = Column(Text, nullable=True)
    artist_id = Column(Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    artist = relationship("Artist", back_populates="publications")
    tags = relationship("Tag", secondary=publication_tags, back_populates="publications")
    
    __table_args__ = (
        Index('idx_type_genre', 'publication_type', 'genre_programming'),
    )

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    publications = relationship("Publication", secondary=publication_tags, back_populates="tags")