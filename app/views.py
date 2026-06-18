import os
from flask import request, render_template, url_for, redirect, flash, jsonify, abort
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import text  # Обязательный импорт

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
    comments = Comment.query.filter_by(movie_id=movie.id).order_by(Comment.id.desc()).all()
    return render_template('movie_detail.html', movie=movie, form=form, comments=comments)

def movie_search():
    query = request.args.get('q', '')
    movies = Movie.query.filter(Movie.name.contains(query)).all()
    return render_template('search.html', movies=movies, query=query)

def about(): return render_template('about.html')
def dmca(): return render_template('dmca.html')
def contacts(): return render_template('contacts.html')
def rules(): return render_template('rules.html')

# ========== API ==========
def api_movies():
    movies = Movie.query.all()
    return jsonify([{'id': m.id, 'name': m.name} for m in movies])

# ========== АККАУНТ ==========
def user_register():
    form = UserRegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('user_login'))
    return render_template('register.html', form=form)

def user_login():
    form = UserLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html', form=form)

def user_logout():
    logout_user()
    return redirect(url_for('index'))

# ========== АДМИНКА ==========
# Сюда вставлены ваши функции admin_..., просто добавьте проверку доступа:
def admin_movie_list():
    if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
        abort(403)
    return render_template('admin/movie_list.html', movies=Movie.query.all())

# (Остальные ваши admin_... функции вставьте здесь аналогично)

# ========== ВРЕМЕННЫЕ ФУНКЦИИ (УДАЛИТЬ ПОСЛЕ НАСТРОЙКИ) ==========

@app.before_request
def fix_database_column():
    try:
        db.session.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;'))
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/set_me_admin')
def set_me_admin():
    user = User.query.filter_by(username='anton').first() 
    if user:
        user.is_admin = True
        db.session.commit()
        return "Готово! Теперь вы администратор."
    return "Пользователь 'anton' не найден."
