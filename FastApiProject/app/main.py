from fastapi import FastAPI, Depends, HTTPException, Form, Request, status, UploadFile
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app import models, view, schemas, forms
import os
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

"""Настройка базы данных и создание движка SQLAlchemy,
который используется для подключения и взаимодействия с базой данных"""
DATABASE_URL = "sqlite:///image_share.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # Движок для взаимодействия с БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)  # Создание таблиц, описанных в моделях

app = FastAPI()  # Создаем экземпляр приложения FastAPI
templates = Jinja2Templates(directory="app/templates")  # Настройка шаблонизатора Jinja2 и установка пути
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")

UPLOAD_DIR = "uploads"  # Директория для хранения загруженных файлов
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.mount("/static", StaticFiles(directory="static"), name="static")

'''функции для создания и проверки токенов:'''

def get_db():
    """Генератор для управления сессиями базы данных"""
    db = SessionLocal()  # Создание новой сессии БД
    try:
        yield db
    finally:
        db.close()

def get_image_from_db(image_id: int, db: Session):
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    return image
'''зависимость для проверки аутентификации:'''
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})
    user = db.query(models.CustomUser).filter(models.CustomUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/login"})
    return user

# Главная страница
@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Этот декоратор регистрирует функцию home
        как обработчик GET-запросов для URL (/).
        Возвращает преобразованный HTML-шаблон"""
    return templates.TemplateResponse("home.html", {"request": request})

# Регистрация нового пользователя
@app.get("/reg", response_class=HTMLResponse)
async def register_form(request: Request) -> HTMLResponse:
    """      Преобразовывает страницу для регистрации пользователя"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/reg", response_class=HTMLResponse)
async def register_user(request: Request, username: str = Form(...), first_name: str = Form(...),
                        last_name: str = Form(...), email: str = Form(...), birth_date: str = Form(...),
                        password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    try:
        # Проверка совпадения паролей
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        # Создание нового пользователя
        user_data = schemas.UserCreate(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        birth_date=birth_date,
        password=password,
        confirm_password=confirm_password
        )
        view.create_user(db, user_data)
        db.commit()

        return templates.TemplateResponse("home.html", {"request": request, "message": "Вы успешно зарегистрировались!"})
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Список пользователей
@app.get("/list", response_class=HTMLResponse)
async def users_list(request: Request, db: Session = Depends(get_db),
                     current_user: models.CustomUser = Depends(get_current_user)) -> HTMLResponse:
    """
    Обработка GET-запроса на получение списка зарегистрированных пользователей.
    Возвращает список пользователей из базы данных.
    """
    users = view.get_users(db)  # Вызываем функцию для извлечения всех пользователей
    return templates.TemplateResponse("users_list.html", {"request": request, "users": users,
                                                          "current_user": current_user})

@app.get("/images", response_class=HTMLResponse)
async def view_images(request: Request, db: Session = Depends(get_db),
                    current_user: models.CustomUser = Depends(get_current_user)) -> HTMLResponse:
    images = view.get_images(db)
    logger.info(f"Current user: {current_user.username}")  # Логирование
    return templates.TemplateResponse(
    "images.html",
    {"request": request, "images": images, "current_user": current_user}
    )

@app.post("/upload_image")
async def upload_image(file: UploadFile, description: Optional[str] = Form(None), db: Session = Depends(get_db)):
    """Асинхронная функция-обработчик для запросов к конечной точке "/upload_image".
        Получает загруженный файл из данных формы и сессию базы данных."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)  # Создаем путь для сохранения картинки
    with open(file_path, "wb") as f:  # Считываем содержимое открытого файла и записываем данные в открытый файл
        f.write(await file.read())
        # Сохранение описания вместе с файлом
        image = models.Image(filename=file.filename, description=description)
        db.add(image)
        db.commit()
    db.refresh(image)
    # Перенаправляем пользователя на страницу с изображением
    return RedirectResponse(url=f"/get_image/{image.id}", status_code=303)

@app.post("/images/{image_id}/comments")
async def add_comment(
    image_id: int,
    text: str = Form(...),  # Получаем текст комментария из формы
    user_id: int = Form(...),  # ID пользователя также передаётся через форму
    db: Session = Depends(get_db),
    ):
    """Асинхронная функция-обработчик для запросов к /images/{image_id}/comments.
    Возвращает словарь об успешной загрузке комментария."""
    comment_data = schemas.CommentCreate(text=text, response_class=HTMLResponse)
    # Передаем в функцию add_comment новый комментарий
    comment = view.add_comment(db, comment_data, user_id=user_id, image_id=image_id)
    # Перенаправляем пользователя обратно на страницу с изображением
    return RedirectResponse(url=f"/get_image/{image_id}", status_code=303)

'''Просмотр, конкретного изображения и его описания'''
@app.get("/get_image/{image_id}", response_class=HTMLResponse)
async def get_image(request: Request, image_id: int, db: Session = Depends(get_db)):
    image = view.get_image_from_db(image_id, db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return templates.TemplateResponse("get_image.html", {"request": request, "image": image})

'''Маршрут для входа в систему'''
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = view.get_user(db, username)
    if not user or not view.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="неверное имя или пароль")
    request.session["user_id"] = user.id
    return RedirectResponse(url="/images", status_code=303)

'''Маршрут для выхода из системы'''
@app.post("/logout")
async def logout(request: Request):
    request.session.pop("user_id", None)
    return RedirectResponse(url="/", status_code=303)