# Основной функционал приложения, создание расписания и работа с ним

import uuid
from werkzeug.security import generate_password_hash, check_password_hash

# Импорт классов, необходимых для создания расписания
from interface_funcs import *
from persons_manager import Persons_manager
from timetable import *
from UserLogin import UserLogin
from app_config import *
from data_base import *

from settings_module import tm_settings

app.register_blueprint(tm_settings, url_prefix='/tm_settings')

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id)


# Начало работы
# Определяется сегодняшний день недели и на его основе создается расписание
@app.route('/')
def index():
    weekday_num = get_weekday_num()
    session['actual_setting_table'] = 'tutor'

    return redirect(url_for('display_timetable', weekday_num=weekday_num))


# Инициализирует объект класса Timetable на основании дня недели и осуществляет рендер html-страницы на его основе
@app.route('/display_timetable/<int:weekday_num>')
def display_timetable(weekday_num):

    if current_user.is_authenticated:
        user_id = current_user.get_id()
        log_label = current_user.get_login()
    else:
        user_id = 'UNKNOW'
        log_label = 'Вход'

    weekdays = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница'}
    weekday = weekdays[weekday_num]
    weekdays = weekdays.values()
    session['weekday_num'] = weekday_num

    person_manager = Persons_manager(user_id)
    actual_tutors = person_manager.get_present_persons_list('tutor')
    options = Options(person_manager).return_timetable_options()
    timetable = Timetable(person_manager, weekday_num).timetable
    tutors = person_manager.tutors_list
    students = person_manager.students_list

    return render_template('main_table.html', weekday=weekday,
                                              weekdays=weekdays,
                                              actual_tutors=actual_tutors,
                                              options=options,
                                              timetable=timetable,
                                              tutors=tutors,
                                              students=students,
                                              log_label=log_label)

# Изменение параметра absent у тьюторов и учеников для исключения их из расписания
@app.route('/change_absent/<db>/<person_id>')
def change_absent(db, person_id):

    if current_user.is_authenticated:
        db_types = {'tutors': Tutor_db, 'students': Timetable_content_db}
        db = db_types[db]

        try:
            absent = db.query.filter(db.content_id==person_id).first().absent
            db.query.filter(db.content_id==person_id).first().absent = 1 - absent

            data_base.session.flush()
            data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Ошибка добавления в базу данных', category='db_mistake')

    else:
        flash('Авторизируйтесь для полноценной работы с приложением', category='need_login')

    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Сохранение изменений, внесенных пользователем в расписание
@app.route('/save_cell', methods=['POST', 'GET'])
def save_cell():

    if current_user.is_authenticated:
        results = {'status': 'not_authenticated'}
        return jsonify(results)

    else:
        user_id = current_user.get_id()
        # Информация об изменениях расписания приходит в виде словаря, в котором указаны тьютор, номер урока и новое значение
        data = request.get_json()
        tutor_id = data['tutor_id']
        lesson_num = int(data['lesson_num'])
        students_id = data['value']
        first_student, second_student = divide_option(students_id)

        lesson_data = {'user': user_id,
                       'lesson_id': str(uuid.uuid4()),
                       'tutor_id': tutor_id,
                       'weekday_num': session['weekday_num'],
                        'category': 'saved',
                       'lesson_num': lesson_num,
                       'first_student': first_student,
                       'second_student': second_student}

        try:
            save_lesson(lesson_data)
            data_base.session.commit()
            results = {'status': 'saved'}
        except:
            data_base.session.rollback()
            results = {'status': 'db_mistake'}
            flash('Ошибка добавления в базу данных', category='db_mistake')

        return jsonify(results)



# Удаление из БД всех уроков, внесенных пользователем во время взаимодействия с расписанием.
@app.route('/clear_timetable')
def clear_timetable():
    if current_user.is_authenticated:


        try:
            Lessons_db.query.filter(Lessons_db.user==current_user.get_id(),
                                    Lessons_db.weekday_num==session['weekday_num'],
                                    Lessons_db.category=='saved').delete()
            data_base.session.flush()
            data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Ошибка добавления в базу данных', category='db_mistake')

    else:
        flash('Авторизируйтесь для полноценной работы с приложением', category='need_login')

    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Сохранение информации о том, что все уроки под некоторым номером на актуальный день недели должны быть
