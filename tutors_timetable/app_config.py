# Конфигурация приложения. Инициализируются база данных (объект класса SQLAlchemy) и логин_мэнэджер (объект класса LoginManager).

from flask import Flask, send_from_directory, request, render_template, g, session, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin

SECRET_KEY = '2b33e737f8c95f06a4043c45a1cac30712c3d1ed'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

data_base = SQLAlchemy(app)
login_manager = LoginManager(app)
