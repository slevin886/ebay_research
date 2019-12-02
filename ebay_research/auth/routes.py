from ebay_research import db
from ebay_research.models import User
from ebay_research.forms import EmailForm, SendConfirmation, LoginForm, ChangePassword, ContactForm
from ebay_research.auth import auth
from ebay_research.auth.email import send_email, send_comment
from flask import flash, render_template, url_for, redirect, session, request
from flask_login import logout_user, login_user, login_required, current_user


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = EmailForm()
    if form.validate_on_submit():
        session["email"] = form.email.data
        user_exists = User.query.filter_by(email=session['email']).first()
        if user_exists:
            flash('That email is already registered! Please login or reset password', 'danger')
        else:
            # change default permissions to 0
            new_user = User(email=session['email'], password=form.password.data, permissions=0,
                            country=form.location.data, state=form.state.data, confirmed=False)
            db.session.add(new_user)
            db.session.commit()
            send_email(new_user, 'Confirm your Genius Bidding account', 'email/confirm_email')
            flash('Please check your email to confirm your account and begin researching! If you do not'
                  ' receive your email soon, please check your spam folder.', 'success')
            return redirect(url_for("main.home"))

    if form.errors:
        errors = 'Please correct the following errors: '
        for err in form.errors.keys():
            errors = errors + ' ' + ' '.join(form.errors[err])
        flash(errors, 'warning')
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
        return redirect(url_for('searching.search'))


@auth.route("/password_reset", methods=['GET', 'POST'])
def password_reset():
    form = SendConfirmation()
    if form.validate_on_submit():
        email = form.confirm_email.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('That email has not been registered. Please check your spelling or register that account.', 'warning')
            return render_template('password_reset.html')
        send_email(user, 'Reset your password for Genius Bidding', 'email/reset_email')
        flash('An email has been sent to that address. Please follow the enclosed link to reset your password', 'warning')
        return redirect(url_for('main.home'))
    return render_template('password_reset.html', form=form)


@auth.route("/change_password/<token>", methods=['GET', 'POST'])
def change_password(token):
    form = ChangePassword()
    if form.validate_on_submit():
        user = User.confirm_token(token)
        if not user:
            flash('Whoops! Your token has expired, enter your email again to receive a new confirmation token.', 'danger')
            return redirect(url_for('auth.password_reset'))
        user.set_password(form.password.data)
        db.session.commit()
        flash('You have successfully changed your password', 'success')
        return redirect(url_for('auth.login'))
    return render_template('change_password.html', form=form, token=token)


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
            send_email(user, 'Confirm your email for Genius Bidding', 'email/confirm_email')
            flash('Please check your email to confirm your account and begin searching!', 'success')
            return redirect(url_for("main.home"))
    return render_template('confirmation.html', form=form)


@auth.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    # TODO: set up contact form
    form = ContactForm()
    if form.validate_on_submit():
        subject, user_message = form.category.data, form.text_area_field.data
        send_comment(current_user.email, subject, user_message)
        flash('Thank you for your message!', 'success')
        return redirect(url_for("main.home"))
    return render_template('contact.html', form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.email.data, form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.validate_password(password):
            if request.form.get('remember_me'):
                login_user(user, remember=True)
            else:
                login_user(user)
            session['id'] = user.id
            return redirect(url_for('searching.search'))
        else:
            flash('Whoops! Check that you entered the correct password & email!', 'danger')
    return render_template("login.html", form=form)


@auth.route("/logout", methods=["GET"])
def logout():
    logout_user()
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('main.home'))
