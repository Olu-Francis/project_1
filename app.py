import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat
from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (StringField, SubmitField, SelectField, IntegerField, TextAreaField, TelField, PasswordField)
from wtforms.validators import DataRequired, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from collections import defaultdict
import uuid as uuid
import calendar
import os

TYPE_CHOICES = [(None, 'Select a type'), ('Income', 'Income'), ('Expense', 'Expenses')]
CATEGORY_CHOICES = [(None, 'Select a type'), ('Freelance Job', 'Freelance Job'), ('Salary', 'Salary'), ('Gift', 'Gift'),
                    ('Groceries', 'Groceries'), ('Utilities', 'Utilities'), ('Travel', 'Travel'),
                    ('Miscellaneous', 'Miscellaneous'), ('Mortgage', 'Mortgage'), ('Weekend Fun', 'Weekend Fun'),
                    ('Transportation', 'Transportation'), ('Dates', 'Dates'),
                    ('Vehicle Maintenance', 'Vehicle Maintenance'), ('Vehicle Repairs', 'Vehicle Repairs'),
                    ('School Fees', 'School Fees'), ('Take-outs', 'Take-outs'), ('Bills', 'Bills'),
                    ('Rent', 'Rent'), ('Coffee, Teas, etc', 'Morning Rituals (coffee, tea,...)')]
RECURRING_CHOICES = [(None, 'Select a type'), ('Annually', 'Annually'), ('Quarterly', 'Quarterly'),
                     ('Trimester', 'Trimester'), ('Semester', 'Semester'), ('Monthly', 'Monthly'),
                     ('Fortnightly', 'Fortnightly'), ('Weekly', 'Weekly'), ('Once', 'Once')]
DURATION_CHOICES = [(None, 'Select a type'), (0, 'Once'), (1, 'A Month'), (2, 'Two Months'), (3, 'Three Months'),
                    (4, 'Four Months'), (5, 'Five Months'), (6, 'Six Months'), (7, 'Seven Months'), (8, 'Eight Months'),
                    (9, 'Nine Months'), (10, '10 Months'), (11, '11 Months'), (12, '12 Months')]
UPLOAD_FOLDER = "static/images/"
DEFAULT_PIC = "profile/profile-user.png"

# Create a Flask Instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "uyfhgfcnbfbgfdgfdhbdfgfdgf"
# Database connection I need this: 'pip install mysql-connector' and 'pip install mysql-connector-python' and 'pip
# install mysql-connector-python-rf'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:rootpass@localhost/test'
# Initialize the Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Set the upload folder
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# Flask Login To do
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.VARCHAR(60), primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    first_name = db.Column(db.String(200), nullable=False)
    last_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(180), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Integer, default=0, nullable=False)
    profile_pic = db.Column(db.String(100), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.now)
    password_hash = db.Column(db.String(180), nullable=False)
    transactions = db.relationship('Transactions', backref='users', lazy=True)

    # Do Password Logic
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!!")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_balance(self):
        """Recalculate the user's balance based on all transactions."""
        income = sum([txn.amount for txn in self.transactions if txn.trans_type == 'Income'])
        expense = sum([txn.amount for txn in self.transactions if txn.trans_type == 'Expense'])
        self.balance = income - expense
        db.session.commit()

    # Create a String
    def __repr__(self):
        return '<Name %r>' % self.name


