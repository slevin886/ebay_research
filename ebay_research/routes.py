from flask import Blueprint, render_template, url_for, session, request
from ebay_research.data_analysis import EasyEbayData
from ebay_research.forms import FreeSearch
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
        test = search.get_ebay_item_info()
    return render_template('home.html', form=form)
