from flask import Blueprint, request, jsonify, render_template
from databaseTable import Item
import json

gameBP = Blueprint("craft", __name__)

# Load recipes at startup
with open("recipes.json") as f:
    RECIPES = json.load(f)

@gameBP.route("/gamepage.html", methods=['GET'])
def index():
    return render_template('/gamepage.html')

# Generate a list of all items used in crafting
# usableItems = select(Item.itemNameUnformatted, Item.itemName).filter_by(usedInCrafting='TRUE');


@gameBP.route("/submit-guess", methods=["GET", "POST"])
def craft_item():
    data = request.json
    grid = data.get("grid")

    # Iterate through all shaped recipes
    for recipe in RECIPES:
        if grid == recipe["pattern"]:
            item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()
            if item:
                print("Item found:", item.itemName)
                return jsonify({
                    "success": True,
                    "crafted_item": item.itemName,
                })

    # No match found
    print("Received grid:", grid)
    return jsonify({"success": False})