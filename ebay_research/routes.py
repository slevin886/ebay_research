from flask import (Blueprint, render_template, request, flash, current_app, Response, redirect, url_for, session)
from flask_login import current_user, login_required
import pandas as pd
from ebay_research import db
from ebay_research.data_analysis import EasyEbayData
from ebay_research.support_functions import ingest_free_search_form, summary_stats
from ebay_research.models import Search, Results
from ebay_research.forms import FreeSearch, ChooseNewPassword, RepeatSearch
from ebay_research.plot_maker import (
    create_us_county_map,
    make_price_by_type,
    make_seller_bar,
    prep_tab_data,
    make_sunburst,
    make_listing_pie_chart,
)

# TODO: add account page where users can change password, see past searches
# TODO: fix basic search table to show ordered by most watched items
# TODO: (make nicer) fix form error formatting on top of page on basic_search page
# TODO: do something with the feedback score, feedbackRatingStar
# TODO: add search result information
# TODO: add error pages
# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Create figure or data for Category ID info
# TODO: Create ability to hide/show different plots in the results, make look more like a dashboard
# TODO: Provide credit to https://www.flaticon.com/ for icons

main = Blueprint("main", __name__)


@main.route('/', methods=["GET"])
def home():
    return render_template('home.html')


@main.route('/account/<user_id>', methods=['GET', 'POST'])
@login_required
def account(user_id):
    search_form = RepeatSearch()
    password_form = ChooseNewPassword()
    if search_form.validate_on_submit() and search_form.search_id.data:
        pass
    elif password_form.validate_on_submit() and password_form.password.data:
        # make sure to check password validity
        pass
    searches = db.session.query(Search, Results).join(Results).filter(Search.user_id == current_user.id)\
        .order_by(Search.time_searched.desc()).limit(5).all()
    return render_template('account.html', user_id=user_id, searches=searches, search_Form=search_form,
                           password_form=password_form)


@main.route("/basic_search", methods=["GET", "POST"])
@login_required
def basic_search():
    form = FreeSearch()
    if form.validate_on_submit():
        form_data = ingest_free_search_form(form)
        search = EasyEbayData(api_id=current_app.config["EBAY_API"], **form_data)
        search_record = Search(user_id=current_user.id, **form_data)
        df = search.get_data(pages_wanted=1)
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
        db.session.add(search_record)
        db.session.commit()
        current_app.redis.set(search_record.id, df.to_msgpack(compress="zlib"))
        current_app.redis.expire(search_record.id, 600)
        session['search_id'] = search_record.id
        stats = summary_stats(df,
                              search.largest_category,
                              search.largest_sub_category,
                              search.total_entries)
        results = Results(search_id=search_record.id, pages_wanted=1, **stats)
        db.session.add(results)
        db.session.commit()
        tab_data = prep_tab_data(df)
        df_seller = make_seller_bar(df)
        df_map = create_us_county_map(df)
        df_type = make_price_by_type(df)
        df_pie = make_listing_pie_chart(df["listingType"])
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
            df_seller=df_seller,
            make_sunburst=sunburst_plot,
            stats=stats,
            page_url=search.search_url
        )
    return render_template("basic_search.html", form=form)


@main.route("/get_csv", methods=["GET"])
def get_csv():
    if current_app.redis.exists(session['search_id']):
        df = pd.read_msgpack(current_app.redis.get(session['search_id']))
        search_record = Search.query.get(session['search_id'])
        search_record.downloaded = True
        db.session.commit()
        return Response(
            df.to_csv(index=False),
            content_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=ebay_research.csv"},
        )
    else:
        # TODO: file will be saved on s3 and can then be read in from there
        flash('Your session has timed out and the data is no longer saved! Please search again!', 'warning')
        return redirect(url_for('main.basic_search'))
