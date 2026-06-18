from datetime import datetime
from flask_login import UserMixin
from . import db, bcrypt, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(255))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120))
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    year = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('movies', lazy='dynamic'))
    image = db.Column(db.String(255))
    video = db.Column(db.String(255))
    trailer_id = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, new_password):
        self.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('comments', lazy=True))
