from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask import jsonify
from functools import wraps
import re


def isInt(num):
    pattern = "^[1-9][0-9]*"
    return re.fullmatch(pattern, str(num))


def jwt_buyer_only(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        claims = get_jwt()
        if "customer" in claims['roles'] and identity != "admin@admin.com":
            # claims = get_jwt()
            # if claims['exp'] < int(time()):
            #     return jsonify(msg="JWT expired."), 401
            response = function(*args, **kwargs)
            return response
        else:
            return jsonify(msg="Missing Authorization Header"), 401
    return wrapper


