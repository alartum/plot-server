from app import app, socketio, db
from flask import request
from cryptography.fernet import Fernet
import os

# key = Fernet.generate_key()
key = b'mNZD3j6DvoHimjoGlXK4pQ7GJrVM9r03Q2gu0QLAu14='
f = Fernet(key)
print('Fernet key:', key)

@app.route('/')
def index():
    return 'Index Page'

@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@app.route('/prepare/<string:user>/<string:project>', methods=['POST'])
def prapare(user, project):
    print(user, project)
    data = request.get_data()
    print('Message:', f.decrypt(data))
    return "Accepted"