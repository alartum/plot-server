from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from cryptography.fernet import Fernet

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    key = db.Column(db.Binary(32))
    password_hash = db.Column(db.String(128))
    projects = db.relationship('Project', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_key(self):
        self.key = Fernet.generate_key()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    last_update = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    frames_saved = db.Column(db.Integer, default=0, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    files = db.relationship('File', backref='base_project', lazy='dynamic')

    def __repr__(self):
        return '<Project {} ({})>'.format(self.name, self.last_update)

import os
from config import Config

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    def get_path(self):
        path = os.path.normpath(os.path.join(Config.PROTECTED_FOLDER, str(self.id)))
        open(path, 'a').close()
        return path

    def __repr__(self):
        return '<File {} ({})>'.format(self.name, self.id)