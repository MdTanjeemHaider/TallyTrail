# Imports
from datetime import datetime
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from dotenv import load_dotenv
from .extension import db
from .models import Transaction, User
import pyrebase
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLITE_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize firebase authentication app
config = {
  "apiKey": os.getenv("FIREBASE_API_KEY"),
  "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
  "projectId": os.getenv("FIREBASE_PROJECT_ID"),
  "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
  "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
  "appId": os.getenv("FIREBASE_APP_ID"),
  "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
  "databaseURL": '' # Not required for authentication
}
auth = pyrebase.initialize_app(config).auth()

# Routes
# Home route: Redirects to dashboard or login/register page based on session
@app.route('/')
def home():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('loginregister'))

# Dashboard route: Main user interface, accessible only when logged in
@app.route('/Dashboard')
def dashboard():
    if 'token' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('loginregister'))
    
# Login/Register page: Serves the login/register template
@app.route('/LoginRegister')
def loginregister():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('loginregister.html')

# Login route: Authenticates user and starts a session
@app.route('/login', methods=['POST'])
def login():
    try:
        # Extract user data from request
        data = request.form
        email = data['email']
        password = data['password']

        # Authenticate with Firebase
        user = auth.sign_in_with_email_and_password(email, password)

        # Store user details in session
        session['uuid'] = user['localId']
        session['email'] = email
        session['token'] = user['idToken']

        # Ensure user exists in the database
        if not User.query.filter_by(id=session['uuid']).first():
            new_user = User(id=session['uuid'], email=session['email'])
            db.session.add(new_user)
            db.session.commit()

        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 401

# Register route: Registers a new user and starts a session
@app.route('/register', methods=['POST'])
def register():
    try:
        # Extract user details
        data = request.form
        email = data['email']
        password = data['password']

        # Create user in Firebase
        user = auth.create_user_with_email_and_password(email, password)

        # Store user details in session
        session['uuid'] = user['localId']
        session['email'] = email
        session['token'] = user['idToken']

        # Add user to the database
        new_user = User(id=session['uuid'], email=session['email'])
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 401

# Add transaction route: Adds a new financial transaction for the logged-in user
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        if 'token' not in session:
            return redirect(url_for('loginregister'))
        
        # Extract transaction details
        data = request.form
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        name = data['name']
        amount = float(data['amount'])
        description = data.get('description')
        user_id=session['uuid']
        
        # Add transaction to the database
        new_transaction = Transaction(date=date, name=name, amount=amount, description=description, user_id=user_id)
        db.session.add(new_transaction)
        db.session.commit()

        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    except ValueError as e:
        return jsonify({'error': 'Invalid Input', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to Add Transaction', 'message': str(e)}), 500

# Delete transaction route: Deletes a specific transaction
@app.route('/delete_transaction/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        if 'token' not in session:
            return redirect(url_for('loginregister'))
        
        # Find and delete transaction
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        db.session.delete(transaction)
        db.session.commit()

        return redirect(url_for('dashboard'))
    except ValueError as e:
        return jsonify({'error': 'Invalid Input', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to Delete Transaction', 'message': str(e)}), 500

# Get transactions route: Fetches all transactions for the logged-in user
@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    try:
        if 'token' not in session:
            return redirect(url_for('loginregister'))
        
        # Query user's transactions
        transactions = Transaction.query.filter_by(user_id=session['uuid']).all()

        # Convert transactions to JSON
        transactions_json = []
        for transaction in transactions:
            transactions_json.append({
                'id': transaction.id,
                'date': transaction.date,
                'name': transaction.name,
                'amount': transaction.amount,
                'description': transaction.description
            })

        # Return transactions as JSON
        return {'transactions': transactions_json}, 200
    except Exception as e:
        return jsonify({'error': 'Failed to Get Transactions', 'message': str(e)}), 500

# Logout route: Clears the session and logs the user out
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('loginregister'))

# Main entry point
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)