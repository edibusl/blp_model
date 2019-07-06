from flask import Blueprint, request, jsonify
from werkzeug.exceptions import Unauthorized
from api_utils import ApiErorrCode, api_ok, api_error
import db_manager
from orm.user import User
import auth


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
        user = User(name=data['name'], email=data.get('email', None), password=hashed_pass, salt=salt)
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
