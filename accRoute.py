from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session, Flask
from Account import maftleAcc, Accounts

#BP for running the home page, only uses the template
bp = Blueprint('main', __name__)
@bp.route("/")
def home():
    return render_template("homepage.html")

#BP for creating an account
@bp.route("/createaccount.html", methods = ["GET", "POST"])
def create_account():
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        account = Accounts(username, email, password)
        maftleAcc.session.add(account)
        maftleAcc.session.commit()
        
        return redirect("/loginpage.html")
    
    return render_template("createaccount.html")

#BP for logging in
@bp.route("/loginpage.html", methods = ["GET", "POST"])
def login():
    
    #Obtaining Email and Password
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        #Filters through accounts with the same email
        user = Accounts.query.filter_by(email=email).first()
        
        #Finds account
        if user and user.checkPassword(password):
            session["user_id"] = user.id
            session["email"] = user.email
            flash("Login Successful!", "success")
            
        #Redirects if valid
            return redirect("/")
        
        else:
        #Redirects if invalid
            flash("Invalid credentials", "error")
            return redirect("/loginpage.html")
        
    return render_template("loginpage.html")

#BP for checking login status
@bp.route('/auth/status')
def auth_status():
    is_logged_in = 'user_id' in session
    return jsonify({'logged_in': is_logged_in})

#BP for logging out
@bp.route("/logoutpage.html")
def logout():
    session.clear()
    return redirect("/")