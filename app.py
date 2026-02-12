import logging
import os
import secrets
import time
from threading import Lock
from uuid import uuid4

from flask import Flask, g, jsonify, request
from flask_smorest import Api

from flask_migrate import Migrate
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

from models import StoreModel
from blocklist import BLOCKLIST
from db import db

from dotenv import load_dotenv
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask.signals import got_request_exception
from sqlalchemy import text

from logging_setup import setup_logging

load_dotenv()  

db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

secret_key = os.getenv("SECRET_KEY")



def create_app(db_url=None):
    setup_logging()
    app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = (
    #     f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    # )

    app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.config["JWT_SECRET_KEY"] = str(secrets.SystemRandom().getrandbits(128))
    tables_init_lock = Lock()
    app.extensions["tables_initialized"] = False

    @app.before_request
    def set_request_context():
        g.request_id = request.headers.get("X-Request-ID") or str(uuid4())
        g.request_start = time.perf_counter()

    @app.before_request
    def create_tables_once():
        if request.endpoint in {"healthz", "readyz"}:
            return
        if request.url_rule is None:
            return
        if app.extensions.get("tables_initialized"):
            return

        with tables_init_lock:
            if app.extensions.get("tables_initialized"):
                return
            db.create_all()
            app.extensions["tables_initialized"] = True

    @app.after_request
    def log_request(response):
        duration_ms = None
        if hasattr(g, "request_start"):
            duration_ms = round((time.perf_counter() - g.request_start) * 1000, 2)

        try:
            user_id = get_jwt_identity()
        except Exception:
            user_id = None

        logging.getLogger("app.request").info(
            "HTTP request completed",
            extra={
                "event": "http_request",
                "request_id": getattr(g, "request_id", None),
                "method": request.method,
                "route": request.url_rule.rule if request.url_rule else None,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.remote_addr,
                "user_id": user_id,
            },
        )

        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
        return response

    def log_exception(sender, exception, **extra):
        try:
            user_id = get_jwt_identity()
        except Exception:
            user_id = None

        logging.getLogger("app.request").error(
            "Unhandled exception during request",
            exc_info=True,
            extra={
                "event": "http_exception",
                "request_id": getattr(g, "request_id", None),
                "method": request.method if request else None,
                "route": request.url_rule.rule if request and request.url_rule else None,
                "path": request.path if request else None,
                "remote_addr": request.remote_addr if request else None,
                "user_id": user_id,
            },
        )

    got_request_exception.connect(log_exception, app, weak=False)

    @app.get("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    @app.get("/readyz")
    def readyz():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ready"}), 200
        except Exception:
            db.session.rollback()
            return jsonify({"status": "not_ready"}), 503

    def create_defaults():
        pass

    api = Api(app)
    migrate = Migrate(app, db)

    jwt = JWTManager(app)
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message" : "The token has expired.", "error": "token_expired"}),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_loader(error):
        return (
            jsonify({"message" : "Signature verification failed.", "error": "invalid_token"}),
            401,
        )
    
    @jwt.unauthorized_loader
    def unauthorized_loader(error):
        return (
            jsonify({"message" : "Request doesn't contain an access token", "error": "authorization_required"}),
            401,
        )

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({"message" : "Token has been revoked.", "error": "token_revoked"}),
            401,
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401
        )

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app
