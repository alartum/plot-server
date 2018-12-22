from app import app, db, socketio
import os
from flask import render_template, flash, redirect, url_for, request, jsonify, send_file
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Project, File
from app.forms import RegistrationForm
from werkzeug.urls import url_parse
from sqlalchemy.sql.expression import join


@app.after_request
def http_to_https(response):
    if response:
        status = response.status
        print("<<[START] RESPONSE {} >>".format(status)) 
        # print(response.status)
        print(response.headers)
        # print(response.get_data())
        print("<<[END] RESPONSE {} >>".format(status))
    # response.location = response.location.replace("http://", "https://")
    return response

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    project_names = [p.name for p in projects]
    key = db.session.query(User.key).filter_by(id=current_user.id).scalar()
    if key:
        key = key.decode('utf-8')
    else:
        key = ""

    return render_template('home.html', project_names=project_names, key=key)

@app.route('/login', methods=['GET', 'POST'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).scalar()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
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
        user = User(username=form.username.data)#, email=form.email.data)
        user.set_password(form.password.data)
        user.generate_key()
        db.session.add(user)
        db.session.commit()
        flash("You've been successfully registered.")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

from functools import wraps
def print_url(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        print(request.url_root)
        return func(*args, **kwargs)
    return decorated

@app.route('/list-files/<string:project_name>', methods=['GET'])
@login_required
def list_files(project_name):
    files = db.session.query(File.name).select_from(join(File, Project)).filter(Project.user_id==current_user.id, Project.name==project_name).all()
    file_names = [f[0] for f in files]

    return jsonify(file_names)

@app.route('/get-data/<string:project_name>/<path:file_name>', methods=['GET'])
@login_required
def get_data(project_name, file_name):
    file = db.session.query(File).select_from(join(File, Project)).filter(File.name==file_name, Project.name==project_name, Project.user_id==current_user.id).one()

    return send_file(file.get_path())

from cryptography.fernet import Fernet
import json
@app.route('/api/prepare/<string:mode>', methods=['POST'])
def prepare(mode):
    if mode == "append":
        fmode = "a"
    elif mode == "refresh":
        fmode = "w"
    else:
        return "Wrong mode specifier"

    # Get data as strings
    data = json.loads(request.data.decode('utf-8'))
    username = data['user']
    user = db.session.query(User).filter_by(username=username).scalar()
    if not user:
        return "User can't be found"
    raw = data['raw'].encode('utf-8')
    key = user.key
    encoder = Fernet(key)
    # Check credentials
    raw = encoder.decrypt(raw).decode('utf-8')

    if not raw.startswith(username):
        return "Auth error"
    else:
        raw = raw[len(username):]
        info = json.loads(raw)
        
        # Create project if doesn't exist
        project_name = info[0]
        pr = user.projects.filter_by(name=project_name).scalar()
        if not pr:
            pr = Project(name=project_name, user_id=user.id)
            db.session.add(pr)

        file_names = info[1]
        bad_files = pr.files.filter(~File.name.in_(file_names)).all()
        for file in bad_files:
            path = file.get_path()
            if os.path.exists(path):
                os.remove(path)
            db.session.delete(file)    
        
        for fname in file_names:
            file = pr.files.filter_by(name=fname).scalar()
            if not file:
                file = File(name=fname, project_id=pr.id)
                db.session.add(file)
            open(file.get_path(), fmode).close()
        db.session.commit()
        return "Project is ready for work"

@app.route('/api/upload', methods=['POST'])
def upload():
    # Get data as strings
    data = json.loads(request.data.decode('utf-8'))
    username = data['user']
    user = db.session.query(User).filter_by(username=username).scalar()
    if not user:
        return "User can't be found"
    raw = data['raw'].encode('utf-8')
    key = user.key
    encoder = Fernet(key)
    # Check credentials
    raw = encoder.decrypt(raw).decode('utf-8')

    if not raw.startswith(username):
        return "Auth error"
    else:
        raw = raw[len(username):]
        info = json.loads(raw)
        
        # Create project if doesn't exist
        project_name = info[0]
        pr = user.projects.filter_by(name=project_name).scalar()
        if not pr:
            return "Project is not found. Prepare it first."

        frames = info[1]
        state = ""
        for fname, values in frames.items():
            file = pr.files.filter_by(name=fname).scalar()
            if not file:
                state += "File {} is not found.\n".format(fname)
            else:
                # Write to file
                str_values = ', '.join(map(str, values))
                with open(file.get_path(), "a") as f:
                    f.write(str_values  + '\n')
                # And emit new data
                # print(">>   EMIT: ", project_name + "/" + fname, str_values, "file:"+str(file.id))
                socketio.emit(project_name + "/" + fname, str_values, room="file:"+str(file.id), namespace="/files")
        return state + "Frames successfully added."

import functools
from flask_socketio import disconnect
def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

from flask_socketio import send, emit, join_room, leave_room
@socketio.on('subscribe')
@authenticated_only
def subscribe(path):
    path = str(path)
    project_name, file_name = path.split('/', 1)
    file_id = db.session.query(File.id).select_from(join(File, Project)).filter(File.name==file_name, Project.name==project_name, Project.user_id==current_user.id).scalar()
    if file_id:
        join_room("file:"+str(file_id), namespace="/files")
        print('>User {} subscribed to {} ({})'.format(current_user.username, path, "file:"+str(file_id)))

@socketio.on('unsubscribe')
@authenticated_only
def unsubscribe(path):
    path = str(path)
    project_name, file_name = path.split('/', 1)
    file_id = db.session.query(File.id).select_from(join(File, Project)).filter(File.name==file_name, Project.name==project_name, Project.user_id==current_user.id).scalar()
    if file_id:
        leave_room("file:"+str(file_id), namespace="/files")
        print('>User {} unsubscribed from {} ({})'.format(current_user.username, path, "file:"+str(file_id)))