from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
table = SQLAlchemy()

#Model for accounts
class Account(table.Model):
    __tablename__ = "users"
    id = table.Column(table.Integer, primary_key = True)
    username = table.Column(table.String(100), nullable=False)
    email = table.Column(table.String(120), unique=True, nullable=False)
    password = table.Column(table.String(200), nullable = False)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password, method= "pbkdf2:sha256", salt_length=16)
    
    def checkPassword(self, password):
        return check_password_hash(self.password, password)

class Item(table.Model):
    __tablename__ = "items"
    id = table.Column(table.Integer, primary_key = True)
    itemNameUnformatted = table.Column(table.String(50), nullable = False)
    itemName = table.Column(table.String(100), nullable = False)
    obtainableFromCrafting = table.Column(table.Boolean)
    usedInCrafting = table.Column(table.Boolean)
