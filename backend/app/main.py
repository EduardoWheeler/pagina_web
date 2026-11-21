import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.core.exceptions import CustomHTTPException
from backend.app.database.session import engine
from backend.app.models import models
from backend.app.routers import artists, auth, posts

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portal de Artistas - db_artista", version="1.1.0")

# No hay CORS: el frontend se sirve desde este mismo origen y las rutas del JS son relativas.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    return response

app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

app.include_router(auth.router)
app.include_router(artists.router)
app.include_router(posts.router)

@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/dashboard", response_class=HTMLResponse)
def read_dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/profile", response_class=HTMLResponse)
def read_profile(request: Request):
    return templates.TemplateResponse(request, "profile.html")
