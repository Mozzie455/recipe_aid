from flask_mail import Message
from flask_mail import Mail
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
import validators
from src.models import db
from .models import User
from .constant.http_status_code import HTTP_409_CONFLICT
from .constant.http_status_code import HTTP_201_CREATED
from .constant.http_status_code import HTTP_200_OK
from .constant.http_status_code import HTTP_400_BAD_REQUEST
from .constant.http_status_code import HTTP_401_UNAUTHORIZED


mail = Mail()

auth = Blueprint('auth', __name__, url_prefix="/api/v1/auth")


@auth.route('/register', methods=['POST'])
def register():
    email = request.json['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(
            {'message': 'That email already exists.'}), HTTP_409_CONFLICT
    else:
        username = request.json['username']
        password = request.json['password']

        if len(password) < 6:
            return jsonify(
                {'error': "Password is too short"}), HTTP_400_BAD_REQUEST

        if len(username) < 3:
            return jsonify(
                {'error': "User is too short"}), HTTP_400_BAD_REQUEST

        if not username.isalnum() or " " in username:
            return jsonify(
                {'error': "Username should be alphanumeric, also no spaces"}
                ), HTTP_400_BAD_REQUEST

        if not validators.email(email):
            return jsonify(
                {'error': "Email is not valid"}), HTTP_400_BAD_REQUEST
        pwd_hash = generate_password_hash(password)
        user = User(username=username,
                    email=email,
                    password=pwd_hash)
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': "User created",
            'user': {
                "username": username,
                "email": email
            }
        }), HTTP_201_CREATED


@ auth.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    password = request.json['password']

    user = User.query.filter_by(email=email).first()
    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.user_id)
            access = create_access_token(identity=user.user_id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user.username,
                    'email': user.email
                }

            }), HTTP_200_OK
    else:
        return jsonify(
            {'error': "Bad email or password"}), HTTP_401_UNAUTHORIZED


@ auth.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("your recipe aid API password is " + user.password,
                      sender="admin@recipe_aid-api.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(
            {"message": "Password sent to " + email}), HTTP_200_OK
    else:
        return jsonify(
            {"message": "That email doesn't exist"}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK
