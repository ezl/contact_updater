from app import db
from datetime import datetime

class EmailCampaign(db.Model):
    """Model for storing email campaign information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    subject = db.Column(db.String(200))
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='draft')  # draft, sending, sent, failed
    
    # Relationship with recipients
    recipients = db.relationship('EmailCampaignRecipient', backref='campaign', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<EmailCampaign {self.name}>'
    
    def to_dict(self):
        """Convert campaign to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'recipient_count': len(self.recipients)
        }

class EmailCampaignRecipient(db.Model):
    """Model for storing email campaign recipient information"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('email_campaign.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    email = db.Column(db.String(120))
    name = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, opened, clicked, responded, bounced
    delivered_at = db.Column(db.DateTime, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)
    bounced_at = db.Column(db.DateTime, nullable=True)
    tracking_id = db.Column(db.String(50), unique=True)  # Unique ID for tracking
    
    # Relationship with contact
    contact = db.relationship('Contact', backref='email_campaign_recipients')
    
    def __repr__(self):
        return f'<EmailCampaignRecipient {self.email}>'
    
    def to_dict(self):
        """Convert recipient to dictionary"""
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'contact_id': self.contact_id,
            'email': self.email,
            'name': self.name,
            'status': self.status,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'bounced_at': self.bounced_at.isoformat() if self.bounced_at else None,
            'tracking_id': self.tracking_id
        } 