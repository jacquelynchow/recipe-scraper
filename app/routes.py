from flask import render_template, flash, redirect, request, url_for
from app import app, db, mail
from app.forms import LoginForm, SignUpForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Recipe
from werkzeug.urls import url_parse
from app.forms import ResetRequestForm, ResetPasswordForm
from app.email import *

@app.route("/", methods=["GET"])
def index():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    # check if user is already logged in or not
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # if not a logged in user, create the sign up form
    form = SignUpForm()
    # if valid login, add user data to the database
    if form.validate_on_submit():
        # get username from form filled user
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You're now registered. Enjoy our app!", "success")
        # redirect user to login page
        return redirect(url_for('login'))
    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    # value of current_user can be a user object from the database 
    # or a special anonymous user object if the user did not log in yet
    # check if user is already logged in or not
    if current_user.is_authenticated:
        return redirect(url_for('searchRecipes'))
    # instantiate form object
    form = LoginForm()
    # if at least one field fails validation, then the function will return False, 
    # and that will cause the form to be rendered back to the user
    if form.validate_on_submit():
        # get username from form filled user
        user = User.query.filter_by(username=form.username.data).first()
        # the username can be invalid, or the password can be incorrect for the user
        # takes pw hash stored with the user and determines if pw entered in form matches the hash or not
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "warning")
            # redirect user back to login page
            return redirect(url_for('login'))
        # registers the user as logged in, so that means that any future pages the user 
        # navigates to will have the current_user variable set to that user.
        login_user(user, remember=form.remember_me.data)
        # If the user navigates to /index, for ex, @login_required will intercept the request & respond with 
        # a redirect to login page, but will add a query string argument to this URL, making the complete 
        # redirect URL: /login?next=/index.
        # if user just logged in and was to return to the last page they were on before logging in.
        next_page = request.args.get('next')
        # user had no redirects, bring them to recipe landing page
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('searchRecipes')
        # otherwise send them to the page they were last at before logging in
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route("/searchRecipes", methods=["GET"])
def searchRecipes():
    return render_template("searchRecipes.html")

@app.route("/saved/<username>")
@login_required # function is protected and will not allow access to users that aren't authenticated
def savedRecipes(username):
    # if there are no results automatically sends a 404 error back to client
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('savedRecipes.html', user=user)

@app.route("/results")
def recipeResults():
    return render_template('recipeResults.html')

@app.route("/random")
def randomRecipe():
    return render_template('randomRecipe.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email for the instructions to reset your password.", "info")
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if not user:
        flash("Invalid or expired token", "warning")
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset. You are now able to log in.", "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

"""
@app.cli.command("initdb")
def reset_db():
    # Drops and creates fresh database
    db.drop_all()
    db.create_all()
    print("Initialized default DB")

@app.cli.command("bootstrap")
def bootstrap_data():
    db.drop_all()
    db.create_all()
    db.session.add(
        User(
            username="jacq",
            email="icecreamjackie@gmail.com",
            password_hash="asdjfk123"
        )
    )
    db.session.commit()
    print("added development dataset")
"""