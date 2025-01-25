from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, CustomUser, Image, Comment
from forms import UserRegistrationForm, UserLoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import os

app = Flask(__name__)  # Создание экземпляр приложения Flask
app.config.from_object('config.Config')  # Инициализация конфигурации приложения
app.config['UPLOAD_FOLDER'] = 'uploads'
db.init_app(app)  # Инициализация SQLAlchemy

migrate = Migrate(app, db)  # Связывание базы данных с приложением

login_manager = LoginManager(app)  # Аутентификацией пользователей
login_manager.login_view = 'login'  # Перенаправление неавторизованных пользователей на страничку с авторизацией

UPLOAD_FOLDER = 'uploads'  # Директория для хранения загруженных файлов
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Создание директории uploads, если она ещё не существует
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Путь для хранения изображений

@login_manager.user_loader
def load_user(user_id):
    """Возвращает объект пользователя или None"""
    try:
        return CustomUser.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

@app.route('/')
def home():
    """связывает URL-адрес '/' (корневой URL) с функцией home."""
    return render_template('home.html')

"""@app.route - это декоратор, который связывает URL /register """

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Функция, позволяющая зарегистрировать пользователя.
    Возвращает главную страницу в случае успешной регистрации,
    в ином случае отображается форма регистрации register.html"""
    form = UserRegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')  # Хэширование пароля
        new_user = CustomUser(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            birth_date=form.birth_date.data,
            password=hashed_password
        )  # Создание нового объект пользователя CustomUser (модель из базы данных) на основе данных формы
        db.session.add(new_user)  # Добавление нового пользователя в базу данных
        db.session.commit()  # Сохранение изменений в базе данных

        login_user(new_user)  # Авторизация пользователя после регистрации
        return redirect(url_for('home'))

    return render_template('register.html', form=form)

"""@app.route - это декоратор, который связывает URL /login с функцией login"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция для авторизации пользователя. Используется форма для входя пользователей.
    Возвращает отрендереный шаблон login.html, если форма не отправлена или введены некорректные данные.
    Если направлен ПОСТ-запрос и пользователь зарегистрирован, то возвращает главную страницу.
    В случае неверного введения данных всплывает надпись о наверно логине или пароле"""
    form = UserLoginForm()
    if form.validate_on_submit():  # Проверка формы на отправку ПОСТ-запроса
        user = CustomUser.query.filter_by(username=form.username.data).first()  # Получение пользователя из БД
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)  # Авторизация, если совпадают пароли и user != None
            return redirect(url_for('home'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html', form=form)

"""Декоратор @login_required ограничивает доступ к представлению только для авторизованных пользователей. 
Если пользователь не авторизован, он будет перенаправлен на маршрут, 
указанный в login_manager.login_view.
app.route - декоратор, который связывает URL /users_list с функцией users_list"""

@app.route('/users_list')
@login_required
def users_list():
    """Функция, которая выводит список пользователей, запрашивая их из базы данных.
    Возвращает отрендеренный HTML-шаблон со списком всех пользователей"""
    users = CustomUser.query.all()
    return render_template('users_list.html', users=users)

"""Этоn декоратор связывает URL /logout с функцией logout"""

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Функция для завершения сессии пользователем.
    Возвращает главную страницу и выход из аккаунта пользователем"""
    logout_user()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('home'))

"""Декоратор @login_required ограничивает доступ к представлению только для авторизованных пользователей. 
Если пользователь не авторизован, он будет перенаправлен на маршрут, 
указанный в login_manager.login_view.
@app.route - это декоратор, который связывает URL /images 
с функцией images, обрабатывающей как GET-запросы (отображение формы), 
так и POST-запросы (обработка данных формы)"""

@app.route('/images', methods=['GET', 'POST'])
@login_required
def images():
    """Функция загружающая изображения и отображающая их"""
    if request.method == 'POST':
        file = request.files.get('image')  # Получение загруженного изображения по ключу
        description = request.form.get('description')  # Получение описания изображения
        if file:  # Проверка на загрузку изображения
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Сохранение изображений в uploads
            new_image = Image(
                user_id=current_user.id,
                image_path=f"{app.config['UPLOAD_FOLDER']}/{filename}",
                description=description
            )  # Создание объекта изображения по модели из БД с описанием, путем и пользователем, загрузившем его
            db.session.add(new_image)  # Добавление фотографии в БД
            db.session.commit()
            flash('Изображение успешно загружено', 'success')  # Отображает сообщение об успешной загрузке
    images = Image.query.order_by(Image.timestamp.desc()).all()
    return render_template('images.html', images=images)

"""Функция маршрута для обслуживания файлов из папки uploads"""

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

"""app.route - декоратор, связывающий URL /images/<int:image_id>/comments с функцией add_comment.
Декоратор @login_required ограничивает доступ к представлению только для авторизованных пользователей. 
Если пользователь не авторизован, он будет перенаправлен на маршрут, указанный в login_manager.login_view"""

@app.route('/images/<int:image_id>/comments', methods=['POST'])
@login_required
def add_comment(image_id):
    content = request.form.get('comment')  # Получения комментария по ключу 'comment'
    if content:  # Проверка на наличие комментария
        new_comment = Comment(
            user_id=current_user.id,
            image_id=image_id,
            content=content
        )  # Создание объекта комментарий с данными о пользователе, изображении и тексте комментария
        db.session.add(new_comment)  # Добавление в базу данных
        db.session.commit()
        flash('Комментарий добавлен', 'success')
    return redirect(url_for('images'))

@app.route('/image/<int:image_id>')
def image_detail(image_id):
    image = Image.query.get_or_404(image_id)
    comments = Comment.query.filter_by(image_id=image_id).all()
    return render_template('image_detail.html', image=image, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)