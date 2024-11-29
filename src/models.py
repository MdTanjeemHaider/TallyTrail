from .extension import db

# Transaction class
class Transaction(db.Model):
    """
    Represents a financial transaction.
    """
    id = db.Column(db.Integer, primary_key=True)  # Unique transaction ID
    date = db.Column(db.Date, nullable=False)  # Transaction date
    name = db.Column(db.String(64), nullable=False)  # Name/title of the transaction
    amount = db.Column(db.Float, nullable=False)  # Transaction amount
    description = db.Column(db.String(256), nullable=False)  # Brief transaction description
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'), nullable=False)  # Reference to User ID

# User class
class User(db.Model):
    """
    Represents a user in the system.
    """
    id = db.Column(db.String(128), primary_key=True)  # Firebase UUID for user
    email = db.Column(db.String(256), nullable=False)  # User email (non-nullable)
    transactions = db.relationship(
        'Transaction', backref='user', lazy=True
    )  # One-to-many relationship with Transaction