from flask import (
    Blueprint, render_template,
    redirect, url_for, session,
    flash, jsonify, request
)
import sqlite3
import uuid
import bcrypt
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
DATABASE = os.getenv('DATABASE')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS')


def allowed_file(filename):
    return '.' in filename \
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_match(target, favorites):
    for favorite in favorites:
        if target == favorite[0]:
            return True
    return False


views = Blueprint('views', __name__)


# Routes
@views.route('/')
def index():
    return render_template('index.html')


@views.route('/search')
def search():
    return render_template('search.html')


@views.route('/signup', methods=['GET', 'POST'])
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
                return redirect(url_for('views.signup'))

        # Hash the password before storing it
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert the new user into the database
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            connection.commit()

        flash('Signup successful! Please log in.')
        return redirect(url_for('views.login'))

    return render_template('signup.html')


@views.route('/login', methods=['GET', 'POST'])
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
                return redirect(url_for('views.dashboard'))
            else:
                flash('Invalid username or password.')

    return render_template('login.html')


@views.route('/search_recipes', methods=['GET'], endpoint='search_recipes')
def search_recipes():
    # Get the search query from the URL parameters
    search_query = request.args.get('search', '')
    user_id = session['user_id']

    # Query the database for recipes matching the search query
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            'SELECT * FROM recipes WHERE title LIKE ? OR ingredients LIKE ?',
            ('%' + search_query + '%', '%' + search_query + '%'))
        search_results = cursor.fetchall()
        cursor.execute(
            'SELECT r.* FROM recipes r JOIN favorites f \
                ON r.id = f.recipe_id WHERE f.user_id=?',
            (user_id,))
        favorites = cursor.fetchall()

    return render_template('search_results.html',
                           search_results=search_results, favorites=favorites)


@views.route('/favorites', methods=['GET'], endpoint='favorites')
def favorites():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))

    user_id = session['user_id']

    # Get user's favorite recipes
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT r.* FROM recipes r JOIN favorites f ON r.id = f.recipe_id WHERE f.user_id=?',
                       (user_id,))
        favorites = cursor.fetchall()

    return render_template('favorites.html', favorites=favorites, user_id=user_id)


@views.route('/remove_from_favorites/<int:recipe_id>', methods=['POST'])
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


@views.route('/dashboard', methods=['GET', 'POST'], endpoint='dashboard')
def dashboard():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))

    return render_template('dashboard.html')


@views.route('/add_recipe', methods=['GET', 'POST'], endpoint='add_recipe')
def add_recipe():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))

    user_id = session['user_id']

    if request.method == 'POST':
        # Handle recipe addition
        title = request.form['title']
        ingredients = request.form['ingredients']
        instructions = request.form['instructions']
        notes = request.form['notes']

        # Initialize filename to None
        filename = None
        file = request.files['image']

        # Check if the post request has the file part
        # Flask submits an emty file is no file selected
        if file.filename != '':
            # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # Generate a unique filename using UUID
                filename = secure_filename(
                    str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                    )
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            else:
                # If not valid file type show message
                flash(
                    'Invalid file type. Allowed types are png, jpg, jpeg, gif.'
                    )

        # Save the recipe to the database with the filename (even if it's None)
        with sqlite3.connect(DATABASE) as connection:
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO recipes (title, ingredients, instructions, notes, user_id, image) VALUES (?, ?, ?, ?, ?, ?)',
                (title, ingredients, instructions, notes, user_id, filename))
            connection.commit()

        return jsonify({'success': True, 'message': 'Recipe added successfully.', 'redirect_url': url_for('views.add_recipe')})

    return render_template('add_recipe.html')


# route for viewing the user's recipes
@views.route('/your_recipes', methods=['GET'], endpoint='your_recipes')
def your_recipes():
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))

    user_id = session['user_id']

    # Display user's recipes
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM recipes WHERE user_id=?', (user_id,))
        recipes = cursor.fetchall()
        cursor.execute(
            'SELECT r.* FROM recipes r JOIN favorites f \
                ON r.id = f.recipe_id WHERE f.user_id=?',
            (user_id,))
        favorites = cursor.fetchall()

    return render_template('your_recipes.html',
                           recipes=recipes, favorites=favorites)

@views.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))

    user_id = session['user_id']

    # Handle recipe deletion
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM recipes WHERE id=? AND user_id=?', (recipe_id, user_id))
        connection.commit()

    return jsonify({'success': True, 'message': 'Recipe deleted successfully.', 'redirect_url': url_for('views.your_recipes')})


@views.route('/instructions', endpoint='instructions')
def instructions():
    return render_template('instructions.html')


# add to favorites
@views.route('/add_to_favorites/<int:recipe_id>', methods=['POST'])
def add_to_favorites(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_id = session['user_id']

    # Check if the recipe is already in favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM favorites \
                       WHERE user_id=? AND recipe_id=?',
                       (user_id, recipe_id))
        existing_favorite = cursor.fetchone()

        if existing_favorite:
            return jsonify(
                {'success': False, 'message': 'Recipe already in favorites'}
                )

    # Add the recipe to favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute(
            'INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)',
            (user_id, recipe_id))
        connection.commit()

    # Get the updated list of favorites
    with sqlite3.connect(DATABASE) as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT r.* FROM recipes r JOIN favorites f ON \
                       r.id = f.recipe_id WHERE f.user_id=?',
                       (user_id,))
        favorites = cursor.fetchall()

    return jsonify({'success': True, 'message': 'Recipe added to favorites',
                    'favorites': favorites})


@views.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in first.')
        return redirect(url_for('views.login'))

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

    # Return the template without flashing the message for the 'GET' request
    return render_template('edit_recipe.html', recipe=recipe, user_id=user_id)
