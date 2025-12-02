from flask import Blueprint, request, jsonify, render_template
from databaseTable import Item
import json
from flask import session
import random
from datetime import date
gameBP = Blueprint("craft", __name__)

""" 
This module handles the crafting mechanics of the game, including rendering the game page,
processing crafting attempts and handling the infinite generator of items and the daily generator of items.
It also handles past attempts and their results.

"""
# Global variable to store the current infinite item and its pattern
# Global Variable to store the current user item and whether it's a valid recipe
currentInfiniteItem = {"item": None, "pattern": None}
currentUserItem = None
isValidRecipe = False
currentDailyItem = {"item": None, "pattern": None, "date": None}

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
    grid = data.get("grid")
    
    global isValidRecipe
    global currentUserItem

    # Check if the crafted grid matches any recipe
    for recipe in RECIPES:
        if grid == recipe["pattern"]:
            item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()
            if item:
                # Updating global variables
                isValidRecipe = True
                currentUserItem = item
                print("Item found:", item.itemName)
                return jsonify({
                    "success": True,
                    "crafted_item": item.itemNameUnformatted
                })
    # If no match found
    isValidRecipe = False
    currentUserItem = None
    print("Received grid:", grid)
    return jsonify({"success": False})

# Checking if the recipe in the crafting table is the correct answer
@gameBP.route("/check-answer", methods=["POST"])
def check_solution():
    
    #Initialization for checking answer
    data = request.json
    grid = data.get("grid")
    target_item = getInfiniteItem()
    target_item_pattern = getInfiniteItemPattern()

    #Global Variables
    global isValidRecipe
    global currentUserItem

    #Base case: Initialize past guesses if not present
    if "past_guesses" not in session:
        session["past_guesses"] = []
    
    #Appends past guess to session
    session["past_guesses"].append(grid)
    session.modified = True
    
    # Tells you whether what's currently in the crafting table is a valid recipe
    if isValidRecipe:
        # Tells you if the user's guess is correct without having to loop through the json a second time
        if grid == target_item_pattern:
            # Correct guess → generate a new target
            # Resets past guesses
            session["past_guesses"] = []
            session.modified = True
            new_item = generateInfiniteItem()
            print("You have crafted the correct item:", currentUserItem.itemNameUnformatted)
            return jsonify({
                "success": True,
                "correct": True,
                "crafted_item": currentUserItem.itemName,
                "next_item": new_item.itemName,
                "message": "Correct! New item generated.",
                "past_guesses": []
            })
        else:
            print("You have crafted an item, but it's not the target:", currentUserItem.itemNameUnformatted)
            return jsonify({
                "success": True,
                "correct": False,
                "crafted_item": currentUserItem.itemNameUnformatted,
                "message": "Valid item, but not the target.",
                "past_guesses": session["past_guesses"]
            })
    # If the user clicked "Submit Guess" without there being a valid recipe in the table
    print("You have not crafted a valid recipe")
    return jsonify({"success": False, "past_guesses": session["past_guesses"]})


#Generates a new infinite target item
def generateInfiniteItem():
    # Pick a random recipe
    recipe = random.choice(RECIPES)

    # Pull matching item from DB
    new_item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()
    

    # Can remove later, just need to know what's needed to win
    print("!TESTING! Item to guess is ", new_item.itemName)


    if not new_item:
        print("DB missing item for recipe:", recipe["name"])
        return generateInfiniteItem()  # Try another

    # Update global variable
    currentInfiniteItem["item"] = new_item
    currentInfiniteItem["pattern"] = recipe["pattern"]

    return new_item



#Retrieves the current infinite target item
def getInfiniteItem():
    if currentInfiniteItem["item"] is None:
        return generateInfiniteItem()
    return currentInfiniteItem["item"]

# Rretrieves the recipe pattern for the current infinite target item
def getInfiniteItemPattern():
    # Item will already have been generated by this point
    return currentInfiniteItem["pattern"]

def generateDailyItem():
    print("Generating new daily item...")

    # Pick a random recipe from the full recipe list
    recipe = random.choice(RECIPES)

    # Pull DB item
    item = Item.query.filter_by(itemNameUnformatted=recipe["name"]).first()

    # If DB is missing something, retry safely
    if not item:
        return generateDailyItem()  # Rare, and safe enough

    # Update global daily state
    currentDailyItem["item"] = item
    currentDailyItem["pattern"] = recipe["pattern"]
    currentDailyItem["date"] = date.today()

    print("[Daily] Today's daily item is:", item.itemName)
    return item

@gameBP.route("/daily", methods=["GET"])
def getDailyItem():
    today = date.today()

    # If no daily item has been generated yet
    if currentDailyItem["item"] is None:
        return generateDailyItem()
    
    # If it's a new day, generate a new one
    if currentDailyItem["date"] != today:
        return generateDailyItem()

    return currentDailyItem["item"]

def getDailyItemPattern():
    getDailyItem() 
    return currentDailyItem["pattern"]

@gameBP.route("/check-daily-answer", methods=["POST"])
def check_daily_answer():
    data = request.json
    grid = data.get("grid")

    # retrieve daily item and pattern
    target_item = getDailyItem()
    target_pattern = getDailyItemPattern()

    # validate recipe using existing infinite mode tool
    # (your existing craft_item() logic)
    valid = False
    crafted_item = None
    for recipe in RECIPES:
        if recipe["pattern"] == grid:
            crafted_item = recipe["name"]
            valid = True
            break

    if not valid:
        return jsonify({"success": False, "message": "Not a valid recipe."})

    # correct guess?
    if grid == target_pattern:
        return jsonify({
            "success": True,
            "correct": True,
            "crafted_item": crafted_item,
            "daily_item": target_item.itemName,
            "message": "Correct! Come back tomorrow."
        })

    return jsonify({
        "success": True,
        "correct": False,
        "crafted_item": crafted_item,
        "message": "Valid recipe, but not today's daily item."
    })

