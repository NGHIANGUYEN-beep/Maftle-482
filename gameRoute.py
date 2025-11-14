from flask import Blueprint, request, jsonify, render_template
import random
from databaseTable import Item
import json
from datetime import date

gameBP = Blueprint("craft", __name__)

# Global Variables
currentDailyItem = {"date": None, "item": None}

# Load recipes at startup
with open("recipes.json") as f:
    RECIPES = json.load(f)

@gameBP.route("/gamepage.html", methods=['GET'])
def index():
    return render_template('/gamepage.html')

# Generate a list of all items used in crafting
# Might need to make changes to syntax
# usableItems = Item.query(Item.itemNameUnformatted, Item.itemName).filter_by(usedInCrafting='TRUE');
# I think this returns a tuple?



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
                    "crafted_item": item.itemNameUnformatted
                })

    # No match found
    print("Received grid:", grid)
    return jsonify({"success": False})

@gameBP.route("/randomGenerator", methods = ["POST"])
def generateRandomItem():
        dailyItem = Item.query.filter_by(obtainableFromCrafting=True).order_by(random()).first()
        for recipe in RECIPES:
            if dailyItem.itemNameUnformatted == recipe["name"]:
                currentDailyItem["item"] = dailyItem
                return jsonify({
                 "success" : True,
                    "daily_item": dailyItem.itemName
            })

def dailyItem():
    today = date.today()
    if currentDailyItem["date"] == today:
        return currentDailyItem["item"]
    
    if currentDailyItem["item"] == None:
        generateRandomItem()
        