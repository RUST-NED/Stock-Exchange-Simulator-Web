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
db = db_connection.cursor(buffered=True)

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