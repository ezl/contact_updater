import uuid
from datetime import datetime
from app import db
from app.models import EmailCampaign, EmailCampaignRecipient, Contact

class EmailService:
    """Service for handling email operations"""
    
    def __init__(self):
        """Initialize the email service"""
        # This would be where we initialize the third-party email service
        pass
    
    def create_campaign(self, name, subject, body, contact_ids):
        """Create a new email campaign"""
        # Create the campaign
        campaign = EmailCampaign(
            name=name,
            subject=subject,
            body=body,
            status='draft'
        )
        db.session.add(campaign)
        db.session.flush()  # Flush to get the campaign ID
        
        # Add recipients
        contacts = Contact.query.filter(Contact.id.in_(contact_ids)).all()
        for contact in contacts:
            if contact.email:  # Only add contacts with email addresses
                recipient = EmailCampaignRecipient(
                    campaign_id=campaign.id,
                    contact_id=contact.id,
                    email=contact.email,
                    name=contact.name,
                    tracking_id=str(uuid.uuid4())
                )
                db.session.add(recipient)
        
        db.session.commit()
        return campaign
    
    def send_campaign(self, campaign_id):
        """Send an email campaign"""
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        # Update campaign status
        campaign.status = 'sending'
        campaign.sent_at = datetime.utcnow()
        db.session.commit()
        
        # Send emails to each recipient
        recipients = EmailCampaignRecipient.query.filter_by(campaign_id=campaign_id).all()
        for recipient in recipients:
            self.send_email(campaign, recipient)
        
        # Update campaign status
        campaign.status = 'sent'
        db.session.commit()
        
        return len(recipients)
    
    def send_email(self, campaign, recipient):
        """Send an individual email for a campaign (stub method)"""
        # Debug print statement
        print(f"Sending email to {recipient.email} - Subject: {campaign.subject}")
        
        # This would be where we call the third-party email service
        # For now, just update the recipient status
        recipient.status = 'sent'
        db.session.commit()
        
        # In a real implementation, we would:
        # 1. Personalize the email content
        # 2. Add tracking pixels and rewrite links
        # 3. Send via third-party API
        # 4. Handle errors and retries
        
        return True
    
    def track_open(self, tracking_id):
        """Track email open event (stub method)"""
        recipient = EmailCampaignRecipient.query.filter_by(tracking_id=tracking_id).first()
        if recipient:
            recipient.status = 'opened'
            recipient.opened_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def track_click(self, tracking_id):
        """Track link click event (stub method)"""
        recipient = EmailCampaignRecipient.query.filter_by(tracking_id=tracking_id).first()
        if recipient:
            recipient.status = 'clicked'
            recipient.clicked_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def track_bounce(self, tracking_id):
        """Track email bounce event (stub method)"""
        recipient = EmailCampaignRecipient.query.filter_by(tracking_id=tracking_id).first()
        if recipient:
            recipient.status = 'bounced'
            recipient.bounced_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def get_campaign_stats(self, campaign_id):
        """Get statistics for a campaign"""
        campaign = EmailCampaign.query.get(campaign_id)
        if not campaign:
            return None
        
        recipients = EmailCampaignRecipient.query.filter_by(campaign_id=campaign_id).all()
        total = len(recipients)
        
        stats = {
            'total': total,
            'sent': sum(1 for r in recipients if r.status != 'pending'),
            'delivered': sum(1 for r in recipients if r.status in ['delivered', 'opened', 'clicked', 'responded']),
            'opened': sum(1 for r in recipients if r.status in ['opened', 'clicked', 'responded']),
            'clicked': sum(1 for r in recipients if r.status in ['clicked', 'responded']),
            'responded': sum(1 for r in recipients if r.status == 'responded'),
            'bounced': sum(1 for r in recipients if r.status == 'bounced')
        }
        
        # Calculate rates
        if total > 0:
            stats['delivery_rate'] = (stats['delivered'] / total) * 100
            stats['open_rate'] = (stats['opened'] / total) * 100 if stats['delivered'] > 0 else 0
            stats['click_rate'] = (stats['clicked'] / stats['opened']) * 100 if stats['opened'] > 0 else 0
            stats['response_rate'] = (stats['responded'] / total) * 100
            stats['bounce_rate'] = (stats['bounced'] / total) * 100
        
        return stats 