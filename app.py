from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import DataRequired

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "uyfhgfcnbfbgfdgfdhbdfgfdgf"

# Create a Form Class



# Create route decorators

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/help-center")
def help_center():
    return render_template("help-center.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/settings")
def settings():
    return render_template("setting.html")


@app.route("/transaction-details")
def transaction_detail():
    return render_template("transaction-detail.html")


@app.route("/wallet")
def wallet():
    return render_template("wallet.html")


# Create Custom Error Pages


# Invalid URL Page
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error Page
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
