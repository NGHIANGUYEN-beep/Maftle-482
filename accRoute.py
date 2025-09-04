from flask import Blueprint, render_template, request, redirect, url_for, flash
from Account import maftleAcc, Account

bp = Blueprint('main', __name__)
@bp.route("/")
def home():
    return render_template("homepage.html")

@bp.route("/create", methods = ["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        account = Account(username, email, password)
        maftleAcc.session.add(account)
        maftleAcc.session.commit()
        
        return redirect('/')
    
    return render_template("createpage.html")