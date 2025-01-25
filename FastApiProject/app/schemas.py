from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from typing import List
from fastapi import HTTPException, status

"""Этот модуль играет ключевую роль в управлении и валидации данных.
Если данные не соответствуют схеме данных, FastAPI вернет ошибку"""

class UserBase(BaseModel):
    """Базовая модель для представления пользователя с параметрами:
    username, first_name, last_name, email, birth_date (необязательное)"""
    username: str
    first_name: str
    last_name: str
    email: str
    birth_date: Optional[date] = None


class UserCreate(UserBase):
    """Модель для создания нового пользователя.
    Добавляет обязательное поле password"""
    password: str
    confirm_password: str


def check_passwords(self):
    if self.password != self.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

class User(UserBase):
    """Модель с идентифицирующим номером пользователя"""
    id: int

    class Config:
        """Настройка поведения Pydantic при взаимодействии с моделями"""
        from_attributes = True


class ImageBase(BaseModel):
    """Базовая модель для представления изображений"""
    filename: str
    description: Optional[str] = None


class ImageCreate(ImageBase):
    """Модель для создания нового изображения"""
    pass


class Image(ImageBase):
    """Модель для представления изображений.
    Список комментариев к изображению, связан с моделью Comment"""
    id: int
    user_id: int
    comments: List["Comment"] = []

    class Config:
        """Настройка поведения Pydantic при взаимодействии с моделями"""
        from_attributes = True


# Схемы для комментариев
class CommentBase(BaseModel):
    text: str


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    photo_id: int
    user_id: int

    class Config:
        from_attributes = True