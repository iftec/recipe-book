from flask import Flask
import sqlite3
import os
from os import path
from dotenv import load_dotenv
from .views import views, find_match

# Load enviroment variables from .env
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS')
DATABASE = os.getenv('DATABASE')


# Setup app 

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS
    app.register_blueprint(views, URL_PREFIX='/')
    app.jinja_env.filters['find_match'] = find_match
    create_tables()
    return app


def db_connect(DATABASE):
    return sqlite3.connect(DATABASE)


def create_tables():
    ## Use if statement to determine is testing then inject database name
    with db_connect(DATABASE) as connection:
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
