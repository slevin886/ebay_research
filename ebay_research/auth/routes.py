from ebay_research import db
from ebay_research.models import User
from ebay_research.forms import EmailForm, SendConfirmation, LoginForm
from ebay_research.auth import auth
from ebay_research.auth.email import send_confirmation_email

from flask import flash, render_template, url_for, redirect, session
from flask_login import logout_user, login_user


@auth.route("/register", methods=["GET", "POST"])
def register():
    # TODO: Possibly add a counter on table to limit to 5 free searches
    form = EmailForm()
    if form.validate_on_submit():
        session["email"] = form.confirm_email.data
        user_exists = User.query.filter_by(email=session['email']).first()
        if user_exists:
            flash('That email is already registered! Please login or reset password', 'danger')
        else:
            # change default permissions to 0
            new_user = User(email=session['email'], password=form.password.data, permissions=0,
                            country=form.location.data, state=form.state.data, confirmed=False)
            db.session.add(new_user)
            db.session.commit()
            send_confirmation_email(new_user)
            flash('Please check your email to confirm your account and begin researching!', 'success')
            return redirect(url_for("main.home"))
    return render_template("register.html", form=form)


@auth.route("/confirmation/<token>", methods=["GET"])
def confirmation(token):
    user = User.confirm_token(token)
    if not user:
        form = SendConfirmation()
        flash('Whoops! Your token has expired, enter your email and password'
              ' again to receive a new confirmation token.', 'danger')
        return render_template("confirmation.html", form=form)
    else:
        user.confirm_account()
        db.session.commit()
        login_user(user)
        session['id'] = user.id
        flash('You have successfully confirmed your email! Start searching!', 'success')
        return redirect(url_for('main.basic_search'))


@auth.route("/confirmation")
def resend_confirmation():
    form = SendConfirmation()
    if form.validate_on_submit():
        email = form.confirm_email.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('That email has not been registered. Please register', 'warning')
            return redirect(url_for('auth.register'))
        elif user.confirmed:
            flash('You are already confirmed! Login to begin searching', 'warning')
            return redirect(url_for('auth.login'))
        else:
            send_confirmation_email(user)
            flash('Please check your email to confirm your account and begin researching!', 'success')
            return redirect(url_for("main.home"))
    return render_template('confirmation.html', form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.email.data, form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.validate_password(password):
            login_user(user)
            session['id'] = user.id
            return redirect(url_for('main.basic_search'))
        else:
            flash('Whoops! Check that you entered the correct password & email!', 'danger')
    return render_template("login.html", form=form)


@auth.route("/logout", methods=["GET"])
def logout():
    logout_user()
    session.clear()
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('main.home'))
