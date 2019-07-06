import hashlib, uuid
from functools import wraps
from flask import _app_ctx_stack, request


def pass_to_hash(password, salt=None):
    if not password:
        raise ValueError("Empty password given")

    if not salt:
        salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512((password + salt).encode('ascii')).hexdigest()

    return hashed_password, salt


def requires_auth(admin_only=False):
    """
    # Verifies that the user_id was passed in the Authorization header
    """
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # Get the user_id from the header
            user_id = get_user_id_from_header()
            if not user_id:
                raise Exception("Unauthorized")

            # If this is an ADMIN endpoint but the user is not ADMIN, raise an exception.
            # We assume an ADMIN user if the request has "ADMIN" in the Authorization header instead of the user's id
            if admin_only and user_id != 'ADMIN':
                raise Exception("Unauthorized")

            # Save the user data in the flask app context
            _app_ctx_stack.top.current_user = {'user_id': user_id}

            # User must have ANY of the listed roles
            return func(*args, **kwargs)

        return decorated_view
    return wrapper


def get_user_id_from_header():
    """
    # TODO - Right now we take the user id from header.
    # In a real production app we need to take from the Authorization header the access token of the user (which was generated in an OAuth process)
    """
    auth = request.headers.get("Authorization", None)
    user_id = auth

    return user_id