import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import signin_user, signout_user, get_stock_data, usd
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
    if not session.get("user_name"):  # if user logged in
        return redirect("/signup")
    else:
        # get API key
        db.execute("""SELECT cash, API_KEY FROM Users WHERE username = %s;""", (session.get("user_name"),))
        db_result = db.fetchone()
        user_cash, api_key = db_result["cash"], db_result["API_KEY"]

        # Get share count for all stocks
        db.execute("""
        SELECT stock_symbol, sum(num_shares) AS shares
        FROM transactions
        WHERE username = %s
        GROUP BY stock_symbol;""",
        (session.get("user_name"),))
        db_result = db.fetchall()

        total = 0
        for row in db_result:
            symbol = row["stock_symbol"]
            stock_data = get_stock_data(symbol, api_key)
            if not stock_data:
                flash("API call frequency exceeded. Please try again later.", "error")
                return render_template("dashboard.html")
            row["company_name"] = stock_data["name"]
            row["stock_price"] = usd(stock_data["price"])
            row["total"] = usd(int(row["shares"]) * float(stock_data["price"]))
            total += int(row["shares"]) * float(stock_data["price"])

        total += user_cash
        total = usd(total)
        user_cash = usd(user_cash)

        return render_template("dashboard.html", stocks_data=db_result, cash=user_cash, total=total)        
            

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
            flash("Please fill all the fields", "error")
            return render_template("signup.html", title="Sign Up")
            # return render_template("signup.html", error="Please fill all the fields")
        if password != confirmpassword:
            flash("Password does not match", "error")
            return render_template("signup.html", title="Sign Up")
            # return render_template("signup.html", error="Password does not match")
        if len(password) < 4:
            flash("Password must be at least 4 characters", "error")
            return render_template("signup.html", title="Sign Up")
            # return render_template("signup.html", error="Password must be at least 4 characters")

        # validate api key
        if not get_stock_data("MSFT", api):
            flash("Invalid API key", "error")
            return render_template("signup.html", title="Sign Up")
            # return render_template("signup.html", error="Invalid API key")

        # checking if username already exists
        db.execute("SELECT * FROM users WHERE username = %s", (username,))
        if db.fetchone():
            flash("Username already exists", "error")
            return render_template("signup.html", title="Sign Up")
            # return render_template("signup.html", error="Username already exists")

        # insert user into database
        db.execute("INSERT INTO users (username, password_hash, API_KEY, CASH) VALUES (%s, %s, %s, %s)", (username, generate_password_hash(password), api, 10000))
        db_connection.commit()

        flash("Successfully registered and signed in", "success")
        signin_user(session, username, api)
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
            flash("Invalid Username", "error")
            return render_template("signIn.html", title = "Sign In")
            # return render_template("signIn.html", error = "Invalid Username")

        if not check_password_hash(user_row["password_hash"], password):
            flash("Invalid Password", "error")
            return render_template("signIn.html", title = "Sign In")
            # return render_template("signIn.html", title = "Sign In", error = "Incorrect Password")

        signin_user(session = session, user_name=user_name, api_key= user_row.get("API_KEY"))
        flash("Successfully signed in", "success")
        return redirect("/")

@app.route("/signout")
def signout():
    signout_user(session)
    flash("Successfully signed out", "success")
    return redirect("/")

@app.route("/buy" ,methods = ["GET", "POST"])
def buy():
    # buy shares of stock
    if request.method == "GET":
        return render_template("buy.html")

    else:  # method == POST
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol or not shares:
            flash("Please fill all the fields", "error")
            return render_template("buy.html")
            # return render_template("buy.html", title = "Buy", error = "The symbol and shares field is empty")

        db.execute("""SELECT cash,API_KEY FROM Users WHERE username = %s;""", (session.get("user_name"),))
        db_result = db.fetchone()
        stock = get_stock_data(symbol,db_result.get("API_KEY")) # all data from the sock symbol

        if stock is None:
            flash("Invalid stock symbol or API call frequency limit exceeded.", "error")
            return render_template("buy.html", title = "Buy")


        symbol = stock["symbol"]  #  convert from nFlx to NFLX
        # check if shares is numeric and positive int
        try:
            shares = int(shares)
            if shares < 1:
                raise ValueError
        except ValueError:
            flash("The shares field is invalid", "error")
            return render_template("buy.html", title = "Buy")

        # get cash in user's account
        cash = float(db_result.get("cash"))

        # if user cant afford transaction
        if (shares * stock["price"]) > cash:
            flash("You can't afford this transaction", "error")
            return render_template("buy.html", title = "Buy")

        # deduct transaction amount
        db.execute("""UPDATE users SET cash = %s WHERE username = %s;""",
        (cash - (shares * stock["price"]), session.get("user_name")))

        # record transaction
        db.execute("INSERT INTO transactions (username, stock_symbol, num_shares, price) VALUES (%s, %s, %s, %s)",
        (session.get("user_name"), symbol, shares, stock["price"]))
        db_connection.commit()

        flash("Successfully bought {} shares of {} at ${}".format(shares, symbol, stock["price"]), "success")
        return redirect("/")


