# Дополнительный модуль приложения. Изменение характеристик тьюторов и учеников с сохранением изменений в db

from flask import Blueprint
from app_config import *

# Импорт классов, необходимых для взаимодействия с данными учеников и тьюторов
from persons_manager import Persons_manager
from timetable import Options
from interface_funcs import *

tm_settings = Blueprint('tm_settings', __name__, template_folder='templates', static_folder='static')

# Генерирует страницу настроек в завсимости об информации об актуальной таблице настроек, находящейся в сессии
@tm_settings.route('/')
def index():

    if current_user.is_authenticated:

        user_id = current_user.get_id()
        persons_manager = Persons_manager(user_id)
        options = Options(persons_manager)

        tutor_options = options.return_tutor_options()
        lesson_options = options.return_timetable_options()

        tutors_list = persons_manager.tutors_list
        students_list = persons_manager.students_list
        plugs = persons_manager.create_plug_list(space=False)
        weekdays = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ']

        return render_template('settings.html', tutors_list=tutors_list,
                               students_list=students_list,
                               plugs=plugs,
                               lesson_options = lesson_options,
                               tutor_options=tutor_options,
                               weekdays=weekdays,
                               actual_setting_table=session['actual_setting_table'])

    else:
        flash('Авторизируйтесь для полноценной работы с приложением', category='need_login')
        return redirect(url_for('display_timetable', weekday_num=session['weekday_num']))

# Изменение информации в сессии об актуальной таблице настроек. Происходит при выборе пользователем пункта в выпадающем списке
@tm_settings.route('/change_actual_table', methods=['POST', 'GET'])
def change_actual_table():

    data = request.get_json()
    session['actual_setting_table'] = data['actual_table']

    results = {'status': 'changed_table'}
    return jsonify(results)

# Удаление ученика, тьютора или урока из БД
@tm_settings.route('/delete/<category>/<element_id>')
def delete(category, element_id):
    db_types = {'tutor': Tutor_db, 'student': Timetable_content_db, 'plug': Timetable_content_db,'lesson': Lessons_db}
    db = db_types[category]
    session['actual_setting_table'] = category

    try:
        db.query.filter(db.content_id==element_id).delete()
        data_base.session.flush()
        data_base.session.commit()
    except:
        data_base.session.rollback()
        flash('Произошла ошибка при работе с базой данных')

    return redirect(url_for('tm_settings.index'))

# Внесение в БД нового тьютора
@tm_settings.route('/new_tutor', methods=['post', 'get'])
def new_tutor():

    if request.method == 'POST':

        user_id = current_user.get_id()
        tutor_id = str(uuid.uuid4())
        name = request.form['name']
        ward = request.form.get('option')

        tutor = Tutor_db(user=user_id,
                         content_id=tutor_id,
                         name=name,
                         ward_id=ward,
                         absent=0,
                         first_lesson=0,
                         last_lesson=7)

        try:
            data_base.session.add(tutor)
            data_base.session.flush()
            data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Произошла ошибка при работе с базой данных')

    return redirect(url_for('tm_settings.index'))

# Внесение в БД нового ученика или внеурочной работы
@tm_settings.route('/new_tm_content', methods=['post', 'get'])
def new_tm_content():

    if request.method == 'POST':

        category = session['actual_setting_table']
        category = 'user_plug' if category == 'plug' else 'student'

        parametrs = {'user_plug': [None, None, None, None], 'student': [1, 0, 0, 5]}

        user_id = current_user.get_id()
        content_id = str(uuid.uuid4())
        name = request.form['name']

        content = Timetable_content_db(user=user_id,
                         content_id=content_id,
                         name=name,
                         category = category,
                         combine = parametrs[category][0],
                         absent=parametrs[category][1],
                         first_lesson=parametrs[category][2],
                         last_lesson=parametrs[category][3])

        try:
            data_base.session.add(content)
            data_base.session.flush()
            data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Произошла ошибка при работе с базой данных')

    return redirect(url_for('tm_settings.index'))

# Внесение в БД нового урока
@tm_settings.route('/new_lesson', methods=['post', 'get'])
def new_lesson():

    if request.method == 'POST':

        user_id = current_user.get_id()
        content_id = str(uuid.uuid4())
        tutor_id = request.form['tutor_id']
        weekday_num = request.form['weekday_num']
        lesson_num = request.form['lesson_num']
        first_student, second_student = divide_option(request.form['option'])

        session['actual_setting_table'] = tutor_id

        lesson = Lessons_db(user=user_id,
                         content_id=content_id,
                         tutor_id = tutor_id,
                         category = 'personal',
                         weekday_num = weekday_num,
                         lesson_num = lesson_num,
                         first_student = first_student,
                         second_student = second_student)

        try:
            data_base.session.add(lesson)
            data_base.session.flush()
            data_base.session.commit()
        except:
            data_base.session.rollback()
            flash('Произошла ошибка при работе с базой данных')

    return redirect(url_for('tm_settings.index'))

# Изменение параметра комбайн у ученика
@tm_settings.route('/change_combine/<student_id>')
def change_combine(student_id):

    try:
        combine = Timetable_content_db.query.filter(Timetable_content_db.content_id == student_id).first().combine
        Timetable_content_db.query.filter(Timetable_content_db.content_id == student_id).first().combine = 1 - combine

        data_base.session.flush()
        data_base.session.commit()
    except:
        data_base.session.rollback()
        flash('Ошибка добавления в базу данных', category='registr_mistake')

    return redirect(url_for('tm_settings.index'))

# Изменение параметров ученика, тьютора или студента
@tm_settings.route('/change_settings', methods=['POST', 'GET'])
def change_settings():

    if request.method == 'POST':
        db_types = {'tutor': Tutor_db, 'student': Timetable_content_db,
                    'plug': Timetable_content_db, 'lesson': Lessons_db}
        attributes = {'name': 'name', 'first': 'first_lesson',
                     'last': 'last_lesson', 'option': 'ward_id',
                     'number': 'lesson_num', 'weekday': 'weekday_num',
                     'students': ['first_student', 'second_student']}

        data = request.get_json()
        category = data['category']
        attribute = data['attribute']
        element_id = data['element_id']
        value = data['value']

        if value.isdigit():
            value = int(value)
        if attribute == 'students':
            first_student, second_student = divide_option(value)

        db = db_types[category]
        attr = attributes[attribute]

        try:
            if attribute == 'students':
                db.query.filter(db.content_id == element_id).update({attr[0]: first_student})
                db.query.filter(db.content_id == element_id).update({attr[1]: second_student})
            else:
                db.query.filter(db.content_id == element_id).update({attr: value})

            data_base.session.flush()
            data_base.session.commit()

            results = {'status': 'changed'}
        except:
            results = {'status': 'db_mistake'}
    else:
        results = {'status': 'pass'}

    return jsonify(results)
