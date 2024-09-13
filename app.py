from flask import Flask, render_template, request, redirect, url_for, session

from pymongo import MongoClient

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = '3f2b1f2c4e6a2c9a5d8e7d6f0a2d1c7b'

# MongoDB Atlas connection

client = MongoClient("mongodb+srv://muneeshpalanivel123:dZZg3obtIb75R6tu@cluster0.6wsbo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

db = client['login']

users_collection = db['users']


@app.route('/')

def index():

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = users_collection.find_one({'email': email})

        

        if user and check_password_hash(user['password'], password):

            session['email'] = email

            return redirect(url_for('dashboard'))

        else:

            return 'Invalid credentials. Please try again.'

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])

def signup():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        hashed_password = generate_password_hash(password)

        

        user = users_collection.find_one({'email': email})

        if user:

            return 'Email already exists!'

        

        users_collection.insert_one({'email': email, 'password': hashed_password})

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/dashboard')

def dashboard():

    if 'email' in session:

        return f"Welcome, {session['email']}!"

    else:

        return redirect(url_for('login'))


@app.route('/logout')

def logout():

    session.pop('email', None)

    return redirect(url_for('login'))


if __name__ == '__main__':

    app.run(debug=True)