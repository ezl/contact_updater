from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app import db
from app.models import Contact, EmailCampaign, EmailCampaignRecipient
from app.services.email_service import EmailService
import json

email_campaigns_bp = Blueprint('email_campaigns', __name__, url_prefix='/email-campaigns')
email_service = EmailService()

@email_campaigns_bp.route('/')
def list_campaigns():
    """List all email campaigns"""
    campaigns = EmailCampaign.query.order_by(EmailCampaign.created_at.desc()).all()
    return render_template('email_campaigns/list.html', campaigns=campaigns)

@email_campaigns_bp.route('/<int:campaign_id>')
def view_campaign(campaign_id):
    """View email campaign details"""
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    recipients = EmailCampaignRecipient.query.filter_by(campaign_id=campaign_id).all()
    stats = email_service.get_campaign_stats(campaign_id)
    return render_template('email_campaigns/view.html', campaign=campaign, recipients=recipients, stats=stats)

@email_campaigns_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    """Compose a new email campaign"""
    if request.method == 'GET':
        # Get selected contact IDs from session
        contact_ids = session.get('selected_contact_ids', [])
        if not contact_ids:
            session['error_message'] = "No contacts selected for email campaign."
            return redirect(url_for('main.dashboard'))
        
        # Get contact details
        contacts = Contact.query.filter(Contact.id.in_(contact_ids)).all()
        
        # Check if contacts have email addresses
        valid_contacts = [c for c in contacts if c.email]
        if not valid_contacts:
            session['error_message'] = "None of the selected contacts have email addresses."
            return redirect(url_for('main.dashboard'))
        
        return render_template('email_campaigns/compose.html', contacts=valid_contacts)
    
    elif request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        subject = request.form.get('subject')
        body = request.form.get('body')
        contact_ids = json.loads(request.form.get('contact_ids', '[]'))
        
        # Validate form data
        if not name or not subject or not body or not contact_ids:
            return render_template('email_campaigns/compose.html', 
                                  error="All fields are required.",
                                  name=name,
                                  subject=subject,
                                  body=body)
        
        # Create campaign
        campaign = email_service.create_campaign(name, subject, body, contact_ids)
        
        # Redirect to campaign view
        return redirect(url_for('email_campaigns.review', campaign_id=campaign.id))

@email_campaigns_bp.route('/<int:campaign_id>/review', methods=['GET'])
def review(campaign_id):
    """Review email campaign before sending"""
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    recipients = EmailCampaignRecipient.query.filter_by(campaign_id=campaign_id).all()
    return render_template('email_campaigns/review.html', campaign=campaign, recipients=recipients)

@email_campaigns_bp.route('/<int:campaign_id>/send', methods=['POST'])
def send(campaign_id):
    """Send email campaign"""
    try:
        # Send the campaign
        recipient_count = email_service.send_campaign(campaign_id)
        
        # Set success message
        campaign_url = url_for('email_campaigns.view_campaign', campaign_id=campaign_id)
        session['success_message'] = f"Successfully sent email to {recipient_count} clients. <a href=\"{campaign_url}\" class=\"underline font-medium\">View campaign</a>"
        session['has_html'] = True
        
        # Redirect to dashboard
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        # Set error message
        session['error_message'] = f"Error sending email campaign: {str(e)}"
        return redirect(url_for('email_campaigns.review', campaign_id=campaign_id))

@email_campaigns_bp.route('/select-contacts', methods=['POST'])
def select_contacts():
    """Store selected contact IDs in session and redirect to compose page"""
    contact_ids = request.json.get('contact_ids', [])
    if not contact_ids:
        return jsonify({'status': 'error', 'message': 'No contacts selected'}), 400
    
    # Store in session
    session['selected_contact_ids'] = contact_ids
    
    return jsonify({
        'status': 'success',
        'redirect': url_for('email_campaigns.compose')
    }) 