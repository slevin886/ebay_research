from ebay_research import create_app
from ebay_research.models import User, Search
from ebay_research.auth.email import send_comment
from datetime import datetime, timedelta


TIME_WINDOW = datetime.utcnow() - timedelta(days=1)


def get_new_users():
    message = 'There were no new users in the last 24 hours\n'
    new_users = User.query.filter(User.registered_on > TIME_WINDOW).all()
    if new_users:
        message = ''.join(str(i) for i in new_users) + '\n'
    return message


def get_recent_searches():
    message = 'There have been no recent searches'
    recent_searches = Search.query.filter(Search.time_searched > TIME_WINDOW).limit(20).all()
    if recent_searches:
        queries = [str(i.user_id) + ': ' + i.keywords + '\n' for i in recent_searches]
        message = ''.join(queries)
    return message


def send_recent_queries():
    cron_app = create_app()
    with cron_app.app_context():
        search_message = get_recent_searches()
        user_message = get_new_users()
        send_comment('Admin', 'Recent Activity on Genius Bidding', user_message + search_message)