@app.route("/sell", methods = ["GET", "POST"])
def sell():
    """Sell shares of stock"""
    # get share count for all stock symbols for which user holds atleast 1 share
    db.execute("""SELECT stock_symbol
    FROM transactions
    WHERE username = %s
    GROUP BY stock_symbol
    HAVING sum(num_shares) > 0;""",
    (session.get("user_name"), ) )
    available_stocks = db.fetchall()
    symbols = [row["stock_symbol"] for row in available_stocks]

    if request.method == "GET":
        if not symbols:
            flash("You don't have any shares to sell", "error")
            return render_template("sale.html", title = "Sell", error = "You don't have any shares to sell")
        else:
            return render_template("sale.html", title = "Sell", symbols = symbols)

    else:  # method post
        symbol = request.form.get("symbol").strip()
        shares = request.form.get("shares").strip()
        if not symbol or not shares:
            flash("Please fill all the fields", "error")
            return render_template("sale.html", title = "Sell", symbols = symbols)

        print(symbol, shares)
        stock_data = get_stock_data(symbol, session.get("api_key"))
        print(stock_data)
        if stock_data is None:
            flash("Invalid stock symbol or API call frequency limit exceeded.", "error")
            return render_template("sale.html", title = "Sell",symbols = symbols)
        symbol = stock_data["symbol"]  # to make symbol proper (eg convert from nFlx to NFLX)

        db.execute("""
        SELECT sum(num_shares) AS shares
        FROM transactions
        WHERE username = %s AND stock_symbol = %s
        GROUP BY stock_symbol;""",
        (session.get("user_name"), symbol))
        db_result = db.fetchone()
        current_shares = db_result["shares"]

        if current_shares <= 0:
            flash(f"You don't have any shares of {symbol} ({stock_data['name']})", "error")
            return render_template("sale.html", title = "Sell", symbols = symbols)

        try:
            shares = int(shares)
            if shares < 1:
                raise ValueError
        except ValueError:
            flash("Numbers of shares must be a positive integer", "error")
            return render_template("sale.html", title = "Sell", symbols = symbols)

        if current_shares < shares:  # if not enough shares present
            flash("You have less than {} shares of {}".format(shares, symbol), "error")
            return render_template("sale.html", title = "Sell", error = f"You have less than {shares} shares of {symbol} ({stock_data['name']})", symbols = symbols)

        # get cash in user's account
        db.execute("SELECT cash FROM users WHERE username = %s", (session.get("user_name"),))
        db_result = db.fetchone()
        user_cash = db_result["cash"]

         # deposit money from selling shares to user
        db.execute("UPDATE users SET cash = %s WHERE username = %s;",
        (user_cash + (stock_data["price"] * shares), session.get("user_name")))

        # record transaction
        shares = -shares
        db.execute("INSERT INTO transactions (username, stock_symbol, num_shares, price) VALUES (%s, %s, %s, %s)",
        (session.get("user_name"), symbol, shares, stock_data["price"]))
        db_connection.commit()
        print(shares)

        # flash(f"Sold {shares} share(s) of {stock_data['name']} ({symbol})!")
        return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
def quote():
    if request.method == "GET":
        return render_template("quote.html", title = "Quote")

    symbol = request.form.get("symbol")
    if not symbol:
        flash("Please fill all the fields", "error")
        return render_template("quote.html", title ="Quote" )

    db.execute("""SELECT cash,API_KEY FROM Users WHERE username = %s;""", (session.get("user_name"),))
    db_result = db.fetchone()
    stock_data = get_stock_data(symbol,db_result.get("API_KEY")) # all data from the sock symbol
    print(stock_data)

    if stock_data is None:
        print("rohan")
        flash("Invalid stock symbol", "error")
        return render_template("quote.html", title = "Sell",)
    
    symbol = stock_data["symbol"]  # to make symbol proper (eg convert from nFlx to NFLX)
    prize = stock_data["price"]

    return render_template("quote.html", title = "Sell",  message = f"The price of the {symbol} is {usd(prize)}." )





    


@app.route("/leaderboard")
def leaderboard():
    """Show all users ranked by amount of cash they have"""
    db.execute("""SELECT username, cash FROM users ORDER BY cash DESC;""")
    db_result = db.fetchall()
    print(db_result)
    return render_template("leaderboard.html", title = "Leaderboard", db_result = db_result)

@app.route("/history")
def history():
    """Show history of transactions"""
    db.execute("""SELECT stock_symbol, num_shares, price, date_time FROM transactions WHERE username = %s ORDER BY date_time DESC;""",
    (session.get("user_name"),))
    db_result = db.fetchall()
    print(db_result)
    return render_template("history.html", title = "History", db_result = db_result)

if __name__ == "__main__":
    app.run(debug=True)