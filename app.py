
import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_login import login_required, current_user

from config import Config
from extensions import db, login_manager, csrf, limiter
from models.user import User
from routes.auth import auth
from security.decorators import role_required
from routes.documents import documents

# Load environment variables
load_dotenv()


def create_app(test_config=None):

    app = Flask(__name__)

    # Load application configuration
    app.config.from_object(Config)

    # Session security configuration
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Remember-me cookie security
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"

    # Configure rate limiting
    app.config["RATELIMIT_STORAGE_URI"] = os.getenv(
        "RATELIMIT_STORAGE_URI",
        "memory://"
    )

    if test_config:
        app.config.update(test_config)

    # Validate SECRET_KEY
    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is missing. Set it in your .env file."
        )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Flask-Login configuration
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in first."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(documents)

    # Dashboard
    @app.route("/")
    @login_required
    def dashboard():
        return render_template(
            "dashboard.html",
            user=current_user
        )

    # Admin dashboard
    @app.route("/admin")
    @login_required
    @role_required("admin")
    def admin_dashboard():
        return "Admin access granted"

    return app


app = create_app()


if __name__ == "__main__":
    # Local development only
    app.run(debug=True)
