from flask import (Blueprint, render_template, request,
                   flash, url_for)
from flask_login import current_user, login_required
from ebay_research import db
from ebay_research.models import Search, Results, Recurring
from ebay_research.forms import ChooseNewPassword
from sqlalchemy import and_


# TODO: make navbar toggle to dropdown instead of new line
# TODO: add how to/suggested use page
# TODO: make more mobile friendly
# TODO: Add blog
# TODO: Add more information to home page and about page
# TODO: Add hover helpers on search page, plus more info on top
# TODO: ability to download from account page
# TODO: Write test functions
# TODO: Provide credit to https://www.flaticon.com/ for icons

main = Blueprint("main", __name__)


@main.route('/', methods=["GET"])
def home():
    return render_template('home.html')


@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@main.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    password_form = ChooseNewPassword()
    if password_form.validate_on_submit():
        password = password_form.old_password.data
        if current_user.validate_password(password):
            new_password = password_form.password.data
            current_user.set_password(new_password)
            db.session.commit()
            flash('You have successfully changed your password!', 'success')
        else:
            flash("Whoops! You entered the wrong password, please try again or reset it from the login page", 'danger')
    page = request.args.get('page', 1, type=int)
    number_searches = Search.query.filter_by(user_id=current_user.id).count()
    search_results = db.session.query(Search, Results).filter(Search.user_id == current_user.id).join(Results)\
        .order_by(Search.time_searched.desc()).paginate(page, 10, False)
    # creating pagination
    next_url = url_for('main.account', page=search_results.next_num) if search_results.has_next else None
    prev_url = url_for('main.account', page=search_results.prev_num) if search_results.has_prev else None
    recurring_searches = db.session.query(Recurring, Search).filter(
        and_(Recurring.user_id == current_user.id,
             Recurring.active == True,
             Recurring.search_id == Search.id)).all()
    return render_template('account.html',
                           password_form=password_form,
                           next_url=next_url,
                           prev_url=prev_url,
                           number_searches=number_searches,
                           recurring_searches=recurring_searches,
                           search_results=search_results.items)



