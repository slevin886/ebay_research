from ebay_research.activity_update import send_recent_queries
from ebay_research.recurring_pull import run_recurring_pulls


if __name__ == '__main__':
    send_recent_queries()
    run_recurring_pulls()
