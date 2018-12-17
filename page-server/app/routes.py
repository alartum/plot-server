from app import app, db, socketio
import os
from flask import render_template, flash, redirect, url_for, request, jsonify, send_file
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Project, File
from app.forms import RegistrationForm
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    project_names = [p.name for p in projects]
    key = db.session.query(User.key).filter_by(id=current_user.id).one()
    return render_template('index.html', project_names=project_names, key=key[0])

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not is_safe_url(next_page):
            return flask.abort(400)
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/list-files/<string:project_name>', methods=['GET'])
@login_required
def list_files(project_name):
    files = db.session.query(File.name).select_from(File, Project).filter(Project.user_id==current_user.id, Project.name==project_name).all()
    file_names = [f[0] for f in files]
    return jsonify(file_names)

@app.route('/get-data/<string:project_name>/<path:file_name>', methods=['GET'])
@login_required
def get_data(project_name, file_name):
    file = db.session.query(File).select_from(File, Project).filter(File.name==file_name, Project.name==project_name, Project.user_id==current_user.id).one()

    return send_file(file.get_path())


from flask_socketio import send, emit, join_room, leave_room
@socketio.on('my event')
@login_required
def handle_my_custom_event(json):
    print(current_user)
    print('received json: ' + str(json))
    send(json)

@app.route('/subscribe/<string:project_name>/<path:file_name>', methods=['GET'])
@login_required
def subscribe(project_name, file_name):
    file_id = db.session.query(File.id).select_from(File, Project).filter(File.name==file_name, Project.name==project_name, Project.user_id==current_user.id).one()
    join_room(str(file_id), namespace="/files")
    return "You've been subscribed!"

@app.route('/unsubscribe/<string:project_name>/<path:file_name>', methods=['GET'])
@login_required
def unsubscribe(project_name, file_name):
    file_id = db.session.query(File.id).select_from(File, Project).filter(File.name==file_name, Project.name==project_name, Project.user_id==current_user.id).one()
    leave_room(str(file_id), namespace="/files")
    return "You've been unsubscribed!"

from cryptography.fernet import Fernet
import json
@app.route('/api/upload/<string:mode>', methods=['POST'])
def upload(mode):
    # Get data as strings
    data = json.loads(request.data.decode('utf-8'))
    username = data['user']
    raw = data['raw'].encode('utf-8')
    key = db.session.query(User.key).filter_by(username=username).one()[0]
    encoder = Fernet(key)
    # Check credentials
    raw = encoder.decrypt(raw).decode('utf-8')
    if raw.startswith(username):
        raw = raw[len(username):]
        info = json.loads(raw)
        print(info)
        # for file, values in info.items():
            
        #     with open 

        return "Uploaded"
    else:
        return "Auth error"