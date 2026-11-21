from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class ArtistUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    bio: Optional[str] = Field(None, max_length=2000)
    avatar: Optional[str] = None
    redes: Optional[str] = Field(None, max_length=500)
    links: Optional[str] = Field(None, max_length=500)
    model_config = ConfigDict(from_attributes=True)

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)

class PublicationCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    publication_type: str = Field(..., min_length=2, max_length=50)
    genre_programming: Optional[str] = Field(None, max_length=50)
    cover_image: Optional[str] = None
    gallery_images: Optional[str] = None
    tag_ids: Optional[List[int]] = []

class PublicationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    publication_type: str
    genre_programming: Optional[str] = None
    cover_image: Optional[str] = None
    gallery_images: Optional[str] = None
    artist_id: int
    created_at: datetime
    tags: List[TagResponse] = []
    model_config = ConfigDict(from_attributes=True)

class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
    data: List[dict]