import re
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, FileField, SelectField, BooleanField, IntegerField, ValidationError,
                     TelField, PasswordField)
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

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
migrate = Migrate(app, db)
# Flask Login To do
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Integer, default=0, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    # Do Password Logic
    password_hash = db.Column(db.String(180), nullable=False)

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

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

class UserForm(FlaskForm):
    name = StringField(label="Name", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    phone = TelField(label="Phone")
    password = PasswordField(label="Password", validators=[DataRequired(), EqualTo("password1",
                                                                                   message="Password Must Match")])
    password1 = PasswordField(label="Re-enter Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TransactionForm(FlaskForm):
    amount = IntegerField(label="Amount", validators=[DataRequired()])
    trans_type = SelectField(label="Type", choices=TYPE_CHOICES, validators=[DataRequired()])
    recurring_trans = BooleanField(label="Is this a recurring transaction")
    duration = IntegerField(label="How long will this transaction occur", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()

    def validate_phone_number(phone_number):
        pattern = re.compile(r'^\+?\d{10,15}$')
        if pattern.match(phone_number):
            return phone_number
        else:
            raise ValueError("Invalid phone number")

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        # Example usage
        try:
            if user is None:
                # Hash the password
                hashed_pw = generate_password_hash(form.password.data)
                phone = validate_phone_number(form.phone.data)
                user = Users(name=form.name.data, username=form.username.data, email=form.email.data, balance=0,
                             phone=phone, password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
            name = form.name.data
            form.name.data = ''
            form.username.data = ''
            form.email.data = ''
            form.phone.data = ''
            form.password.data = ''

            flash("User Added Successfully!")
        except ValueError as e:
            print(e)
    our_users = Users.query.order_by(Users.date_added)
    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)


# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Clear the form
        form.email.data = ''
        form.password.data = ''

        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)


# Create Login Form
class LoginForm(FlaskForm):
    username = StringField(label="Username", validators=[DataRequired()])
    password = PasswordField(label="Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create login page
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for("index"))
            else:
                flash("Wrong Details - Try Again!")
        else:
            flash("Wrong Details - Try Again!")
    return render_template("login.html", form=form)


# Create logout page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You just logged out!")
    return redirect(url_for("login"))


# Create route decorators
@app.route("/")
@login_required
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


@app.route("/delete/<int:id>")
def delete(id):
    delete_transaction = Transactions.query.get_or_404(id)
    try:
        db.session.delete(delete_transaction)
        db.session.commit()
        return redirect(url_for('wallet'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error!!... There was a problem deleting your record: {str(e)}")
        return redirect(url_for('wallet'))


@app.route("/delete_user/<int:id>")
def delete_user(id):
    delete_users = Users.query.get_or_404(id)
    try:
        db.session.delete(delete_users)
        db.session.commit()
        return redirect(url_for('add_user'))
    except Exception as e:
        db.session.rollback()
        flash(f"Error!!... There was a problem deleting your record: {str(e)}")
        return redirect(url_for('add_user'))


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
