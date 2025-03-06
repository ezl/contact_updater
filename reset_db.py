"""
Database reset script for Client Magic application.
This script drops all tables and recreates them, effectively resetting the database.
WARNING: This will delete all data in the database!
Run this script to completely reset the database.
"""
from app import create_app, db
import os

def reset_db():
    """Reset the database by dropping and recreating all tables"""
    app = create_app()
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped.")
        
        # Create all tables
        db.create_all()
        print("Database reset successfully.")
        
        # Verify the operation was successful
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_file = db_uri.replace('sqlite:///', '')
            if os.path.exists(db_file):
                print(f"Database has been reset successfully ({os.path.getsize(db_file)} bytes).")
            else:
                print("WARNING: Database file does not exist after reset operation!")

if __name__ == '__main__':
    # Confirm with the user
    confirm = input("This will delete all data in the database. Are you sure? (y/n): ")
    if confirm.lower() == 'y':
        reset_db()
    else:
        print("Database reset cancelled.") 