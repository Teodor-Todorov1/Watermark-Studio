

import pyrebase
from flask import Blueprint, flash, redirect, render_template, request, session, url_for



# Defining a blueprint
registration_bp = Blueprint(
    'registration_bp', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/register/static/'
)


config = {
    "apiKey": "AIzaSyAtyFAcewblFH0zxaY3BXbPyjagRkS_HTY",
    "authDomain": "pythonauthsys-15ed1.firebaseapp.com",
    "databaseURL": "https://pythonauthsys-15ed1-default-rtdb.europe-west1.firebasedatabase.app",
    "projectId": "pythonauthsys-15ed1",
    "storageBucket": "pythonauthsys-15ed1.appspot.com",
    "messagingSenderId": "155695857534",
    "appId": "1:155695857534:web:54a66184993b209fa33d2f",
    "measurementId": "G-5FBDR6ZF5V"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

@registration_bp.route("/")
def signup():
    return render_template("signup.html")

@registration_bp.route("/login")
def login():
    return render_template("login.html")

@registration_bp.route("/welcome")
def welcome():
    if person["is_logged_in"]:
        return render_template("index.html", email=person["email"], name=person["name"])
    else:
        return redirect(url_for('registration_bp.login'))

@registration_bp.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            return redirect(url_for('registration_bp.welcome'))
        except Exception as err:
            return redirect(url_for('registration_bp.login'))
    else:
        if person["is_logged_in"]:
            return redirect(url_for('registration_bp.welcome'))
        else:
            return redirect(url_for('registration_bp.login'))

@registration_bp.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            auth.create_user_with_email_and_password(email, password)
            user = auth.sign_in_with_email_and_password(email, password)
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            return redirect(url_for('registration_bp.welcome'))
        except Exception as err:
            return redirect(url_for('registration_bp.register'))

    else:
        if person["is_logged_in"]:
            return redirect(url_for('registration_bp.welcome'))
        else:
            return redirect(url_for('registration_bp.register'))
