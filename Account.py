from flask_sqlalchemy import SQLAlchemy

maftleAcc = SQLAlchemy()
class Accounts(maftleAcc.Model):
    __tablename__ = "users"
    id = maftleAcc.Column(maftleAcc.Integer, primary_key = True)
    username = maftleAcc.Column(maftleAcc.String(100), nullable=False)
    email = maftleAcc.Column(maftleAcc.String(120), unique=True, nullable=False)
    password = maftleAcc.Column(maftleAcc.String(100), nullable = False)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password