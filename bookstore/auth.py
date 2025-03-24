from flask import Blueprint, render_template, flash, redirect, url_for
from .forms import SignUpForm, LoginForm, PasswordChangeForm  # ✅ Add LoginForm here
from .models import Customer
from . import db
from flask_login import login_user, login_required, logout_user


auth = Blueprint('auth', __name__)  # ✅ Define Blueprint

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        email = form.email.data

        # ✅ Validate DUT email
        if not (email.endswith("@dut4life.ac.za") or email.endswith("@dut.ac.za")):
            flash("Only DUT students can sign up with @dut4life.ac.za or @dut.ac.za emails.", "danger")
            return redirect(url_for('auth.sign_up'))

        # ✅ Check if email is already registered
        existing_user = Customer.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('auth.sign_up'))

        # ✅ Save user to database
        try:
            new_user = Customer(
                email=email,
                username=form.username.data,
                department=form.department.data
            )
            new_user.set_password(form.password1.data)  # Ensure set_password is correctly defined
            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()  # Rollback if error occurs
            flash(f"Error creating account: {str(e)}", "danger")

    else:
        # Debug form errors
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")

    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        customer = Customer.query.filter_by(email=email).first()

        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                return redirect('/')
            else:
                flash('Incorrect Email or Password')

        else:
            flash('Account does not exist please Sign Up')

    return render_template('login.html', form=form)


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    logout_user()
    return redirect('/')


@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)


@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password Updated Successfully')
                return redirect(f'/profile/{customer.id}')
            else:
                flash('New Passwords do not match!!')

        else:
            flash('Current Password is Incorrect')

    return render_template('change_password.html', form=form)







