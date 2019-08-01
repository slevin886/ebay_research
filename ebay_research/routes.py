from flask import Blueprint, render_template, url_for, session, request, flash, current_app, Response
import os
import pandas as pd
from ebay_research.data_analysis import EasyEbayData
from ebay_research.forms import FreeSearch
from ebay_research.plot_maker import (create_us_county_map, make_price_by_type, prep_tab_data, make_sunburst,
                                      summary_stats)

# TODO: Eventually I will set the redis key to a specific user
# TODO: Implement additional item filters
# TODO: Write test functions
# TODO: Create figure or data for Category ID info & get sub category info for biggest category
# TODO: Create ability to hide/show different plots in the results
# TODO: Provide credit to https://www.flaticon.com/ for icons

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
        listing_type = request.form.get("listing_type")
        condition = request.form.get("condition")
        search = EasyEbayData(api_id=current_app.config['EBAY_API'], keywords=keywords, excluded_words=excluded_words,
                              sort_order=sort_order,
                              wanted_pages=1, min_price=min_price, max_price=max_price, listing_type=listing_type,
                              item_condition=condition)
        df = search.get_data()
        current_app.redis.set('change_me', df.to_msgpack(compress='zlib'))
        # CATCH CONNECTION ERROR AND NO RESULTS- WHICH RETURN AS STRINGS
        if isinstance(df, str):
            if df == "connection_error":
                flash("Uh oh! There seems to be a problem connecting to the API, please try again later!", 'danger')
            else:
                flash("There were no results for those search parameters, please try a different search.", 'danger')
            return render_template('home.html', form=form)
        tab_data = prep_tab_data(df)
        df_map = create_us_county_map(df)
        df_type = make_price_by_type(df)
        stats = summary_stats(df)
        if search.item_aspects is None:
            sunburst_plot = None
        else:
            sunburst_plot = make_sunburst(search.item_aspects)
        return render_template('home.html', form=form,
                               map_plot=df_map.to_dict(orient='list'),
                               tab_data=tab_data.to_dict(orient='records'),
                               hist_plot=df['currentPrice_value'].tolist(),
                               df_type=df_type, make_sunburst=sunburst_plot, stats=stats,
                               page_url=search.search_url, total_entries=search.total_entries)
    return render_template('home.html', form=form)


@main.route('/get_csv', methods=['GET'])
def get_csv():
    df = pd.read_msgpack(current_app.redis.get('change_me'))
    return Response(df.to_csv(index=False), content_type="text/csv",
                    headers={"Content-Disposition": "attachment;filename=ebay_research.csv"})
