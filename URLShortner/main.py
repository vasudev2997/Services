from flask import Flask, render_template, request, redirect, abort
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os

# Flask app initialization
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "data_urls.sqlite")

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Model definition
class URLShortener(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String(2048), nullable=False, unique=True)
    short_code = db.Column(db.String(10), nullable=False, unique=True)

    def __init__(self, long_url, short_code):
        self.long_url = long_url
        self.short_code = short_code

# Ensures database tables are created
@app.before_first_request
def initialize_database():
    db.create_all()

# Utility to generate a unique short code
def generate_unique_code(length=10):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(characters, k=length))
        if not URLShortener.query.filter_by(short_code=code).first():
            return code

# Home route
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form.get("long_url")
        if not long_url:
            return "Invalid URL", 400

        existing = URLShortener.query.filter_by(long_url=long_url).first()
        if existing:
            return f"{request.url_root}{existing.short_code}"

        short_code = generate_unique_code()
        new_entry = URLShortener(long_url=long_url, short_code=short_code)
        db.session.add(new_entry)
        db.session.commit()
        return f"{request.url_root}{short_code}"

    return render_template("form.html")

# Redirect route
@app.route("/<string:short_code>")
def redirect_to_long_url(short_code):
    entry = URLShortener.query.filter_by(short_code=short_code).first()
    if entry:
        return redirect(entry.long_url)
    return abort(404, description="Short URL not found.")

# Run the app
if __name__ == "__main__":
    app.run(debug=True, port=5000)
