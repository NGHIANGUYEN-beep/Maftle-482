from flask import Blueprint, request, jsonify, render_template
from sqlalchemy.sql.expression import func
from databaseTable import Item
import json
from flask import session

gameBP = Blueprint("craft", __name__)

""" 
This module handles the crafting mechanics of the game, including rendering the game page,
processing crafting attempts and handling the infinite generator of items and the daily generator of items.
It also handles past attempts and their results.

"""
# Global variable to store the current infinite target
currentInfiniteItem = {"item": None}

# Load recipes at startup
with open("recipes.json") as f:
    RECIPES = json.load(f)

#Renders the game page
@gameBP.route("/gamepage.html", methods=['GET'])
def index():
    return render_template('/gamepage.html')

# Handles crafting attempts
@gameBP.route("/submit-guess", methods=["POST"])
def craft_item():
    data = request.json
    grid = data.get("grid")
    target_item = getInfiniteItem()

    #Base case: Initialize past guesses if not present
    if "past_guesses" not in session:
        session["past_guesses"] = []
    
    #Appends past guess to session
    session["past_guesses"].append(grid)
    session.modified = True
    
    # Check if the crafted grid matches any recipe
    for recipe in RECIPES:
        if grid == recipe["pattern"]:
            item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()
            if item:
                if item.itemNameUnformatted == target_item.itemNameUnformatted:
                    # Correct guess → generate a new target
                    # Resets past guesses
                    
                    session["past_guesses"] = []
                    session.modified = True
                    new_item = generateInfiniteItem()
                    print("You have crafted the correct item:", item.itemNameUnformatted)
                    return jsonify({
                        "success": True,
                        "correct": True,
                        "crafted_item": item.itemNameUnformatted,
                        "next_item": new_item.itemName,
                        "message": "Correct! New item generated.",
                        "past_guesses": []
                    })
                else:
                    print("You have crafted an item, but it's not the target:", item.itemNameUnformatted)
                    return jsonify({
                        "success": True,
                        "correct": False,
                        "crafted_item": item.itemNameUnformatted,
                        "message": "Valid item, but not the target.",
                        "past_guesses": session["past_guesses"]
                    })

    # No match found
    return jsonify({"success": False, "past_guesses": session["past_guesses"]})


#Generates a new infinite target item
def generateInfiniteItem():
    new_item = Item.query.filter_by(itemNameUnformatted="bow").first()
    
    # .order_by(func.random()).first()
    #^^ Code for SQLite ^^
    
    # Ensure the new item has a recipe
    for recipe in RECIPES:
        if new_item.itemNameUnformatted == recipe["name"]:
            currentInfiniteItem["item"] = new_item
            return new_item
    return None

#Retrieves the current infinite target item
def getInfiniteItem():
    if currentInfiniteItem["item"] is None:
        return generateInfiniteItem()
    return currentInfiniteItem["item"]
