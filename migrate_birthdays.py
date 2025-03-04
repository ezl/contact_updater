"""
Birthday format migration script for Client Joy application.
This script updates any existing birthday entries to ensure they are in MM-DD format.
"""
from app import app, db, Contact
from datetime import datetime
import sys

# Check for --auto flag for non-interactive mode
auto_mode = "--auto" in sys.argv

print("Birthday Format Migration Tool")
print("------------------------------")
print("This script will update any birthday entries that are not in MM-DD format.")

if not auto_mode:
    print("WARNING: This will modify birthday data in the database!")
    confirmation = input("Type 'YES' to confirm: ")
else:
    # Auto mode bypasses confirmation
    confirmation = "YES"

if confirmation == "YES":
    with app.app_context():
        # Get all contacts
        contacts = Contact.query.all()
        updated_count = 0
        skipped_count = 0
        
        print(f"Found {len(contacts)} contacts in the database.")
        
        for contact in contacts:
            # Skip if no birthday
            if not contact.birthday:
                continue
                
            birthday = contact.birthday.strip()
            
            # Skip if already in MM-DD format
            if len(birthday) == 5 and birthday[2] == '-':
                try:
                    # Validate it's a proper MM-DD format
                    datetime.strptime(birthday, '%m-%d')
                    continue
                except ValueError:
                    # Not a valid MM-DD format, so process it
                    pass
            
            # Try to convert to MM-DD format
            try:
                # Handle YYYY-MM-DD format
                if len(birthday) == 10 and birthday[4] == '-' and birthday[7] == '-':
                    date_obj = datetime.strptime(birthday, '%Y-%m-%d')
                    new_birthday = date_obj.strftime('%m-%d')
                    print(f"Converting birthday for {contact.name}: {birthday} → {new_birthday}")
                    contact.birthday = new_birthday
                    updated_count += 1
                else:
                    # Try a more flexible approach
                    try:
                        import pandas as pd
                        date_obj = pd.to_datetime(birthday)
                        new_birthday = date_obj.strftime('%m-%d')
                        print(f"Converting birthday for {contact.name}: {birthday} → {new_birthday}")
                        contact.birthday = new_birthday
                        updated_count += 1
                    except:
                        print(f"Could not convert birthday for {contact.name}: {birthday}")
                        skipped_count += 1
            except Exception as e:
                print(f"Error processing birthday for {contact.name}: {e}")
                skipped_count += 1
        
        # Commit changes
        if updated_count > 0:
            db.session.commit()
            print(f"Migration complete: {updated_count} birthdays updated, {skipped_count} birthdays skipped.")
        else:
            print("No birthdays needed updating. All are already in MM-DD format.")
else:
    print("Operation cancelled. No changes were made to the database.") 