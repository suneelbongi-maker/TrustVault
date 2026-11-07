
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import (
    login_user,
    logout_user,
    current_user,
    login_required
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Regexp

from extensions import limiter
from models.user import User

auth = Blueprint("auth", __name__)


class LoginForm(FlaskForm):

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Regexp(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                message="Enter a valid email address."
            )
        ]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    remember_me = BooleanField("Remember me")
    submit = SubmitField("Sign In")


# Login Route
@auth.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.is_active and user.check_password(form.password.data):

            session.clear()

            login_user(
                user,
                remember=form.remember_me.data,
                fresh=True
            )

            flash("Login successful!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)


# Logout Route
@auth.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have logged out successfully.", "success")

    return redirect(url_for("auth.login"))
