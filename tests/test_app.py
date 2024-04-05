import pytest
from build import create_app
from dotenv import load_dotenv
import os
import sqlite3
from flask import session

load_dotenv()
TEST_DATABASE = os.getenv('TEST_DATABASE')

# Set test data
test_username = "testuser"
test_password = "test1234"
test_title = "Test Recipe"
test_ingredients = "Ingredient 1"
test_instructions = "Step1"
test_notes = "Some notes"
recipe_id = 1


@pytest.fixture(scope='function')
def app():
    app = create_app(testing=True)
    app.config['TESTING'] = True
    return app


@pytest.fixture(scope='function')
def client(app):
    with app.test_client() as client:
        with client.session_transaction() as sess:

            # Mock the session data
            sess['_user_id'] = 1
        yield client


# Test accessing the dashboard without logging in
def test_dashboard_not_logged_in(client):
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'You need to log in first.' in response.data


# Test accessing the edit recipe page without logging in
def test_edit_recipe_not_logged_in(client):
    response = client.get('/edit_recipe/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'You need to log in first.' in response.data


# Test signing up as new user
def test_signup_new_user(client):
    response = client.post('/signup',
                           data={"username": test_username,
                                 "password": test_password})

    # Check user is redirected to home page
    assert response.status_code == 302


# Test valid message is shown with incorrect login details
def test_incorrect_login_details(client):
    response = client.post('/login',
                           data={'username': 'wrong', 'password': 'test'},
                           follow_redirects=True)
    assert b'Invalid username or password.' in response.data


# Test with correct login details
def test_correct_login_details(client):
    response = client.post('/login',
                           data={'username': test_username,
                                 'password': test_password},
                           follow_redirects=True)
    assert response.status_code == 200
    assert b'/dashboard' in response.data


# Test logged in user can add new recipe
def test_add_recipe(client):
    # Log in the user
    client.post('/login', data={'username': test_username,
                                'password': test_password})

    # Make a POST request to add a recipe
    response = client.post('/add_recipe',
                           data={'title': test_title,
                                 'ingredients': test_ingredients,
                                 'instructions': test_instructions,
                                 'notes': test_notes},
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == 200

    # Check recipe is in database
    conn = sqlite3.connect(TEST_DATABASE)
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM recipes WHERE title = 'Test Recipe';")
        result = cursor.fetchall()
    assert len(result) != 0


# Test logged in user can search for recipes
def test_search_recipe(client):
    # Log in the user
    client.post('/login', data={'username': test_username,
                                'password': test_password})

    # Make a GET request to search for the test recipe
    response = client.get(f'/search_recipes?{test_title}',
                          follow_redirects=True)
    assert response.status_code == 200

    # Check Test Recipe apears in the search results
    assert b'Test Recipe' in response.data


# Test update recipe
def test_update_recipe(client):
    # Log in the user
    client.post('/login', data={'username': test_username,
                                'password': test_password})
    # Make a POST request to update a specific recipe
    response = client.post(f'/edit_recipe/{recipe_id}',
                           data={'title': 'Test Recipe2',
                                 'ingredients': test_ingredients,
                                 'instructions': test_instructions,
                                 'notes': test_notes},
                           content_type='multipart/form-data',
                           follow_redirects=True)
    assert response.status_code == 200
    # Check updated recipe is in database
    conn = sqlite3.connect(TEST_DATABASE)
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM recipes WHERE title = 'Test Recipe2';")

        # Get first result as there will only be one returned value
        result = cursor.fetchone()

    # Result should contain a value
    assert len(result) != 0


# Test add a recipe to favorites
def test_add_to_favorites(client):
    # Log in the user
    client.post('/login', data={'username': test_username,
                                'password': test_password})
    # Make a POST request to update a specific recipe
    response = client.post(f'/add_to_favorites/{recipe_id}',
                           follow_redirects=True)
    assert response.status_code == 200

    # Check updated recipe is in database
    conn = sqlite3.connect(TEST_DATABASE)
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM favorites;")

        # Get first result as there will only be one returned value
        result = cursor.fetchone()

    # Result should contain a value
    assert len(result) != 0


# Test remove recipe from favorites
def test_remove_from_favorites(client):
    # Log in the user
    client.post('/login', data={'username': test_username,
                                'password': test_password})
    # Make a POST request to update a specific recipe
    response = client.post(f'/remove_from_favorites/{recipe_id}',
                           follow_redirects=True)
    assert response.status_code == 200

    # Check updated recipe is in database
    conn = sqlite3.connect(TEST_DATABASE)
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM favorites;")
        result = cursor.fetchall()

    # Should be no results found in favorites table
    assert len(result) == 0


# Test delete a recipe
def test_delete_recipe(client):
    # Log in the user
    client.post('/login', data={'username': test_username,
                                'password': test_password})
    # Make a POST request to update a specific recipe
    response = client.post(f'/delete_recipe/{recipe_id}',
                           follow_redirects=True)
    assert response.status_code == 200
    # Check updated recipe is in database
    conn = sqlite3.connect(TEST_DATABASE)
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM recipes;")
        result = cursor.fetchall()

    # Should be no results found in recipe table
    assert len(result) == 0


# Remove test data once tests complete
def test_empty_test_db():
    conn = sqlite3.connect(TEST_DATABASE)
    print("Deleting test data")
    with conn as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Loop through tables and delete content
        for table in tables:
            cursor.execute(f"DELETE FROM {table[0]};")

        connection.commit()
        print("Test data deleted.")
