from app import db
from datetime import datetime

class Contact(db.Model):
    """Model for storing contact information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    cell = db.Column(db.String(20))
    email = db.Column(db.String(120))
    mailing_address = db.Column(db.String(300))
    notes = db.Column(db.Text)
    birthday = db.Column(db.String(5))  # Store as MM-DD format
    email_updated = db.Column(db.DateTime, nullable=True)
    cell_updated = db.Column(db.DateTime, nullable=True)
    mailing_address_updated = db.Column(db.DateTime, nullable=True)
    facebook = db.Column(db.String(200), nullable=True)
    instagram = db.Column(db.String(200), nullable=True)
    twitter = db.Column(db.String(200), nullable=True)
    dateAdded = db.Column(db.DateTime, default=datetime.utcnow)
    lastModified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'cell': self.cell,
            'email': self.email,
            'mailing_address': self.mailing_address,
            'notes': self.notes,
            'birthday': self.birthday,
            'email_updated': self.email_updated.isoformat() if self.email_updated else None,
            'cell_updated': self.cell_updated.isoformat() if self.cell_updated else None,
            'mailing_address_updated': self.mailing_address_updated.isoformat() if self.mailing_address_updated else None,
            'facebook': self.facebook,
            'instagram': self.instagram,
            'twitter': self.twitter,
            'dateAdded': self.dateAdded.isoformat() if self.dateAdded else None,
            'lastModified': self.lastModified.isoformat() if self.lastModified else None
        }


class DeletedContact(db.Model):
    """Model for storing deleted contacts for undo functionality"""
    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer)  # Original ID of the contact
    contact_data = db.Column(db.Text)  # JSON string of contact data
    deletion_type = db.Column(db.String(20))  # 'single', 'all', or 'duplicate'
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)
    operation_id = db.Column(db.String(50))  # Group ID for batch operations 