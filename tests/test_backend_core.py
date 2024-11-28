from tests.utils import generate_random_account
from src.app import app, db
from src.models import Transaction
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

def test_session_routing(client):
    """Test if the routes redirect correctly based on session state."""

    # Case 1: No session
    response = client.get('/')
    assert response.status_code == 302
    assert '/LoginRegister' in response.location

    response = client.get('/LoginRegister')
    assert response.status_code == 200
    assert b'Login/Register' in response.data

    response = client.get('/Dashboard')
    assert response.status_code == 302
    assert '/LoginRegister' in response.location

    # Case 2: Session exists
    with client.session_transaction() as session:
        session['token'] = 'test_token' # Add a dummy token to session

    response = client.get('/')
    assert response.status_code == 302
    assert '/Dashboard' in response.location

    response = client.get('/LoginRegister')
    assert response.status_code == 302
    assert '/Dashboard' in response.location

    response = client.get('/Dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_login_and_register(client):
    """Test user login functionality."""

    email, password = generate_random_account()

    # Register user
    response = client.post('/register', data={'email': email, 'password': password})
    assert response.status_code == 302
    assert '/Dashboard' in response.location
    client.get('/logout')  # logout

    # Login user
    response = client.post('/login', data={'email': email, 'password': password})
    assert response.status_code == 302
    assert '/Dashboard' in response.location

def test_add_transaction(client):
    """Test adding a transaction."""

    email, password = generate_random_account()

    # Register and login user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Add a transaction
    response = client.post('/add_transaction', data={
        'date': '2024-11-27',
        'name': 'Grocery',
        'amount': '50.00',
        'description': 'Weekly grocery shopping'
    })
    assert response.status_code == 302

    # Check if the transaction exists in the database
    with app.app_context():
        transaction = Transaction.query.first()
        assert transaction is not None
        assert transaction.name == 'Grocery'
        assert transaction.amount == 50.00
        assert transaction.description == 'Weekly grocery shopping'


def test_get_transactions(client):
    """Test fetching transactions."""

    email, password = generate_random_account()

    # Register and login user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Add a transaction
    client.post('/add_transaction', data={
        'date': '2024-11-27',
        'name': 'Grocery',
        'amount': '50.00',
        'description': 'Weekly grocery shopping'
    })

    # Fetch transactions
    response = client.get('/get_transactions')
    assert response.status_code == 200
    transactions = response.get_json()['transactions']
    assert len(transactions) == 1
    assert transactions[0]['name'] == 'Grocery'
    assert transactions[0]['amount'] == 50.00

def test_delete_transaction(client):
    """Test deleting a transaction."""

    email, password = generate_random_account()

    # Register and login user
    client.post('/register', data={'email': email, 'password': password})
    client.post('/login', data={'email': email, 'password': password})

    # Add a transaction
    client.post('/add_transaction', data={
        'date': '2024-11-27',
        'name': 'Grocery',
        'amount': '50.00',
        'description': 'Weekly grocery shopping'
    })

    # Fetch transactions
    response = client.get('/get_transactions')
    transactions = response.get_json()['transactions']
    assert len(transactions) == 1

    # Delete the transaction
    transaction_id = transactions[0]['id']
    response = client.delete(f'/delete_transaction/{transaction_id}')
    assert response.status_code == 302

    # Check if the transaction is deleted from the database
    response = client.get('/get_transactions')
    transactions = response.get_json()['transactions']
    assert len(transactions) == 0