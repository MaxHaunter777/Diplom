from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, ImageForm, CommentForm
from .models import CustomUser, Image, Comment
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


def register(request):
    """Обработка POST-запроса для регистрации нового пользователя.
    В зависимости от запроса возвращаем либо главную страницу, либо форму регистрации"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сохраняем нового пользователя
            login(request, user)  # Авторизуем пользователя сразу после регистрации
            return redirect('home')  # Перенаправляем на главную страницу
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password) # Проверяем учетные данные
            if user is not None:
                login(request, user)     # Выполняем вход
                return redirect('home')  # Перенаправляем на главную страницу
    return render(request, './login.html', {'form': form})

def home(request):
    """Функция-представление, которая выводит главную страницу."""
    title = 'Home'
    context = {
        'title': title,
    }
    return render(request, 'home.html', context)

def users_list(request):
    """Функция-представление, которая извлекает записи о пользователях из базы данных.
    Возвращаем HTML-шаблон users_list.html, передавая ему список пользователей"""
    users = CustomUser.objects.all()
    return render(request, 'users_list.html', {'users': users})

@login_required
def image_gallery(request):
    """Декоратор, ограничивающий доступ для не авторизованных пользователей.
    Функция-представление отображает загруженные изображения."""
    try:
        images = Image.objects.all()
    except Image.DoesNotExist:
        images = []
    return render(request, 'image_gallery.html', {'images': images})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def upload_image(request):
    """Загрузка изображений доступна только для авторизованных пользователей.
     В случае успешной загрузки изображения
    отображает галерею. """
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                image = form.save(commit=False)
                image.user = request.user
                image.save()
                messages.success(request, "Фотография успешно загружена!")
                return redirect('image_gallery')
            except ValidationError as e:
                messages.error(request, f"Ошибка валидации: {e}")
                return render(request, 'upload_image.html', {'form': form})
            except Exception as e:
                messages.error(request, f"Произошла неизвестная ошибка: {e}")
                return render(request, 'upload_image.html', {'form': form})
    else:
        form = ImageForm()
    return render(request, 'upload_image.html', {'form': form})

@login_required
def image_detail(request, pk):
    """Добавление комментариев доступно только для авторизованных пользователей.
    Комментарии будут добавлены, если передаваемое значение является POST-запросом,
    а также будет пройдена проверка на корректность заполнения"""
    image = get_object_or_404(Image, pk=pk)  # получение объекта или возвращение ошибки в случае его отсутствия
    comments = image.comments.all()  # получение всех связанных комментариев
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.image = image
            comment.user = request.user
            comment.save()
            return redirect('image_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'image_detail.html', {'image': image, 'comments': comments, 'form': form})
