from app import app, db
import os
from flask import render_template, flash, redirect, url_for, request, jsonify, send_file
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app.forms import RegistrationForm
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    directory = os.path.normpath(os.path.join(app.config["PROTECTED_FOLDER"], current_user.username))
    
    projects=[]
    for filename in sorted(os.listdir(directory)):
        projects.append({"name": filename})
    return render_template('index.html', projects=projects)

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
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/list-files/<path:project>', methods=['GET'])
@login_required
def list_files(project):
    directory = os.path.join(app.config["PROTECTED_FOLDER"], current_user.username, project)
    print(directory)
    files=[]
    for filename in sorted(os.listdir(directory)):
        files.append(filename)
    return jsonify(files)

@app.route('/get-data/<path:data_path>', methods=['GET'])
@login_required
def get_data(data_path):

    path = os.path.join(app.config["PROTECTED_FOLDER"], current_user.username, data_path); 
    return send_file(path)