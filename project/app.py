import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, visualize_emotion, motivate, analyze, generate_colors, giphy


# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///serenaid.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@app.route("/")
@login_required
def index():
    name = db.execute("SELECT name FROM users WHERE id = ?", session["user_id"])[0]['name']

    return render_template(
        "index.html", name = name
    )

@app.route("/welcome")
def welcome():
    # Get information on each stock and add the real-time stock value to it
    return render_template(
        "welcome.html", primaryColor = '#90323D', secondaryColor= '#D5CAD6', tertiaryColor = 'blue'
    )


@app.route("/vrs", methods=["GET", "POST"])
@login_required
def vsr():
    if request.method == "GET":
        return render_template("vrs.html",  primaryColor = 'white', secondaryColor= '#ADD8E6', tertiaryColor = 'purple')

    if request.method == "POST":
        emotion = request.form.get("emotion")
        if not emotion:
            return apology("Hmm, SerenAId didn't catch your emotion there!")

        quote = motivate(emotion)

        image_url = 'filler' #visualize_emotion(emotion)
        print(image_url)
        return render_template("vrs-loaded.html", image_url = 'https://oaidalleapiprodscus.blob.core.windows.net/private/org-fVLiDaNvFjnQgAePQJZHmWeZ/user-Bi36hV4bYx8IgZWyC0c9zqvb/img-Bf3uslJj7fJsmMAtQqN9vVSK.png?st=2023-12-05T23%3A29%3A51Z&se=2023-12-06T01%3A29%3A51Z&sp=r&sv=2021-08-06&sr=b&rscd=inline&rsct=image/png&skoid=6aaadede-4fb3-4698-a8f6-684d7786b067&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2023-12-05T19%3A53%3A56Z&ske=2023-12-06T19%3A53%3A56Z&sks=b&skv=2021-08-06&sig=8KmMlStrhxvq8y0dzW/0319cuFU%2BtmsKsByJOLOsglo%3D', quote = quote)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", primaryColor = '#6E2594', secondaryColor= '#ECD444', tertiaryColor = '#E1F2FE')


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", primaryColor = '#F12903', secondaryColor = '#BFBADF', tertiaryColor = '#C1673E')

    if request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation or not name:
            return apology("Invalid Input", 400)

        if not password == confirmation:
            return apology("Passwords Do Not Match", 400)

        if db.execute("SELECT * FROM users WHERE username = ?", username):
            return apology("User already exists", 400)

        db.execute(
            "INSERT INTO users (username, hash, name) VALUES (?, ?, ?)",
            username,
            generate_password_hash(password),
            name
        )

        user_id = db.execute("SELECT id FROM users WHERE username = ?", username)

        session["user_id"] = user_id[0]["id"]

    return redirect("/")

@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    current_date = datetime.now()
    formatted_date_md = current_date.strftime("%B %d")
    formatted_date_ymd = current_date.strftime("%Y-%m-%d")

    if request.method == "GET":
        # Set default checkedin value to false and set to true if for that day the user has already checked in
        checkedin = False

        # Initialize current_analysis as an empty string and then update it later if needed (if the user already logged their emotions for today)
        current_analysis = "Empty"

        # If they already logged emotions for current day, pass that in so we can render a different part of the page
        if (db.execute("SELECT date FROM emotions WHERE date = ?", formatted_date_ymd)):
            # Access the analysis of their emotions since they've logged emotions for today, so we can access it
            current_analysis = db.execute("SELECT analysis FROM emotions WHERE date = ?", formatted_date_ymd)[0]

            checkedin = True

        return render_template("checkin.html", date = formatted_date_md, primaryColor = '#A78A7F', secondaryColor= '#C5FFFD', tertiaryColor = '#073B4C', checkedin = checkedin, current_analysis = current_analysis)

    if request.method == "POST":

        mood = request.form.get("mood")
        selected_emotions = request.form.getlist('emotions[]')
        notes = request.form.get('notes')

        if not mood or not selected_emotions or not notes:
            return apology("Invalid Input", 400)

        emotions_string = ",".join(selected_emotions)

        # Log emotions
        db.execute(
            "INSERT INTO emotions (user_id, mood, feelings, notes, date) VALUES (?, ?, ?, ?, ?)",
            session["user_id"],
            mood,
            emotions_string,
            notes,
            formatted_date_ymd
        )

        # Access the user's emotional history
        logs = str(db.execute("SELECT mood, feelings, notes, date FROM emotions"))

        # With this new logged emotion, interpret the user's progression and add it to the database for that day
        analysis = analyze(logs)
        db.execute("UPDATE emotions SET analysis = ? WHERE date = ?", analysis, formatted_date_ymd)

        return redirect("/checkin")

@app.route("/escapism", methods=["GET", "POST"])
def escapism():
    if request.method == "GET":
        return render_template("escapism.html", primaryColor = '#5d146e', secondaryColor= '#aa31ad', tertiaryColor = '#010660')

    if request.method == "POST":
        media = request.form.get("media")

        color_list = generate_colors(media)

        gifs = giphy(media)

        return render_template("escapism-loaded.html", media = media, primaryColor = color_list[0], secondaryColor= color_list[1], tertiaryColor = color_list[2], gifs = gifs)

@app.route("/journal", methods=["GET", "POST"])
@login_required
def journal():
    if request.method == "GET":
        journal = db.execute("SELECT journal FROM users WHERE id = ?", session["user_id"])[0]['journal']

        return render_template("journal.html",  primaryColor = '#72a0c1', secondaryColor= '#ff7f50', tertiaryColor = '#98c7c2', journal=journal)

    if request.method == "POST":
        new_journal = request.form.get("journal-content")
        if not new_journal:
            return apology("Hmm, SerenAId didn't catch your emotion there!")

        upload = db.execute("UPDATE users SET journal = ? WHERE id = ?", new_journal, session["user_id"])

        if not upload:
            return apology("Unable to update journal!")

        return redirect("/journal")

