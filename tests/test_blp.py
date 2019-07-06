import os
import pytest
import main
from api_utils import ApiErorrCode

@pytest.fixture
def client():
    # Delete temp sqlite DB if it exists in the dir
    ut_db_filename = 'ut.db'
    if os.path.exists(ut_db_filename):
        os.unlink(ut_db_filename)

    # Create a special DB for this UT
    main.create_db(ut_db_filename)

    # Start flask app and get its test client
    app = main.start_flask()
    app.config['TESTING'] = True
    client = app.test_client()

    # Start the test
    yield client

    # Delete the temp DB file that was created for this UT
    os.unlink(ut_db_filename)


def get(client, url):
    rv = client.get(url)
    return rv.get_json(), rv.status_code


def post(client, url, data):
    rv = client.post(url, json=data)
    return rv.get_json(), rv.status_code


def test_create_user(client):
    # Create some user
    data = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi'
    }
    r, s = post(client, '/users', data)
    assert s == 200

    # Create an existing user with the same email - should fail
    r, s = post(client, '/users', data)
    assert s == 400
    assert r['api_result_code'] == ApiErorrCode.USER_EXISTS.name
