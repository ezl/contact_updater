import sqlite3
import os

# Get the database file paths
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
db_paths = [
    os.path.join(instance_dir, 'contacts.db'),
    os.path.join(instance_dir, 'sqlite3.db')
]

success = False

for db_path in db_paths:
    print(f"Checking database: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if the contact table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contact'")
        if not cursor.fetchone():
            print(f"Table 'contact' not found in {db_path}")
            conn.close()
            continue
            
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(contact)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'mailing_address_updated' not in columns:
            # Add the new column
            cursor.execute("ALTER TABLE contact ADD COLUMN mailing_address_updated TIMESTAMP")
            print(f"Column 'mailing_address_updated' added successfully to {db_path}!")
            success = True
        else:
            print(f"Column 'mailing_address_updated' already exists in {db_path}.")
            success = True
        
        # Commit the changes
        conn.commit()
        
    except Exception as e:
        print(f"Error updating database {db_path}: {e}")
        conn.rollback()
        
    finally:
        # Close the connection
        conn.close()

if success:
    print("Database schema updated successfully!")
else:
    print("Failed to update any database schema.") 