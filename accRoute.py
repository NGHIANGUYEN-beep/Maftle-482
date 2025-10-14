from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session, Flask
from databaseTable import table, Account

#BP for running the home page, only uses the template
bp = Blueprint('main', __name__)
@bp.route("/")
def home():
    return render_template("homepage.html")

#BP for creating an account
@bp.route("/createaccount.html", methods = ["GET", "POST"])
def create_account():
    
    #Gets username, email, password from front-end submission
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
    
    #Checks if username is taken
        existing_user = Account.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!", "usererror")
            return redirect("/createaccount.html")
        
    #Checks if there is account with existing email
        existing_email = Account.query.filter_by(email=email).first()
        if existing_email:
            flash("Email is already registered. Please log in!", "createerror")
            return redirect("/createaccount.html")
    
    #Commits account to database
        account = Account(username, email, password)
        table.session.add(account)
        table.session.commit()
        
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
        user = Account.query.filter_by(email=email).first()
        
        #Finds account
        if user and user.checkPassword(password):
            session["user_id"] = user.id
            session["email"] = user.email
            session["username"] = user.username
            
        #Redirects if valid
            return redirect("/")
        
        else:
        #Redirects if invalid
            flash("Invalid Email or Password!", "error")
            return redirect("/loginpage.html")
        
    return render_template("loginpage.html")

#BP for checking login status
@bp.route('/auth/status')
def auth_status():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'username': session.get('username')})
    return jsonify({'logged_in': False})

#BP for logging out
@bp.route("/logoutpage.html")
def logout():
    session.clear()
    return render_template("/logoutpage.html")