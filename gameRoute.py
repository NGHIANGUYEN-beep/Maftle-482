from flask import Blueprint, request, jsonify
from gameModel import Item
import json

bp = Blueprint("craft", __name__, url_prefix="/craft")

# Load recipes at startup
with open("recipes.json") as f:
    RECIPES = json.load(f)


@bp.route("/", methods=["POST"])
def craft_item():
    data = request.json
    grid = data.get("grid")

    # Iterate through all shaped recipes
    for recipe in RECIPES:
        if grid == recipe["pattern"]:
            item = Item.query.filter_by(name=recipe["name"]).first()
            if item:
                return jsonify({
                    "success": True,
                    "crafted_item": item.name,
                })

    # No match found
    return jsonify({"success": False})
