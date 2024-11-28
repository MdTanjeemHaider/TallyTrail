from .extension import db

# Transaction class
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(256), nullable=False)
    user_id = db.Column(db.String(128), db.ForeignKey('user.id'), nullable=False)

# User class
class User(db.Model):
    id = db.Column(db.String(128), primary_key=True) # Firebase UUID
    email = db.Column(db.String(256), nullable=False)
    transactions = db.relationship('Transaction', backref='user', lazy=True)