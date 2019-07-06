import enum
from flask import jsonify, make_response


class ApiErorrCode(enum.Enum):
    UNKNOWN_ERROR = 1
    USER_EXISTS = 2
    UNAUTHORIZED = 3


def api_error(http_code=400, api_result_code=None, error_message=None):
    ret = {
        'api_result_code': api_result_code.name if api_result_code else ApiErorrCode.UNKNOWN_ERROR.name,
        'message': error_message
    }

    return make_response(jsonify(ret), http_code)


def api_ok():
    return make_response(jsonify({}), 200)