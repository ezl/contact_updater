from app import create_app, db
import sqlite3
import os

# This script handles database schema updates
# It creates tables that don't exist and adds missing columns to existing tables

def get_db_path():
    """Get the path to the SQLite database file from the app configuration"""
    app = create_app()
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        return db_uri.replace('sqlite:///', '')
    else:
        raise ValueError("This script only works with SQLite databases")

def add_column_if_not_exists(column_name, column_type, table_name='contact'):
    """Add a column to a table if it doesn't already exist"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [info[1] for info in cursor.fetchall()]
        
        if column_name not in columns:
            print(f"Adding column '{column_name}' to table '{table_name}'...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
            conn.commit()
            print(f"Column '{column_name}' added successfully.")
            return True
        else:
            print(f"Column '{column_name}' already exists in table '{table_name}'.")
            return False
    except Exception as e:
        print(f"Error adding column: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Updating database schema...")
    
    # Create the app and ensure all tables exist
    app = create_app()
    with app.app_context():
        db.create_all()
    
    # Add any missing columns
    add_column_if_not_exists('facebook', 'TEXT')
    add_column_if_not_exists('instagram', 'TEXT')
    add_column_if_not_exists('twitter', 'TEXT')
    
    print("Schema update complete.") 