class Transactions(db.Model):
    id = db.Column(db.VARCHAR(60), primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    trans_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(150), nullable=False)
    transaction_frequency = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(25), nullable=True)
    duration = db.Column(db.Integer, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    # Foreign key to User
    user_id = db.Column(db.VARCHAR(60), db.ForeignKey('users.id'), nullable=False)

    @staticmethod
    def create_transaction(form, user):
        """Handle creating a new transaction and updating user balance."""
        new_transaction = Transactions(
            id=str(uuid.uuid4()),
            amount=form.amount.data,
            trans_type=form.trans_type.data,
            category=form.category.data,
            transaction_frequency=form.transaction_frequency.data,
            duration=form.duration.data,
            description=form.description.data,
            user_id=user.id,
        )
        db.session.add(new_transaction)
        user.update_balance()

    @staticmethod
    def update_transaction(transaction, form):
        """Handle updating an existing transaction and user balance."""
        transaction.amount = form.amount.data
        transaction.trans_type = form.trans_type.data
        transaction.transaction_frequency = form.transaction_frequency.data
        transaction.duration = form.duration.data
        transaction.category = form.category.data
        transaction.description = form.description.data
        db.session.commit()
        transaction.users.update_balance()

    @staticmethod
    def delete_transaction(transaction):
        """Handle deleting a transaction and updating user balance."""
        db.session.delete(transaction)
        transaction.users.update_balance()

    def __repr__(self):
        return '<Transaction %r>' % self.id


# Create a Form Class

class UserForm(FlaskForm):
    first_name = StringField(label="First Name", validators=[DataRequired()])
    last_name = StringField(label="Last Name", validators=[DataRequired()])
    username = StringField(label="Username", validators=[DataRequired()])
    email = StringField(label="Email", validators=[DataRequired()])
    phone = TelField(label="Phone")
    profile_pic = FileField(label="Profile Pic")
    password = PasswordField(label="Password", validators=[DataRequired(), EqualTo("password1",
                                                                                   message="Password Must Match")])
    password1 = PasswordField(label="Re-enter Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TransactionForm(FlaskForm):
    amount = IntegerField(label="Amount", validators=[DataRequired()])
    trans_type = SelectField(label="Transaction Type", choices=TYPE_CHOICES, validators=[DataRequired()])
    category = SelectField(label="Category", choices=CATEGORY_CHOICES, validators=[DataRequired()])
    transaction_frequency = SelectField(label="Frequency Of This Transaction", choices=RECURRING_CHOICES,
                                        validators=[DataRequired()])
    duration = SelectField(label="Duration Of This Transaction", choices=DURATION_CHOICES, validators=[DataRequired()])
    description = TextAreaField(label="Additional Details")
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# @app.route('/user/add', methods=['GET', 'POST'])
# def add_user():
#     first_name = None
#     form = UserForm()
#
#     def process_phone_number(raw_phone_number, default_region='NG'):
#         try:
#             # Parse the phone number
#             phone_number = phonenumbers.parse(raw_phone_number, default_region)
#
#             # Check if the phone number is valid
#             if not phonenumbers.is_valid_number(phone_number):
#                 raise ValueError("Invalid phone number")
#
#             # Format the number to the international format
#             formatted_number = phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
#             return formatted_number
#
#         except NumberParseException as f:
#             raise ValueError(f"Error parsing phone number: {f}")
#
#     if form.validate_on_submit():
#         user = Users.query.filter_by(email=form.email.data).first()
#         try:
#             if user is None:
#                 # Hash the password
#                 hashed_pw = generate_password_hash(form.password.data)
#                 phone = process_phone_number(form.phone.data)
#                 image = request.files['profile_pic']
#                 # Grab image first_name
#                 pic_filename = secure_filename(image.profile_pic.filename)
#                 # Set UUID for image
#                 pic_name = str(current_user.id) + '_' + pic_filename
#                 # Save the image
#                 image.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
#                 user = Users(
#                     id=str(uuid.uuid4()),
#                     first_name=form.first_name.data.title(),
#                     username=form.username.data,
#                     email=form.email.data,
#                     balance=0,
#                     phone=phone,
#                     password_hash=hashed_pw,
#                     profile_pic=pic_name,
#                 )
#                 db.session.add(user)
#                 db.session.commit()
#             first_name = form.first_name.data
#             form.first_name.data = ''
#             form.username.data = ''
#             form.email.data = ''
#             form.phone.data = ''
#             form.password.data = ''
#
#             flash("User Added Successfully!")
#         except ValueError as e:
#             print(e)
#     our_users = Users.query.order_by(Users.date_added)
#     return render_template("add_user.html",
#                            form=form,
#                            first_name=first_name,
#                            our_users=our_users)
# @app.route('/user/add', methods=['GET', 'POST'])
# def add_user():
#     form = UserForm()
#     first_name = None
#
#     if form.validate_on_submit():
#         user = Users.query.filter_by(email=form.email.data).first()
#
#         if user is None:
#             try:
#                 # Process and validate the phone number
#                 phone = process_phone_number(form.phone.data)
#
#                 # Hash the password
#                 hashed_pw = generate_password_hash(form.password.data)
#
#                 # Handle profile picture upload
#                 image = request.files['profile_pic']
#                 pic_filename = secure_filename(image.filename)
#                 pic_name = f"{uuid.uuid4()}_{pic_filename}"
#                 image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
#
#                 # Create and add the new user
#                 user = Users(
#                     id=str(uuid.uuid4()),
#                     first_name=form.first_name.data.title(),
#                     username=form.username.data,
#                     email=form.email.data,
#                     balance=0,
#                     phone=phone,
#                     password_hash=hashed_pw,
#                     profile_pic=pic_name,
#                 )
#                 db.session.add(user)
#                 db.session.commit()
#
#                 flash("User Added Successfully!")
#                 # Clear form fields
#                 form = UserForm()
#             except ValueError as e:
#                 flash(str(e), "error")
#
#         else:
#             flash("Email already registered.", "error")
#
#     our_users = Users.query.order_by(Users.date_added).all()
#
#     return render_template("add_user.html", form=form, first_name=first_name, our_users=our_users)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()

    if form.validate_on_submit():
        existing_user = Users.query.filter_by(email=form.email.data).first()

        if existing_user is None:
            try:
                # Process and validate the phone number
                phone = process_phone_number(form.phone.data)

                # Handle profile picture upload
                image = request.files.get('profile_pic')
                if image and image.filename != '':
                    pic_filename = secure_filename(image.filename)
                    pic_name = f"{uuid.uuid4()}_{pic_filename}"
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                else:
                    pic_name = DEFAULT_PIC  # Set to a default image

                # Create and add the new user
                new_user = Users(
                    id=str(uuid.uuid4()),
                    first_name=form.first_name.data.title(),
                    last_name=form.last_name.data.title(),
                    username=form.username.data,
                    email=form.email.data,
                    balance=0,
                    phone=phone,
                    password_hash=generate_password_hash(form.password.data),
                    profile_pic=pic_name,
                )
                db.session.add(new_user)
                db.session.commit()

                flash("User added successfully!", "success")
                return redirect(url_for('login'))
            except ValueError as e:
                flash(str(e), "danger")
        else:
            flash("Email already registered.", "danger")

    our_users = Users.query.order_by(Users.date_added).all()
    return render_template("add_user.html", form=form, our_users=our_users)


def process_phone_number(raw_phone_number, default_region='NG'):
    try:
        # Parse the phone number
        phone_number = phonenumbers.parse(raw_phone_number, default_region)

        # Validate and format the phone number
        if not phonenumbers.is_valid_number(phone_number):
            raise ValueError("Invalid phone number")

        return phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
    except NumberParseException as e:
        raise ValueError(f"Error parsing phone number: {e}")


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


# Pass data to Extended HTML files
# @app.context_processor
# def base():
#     pass

@app.route('/get_latest_data')
@login_required
def get_latest_data():
    user = Users.query.get(current_user.id)
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})

    for transaction in user.transactions:
        month = transaction.date_added.month - 1  # Adjusting month to be 0-indexed for use in charts
        if transaction.trans_type.lower() == 'income':
            monthly_data[month]['income'] += transaction.amount
        elif transaction.trans_type.lower() == 'expense':
            monthly_data[month]['expense'] += transaction.amount

    data = {
        'balance': user.balance,
        'income_data': [monthly_data[month]['income'] for month in range(12)],
        'expense_data': [monthly_data[month]['expense'] for month in range(12)],
        'income_sum': sum([monthly_data[month]['income'] for month in range(12)]),
        'expense_sum': sum([monthly_data[month]['expense'] for month in range(12)]),
    }
    return data


