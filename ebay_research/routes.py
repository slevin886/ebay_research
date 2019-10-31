from flask import (Blueprint, render_template, request, flash, jsonify,
                   current_app, Response, redirect, url_for, session, abort)
from flask_login import current_user, login_required
import pandas as pd
from ebay_research import db
from ebay_research.data_analysis import EasyEbayData
from ebay_research.support_functions import ingest_free_search_form, summary_stats
from ebay_research.models import Search, Results
from ebay_research.forms import FreeSearch, ChooseNewPassword
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
    number_searches = Search.query.filter_by(user_id=current_user.id).count()
    search_results = db.session.query(Search, Results).filter(Search.user_id == current_user.id).join(Results)\
        .order_by(Search.time_searched.desc()).limit(10).all()
    return render_template('account.html', user_id=user_id, search_results=search_results,
                           number_searches=number_searches, password_form=password_form)


@main.route("/search", methods=['GET'])
@login_required
def search():
    form = FreeSearch()
    return render_template("search.html", form=form)


@main.route("/get_data", methods=['POST'])
@login_required
def get_data():
    form = FreeSearch(data=request.get_json())
    if form.validate():
        form_data = ingest_free_search_form(form)
        searching = EasyEbayData(api_id=current_app.config["EBAY_API"], **form_data)
        page_number = int(request.form.get('pageNumber'))
        first_pull = True if request.form.get('first_pull') == 'true' else False
        last_pull = True if request.form.get('last_pull') == 'true' else False
        if first_pull:
            pages_wanted = int(request.form.get('max_pages'))
            search_record = Search(user_id=current_user.id, pages_wanted=pages_wanted, **form_data)
            existing_records = None
        else:
            search_record = Search.query.filter_by(id=session['search_id']).first()
            existing_records = pd.read_msgpack(current_app.redis.get(search_record.id))

        base_data = searching.single_page_query(page_number=page_number, include_meta_data=first_pull)

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

        data = base_data['searchResult']['item']
        df = pd.DataFrame([searching.flatten_dict(i) for i in data])

        if first_pull:
            db.session.add(search_record)
            db.session.commit()
            session['search_id'] = search_record.id
            session['total_entries'] = searching.total_entries
        else:
            df = pd.concat([existing_records, df], axis=0, sort=False)

        current_app.redis.set(search_record.id, df.to_msgpack(compress="zlib"), ex=1200)

        stats = summary_stats(df,
                              searching.largest_category,
                              searching.largest_sub_category,
                              searching.total_entries)

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
        tab_data = prep_tab_data(df)
        df_seller = make_seller_bar(df)
        map_plot = create_us_county_map(df[['postalCode', 'itemId']])
        df_type = make_price_by_type(df[['listingType', 'currentPrice_value']])
        df_pie = make_listing_pie_chart(df["listingType"])
        df_length = make_auction_length(df[['endTime', 'startTime']])
        df_box = make_box_plot(df[['listingType', 'currentPrice_value']].copy())
        if searching.item_aspects is None:
            sunburst_plot = None
        else:
            sunburst_plot = make_sunburst(searching.item_aspects)
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
                       search_url=searching.search_url,
                       search_id=search_record.id)
    return Response(response='please ensure you are putting sane values into the form...', status=400)


@main.route("/get_csv", methods=["GET"])
@login_required
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
        return redirect(url_for('main.search'))
