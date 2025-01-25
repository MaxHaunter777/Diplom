from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

"""В данном модуле определены столбцы таблиц, их типы данных и ограничения.
Отношения между моделями с использованием relationship (один-ко-многим)"""

Base = declarative_base()

"""Создание базового класса Base, 
который используется для описания моделей базы данных"""

class CustomUser(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    birth_date = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}' # Строковое представление объекта CustomUser

# Изображение пользователя
class Image(Base):
    __tablename__ = 'images' # Указание имени таблицы в базе данных.

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    filename = Column(String, nullable=False)
    description = Column(String, nullable=True)
    user = relationship("CustomUser", back_populates="images")

# Комментарии к фото
class Comment(Base):
    __tablename__ = 'comments' # Указание имени таблицы в базе данных.

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey('images.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    text = Column(Text, nullable=False)
    user = relationship("CustomUser", back_populates="comments")
    image = relationship("Image", back_populates="comments")

"""Эти строки добавляют связи между моделями, 
которые были объявлены без обратных связей"""
CustomUser.images = relationship("Image", back_populates="user")
CustomUser.comments = relationship("Comment", back_populates="user")
Image.comments = relationship("Comment", back_populates="image")