# def get_latest_data():
#     user = Users.query.get(current_user.id)
#     transactions = Transactions.query.filter_by(user_id=user.id).all()
#
#     # Initialize data for each month
#     monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0})
#
#     for trans in transactions:
#         month = trans.date_added.month
#         if trans.trans_type == 'income':
#             monthly_data[month]['income'] += trans.amount
#         elif trans.trans_type == 'expense':
#             monthly_data[month]['expense'] += trans.amount
#
#     # Prepare data for the chart
#     income_data = [monthly_data[month]['income'] for month in range(1, 13)]
#     expense_data = [monthly_data[month]['expense'] for month in range(1, 13)]
#
#     data = {
#         'balance': user.balance,
#         'income_sum': sum(income_data),
#         'expense_sum': sum(expense_data),
#         'income_data': income_data,
#         'expense_data': expense_data,
#     }
#     print(data)
#     return data


# Create route decorators
@app.route("/")
@login_required
def index():
    # user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).limit(limit=4)
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).where(
        Transactions.user_id == current_user.id).limit(limit=4)
    user = Users.query.get(current_user.id)

    # Group transactions by month and type
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'balance': user.balance})

    for transaction in user.transactions:
        month = transaction.date_added.month
        if transaction.trans_type.lower() == 'income':
            monthly_data[month]['income'] += transaction.amount
        elif transaction.trans_type.lower() == 'expense':
            monthly_data[month]['expense'] += transaction.amount

    # Prepare data for the chart
    income_data = [monthly_data.get(month, {}).get('income', 0) for month in range(1, 13)]
    expense_data = [monthly_data.get(month, {}).get('expense', 0) for month in range(1, 13)]
    balance_data = [monthly_data[month]['balance'] for month in range(1, 13)]

    # Detect overspending by comparing expenses and income
    overspending = any(monthly_data[month]['expense'] > monthly_data[month]['income'] for month in range(1, 13))
    date = datetime.now().year
    return render_template("index.html", user_transactions=user_transactions, date=date,
                           income_data=income_data, expense_data=expense_data, balance=balance_data, user=user,
                           overspending=overspending)


