from flask import (Blueprint, render_template, request, flash, current_app, Response, redirect, url_for)
from flask_login import current_user, login_required
import pandas as pd
from ebay_research import db
from ebay_research.data_analysis import EasyEbayData
from ebay_research.models import Search
from ebay_research.forms import FreeSearch
from ebay_research.plot_maker import (
    create_us_county_map,
    make_price_by_type,
    prep_tab_data,
    make_sunburst,
    summary_stats,
    make_listing_pie_chart,
)

# TODO: add account page where users can change password, see past searches
# TODO: have the number of wanted pages be a part of get data
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


def ingest_free_search_form(form):
    final = dict()
    final['keywords'] = form.keywords_include.data.strip()
    final['excluded_words'] = form.keywords_exclude.data.strip()
    final['min_price'] = form.minimum_price.data
    final['max_price'] = form.maximum_price.data
    final['sort_order'] = request.form.get("item_sort")
    final['listing_type'] = request.form.get("listing_type")
    final['item_condition'] = request.form.get("condition")
    return final


@main.route("/basic_search", methods=["GET", "POST"])
@login_required
def basic_search():
    form = FreeSearch()
    if form.validate_on_submit():
        form_data = ingest_free_search_form(form)
        search = EasyEbayData(api_id=current_app.config["EBAY_API"], wanted_pages=1, **form_data)
        search_record = Search(user_id=current_user.id, **form_data)
        df = search.get_data()
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
        current_app.redis.set(current_user.id, df.to_msgpack(compress="zlib"))
        current_app.redis.expire(current_user.id, 600)
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
    # TODO: change downloaded in Search table
    if current_app.redis.exists(current_user.id):
        df = pd.read_msgpack(current_app.redis.get(current_user.id))

        return Response(
            df.to_csv(index=False),
            content_type="text/csv",
            headers={"Content-Disposition": "attachment;filename=ebay_research.csv"},
        )
    else:
        flash('Your session has timed out and the data is no longer saved! Please search again!', 'warning')
        return redirect(url_for('main.basic_search'))
