# Определение модели данных, с которой взаимодействует программа

# Импорт экземпляра SQLAlchemy из конфигурации приложения
from app_config import data_base

class Users_db(data_base.Model):
    user_id = data_base.Column(data_base.String(100), primary_key=True)
    login = data_base.Column(data_base.String(100))
    password = data_base.Column(data_base.String(500))
    email = data_base.Column(data_base.String(100))

    tutor_data = data_base.relationship('Tutor_db', backref = 'users_db', uselist=True)
    content_data = data_base.relationship('Timetable_content_db', backref = 'users_db', uselist=True)
    lessons_data = data_base.relationship('Lessons_db', backref='users_db', uselist=True)

# TO DO Переименновать ДБ
class Tutor_db(data_base.Model):
    user = data_base.Column(data_base.String(100), data_base.ForeignKey('users_db.user_id'))
    content_id = data_base.Column(data_base.String(100), primary_key=True)
    name = data_base.Column(data_base.String(20))
    ward_id = data_base.Column(data_base.String(100))
    absent = data_base.Column(data_base.Integer)
    first_lesson = data_base.Column(data_base.Integer)
    last_lesson = data_base.Column(data_base.Integer)

    stud_data = data_base.relationship('Timetable_content_db', backref = 'tutor_db', uselist=False)
    lesson_data = data_base.relationship('Lessons_db', backref = 'tutor_db', uselist=True)

class Timetable_content_db(data_base.Model):

    user = data_base.Column(data_base.String(100), data_base.ForeignKey('users_db.user_id'))
    content_id = data_base.Column(data_base.String(100), data_base.ForeignKey('tutor_db.ward_id'), primary_key=True)
    name = data_base.Column(data_base.String(20))
    category = data_base.Column(data_base.String(20))
    absent = data_base.Column(data_base.Integer)
    combine = data_base.Column(data_base.Integer)
    first_lesson = data_base.Column(data_base.Integer)
    last_lesson = data_base.Column(data_base.Integer)

class Lessons_db(data_base.Model):

    user = data_base.Column(data_base.String(100), data_base.ForeignKey('users_db.user_id'))
    content_id = data_base.Column(data_base.String(100), primary_key=True)
    tutor_id = data_base.Column(data_base.String(100), data_base.ForeignKey('tutor_db.content_id'))
    category = data_base.Column(data_base.String(10))
    weekday_num = data_base.Column(data_base.Integer)
    lesson_num = data_base.Column(data_base.Integer)
    first_student = data_base.Column(data_base.String(100))
    second_student = data_base.Column(data_base.String(100))