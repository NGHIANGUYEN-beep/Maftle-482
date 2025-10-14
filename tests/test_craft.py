import pytest
from flask import Flask
from gameRoute import gameBP, RECIPES
from databaseTable import table, Item

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    table.init_app(app)
    app.secret_key = "test_secret"
    app.register_blueprint(gameBP)
    
    with app.app_context():
        table.create_all()
        # insert test items
        table.session.add(Item(
            itemNameUnformatted="stick",
            itemName="Stick",
            obtainableFromCrafting=True,
            usedInCrafting=True
        ))
        table.session.commit()
    return app


@pytest.fixture
def client(app):
    return app.test_client()

def test_craft_stick(client):
  data = {
        "grid": [
            ["oak_plank"],
            ["oak_plank"]
        ]
    }
  response = client.post("/gamepage.html", json=data)
  result = response.get_json()

  assert result["success"] is True
  assert result["crafted_item"] == "Stick"

def test_craft_no_match(client):
    data = {
        "grid": [
            ["dirt"],
            ["dirt"]
        ]
    }
    response = client.post("/gamepage.html", json=data)
    result = response.get_json()

    assert result["success"] is False
