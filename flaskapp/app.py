from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
import boto3, datetime
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#  Session timeout
@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    session.modified = True

@app.route('/home')
@is_logged_in
def home():
    return render_template('index.html')

@app.route('/')
@is_logged_in
def index():
    return render_template('index.html')

@app.route('/collections')
@is_logged_in
def collections():
    return render_template('collections.html')

class RegisterForm(Form):
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        ddb = boto3.client('dynamodb')
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        response = ddb.put_item(
            Item={
                'email': {
                    'S': email,
                },
                'password': {
                    'S': password,
                },
                'ipcam': {
                    'L': [],
                },
                'ipcamvid': {
                    'L': [],
                },
            },
            TableName='users',
        )
        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get form fields
        email = request.form['email']
        password_candidate = request.form['password']
        ddb = boto3.client('dynamodb')
        try:
            response = ddb.get_item(
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )

            password = response['Item']['password']['S']

            # compare pwd
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = email

                flash('you are logged in', 'success')
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials'
                return render_template('login.html', error=error)

        except KeyError:
            error = 'Invalid credentials!'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('you are logged out', 'success')
    return redirect(url_for('login'))

class RegisterIpcam(Form):
    ipcam = StringField('ipcam', [validators.length(min=6, max=200)])
    ipcamvid = StringField('ipcamvid', [validators.length(min=6, max=200)])

@app.route('/registeripcam', methods=['GET', 'POST'])
@is_logged_in
def registeripcam():
    form = RegisterIpcam(request.form)
    ddb = boto3.client('dynamodb')
    email = session['username']
    if request.method == 'POST' and form.validate():
        ipcam = form.ipcam.data
        ipcamvid = form.ipcamvid.data
        try:
            response = ddb.update_item(
                UpdateExpression="SET ipcam = list_append(ipcam, :cam), ipcamvid = list_append(ipcamvid, :camvid)",
                ExpressionAttributeValues={
                    ':cam': {
                        "L": [
                            {"S": ipcam}
                        ]
                    },
                    ':camvid': {
                        "L": [
                            {"S": ipcamvid}
                        ]
                    },
                },
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )
            return redirect(url_for('registeripcam'))
        except:
            flash('Could add the IP camera', 'danger')
            return redirect(url_for('registeripcam'))

    else:
        try:
            response = ddb.get_item(
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )

            ipcamlist = response['Item']['ipcam']['L']
            ipcamvidlist = response['Item']['ipcamvid']['L']

        except:
            ipcamlist = []
        return render_template('registeripcam.html', ipcam2lists=zip(ipcamlist, ipcamvidlist))

if __name__ == '__main__':
    app.secret_key='TheSecretKey!'
    app.run(host='0.0.0.0', debug=True)