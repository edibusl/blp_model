from flask import Blueprint, request, jsonify
from werkzeug.exceptions import Unauthorized
from api_utils import ApiErorrCode, api_ok, api_error
import db_manager
from orm.user import User
from orm.file import File
import auth
import file_manager

bp_endpoints = Blueprint('gw_endpoints', __name__)


@bp_endpoints.route('/users', methods=['POST'])
@auth.requires_auth(admin_only=True)
def users_create():
    data = request.get_json()

    with db_manager.session_scope() as session:
        # Verify that a user with the same email doesn't exist
        users = session.query(User).filter(User.email == data['email']).all()
        if users:
            return api_error(api_result_code=ApiErorrCode.USER_EXISTS, error_message="User {} already exists".format(data['email']))

        # Create the user
        hashed_pass, salt = auth.pass_to_hash(data['password'])
        user = User(name=data['name'], email=data.get('email', None), password=hashed_pass, salt=salt, level=data['level'])
        session.add(user)
        session.commit()

        return jsonify(user.to_dict())


@bp_endpoints.route('/users/<user_id>', methods=['DELETE'])
@auth.requires_auth(admin_only=True)
def users_delete(user_id):
    with db_manager.session_scope() as session:
        user = session.query(User).get(user_id)
        if not user:
            return api_error()
        else:
            session.delete(user)
            session.commit()

            return api_ok()


@bp_endpoints.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    def login_error():
        return api_error(http_code=Unauthorized.code, api_result_code=ApiErorrCode.UNAUTHORIZED, error_message="Bad user or password")

    with db_manager.session_scope() as session:
        # Get user from DB
        user = session.query(User).filter(User.email == data['email']).one_or_none()

        # Verify that user exists
        if not user:
            return login_error()

        # Validate the password
        hashed_password, _ = auth.pass_to_hash(data['password'], user.salt)
        if hashed_password == user.password:
            return jsonify({'id': user.id})
        else:
            return login_error()


@bp_endpoints.route('/files', methods=['POST'])
@auth.requires_auth()
def files_create():
    data = request.get_json()
    user_id = auth.get_current_user_id()

    with db_manager.session_scope() as session:
        # Get user from DB
        user = session.query(User).get(user_id)

        # Verify that user exists
        if not user:
            return api_error(http_code=Unauthorized.code, api_result_code=ApiErorrCode.UNAUTHORIZED)

        # Verify that file doesn't exist yet
        file = session.query(File).filter(File.filename == data['filename']).all()
        if file:
            return api_error(api_result_code=ApiErorrCode.FILE_ALREADY_EXISTS)

        # Create the file in DB with the same level of the owner user
        file = File(filename=data['filename'], level=user.level, owner=user)
        session.add(file)
        session.commit()

        # Create the file on the filesystem
        file_manager.create_file(file.filename)

        return jsonify(file.to_dict())


@bp_endpoints.route('/files', methods=['DELETE'])
@auth.requires_auth()
def files_delete():
    data = request.get_json()
    user_id = auth.get_current_user_id()

    with db_manager.session_scope() as session:
        # Verify that file exists
        file = session.query(File).filter(File.filename == data['filename']).one_or_none()
        if not file:
            return api_error(api_result_code=ApiErorrCode.FILE_NOT_EXISTS)

        # Verify that the
        if file.owner_id != user_id:
            return api_error(api_result_code=ApiErorrCode.UNAUTHORIZED, error_message="The file can be deleted only by its owner")

        # Delete the file entry from DB
        session.delete(file)
        session.commit()

        # Delete the file on the filesystem
        file_manager.delete_file(data['filename'])

        return api_ok()
