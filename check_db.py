"""
Database check script for Contact Updater application.
Run this script to verify the database is set up correctly and display information about it.
"""
from app import app, db, Contact
import os

# Flask-SQLAlchemy stores the database in the instance folder by default
INSTANCE_DIR = 'instance'
DB_FILE = os.path.join(INSTANCE_DIR, 'sqlite3.db')
DB_ABSOLUTE_PATH = os.path.abspath(DB_FILE)

def get_db_stats():
    """Get statistics about the database."""
    with app.app_context():
        contact_count = Contact.query.count()
        db_exists = os.path.exists(DB_FILE)
        if db_exists:
            db_size = os.path.getsize(DB_FILE) / 1024  # Size in KB
        else:
            db_size = 0
    
    return {
        'exists': db_exists,
        'size_kb': db_size,
        'contacts': contact_count
    }

def check_db_tables():
    """Check if all required tables exist in the database."""
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
    print(f"Database file: {DB_FILE}")
    print(f"Absolute path: {DB_ABSOLUTE_PATH}")
    
    stats = get_db_stats()
    
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