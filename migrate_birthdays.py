"""
Birthday format migration script for Client Magic application.
This script updates any existing birthday entries to ensure they are in MM-DD format.
"""
from app import create_app, db
from app.models import Contact
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

if confirmation != "YES":
    print("Migration cancelled.")
    sys.exit(0)

# Function to convert various date formats to MM-DD
def normalize_birthday(birthday_str):
    if not birthday_str or birthday_str == '-':
        return None
    
    # Try different date formats
    formats = [
        '%m-%d',       # MM-DD
        '%d-%b',       # DD-MMM
        '%m/%d/%Y',    # MM/DD/YYYY
        '%Y-%m-%d',    # YYYY-MM-DD
    ]
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(birthday_str, fmt)
            # Return in MM-DD format
            return date_obj.strftime('%m-%d')
        except ValueError:
            continue
    
    # If we get here, none of the formats matched
    return None

# Create app and run migration within app context
app = create_app()
with app.app_context():
    # Get all contacts with birthday data
    contacts = Contact.query.filter(Contact.birthday.isnot(None)).all()
    
    print(f"Found {len(contacts)} contacts with birthday data.")
    
    # Track statistics
    updated = 0
    already_correct = 0
    invalid = 0
    
    for contact in contacts:
        if not contact.birthday or contact.birthday == '-':
            continue
            
        # Try to normalize the birthday
        normalized = normalize_birthday(contact.birthday)
        
        if normalized:
            if normalized == contact.birthday:
                already_correct += 1
                print(f"✓ {contact.name}: {contact.birthday} (already in correct format)")
            else:
                print(f"✓ {contact.name}: {contact.birthday} → {normalized}")
                contact.birthday = normalized
                updated += 1
        else:
            print(f"✗ {contact.name}: {contact.birthday} (invalid format, cannot convert)")
            invalid += 1
    
    # Commit changes if any were made
    if updated > 0:
        db.session.commit()
        print(f"Successfully updated {updated} contacts.")
    
    # Print summary
    print("\nMigration Summary:")
    print(f"- Total contacts with birthday data: {len(contacts)}")
    print(f"- Already in correct format: {already_correct}")
    print(f"- Updated to MM-DD format: {updated}")
    print(f"- Invalid formats (not updated): {invalid}")
    
    if updated == 0 and invalid == 0:
        print("\nAll birthdays are already in the correct format. No changes needed.") 