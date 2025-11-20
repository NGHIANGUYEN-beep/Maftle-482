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
# pattern is from the recipes json  # - array of arrays, strings
currentInfiniteItem = {"item": None, "pattern": None}

# Load recipes at startup
with open("recipes.json") as f:
    RECIPES = json.load(f)

#Renders the game page
@gameBP.route("/gamepage.html", methods=['GET'])
def index():
    return render_template('/gamepage.html')

# Checking if what's in the crafting table is a valid recipe, and if so, sending the resulting item back
@gameBP.route("/check-craft-result", methods=["POST"])
def craft_item():
    data = request.json
    grid = data.get("grid") # gives us trimmedGrid from gamepage.js
    
    # Check if the crafted grid matches any recipe
    for recipe in RECIPES:
        if grid == recipe["pattern"]:
            item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()
            if item:
                print("Item found:", item.itemName)
                return jsonify({
                    "success": True,
                    "crafted_item": item.itemNameUnformatted
                })
    # If no match found
    print("Received grid:", grid)
    return jsonify({"success": False})

# Checking if the recipe in the crafting table is the correct answer
@gameBP.route("/check-answer", methods=["POST"])
def check_solution():
    data = request.json
    grid = data.get("grid") # gives us trimmedGrid from gamepage.js
    # The current correct answer
        # a row from our database
    target_item = getInfiniteItem()
    # Going to need this in order to check which items are part of the correct answer and which aren't
    target_item_pattern = getInfiniteItemPattern();

    #Base case: Initialize past guesses if not present
    if "past_guesses" not in session:
        session["past_guesses"] = []
    
    #Appends past guess to session
    session["past_guesses"].append(grid)
    session.modified = True
    

    # This tells you if the user's guess is correct without having to loop through the json again
    # issue is that if the guess is incorrect, you don't know what item the user did craft
    # if grid == target_item_pattern:

    
    # Check if the crafted grid matches any recipe
    # Don't actually need to do all of this again, since we already know it's a valid item
        # All we need to do now is compare what's in the grid to the answer
    # Plan: fix in next push
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

    # new_item gives us a row from our database
        # we can't access the pattern through this though
    # We're going to access the pattern for the item from the recipes json and then add it to our global variable

    # Ensure the new item has a recipe
    for recipe in RECIPES:
        if new_item.itemNameUnformatted == recipe["name"]:
            currentInfiniteItem["item"] = new_item
            currentInfiniteItem["pattern"] = recipe["pattern"]
            return new_item
    return None


#Retrieves the current infinite target item
def getInfiniteItem():
    if currentInfiniteItem["item"] is None:
        return generateInfiniteItem()
    return currentInfiniteItem["item"]

# Rretrieves the recipe pattern for the current infinite target item
def getInfiniteItemPattern():
    # Item will already have been generated by this point
    return currentInfiniteItem["pattern"]