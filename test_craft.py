import pytest
from flask import Flask
from gameRoute import gameBP, RECIPES
from gameModel import Item, items

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    items.init_app(app)
    app.secret_key = "test_secret"
    app.register_blueprint(gameBP)
    with app.app_context():
        items.create_all()
        # insert test items
        items.session.add(Item(
            itemNameUnformatted="stick",
            itemName="Stick",
            obtainableFromCrafting=True,
            usedInCrafting=True
        ))
        items.session.commit()
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
  response = client.post("/craft/", json=data)
  result = response.get_json()

  assert result["success"] is True
  assert result["crafted_item"] == "Stick"

def test_craft_no_match(client):
    """Test invalid recipe returns success=False."""
    data = {
        "grid": [
            ["dirt"],
            ["dirt"]
        ]
    }
    response = client.post("/craft/", json=data)
    result = response.get_json()

    assert result["success"] is False
