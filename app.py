import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# DATABASE
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db = SQLAlchemy()
db.init_app(app)

# SESSION
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100))
    categorie = db.Column(db.String(100))
    image_path = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique = True)
    password = db.Column(db.String(255))

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    items = Item.query.filter_by(user_id = session["user_id"]).all()
    return render_template("index.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return render_template("error.html", message="must provide username")

        if not password:
             return render_template("error.html", message="Must provide password")

        if password != request.form.get("confirmation"):
             return render_template("error.html", message="Passwords do not match")

        user = User.query.filter_by(username=username).first()

        if user:
            return render_template("error.html", message="Username already taken")

        # create user
        new_user = User(
            username=username,
            password=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        # Ensure username was submitted
        if not username:
            return render_template("error.html", message="must provide username"), 403

        # Ensure password was submitted
        if not password:
            return render_template("error.html", message="must provide password"), 403


        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password, password):
            return render_template("error.html", message="invalid username or password")

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    return render_template("login.html")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session: 
        return redirect("/login")
    
    if request.method == "POST":
        naam = request.form.get("naam")
        categorie = request.form.get("categorie")
        image_path = request.form.get("image_path")

        new_item = Item(
            naam = naam,
            categorie = categorie,
            image_path = image_path,
            user_id = session["user_id"]
        )

        db.session.add(new_item)
        db.session.commit()

        return redirect("/")
    
    return render_template("upload.html")

if __name__ == "__main__":
    app.run(debug=True)