from pydantic import BaseModel
from typing import Optional
from datetime import date

"""Модуль для обработки данных из HTML-форм"""


class UserRegistrationForm(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: str
    birth_date: Optional[date] = None
    password: str
    confirm_password: str

    def check_passwords(self):
        if self.password != self.confirm_password:
            raise ValueError("Пароли не совпадают")