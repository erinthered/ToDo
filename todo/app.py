from flask import Flask
from flask import render_template
from wtforms import Form, TextField, validators, StringField, SubmitField
# Used by Userform.signup
from flask import session, flash, request, redirect, abort
from sqlalchemy.orm import sessionmaker
import os

app = Flask(__name__)

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
            # Start DB session
            Session = sessionmaker(bind=engine)
            s = Session()
            # Add user to table
            user = User(username)
            s.add(user)
            # Commit changes to DB
            s.commit

            flash('Hello ' + username + '! You are now registered!')
    else:
        flash('Error: Username Required.')

    return render_template('signup.html', form=form)


app.secret_key = os.urandom(12)
