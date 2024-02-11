from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key

# Define the path to the uploads folder
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# SQLite database setup
DATABASE = 'recipes.db'

def create_tables():
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                notes TEXT,
                image TEXT,  -- Add the new column for image
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        # Create the UPLOAD_FOLDER directory if it doesn't exist
        upload_folder_path = os.path.join(os.getcwd(), UPLOAD_FOLDER)
        os.makedirs(upload_folder_path, exist_ok=True)
        connection.commit()

create_tables()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            connection.commit()

        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
            user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            flash('Login successful!')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    # Get the search query from the URL parameters
    search_query = request.args.get('search', '')

    # Query the database for recipes matching the search query
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM recipes WHERE title LIKE ? OR ingredients LIKE ?', ('%' + search_query + '%', '%' + search_query + '%'))
        search_results = cursor.fetchall()

    return render_template('search_results.html', search_results=search_results)

@app.route('/favorites', methods=['GET'])
def favorites():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Get user's favorite recipes
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT r.* FROM recipes r JOIN favorites f ON r.id = f.recipe_id WHERE f.user_id=?', (user_id,))
        favorites = cursor.fetchall()

    return render_template('favorites.html', favorites=favorites, user_id=user_id)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']
     return render_template('dashboard.html')