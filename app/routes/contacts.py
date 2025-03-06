from flask import Blueprint, request, redirect, url_for, jsonify, session, json
from datetime import datetime
import uuid
from app import db
from app.models import Contact, DeletedContact
from app.utils.helpers import serialize_contact

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/add_contact', methods=['POST'])
def add_contact():
    """Add a new contact"""
    try:
        # Get form data
        name = request.form.get('name')
        cell = request.form.get('cell')
        email = request.form.get('email')
        mailing_address = request.form.get('mailing_address')
        notes = request.form.get('notes')
        birthday = request.form.get('birthday')
        facebook = request.form.get('facebook')
        instagram = request.form.get('instagram')
        twitter = request.form.get('twitter')
        
        # Format birthday if provided
        if birthday:
            try:
                # Parse the date from the form
                date_obj = datetime.strptime(birthday, '%Y-%m-%d')
                # Format as MM-DD
                birthday = date_obj.strftime('%m-%d')
            except ValueError:
                # If the date is invalid, use the raw input
                pass
        
        # Create new contact
        new_contact = Contact(
            name=name,
            cell=cell,
            email=email,
            mailing_address=mailing_address,
            notes=notes,
            birthday=birthday,
            facebook=facebook,
            instagram=instagram,
            twitter=twitter
        )
        
        # Add to database
        db.session.add(new_contact)
        db.session.commit()
        
        session['success_message'] = f"Successfully added {name} to your contacts."
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error adding contact: {str(e)}"
        return redirect(url_for('main.dashboard'))

@contacts_bp.route('/update_contact/<int:id>', methods=['POST'])
def update_contact(id):
    """Update an existing contact"""
    try:
        # Find the contact
        contact = Contact.query.get_or_404(id)
        
        # Get form data
        name = request.form.get('name')
        cell = request.form.get('cell')
        email = request.form.get('email')
        mailing_address = request.form.get('mailing_address')
        notes = request.form.get('notes')
        birthday = request.form.get('birthday')
        facebook = request.form.get('facebook')
        instagram = request.form.get('instagram')
        twitter = request.form.get('twitter')
        
        # Format birthday if provided
        if birthday:
            try:
                # Parse the date from the form
                date_obj = datetime.strptime(birthday, '%Y-%m-%d')
                # Format as MM-DD
                birthday = date_obj.strftime('%m-%d')
            except ValueError:
                # If the date is invalid, use the raw input
                pass
        
        # Update contact fields
        contact.name = name
        
        # Track field updates with timestamps
        if cell != contact.cell:
            contact.cell = cell
            contact.cell_updated = datetime.utcnow()
            
        if email != contact.email:
            contact.email = email
            contact.email_updated = datetime.utcnow()
            
        if mailing_address != contact.mailing_address:
            contact.mailing_address = mailing_address
            contact.mailing_address_updated = datetime.utcnow()
        
        contact.notes = notes
        contact.birthday = birthday
        contact.facebook = facebook
        contact.instagram = instagram
        contact.twitter = twitter
        
        # Save changes
        db.session.commit()
        
        session['success_message'] = f"Successfully updated {name}'s information."
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error updating contact: {str(e)}"
        return redirect(url_for('main.dashboard'))

@contacts_bp.route('/delete_contact/<int:id>', methods=['POST'])
def delete_contact(id):
    """Delete a single contact"""
    try:
        # Find the contact
        contact = Contact.query.get_or_404(id)
        name = contact.name
        
        # Store the contact data for undo functionality
        contact_data = json.dumps(serialize_contact(contact))
        
        # Create a record in the DeletedContact table
        deleted_contact = DeletedContact(
            original_id=contact.id,
            contact_data=contact_data,
            deletion_type='single',
            operation_id=str(datetime.utcnow().timestamp())
        )
        
        # Add the deleted contact record
        db.session.add(deleted_contact)
        
        # Delete the contact
        db.session.delete(contact)
        db.session.commit()
        
        session['success_message'] = f"Successfully deleted {name} from your contacts."
        return redirect(url_for('main.dashboard', 
                              undo_action='single', 
                              undo_id=deleted_contact.operation_id))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error deleting contact: {str(e)}"
        return redirect(url_for('main.dashboard'))

