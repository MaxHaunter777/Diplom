from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer




"""Модуль реализует логику работы базы данных для дальнейшего включения в обработку запросов.
Использование готовых данных из модулей models, schemas и их синхронизация"""

"""Создание объекта для хеширования пароля"""
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

''' зависимость для проверки аутентификации:'''
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_user(db: Session, user: schemas.UserCreate):
    """Функция для создания нового пользователя."""
    # Проверка на существование пользователя
    existing_user = db.query(models.CustomUser).filter(models.CustomUser.email == user.email).first()
    if existing_user:
        raise ValueError("Пользователь с таким email уже существует")

    hashed_password = pwd_context.hash(user.password)  # Хеширование пароля
    db_user = models.CustomUser(
    username=user.username,
    first_name=user.first_name,
    last_name=user.last_name,
    email=user.email,
    birth_date=user.birth_date,
    hashed_password=hashed_password,
    )
    db.add(db_user)  # Добавление объекта
    print(f"Добавлен пользователь: {db_user}")  # Отладочное сообщение
    db.commit()  # Сохранение изменений в БД
    db.refresh(db_user)  # Обновление сессии
    print(f"Пользователь сохранен: {db_user}")  # Отладочное сообщение
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Функция для получения списка пользователей.
        Возвращает список пользователей, запрошенных из базы данных
        с учетом параметров пропуска и лимита"""
    return db.query(models.CustomUser).offset(skip).limit(limit).all()


def get_user_by_username(db: Session, username: str):
    """Функция для получения пользователя по имени пользователя"""
    return db.query(models.CustomUser).filter(models.CustomUser.username == username).first()


def add_image(db: Session, image: schemas.ImageCreate, user_id: int):
    """Функция возвращает добавленное изображение"""
    db_image = models.Image(**image.dict(), user_id=user_id)  # Создание объект модели Image на основе схемы ImageCreate
    db.add(db_image)  # Добавление объекта
    db.commit()
    db.refresh(db_image)
    return db_image


def get_images(db: Session, skip: int = 0, limit: int = 100):
    """Функция возвращает список изображений, с учетом параметров пропуска и лимита."""
    return db.query(models.Image).offset(skip).limit(limit).all()


def add_comment(db: Session, comment: schemas.CommentCreate, user_id: int, image_id: int):
    """Функция возвращает сохраненный объект комментария"""
    db_comment = models.Comment(**comment.dict(), user_id=user_id, image_id=image_id)
    # Создает объект модели Comment на основе данных из схемы CommentCreate, user_id и image_id
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_image(db: Session, image_id: int):
    """Функция возвращает список комментариев к изображению"""
    return db.query(models.Comment).filter(models.Comment.image_id == image_id).all()

def get_image_from_db(image_id: int, db: Session):
    """Функция возвращает изображение"""
    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    return image

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, username: str):
    return db.query(models.CustomUser).filter(models.CustomUser.username == username).first()