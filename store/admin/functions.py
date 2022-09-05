from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask import jsonify
from functools import wraps


def jwt_admin_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        if identity == "admin@admin.com":
            # claims = get_jwt()
            # if claims['exp'] < int(time()):
            #     return jsonify(msg="JWT expired."), 401
            response = function(*args, **kwargs)
            return response
        else:
            return jsonify(msg="Missing Authorization Header"), 401
    return wrapper


