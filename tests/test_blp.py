import os
import copy
import urllib.parse
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

    # Delete the BLP FS
    main.purge_filesystem()


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


def put(client, url, data, access_token=None):
    rv = client.put(url, json=data, headers=generate_request_headers(access_token))
    return rv.get_json(), rv.status_code


def patch(client, url, data, access_token=None):
    rv = client.patch(url, json=data, headers=generate_request_headers(access_token))
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
    assert s == 401

    # Delete the file by the right user - now it should succeed
    r, s = delete(client, '/files', {'filename': filename}, access_token=user1['id'])
    assert s == 200

    # Verify that the file was actually deleted from the FS
    assert os.path.exists(os.path.join('fs', filename)) == False


def test_read_write_files(client):
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
    assert s == 200

    # Write to the file
    str = "This is the first line,\nand this is the second one."
    r, s = put(client, '/files', {'filename': filename, 'content': str}, access_token=user1['id'])
    assert s == 200

    # Read the file
    r, s = get(client, '/files/{}'.format(urllib.parse.quote(filename)), access_token=user1['id'])
    assert s == 200
    assert r['content'] == str

    # Write to the file again and verify that the new text overriden the previous one
    str2 = "Writing again."
    r, s = put(client, '/files', {'filename': filename, 'content': str2}, access_token=user1['id'])
    assert s == 200
    r, s = get(client, '/files/{}'.format(urllib.parse.quote(filename)), access_token=user1['id'])
    assert r['content'] == str2

    # Append to the file
    str3 = "\nAppending some text."
    r, s = patch(client, '/files', {'filename': filename, 'content': str3}, access_token=user1['id'])
    assert s == 200

    # Verify that the new text was appended to the end of the file and not overridden it
    r, s = get(client, '/files/{}'.format(urllib.parse.quote(filename)), access_token=user1['id'])
    assert r['content'] == (str2 + str3)


def create_blp_users(client):
    junior = {
        'email': 'junior@gmail.com',
        'password': 'Qwer1234!',
        'name': 'Junior',
        'level': BlpLevel.UNCLASSIFIED.name
    }
    mid1 = {
        'email': 'mid1@gmail.com',
        'password': 'Qwer53467%',
        'name': 'Mid1',
        'level': BlpLevel.SECRET.name
    }
    mid2 = {
        'email': 'mid2@gmail.com',
        'password': 'Fasg53467&',
        'name': 'Mid2',
        'level': BlpLevel.SECRET.name
    }
    senior = {
        'email': 'senior@gmail.com',
        'password': 'Qwer578567@',
        'name': 'Senior',
        'level': BlpLevel.TOP_SECRET.name
    }

    # Create users with different levels
    r = create_user(client, junior)
    junior['id'] = r['id']
    r = create_user(client, mid1)
    mid1['id'] = r['id']
    r = create_user(client, mid2)
    mid2['id'] = r['id']
    r = create_user(client, senior)
    senior['id'] = r['id']

    return junior, mid1, mid2, senior


def create_file_and_write(client, user_id, filename, content):
    r, s = post(client, '/files', {'filename': filename}, access_token=user_id)
    assert s == 200
    r, s = put(client, '/files', {'filename': filename, 'content': content}, access_token=user_id)
    assert s == 200


def read_file(client, user_id, filename):
    return get(client, '/files/{}'.format(urllib.parse.quote(filename)), access_token=user_id)


def append_file(client, user_id, filename, content):
    return patch(client, '/files', {'filename': filename, 'content': content}, access_token=user_id)


def test_blp_no_read_up(client):
    # Create users with different BLP clearance levels
    junior, mid1, mid2, senior = create_blp_users(client)

    # Each user creates a file and writes some text to it
    create_file_and_write(client, junior['id'], 'unclassified.txt', "Nothing interesting")
    create_file_and_write(client, mid1['id'], 'secret1.txt', "Something very secret 1")
    create_file_and_write(client, mid2['id'], 'secret2.txt', "Something very secret 2")
    create_file_and_write(client, senior['id'], 'topsecret.txt', "Something very very secret")

    # Verify that mid1 can read the file of mid2 and vice versa
    r, s = read_file(client, mid1['id'], 'secret2.txt')
    assert s == 200
    r, s = read_file(client, mid2['id'], 'secret1.txt')
    assert s == 200

    # Verify that junior can read his own file
    r, s = read_file(client, junior['id'], 'unclassified.txt')
    assert s == 200

    # Verify that senior can read everyone elses files
    r, s = read_file(client, senior['id'], 'topsecret.txt')
    assert s == 200
    r, s = read_file(client, senior['id'], 'secret1.txt')
    assert s == 200
    r, s = read_file(client, senior['id'], 'secret2.txt')
    assert s == 200
    r, s = read_file(client, senior['id'], 'unclassified.txt')
    assert s == 200

    # Verify that junior can't read files above his level
    r, s = read_file(client, junior['id'], 'secret1.txt')
    assert s == 401
    assert r['api_result_code'] == ApiErorrCode.UNAUTHORIZED.name


def test_blp_no_write_down(client):
    # Create users with different BLP clearance levels
    junior, mid1, mid2, senior = create_blp_users(client)

    # Each user creates a file and writes some text to it
    create_file_and_write(client, junior['id'], 'unclassified.txt', "Nothing interesting")
    create_file_and_write(client, mid1['id'], 'secret1.txt', "Something very secret 1")
    create_file_and_write(client, mid2['id'], 'secret2.txt', "Something very secret 2")
    create_file_and_write(client, senior['id'], 'topsecret.txt', "Something very very secret")

    # Verify that mid1 can write to the file of mid2 and vice versa
    text_to_append = "\nappending write down test text."
    r, s = append_file(client, mid1['id'], 'secret2.txt', text_to_append)
    assert s == 200
    r, s = append_file(client, mid2['id'], 'secret1.txt', text_to_append)
    assert s == 200

    # Verify that junior can write to his own file
    r, s = append_file(client, junior['id'], 'unclassified.txt', text_to_append)
    assert s == 200

    # Verify that junior can write to everyone elses files
    r, s = append_file(client, junior['id'], 'topsecret.txt', text_to_append)
    assert s == 200
    r, s = append_file(client, junior['id'], 'secret1.txt', text_to_append)
    assert s == 200
    r, s = append_file(client, junior['id'], 'secret2.txt', text_to_append)
    assert s == 200
    r, s = append_file(client, junior['id'], 'unclassified.txt', text_to_append)
    assert s == 200

    # Verify that senior can't read files below his level
    r, s = append_file(client, senior['id'], 'secret1.txt', text_to_append)
    assert s == 401
    assert r['api_result_code'] == ApiErorrCode.UNAUTHORIZED.name