@app.route("/help-center")
def help_center():
    date = datetime.now().year
    return render_template("help-center.html", date=date)


@app.route("/profile")
@login_required
def profile():
    date = datetime.now().year
    return render_template("profile.html", date=date)


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UserForm()
    user_to_update = Users.query.get_or_404(current_user.id)

    if request.method == "POST":
        user_to_update.first_name = form.first_name.data
        user_to_update.last_name = form.last_name.data
        user_to_update.email = form.email.data
        user_to_update.phone = form.phone.data

        # Check if a new profile picture is uploaded
        if 'profile_pic' in request.files:
            profile_pic_file = request.files['profile_pic']

            if profile_pic_file and profile_pic_file.filename != '':
                # Handle new profile picture upload
                pic_filename = secure_filename(profile_pic_file.filename)
                pic_name = str(current_user.id) + '_' + pic_filename
                pic_path = os.path.join(app.config['UPLOAD_FOLDER'], pic_name)
                profile_pic_file.save(pic_path)
                user_to_update.profile_pic = pic_name

        try:
            db.session.commit()
            flash("Profile Updated Successfully", "success")
            return redirect(url_for('settings'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating profile: {str(e)}", "danger")
            return redirect(url_for('settings'))

    else:
        form.first_name.data = user_to_update.first_name
        form.last_name.data = user_to_update.last_name
        form.email.data = user_to_update.email
        form.phone.data = user_to_update.phone
        date = datetime.now().year
        return render_template("setting.html", date=date, form=form)


# Get the individual transaction details and update transaction record in the database
@app.route('/transaction/<string:transaction_id>', methods=["GET", "POST"])
@login_required
def transaction_detail(transaction_id):
    transaction = Transactions.query.get_or_404(transaction_id)
    form = TransactionForm()

    if request.method == "POST":
        if current_user.id == transaction.users.id:
            try:
                Transactions.update_transaction(transaction, form)
                flash("Transaction Updated Successfully")
                return redirect(url_for('wallet'))
            except Exception as e:
                db.session.rollback()
                flash(f"Error!!... There was a problem updating your record: {str(e)}")
        else:
            flash(f"You Are Not Authorized To Perform This Action")
            return redirect(url_for('wallet'))
    else:
        form.amount.data = transaction.amount
        form.trans_type.data = transaction.trans_type
        form.transaction_frequency.data = transaction.transaction_frequency
        form.duration.data = transaction.duration
        form.category.data = transaction.category
        form.description.data = transaction.description
        date = datetime.now().year
        return render_template('transaction_detail.html', transaction=transaction, form=form, date=date,
                               transaction_id=transaction.id)


# def transaction_detail(transaction_id):
#     form = TransactionForm()
#     transaction = Transactions.query.get_or_404(transaction_id)
#     if request.method == "POST":
#         if current_user.id == transaction.users.id:
#             transaction.amount = form.amount.data
#             transaction.trans_type = form.trans_type.data
#             transaction.transaction_frequency = form.transaction_frequency.data
#             transaction.duration = form.duration.data
#             transaction.category = form.category.data
#             transaction.description = form.description.data
#             transaction.user_id = current_user.id
#             try:
#                 if transaction.trans_type == 'Income':
#                     current_user.balance += int(transaction.amount) * 2
#                 elif transaction.trans_type == 'Expense':
#                     current_user.balance -= int(transaction.amount) * 2
#                 db.session.commit()
#                 flash("Transaction Updated Successfully")
#                 date = datetime.now().year
#                 return redirect(url_for('wallet', transaction=transaction, date=date,
#                                         form=form, transaction_id=transaction_id))
#             except Exception as e:
#                 db.session.rollback()
#                 flash(f"Error!!... There was a problem updating your record: {str(e)}")
#                 date = datetime.now().year
#                 return redirect(url_for('transaction_detail', transaction=transaction, date=date,
#                                         form=form, transaction_id=transaction_id))
#         else:
#             flash(f"You Are Not Authorized To Perform This Action")
#             return redirect(url_for('wallet'))
#     else:
#         form.amount.data = transaction.amount
#         form.trans_type.data = transaction.trans_type
#         form.transaction_frequency.data = transaction.transaction_frequency
#         form.duration.data = transaction.duration
#         transaction.category = form.category.data
#         transaction.description = form.description.data
#         date = datetime.now().year
#         return render_template('transaction_detail.html', transaction=transaction, date=date,
#                                form=form, transaction_id=transaction_id)


# TODO: Search functionality for searching through transactions

# @app.route('/transaction/<int:transaction_id>', methods=["GET", "POST"])
# def transaction_detail(transaction_id):
#     form = TransactionForm()
#     transaction = Transactions.query.get_or_404(transaction_id)
#     if request.method == "POST":
#         transaction.amount = request.form["amount"]
#         transaction.trans_type = request.form["trans_type"]
#         transaction.transaction_frequency = request.form["transaction_frequency"]
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
#         form.transaction_frequency.data = transaction.transaction_frequency
#         form.duration.data = transaction.duration
#         date = datetime.now().year
#         return render_template('transaction_detail.html', transaction=transaction, date=date,
#                                form=form, transaction_id=transaction_id)


# @app.route("/transaction-details")
# def transaction_detail():
#     return render_template("transaction_detail.html")


@app.route("/wallet")
@login_required
def wallet():
    user = Users.query.get(current_user.id)
    user_transactions = Transactions.query.order_by(Transactions.date_added.desc()).where(
        Transactions.user_id == current_user.id)

    # Group transactions by month and type
    monthly_data = defaultdict(lambda: {'income': 0, 'expense': 0, 'balance': user.balance})

    for transaction in user.transactions:
        month = transaction.date_added.month
        if transaction.trans_type.lower() == 'income':
            monthly_data[month]['income'] += transaction.amount
        elif transaction.trans_type.lower() == 'expense':
            monthly_data[month]['expense'] += transaction.amount

    # Prepare data for the chart
    income_data = [monthly_data.get(month, {}).get('income', 0) for month in range(1, 13)]
    expense_data = [monthly_data.get(month, {}).get('expense', 0) for month in range(1, 13)]
    balance_data = [monthly_data[month]['balance'] for month in range(1, 13)]

    # Detect overspending by comparing expenses and income
    overspending = any(monthly_data[month]['expense'] > monthly_data[month]['income'] for month in range(1, 13))
    date = datetime.now().year
    month = datetime.now().month
    return render_template("wallet.html", user_transactions=user_transactions, date=date,
                           income_data=income_data, expense_data=expense_data, balance=balance_data, user=user,
                           overspending=overspending, month=month)

# def wallet():

#     user = Users.query.get(current_user.id)
#     user_transactions = user.transactions
#     incomes = Transactions.query.filter_by(trans_type='income')
#     expenses = Transactions.query.filter_by(trans_type='expense')
#     # user_data = {}
#     user_data = {
#         'balance': user.balance,
#         'income': [inc.amount for inc in incomes],
#         'expense': [exs.amount for exs in expenses],
#     }
#     income_data = user_data['income']
#     expense_data = user_data['expense']
#     balance = user_data['balance']
#     date = datetime.now().year
#     return render_template("wallet.html", user_transactions=user_transactions, date=date,
#                            income_data=income_data, expense_data=expense_data, balance_data=balance_data, user=user,
#                            overspending=overspending)


# Create Transaction forms
@app.route("/add-transaction", methods=['GET', 'POST'])
@login_required
def add_transaction_detail():
    form = TransactionForm()
    if form.validate_on_submit():
        try:
            Transactions.create_transaction(form, current_user)
            return redirect(url_for("wallet"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error!!... There was a problem adding your transaction: {str(e)}")
    date = datetime.now().year
    return render_template('transaction_form.html', form=form, date=date)


# def add_transaction_detail():
#     form = TransactionForm()
#     user = Users.query.get_or_404(current_user.id)
#
#     if form.validate_on_submit():
#         # Determine if the transaction is recurring
#         recurring = form.transaction_frequency.data == 1
#
#         # Calculate the balance after the transaction
#         if form.trans_type.data == 'Income':
#             user.balance += int(form.amount.data)
#         elif form.trans_type.data == 'Expense':
#             user.balance -= int(form.amount.data)
#
#         balance = user.balance
#         # Create a new transaction
#         new_transaction = Transactions(
#             id=str(uuid.uuid4()),
#             amount=form.amount.data,
#             trans_type=form.trans_type.data,
#             category=form.category.data,
#             transaction_frequency=recurring,
#             duration=form.duration.data,
#             description=form.description.data,
#             user_id=current_user.id,
#         )
#         db.session.add(new_transaction)
#         db.session.commit()
#
#         # Update the user's current balance
#         user.balance = balance
#         db.session.commit()
#
#         return redirect(url_for("wallet"))
#
#     date = datetime.now().year
#     return render_template('transaction_form.html', form=form, date=date)

# amount = None
# trans_type = None
# transaction_frequency = None
# duration = None
# form = TransactionForm()
# # Validate Form
# if form.validate_on_submit():
#     amount = form.amount.data
#     form.amount.data = None
#     trans_type = form.trans_type.data
#     form.trans_type.data = None
#     transaction_frequency = form.transaction_frequency.data
#     form.transaction_frequency.data = None
#     duration = form.duration.data
#     form.duration.data = None
#     flash("Details Added Successfully!!")
#     render_template("transaction_detail.html",
#                     amount=amount,
#                     trans_type=trans_type,
#                     transaction_frequency=transaction_frequency,
#                     duration=duration,
#                     form=form)
# return render_template("transaction_form.html",
#                        amount=amount,
#                        trans_type=trans_type,
#                        transaction_frequency=transaction_frequency,
#                        duration=duration,
#                        form=form, )


@app.route("/delete/<string:id>")
@login_required
def delete(id):
    transaction = Transactions.query.get_or_404(id)
    if current_user.id == transaction.users.id:
        try:
            Transactions.delete_transaction(transaction)
            return redirect(url_for('wallet'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error!!... There was a problem deleting your transaction: {str(e)}")
    else:
        flash(f"You Are Not Authorized To Perform This Action")
        return redirect(url_for('wallet'))


# def delete(id):
#     delete_transaction = Transactions.query.get_or_404(id)
#     user = Users.query.get_or_404(current_user.id)
#     if current_user.id == delete_transaction.users.id:
#         try:
#             # Calculate the balance after the transaction
#             if delete_transaction.trans_type == 'Income':
#                 user.balance -= int(delete_transaction.amount)
#             elif delete_transaction.trans_type == 'Expense':
#                 user.balance += int(delete_transaction.amount)
#
#             balance_after = user.balance
#
#             # Update the user's current balance
#             user.balance = balance_after
#             db.session.commit()
#
#             # Delete the transaction
#             db.session.delete(delete_transaction)
#             db.session.commit()
#             return redirect(url_for('wallet'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f"Error!!... There was a problem deleting your record: {str(e)}")
#             return redirect(url_for('wallet'))
#     else:
#         flash(f"You Are Not Authorized To Perform This Action")
#         return redirect(url_for('wallet'))


@app.route("/delete_user/<string:id>")
def delete_user(id):
    delete_users = Users.query.get_or_404(id)
    user_transactions = Transactions.query.where(Transactions.user_id == id)
    try:
        for tran in user_transactions:
            db.session.delete(tran)
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
    print(e)
    date = datetime.now().year
    return render_template("404.html", date=date), 404


# Internal Server Error Page
@app.errorhandler(500)
def page_not_found(e):
    print(e)
    date = datetime.now().year
    return render_template("500.html", date=date), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
