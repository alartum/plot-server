from app import app, socketio
from config import Config

if __name__ == '__main__':
    socketio.run(app, port=Config.PORT, debug=Config.DEBUG, use_reloader=Config.DEBUG)