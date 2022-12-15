import flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required
import wikipedia
import random
import uuid


app = flask.Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "wikifun"

db = SQLAlchemy(app)
login_manager = LoginManager(app)


class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String)
    password = db.Column(db.String)
    interests = db.Column(db.String)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/")
def wiki_fun():
    if not current_user.is_authenticated:
        return flask.redirect("/signup")
    return flask.render_template("index.html")


@app.route("/get-article")
def article():
    if current_user.is_authenticated:
        interest_choice = random.choice(current_user.interests.split("&&"))
        chosen_article = \
            random.choice(wikipedia.search(interest_choice, results=200))
        try:
            return flask.jsonify({
                "content": wikipedia.summary(chosen_article, sentences=2).replace("\n", ""),
                "title": chosen_article,
                "interest_choice": interest_choice
            })
        except:
            return flask.redirect("/get-article")
    return "No Auth"


@app.route("/login", methods=["POST", "GET"])
def login():
    if flask.request.method == "POST":
        user = User.query.filter_by(email=flask.request.values["email"]).first()
        if user.password == flask.request.values["password"]:
            login_user(user)
        return flask.redirect("/")
    return flask.render_template("login.html")


@app.route("/express_interest/<category>")
@login_required
def express_particular_interest(category):
    current_user.interests += "&&" + category
    db.session.commit()
    return "Completed"


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if flask.request.method == "POST":
        new_user = User(id=str(uuid.uuid4()), email=flask.request.values["email"],
                        password=flask.request.values["password"],
                        interests=flask.request.values["interests"].replace(",", "&&"))

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return flask.redirect("/")
    return flask.render_template("signup.html")
