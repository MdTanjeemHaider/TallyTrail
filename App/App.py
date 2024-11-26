from flask import Flask, render_template, request, session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
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
db = SQLAlchemy(app)

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

# Login route
@app.route('/login', methods=['POST'])
def login():
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

    # Redirect to dashboard
    return render_template('dashboard.html')


# Home route
@app.route('/')
def home():
    return render_template('loginregister.html')

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    print("Before logout")
    print(session)
    session.clear()
    print(session)
    return render_template('loginregister.html')


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)