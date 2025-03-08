"""
Database check script for Client Magic application.
Run this script to verify the database is set up correctly and display information about it.
"""
from app import create_app, db
from app.models import Contact
import os

def get_db_stats():
    """Get statistics about the database."""
    app = create_app()
    with app.app_context():
        # Get the database file path from the app config
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            db_file = db_uri.replace('sqlite:///', '')
            db_absolute_path = os.path.abspath(db_file)
        else:
            db_file = "Unknown (not SQLite)"
            db_absolute_path = "Unknown"
            
        contact_count = Contact.query.count()
        db_exists = os.path.exists(db_file) if db_file != "Unknown (not SQLite)" else False
        if db_exists:
            db_size = os.path.getsize(db_file) / 1024  # Size in KB
        else:
            db_size = 0
    
    return {
        'exists': db_exists,
        'size_kb': db_size,
        'contacts': contact_count,
        'db_file': db_file,
        'db_absolute_path': db_absolute_path
    }

def check_db_tables():
    """Check if all required tables exist in the database."""
    app = create_app()
    with app.app_context():
        # This will not throw an error if the table exists
        try:
            Contact.query.limit(1).all()
            return True
        except Exception as e:
            print(f"Error checking tables: {e}")
            return False

if __name__ == "__main__":
    print("Checking database configuration...")
    
    stats = get_db_stats()
    
    print(f"Database file: {stats['db_file']}")
    print(f"Absolute path: {stats['db_absolute_path']}")
    
    if stats['exists']:
        print(f"✅ Database file exists ({stats['size_kb']:.2f} KB)")
    else:
        print("❌ Database file does not exist!")
        print("Run 'python init_db.py' to create the database.")
        exit(1)
    
    if check_db_tables():
        print("✅ Database tables are properly configured")
    else:
        print("❌ Database tables are not properly configured!")
        print("Run 'python init_db.py' to set up the tables.")
        exit(1)
    
    print(f"Total contacts in database: {stats['contacts']}")
    print("Database check completed successfully!") 