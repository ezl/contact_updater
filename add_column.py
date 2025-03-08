from app import create_app
import sqlite3
import os
import sys

# This script adds a new column to the contacts table
# Usage: python add_column.py column_name column_type

if len(sys.argv) < 3:
    print("Usage: python add_column.py column_name column_type")
    print("Example: python add_column.py facebook TEXT")
    sys.exit(1)

column_name = sys.argv[1]
column_type = sys.argv[2]

# Get the database file path from the app configuration
app = create_app()
db_uri = app.config['SQLALCHEMY_DATABASE_URI']
if db_uri.startswith('sqlite:///'):
    db_path = db_uri.replace('sqlite:///', '')
else:
    print("This script only works with SQLite databases")
    sys.exit(1)

print(f"Using database: {db_path}")
print(f"Adding column '{column_name}' with type '{column_type}' to contacts table...")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(contact)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if column_name in columns:
        print(f"Column '{column_name}' already exists in the contacts table.")
        sys.exit(0)
    
    # Add the column
    cursor.execute(f"ALTER TABLE contact ADD COLUMN {column_name} {column_type}")
    conn.commit()
    print(f"Column '{column_name}' added successfully.")
    
    # Verify the column was added
    cursor.execute("PRAGMA table_info(contact)")
    columns = [info[1] for info in cursor.fetchall()]
    if column_name in columns:
        print("Verification successful: Column exists in the schema.")
    else:
        print("Warning: Column was not found in schema after adding!")
        
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    conn.close() 