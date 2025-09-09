from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Account import maftleAcc

def accountImport():

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://nghianguyen@compsci.adelphi.edu:epicexplosion1@localhost/fall2025_482m"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    maftleAcc.init_app(app)
    
    from accRoute import bp
    app.register_blueprint(bp)
    
    return app

app = accountImport()
app.run()
    
    
    
    