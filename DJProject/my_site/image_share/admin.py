from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Регистрируем модель CustomUser в административном интерфейсе.
    Настраиваем панель отображения, критерии поиска и сортировка списка пользователей"""
    list_display = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)