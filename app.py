from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from Account import maftleAcc

def accountImport():

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://nghianguyen@localhost/fall2025_482m"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    maftleAcc.init_app(app)
    
    app.config["SECRET_KEY"] = "keyOfSecrets"
    from accRoute import bp
    app.register_blueprint(bp)
    
    return app

app = accountImport()
if __name__ == "__main__":
    app.run(debug=True)
    