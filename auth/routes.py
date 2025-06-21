from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, db
from .forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('auth.login'))

        # Hash the password before saving
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,  # ✅ required
            email=form.email.data,
            password=hashed_password,
            user_type='Customer'
        )
        
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Look up the user by email
        user = User.query.filter_by(email=form.email.data).first()

        # Validate password
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('home'))  # Change as per your main route
        else:
            flash("Invalid email or password", "danger")

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password')
def reset_password_request():
    return "Password reset page (coming soon)"
