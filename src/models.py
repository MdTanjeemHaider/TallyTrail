from datetime import datetime, timezone
from extension import db

# Transaction class
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    recurring = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.String(127), db.ForeignKey('user.id'), nullable=False)


# User class
class User(db.Model):
    id = db.Column(db.String(127), primary_key=True) # Firebase UUID
    email = db.Column(db.String(255), nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)