from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from databaseTable import table
def main():

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://nghianguyen@localhost/fall2025_482m"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    table.init_app(app)


    app.config["SECRET_KEY"] = "keyOfSecrets"
    from accRoute import bp
    from gameRoute import gameBP
    app.register_blueprint(bp)
    app.register_blueprint(gameBP)

    return app

app = main()
if __name__ == "__main__":
    app.run(debug=True, port = 5003)

    
    