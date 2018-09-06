from flask import Flask
from flask import render_template, url_for
from wtforms import Form, TextField, validators, StringField, SubmitField, BooleanField
# Used by Userform.signup
from flask import session, flash, request, redirect, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from tabledef import *

app = Flask(__name__)

# An engine that the SQLAlchemy Session will use for DB connection
engine = create_engine('sqlite:///todo.db', echo=True)

class UserForm(Form):
    username = StringField('Username', validators=[validators.required()])

    # Protects against CSRF attacks (WTForms)
    def reset(self):
        blankData = MultiDict([ ('csrf', self.reset_crsf()) ])
        self.process(blankData)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    todos = []

    if session.get('logged_in'):
        Session = sessionmaker(bind=engine)
        s = Session()

        current_user = s.query(User).get(session['user_id'])

        if request.method == 'POST':
            new_todo = request.form['todo']
            #if todo not empty
            if new_todo != '':
                todo = Todo(content=new_todo, user=current_user, completed=0)
                s.add(todo)
                s.commit()

        user_todos = current_user.todos.all()

        for todo in user_todos:
            todos.append([todo.id, todo.content, todo.completed])

    return render_template('index.html', list=todos)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserForm(request.form)
    # If user has sent pressed submit button
    if request.method == 'POST':
        # Get username from form
        username = request.form['username']
        if form.validate():
            # Start session
            Session = sessionmaker(bind=engine)
            s = Session()

            query = s.query(User).filter(User.username.in_([username]))
            result = query.first()

            if result:
                flash('Username already exists, please log in.')
            else:
                # Add user to table
                user = User(username)
                s.add(user)
                # Commit changes to DB
                s.commit()
                flash('Hello ' + username + '! You are now registered, please log in to continue.')
            return redirect(url_for('login'))
        else:
            flash('Error: Username Required.')

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm(request.form)

    if request.method == 'POST':
        username = request.form['username']

        if form.validate():
            Session = sessionmaker(bind=engine)
            s = Session()
            query = s.query(User).filter(User.username.in_([username]))
            result = query.first()

            if result:
                session['logged_in'] = True
                session['user_id'] = result.id
                session['username'] = username
                flash('Welcome back, ' + session.get('username') + '!')
                return redirect(url_for('index'))
            else:
                flash('Username not valid. Please create an account or try again.')
        else:
            flash('Error: Username required for login.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['user_id'] = 0
    session['username'] = 'Guest'
    return redirect(url_for('login'))

@app.route('/complete')
def complete():
    if session.get('logged_in'):
        Session = sessionmaker(bind=engine)
        s = Session()

        todo_id = int(request.args.get('id'))
        todo = s.query(Todo).get(todo_id)
        todo.completed = 1
        s.commit()
    return redirect(url_for('index'))

@app.route('/uncomplete')
def uncomplete():
    if session.get('logged_in'):
        Session = sessionmaker(bind=engine)
        s = Session()

        todo_id = int(request.args.get('id'))
        todo = s.query(Todo).get(todo_id)
        todo.completed = 0
        s.commit()
    return redirect(url_for('index'))

@app.route('/delete')
def delete():
    if session.get('logged_in'):
        Session = sessionmaker(bind=engine)
        s = Session()

        todo_id = int(request.args.get('id'))
        todo = s.query(Todo).get(todo_id)
        s.delete(todo)
        s.commit()
    return redirect(url_for('index'))


app.secret_key = os.urandom(12)
app.run(host='0.0.0.0')
