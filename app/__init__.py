import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev-key-123'

database_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(os.path.join('app', 'static', 'movie_files'), exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'
login_manager.login_message = 'Пожалуйста, войдите.'

# ВАЖНО: models импортируется ДО views, иначе будет circular import
from app import models, views

app.config['SECURE_REFERRER_POLICY'] = 'strict-origin-when-cross-origin'
