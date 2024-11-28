from tests.utils import generate_random_account
from src.app import app, db
import pytest

@pytest.fixture
def client():
    # Configure test app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for testing
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with client.session_transaction() as session:
            session.clear()
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_login_failure(client):
    """Test user login failure."""

    email, password = generate_random_account()

    # Login with unregistered user
    response = client.post('/login', data={'email': email, 'password': password})
    assert response.status_code == 401
    assert b'Login failed' in response.data

def test_register_failure(client):
    """Test user registration failure."""

    # Invalid email and password
    email = 'invalid_email'  
    password = 'N'

    # Register user
    response = client.post('/register', data={'email': email, 'password': password})
    assert response.status_code == 401
    assert b'Registration failed' in response.data

def test_add_transaction_failure(client):
    """Test adding a transaction failure."""

    email, password = generate_random_account()

    # Register and login user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Invalid transaction data
    response = client.post('/add_transaction', data={
        'date': 'invalid date',
        'name': 'Grocery',
        'amount': '50.00',
        'description': 'Weekly grocery shopping'
    })
    assert response.status_code == 400
    assert b'Invalid Input' in response.data

def test_delete_transaction_failure(client):
    """Test deleting a transaction failure."""

    email, password = generate_random_account()

    # Register and login user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Delete the transaction
    response = client.delete(f'/delete_transaction/100')
    assert response.status_code == 500
    assert b'Failed to Delete Transaction' in response.data