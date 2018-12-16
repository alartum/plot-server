from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

app = Flask(__name__)

from werkzeug.debug import DebuggedApplication
app.debug = True
app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(app, message_queue=Config.MESSAGE_QUEUE)

from app import routes