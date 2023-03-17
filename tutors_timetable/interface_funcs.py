import datetime
import uuid
from werkzeug.security import generate_password_hash

from data_base import *

# Возвращает актуальный день недели в качестве номера (int).
# В субботу и воскресенье возвращает понедельник
def get_weekday_num():
    weekday_num = datetime.datetime.now().weekday()
    if weekday_num > 4:
        weekday_num = 0

    return weekday_num

# Принимает опцию в расписании (str) и возвращает список записей для последующего внесения в БД
def divide_option(option):
    option = option.split('/')

    if len(option) < 2:
        option.append(None)

    return option

# Сохранение нового урока в БД.
# Перед внесением нового урока, проверяет, есть ли в БД урок с такими же параметрами и, если есть, удаляет его
def save_lesson(data):

    old_lesson = Lessons_db.query.filter(Lessons_db.category==data['category'],
                                         Lessons_db.weekday_num==data['weekday_num'],
                                         Lessons_db.lesson_num==data['lesson_num'],
                                         Lessons_db.tutor_id==data['tutor_id']).first()
    if old_lesson:
        data_base.session.delete(old_lesson)

    new_lesson = Lessons_db(user=data['user'],
                            content_id=data['lesson_id'],
                            tutor_id=data['tutor_id'],
                            category=data['category'],
                            weekday_num=data['weekday_num'],
                            lesson_num=data['lesson_num'],
                            first_student=data['first_student'],
                            second_student=data['second_student'])


    data_base.session.add(new_lesson)
    data_base.session.flush()

# Регистрация пользователя.
# Помимо внесения логина и пароля, создает тьюторов и учеников, с которыми пользователь будет взаимодействовать
def add_user(login, email, password):
    user_id = str(uuid.uuid4())
    password = generate_password_hash(password)

    user = Users_db(user_id=user_id, login=login, password=password, email=email)
    data_base.session.add(user)

    stud_id_1 = str(uuid.uuid4())
    stud_id_2 = str(uuid.uuid4())
    stud_id_3 = str(uuid.uuid4())

    tut_1 = Tutor_db(user=user_id, content_id=str(uuid.uuid4()), name='Тьютор A', ward_id=stud_id_1, absent=0, first_lesson=0, last_lesson=7)
    data_base.session.add(tut_1)
    tut_2 = Tutor_db(user=user_id, content_id=str(uuid.uuid4()), name='Тьютор B', ward_id=stud_id_2, absent=0, first_lesson=0, last_lesson=7)
    data_base.session.add(tut_2)
    tut_3 = Tutor_db(user=user_id, content_id=str(uuid.uuid4()), name='Тьютор C', ward_id=stud_id_3, absent=0, first_lesson=0, last_lesson=7)
    data_base.session.add(tut_3)

    stud_1 = Timetable_content_db(user=user_id, content_id=stud_id_1, category='student', name='Ученик A', combine=1, absent=0, first_lesson=0, last_lesson=5)
    data_base.session.add(stud_1)
    stud_2 = Timetable_content_db(user=user_id, content_id=stud_id_2, category='student', name='Ученик B', combine=1, absent=0, first_lesson=0, last_lesson=5)
    data_base.session.add(stud_2)
    stud_3 = Timetable_content_db(user=user_id, content_id=stud_id_3, category='student', name='Ученик C', combine=1, absent=0, first_lesson=0, last_lesson=5)
    data_base.session.add(stud_3)

    plug_1 = Timetable_content_db(user=user_id, content_id=str(uuid.uuid4()), category='user_plug', name='Метод. работа',
                                  combine=None, absent=None, first_lesson=None, last_lesson=None)
    data_base.session.add(plug_1)

    data_base.session.flush()
    data_base.session.commit()




