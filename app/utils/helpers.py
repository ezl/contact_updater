import os
import uuid
import holidays
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from app import db
from app.models import Contact, DeletedContact

# Global store for rejected records
rejected_records_store = {}

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv'}

def serialize_contact(contact):
    """Serialize a contact object to a dictionary"""
    return {
        'id': contact.id,
        'name': contact.name,
        'cell': contact.cell,
        'email': contact.email,
        'mailing_address': contact.mailing_address,
        'notes': contact.notes,
        'birthday': contact.birthday,
        'facebook': contact.facebook,
        'instagram': contact.instagram,
        'twitter': contact.twitter,
        'email_updated': contact.email_updated.isoformat() if contact.email_updated else None,
        'cell_updated': contact.cell_updated.isoformat() if contact.cell_updated else None,
        'mailing_address_updated': contact.mailing_address_updated.isoformat() if contact.mailing_address_updated else None,
        'dateAdded': contact.dateAdded.isoformat() if contact.dateAdded else None,
        'lastModified': contact.lastModified.isoformat() if contact.lastModified else None
    }

def get_holidays_for_month(month, year):
    """Get holidays for a specific month and year"""
    us_holidays = holidays.US(years=year)
    
    # Filter holidays for the specified month
    month_holidays = []
    for date, name in us_holidays.items():
        if date.month == month:
            month_holidays.append({
                'date': date.day,
                'name': name
            })
    
    return month_holidays

def cleanup_deleted_contacts(app):
    """Clean up old deleted contacts based on expiration time"""
    with app.app_context():
        # Calculate the expiration time
        expiration_minutes = app.config.get('UNDO_EXPIRATION_MINUTES', 30)
        expiration_time = datetime.utcnow() - timedelta(minutes=expiration_minutes)
        
        # Delete expired records
        DeletedContact.query.filter(DeletedContact.deleted_at < expiration_time).delete()
        db.session.commit() 