from ebay_research.searching import searching
from flask import (render_template, request, flash, jsonify,
                   current_app, Response, redirect, url_for, session)
from flask_login import current_user, login_required
import pandas as pd
from ebay_research import db
from ebay_research.aws_functions import write_file_to_s3, read_file_from_s3
from ebay_research.data_analysis import EasyEbayData
from ebay_research.support_functions import ingest_free_search_form, summary_stats
from ebay_research.models import Search, Results
from ebay_research.forms import FreeSearch
from ebay_research.plot_maker import (
    create_us_county_map,
    make_price_by_type,
    make_seller_bar,
    prep_tab_data,
    make_sunburst,
    make_box_plot,
    make_listing_pie_chart,
    make_auction_length,
)


@searching.route("/search", methods=['GET'])
@login_required
def search():
    form = FreeSearch()
    return render_template("search.html", form=form)


@searching.route("/get_data", methods=['POST'])
@login_required
def get_data():
    form = FreeSearch(data=request.get_json())
    if form.validate():
        search_parameters = ingest_free_search_form(form)
        easy_ebay = EasyEbayData(api_id=current_app.config["EBAY_API"], **search_parameters)
        page_number = int(request.form.get('pageNumber'))
        first_pull = True if request.form.get('first_pull') == 'true' else False
        last_pull = True if request.form.get('last_pull') == 'true' else False
        if first_pull:
            pages_wanted = int(request.form.get('max_pages'))
            search_record = Search(user_id=current_user.id, pages_wanted=pages_wanted, **search_parameters)
            existing_records = None
        else:
            search_record = Search.query.filter_by(id=session['search_id']).first()
            existing_records = pd.read_msgpack(current_app.redis.get(search_record.id))

        base_data = easy_ebay.single_page_query(page_number=page_number, include_meta_data=first_pull)

        if isinstance(base_data, str):
            if first_pull:
                search_record.is_successful = False
                db.session.add(search_record)
                db.session.commit()
            if base_data == "connection_error":
                message = "Uh oh! There seems to be a problem connecting to ebay's API, please try again later!"
            else:
                message = "There were no results for those search parameters, please try a different search."
            return Response(response=message, status=400)

        df = pd.DataFrame(base_data)

        if first_pull:
            db.session.add(search_record)
            db.session.commit()
            session['search_id'] = search_record.id
            session['total_entries'] = easy_ebay.total_entries
        else:
            df = pd.concat([existing_records, df], axis=0, sort=False)

        current_app.redis.set(search_record.id, df.to_msgpack(compress="zlib"), ex=60)

        stats = summary_stats(df,
                              easy_ebay.largest_category,
                              easy_ebay.largest_sub_category,
                              easy_ebay.total_entries)

        if last_pull:
            if not first_pull:
                stats['largest_cat_name'] = session.get('largest_cat_name', None)
                stats['largest_cat_count'] = session.get('largest_cat_count', None)
                stats['largest_sub_name'] = session.get('largest_sub_name', None)
                stats['largest_sub_count'] = session.get('largest_sub_count', None)
                stats['total_entries'] = session.get('total_entries', None)
            results = Results(search_id=search_record.id, user_id=current_user.id, **stats)
            db.session.add(results)
            db.session.commit()
            s3_filename = str(current_user.id) + '_' + str(search_record.id) + '.csv'
            write_file_to_s3(s3_filename, df)

        tab_data = prep_tab_data(df)
        df_seller = make_seller_bar(df)
        map_plot = create_us_county_map(df[['postalCode', 'itemId']].copy())
        df_type = make_price_by_type(df[['listingType', 'currentPrice_value']])
        df_pie = make_listing_pie_chart(df["listingType"])
        df_length = make_auction_length(df[['endTime', 'startTime']].copy())
        df_box = make_box_plot(df[['listingType', 'currentPrice_value']].copy())
        if easy_ebay.item_aspects is None:
            sunburst_plot = None
        else:
            sunburst_plot = make_sunburst(easy_ebay.item_aspects)
        return jsonify(map_plot=map_plot,
                       tab_data=tab_data,
                       hist_plot=df["currentPrice_value"].tolist(),
                       df_pie=df_pie,
                       df_type=df_type,
                       df_seller=df_seller,
                       df_length=df_length,
                       df_box=df_box,
                       sunburst_plot=sunburst_plot,
                       stats=stats,
                       search_url=easy_ebay.search_url,
                       search_id=search_record.id)
    return Response(response='Whoops! Please ensure you entered text for keywords and put only numeric values '
                             'in the price entries...', status=400)


@searching.route("/get_csv", methods=["GET"])
@login_required
def get_csv():
    if current_app.redis.exists(session['search_id']):
        df = pd.read_msgpack(current_app.redis.get(session['search_id']))
    else:
        filename = str(current_user.id) + '_' + str(session['search_id']) + '.csv'
        df = read_file_from_s3(filename)

    if not isinstance(df, pd.DataFrame):
        flash('Whoops! We were unable to find any data for that search...', 'warning')
        return redirect(url_for('searching.search'))

    search_record = Search.query.get(session['search_id'])
    search_record.downloaded = True
    db.session.commit()
    return Response(
        df.to_csv(index=False),
        content_type="text/csv",
        headers={"Content-Disposition": "attachment;filename=ebay_research.csv"},
    )
