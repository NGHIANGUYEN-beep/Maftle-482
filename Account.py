from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
maftleAcc = SQLAlchemy()

#Model for accounts
class Accounts(maftleAcc.Model):
    __tablename__ = "users"
    id = maftleAcc.Column(maftleAcc.Integer, primary_key = True)
    username = maftleAcc.Column(maftleAcc.String(100), nullable=False)
    email = maftleAcc.Column(maftleAcc.String(120), unique=True, nullable=False)
    password = maftleAcc.Column(maftleAcc.String(200), nullable = False)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password, method= "pbkdf2:sha256", salt_length=16)
    
    def checkPassword(self, password):
        return check_password_hash(self.password, password)