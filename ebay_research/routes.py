from flask import (Blueprint, render_template, request, flash, url_for)
from flask_login import current_user, login_required
from ebay_research import db
from ebay_research.models import Search, Results
from ebay_research.forms import ChooseNewPassword


# TODO: fix size of the spinner for mobile
# TODO: add how to/suggested use page
# TODO: make more mobile friendly
# TODO: possibly only draw figures on lastpull
# TODO: Add blog
# TODO: Add more information to home page and about page
# TODO: Add hover helpers on search page, plus more info on top
# TODO: reorganize search page to make # of items to pull more prominent
# TODO: implement repeat search on account page and possibly something to download search result metadata
# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Create ability to hide/show different plots in the results
# TODO: Provide credit to https://www.flaticon.com/ for icons

main = Blueprint("main", __name__)


@main.route('/', methods=["GET"])
def home():
    return render_template('home.html')


@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@main.route('/account/<user_id>', methods=['GET', 'POST'])
@login_required
def account(user_id):
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
    next_url = url_for('main.account', page=search_results.next_num, user_id=current_user.id) \
        if search_results.has_next else None
    prev_url = url_for('main.account', page=search_results.prev_num, user_id=current_user.id) \
        if search_results.has_prev else None
    return render_template('account.html', user_id=user_id, search_results=search_results.items,
                           number_searches=number_searches, password_form=password_form,
                           next_url=next_url, prev_url=prev_url)
