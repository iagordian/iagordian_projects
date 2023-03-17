# Импорт моделей db
from data_base import *

# Класс Tutor содержит информацию о тьюторах и набор объектов Lesson
# При инициализации принимает объект, возвращаемый базой данных
class Tutor:

     def __init__(self, data):
         self.id = data.content_id
         self.name = data.name
         self.absent = bool(data.absent)
         self.first_lesson = data.first_lesson
         self.last_lesson = data.last_lesson

         if data.stud_data and data.stud_data.content_id != 'space':
            self.student = data.stud_data
            self.option = self.student.content_id
         else:
             self.student = None
             self.option = 'space'

         lessons = []
         for lesson_data in data.lesson_data:
             lesson = Lesson(lesson_data)
             lessons.append(lesson)

         self.lessons = lessons

     def return_lessons_by_weekday(self, category, weekday_num):
        exit_lessons = [lesson for lesson in self.lessons if lesson.category==category and lesson.weekday_num==weekday_num]
        return exit_lessons

# Класс Lesson хранит информацию об уроке
# При инициализации принимает объект, возвращаемый базой данных
class Lesson:

    def __init__(self, data):
        self.id = data.content_id
        self.category = data.category
        self.weekday_num = data.weekday_num
        self.lesson_num = data.lesson_num
        self.content = self.get_content(data)
        self.option = '/'.join([content.content_id for content in self.content])

    def get_content(self, data):

        students = []
        for stud_id in [data.first_student, data.second_student]:
            student_data = Timetable_content_db.query.filter(Timetable_content_db.content_id==stud_id).first()
            if student_data:
                students.append(student_data)
        return students

# Класс Persons_manager представляет собой интерфейс для взаимодействия с базой данных
# При инициализации принимает id авторизированного пользователя или информацию о том, что пользователь неавторизирован
class Persons_manager:

    def __init__(self, user_id):
        self.user_id = user_id
        self.tutors_list = self.create_tutor_list()
        self.students_list = self.create_students_list()
        self.plugs = self.create_plug_list()

    def create_tutor_list(self):
        tutors_data = Users_db.query.filter_by(user_id=self.user_id).first().tutor_data

        tutor_list = [Tutor(data) for data in tutors_data]
        tutor_list = sorted(tutor_list, key=lambda tutor: tutor.name)
        return tutor_list

    def create_students_list(self):
        students_data = Users_db.query.filter_by(user_id=self.user_id).first().content_data

        students_list = [student_data for student_data in students_data if student_data.category=='student']
        students_list = sorted(students_list, key=lambda student: student.name)
        return students_list

    def create_plug_list(self, space=True):
        plugs_data = Users_db.query.filter_by(user_id=self.user_id).first().content_data

        plug_list = [plug_data for plug_data in plugs_data if plug_data.category=='user_plug']
        plug_list = sorted(plug_list, key=lambda student: student.name)

        if space:
            system_plug_data = Timetable_content_db.query.filter_by(content_id='space').first()
            plug_list.insert(0, system_plug_data)

        return plug_list

    def get_present_persons_list(self, key):
        persons_lists = {'tutor': self.tutors_list, 'student': self.students_list}
        actual_person_list = [person for person in persons_lists[key] if not person.absent]

        return actual_person_list