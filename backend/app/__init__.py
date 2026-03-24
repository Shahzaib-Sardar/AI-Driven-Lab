from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.routes.auth import auth_bp
from app.routes.budgets import budgets_bp
from app.routes.categories import categories_bp
from app.routes.dashboard import dashboard_bp
from app.routes.health import health_bp
from app.routes.reports import reports_bp
from app.routes.transactions import transactions_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(budgets_bp, url_prefix="/api/budgets")
    app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    return app
