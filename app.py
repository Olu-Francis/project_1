from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

TYPE_CHOICES = [('1', 'Income'), ('2', 'Expenses')]

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "uyfhgfcnbfbgfdgfdhbdfgfdgf"
# Database connection I need this: 'pip install mysql-connector' and 'pip install mysql-connector-python' and 'pip
# install mysql-connector-python-rf'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootpass@localhost/our_users'
# Initialize the Database
db = SQLAlchemy(app)


# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now)

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name


class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    trans_type = db.Column(db.String(50), nullable=False)
    recurring_trans = db.Column(db.Boolean, default=False)
    duration = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Transaction %r>' % self.id


# Create a Form Class
class TransactionForm(FlaskForm):
    amount = IntegerField(label="Amount", validators=[DataRequired()])
    trans_type = SelectField(label="Type", choices=TYPE_CHOICES, validators=[DataRequired()])
    recurring_trans = BooleanField(label="Is this a recurring transaction")
    duration = IntegerField(label="How long will this transaction occur")
    submit = SubmitField("Submit")


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


# TODO: Get the individual transaction details
@app.route("/transaction-details")
def transaction_detail():
    return render_template("transaction-detail.html")


@app.route("/wallet")
def wallet():
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).all()
    return render_template("wallet.html", user_transactions=user_transactions)


# Create Transaction forms
@app.route("/add-transaction", methods=['GET', 'POST'])
def add_transaction_detail():
    form = TransactionForm()
    if form.validate_on_submit():
        new_transaction = Transactions(
            amount=form.amount.data,
            trans_type=form.trans_type.data,
            recurring_trans=form.recurring_trans.data,
            duration=form.duration.data
        )
        db.session.add(new_transaction)
        db.session.commit()
        return redirect(url_for("wallet"))
    return render_template('transaction_form.html', form=form)
    # amount = None
    # trans_type = None
    # recurring_trans = None
    # duration = None
    # form = TransactionForm()
    # # Validate Form
    # if form.validate_on_submit():
    #     amount = form.amount.data
    #     form.amount.data = None
    #     trans_type = form.trans_type.data
    #     form.trans_type.data = None
    #     recurring_trans = form.recurring_trans.data
    #     form.recurring_trans.data = None
    #     duration = form.duration.data
    #     form.duration.data = None
    #     flash("Details Added Successfully!!")
    #     render_template("transaction-detail.html",
    #                     amount=amount,
    #                     trans_type=trans_type,
    #                     recurring_trans=recurring_trans,
    #                     duration=duration,
    #                     form=form)
    # return render_template("transaction_form.html",
    #                        amount=amount,
    #                        trans_type=trans_type,
    #                        recurring_trans=recurring_trans,
    #                        duration=duration,
    #                        form=form, )


# @app.route('/transaction_detail/<int:transaction_id>')
# def transaction_detail(transaction_id):
#     transaction = Transactions.query.get_or_404(transaction_id)
#     return render_template('transaction-detail.html', transaction=transaction)


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
    with app.app_context():
        db.create_all()
    app.run(debug=True)
