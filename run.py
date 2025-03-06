from app import create_app, db
from flask import request

# Create the Flask application
app = create_app()

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

@app.before_request
def log_request_info():
    """Log request information for debugging"""
    if app.debug:
        print(f"Request: {request.method} {request.path}")

if __name__ == '__main__':
    # Run the application
    app.run(debug=True) 