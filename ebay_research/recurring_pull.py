from ebay_research import db, create_app
from ebay_research.data_analysis import EasyEbayData
from ebay_research.models import Recurring, Search, Results, RecurringIds
from ebay_research.support_functions import summary_stats
from ebay_research.aws_functions import write_file_to_s3
from datetime import datetime
from ebay_research.auth.email import send_comment
from sqlalchemy import and_
import os

# TODO: change the account page table to ensure that the select button is visible on left side


SETTINGS = os.environ.get('APP_SETTINGS')
EBAY_API = os.environ.get('EBAY_API')

DAY_COMBOS = {0: (0,), 1: (1, 4), 2: (2, 5, 6), 3: (3, 0),
              4: (1, 4), 5: (2, 5), 6: (3, 6)}


def convert_table_to_search(recurring_objects):
    final = []
    for obj in recurring_objects:
        data = dict(search=dict())
        data['search_id'] = obj.Recurring.search_id
        data['recur_id'] = obj.Recurring.id
        data['user_id'] = obj.Recurring.user_id
        data['pages_wanted'] = obj.Search.pages_wanted
        data['search']['category_id'] = obj.Search.category_id
        data['search']['keywords'] = obj.Search.keywords
        data['search']['excluded_words'] = obj.Search.excluded_words
        data['search']['min_price'] = obj.Search.min_price
        data['search']['max_price'] = obj.Search.max_price
        data['search']['sort_order'] = obj.Search.sort_order
        data['search']['listing_type'] = obj.Search.listing_type
        data['search']['item_condition'] = obj.Search.item_condition
        final.append(data)
    return final


def get_searches_to_replicate():
    day = datetime.utcnow().weekday()
    recurring_ids = db.session.query(Recurring, Search).filter(
        and_(Recurring.day_of_week in DAY_COMBOS[day], Recurring.active == True)).join(Search).all()
    if recurring_ids:
        return convert_table_to_search(recurring_ids), True
    return [], False


def write_results_to_db(stats: dict, recurring_id: int):
    result = Results(**stats)
    db.session.add(result)
    db.session.commit()
    recurring = RecurringIds(recurring_id=recurring_id, result_id=result.id)
    db.session.add(recurring)
    db.session.commit()
    print(f'Successfully wrote {recurring_id} to database')
    return recurring.id


def execute_search(search: dict):
    ebay = EasyEbayData(api_id=EBAY_API, **search['search'])
    try:
        df = ebay.full_data_pull(pages_wanted=search['pages_wanted'], include_meta_data=False)
    except RuntimeError:
        message = f"Failed on recur_id {search['recur_id']} and search_id {search['search_id']}"
        return message, False
    stats = summary_stats(df, total_items_available=ebay.total_entries)
    stats['search_id'], stats['user_id'] = search['search_id'], search['user_id']
    re_id = write_results_to_db(stats, search['recur_id'])
    filename = str(search['user_id']) + '_' + str(search['search_id']) + '_' + str(re_id) + '.csv'
    write_file_to_s3(filename, df)
    return 'success', True


def run_recurring_pulls():
    cron_app = create_app()
    message = 'There were no recurring searches executed today.'
    with cron_app.app_context():
        searches, success = get_searches_to_replicate()
        if success:
            failed_pulls = []
            for item in searches:
                fail_message, success = execute_search(item)
                if not success:
                    failed_pulls.append(fail_message)
            message = f"Ran {len(searches)} recurring searches." + '\n'.join(failed_pulls)
        send_comment('Admin', 'Nightly Recurring Searches on Genius Bidding', message)
        print('Finished nightly pull')


if __name__ == '__main__':
    run_recurring_pulls()
