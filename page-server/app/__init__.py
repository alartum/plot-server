from flask import Flask
from config import Config
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

app = Flask(__name__, static_folder=Config.STATIC_FOLDER)
app.config.from_object(Config)
socketio = SocketIO(app)
if not os.path.exists(app.config["PROTECTED_FOLDER"]):
    os.makedirs(app.config["PROTECTED_FOLDER"])
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app)
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models, errors