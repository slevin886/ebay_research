from flask import Blueprint, render_template, url_for, session, request, flash
from ebay_research.data_analysis import EasyEbayData
from ebay_research.forms import FreeSearch
from ebay_research.plot_maker import create_us_county_map, make_price_by_type, prep_tab_data
import pandas as pd
import os

# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Capture occurrence of no results for that search


APP_ID = os.environ.get('APP_ID')
main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def home():
    form = FreeSearch()
    if form.validate_on_submit():
        keywords = form.keywords_include.data.strip()
        excluded_words = form.keywords_exclude.data.strip()
        min_price = form.minimum_price.data
        max_price = form.maximum_price.data
        sort_order = request.form.get("item_sort")
        usa_check = request.form.get("usa_check")
        listing_type = request.form.get("listing_type")
        search = EasyEbayData(api_id=APP_ID, keywords=keywords, excluded_words=excluded_words, sort_order=sort_order,
                              usa_only=usa_check, wanted_pages=1, min_price=min_price, max_price=max_price,
                              listing_type=listing_type)
        df = search.get_data()
        # CATCH CONNECTION ERROR AND NO DATA WHICH RETURN AS STR
        if isinstance(df, str):
            if df == "connection_error":
                flash("Uh oh! There seems to be a problem connecting to the API, try again later!")
            else:
                flash("There were no results for those search parameters, try a different search.")
            return render_template('home.html', form=form)
        tab_data = prep_tab_data(df)
        df_map = create_us_county_map(df)
        df_type = make_price_by_type(df)
        return render_template('home.html', form=form,
                               map_plot=df_map.to_dict(orient='list'),
                               tab_data=tab_data.to_dict(orient='records'),
                               hist_plot=df['currentPrice_value'].tolist(),
                               df_type=df_type,
                               page_url=search.search_url, total_entries=search.total_entries)
    return render_template('home.html', form=form)
