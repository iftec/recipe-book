from flask import Flask
import sqlite3
import os
from os import path
from dotenv import load_dotenv


# Load enviroment variables from .env
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = os.getenv('UPLOAD_PATH')
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS')
DATABASE = os.getenv('DATABASE')
TEST_DATABASE = os.getenv('TEST_DATABASE')

# Used to switch database if testing
is_testing = False


def create_app(testing=False):
    # Set global variable recived from test file
    global is_testing
    is_testing = testing

    # Define app
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

    from .views import views, find_match
    app.register_blueprint(views, URL_PREFIX='/')

    # Define custom filter for modifying buttons (see views: def find_match)
    app.jinja_env.filters['find_match'] = find_match
    create_tables()
    return app


# Connection to database
def db_connect():
    if is_testing is False:
        conn = sqlite3.connect(DATABASE)
    else:
        conn = sqlite3.connect(TEST_DATABASE)
    return conn


# Create tables if required
def create_tables():
    with db_connect() as connection:
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
