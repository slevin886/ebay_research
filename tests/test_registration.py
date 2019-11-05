"""
Test geniusbidding/registration 
"""
def test_register(test_client, init_database):
    response = test_client.post(
        'register',
        data=dict(
                email='bob@gmail.com',
                confirm_email='bob@gmail.com',
                password='test123',
                confirm_password='test123',
                location='USA',
                state='Massachusetts',
            ),
    )
    assert response.status_code == 302
    assert response.location[-1] == '/'
