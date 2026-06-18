import os
from app import app, db
from app import views

# ========== МАРШРУТЫ ==========
app.add_url_rule('/', view_func=views.index)
app.add_url_rule('/movie/<int:movie_id>', view_func=views.movie_detail, methods=['POST', 'GET'])
app.add_url_rule('/search', view_func=views.movie_search)
app.add_url_rule('/about', view_func=views.about)
app.add_url_rule('/dmca', view_func=views.dmca)
app.add_url_rule('/contacts', view_func=views.contacts)
app.add_url_rule('/rules', view_func=views.rules)
app.add_url_rule('/api/movies', view_func=views.api_movies)
app.add_url_rule('/account/register', view_func=views.user_register, methods=['POST', 'GET'])
app.add_url_rule('/account/login', view_func=views.user_login, methods=['POST', 'GET'])
app.add_url_rule('/account/logout', view_func=views.user_logout)
app.add_url_rule('/admin/category/create', view_func=views.admin_category_create, methods=['POST', 'GET'])
app.add_url_rule('/admin/category/list', view_func=views.admin_category_list)
app.add_url_rule('/admin/category/<int:category_id>/update', view_func=views.admin_category_update, methods=['POST', 'GET'])
app.add_url_rule('/admin/category/<int:category_id>/delete', view_func=views.admin_category_delete, methods=['POST', 'GET'])
app.add_url_rule('/admin/movie/create', view_func=views.admin_movie_create, methods=['POST', 'GET'])
app.add_url_rule('/admin/movie/list', view_func=views.admin_movie_list)
app.add_url_rule('/admin/movie/<int:movie_id>/update', view_func=views.admin_movie_update, methods=['POST', 'GET'])
app.add_url_rule('/admin/movie/<int:movie_id>/delete', view_func=views.admin_movie_delete, methods=['POST', 'GET'])


# ========== СОЗДАНИЕ АДМИНИСТРАТОРА ==========
def create_admin(username, password):
    from app.models import User
    existing = User.query.filter_by(username=username).first()
    if existing:
        if not existing.is_admin:
            existing.is_admin = True
            db.session.commit()
            print(f"Пользователь '{username}' повышен до администратора.")
        else:
            print(f"Администратор '{username}' уже существует.")
        return
    admin = User(username=username, is_admin=True)
    admin.password = password
    db.session.add(admin)
    db.session.commit()
    print(f"Администратор '{username}' создан!")


# ========== ЗАПУСК ==========
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if admin_username and admin_password:
            create_admin(admin_username, admin_password)
        else:
            print("Задайте ADMIN_USERNAME и ADMIN_PASSWORD в переменных окружения!")
    app.run(debug=True, port=5002)
