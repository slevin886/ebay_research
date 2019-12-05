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
from ebay_research.plot_maker import MakePlots


# TODO: Close the results view on search page on each new click of the button
# TODO: Add what days a search recurs on to account page
# TODO: add ability to set recurring search from search page
# TODO: Make avg. auction length a statistic
# TODO: Combine price distribution plots and add bottom descriptors
# TODO: Add logic to ensure that plot exists before putting into dropdown


@searching.route("/search", methods=['GET'])
@login_required
def search():
    form = FreeSearch()
    return render_template("search.html", form=form)


@searching.route("/get_async_data", methods=['POST'])
@login_required
def get_async_data():
    form = FreeSearch(data=request.get_json())
    if form.validate():
        search_parameters = ingest_free_search_form(form)
        easy_ebay = EasyEbayData(api_id=current_app.config["EBAY_API"], **search_parameters)
        search_record = Search(user_id=current_user.id, **search_parameters)
        result = easy_ebay.single_page_query(page_number=1,
                                             include_meta_data=True,
                                             return_df=False)
        if isinstance(result, str):
            search_record.is_successful = False
            db.session.add(search_record)
            db.session.commit()
            if 'no results' in result:
                message = 'Sorry there are no items for those search parameters'
            else:
                message = 'Whoops! Something went wrong. Please try again later.'
            return jsonify(message=message), 400

        db.session.add(search_record)
        db.session.commit()
        session['search_id'] = search_record.id

        if search_parameters['pages_wanted'] > 1:
            max_pages = min([search_parameters['pages_wanted'], easy_ebay.total_pages])
            more_results = easy_ebay.run_async(pages_wanted=max_pages, max_workers=max_pages,
                                               return_df=False, start_page=2)
            result = result + more_results

        df = pd.DataFrame(result)
        stats = summary_stats(df,
                              easy_ebay.largest_category,
                              easy_ebay.largest_sub_category,
                              easy_ebay.total_entries)

        results = Results(search_id=search_record.id, user_id=current_user.id, **stats)
        db.session.add(results)
        db.session.commit()
        session['file_name'] = str(current_user.id) + '_' + str(search_record.id) + '.csv'
        write_file_to_s3(session['file_name'], df)
        plots = MakePlots(df, easy_ebay.item_aspects)
        plots.run()
        return jsonify(stats=stats, search_url=easy_ebay.search_url, search_id=search_record.id,
                       **plots.results), 200
    return jsonify(message='Whoops! Please ensure you entered text for keywords and put only numeric values '
                           'in the price entries...'), 400


@searching.route("/get_csv", methods=["GET"])
@login_required
def get_csv():
    df = read_file_from_s3(session['file_name'])
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
