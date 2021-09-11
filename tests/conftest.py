import pytest
from ebay_research import create_app, db
from ebay_research.models import User, Search, Results


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(settings='testing')
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()
    authorized_user = User(email='auth@test.com', password='test123', country='USA',
                           state='Texas', permissions=1, confirmed=True, admin=True)
    db.session.add(authorized_user)
    db.session.commit()
    search_history = Search(keywords='roman coin', sort_order='price', is_successful=True,
                            user_id=authorized_user.id)
    db.session.add(search_history)
    db.session.commit()
    result_history = Results(avg_price=20, median_price=25, returned_count=100,
                             top_rated_percent=75, top_seller='big seller', top_seller_count=10,
                             total_entries=1000, total_watch_count=500, avg_shipping_price=2,
                             user_id=authorized_user.id, search_id=search_history.id)
    db.session.add(result_history)
    db.session.commit()
    yield db
    db.session.close()
    db.drop_all()


def login(client, email, password):
    return client.post('/login', data=dict(
        email=email,
        password=password
    ), follow_redirects=True)
