import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

app.config['SECRET_KEY'] = 'секретный-ключ-замените'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(os.path.join('app', 'static', 'movie_files'), exist_ok=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'user_login'
login_manager.login_message = 'Пожалуйста, войдите.'

from app import models, views

app.config['SECURE_REFERRER_POLICY'] = 'strict-origin-when-cross-origin'

app.config['KINESCOPE_API_KEY'] = '0727b8d9-00a0-47fb-89ad-0789827360c8'