# заполнены пробелами
# Для пользователя выглядит как полная очистка столбца расписания
@app.route('/clear_column/<int:column_ind>')
def clear_column(column_ind):

    if current_user.is_authenticated:
        user_id = current_user.get_id()

        actual_tutors = Persons_manager(user_id).get_present_persons_list('tutor')
        try:
            for tutor in actual_tutors:
                lesson_data = {'user': user_id,
                               'lesson_id': str(uuid.uuid4()),
                               'tutor_id': tutor.id,
                               'weekday_num': session['weekday_num'],
                               'category': 'saved',
                               'lesson_num': column_ind,
                               'first_student': 'space',
                               'second_student': None}
                save_lesson(lesson_data)
                data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Ошибка добавления в базу данных', category='registr_mistake')

    else:
        flash('Авторизируйтесь для полноценной работы с приложением', category='need_login')

    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Сохранение информации о том, что для определенного тьютора все уроки на актуальный день недели должны быть
# заполнены пробелами
# Для пользователя выглядит как полная очистка строки расписания
@app.route('/clear_row/<tutor_id>')
def clear_row(tutor_id):

    if current_user.is_authenticated:
        user_id = current_user.get_id()

        try:
            for lesson_num in range(8):
                lesson_data = {'user': user_id,
                               'lesson_id': str(uuid.uuid4()),
                               'tutor_id': tutor_id,
                               'weekday_num': session['weekday_num'],
                               'category': 'saved',
                               'lesson_num': lesson_num,
                               'first_student': 'space',
                               'second_student': None}

                save_lesson(lesson_data)
                data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Ошибка добавления в базу данных', category='registr_mistake')

    else:
        flash('Авторизируйтесь для полноценной работы с приложением', category='need_login')

    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Создание xlsx файла на основании атрибутов класса Timetable и загрузка его из директории
@app.route('/download_xlsx')
def download_xlsx():
    if current_user.is_authenticated:
        user_id = current_user.get_id()

        weekday_num = session['weekday_num']

        weekdays = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday'}
        weekdays_lab = {0: 'пн', 1: 'вт', 2: 'ср', 3: 'чт', 4: 'пт'}

        file_code = f'{user_id}_{weekday_num}_{weekdays_lab[weekday_num]}.xlsx'
        file_name = f'Timetable ({weekdays[weekday_num]}).xlsx'

        persons_manager = Persons_manager(user_id)
        timetable_object = Timetable(persons_manager, weekday_num)
        timetable_object.return_xlsx(weekday_num, file_code)

    return send_from_directory('xlsx_files', file_code, download_name=file_name, as_attachment=True)

# Регистрация пользователя
@app.route('/display_timetable/registrate', methods=['POST', 'GET'])
def registrate():
    if request.method == 'POST':

        login = request.form['login']
        email = request.form['email']
        password = request.form['password']
        check_password = request.form['check_password']

        if password == check_password:

            try:
                add_user(login, email, password)
                user = Users_db.query.filter_by(login=login).first()
                userlogin = UserLogin().create(user)
                remember = True if request.form.get('remainme') else False
                login_user(userlogin, remember=remember)

            except:
                data_base.session.rollback()
                flash('Ошибка добавления в базу данных', category='registr_mistake')

        else:
            flash('Введенные пароли не совпадают', category='registr_mistake')

    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Авторизация пользователя в системе
@app.route('/display_timetable/enter', methods=['POST', 'GET'])
def enter():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']

        try:
            user = Users_db.query.filter_by(login=login).first()

            if user and check_password_hash(user.password, password):
                userlogin = UserLogin().create(user)
                remember = True if request.form.get('remainme') else False
                login_user(userlogin, remember=remember)
            else:
                flash('Неверный пароль', category='registr_mistake')
        except:
            flash('Пользователя с таким логином не существует', category='registr_mistake')

    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Выход пользователя из системы
@app.route('/display_timetable/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    flash('Теперь вы неавторизированы', category='registr_mistake')
    return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Декоратор разрывает соединение с БД
@app.teardown_appcontext
def close(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

if __name__ == '__main__':

    app.run(debug=True)