from flask import Blueprint, request, redirect, url_for, session, send_file, make_response, jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import csv
import io
import uuid
import os
from datetime import datetime
from app import db, csrf
from app.models import Contact
from app.utils.helpers import allowed_file, rejected_records_store

file_ops_bp = Blueprint('file_ops', __name__)

def process_csv_file(file):
    """
    Process a CSV file and return the results.
    Returns a tuple of (success, message, status_code)
    """
    try:
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        print("Starting CSV import...")
        csv_reader = csv.reader(stream, quoting=csv.QUOTE_MINIMAL, skipinitialspace=True)
        
        # Skip header row if it exists
        header = next(csv_reader, None)
        print(f"Header row: {header}")
        if not header:
            return False, "Empty CSV file", 400
        
        # Define field names based on header or default names
        fieldnames = header or ['name', 'cell', 'email', 'mailing_address', 'notes', 'birthday', 'facebook', 'instagram', 'twitter']
        
        # Track processed and rejected rows
        rows_processed = 0
        rejected_rows = []
        
        # Process each row in the CSV
        for index, row in enumerate(csv_reader):
            try:
                print(f"Processing row: {row}")
                # Skip empty rows
                if not row or not any(row):
                    print("Skipping empty row")
                    continue
                
                # Get raw values first for debugging
                raw_values = dict(zip(fieldnames, row))
                print(f"\nProcessing row {index}:")
                print("Raw values:", raw_values)
                
                # Map CSV fields to database fields with stricter validation
                contact_data = {
                    'name': str(row[0]).strip() if len(row) > 0 else '',
                    'cell': str(row[1]).strip() if len(row) > 1 else '',
                    'email': str(row[2]).strip() if len(row) > 2 else '',
                    'mailing_address': str(row[3]).strip() if len(row) > 3 else '',
                    'notes': str(row[4]).strip() if len(row) > 4 else '',
                    'birthday': str(row[5]).strip() if len(row) > 5 else '',
                    'facebook': str(row[6]).strip() if len(row) > 6 else '',
                    'instagram': str(row[7]).strip() if len(row) > 7 else '',
                    'twitter': str(row[8]).strip() if len(row) > 8 else ''
                }
                
                # Replace 'nan' strings with empty strings
                contact_data = {k: '' if v.lower() == 'nan' else v for k, v in contact_data.items()}
                
                # Print mapped values for debugging
                print("Mapped values:")
                for field, value in contact_data.items():
                    print(f"  {field}: '{value}'")
                
                # Count non-empty fields
                non_empty_fields = [k for k, v in contact_data.items() if v]
                
                # Name is required, plus at least one other field
                if contact_data['name'] and len(non_empty_fields) > 1:
                    # Format birthday if provided
                    if contact_data['birthday']:
                        try:
                            for fmt in ['%d-%b', '%m/%d/%Y', '%Y-%m-%d', '%m-%d']:
                                try:
                                    date_obj = datetime.strptime(contact_data['birthday'], fmt)
                                    contact_data['birthday'] = date_obj.strftime('%m-%d')
                                    print(f"  Formatted birthday: {contact_data['birthday']}")
                                    break
                                except ValueError:
                                    continue
                        except Exception as e:
                            print(f"  Error formatting birthday: {str(e)}")
                    
                    # Create new contact
                    new_contact = Contact(**contact_data)
                    
                    # Add to database
                    db.session.add(new_contact)
                    rows_processed += 1
                    print(f"Row {index}: ACCEPTED - Fields: {', '.join(non_empty_fields)}")
                else:
                    reason = "Missing name" if not contact_data['name'] else "Insufficient fields"
                    print(f"Row {index}: REJECTED - {reason}")
                    rejected_rows.append(raw_values)
            
            except Exception as e:
                print(f"Error processing row {index}: {str(e)}")
                rejected_rows.append(dict(zip(fieldnames, row)))
        
        # Commit changes to database
        db.session.commit()
        
        # Create success message
        if rejected_rows:
            rejected_id = str(uuid.uuid4())
            rejected_records_store[rejected_id] = rejected_rows
            message = {
                'success': True,
                'message': f"Successfully imported {rows_processed} contacts. Some records were rejected.",
                'rejected_id': rejected_id,
                'has_html': True
            }
        else:
            message = {
                'success': True,
                'message': f"Successfully imported {rows_processed} contacts."
            }
        
        print(f"\nImport summary:")
        print(f"- Processed: {rows_processed}")
        print(f"- Rejected: {len(rejected_rows)}")
        
        return True, message, 200
        
    except Exception as e:
        db.session.rollback()
        error_message = f"Error processing CSV file: {str(e)}"
        print(error_message)
        return False, error_message, 500

@file_ops_bp.route('/upload', methods=['POST'])
@csrf.exempt  # Temporarily disable CSRF for testing
def upload_file():
    """Handle CSV file upload and import"""
    if 'csv_file' not in request.files:
        return jsonify({'success': False, 'message': "No file part in the request"}), 400
    
    file = request.files['csv_file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': "No file selected"}), 400
    
    if not file or not allowed_file(file.filename):
        return jsonify({'success': False, 'message': f"Invalid file type: {file.filename}. Only CSV files are supported."}), 400
    
    success, message, status_code = process_csv_file(file)
    
    if isinstance(message, dict):
        # Store success message in session for the redirect
        session['success_message'] = message['message']
        if message.get('has_html'):
            session['has_html'] = True
            # Add the rejected records link to the message
            rejected_url = url_for('file_ops.download_rejected_records', rejected_id=message['rejected_id'])
            session['success_message'] += f" <a href=\"{rejected_url}\" class=\"underline font-medium\">View rejected records</a>."
    else:
        # Store error message in session for the redirect
        session['error_message'] = message
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # For AJAX requests (drag and drop), return JSON
        return jsonify({
            'success': success,
            'message': message,
            'redirect': url_for('main.dashboard')
        }), status_code
    else:
        # For form submissions, redirect
        return redirect(url_for('main.dashboard'))

@file_ops_bp.route('/upload/error', methods=['POST'])
@csrf.exempt
def upload_error():
    """Handle error messages for file uploads from the client side"""
    data = request.json
    if data and 'error_message' in data:
        session['error_message'] = data['error_message']
    return jsonify({'status': 'success'})

@file_ops_bp.route('/download_rejected_records', methods=['GET'])
def download_rejected_records():
    """Download rejected records as a CSV file"""
    # Get the rejected ID from the request
    rejected_id = request.args.get('rejected_id')
    
    # Check if the rejected ID exists in the store
    if rejected_id and rejected_id in rejected_records_store:
        try:
            # Get the rejected rows
            rejected_rows = rejected_records_store[rejected_id]
            
            # Create a CSV in memory
            output = io.StringIO()
            
            # Write the CSV header and rows
            if rejected_rows:
                fieldnames = rejected_rows[0].keys()
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rejected_rows)
            
            # Create a response with the CSV
            output.seek(0)
            response = make_response(output.getvalue())
            response.headers['Content-Disposition'] = 'attachment; filename=rejected_records.csv'
            response.headers['Content-type'] = 'text/csv'
            
            return response
        except Exception as e:
            session['error_message'] = f"Error generating rejected records file: {str(e)}"
            return redirect(url_for('main.dashboard'))
    else:
        session['error_message'] = "No rejected records found or invalid ID."
        return redirect(url_for('main.dashboard'))

@file_ops_bp.route('/download_all_contacts', methods=['GET'])
def download_all_contacts():
    """Download all contacts as a CSV file"""
    try:
        # Get all contacts
        contacts = Contact.query.all()
        
        # Create a CSV in memory
        output = io.StringIO()
        
        # Define the CSV fields
        fieldnames = ['name', 'cell', 'email', 'mailing_address', 'notes', 'birthday', 
                     'facebook', 'instagram', 'twitter', 'email_updated', 'cell_updated', 
                     'mailing_address_updated', 'dateAdded', 'lastModified']
        
        # Write the CSV header and rows
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for contact in contacts:
            # Convert contact to dictionary
            contact_dict = {
                'name': contact.name,
                'cell': contact.cell,
                'email': contact.email,
                'mailing_address': contact.mailing_address,
                'notes': contact.notes,
                'birthday': contact.birthday,
                'facebook': contact.facebook,
                'instagram': contact.instagram,
                'twitter': contact.twitter,
                'email_updated': contact.email_updated.strftime('%Y-%m-%d %H:%M:%S') if contact.email_updated else '',
                'cell_updated': contact.cell_updated.strftime('%Y-%m-%d %H:%M:%S') if contact.cell_updated else '',
                'mailing_address_updated': contact.mailing_address_updated.strftime('%Y-%m-%d %H:%M:%S') if contact.mailing_address_updated else '',
                'dateAdded': contact.dateAdded.strftime('%Y-%m-%d %H:%M:%S') if contact.dateAdded else '',
                'lastModified': contact.lastModified.strftime('%Y-%m-%d %H:%M:%S') if contact.lastModified else ''
            }
            writer.writerow(contact_dict)
        
        # Create a response with the CSV
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=all_contacts.csv'
        response.headers['Content-type'] = 'text/csv'
        
        return response
    except Exception as e:
        session['error_message'] = f"Error generating contacts file: {str(e)}"
        return redirect(url_for('main.dashboard'))

@file_ops_bp.route('/download/sample_csv')
def download_sample():
    """Download a sample CSV template"""
    try:
        # Use the static test_import.csv file
        sample_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'test_import.csv')
        
        if not os.path.exists(sample_file_path):
            session['error_message'] = "Sample file not found."
            return redirect(url_for('main.dashboard'))
        
        return send_file(
            sample_file_path,
            mimetype='text/csv',
            as_attachment=True,
            download_name='sample_contacts.csv'
        )
    except Exception as e:
        session['error_message'] = f"Error downloading sample file: {str(e)}"
        return redirect(url_for('main.dashboard')) 