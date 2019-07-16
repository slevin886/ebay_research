from flask import Blueprint, render_template, url_for, session, request, flash
from ebay_research.data_analysis import EasyEbayData
from ebay_research.forms import FreeSearch
from ebay_research.plot_maker import create_us_county_map
import pandas as pd
import os

# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Figure out a way to drop nulls from dataframe


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
        search = EasyEbayData(api_id=APP_ID, keywords=keywords, excluded_words=excluded_words, sort_order=sort_order,
                              usa_only=usa_check, wanted_pages=1, min_price=min_price, max_price=max_price)
        df = search.get_data()
        # CATCH CONNECTION ERROR AND NO DATA WHICH RETURN AS STR
        if isinstance(df, str):
            if df == "connection_error":
                flash("Uh oh! There seems to be a problem connecting to the API, try again later!")
            else:
                flash("There were no results for those search parameters, try a different search.")
            return render_template('home.html', form=form)
        tab_data = df[['title', 'location', 'sellingStatus_bidCount',
                       'sellingStatus_timeLeft', 'currentPrice_value']].copy()
        return render_template('home.html', form=form, map_plot=create_us_county_map(df),
                               tab_data=tab_data.to_dict(orient='records'))
    return render_template('home.html', form=form)
