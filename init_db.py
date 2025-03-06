"""
Database initialization script for Client Magic application.
Run this script to create the database tables if they don't exist.
"""
from app import create_app, db
import os

def init_db():
    """Initialize the database by creating all tables"""
    print("Initializing database...")
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized successfully.")
        
        # Verify the database file exists
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_file = db_uri.replace('sqlite:///', '')
            db_absolute_path = os.path.abspath(db_file)
            print(f"Database file path: {db_absolute_path}")
            if os.path.exists(db_file):
                print(f"Database file size: {os.path.getsize(db_file)} bytes")
            else:
                print("WARNING: Database file does not exist after initialization!")

if __name__ == '__main__':
    init_db() 