@contacts_bp.route('/delete_all_contacts', methods=['POST'])
def delete_all_contacts():
    """Delete all contacts"""
    try:
        # Get all contacts
        contacts = Contact.query.all()
        count = len(contacts)
        
        if count == 0:
            session['error_message'] = "No contacts to delete."
            return redirect(url_for('main.dashboard'))
        
        # Generate an operation ID for this batch deletion
        operation_id = str(datetime.utcnow().timestamp())
        
        # Store each contact for undo functionality
        for contact in contacts:
            contact_data = json.dumps(serialize_contact(contact))
            
            # Create a record in the DeletedContact table
            deleted_contact = DeletedContact(
                original_id=contact.id,
                contact_data=contact_data,
                deletion_type='all',
                operation_id=operation_id
            )
            
            # Add the deleted contact record
            db.session.add(deleted_contact)
        
        # Delete all contacts
        Contact.query.delete()
        db.session.commit()
        
        session['success_message'] = f"Successfully deleted all {count} clients from the database."
        return redirect(url_for('main.dashboard', 
                              undo_action='all', 
                              undo_id=operation_id))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error deleting contacts: {str(e)}"
        return redirect(url_for('main.dashboard'))

@contacts_bp.route('/get_contact/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact as JSON"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        return jsonify(serialize_contact(contact))
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@contacts_bp.route('/undo_delete/<string:action>/<string:id>')
def undo_delete(action, id):
    """Undo a delete operation"""
    try:
        if action == 'single':
            # Find the deleted contact record
            deleted_contact = DeletedContact.query.filter_by(operation_id=id).first()
            
            if not deleted_contact:
                session['error_message'] = "Could not find the deleted contact to restore."
                return redirect(url_for('main.dashboard'))
            
            # Parse the contact data
            contact_data = json.loads(deleted_contact.contact_data)
            
            # Create a new contact with the original data
            new_contact = Contact(
                name=contact_data.get('name'),
                cell=contact_data.get('cell'),
                email=contact_data.get('email'),
                mailing_address=contact_data.get('mailing_address'),
                notes=contact_data.get('notes'),
                birthday=contact_data.get('birthday'),
                facebook=contact_data.get('facebook'),
                instagram=contact_data.get('instagram'),
                twitter=contact_data.get('twitter')
            )
            
            # Add the new contact
            db.session.add(new_contact)
            
            # Delete the deleted contact record
            db.session.delete(deleted_contact)
            db.session.commit()
            
            session['success_message'] = f"Successfully restored {new_contact.name} to your contacts."
            
        elif action == 'all' or action == 'duplicate':
            # Find all deleted contacts for this operation
            deleted_contacts = DeletedContact.query.filter_by(operation_id=id).all()
            
            if not deleted_contacts:
                session['error_message'] = "Could not find the deleted contacts to restore."
                return redirect(url_for('main.dashboard'))
            
            # Restore each contact
            count = 0
            for deleted_contact in deleted_contacts:
                # Parse the contact data
                contact_data = json.loads(deleted_contact.contact_data)
                
                # Create a new contact with the original data
                new_contact = Contact(
                    name=contact_data.get('name'),
                    cell=contact_data.get('cell'),
                    email=contact_data.get('email'),
                    mailing_address=contact_data.get('mailing_address'),
                    notes=contact_data.get('notes'),
                    birthday=contact_data.get('birthday'),
                    facebook=contact_data.get('facebook'),
                    instagram=contact_data.get('instagram'),
                    twitter=contact_data.get('twitter')
                )
                
                # Add the new contact
                db.session.add(new_contact)
                count += 1
            
            # Delete the deleted contact records
            for deleted_contact in deleted_contacts:
                db.session.delete(deleted_contact)
            
            db.session.commit()
            
            action_type = "all contacts" if action == 'all' else "duplicate contacts"
            session['success_message'] = f"Successfully restored {count} {action_type} to your database."
        
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error restoring contacts: {str(e)}"
        return redirect(url_for('main.dashboard'))

@contacts_bp.route('/remove_duplicates', methods=['POST'])
def remove_duplicates():
    """Remove duplicate contacts based on email or phone"""
    try:
        # Get all contacts
        contacts = Contact.query.all()
        
        # Track emails and phones we've seen
        seen_emails = {}
        seen_phones = {}
        
        # Track duplicates to remove
        duplicates = []
        
        # Generate an operation ID for this batch deletion
        operation_id = str(datetime.utcnow().timestamp())
        
        # Find duplicates
        for contact in contacts:
            is_duplicate = False
            
            # Check for duplicate email
            if contact.email and contact.email in seen_emails:
                is_duplicate = True
                
            # Check for duplicate phone
            if contact.cell and contact.cell in seen_phones:
                is_duplicate = True
                
            if is_duplicate:
                duplicates.append(contact)
            else:
                # Add to seen lists
                if contact.email:
                    seen_emails[contact.email] = contact.id
                if contact.cell:
                    seen_phones[contact.cell] = contact.id
        
        # If no duplicates found
        if not duplicates:
            session['success_message'] = "No duplicate contacts found."
            return redirect(url_for('main.dashboard'))
        
        # Store duplicates for undo functionality
        for contact in duplicates:
            contact_data = json.dumps(serialize_contact(contact))
            
            # Create a record in the DeletedContact table
            deleted_contact = DeletedContact(
                original_id=contact.id,
                contact_data=contact_data,
                deletion_type='duplicate',
                operation_id=operation_id
            )
            
            # Add the deleted contact record
            db.session.add(deleted_contact)
            
            # Delete the duplicate contact
            db.session.delete(contact)
        
        db.session.commit()
        
        session['success_message'] = f"Successfully removed {len(duplicates)} duplicate contacts."
        return redirect(url_for('main.dashboard', 
                              undo_action='duplicate', 
                              undo_id=operation_id))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error removing duplicates: {str(e)}"
        return redirect(url_for('main.dashboard'))

@contacts_bp.route('/bulk_delete_contacts', methods=['POST'])
def bulk_delete_contacts():
    """Delete multiple selected contacts"""
    try:
        # Get the list of contact IDs to delete
        contact_ids = request.form.getlist('contact_ids[]')
        
        if not contact_ids:
            session['error_message'] = "No contacts selected for deletion."
            return redirect(url_for('main.dashboard'))
        
        # Generate an operation ID for this batch deletion
        operation_id = str(datetime.utcnow().timestamp())
        
        # Delete each contact
        count = 0
        for contact_id in contact_ids:
            try:
                contact = Contact.query.get(contact_id)
                if contact:
                    # Store the contact data for undo functionality
                    contact_data = json.dumps(serialize_contact(contact))
                    
                    # Create a record in the DeletedContact table
                    deleted_contact = DeletedContact(
                        original_id=contact.id,
                        contact_data=contact_data,
                        deletion_type='bulk',
                        operation_id=operation_id
                    )
                    
                    # Add the deleted contact record
                    db.session.add(deleted_contact)
                    
                    # Delete the contact
                    db.session.delete(contact)
                    count += 1
            except Exception as e:
                # Continue with other contacts if one fails
                print(f"Error deleting contact {contact_id}: {str(e)}")
        
        db.session.commit()
        
        session['success_message'] = f"Successfully deleted {count} selected contacts."
        return redirect(url_for('main.dashboard', 
                              undo_action='bulk', 
                              undo_id=operation_id))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error deleting contacts: {str(e)}"
        return redirect(url_for('main.dashboard')) 