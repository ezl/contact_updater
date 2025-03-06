from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for, jsonify, session, send_file, make_response
import os
import pandas as pd
import json
import uuid
from datetime import datetime, timedelta
import io
from werkzeug.utils import secure_filename
import re
import csv
import holidays
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from dateutil.relativedelta import relativedelta
from flask_session import Session

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for flashing messages and sessions
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UNDO_EXPIRATION_MINUTES'] = 30  # How long undo actions are available
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'flask_session')

# Initialize session
Session(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Store rejected records in memory
rejected_records_store = {}

# Custom Jinja filter for formatting dates
@app.template_filter('format_date')
def format_date(date_str):
    if not date_str or date_str == '-':
        return '-'
    try:
        # Parse MM-DD format
        date_obj = datetime.strptime(date_str, '%m-%d')
        # Format as "Month Day"
        return date_obj.strftime('%b %-d')
    except ValueError:
        return date_str

# Define Contact model
class Contact(db.Model):
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

# Define DeletedContact model to store deleted contacts for undo functionality
class DeletedContact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_id = db.Column(db.Integer)  # Original ID of the contact
    contact_data = db.Column(db.Text)  # JSON string of contact data
    deletion_type = db.Column(db.String(20))  # 'single', 'all', or 'duplicate'
    deleted_at = db.Column(db.DateTime, default=datetime.utcnow)
    operation_id = db.Column(db.String(50))  # Group ID for batch operations

# Database setup is now handled by separate scripts
# See init_db.py to create tables and reset_db.py to reset the database

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
@app.route('/dashboard')
def dashboard():
    # Get messages from session
    success_message = session.pop('success_message', None)
    error_message = session.pop('error_message', None)
    
    # Check for HTML content in success message
    has_html = False
    if success_message and ('<' in success_message and '>' in success_message):
        has_html = True
    
    # Get undo parameters if present
    undo_action = request.args.get('undo_action')
    undo_id = request.args.get('undo_id')
    
    # Load contacts
    try:
        contacts = Contact.query.order_by(Contact.name).all()
    except Exception as e:
        contacts = []
        error_message = f"Error loading contacts: {str(e)}"
    
    return render_template('dashboard.html', 
                          contacts=contacts,
                          success_message=success_message,
                          error_message=error_message,
                          has_html=has_html,
                          undo_action=undo_action,
                          undo_id=undo_id)

# Helper function to serialize a contact to JSON
def serialize_contact(contact):
    contact_dict = {
        'original_id': contact.id,
        'name': contact.name,
        'cell': contact.cell,
        'email': contact.email,
        'mailing_address': contact.mailing_address,
        'notes': contact.notes,
        'birthday': contact.birthday,
        'facebook': contact.facebook,
        'instagram': contact.instagram,
        'twitter': contact.twitter
    }
    
    # Handle datetime objects
    if contact.email_updated:
        contact_dict['email_updated'] = contact.email_updated.isoformat()
    if contact.cell_updated:
        contact_dict['cell_updated'] = contact.cell_updated.isoformat()
    if contact.dateAdded:
        contact_dict['dateAdded'] = contact.dateAdded.isoformat()
    if contact.lastModified:
        contact_dict['lastModified'] = contact.lastModified.isoformat()
    
    return contact_dict

@app.route('/delete_contact/<int:id>', methods=['POST'])
def delete_contact(id):
    try:
        contact = Contact.query.get_or_404(id)
        
        # Serialize the contact data before deletion
        contact_data = serialize_contact(contact)
        
        # Create a unique operation ID for this deletion
        operation_id = str(datetime.utcnow().timestamp())
        
        # Store the deleted contact in the DeletedContact table
        deleted_contact = DeletedContact(
            original_id=contact.id,
            contact_data=json.dumps(contact_data),
            deletion_type='single',
            operation_id=operation_id
        )
        db.session.add(deleted_contact)
        
        # Delete the contact
        db.session.delete(contact)
        db.session.commit()
        
        # Set success message in session
        session['success_message'] = f"Successfully deleted {contact.name}."
        
        # Return to dashboard with success message and undo info
        return redirect(url_for('dashboard', undo_action='single', undo_id=deleted_contact.id))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error deleting contact: {str(e)}"
        return redirect(url_for('dashboard'))

@app.route('/download/sample_csv')
def download_sample():
    return send_from_directory('static', 'sample_contacts.csv')

@app.route('/remove_duplicates', methods=['POST'])
def remove_duplicates():
    try:
        # Get all contacts
        all_contacts = Contact.query.all()
        
        # Create a dictionary to track unique contacts by email and cell
        unique_emails = {}
        unique_cells = {}
        duplicates_removed = 0
        
        # Create an operation ID for this batch deletion
        operation_id = str(datetime.utcnow().timestamp())
        
        for contact in all_contacts:
            # Check for email duplicates (if email exists)
            if contact.email and contact.email.strip():
                email_key = contact.email.lower().strip()
                if email_key in unique_emails:
                    # This is a duplicate, store for potential undo
                    contact_data = serialize_contact(contact)
                    deleted_contact = DeletedContact(
                        original_id=contact.id,
                        contact_data=json.dumps(contact_data),
                        deletion_type='duplicate',
                        operation_id=operation_id
                    )
                    db.session.add(deleted_contact)
                    
                    # Mark for deletion
                    db.session.delete(contact)
                    duplicates_removed += 1
                    continue
                else:
                    unique_emails[email_key] = contact.id
            
            # If we get here and the contact has a cell number, check for cell duplicates
            if contact.cell and contact.cell.strip():
                # Normalize the cell number by removing non-digits
                cell_key = ''.join(filter(str.isdigit, contact.cell))
                if cell_key and cell_key in unique_cells:
                    # This is a duplicate, store for potential undo
                    contact_data = serialize_contact(contact)
                    deleted_contact = DeletedContact(
                        original_id=contact.id,
                        contact_data=json.dumps(contact_data),
                        deletion_type='duplicate',
                        operation_id=operation_id
                    )
                    db.session.add(deleted_contact)
                    
                    # Mark for deletion
                    db.session.delete(contact)
                    duplicates_removed += 1
                    continue
                else:
                    unique_cells[cell_key] = contact.id
        
        # Commit the changes to the database
        db.session.commit()
        
        if duplicates_removed > 0:
            success_message = f"Successfully removed {duplicates_removed} duplicate client(s)."
            return redirect(url_for('dashboard', 
                                   success_message=success_message,
                                   undo_action='duplicates',
                                   undo_id=operation_id))
        else:
            success_message = "No duplicate clients were found."
            return redirect(url_for('dashboard', success_message=success_message))
    
    except Exception as e:
        db.session.rollback()
        error_message = f"Error removing duplicates: {str(e)}"
        return redirect(url_for('dashboard', error_message=error_message))

@app.route('/delete_all_contacts', methods=['POST'])
def delete_all_contacts():
    try:
        # Get all contacts
        contacts = Contact.query.all()
        
        if not contacts:
            session['error_message'] = "No contacts to delete."
            return redirect(url_for('dashboard'))
        
        # Create a unique operation ID for this batch deletion
        operation_id = str(datetime.utcnow().timestamp())
        
        # Store each contact in the DeletedContact table
        for contact in contacts:
            contact_data = serialize_contact(contact)
            deleted_contact = DeletedContact(
                original_id=contact.id,
                contact_data=json.dumps(contact_data),
                deletion_type='all',
                operation_id=operation_id
            )
            db.session.add(deleted_contact)
        
        # Delete all contacts
        count = len(contacts)
        Contact.query.delete()
        db.session.commit()
        
        # Set success message in session
        session['success_message'] = f"Successfully deleted all {count} clients from the database."
        
        # Return to dashboard with success message and undo info
        return redirect(url_for('dashboard', undo_action='all', undo_id=operation_id))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error deleting all contacts: {str(e)}"
        return redirect(url_for('dashboard'))

# Add routes for undoing deletions
@app.route('/undo_delete/<string:action>/<string:id>')
def undo_delete(action, id):
    try:
        if action == 'single':
            # Restore a single deleted contact
            deleted_contact = DeletedContact.query.get_or_404(id)
            contact_data = json.loads(deleted_contact.contact_data)
            
            # Create a new contact with the original data
            new_contact = Contact(
                name=contact_data.get('name', ''),
                email=contact_data.get('email', ''),
                cell=contact_data.get('cell', ''),
                mailing_address=contact_data.get('mailing_address', ''),
                birthday=parse_date(contact_data.get('birthday', None)),
                email_updated=parse_date(contact_data.get('email_updated', None)),
                cell_updated=parse_date(contact_data.get('cell_updated', None))
            )
            
            db.session.add(new_contact)
            db.session.delete(deleted_contact)
            db.session.commit()
            
            session['success_message'] = f"Successfully restored {new_contact.name}."
            
        elif action == 'all':
            # Restore all contacts from a batch deletion
            operation_id = id
            deleted_contacts = DeletedContact.query.filter_by(operation_id=operation_id).all()
            
            if not deleted_contacts:
                session['error_message'] = "No contacts found to restore."
                return redirect(url_for('dashboard'))
            
            restored_count = 0
            for deleted_contact in deleted_contacts:
                contact_data = json.loads(deleted_contact.contact_data)
                
                # Create a new contact with the original data
                new_contact = Contact(
                    name=contact_data.get('name', ''),
                    email=contact_data.get('email', ''),
                    cell=contact_data.get('cell', ''),
                    mailing_address=contact_data.get('mailing_address', ''),
                    birthday=parse_date(contact_data.get('birthday', None)),
                    email_updated=parse_date(contact_data.get('email_updated', None)),
                    cell_updated=parse_date(contact_data.get('cell_updated', None))
                )
                
                db.session.add(new_contact)
                db.session.delete(deleted_contact)
                restored_count += 1
            
            db.session.commit()
            
            session['success_message'] = f"Successfully restored {restored_count} clients."
            
        else:
            session['error_message'] = "Invalid undo action."
            
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        session['error_message'] = f"Error restoring contact(s): {str(e)}"
        return redirect(url_for('dashboard'))

# Cleanup expired deleted contacts
@app.before_request
def cleanup_deleted_contacts():
    try:
        # Calculate the expiration time
        expiration_time = datetime.utcnow() - timedelta(minutes=app.config['UNDO_EXPIRATION_MINUTES'])
        
        # Delete expired records
        DeletedContact.query.filter(DeletedContact.deleted_at < expiration_time).delete()
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/add_contact', methods=['POST'])
def add_contact():
    try:
        # Extract contact data from form
        contact_data = {
            'name': request.form.get('name', ''),
            'cell': request.form.get('cell', ''),
            'email': request.form.get('email', ''),
            'mailing_address': request.form.get('mailing_address', ''),
            'notes': request.form.get('notes', ''),
            'facebook': request.form.get('facebook', ''),
            'instagram': request.form.get('instagram', ''),
            'twitter': request.form.get('twitter', '')
        }
        
        # Handle birthday field - ensure it's in MM-DD format
        birthday = request.form.get('birthday', '')
        if birthday:
            try:
                # Try to parse the date in various formats
                date_obj = datetime.strptime(birthday, '%Y-%m-%d')
                contact_data['birthday'] = date_obj.strftime('%m-%d')
            except ValueError:
                try:
                    # Try MM-DD format
                    datetime.strptime(birthday, '%m-%d')
                    contact_data['birthday'] = birthday
                except ValueError:
                    try:
                        # Try flexible parsing
                        date_obj = pd.to_datetime(birthday)
                        contact_data['birthday'] = date_obj.strftime('%m-%d')
                    except:
                        # If all parsing fails, don't include the birthday
                        pass
        
        # Create and save the new contact
        new_contact = Contact(**contact_data)
        
        # Set update timestamps for fields that have values
        now = datetime.utcnow()
        if contact_data['email']:
            new_contact.email_updated = now
        if contact_data['cell']:
            new_contact.cell_updated = now
        if contact_data['mailing_address']:
            new_contact.mailing_address_updated = now
            
        db.session.add(new_contact)
        db.session.commit()
        
        success_message = f"Client '{contact_data['name']}' added successfully!"
        return redirect(url_for('dashboard', success_message=success_message))
    
    except Exception as e:
        db.session.rollback()
        error_message = f"Error adding contact: {str(e)}"
        return redirect(url_for('dashboard', error_message=error_message))

@app.route('/update_contact/<int:id>', methods=['POST'])
def update_contact(id):
    try:
        # Get the contact
        contact = Contact.query.get_or_404(id)
        
        # Get the data from the request
        data = request.json
        field = data.get('field')
        value = data.get('value')
        
        # Validate the field
        allowed_fields = ['name', 'cell', 'email', 'mailing_address', 'notes', 
                          'birthday', 'facebook', 'instagram', 'twitter']
        
        if field not in allowed_fields:
            return jsonify({'success': False, 'message': 'Invalid field'}), 400
        
        # Update the field
        setattr(contact, field, value)
        
        # Update timestamp fields if applicable
        updated_timestamp = None
        if field == 'email':
            contact.email_updated = datetime.utcnow()
            updated_timestamp = contact.email_updated
        elif field == 'cell':
            contact.cell_updated = datetime.utcnow()
            updated_timestamp = contact.cell_updated
        elif field == 'mailing_address':
            contact.mailing_address_updated = datetime.utcnow()
            updated_timestamp = contact.mailing_address_updated
        
        # Save the changes
        db.session.commit()
        
        response_data = {
            'success': True, 
            'message': 'Client updated successfully',
            'field': field,
            'value': value
        }
        
        # Add the updated timestamp to the response if applicable
        if updated_timestamp:
            response_data['updated_timestamp'] = updated_timestamp.strftime('%Y-%m-%d %H:%M:%S')
            response_data['updated_field'] = field
        
        return jsonify(response_data)
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Custom filter for formatting dates in templates
@app.template_filter('date')
def format_date(value):
    if value:
        return value.strftime('%Y-%m-%d')
    return ''

# Custom filter to format birthday from MM-DD to Month Day
@app.template_filter('formatBirthday')
def format_birthday(value):
    if value:
        try:
            # Parse the MM-DD string
            date_obj = datetime.strptime(value, '%m-%d')
            # Format to Month Day with 3-letter abbreviation (e.g., "May 15")
            return date_obj.strftime('%b %d')
        except ValueError:
            try:
                # Try alternate format (for backward compatibility)
                if len(value) > 5 and '-' in value:
                    date_obj = datetime.strptime(value, '%Y-%m-%d')
                    return date_obj.strftime('%b %d')
                return value
            except:
                # Return as is if all parsing fails
                return value
    return 'N/A'

@app.route('/get_contact/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Format dates for JSON serialization
        date_added = contact.dateAdded.strftime('%Y-%m-%d %H:%M:%S') if contact.dateAdded else None
        email_updated = contact.email_updated.strftime('%Y-%m-%d %H:%M:%S') if contact.email_updated else None
        cell_updated = contact.cell_updated.strftime('%Y-%m-%d %H:%M:%S') if contact.cell_updated else None
        mailing_address_updated = contact.mailing_address_updated.strftime('%Y-%m-%d %H:%M:%S') if contact.mailing_address_updated else None
        
        # Create a dictionary with all contact fields
        contact_data = {
            'id': contact.id,
            'name': contact.name,
            'cell': contact.cell,
            'email': contact.email,
            'mailing_address': contact.mailing_address,
            'notes': contact.notes,
            'birthday': contact.birthday,
            'dateAdded': date_added,
            'email_updated': email_updated,
            'cell_updated': cell_updated,
            'mailing_address_updated': mailing_address_updated,
            'facebook': contact.facebook,
            'instagram': contact.instagram,
            'twitter': contact.twitter
        }
        
        return jsonify(contact_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_all_contacts', methods=['GET'])
def download_all_contacts():
    try:
        # Get all contacts
        contacts = Contact.query.order_by(Contact.name).all()
        
        if not contacts:
            return redirect(url_for('dashboard', error_message="No contacts to download"))
        
        # Create a DataFrame from the contacts
        data = []
        for contact in contacts:
            contact_dict = {
                'name': contact.name,
                'cell': contact.cell,
                'email': contact.email,
                'mailing_address': contact.mailing_address,
                'notes': contact.notes,
                'birthday': contact.birthday,
                'facebook': contact.facebook,
                'instagram': contact.instagram,
                'twitter': contact.twitter
            }
            data.append(contact_dict)
        
        df = pd.DataFrame(data)
        
        # Create a temporary file to store the CSV
        temp_file = os.path.join(app.config['UPLOAD_FOLDER'], 'contacts_export.csv')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Write the DataFrame to CSV
        df.to_csv(temp_file, index=False)
        
        # Return the file as an attachment
        return send_from_directory(
            app.config['UPLOAD_FOLDER'],
            'contacts_export.csv',
            as_attachment=True,
            download_name=f'contacts_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        error_message = f"Error downloading contacts: {str(e)}"
        return redirect(url_for('dashboard', error_message=error_message))

@app.route('/events', methods=['GET'])
def events():
    # Get all contacts
    try:
        contacts = Contact.query.all()
    except Exception as e:
        error_message = f"Error loading contacts: {str(e)}"
        contacts = []
    
    # Get current date
    current_date = datetime.now()
    
    # Create a list of the next 12 months
    months = []
    for i in range(12):
        month_date = current_date.replace(day=1) + relativedelta(months=i)
        month_name = month_date.strftime("%B %Y")
        month_number = month_date.month
        
        # Get contacts with birthdays in this month
        month_birthdays = []
        for contact in contacts:
            if contact.birthday and len(contact.birthday) == 5:  # MM-DD format
                try:
                    birthday_month = int(contact.birthday.split('-')[0])
                    birthday_day = int(contact.birthday.split('-')[1])
                    if birthday_month == month_number:
                        month_birthdays.append({
                            'contact': contact,
                            'day': birthday_day
                        })
                except (ValueError, IndexError):
                    # Skip invalid birthday formats
                    continue
        
        # Sort birthdays by day
        month_birthdays.sort(key=lambda x: x['day'])
        
        # Get holidays for this month
        holidays = get_holidays_for_month(month_number, month_date.year)
        
        months.append({
            'name': month_name,
            'number': month_number,
            'year': month_date.year,
            'birthdays': month_birthdays,
            'holidays': holidays
        })
    
    return render_template('events.html', months=months)

def get_holidays_for_month(month, year):
    """Get common holidays for a specific month and year."""
    holidays = []
    
    # US Holidays
    if month == 1:  # January
        holidays.append({'name': "New Year's Day", 'date': f"01-01-{year}"})
        holidays.append({'name': "Martin Luther King Jr. Day", 'date': f"Third Monday of January {year}"})
    elif month == 2:  # February
        holidays.append({'name': "Valentine's Day", 'date': f"02-14-{year}"})
        holidays.append({'name': "Presidents' Day", 'date': f"Third Monday of February {year}"})
    elif month == 3:  # March
        holidays.append({'name': "St. Patrick's Day", 'date': f"03-17-{year}"})
    elif month == 4:  # April
        holidays.append({'name': "Earth Day", 'date': f"04-22-{year}"})
    elif month == 5:  # May
        holidays.append({'name': "Memorial Day", 'date': f"Last Monday of May {year}"})
        holidays.append({'name': "Mother's Day", 'date': f"Second Sunday of May {year}"})
    elif month == 6:  # June
        holidays.append({'name': "Father's Day", 'date': f"Third Sunday of June {year}"})
        holidays.append({'name': "Juneteenth", 'date': f"06-19-{year}"})
    elif month == 7:  # July
        holidays.append({'name': "Independence Day", 'date': f"07-04-{year}"})
    elif month == 9:  # September
        holidays.append({'name': "Labor Day", 'date': f"First Monday of September {year}"})
    elif month == 10:  # October
        holidays.append({'name': "Halloween", 'date': f"10-31-{year}"})
        holidays.append({'name': "Columbus Day", 'date': f"Second Monday of October {year}"})
    elif month == 11:  # November
        holidays.append({'name': "Veterans Day", 'date': f"11-11-{year}"})
        holidays.append({'name': "Thanksgiving", 'date': f"Fourth Thursday of November {year}"})
    elif month == 12:  # December
        holidays.append({'name': "Christmas", 'date': f"12-25-{year}"})
        holidays.append({'name': "New Year's Eve", 'date': f"12-31-{year}"})
    
    return holidays

@app.route('/bulk_delete_contacts', methods=['POST'])
def bulk_delete_contacts():
    try:
        # Get the list of contact IDs to delete
        contact_ids = request.form.getlist('contact_ids')
        
        if not contact_ids:
            flash('No contacts selected for deletion.', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate a unique operation ID for this bulk deletion
        operation_id = str(datetime.utcnow().timestamp())
        deleted_count = 0
        
        for contact_id in contact_ids:
            try:
                contact_id = int(contact_id)
                contact = Contact.query.get(contact_id)
                
                if contact:
                    # Store the contact data for potential undo
                    contact_data = serialize_contact(contact)
                    
                    # Create a DeletedContact record
                    deleted_contact = DeletedContact(
                        original_id=contact.id,
                        contact_data=json.dumps(contact_data),
                        deletion_type='bulk',
                        operation_id=operation_id
                    )
                    db.session.add(deleted_contact)
                    
                    # Delete the contact
                    db.session.delete(contact)
                    deleted_count += 1
            except Exception as e:
                app.logger.error(f"Error deleting contact {contact_id}: {str(e)}")
                continue
        
        db.session.commit()
        
        success_message = f"{deleted_count} contact(s) deleted successfully!"
        return redirect(url_for('dashboard', 
                               success_message=success_message,
                               undo_action='bulk',
                               undo_id=operation_id))
    except Exception as e:
        db.session.rollback()
        error_message = f"Error deleting contacts: {str(e)}"
        flash(error_message, 'error')
        return redirect(url_for('dashboard'))

@app.route('/download_rejected_records', methods=['GET'])
def download_rejected_records():
    """Download the CSV file containing rejected records from the last import."""
    rejected_id = request.args.get('rejected_id')
    
    if rejected_id and rejected_id in rejected_records_store:
        rejected_rows = rejected_records_store[rejected_id]
        
        # Create a CSV in memory
        output = io.StringIO()
        if rejected_rows:
            # Get the fieldnames from the first row
            fieldnames = rejected_rows[0].keys()
            
            # Create a CSV writer
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write all rows
            for row in rejected_rows:
                writer.writerow(row)
            
            # Reset the pointer to the beginning of the StringIO object
            output.seek(0)
            
            # Create a response with the CSV data
            response = make_response(output.getvalue())
            response.headers["Content-Disposition"] = f"attachment; filename=rejected_records.csv"
            response.headers["Content-type"] = "text/csv"
            
            return response
        else:
            session['error_message'] = "No rejected records to download."
            return redirect(url_for('dashboard'))
    else:
        session['error_message'] = "No rejected records found or invalid ID."
        return redirect(url_for('dashboard'))

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'csv_file' not in request.files:
        session['error_message'] = "No file part in the request"
        return redirect(url_for('dashboard'))
    
    file = request.files['csv_file']
    
    # If user does not select file, browser may submit an empty file without filename
    if file.filename == '':
        session['error_message'] = "No file selected"
        return redirect(url_for('dashboard'))
    
    if file and allowed_file(file.filename):
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Log the first 3 rows of the CSV
            print("======= CSV DATA (FIRST 3 ROWS) =======")
            print(df.head(3))
            print("========================================")
            
            # Track processed and rejected rows
            rows_processed = 0
            rejected_rows = []
            
            # Process each row in the CSV
            for index, row in df.iterrows():
                # Clean and prepare data
                contact_data = {}
                
                # Map CSV columns to database fields
                field_mapping = {
                    'name': 'name',
                    'cell': 'cell',
                    'email': 'email',
                    'mailing_address': 'mailing_address',
                    'notes': 'notes',
                    'birthday': 'birthday',
                    'email_updated': 'email_updated',
                    'cell_updated': 'cell_updated',
                    'facebook': 'facebook',
                    'instagram': 'instagram',
                    'twitter': 'twitter'
                }
                
                # Count valid fields
                valid_field_count = 0
                valid_fields = []
                
                # Process each field if it exists in the CSV
                for csv_field, db_field in field_mapping.items():
                    if csv_field in row and not pd.isna(row[csv_field]) and str(row[csv_field]).strip():
                        valid_field_count += 1
                        valid_fields.append(csv_field)
                        
                        # Handle date fields
                        if csv_field in ['email_updated', 'cell_updated'] and row[csv_field]:
                            try:
                                # Try to parse the date string
                                contact_data[db_field] = datetime.strptime(str(row[csv_field]), '%Y-%m-%d')
                            except ValueError:
                                # If parsing fails, leave as None
                                pass
                        # Special handling for birthday to store only month and day
                        elif csv_field == 'birthday' and row[csv_field]:
                            try:
                                # Check if it's in YYYY-MM-DD format
                                if len(str(row[csv_field])) > 5:
                                    # Parse the full date and extract just month and day
                                    full_date = datetime.strptime(str(row[csv_field]), '%Y-%m-%d')
                                    contact_data[db_field] = full_date.strftime('%m-%d')
                                # Check if it's already in MM-DD format
                                elif len(str(row[csv_field])) == 5 and '-' in str(row[csv_field]):
                                    # Validate that it's a proper MM-DD format
                                    datetime.strptime(str(row[csv_field]), '%m-%d')
                                    contact_data[db_field] = str(row[csv_field])
                                else:
                                    # Try to parse in flexible format, but store as MM-DD
                                    try:
                                        date_obj = pd.to_datetime(str(row[csv_field]))
                                        contact_data[db_field] = date_obj.strftime('%m-%d')
                                    except:
                                        # If all parsing fails, skip this field
                                        print(f"Skipping invalid birthday format: {row[csv_field]}")
                            except (ValueError, AttributeError) as e:
                                print(f"Error processing birthday: {e}")
                            
                            if db_field in contact_data:
                                print(f"Importing {csv_field}: {row[csv_field]} → {contact_data[db_field]} (MM-DD)")
                        else:
                            contact_data[db_field] = str(row[csv_field])
                            print(f"Importing {csv_field}: {row[csv_field]}")
                
                # Check if we have at least 3 valid fields
                if valid_field_count >= 3:
                    # Create the contact record
                    contact = Contact(**contact_data)
                    db.session.add(contact)
                    rows_processed += 1
                    print(f"Row {index}: ACCEPTED - {valid_field_count} valid fields: {', '.join(valid_fields)}")
                else:
                    # Add to rejected rows
                    rejected_rows.append(row.to_dict())
                    print(f"Row {index}: REJECTED - Only {valid_field_count} valid fields: {', '.join(valid_fields)}")
            
            # Commit all changes to the database
            db.session.commit()
            
            # Store rejected rows in memory if any exist
            if rejected_rows:
                # Generate a unique ID for this set of rejected records
                rejected_id = str(uuid.uuid4())
                rejected_records_store[rejected_id] = rejected_rows
                
                # Create a success message with errors
                session['success_message'] = f"Successfully imported {rows_processed} clients. Were unable to import some. <a href=\"{url_for('download_rejected_records', rejected_id=rejected_id)}\" class=\"underline font-medium\">View errors</a>."
            else:
                # Simple success message with no errors
                session['success_message'] = f"Successfully imported {rows_processed} clients."
            
            print(f"Import summary: {rows_processed} records imported, {len(rejected_rows)} records rejected")
            
            # Redirect to dashboard to show the updated page with success message
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            session['error_message'] = f"Error processing CSV file: {str(e)}"
            return redirect(url_for('dashboard'))
    else:
        # Provide a clear error message for non-CSV files
        session['error_message'] = f"Invalid file type: {file.filename}. Only CSV files are supported."
        return redirect(url_for('dashboard'))

@app.route('/upload/error', methods=['POST'])
@csrf.exempt
def upload_error():
    """Handle error messages for file uploads from the client side."""
    data = request.json
    if data and 'error_message' in data:
        session['error_message'] = data['error_message']
    return jsonify({'status': 'success'})

@app.route('/debug_session')
def debug_session():
    """Debug route to check session contents."""
    session['test_message'] = "This is a test message"
    return jsonify({
        'session_contents': dict(session),
        'session_id': session.sid if hasattr(session, 'sid') else None
    })

if __name__ == '__main__':
    # Make sure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
    app.run(debug=True) 