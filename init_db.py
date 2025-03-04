"""
Database initialization script for Client Magic application.
Run this script to create the database tables if they don't exist.
"""
from app import app, db
import os

print("Initializing database...")

# Flask-SQLAlchemy stores the database in the instance folder by default
INSTANCE_DIR = 'instance'
DB_FILE = os.path.join(INSTANCE_DIR, 'sqlite3.db')
DB_ABSOLUTE_PATH = os.path.abspath(DB_FILE)

print(f"Database file path: {DB_ABSOLUTE_PATH}")

with app.app_context():
    # Create tables only if they don't exist
    db.create_all()
    print("Database tables created.")
    
    # Verify the database file exists
    if os.path.exists(DB_FILE):
        print(f"Database file created successfully ({os.path.getsize(DB_FILE)} bytes)")
    else:
        print("WARNING: Database file was not created at the expected location!")
        print(f"Expected at: {DB_ABSOLUTE_PATH}")
    
print("Database initialization complete.") 