from data_base import Users_db

# Класс описывает состояние авторизированного пользователя
class UserLogin:

    def from_db(self, user_id):
        self.user = Users_db.query.filter_by(user_id=user_id).first()
        return self

    def create(self, user):
        self.user = user
        return self

    def is_authenticated(self):
        if self.user:
            return True
        else:
            return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user.user_id)

    def get_login(self):
        return str(self.user.login)