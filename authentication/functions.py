from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask import jsonify
import re
from time import time
from functools import wraps

def checkPass(password):
    digit = False
    lower = False
    upper = False
    password = str(password)
    if len(password) < 8:
        return False
    for k in range(len(password)):
        if password[k].isdigit():
            digit = True
        if password[k].islower():
            lower = True
        if password[k].isupper():
            upper = True
    return digit and lower and upper


def emailFormat(email):
    pattern = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{3}$"
    return re.fullmatch(pattern, email)


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
