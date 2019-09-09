from flask import (Blueprint, render_template, request, flash, current_app, Response)
from flask_login import current_user, login_required
import pandas as pd
from ebay_research import db
from ebay_research.data_analysis import EasyEbayData
from ebay_research.models import  Search
from ebay_research.forms import FreeSearch, EmailForm, LoginForm, SendConfirmation
from ebay_research.plot_maker import (
    create_us_county_map,
    make_price_by_type,
    prep_tab_data,
    make_sunburst,
    summary_stats,
    make_listing_pie_chart,
)

# TODO: check if aspects are appearing again
# TODO: set up email confirmation
# TODO: add error pages
# TODO: better css classes for see it on ebay & download file
# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Create figure or data for Category ID info
# TODO: Change hover mode to closest, improve text font
# TODO: Create ability to hide/show different plots in the results
# TODO: Provide credit to https://www.flaticon.com/ for icons

main = Blueprint("main", __name__)


@main.route('/', methods=["GET"])
def home():
    return render_template('home.html')


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
        current_app.redis.set(current_user.id, df.to_msgpack(compress="zlib"))
        current_app.redis.expire(current_user.id, 120)
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
    if current_app.redis.exists(current_user.id):
        df = pd.read_msgpack(current_app.redis.get(current_user.id))

        return Response(
            df.to_csv(index=False),
            content_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=ebay_research.csv"},
        )
    else:
        pass
        # TODO: perhaps write these files temporarily to s3 and then delete them/pull them from here
