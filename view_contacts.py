from app import create_app
from app.models import Contact

app = create_app()

with app.app_context():
    contacts = Contact.query.all()
    print("\nDatabase Contents:")
    print("==================")
    for contact in contacts:
        print(f"\nContact ID: {contact.id}")
        print(f"Name: {contact.name}")
        print(f"Cell: {contact.cell}")
        print(f"Email: {contact.email}")
        print(f"Address: {contact.mailing_address}")
        print(f"Notes: {contact.notes}")
        print(f"Birthday: {contact.birthday}")
        print(f"Facebook: {contact.facebook}")
        print(f"Instagram: {contact.instagram}")
        print(f"Twitter: {contact.twitter}")
        print("-" * 50) 