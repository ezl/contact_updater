from app import create_app, db
from app.models import Contact

app = create_app()

with app.app_context():
    Contact.query.delete()
    db.session.commit()
    print("Database cleared successfully.") 