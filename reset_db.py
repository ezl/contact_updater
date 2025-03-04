"""
Database reset script for Contact Updater application.
WARNING: This script will delete all data in the database!
Run this script to completely reset the database.
"""
from app import app, db
import os
import sys

# Check for --auto flag for non-interactive mode
auto_mode = "--auto" in sys.argv

# Flask-SQLAlchemy stores the database in the instance folder by default
INSTANCE_DIR = 'instance'
DB_FILE = os.path.join(INSTANCE_DIR, 'sqlite3.db')
DB_ABSOLUTE_PATH = os.path.abspath(DB_FILE)

print(f"Database file: {DB_ABSOLUTE_PATH}")

if not auto_mode:
    print("WARNING: This will delete all contacts data in the database!")
    confirmation = input("Type 'YES' to confirm: ")
else:
    # Auto mode bypasses confirmation
    confirmation = "YES"

if confirmation == "YES":
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        
        # Verify the operation was successful
        if os.path.exists(DB_FILE):
            print(f"Database has been reset successfully ({os.path.getsize(DB_FILE)} bytes).")
        else:
            print("WARNING: Database file does not exist after reset operation!")
else:
    print("Operation cancelled. Database was not reset.") 