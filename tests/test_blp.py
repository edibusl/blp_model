import os
import copy
import pytest
import main
from api_utils import ApiErorrCode
from orm.level import BlpLevel


@pytest.fixture
def client():
    # Delete temp sqlite DB if it exists in the dir
    ut_db_filename = 'ut.db'
    if os.path.exists(ut_db_filename):
        os.unlink(ut_db_filename)

    # Create a special DB for this UT
    main.create_db(ut_db_filename)

    # Init file manager and start a fresh new filesystem
    main.init_filemanager(True)

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


def delete(client, url, data, access_token=None):
    rv = client.delete(url, json=data, headers=generate_request_headers(access_token))
    return rv.get_json(), rv.status_code


def create_user(client, data):
    r, s = post(client, '/users', data, access_token='ADMIN')
    assert s == 200

    return r


####################################3


def test_create_user(client):
    # Create some user
    data = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi',
        'level': BlpLevel.SECRET.name
    }
    r, s = post(client, '/users', data, access_token='ADMIN')
    assert s == 200
    assert r['level'] == BlpLevel.SECRET.name

    # Create an existing user with the same email - should fail
    r, s = post(client, '/users', data, access_token='ADMIN')
    assert s == 400
    assert r['api_result_code'] == ApiErorrCode.USER_EXISTS.name


def test_delete_user(client):
    # Create some user
    data = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi',
        'level': BlpLevel.SECRET.name
    }
    r, s = post(client, '/users', data, access_token='ADMIN')
    user_id = r['id']

    # Delete this user
    r, s = delete(client, '/users/{}'.format(user_id), None, access_token='ADMIN')
    assert s == 200

    # Delete a non existing user
    r, s = delete(client, '/users/{}'.format(user_id), None, access_token='ADMIN')
    assert s == 400


def test_login(client):
    # Create some user
    user = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi',
        'level': BlpLevel.SECRET.name
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


def test_create_delete_files(client):
    # Create user
    user1 = {
        'email': 'edibusl@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Edi',
        'level': BlpLevel.SECRET.name
    }
    r = create_user(client, user1)
    user1['id'] = r['id']

    # Create the file
    filename = 'edi.txt'
    r, s = post(client, '/files', {'filename': filename}, access_token=user1['id'])

    # Verify the file's blp level is the same as the owner's level
    assert s == 200
    assert r['level'] == user1['level']

    # Verify that the file was actually created on the FS
    assert os.path.exists(os.path.join('fs', filename)) == True

    # Create another user
    user2 = copy.deepcopy(user1)
    user2['email'] = "user2@gmail.com"
    r = create_user(client, user2)
    user2['id'] = r['id']

    # Try to delete the file of user1 by user2
    # Exception should be thrown since the file belongs to user1
    r, s = delete(client, '/files', {'filename': filename}, access_token=user2['id'])
    assert s == 400

    # Delete the file by the right user - now it should succeed
    r, s = delete(client, '/files', {'filename': filename}, access_token=user1['id'])
    assert s == 200

    # Verify that the file was actually deleted from the FS
    assert os.path.exists(os.path.join('fs', filename)) == False
