from flask import Flask, request, jsonify, Response
from config import Configuration
from models import db, User, UserRole
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, \
    get_jwt, get_jwt_identity, jwt_required
from functions import checkPass, jwt_admin_only, emailFormat


app = Flask(__name__)
app.config.from_object(Configuration)


@app.post('/register')
def register():
    data = request.get_json()
    forename = data.get("forename", "")
    surname = data.get("surname", "")
    email = data.get("email", "")
    password = data.get("password", "")
    isCustomer = data.get("isCustomer", None)

    if len(forename) == 0:
        return jsonify(message="Field forename is missing."), 400
    if len(surname) == 0:
        return jsonify(message="Field surname is missing."), 400
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400
    if isCustomer is None:
        return jsonify(message="Field isCustomer is missing."), 400

    if not emailFormat(email):
        return jsonify(message="Invalid email."), 400

    if not checkPass(password):
        return jsonify(message="Invalid password."), 400

    res = User.query.filter(User.email == email).first()
    if res:
        return jsonify(message="Email already exists."), 400

    new_user = User(forename=forename, surname=surname, email=email, password=password)
    new_role = 2 if isCustomer else 3
    db.session.add(new_user)
    db.session.commit()

    userrole = UserRole(userID=new_user.id, roleID=new_role)
    db.session.add(userrole)
    db.session.commit()

    return Response(status=200)


jwt = JWTManager(app)


@app.post('/login')
def login():
    data = request.get_json()
    email = data.get('email', '')
    password = data.get('password', '')

    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400

    if not emailFormat(email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email, User.password == password).first()
    if not user:
        return jsonify(message="Invalid credentials."), 400

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "password": user.password,
        "roles": [role.name for role in user.roles]
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken=access_token, refreshToken=refresh_token), 200


@app.post('/refresh')
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    claims = get_jwt()
    additional_claims = {
        "forename": claims['forename'],
        "surname": claims['surname'],
        "password": claims['password'],
        "roles": claims['roles']
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)

    return jsonify(accessToken=access_token), 200


@app.post('/delete')
@jwt_admin_only
def delete():
    data = request.get_json()
    email = data.get('email', '')

    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    if not emailFormat(email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()
    if not user:
        return jsonify(message="Unknown user."), 400

    db.session.delete(user)
    db.session.commit()

    return Response(status=200)


if __name__ == "__main__":
    db.init_app(app)
    app.run(debug=True, host='0.0.0.0', port=5002)
