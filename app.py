from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for, jsonify, session
import os
import pandas as pd
import json
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UNDO_EXPIRATION_MINUTES'] = 30  # How long undo actions are available

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

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
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    success_message = request.args.get('success_message')
    error_message = request.args.get('error_message')
    undo_action = request.args.get('undo_action')
    undo_id = request.args.get('undo_id')
    
    # Get all contacts
    try:
        contacts = Contact.query.order_by(Contact.name).all()
    except Exception as e:
        error_message = f"Error loading contacts: {str(e)}"
        contacts = []
    
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'csv_file' not in request.files:
            error_message = "No file part in the request"
            return render_template('dashboard.html', 
                                  contacts=contacts, 
                                  success_message=success_message,
                                  error_message=error_message)
        
        file = request.files['csv_file']
        
        # If user does not select file, browser may submit an empty file without filename
        if file.filename == '':
            error_message = "No file selected"
            return render_template('dashboard.html', 
                                  contacts=contacts, 
                                  success_message=success_message,
                                  error_message=error_message)
        
        if file and allowed_file(file.filename):
            try:
                # Read the CSV file
                df = pd.read_csv(file)
                
                # Log the first 3 rows of the CSV
                print("======= CSV DATA (FIRST 3 ROWS) =======")
                print(df.head(3))
                print("========================================")
                
                # Process each row in the CSV
                rows_processed = 0
                for _, row in df.iterrows():
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
                    
                    # Process each field if it exists in the CSV
                    for csv_field, db_field in field_mapping.items():
                        if csv_field in row and not pd.isna(row[csv_field]):
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
                    
                    # Create the contact record
                    contact = Contact(**contact_data)
                    db.session.add(contact)
                    rows_processed += 1
                
                # Commit all changes to the database
                db.session.commit()
                
                success_message = f"Successfully processed {rows_processed} contacts from the CSV file."
                
                # Refresh contacts list
                contacts = Contact.query.order_by(Contact.name).all()
            except Exception as e:
                db.session.rollback()
                error_message = f"Error processing CSV file: {str(e)}"
        else:
            error_message = "File type not allowed. Please upload a CSV file."
        
    return render_template('dashboard.html', 
                          contacts=contacts, 
                          success_message=success_message,
                          error_message=error_message,
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
        # Get the contact
        contact = Contact.query.get_or_404(id)
        
        # Store the contact data for potential undo
        contact_data = serialize_contact(contact)
        
        # Create a DeletedContact record
        deleted_contact = DeletedContact(
            original_id=contact.id,
            contact_data=json.dumps(contact_data),
            deletion_type='single',
            operation_id=str(datetime.utcnow().timestamp())
        )
        db.session.add(deleted_contact)
        
        # Delete the contact
        db.session.delete(contact)
        db.session.commit()
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'message': 'Contact deleted successfully!'
            })
        
        # For regular form submissions, redirect with undo parameters
        success_message = "Contact deleted successfully!"
        return redirect(url_for('dashboard', 
                               success_message=success_message,
                               undo_action='single',
                               undo_id=deleted_contact.id))
    except Exception as e:
        db.session.rollback()
        error_message = f"Error deleting contact: {str(e)}"
        
        # Check if this is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': error_message
            })
        
        return redirect(url_for('dashboard', error_message=error_message))

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
            success_message = f"Successfully removed {duplicates_removed} duplicate contact(s)."
            return redirect(url_for('dashboard', 
                                   success_message=success_message,
                                   undo_action='duplicates',
                                   undo_id=operation_id))
        else:
            success_message = "No duplicate contacts were found."
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
        contact_count = len(contacts)
        
        if contact_count > 0:
            # Create an operation ID for this batch deletion
            operation_id = str(datetime.utcnow().timestamp())
            
            # Store all contacts for potential undo
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
            Contact.query.delete()
            
            # Commit the changes to the database
            db.session.commit()
            
            success_message = f"Successfully deleted all {contact_count} contacts from the database."
            return redirect(url_for('dashboard', 
                                   success_message=success_message,
                                   undo_action='all',
                                   undo_id=operation_id))
        else:
            success_message = "No contacts to delete."
            return redirect(url_for('dashboard', success_message=success_message))
    
    except Exception as e:
        db.session.rollback()
        error_message = f"Error deleting all contacts: {str(e)}"
        return redirect(url_for('dashboard', error_message=error_message))

# Add routes for undoing deletions
@app.route('/undo_delete/<string:action>/<string:id>', methods=['POST'])
def undo_delete(action, id):
    try:
        if action == 'single':
            # Restore a single deleted contact
            deleted_contact = DeletedContact.query.get_or_404(id)
            contact_data = json.loads(deleted_contact.contact_data)
            
            # Remove fields that shouldn't be directly set
            original_id = contact_data.pop('original_id', None)
            contact_data.pop('dateAdded', None)
            contact_data.pop('lastModified', None)
            
            # Convert ISO format dates back to datetime objects
            if 'email_updated' in contact_data and contact_data['email_updated']:
                contact_data['email_updated'] = datetime.fromisoformat(contact_data['email_updated'])
            if 'cell_updated' in contact_data and contact_data['cell_updated']:
                contact_data['cell_updated'] = datetime.fromisoformat(contact_data['cell_updated'])
            
            # Create a new contact with the original data
            new_contact = Contact(**contact_data)
            db.session.add(new_contact)
            
            # Delete the DeletedContact record
            db.session.delete(deleted_contact)
            db.session.commit()
            
            success_message = "Contact restored successfully!"
            
        elif action in ['all', 'duplicates']:
            # Restore all contacts from a batch operation
            deleted_contacts = DeletedContact.query.filter_by(operation_id=id).all()
            
            if not deleted_contacts:
                return redirect(url_for('dashboard', error_message="No contacts found to restore."))
            
            # Restore each contact
            restored_count = 0
            for deleted_contact in deleted_contacts:
                contact_data = json.loads(deleted_contact.contact_data)
                
                # Remove fields that shouldn't be directly set
                original_id = contact_data.pop('original_id', None)
                contact_data.pop('dateAdded', None)
                contact_data.pop('lastModified', None)
                
                # Convert ISO format dates back to datetime objects
                if 'email_updated' in contact_data and contact_data['email_updated']:
                    contact_data['email_updated'] = datetime.fromisoformat(contact_data['email_updated'])
                if 'cell_updated' in contact_data and contact_data['cell_updated']:
                    contact_data['cell_updated'] = datetime.fromisoformat(contact_data['cell_updated'])
                
                # Create a new contact with the original data
                new_contact = Contact(**contact_data)
                db.session.add(new_contact)
                
                # Delete the DeletedContact record
                db.session.delete(deleted_contact)
                restored_count += 1
            
            db.session.commit()
            
            action_type = "all contacts" if action == 'all' else "duplicate contacts"
            success_message = f"Successfully restored {restored_count} {action_type}!"
            
        else:
            return redirect(url_for('dashboard', error_message="Invalid undo action."))
        
        return redirect(url_for('dashboard', success_message=success_message))
    
    except Exception as e:
        db.session.rollback()
        error_message = f"Error restoring contact(s): {str(e)}"
        return redirect(url_for('dashboard', error_message=error_message))

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
        db.session.add(new_contact)
        db.session.commit()
        
        success_message = "Contact added successfully!"
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
        if field == 'email':
            contact.email_updated = datetime.utcnow()
        elif field == 'cell':
            contact.cell_updated = datetime.utcnow()
        
        # Save the changes
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Contact updated successfully',
            'field': field,
            'value': value
        })
    
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

if __name__ == '__main__':
    # Make sure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
    app.run(debug=True) 