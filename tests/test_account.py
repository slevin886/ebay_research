"""
Tests the account page
"""
from .conftest import login


def test_account_page(test_client, init_database):
    login(test_client, 'auth@test.com', 'test123')
    response = test_client.get('/account')
    assert b'roman coin' in response.data  # correct search data
    assert b'total searches</span> 1' in response.data # correct search count
