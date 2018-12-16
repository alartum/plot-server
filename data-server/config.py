import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MESSAGE_QUEUE = os.environ.get('MESSAGE_QUEUE') or 'redis://localhost:6379/0'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://localhost:5432/plot_server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False