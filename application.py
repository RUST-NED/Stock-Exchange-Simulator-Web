import mysql.connector
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash


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
        return redirect("/signin")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html", title="Sign Up")
    else:
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirmpassword = request.form.get("confirmpassword").strip()
        api = request.form.get("api").strip()
        if username == "" or password == "" or confirmpassword == "" or api == "":
            # flash("Please fill all the fields", "danger")
            return redirect("/signup")
        if password != confirmpassword:
            # flash("Password does not match", "danger")
            return redirect("/signup")

@app.route("/signin", methods  = ["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("siginIn.html", title = "Sign In")
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

        if not check_password_hash(user_row[password_hash], password):
            # flash
            return render_template("signIn.html", title = "Sign In", error = "Incorrect Password")

        signin_user(session = session, useer_name = user_row[username]), 
        return redirect("/")

    



