import pytest
import sqlite3
from app import app


@pytest.fixture
def client():
    # Create a test client using Flask's test_client() method
    with app.test_client() as client:
        yield client
        

def test_signup(client):
    # Test the signup route
    response = client.post('/signup', data={'username': 'testuser', 'password': '<PASSWORD>'}, follow_redirects=True)
    assert response.status_code == 200


def test_login(client):
    # Test the login route
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'You need to log in first.' not in response.data



def test_login_invalid_credentials(client):
    # Test login with invalid credentials
    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpassword'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid username or password.' in response.data


def test_add_recipe(client):
    # Test adding a recipe
    # First, perform a login
    client.post('/login', data={'username': 'testuser', 'password': '<PASSWORD>'}, follow_redirects=True)
    # Then, add a recipe
    response = client.post('/add_recipe', data={'name': 'testrecipe', 'description': 'test description', 'time': '10', 'difficulty': '1', 'ingredients': 'test ingredients', 'directions': 'test directions'}, follow_redirects=True)
    assert response.status_code == 200
    
   



def test_delete_recipe(client):
    # Test deleting a recipe
    # First, perform a login
    client.post('/login', data={'username': 'testuser', 'password': '<PASSWORD>'}, follow_redirects=True)

def test_dashboard_not_logged_in(client):
    # Test accessing the dashboard without logging in
    response = client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'You need to log in first.' in response.data

def test_dashboard_logged_in(client):
    # Test accessing the dashboard after logging in
    # First, perform a login
    client.post('/login', data={'username': 'testuser', 'password': '<PASSWORD>'}, follow_redirects=True)

def test_edit_recipe_not_logged_in(client):
    # Test accessing the edit recipe page without logging in
    response = client.get('/edit_recipe/1', follow_redirects=True)
    assert response.status_code == 200
    assert b'You need to log in first.' in response.data

def test_your_recipes(client):
    # Test accessing the user's recipes page
    # First, perform a login
    client.post('/login', data={'username': 'testuser', 'password': 'testpassword'}, follow_redirects=True)
    # Then, access the user's recipes page
    response = client.get('/your_recipes', follow_redirects=True)
    assert response.status_code == 200
    assert b'Your Recipes' in response.data

def test_add_favorite(client):
    # Test adding a recipe to the user's favorites
    # First, perform a login
    client.post('/login', data={'username': 'testuser', 'password': '<PASSWORD>'}, follow_redirects=True)

def test_remove_from_favorites(client):
    # Test removing a recipe from the user's favorites
    # First, perform a login
    client.post('/login', data={'username': 'testuser', 'password': '<PASSWORD>'}, follow_redirects=True)
