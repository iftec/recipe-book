from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from dotenv import load_dotenv
import sqlite3
from werkzeug.utils import secure_filename
import os
import uuid
import bcrypt

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY

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


@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

          # Check if the username already exists
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username=?', (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('signup'))

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            connection.commit()

        flash('Signup successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic for POST requests
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM users WHERE username=?', (username,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
                session['user_id'] = user[0]
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.')

    return render_template('login.html')



@app.route('/search_recipes', methods=['GET'])
def search_recipes():
    # Get the search query from the URL parameters
    search_query = request.args.get('search', '')

    # Query the database for recipes matching the search query
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM recipes WHERE title LIKE ? OR ingredients LIKE ?',
                       ('%' + search_query + '%', '%' + search_query + '%'))
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
        cursor.execute('SELECT r.* FROM recipes r JOIN favorites f ON r.id = f.recipe_id WHERE f.user_id=?',
                       (user_id,))
        favorites = cursor.fetchall()

    return render_template('favorites.html', favorites=favorites, user_id=user_id)


@app.route('/remove_from_favorites/<int:recipe_id>', methods=['POST'])
def remove_from_favorites(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_id = session['user_id']

    # Handle removing the recipe from favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM favorites WHERE user_id=? AND recipe_id=?', (user_id, recipe_id))
        connection.commit()

    return jsonify({'success': True, 'message': 'Recipe removed from favorites'})


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    return render_template('dashboard.html')


@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Handle recipe addition
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        notes = request.form['notes']

        # Initialize filename to None
        filename = None

        # Check if the post request has the file part
        if 'image' in request.files:
            file = request.files['image']
            # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # Generate a unique filename, e.g., using UUID
                filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Invalid file type. Allowed types are png, jpg, jpeg, gif.')

        # Save the recipe to the database with the filename (even if it's None)
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO recipes (title, ingredients, instructions, notes, user_id, image) VALUES (?, ?, ?, ?, ?, ?)',
                (title, ingredients, instructions, notes, user_id, filename))
            connection.commit()

        flash('Recipe added successfully.')
        return redirect(url_for('dashboard'))

    return render_template('add_recipe.html')


# route for viewing the user's recipes
@app.route('/your_recipes', methods=['GET'])
def your_recipes():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Display user's recipes
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM recipes WHERE user_id=?', (user_id,))
        recipes = cursor.fetchall()

    return render_template('your_recipes.html', recipes=recipes)


@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Handle recipe deletion
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM recipes WHERE id=? AND user_id=?', (recipe_id, user_id))
        connection.commit()

        flash('Recipe deleted successfully.')

    return redirect(url_for('dashboard'))


@app.route('/instructions')
def instructions():
    return render_template('instructions.html')


# add to favorites
@app.route('/add_to_favorites/<int:recipe_id>', methods=['POST'])
def add_to_favorites(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_id = session['user_id']

    # Check if the recipe is already in favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM favorites WHERE user_id=? AND recipe_id=?', (user_id, recipe_id))
        existing_favorite = cursor.fetchone()

        if existing_favorite:
            return jsonify({'success': False, 'message': 'Recipe already in favorites'})

    # Add the recipe to favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)', (user_id, recipe_id))
        connection.commit()

    # Get the updated list of favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT r.* FROM recipes r JOIN favorites f ON r.id = f.recipe_id WHERE f.user_id=?',
                       (user_id,))
        favorites = cursor.fetchall()

    return jsonify({'success': True, 'message': 'Recipe added to favorites', 'favorites': favorites})


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Retrieve recipe details for editing
    with sqlite3.connect(DATABASE) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM recipes WHERE id=? AND user_id=?', (recipe_id, user_id))
        recipe = cursor.fetchone()

    # Define the variable outside of the 'if request.method == 'POST':' block
    image_filename = None

    if request.method == 'POST':
        # Handle recipe editing
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        notes = request.form['notes']

        # Check if the request has a file part
        if 'image' in request.files:
            file = request.files['image']

            # Save the file if it has a filename
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Update the 'image' column in the database with the filename
                with sqlite3.connect(DATABASE) as connection:
                    cursor = connection.cursor()
                    cursor.execute('UPDATE recipes SET image=? WHERE id=? AND user_id=?',
                                   (filename, recipe_id, user_id))
                    connection.commit()
                    # Set the variable to be used later
                    image_filename = filename

        # Update other recipe details
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('UPDATE recipes SET title=?, ingredients=?, instructions=?, notes=? WHERE id=? AND user_id=?',
                           (title, ingredients, instructions, notes, recipe_id, user_id))
            connection.commit()

        # Debugging print statements
        print(f"Image filename: {image_filename}")
        print(f"Recipe image: {recipe[5]}")

    # Return the template without flashing the message for the 'GET' request
    return render_template('edit_recipe.html', recipe=recipe, user_id=user_id)
