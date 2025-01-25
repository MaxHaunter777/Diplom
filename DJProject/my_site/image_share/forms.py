from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, Image, Comment
from django.core.validators import FileExtensionValidator
from django.contrib.auth.forms import  AuthenticationForm


class UserRegistrationForm(forms.ModelForm):
    """Отображение полей для регистрации нового пользователя
    с указанием их типов и настройкой виджетов"""
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Пароль")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Подтверждение пароля")
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label='Дата рождения'
    )

    class Meta:
        """Построение динамической формы Пользователя на основании модели CustomUser"""
        model = CustomUser
        fields = [
            'username', 'first_name',
            'last_name', 'email',
            'birth_date']
        labels = {
            'username': 'Логин',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'birth_date': 'Дата рождения',
        }

    def clean_confirm_password(self):
        """Проверка на совпадение полей "Пароль" и "Подтверждение пароля" """
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Пароли не совпадают")
        return confirm_password

    def save(self, commit=True):
        """Сохранение формы в базе данных"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)

class ImageForm(forms.ModelForm):
    """Отображение полей для загрузки фотографий"""
    class Meta:
        """Построение динамической формы для загрузки фотографий
         на основании модели Photo"""
        model = Image
        fields = ['image', 'title', 'description']
        labels = {
            'image': 'Изображение',
            'title': 'Название',
            'description': 'Описание',
        }
        widgets = {
            'image': forms.FileInput()
        }
        validators = [
            FileExtensionValidator(['jpeg', 'jpg', 'png', 'gif']),
        ]


class CommentForm(forms.ModelForm):
    """Отображение полей, где можно оставить комментарий"""
    class Meta:
        """Построение динамической формы комментариев
        на основании модели Comment"""
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Комментарий',
        }
        widgets = {
            'content': forms.Textarea(),
        }