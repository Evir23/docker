from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pages.auth import router as auth_pages_router
from auth.router import router as auth_router
from auth.models import create_tables
from fastapi.middleware.cors import CORSMiddleware
from pages.dashboard import router as dashboard_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем маршруты из других файлов
app.include_router(auth_pages_router)
app.include_router(auth_router)
app.include_router(dashboard_router)

# Маршрут для стартовой страницы
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    await create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

