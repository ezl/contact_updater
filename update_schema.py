from app import app, db
import sqlite3
import os

# This script handles database schema updates
# It creates tables that don't exist and adds missing columns to existing tables

def get_db_path():
    """Get the path to the SQLite database file"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'sqlite3.db')

def add_column_if_not_exists(column_name, column_type, table_name='contact'):
    """Add a column to a table if it doesn't already exist"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        if column_name not in columns:
            # Add the new column
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            print(f"Column '{column_name}' added to table '{table_name}'")
            conn.commit()
            return True
        else:
            print(f"Column '{column_name}' already exists in table '{table_name}'")
            return False
            
    except Exception as e:
        print(f"Error adding column '{column_name}': {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

# Create all tables that don't exist yet
with app.app_context():
    db.create_all()
    print("Database tables created (if they didn't exist already)")

# Add any missing columns to existing tables
# This is necessary because SQLAlchemy's create_all() doesn't alter existing tables
add_column_if_not_exists('email_updated', 'TIMESTAMP')
add_column_if_not_exists('cell_updated', 'TIMESTAMP')
add_column_if_not_exists('mailing_address_updated', 'TIMESTAMP')

print("Database schema update completed!") 