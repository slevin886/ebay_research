from ebay_research.models import Recurring, Search, RecurringIds
from ebay_research.trends import recurring
from ebay_research import db
from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import and_
from datetime import datetime
import calendar

# TODO: set pop up on account page that shows how to access recurring results

DAY_RECURRING = {0: (0, 3), 1: (1, 4), 2: (2, 5), 3: (3, 6), 4: (1, 4), 5: (2, 5), 6: (2, 6)}


@recurring.route('/set_recurring_search', methods=['POST'])
@login_required
def set_recurring_search():
    current_recurring = Recurring.query.filter_by(user_id=current_user.id, active=True).all()
    if len(current_recurring) >= 2:
        return jsonify({'message': 'You can only have two recurring searches at a time, you must delete '
                                   'an old one before setting up a new one.',
                        'success': False}), 200
    weekday = datetime.utcnow().weekday()
    search_id = int(request.get_json()['search_id'])
    existing = Recurring.query.filter_by(search_id=search_id).first()
    if existing:
        if existing.active:
            return jsonify({'message': f'That recurring search is already active!', 'success': True}), 200
        else:
            existing.active = True
            db.session.commit()
            return jsonify({'message': f'You have previously tracked this search. It is now active again.',
                            'success': True}), 200
    recur = Recurring(search_id=search_id, user_id=current_user.id,
                      day_of_week=weekday, active=True)
    db.session.add(recur)
    db.session.commit()
    first_search = Search.query.get(search_id)
    first_recur = RecurringIds(recurring_id=recur.id,
                               time_searched=first_search.time_searched,
                               result_id=first_search.search_results[0].id)
    db.session.add(first_recur)
    db.session.commit()
    return jsonify({'message': f'Your recurring search has been set! The search will '
                               f'be run twice weekly on {calendar.day_name[DAY_RECURRING[weekday][0]]}'
                               f' and {calendar.day_name[DAY_RECURRING[weekday][1]]}.',
                    'success': True}), 200


@recurring.route('/stop_recurring_search', methods=['POST'])
@login_required
def stop_recurring_search():
    recur_id = request.get_json()['recur_id']
    recur = Recurring.query.filter_by(id=recur_id).first()
    recur.active = False
    db.session.commit()
    return jsonify({'message': f'Your recurring search has been stopped.',
                    'success': True}), 200


@recurring.route('/trends', methods=['GET'])
@login_required
def trends():
    searches = db.session.query(Recurring, Search).filter(
        and_(Recurring.user_id == current_user.id,
             Recurring.active == True,
             Recurring.search_id == Search.id)
    ).all()
    return render_template('trends.html', searches=searches)


def extract_results(obj):
    # need to maintain obj to get time searched
    result = obj.result_data.__dict__
    for category in ['largest_cat_count', 'user_id', 'largest_cat_name', 'largest_sub_name',
                     'largest_sub_count', 'id', '_sa_instance_state']:
        result.pop(category, None)
    result['date'] = obj.time_searched.date().strftime('%m/%d/%Y')
    return result


@recurring.route('/get_trend_data', methods=['POST'])
@login_required
def get_trend_data():
    """
    Expects a json w/ a key for 'recurring_id'
    """
    recurring_id = int(request.get_json()['recurring_id'])
    results = RecurringIds.query.filter_by(recurring_id=recurring_id).all()
    if results:
        results = [extract_results(i) for i in results]
    return jsonify({'data': results}), 200

