import pytest
from ebay_research import create_app, db
from ebay_research.models import User


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
    yield db
    db.session.close()
    db.drop_all()
