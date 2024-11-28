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
  "databaseURL": ''
}
auth = pyrebase.initialize_app(config).auth()

# Home route
# Will determine which page to go based on the session
@app.route('/')
def home():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('loginregister'))

# Dashboard route
@app.route('/Dashboard')
def dashboard():
    if 'token' in session:
        return render_template('dashboard.html')
    else:
        return redirect(url_for('loginregister'))
    
# Login/Register route
@app.route('/LoginRegister')
def loginregister():
    if 'token' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('loginregister.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    try:
        # Extract user data from request
        data = request.form
        email = data['email']
        password = data['password']

        # Authenticate user
        user = auth.sign_in_with_email_and_password(email, password)

        # Store user in session
        session['uuid'] = user['localId']
        session['email'] = email
        session['token'] = user['idToken']

        # Check if user is in database, if not add them
        if not User.query.filter_by(id=session['uuid']).first():
            new_user = User(id=session['uuid'], email=session['email'])
            db.session.add(new_user)
            db.session.commit()

        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 401

# Register route
@app.route('/register', methods=['POST'])
def register():
    try:
        # Extract user data from request
        data = request.form
        email = data['email']
        password = data['password']

        # Create user
        user = auth.create_user_with_email_and_password(email, password)

        # Store user in session
        session['uuid'] = user['localId']
        session['email'] = email
        session['token'] = user['idToken']

        # Add user to database
        new_user = User(id=session['uuid'], email=session['email'])
        db.session.add(new_user)

        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 401

# Add transaction route
@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        if 'token' not in session:
            return redirect(url_for('loginregister'))
        
        # Extract transaction data from request
        data = request.form
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        name = data['name']
        amount = float(data['amount'])
        description = data.get('description')
        user_id=session['uuid']
        
        # Add transaction to database
        new_transaction = Transaction(date=date, name=name, amount=amount, description=description, user_id=user_id)
        db.session.add(new_transaction)
        db.session.commit()

        # Redirect to dashboard
        return redirect(url_for('dashboard'))
    except ValueError as e:
        return jsonify({'error': 'Invalid Input', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to Add Transaction', 'message': str(e)}), 500

# Delete transaction route
@app.route('/delete_transaction/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    try:
        if 'token' not in session:
            return redirect(url_for('loginregister'))
        
        # Extract transaction id from request
        transaction = Transaction.query.filter_by(id=transaction_id).first()
        db.session.delete(transaction)
        db.session.commit()

        return redirect(url_for('dashboard'))
    except ValueError as e:
        return jsonify({'error': 'Invalid Input', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to Delete Transaction', 'message': str(e)}), 500


# Get transactions route
@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    try:
        if 'token' not in session:
            return redirect(url_for('loginregister'))
        
        # Get transactions from database
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

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('loginregister'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)