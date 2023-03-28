import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from .constant.http_status_code import HTTP_404_NOT_FOUND
from .constant.http_status_code import HTTP_500_INTERNAL_SERVER_ERROR

# Initialize SQLAlchemy
db = SQLAlchemy()


def create_app():
    # create and configure the app
    app = Flask(__name__)

    # set configs
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[
        'SQLALCHEMY_DATABASE_URI']
    app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
    app.config['MAIL_PORT'] = os.environ['MAIL_PORT']
    app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
    app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False

    db.init_app(app)
    JWTManager(app)
    Mail(app)

    from src.views import main
    from src.auth import auth
    app.register_blueprint(auth)
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404_error(_error):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500_error(_error):
        return jsonify(
            {'error': 'Something went wrong, we are working on it'}
        ), HTTP_500_INTERNAL_SERVER_ERROR

    return app
