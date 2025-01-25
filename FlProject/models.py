from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy() # Создание объекта SQLAlchemy

class CustomUser(db.Model, UserMixin): # UserMixin необходим для авторизации пользователя
    """Модель пользователя для отображения в базе данных"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        """Метод __repr__ возвращает строковое представление объекта в БД"""
        return f'<CustomUser {self.username}>'

class Image(db.Model):
    """Модель изображений для отображения в БД"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('custom_user.id'), nullable=False)
    image_path = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('CustomUser', backref='images')

class Comment(db.Model):
    "Модель комментариев для отображения в БД"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('custom_user.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('CustomUser', backref='comments')
    image = db.relationship('Image', backref='comments')