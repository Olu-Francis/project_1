from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, ValidationError

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

TYPE_CHOICES = [('', 'Select a type'), ('Income', 'Income'), ('Expense', 'Expenses')]

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
    balance = db.Column(db.Integer, default=0)
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
    duration = IntegerField(label="How long will this transaction occur", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create route decorators
@app.route("/")
def index():
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).limit(limit=4)
    date = datetime.now().year
    return render_template("index.html", user_transactions=user_transactions, date=date)


@app.route("/help-center")
def help_center():
    date = datetime.now().year
    return render_template("help-center.html", date=date)


@app.route("/profile")
def profile():
    date = datetime.now().year
    return render_template("profile.html", date=date)


@app.route("/settings")
def settings():
    date = datetime.now().year
    return render_template("setting.html", date=date)


# Get the individual transaction details and update transaction record in the database
@app.route('/transaction/<int:transaction_id>', methods=["GET", "POST"])
def transaction_detail(transaction_id):
    form = TransactionForm()
    transaction = Transactions.query.get_or_404(transaction_id)
    if request.method == "POST":
        transaction.amount = form.amount.data
        transaction.trans_type = form.trans_type.data
        transaction.recurring_trans = form.recurring_trans.data
        transaction.duration = form.duration.data
        try:
            db.session.commit()
            flash("Transaction Updated Successfully")
            date = datetime.now().year
            return redirect(url_for('transaction_detail', transaction=transaction, date=date,
                                    form=form, transaction_id=transaction_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error!!... There was a problem updating your record: {str(e)}")
            date = datetime.now().year
            return redirect(url_for('transaction_detail', transaction=transaction, date=date,
                                    form=form, transaction_id=transaction_id))
    else:
        form.amount.data = transaction.amount
        form.trans_type.data = transaction.trans_type
        form.recurring_trans.data = transaction.recurring_trans
        form.duration.data = transaction.duration
        date = datetime.now().year
        return render_template('transaction_detail.html', transaction=transaction, date=date,
                               form=form, transaction_id=transaction_id)


# @app.route('/transaction/<int:transaction_id>', methods=["GET", "POST"])
# def transaction_detail(transaction_id):
#     form = TransactionForm()
#     transaction = Transactions.query.get_or_404(transaction_id)
#     if request.method == "POST":
#         transaction.amount = request.form["amount"]
#         transaction.trans_type = request.form["trans_type"]
#         transaction.recurring_trans = request.form["recurring_trans"]
#         transaction.duration = request.form["duration"]
#         try:
#             db.session.commit()
#             flash("Transaction Updated Successfully")
#             return redirect(url_for('transaction_detail', transaction_id=transaction_id))
#         except Exception as e:
#             db.session.rollback()
#             flash(f"Error!!... There was a problem updating your record: {str(e)}")
#             return redirect(url_for('transaction_detail', transaction_id=transaction_id))
#     else:
#         form.amount.data = transaction.amount
#         form.trans_type.data = transaction.trans_type
#         form.recurring_trans.data = transaction.recurring_trans
#         form.duration.data = transaction.duration
#         date = datetime.now().year
#         return render_template('transaction_detail.html', transaction=transaction, date=date,
#                                form=form, transaction_id=transaction_id)


# @app.route("/transaction-details")
# def transaction_detail():
#     return render_template("transaction_detail.html")


@app.route("/wallet")
def wallet():
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).all()
    date = datetime.now().year
    return render_template("wallet.html", user_transactions=user_transactions, date=date)


# Create Transaction forms
@app.route("/add-transaction", methods=['GET', 'POST'])
def add_transaction_detail():
    form = TransactionForm()
    if form.validate_on_submit():
        if form.recurring_trans.data == 1:
            form.recurring_trans.data = True
            new_transaction = Transactions(
                amount=form.amount.data,
                trans_type=form.trans_type.data,
                recurring_trans=form.recurring_trans.data,
                duration=form.duration.data
            )
            db.session.add(new_transaction)
            db.session.commit()
        else:
            form.recurring_trans.data = False
            new_transaction = Transactions(
                amount=form.amount.data,
                trans_type=form.trans_type.data,
                recurring_trans=form.recurring_trans.data,
                duration=form.duration.data
            )
            db.session.add(new_transaction)
            db.session.commit()
        return redirect(url_for("wallet"))
    date = datetime.now().year
    return render_template('transaction_form.html', form=form, date=date)
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
    #     render_template("transaction_detail.html",
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

# TODO: 1.) Work on the Deletion of transaction
#  2.) Balance record keeping


# Create Custom Error Pages

# Invalid URL Page
@app.errorhandler(404)
def page_not_found(e):
    date = datetime.now().year
    return render_template("404.html", date=date), 404


# Internal Server Error Page
@app.errorhandler(500)
def page_not_found(e):
    date = datetime.now().year
    return render_template("500.html", date=date), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
