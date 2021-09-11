"""
Test that login works
"""


def test_login(test_client, init_database):
    # Fail login, wrong password
    response = test_client.post(
        'login',
        data=dict(
            email='auth@test.com',
            password='wrong_password',
        ),
        follow_redirects=True
    )
    assert b'Whoops! Check that you entered' in response.data
    # Successful login redirects to search page
    response = test_client.post(
        'login',
        data=dict(
            email='auth@test.com',
            password='test123',
        ),
        follow_redirects=True
    )
    assert b'choose your search criteria' in response.data