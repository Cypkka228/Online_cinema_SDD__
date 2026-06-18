from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from .models import Category

class CategoryForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired(), Length(max=60)])
    description = StringField('Описание', validators=[Length(max=255)])

class MovieForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    slug = StringField('Slug (необязательно)')
    description = TextAreaField('Описание')
    year = IntegerField('Год', validators=[DataRequired()])
    category_id = SelectField('Категория', coerce=int)
    image = FileField('Постер', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только изображения!')])
    video = StringField('Код для вставки (iframe)', validators=[DataRequired()])  # ← Только iframe!

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Category
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class MovieUpdateForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    slug = StringField('Slug')
    description = TextAreaField('Описание')
    year = IntegerField('Год')
    category_id = SelectField('Категория', coerce=int)
    video = StringField('Код для вставки (iframe)')
    image = FileField('Новый постер (оставьте пустым, если не хотите менять)', 
                      validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Только изображения!')])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from app.models import Category
        self.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

class UserRegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(min=3, max=60)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=4)])

class UserLoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])

class CommentForm(FlaskForm):
    text = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=2, max=1000)])
