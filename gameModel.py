from flask_sqlalchemy import SQLAlchemy
items = SQLAlchemy()

class Item(items.Model):
    __tablename__ = "items"
    id = items.Column(items.Integer, primary_key = True)
    itemNameUnformatted = items.Column(items.String(50), nullable = False)
    itemName = items.Column(items.String(100), nullable = False)
    obtainableFromCrafting = items.Column(items.Boolean)
    usedInCrafting = items.Column(items.Boolean)