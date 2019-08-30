from flask import (Blueprint, render_template, url_for, request, session, redirect, flash, current_app, Response)
from flask_login import current_user, login_required, login_user
import pandas as pd
from ebay_research import db
from ebay_research.data_analysis import EasyEbayData
from ebay_research.models import User, Search
from ebay_research.forms import FreeSearch, EmailForm, LoginForm
from ebay_research.plot_maker import (
    create_us_county_map,
    make_price_by_type,
    prep_tab_data,
    make_sunburst,
    summary_stats,
    make_listing_pie_chart,
)

# TODO: The main login isn't working... 

# TODO: set the redis key to a specific user, with a timeout
# TODO: add position for flashed warnings
# TODO: Add logout
# TODO: better css classes for see it on ebay & download file
# TODO: look up why you should use flask.g.user & before_request
# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Create figure or data for Category ID info & get sub category info for biggest category
# TODO: Create ability to hide/show different plots in the results
# TODO: Provide credit to https://www.flaticon.com/ for icons

main = Blueprint("main", __name__)


@main.route("/", methods=["GET", "POST"])
def home():
    # TODO: Save email in posgres table
    # TODO: Possibly add a counter on table to limit to 5 free searches
    form = EmailForm()
    print('0*******')
    print(form.email.data)
    if form.validate_on_submit():
        print('1*********')
        session["email"] = form.confirm_email.data
        user_exists = User.query.filter_by(email=session['email']).first()
        if user_exists:
            flash('That email is already registered! Please login or reset password', 'danger')
        else:
            # change default permissions to 0
            new_user = User(email=session['email'], password=form.password.data, permissions=0,
                            country=form.location.data, state=form.state.data)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            session['id'] = new_user.id
            print('2*********')
            return redirect(url_for("main.basic_search"))
    return render_template("home.html", form=form)


@main.route("/login", methods=["GET", "POST"])
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


@main.route("/basic_search", methods=["GET", "POST"])
@login_required
def basic_search():
    form = FreeSearch()
    if form.validate_on_submit():
        keywords = form.keywords_include.data.strip()
        excluded_words = form.keywords_exclude.data.strip()
        min_price, max_price = form.minimum_price.data, form.maximum_price.data
        sort_order = request.form.get("item_sort")
        listing_type = request.form.get("listing_type")
        condition = request.form.get("condition")
        search = EasyEbayData(
            api_id=current_app.config["EBAY_API"],
            keywords=keywords,
            excluded_words=excluded_words,
            sort_order=sort_order,
            wanted_pages=1,
            min_price=min_price,
            max_price=max_price,
            listing_type=listing_type,
            item_condition=condition,
        )
        df = search.get_data()
        search_record = Search(user_id=current_user.id, full_query=search.full_query)
        if isinstance(df, str):
            search_record.is_successful = False
            db.session.add(search_record)
            db.session.commit()
            if df == "connection_error":
                flash(
                    "Uh oh! There seems to be a problem connecting to the API, please try again later!",
                    "danger",
                )
            else:
                flash(
                    "There were no results for those search parameters, please try a different search.",
                    "danger",
                )
            return render_template("basic_search.html", form=form)
        search_record.is_successful = True
        db.session.add(search_record)
        db.session.commit()
        # TODO: check if something needs to be deleted here first
        current_app.redis.set(current_user.id, df.to_msgpack(compress="zlib"), ex=120)
        tab_data = prep_tab_data(df)
        df_map = create_us_county_map(df)
        df_type = make_price_by_type(df)
        df_pie = make_listing_pie_chart(df["listingType"])
        stats = summary_stats(df, search.largest_category, search.largest_sub_category)
        if search.item_aspects is None:
            sunburst_plot = None
        else:
            sunburst_plot = make_sunburst(search.item_aspects)
        return render_template(
            "basic_search.html",
            form=form,
            map_plot=df_map,
            tab_data=tab_data.to_dict(orient="records"),
            hist_plot=df["currentPrice_value"].tolist(),
            df_pie=df_pie,
            df_type=df_type,
            make_sunburst=sunburst_plot,
            stats=stats,
            page_url=search.search_url,
            total_entries=search.total_entries,
        )
    return render_template("basic_search.html", form=form)


@main.route("/get_csv", methods=["GET"])
def get_csv():
    df = pd.read_msgpack(current_app.redis.get("change_me"))
    return Response(
        df.to_csv(index=False),
        content_type="text/csv",
        headers={"Content-Disposition": "attachment;filename=ebay_research.csv"},
    )
