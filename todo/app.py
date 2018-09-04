from flask import Flask
from flask import render_template
from wtforms import Form, TextField, validators, StringField, SubmitField
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


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

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
            # Add user to table
            user = User(username)
            s.add(user)
            # Commit changes to DB
            s.commit()

            flash('Hello ' + username + '! You are now registered!')
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
    return redirect('/login')

app.secret_key = os.urandom(12)
