import os
from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Access the secret key and MongoDB URI from environment variables
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')  # Fallback in case it's not set

# MongoDB Atlas connection
mongo_uri = os.getenv('MONGO_URI')
if not mongo_uri:
    raise ValueError("No MongoDB URI found in environment variables")

try:
    client = MongoClient(mongo_uri)
    db = client['login']
    users_collection = db['users']
except Exception as e:
    raise Exception(f"Error connecting to MongoDB: {str(e)}")


@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            user = users_collection.find_one({'email': email})
        except Exception as e:
            return f"Database query failed: {str(e)}"

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
        
        # Use sha256 as the hashing method
        hashed_password = generate_password_hash(password, method='sha256')

        try:
            user = users_collection.find_one({'email': email})
        except Exception as e:
            return f"Database query failed: {str(e)}"

        if user:
            return 'Email already exists!'

        try:
            users_collection.insert_one({'email': email, 'password': hashed_password})
        except Exception as e:
            return f"Failed to insert user: {str(e)}"

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
