from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):
    '''Создание модели CustomUser с расширением базовой модели AbstractUser
    (добавляе даты рождения)
    Редактирование административной панели'''
    birth_date = models.DateField(verbose_name='Дата рождения', blank=True, null=True)

    def __str__(self):
        """Переопределение строкового представления объекта.
        Возвращает имя и фамилию пользователя"""
        return f'{self.first_name} {self.last_name}'

    class Meta:
        """Определяем наименование в административной панеле"""
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


class Image(models.Model):
    """Создание модели с описанием характеристик для загруженных изображений.
    Данная модель сохраняет загруженные изображения в директорию 'images/',
    а также связывает изображение с пользователем, который ее загрузил."""
    image = models.ImageField(upload_to='media/')
    title = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='image')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Возвращает название картинки,
        которое изначально дает пользователь"""
        return self.title


class Comment(models.Model):
    """Создание модели для хранения комментариев к картинке.
    Связывает комментарий с конкретным изаображением и пользователем,
    который его оставил."""
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Возвращает строковое представление,
        включающее имя пользователя и название картинки"""
        return f"Комментарий от {self.user.username} на {self.image.title}"
