"""
Application Entry point

Creates the Flask application instance and starts the development server.
Also ensures default admin user is created on startup.
"""

# Import application factory
from app import create_app

# Import utility function to create default admin
from app.utils import create_admin

# Create Flask app instance
app = create_app()

# Ensure default admin exists safely (won’t crash app)
try:
    with app.app_context():
        create_admin()
except Exception as e:
    print("Admin creation skipped:", e)

# Run development server (only for local)
if __name__ == "__main__":
    app.run(debug=True)