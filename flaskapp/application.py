from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
import boto3
import datetime
import sys
from wtforms import Form, StringField, PasswordField, validators, SelectField
from passlib.hash import sha256_crypt
from functools import wraps

application = Flask(__name__)
app = application
app.secret_key='TheSecretKey!'

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

class RegisterCollection(Form):
    collection = StringField('Enter new collection name', [validators.length(min=4, max=50)])

@app.route('/collections', methods=['GET', 'POST'])
@is_logged_in
def collections():
    form = RegisterCollection(request.form)
    ddb = boto3.client('dynamodb', region_name='eu-west-1')
    email = session['username']
    try:
        response = ddb.get_item(
            Key={
                'email': {
                    'S': email,
                },
            },
            TableName='users',
        )

        collections = response['Item']['collections']['L']

    except:
        collections = []

    if request.method == 'POST' and request.form['btn'] == 'create' and form.validate():
        collection = form.collection.data
        for collectionexist in collections:
            if collection == collectionexist['S']:
                flash('Collection already defined', 'danger')
                return redirect(url_for('collections'))
        try:
            response = ddb.update_item(
                UpdateExpression="SET collections = list_append(collections, :col)",
                ExpressionAttributeValues={
                    ':col': {
                        "L": [
                            {"S": collection}
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
            return redirect(url_for('collections'))
        except:
            flash('Could not create new collection', 'danger')
            return redirect(url_for('collections'))

    elif request.method == 'POST':
        collectiondelete = request.form['btn']
        i = 0
        for collection in collections:
            if collectiondelete == collection['S']:
                try:
                    response = ddb.update_item(
                        UpdateExpression="REMOVE collections[%(collection)d]" % {'collection': i},
                        Key={
                            'email': {
                                'S': email,
                            },
                        },
                        TableName='users',
                    )
                    return redirect(url_for('collections'))
                except:
                    flash('Could not delete collection', 'danger')
                    return redirect(url_for('collections'))
            i = i+1
        return render_template('collections.html', form=form, collections=collections)

    else:
        return render_template('collections.html', form=form, collections=collections)


@app.route('/photos/<string:id>/')
@is_logged_in
def photos(id):
    return render_template('photo.html', collection=id)


class RegisterForm(Form):
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
@is_logged_in
def register():
    form = RegisterForm(request.form)
    ddb = boto3.client('dynamodb', region_name='eu-west-1')
    email = form.email.data
    emailexist = ''
    try:
        response = ddb.get_item(
            Key={
                'email': {
                    'S': email,
                },
            },
            TableName='users',
        )
        emailexist = response['Item']['email']['S']
    except:
        emailexist = ''

    if request.method == 'POST' and form.validate():
        if emailexist != '':
            flash('email address already registered', 'danger')
            return redirect(url_for('register'))
        else:
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
                    'collections': {
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
        ddb = boto3.client('dynamodb', region_name='eu-west-1')
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
    collection = SelectField('collection', [validators.length(min=6, max=200)])

@app.route('/registeripcam', methods=['GET', 'POST'])
@is_logged_in
def registeripcam():
    form = RegisterIpcam(request.form)
    ddb = boto3.client('dynamodb', region_name='eu-west-1')
    email = session['username']
    if request.method == 'POST':
        if request.form['btn'] == 'register':
            ipcam = form.ipcam.data
            ipcamvid = form.ipcamvid.data
            collection = form.collection.data

            response = ddb.get_item(
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )

            ipcamlist = response['Item']['ipcam']['L']

            for ipcamexist in ipcamlist:
                if ipcam == ipcamexist['M']['Ipcam']['S']:
                    flash('IP camera already defined', 'danger')
                    return redirect(url_for('registeripcam'))

            try:
                response = ddb.update_item(
                    UpdateExpression="SET ipcam = list_append(ipcam, :cam), ipcamvid = list_append(ipcamvid, :camvid)",
                    ExpressionAttributeValues={
                        ':cam': {
                            "L": [
                                {"M": {"Ipcam": {"S": ipcam}, "Collection": {"S": collection}, "Detection": {"S": 'false'}}}
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
                flash('Could not add the IP camera', 'danger')
                return redirect(url_for('registeripcam'))

        elif 'rekon-fbpics' in request.form['btn']:
            image = request.form['btn']
            response = ddb.get_item(
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )

            ipcamlist = response['Item']['ipcam']['L']
            i = 0
            for ipcamexist in ipcamlist:
                if image == ipcamexist['M']['Detection']['S']:
                    ipcam = ipcamexist['M']['Ipcam']['S']
                    collectionName = ipcamexist['M']['Collection']['S']
                    print(ipcam + '-' + collectionName)
                    try:
                        response = ddb.update_item(
                            UpdateExpression="SET ipcam = :cam",
                            ExpressionAttributeValues={
                                ':cam': {
                                    "L": [
                                        {"M": {"Ipcam": {"S": ipcam}, "Collection": {"S": collectionName},
                                               "Detection": {"S": 'false'}}}
                                    ]
                                }
                            },
                            Key={
                                'email': {
                                    'S': email,
                                },
                            },
                            TableName='users',
                        )
                        return redirect(url_for('registeripcam'))
                    except Exception as e:
                        print(e)
                        flash('Could not acknowledge image', 'danger')
                        return redirect(url_for('registeripcam'))

                i = i + 1
        else:
            ipcamvid = request.form['btn']
            response = ddb.get_item(
                Key={
                    'email': {
                        'S': email,
                    },
                },
                TableName='users',
            )

            ipcamlist = response['Item']['ipcamvid']['L']
            i = 0
            for ipcamexist in ipcamlist:
                if ipcamvid == ipcamexist['S']:
                    try:
                        response = ddb.update_item(
                            UpdateExpression='REMOVE ipcam[%(ipcam)d], ipcamvid[%(ipcamvid)d]' % {'ipcam': i,
                                                                                                  'ipcamvid': i},
                            Key={
                                'email': {
                                    'S': email,
                                },
                            },
                            TableName='users',
                        )
                        return redirect(url_for('registeripcam'))
                    except:
                        flash('Could not delete the IP camera', 'danger')
                        return redirect(url_for('registeripcam'))

                i = i + 1
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
            collections = response['Item']['collections']['L']

        except:
            ipcamlist = []
            collections = []

        return render_template('registeripcam.html', ipcam2lists=zip(ipcamlist, ipcamvidlist), camcollections=collections)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)