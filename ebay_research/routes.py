from flask import (Blueprint, render_template, request, flash, jsonify,
                   current_app, Response, redirect, url_for, session)
from flask_login import current_user, login_required
import pandas as pd
from ebay_research import db
from ebay_research.data_analysis import EasyEbayData
from ebay_research.support_functions import ingest_free_search_form, summary_stats
from ebay_research.models import Search, Results, User
from ebay_research.forms import FreeSearch, ChooseNewPassword, RepeatSearch
from ebay_research.plot_maker import (
    create_us_county_map,
    make_price_by_type,
    make_seller_bar,
    prep_tab_data,
    make_sunburst,
    make_listing_pie_chart,
)

# TODO: implement repeat search on account page and possibly something do download search result metadata
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
    # TODO: eliminate or implement RepeatSearch
    search_form = RepeatSearch()
    password_form = ChooseNewPassword()
    if search_form.validate_on_submit() and search_form.search_id.data:
        pass
    elif password_form.validate_on_submit():
        password = password_form.old_password.data
        if current_user.validate_password(password):
            new_password = password_form.password.data
            current_user.set_password(new_password)
            db.session.commit()
            flash('You have successfully changed your password!', 'success')
        else:
            flash("Whoops! You entered the wrong password, please try again or reset it from the login page", 'danger')
    searches = db.session.query(Search, Results).join(Results).filter(Search.user_id == current_user.id) \
        .order_by(Search.time_searched.desc()).limit(5).all()
    number_searches = len(User.query.filter_by(id=current_user.id).first().searches)
    return render_template('account.html', user_id=user_id, searches=searches, number_searches=number_searches,
                           search_Form=search_form, password_form=password_form)


@main.route("/basic_search", methods=["GET", "POST"])
@login_required
def basic_search():
    form = FreeSearch()
    if form.validate_on_submit():
        form_data = ingest_free_search_form(form)
        search = EasyEbayData(api_id=current_app.config["EBAY_API"], **form_data)
        search_record = Search(user_id=current_user.id, **form_data)
        df = search.full_data_pull(pages_wanted=1)
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


@main.route("/search", methods=['GET'])
def search():
    form = FreeSearch()
    return render_template("search.html", form=form)


@main.route("/get_data", methods=['POST'])
def get_data():
    form = FreeSearch(data=request.get_json())
    if form.validate():
        form_data = ingest_free_search_form(form)
        searching = EasyEbayData(api_id=current_app.config["EBAY_API"], **form_data)
        page_number = int(request.form.get('pageNumber'))
        include_meta_data = False
        if page_number == 1:
            include_meta_data = True
            search_record = Search(user_id=current_user.id, **form_data)
        else:
            search_record = Search.query.filter_by(id=session['search_id']).first()
            existing_records = pd.read_msgpack(current_app.redis.get(session['search_id']))

        base_data = searching.single_page_query(page_number=page_number, include_meta_data=include_meta_data)
        data = base_data['searchResult']['item']
        df = pd.DataFrame([searching.flatten_dict(i) for i in data])

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
        if page_number == 1:
            db.session.add(search_record)
            db.session.commit()
        else:
            df = pd.concat([existing_records, df], axis=0, sort=False)

        current_app.redis.set(search_record.id, df.to_msgpack(compress="zlib"))
        current_app.redis.expire(search_record.id, 600)
        session['search_id'] = search_record.id
        stats = summary_stats(df,
                              searching.largest_category,
                              searching.largest_sub_category,
                              searching.total_entries)
        print(searching.largest_category)
        # TODO: add logic to only commit results on the last pull
        # results = Results(search_id=search_record.id, pages_wanted=1, **stats)
        # db.session.add(results)
        # db.session.commit()
        tab_data = prep_tab_data(df)
        df_seller = make_seller_bar(df)
        map_plot = create_us_county_map(df)
        df_type = make_price_by_type(df)
        df_pie = make_listing_pie_chart(df["listingType"])
        if searching.item_aspects is None:
            sunburst_plot = None
        else:
            sunburst_plot = make_sunburst(searching.item_aspects)
        return jsonify(map_plot=map_plot,
                       tab_data=tab_data.to_dict(orient="records"),
                       hist_plot=df["currentPrice_value"].tolist(),
                       df_pie=df_pie,
                       df_type=df_type,
                       df_seller=df_seller,
                       sunburst_plot=sunburst_plot,
                       stats=stats,
                       search_id=search_record.id)


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
