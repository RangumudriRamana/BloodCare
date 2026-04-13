"""
Application Entry point

Creates the Flask application instance and starts the development server.
Also ensures database tables and default admin user are created safely.
"""

# Import application factory
from app import create_app

# Import extensions
from app.extensions import db

# Import utility function to create default admin
from app.utils import create_admin

# Create Flask app instance
app = create_app()

# Ensure database tables + admin exist (safe startup)
try:
    with app.app_context():
        db.create_all()
        create_admin()
except Exception as e:
    print("Startup setup skipped:", e)

# Run development server (only for local)
if __name__ == "__main__":
    app.run(debug=True)