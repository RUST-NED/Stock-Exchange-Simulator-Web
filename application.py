import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import signin_user, signout_user ,quote_stock
from os import getenv

from flask_session import Session

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getenv("MySQLpassword"),
    database="stockexchangesimulator"
)
db = db_connection.cursor(buffered=True, dictionary = True)

app = Flask(__name__)
app.secret_key = "35gbbad932565nnssndg"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    if session.get("user_name"):  # if user logged in
        return render_template("dashboard.html", user_name=session["user_name"])
    else:
        return redirect("/signup")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", title="Sign Up")
    else:
        print(request.form)
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmpassword = request.form.get("confirmpassword").strip()
        api = request.form.get("api").strip()

        # validation
        if username == "" or password == "" or confirmpassword == "" or api == "":
            # flash("Please fill all the fields", "danger")
            return render_template("signup.html", error="Please fill all the fields")
        if password != confirmpassword:
            # flash("Password does not match", "danger")
            return render_template("signup.html", error="Password does not match")
        if len(password) < 4:
            # flash("Password must be at least 4 characters", "danger")
            return render_template("signup.html", error="Password must be at least 4 characters")

        # checking if username already exists
        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        if db.fetchone():
            # flash("Username already exists", "danger")
            return render_template("signup.html", error="Username already exists")

        # insert user into database
        db.execute("INSERT INTO users (username, password_hash, API_KEY, CASH) VALUES (%s, %s, %s, %s)", (username, generate_password_hash(password), api, 10000))
        db_connection.commit()

        # flash("You are now registered and can log in", "success")
        signin_user(session, username)
        return redirect("/")

      
@app.route("/signin", methods  = ["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signIn.html", title = "Sign In")
    else:
        user_name = request.form.get("username").strip()
        password = request.form.get("password").strip()

        #checking if exist 
        db.execute("""
        SELECT * FROM Users
        WHERE username = %s;""",(user_name,)
        )

        user_row = db.fetchone()
        if not user_row:
            # flash("Invalid Username", "error")
            return render_template("signIn.html", error = "Invalid Username")

        if not check_password_hash(user_row["password_hash"], password):
            # flash
            return render_template("signIn.html", title = "Sign In", error = "Incorrect Password")

        signin_user(session = session, user_name = user_row["username"]), 
        return redirect("/")

@app.route("/signout")
def signout():
    signout_user(session)
    return redirect("/")

@app.route("/buy")
def buy():
    # buy shares of stock
    if request.method == "GET":
        return render_template("buy.html")

    else:  # method == POST
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol or not shares:
            return render_template("buy.html", title = "Buy", error = "The symbol and shares field is empty")

        stock = get_stock_data(symbol) # all data from the sock symbol

        if stock is None:
            return render_template("buy.html", title = "Buy", error = "Invalid stock symbol")


        symbol = stock["symbol"]  #  convert from nFlx to NFLX

        # check if shares is numeric and positive int
        try:
            shares = int(shares)
            if shares < 1:
                raise ValueError
        except ValueError:
            return render_template("buy.html", title = "Buy", error = "The Shares field is invalid")

        # get cash in user's account
        db.execute("""SELECT cash FROM Users WHERE username = %s;""", (session.get("user_name"),))
        cash = db.fetchone()["cash"]

        # if user cant afford transaction
        if (shares * stock["price"]) > cash:
            return render_template("buy.html", title = "Buy", error = "You don't have enough cash")

        # deduct transaction amount
        db.execute("""UPDATE users SET cash = %s WHERE username = %s;""",
        (cash - (shares * stock["price"]), session.get("user_name")))

        # record transaction
        db.execute("INSERT INTO transactions (username, symbol, shares, price) VALUES (%s, %s, %s, %s)",
        session.get("user_name"), symbol, shares, stock["price"])
        db_connection.commit()


        return redirect("/")

    
if __name__ == "__main__":
    app.run(debug=True)