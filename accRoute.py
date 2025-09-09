from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Flask
from Account import maftleAcc, Accounts

#BP for running the home page, only uses the template
bp = Blueprint('main', __name__)
@bp.route("/")
def home():
    return render_template("homepage.html")

#BP for creating an account
@bp.route("/create", methods = ["GET", "POST"])
def create_account():
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        account = Accounts(username, email, password)
        maftleAcc.session.add(account)
        maftleAcc.session.commit()
        
        return redirect('/')
    
    return render_template("createaccount.html")

#BP for logging in
@bp.route("/login", methods = ["GET", "POST"])
def login():
    
    #Obtaining Email and Password
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        #Filters through accounts with the same email
        user = Accounts.query.filter_by(email=email).first()
        
        #Finds account
        if user and user.password == password:
            session[user.id] = user.id
            session[password] = user.password
            flash("Login Successful!", "Success")
            
        #Redirects if valid
            return redirect('/')
        
        else:
        #Redirects if invalid
            flash("Invalid credentials", "Error")
            return redirect("/login")
        
    return render_template("loginpage.html")