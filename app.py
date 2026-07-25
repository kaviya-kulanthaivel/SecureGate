from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "securegate123"

# Create Database
def create_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

create_database()

# Home
@app.route("/")
def home():
    return redirect("/login")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username, password)
            )
            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists!"

        conn.close()
        return redirect("/login")

    return render_template("register.html")


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT username,password FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            if check_password_hash(user[1], password):
                session["username"] = user[0]
                return redirect("/dashboard")

        return "Invalid Username or Password"

    return render_template("login.html")

@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        username = request.form["username"]
        new_password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        if user:

            cursor.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_password, username)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        conn.close()

        return "Username not found!"

    return render_template("forgot.html")
# Dashboard
from flask import request

@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/login")

    ip = request.remote_addr

    return render_template(
        "dashboard.html",
        username=session["username"],
        ip=ip
    )


# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)