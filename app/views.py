import os
from flask import render_template, url_for, redirect, flash, jsonify, abort, request
from flask_login import login_user, logout_user, current_user

# Импортируем из текущего пакета
from . import app, db
from .models import Category, Movie, User, Comment
from .forms import (CategoryForm, MovieForm, MovieUpdateForm, 
                    UserLoginForm, UserRegisterForm, CommentForm)

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
def check_admin():
    if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
        abort(403)

def admin_movie_list():
    check_admin()
    return render_template('admin/movie_list.html', movies=Movie.query.all())

def admin_movie_create():
    check_admin()
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(name=form.name.data, description=form.description.data, 
                      year=form.year.data, country=form.country.data, 
                      director=form.director.data, image=form.image.data)
        db.session.add(movie)
        db.session.commit()
        flash('Фильм создан!', 'success')
        return redirect(url_for('admin_movie_list'))
    return render_template('admin/movie_create.html', form=form)

def admin_category_list():
    check_admin()
    return render_template('admin/category_list.html', categories=Category.query.all())

def admin_category_create():
    check_admin()
    form = CategoryForm()
    if form.validate_on_submit():
        db.session.add(Category(name=form.name.data))
        db.session.commit()
        flash('Категория создана!', 'success')
        return redirect(url_for('admin_category_list'))
    return render_template('admin/category_create.html', form=form)

def admin_category_update(category_id):
    check_admin()
    category = Category.query.get_or_404(category_id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        return redirect(url_for('admin_category_list'))
    return render_template('admin/category_update.html', form=form)

def admin_category_delete(category_id):
    check_admin()
    db.session.delete(Category.query.get_or_404(category_id))
    db.session.commit()
    return redirect(url_for('admin_category_list'))

def admin_movie_update(movie_id):
    check_admin()
    movie = Movie.query.get_or_404(movie_id)
    form = MovieUpdateForm(obj=movie)
    if form.validate_on_submit():
        movie.name = form.name.data
        movie.description = form.description.data
        movie.year = form.year.data
        db.session.commit()
        return redirect(url_for('admin_movie_list'))
    return render_template('admin/movie_update.html', form=form)

def admin_movie_delete(movie_id):
    check_admin()
    db.session.delete(Movie.query.get_or_404(movie_id))
    db.session.commit()
    return redirect(url_for('admin_movie_list'))
