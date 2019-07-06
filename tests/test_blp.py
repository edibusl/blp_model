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


def generate_request_headers(access_token=None):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    if access_token:
        headers['Authorization'] = access_token

    return headers


def get(client, url, access_token=None):
    rv = client.get(url, headers=generate_request_headers(access_token))
    return rv.get_json(), rv.status_code


def post(client, url, data, access_token=None):
    rv = client.post(url, json=data, headers=generate_request_headers(access_token))
    return rv.get_json(), rv.status_code


def delete(client, url, access_token=None):
    rv = client.delete(url, headers=generate_request_headers(access_token))
    return rv.get_json(), rv.status_code


def create_user():
    data = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi'
    }
    r, s = post(client, '/users', data, access_token='ADMIN')
    assert s == 200

    return r


####################################3


def test_create_user(client):
    # Create some user
    data = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi'
    }
    r, s = post(client, '/users', data, access_token='ADMIN')
    assert s == 200

    # Create an existing user with the same email - should fail
    r, s = post(client, '/users', data, access_token='ADMIN')
    assert s == 400
    assert r['api_result_code'] == ApiErorrCode.USER_EXISTS.name


def test_delete_user(client):
    # Create some user
    data = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi'
    }
    r, s = post(client, '/users', data, access_token='ADMIN')
    user_id = r['id']

    # Delete this user
    r, s = delete(client, '/users/{}'.format(user_id), access_token='ADMIN')
    assert s == 200

    # Delete a non existing user
    r, s = delete(client, '/users/{}'.format(user_id), access_token='ADMIN')
    assert s == 400


def test_login(client):
    # Create some user
    user = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi'
    }
    r, s = post(client, '/users', user, access_token='ADMIN')
    assert s == 200
    user_id = r['id']

    # Try to login with this user
    r, s = post(client, '/login', {'email': user['email'], 'password': user['password']})
    assert s == 200
    assert r['id'] == user_id

    # Try to login with wrong password
    r, s = post(client, '/login', {'email': user['email'], 'password': 'SOME WRONG PASSWORD'})
    assert s == 401
    assert r['api_result_code'] == ApiErorrCode.UNAUTHORIZED.name