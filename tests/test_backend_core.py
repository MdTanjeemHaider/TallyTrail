from tests.utils import generate_random_account
from src.app import app, db
import pytest


@pytest.fixture
def client():
    """Set up a Flask test client with an in-memory database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Initialize database tables
        yield client
        with client.session_transaction() as session:
            session.clear()  # Clear session after each test
        with app.app_context():
            db.session.remove()  # Remove database session
            db.drop_all()  # Drop all tables


def test_login_failure(client):
    """Test user login failure for unregistered credentials."""
    email, password = generate_random_account()

    # Attempt to log in with an unregistered user
    response = client.post('/login', data={'email': email, 'password': password})
    assert response.status_code == 401  # Unauthorized
    assert b'Login failed' in response.data


def test_register_failure(client):
    """Test user registration failure with invalid input."""
    email = 'invalid_email'  # Invalid email format
    password = 'N'

    # Attempt to register with invalid input
    response = client.post('/register', data={'email': email, 'password': password})
    assert response.status_code == 401  # Bad request for registration failure
    assert b'Registration failed' in response.data


def test_add_transaction_failure(client):
    """Test failure when adding a transaction with invalid input."""
    email, password = generate_random_account()

    # Register and login the user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Attempt to add a transaction with an invalid date
    response = client.post('/add_transaction', data={
        'date': 'invalid date',  # Invalid date format
        'name': 'Train Ticket',
        'amount': '50.00',
        'description': 'Weekly Train Ticket'
    })
    assert response.status_code == 400  # Bad request
    assert b'Invalid Input' in response.data


def test_delete_transaction_failure(client):
    """Test failure when trying to delete a non-existent transaction."""
    email, password = generate_random_account()

    # Register and login the user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Attempt to delete a transaction with a non-existent ID
    response = client.delete('/delete_transaction/100')  # ID 100 does not exist
    assert response.status_code == 500  # Internal server error
    assert b'Failed to Delete Transaction' in response.data
