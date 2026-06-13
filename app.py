# =============================================================
# app.py  —  Main Flask application for the Climate Tracker
# =============================================================
# Flask is a "micro-framework": it gives you routing, request
# handling, and template rendering without forcing a specific
# project structure. You add only what you need.
# =============================================================

import sqlite3                  # Built-in Python module for SQLite
from flask import (
    Flask,
    render_template,            # Renders a Jinja2 HTML template
    request,                    # Gives access to form/query data
    redirect,                   # Sends the browser to another URL
    url_for,                    # Builds a URL from a function name
    flash,                      # One-time status messages
)

# -------------------------------------------------------------
# App Initialisation
# -------------------------------------------------------------
# Flask(__name__) creates the application object.
# __name__ tells Flask where to look for templates and static
# files (relative to this file's directory).
app = Flask(__name__)

# flash() needs a secret key to sign session cookies that carry
# the message between requests. Change this to a random string
# in production — never hard-code secrets in real projects!
app.secret_key = "change-me-in-production"

# Path to our SQLite database file. SQLite wil  l create this file
# automatically the first time we connect.
DATABASE = "climate.db"


# =============================================================
# Database helpers
# =============================================================

def get_db():
    """
    Open (or reuse) a connection to the SQLite database.

    sqlite3.connect() either opens an existing .db file or
    creates a new one on disk. We set row_factory so that
    rows come back as dict-like objects (access by column name)
    instead of plain tuples.
    """
    conn = sqlite3.connect(DATABASE)
    # Row objects behave like both tuples AND dicts:
    #   row[0]          → first column value
    #   row["city"]     → column named "city"
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Run schema.sql to create tables if they don't exist yet.

    open() reads the SQL file as a string, then executescript()
    runs all the statements in one go. Called once at startup.
    """
    with get_db() as conn:
        with open("schema.sql", "r") as f:
            conn.executescript(f.read())


# =============================================================
# Routes
# =============================================================
# A "route" maps a URL path + HTTP method to a Python function.
# The @app.route decorator registers the mapping with Flask.
# =============================================================

@app.route("/", methods=["GET"])
def index():
    """
    GET /  —  Show all temperature readings.

    HTTP GET is a read-only request; the browser uses it when
    you navigate to a page or click a link.

    Steps:
      1. Query every row from the readings table, newest first.
      2. Pass the rows to the HTML template for rendering.
    """
    with get_db() as conn:
        # cursor.execute() runs a SQL query.
        # fetchall() retrieves every matching row as a list.
        # ORDER BY date DESC puts the most recent readings first.
        readings = conn.execute(
            "SELECT id, city, temperature, date FROM readings ORDER BY date DESC"
        ).fetchall()

    # render_template() finds templates/index.html and fills in
    # the {{ readings }} placeholder with our list of rows.
    return render_template("index.html", readings=readings)


@app.route("/submit", methods=["POST"])
def submit():
    """
    POST /submit  —  Save a new temperature reading.

    HTTP POST is used to send data to the server (e.g. a form
    submission). The form data arrives in request.form, a dict
    keyed by the HTML <input name="..."> attribute.

    Steps:
      1. Read and validate the form fields.
      2. INSERT a new row into the database.
      3. Redirect back to GET / (the "Post/Redirect/Get" pattern).
         This prevents a duplicate submission if the user
         refreshes the page after posting.
    """
    # request.form.get() is safer than request.form[] because
    # it returns None instead of raising a KeyError if the field
    # is missing. .strip() removes accidental whitespace.
    city        = request.form.get("city", "").strip()
    temperature = request.form.get("temperature", "").strip()
    date        = request.form.get("date", "").strip()

    # --- Basic validation ---
    # Always validate on the server — client-side (HTML5 / JS)
    # validation can be bypassed by a determined user.
    if not city or not temperature or not date:
        flash("All fields are required.", "error")
        return redirect(url_for("index"))

    try:
        # float() converts the string "23.5" → 23.5
        # Raises ValueError if the string isn't a valid number.
        temperature = float(temperature)
    except ValueError:
        flash("Temperature must be a number.", "error")
        return redirect(url_for("index"))

    # --- Insert into the database ---
    with get_db() as conn:
        # Use parameterised queries (the ? placeholders) to
        # prevent SQL injection attacks. NEVER use f-strings or
        # string concatenation to build SQL with user data!
        conn.execute(
            "INSERT INTO readings (city, temperature, date) VALUES (?, ?, ?)",
            (city, temperature, date),
        )
        # "with get_db() as conn:" auto-commits on success and
        # rolls back on exception, thanks to sqlite3's context
        # manager protocol.

    flash(f"Reading for {city} saved successfully! 🌡️", "success")

    # redirect() + url_for() sends the browser to GET /
    # url_for("index") looks up the URL for the index() function,
    # so renaming the route won't break this line.
    return redirect(url_for("index"))


# =============================================================
# Entry point
# =============================================================
# This block only runs when you execute `python app.py` directly.
# It won't run if another module imports this file (e.g. gunicorn).
# =============================================================

if __name__ == "__main__":
    # Create the database table(s) before starting the server.
    init_db()
    # debug=True enables:
    #   • Auto-reload when you save a file
    #   • An interactive debugger in the browser on errors
    # NEVER use debug=True in production!
    app.run(debug=True)