import pytest
import os, json
from flask import Flask
import databaseTable
import gameRoute

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    databaseTable.table.init_app(app)
    app.secret_key = "test_secret"
    app.register_blueprint(gameRoute.gameBP)
    
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RECIPES_PATH = os.path.join(BASE_DIR, "recipes.json")

    
    with open(RECIPES_PATH, "r") as f:
        gameRoute.RECIPES = json.load(f)
    with app.app_context():
        databaseTable.table.create_all()
        # insert test items
        items = [
            databaseTable.Item(itemNameUnformatted="stick", itemName="Stick",
                               obtainableFromCrafting=True, usedInCrafting=True),
            databaseTable.Item(itemNameUnformatted="bow", itemName="Bow",
                               obtainableFromCrafting=True, usedInCrafting=True),
            databaseTable.Item(itemNameUnformatted="string", itemName="String",
                               obtainableFromCrafting=False, usedInCrafting=True),
            databaseTable.Item(itemNameUnformatted="oak_plank", itemName="Oak Plank",
                               obtainableFromCrafting=False, usedInCrafting=True),
            databaseTable.Item(itemNameUnformatted="dirt", itemName="Dirt",
                               obtainableFromCrafting=False, usedInCrafting=False),
            databaseTable.Item(itemNameUnformatted="fishing_rod", itemName="Fishing Rod",
                               obtainableFromCrafting=True, usedInCrafting=True),
        ]
        databaseTable.table.session.add_all(items)
        databaseTable.table.session.commit()
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
  response = client.post("/submit-guess", json=data)
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
    response = client.post("/submit-guess", json=data)
    result = response.get_json()

    assert result["success"] is False
    
def test_craft_fishing_rod(client):
    data = {
        "grid": [
            [None,None,"stick"],
            [None,"stick","string"],
            ["stick",None,"string"]
        ]
    }
    response = client.post("/submit-guess", json=data)
    result = response.get_json()
    assert result["success"] is True
    assert result["crafted_item"] == "Fishing Rod"

