"""
Test geniusbidding/registration 
"""
from ebay_research import mail


def test_register(test_client, init_database):
    with mail.record_messages() as outbox:
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
            follow_redirects=True
        )
        assert b'Please check your email' in response.data
        assert 'Confirm your' in outbox[0].subject
        assert 'bob@gmail.com' in outbox[0].recipients
        assert response.status_code == 200
