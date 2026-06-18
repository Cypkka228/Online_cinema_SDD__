import os
from flask import request, render_template, url_for, redirect, flash, jsonify
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user

from . import app, db
from .models import Category, Movie, User, Comment
from .forms import CategoryForm, MovieForm, MovieUpdateForm, UserLoginForm, UserRegisterForm, CommentForm

STATIC_ROOT = os.path.join('app', 'static')

# ========== ПУБЛИЧНЫЕ ==========
def index():
    movies = Movie.query.order_by(Movie.created_at.desc()).all()
    return render_template('index.html', title='SanDaDan', movies=movies)

def movie_detail(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Необходимо войти, чтобы оставить комментарий.', 'warning')
            return redirect(url_for('user_login'))
        comment = Comment(text=form.text.data, user_id=current_user.id, movie_id=movie.id)
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен!', 'success')
        return redirect(url_for('movie_detail', movie_id=movie.id))
    comments = Comment.query.filter_by(movie_id=movie.id).order_by(Comment.created_at.desc()).all()
    return render_template('movie_detail.html', movie=movie, comments=comments, form=form, title=movie.name)

def movie_search():
    search_name = request.args.get('search', '').strip()
    if search_name:
        movie_list = Movie.query.filter(Movie.name.ilike(f'%{search_name}%')).all()
    else:
        movie_list = Movie.query.all()
    return render_template('movie_search.html', movie_list=movie_list, title='Поиск')

def api_movies():
    movies = Movie.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'year': m.year,
        'image': m.image,
        'video': m.video,
        'description': m.description,
        'category_id': m.category_id,
        'category_name': m.category.name if m.category else None,
    } for m in movies])

def about():
    return render_template('about.html', title='О проекте')

def dmca():
    return render_template('dmca.html', title='Правообладателям')

def contacts():
    return render_template('contacts.html', title='Контакты')

def rules():
    return render_template('rules.html', title='Правила')

# ========== АККАУНТ ==========
def user_register():
    form = UserRegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            db.session.add(new_user)
            db.session.commit()
            flash(f'Пользователь {new_user.username} успешно зарегистрирован', 'success')
            return redirect(url_for('user_login'))
        else:
            errors = '; '.join(f'{f}: {", ".join(e)}' for f, e in form.errors.items())
            flash(f'Ошибка регистрации: {errors}', 'error')
    return render_template('account/index.html', form=form, title='Регистрация')

def user_login():
    form = UserLoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Вы успешно вошли в систему', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неверный логин или пароль', 'error')
    return render_template('account/index.html', form=form, title='Авторизация')

def user_logout():
    logout_user()
    return redirect(url_for('user_login'))

# ========== АДМИН — КАТЕГОРИИ ==========
@login_required
def admin_category_create():
    form = CategoryForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            cat = Category(name=form.name.data, description=form.description.data)
            db.session.add(cat)
            db.session.commit()
            flash('Категория успешно добавлена', 'success')
            return redirect(url_for('admin_category_list'))
        else:
            errors = '; '.join(f'{f}: {", ".join(e)}' for f, e in form.errors.items())
            flash(f'Ошибка: {errors}', 'error')
    return render_template('admin/form.html', form=form, title='Новая категория')

@login_required
def admin_category_list():
    return render_template('admin/category_list.html', category_list=Category.query.all(), title='Категории')

@login_required
def admin_category_update(category_id):
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if request.method == 'POST' and form.validate_on_submit():
        form.populate_obj(category)
        db.session.commit()
        flash('Категория обновлена', 'success')
        return redirect(url_for('admin_category_list'))
    return render_template('admin/form.html', form=form, title='Редактировать категорию')

@login_required
def admin_category_delete(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        return redirect(url_for('admin_category_list'))
    return render_template('admin/category_delete.html', category=category, title='Удалить категорию')

# ========== АДМИН — ФИЛЬМЫ ==========
@login_required
def admin_movie_create():
    form = MovieForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            image = form.image.data
            slug = form.slug.data or secure_filename(form.name.data.lower().replace(' ', '-'))

            file_path = os.path.join(STATIC_ROOT, 'movie_files', slug)
            os.makedirs(file_path, exist_ok=True)

            image_name = secure_filename(image.filename)
            image.save(os.path.join(file_path, image_name))

            movie = Movie(
                slug=slug,
                name=form.name.data,
                description=form.description.data,
                year=form.year.data,
                category_id=form.category_id.data,
                image=f'movie_files/{slug}/{image_name}',
                video=form.video.data  # это iframe-код
            )
            db.session.add(movie)
            db.session.commit()
            flash('Фильм добавлен!', 'success')
            return redirect(url_for('index'))
        else:
            print(form.errors)
            flash('Ошибка валидации. Проверьте поля.', 'error')
    return render_template('admin/form.html', form=form, title='Добавить фильм')

@login_required
def admin_movie_list():
    return render_template('admin/movie_list.html', movie_list=Movie.query.all(), title='Фильмы')

@login_required
def admin_movie_update(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    form = MovieUpdateForm(obj=movie)

    if request.method == 'POST' and form.validate_on_submit():
        movie.name = form.name.data
        movie.slug = form.slug.data
        movie.description = form.description.data
        movie.year = form.year.data
        movie.category_id = form.category_id.data
        movie.video = form.video.data

        # Если загружен новый постер
        if form.image.data and form.image.data.filename:
            slug = movie.slug or secure_filename(movie.name.lower().replace(' ', '-'))
            file_path = os.path.join(STATIC_ROOT, 'movie_files', slug)
            os.makedirs(file_path, exist_ok=True)
            if movie.image and isinstance(movie.image, str):
                old_image_path = os.path.join(STATIC_ROOT, movie.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            image = form.image.data
            image_name = secure_filename(image.filename)
            image.save(os.path.join(file_path, image_name))
            movie.image = f'movie_files/{slug}/{image_name}'

        db.session.commit()
        flash('Фильм обновлён', 'success')
        return redirect(url_for('admin_movie_list'))

    return render_template('admin/form.html', form=form, title='Редактировать фильм')

@login_required
def admin_movie_delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    if request.method == 'POST':
        db.session.delete(movie)
        db.session.commit()
        return redirect(url_for('admin_movie_list'))
    return render_template('admin/movie_delete.html', movie=movie, title='Удалить фильм')
