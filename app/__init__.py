"""
Application Factory

Initializes the Flask application, registers extensions,
and attaches all blueprints.
"""

from flask import Flask, render_template
from config import Config

# Import initialized extensions
from .extensions import db, login_manager, mail, csrf, migrate

# Import models
from .models import User

def create_app():
    """Create and configurate the Flask application instance."""

    # Create Flask application instance
    app = Flask(__name__)

    # Load configuration settings
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    # Configure login manager
    login_manager.login_view = "main.index"
    login_manager.login_message_category = "warning"

    # User Loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from .main.routes import main_bp
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .donor.routes import donor_bp
    from .requester.routes import requester_bp
    from .volunteer.routes import volunteer_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(requester_bp)
    app.register_blueprint(volunteer_bp)

    # Register Global Error Handlers
    register_error_handlers(app)

    return app


# GLOBAL ERROR HANDLERS
def register_error_handlers(app):
    """Register application-wide errors."""

    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbiden errors."""
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Forbiden errors."""
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server error."""
        db.session.rollback()
        return render_template("errors/500.html"), 500