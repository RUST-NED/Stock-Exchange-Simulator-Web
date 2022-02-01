import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import signin_user, signout_user
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

        # validate api key
        if not quote_stock("MSFT", api):
            # flash("Invalid API key", "danger")
            return render_template("signup.html", error="Invalid API key")

        # checking if username already exists
        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        if db.fetchone():
            # flash("Username already exists", "danger")
            return render_template("signup.html", error="Username already exists")

        # insert user into database
        db.execute("INSERT INTO users (username, password_hash, API_KEY, CASH) VALUES (%s, %s, %s, %s)", (username, generate_password_hash(password), api, 10000))
        db_connection.commit()

        # flash("You are now registered and can log in", "success")
        signin_user(session, username, api_key)
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

@app.route("/sell", methods = ["GET", "POST"])
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        # get share count for all stock symbols for which user holds atleast 1 share
        db.execute("""SELECT stock_symbol
        FROM transactions
        WHERE username = %s
        GROUP BY stock_symbol
        HAVING sum(num_shares) > 0;""",
        (session.get("user_name"), ) )
        db_result = db.fetchall()
        if not db_result:
            return render_template("sale.html", title = "Sell", error = "You don't have any shares to sell")
        else:
            symbols = [row["stock_symbol"] for row in db_result]
            return str(symbols)

    else:  # method post
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol or not shares:
            return render_template("sale.html", title = "Sell", error = "Please fill all the fields")

        stock_data = get_stock_data(symbol, session.get("api_key"))
        if stock_data is None:
            return render_template("sale.html", title = "Sell", error = "Invalid stock symbol")
        symbol = stock_data["symbol"]  # to make symbol proper (eg convert from nFlx to NFLX)

        db.execute("""
        SELECT sum(num_shares) AS shares
        FROM transactions
        WHERE user_name = %s AND stock_symbol = %s
        GROUP BY stock_symbol;""",
        (session.get("user_name"), symbol))
        db_result = db.fetchone()
        current_shares = db_result["num_shares"]

        if current_shares <= 0:
            return render_template("sale.html", title = "Sell", error = f"You don't have any shares of {symbol} ({stock_data['name']})")

        # check if shares is numeric and positive int
        try:
            shares = int(shares)
            if shares < 1:
                raise ValueError
        except ValueError:
            return render_template("sale.html", title = "Sell", error = "Numbers of shares must be a positive integer")

        if current_shares < shares:  # if not enough shares present
            return render_template("sale.html", title = "Sell", error = f"You have less than {shares} shares of {symbol} ({stock_data['name']})")

        # get cash in user's account
        db.execute("SELECT cash FROM users WHERE username = %s", (session.get("user_name"),))
        db_result = db.fetchone()
        user_cash = db_result["cash"]

         # deposit money from selling shares to user
        db.execute("UPDATE users SET cash = %s WHERE id = %s;",
        (user_cash + (stock_data["price"] * shares), session.get("user_id")))

        # record transaction
        db.execute("INSERT INTO transactions (user_name, stock_symbol, num_shares, price) VALUES (%s, %s, %s, %s)",
        (session.get("user_name"), symbol, -shares, stock_data["price"]))
        db_connection.commit()

        # flash(f"Sold {shares} share(s) of {stock_data['name']} ({symbol})!")
        return redirect("/")
    
if __name__ == "__main__":
    app.run(debug=True)