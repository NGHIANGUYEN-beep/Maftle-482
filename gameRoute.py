from flask import Blueprint, request, jsonify
from gameModel import Item
import json

gameBP = Blueprint("craft", __name__, url_prefix="/craft")

# Load recipes at startup
with open("recipeTest.json") as f:
    RECIPES = json.load(f)


# Generate a list of all items used in crafting
# usableItems = select(Item.itemNameUnformatted, Item.itemName).filter_by(usedInCrafting='TRUE');


@gameBP.route("/", methods=["POST"])
def craft_item():
    data = request.json
    grid = data.get("grid")

    # Iterate through all shaped recipes
    for recipe in RECIPES:
        if grid == recipe["pattern"]:
            item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()
            if item:
                return jsonify({
                    "success": True,
                    "crafted_item": item.itemName,
                })

    # No match found
    return jsonify({"success": False})
