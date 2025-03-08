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

@file_ops_bp.route('/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and import"""
    # Check if the post request has the file part
    if 'csv_file' not in request.files:
        session['error_message'] = "No file part in the request"
        return redirect(url_for('main.dashboard'))
    
    file = request.files['csv_file']
    
    # If user does not select file, browser may submit an empty file without filename
    if file.filename == '':
        session['error_message'] = "No file selected"
        return redirect(url_for('main.dashboard'))
    
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
                try:
                    # Map CSV fields to database fields
                    name = row.get('name', '')
                    cell = row.get('cell', '')
                    email = row.get('email', '')
                    mailing_address = row.get('mailing_address', '')
                    notes = row.get('notes', '')
                    birthday = row.get('birthday', '')
                    facebook = row.get('facebook', '')
                    instagram = row.get('instagram', '')
                    twitter = row.get('twitter', '')
                    
                    # Print what we're importing for debugging
                    print(f"Importing name: {name}")
                    print(f"Importing cell: {cell}")
                    print(f"Importing email: {email}")
                    print(f"Importing mailing_address: {mailing_address}")
                    print(f"Importing notes: {notes}")
                    
                    # Format birthday if provided
                    if birthday:
                        try:
                            # Try different date formats
                            for fmt in ['%d-%b', '%m/%d/%Y', '%Y-%m-%d', '%m-%d']:
                                try:
                                    date_obj = datetime.strptime(str(birthday), fmt)
                                    # Format as MM-DD
                                    birthday = date_obj.strftime('%m-%d')
                                    print(f"Importing birthday: {str(birthday)} → {birthday} (MM-DD)")
                                    break
                                except ValueError:
                                    continue
                        except Exception as e:
                            print(f"Error formatting birthday: {str(e)}")
                    
                    # Print social media fields
                    if facebook:
                        print(f"Importing facebook: {facebook}")
                    if instagram:
                        print(f"Importing instagram: {instagram}")
                    if twitter:
                        print(f"Importing twitter: {twitter}")
                    
                    # Validate required fields
                    valid_fields = 0
                    if name:
                        valid_fields += 1
                    if cell:
                        valid_fields += 1
                    if email:
                        valid_fields += 1
                    if mailing_address:
                        valid_fields += 1
                    if notes:
                        valid_fields += 1
                    if birthday:
                        valid_fields += 1
                    if facebook:
                        valid_fields += 1
                    if instagram:
                        valid_fields += 1
                    if twitter:
                        valid_fields += 1
                    if 'email_updated' in row and row['email_updated']:
                        valid_fields += 1
                    if 'cell_updated' in row and row['cell_updated']:
                        valid_fields += 1
                    
                    # Check if we have enough valid fields
                    if valid_fields >= 1:  # At least one valid field
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
                        rows_processed += 1
                        print(f"Row {index}: ACCEPTED - {valid_fields} valid fields: {', '.join([field for field in ['name', 'cell', 'email', 'mailing_address', 'notes', 'birthday', 'email_updated', 'cell_updated', 'facebook', 'instagram', 'twitter'] if field in row and row[field]])}")
                    else:
                        # Add to rejected rows
                        rejected_rows.append(dict(row))
                        print(f"Row {index}: REJECTED - Only {valid_fields} valid fields: {', '.join([field for field in ['name', 'cell', 'email', 'mailing_address', 'notes', 'birthday', 'facebook', 'instagram', 'twitter'] if field in row and row[field]])}")
                
                except Exception as e:
                    # Add to rejected rows
                    rejected_rows.append(dict(row))
                    print(f"Error processing row {index}: {str(e)}")
            
            # Commit changes to database
            db.session.commit()
            
            # Create success message
            if rejected_rows:
                # Generate a unique ID for this set of rejected records
                rejected_id = str(uuid.uuid4())
                rejected_records_store[rejected_id] = rejected_rows
                
                # Create a success message with errors
                session['success_message'] = f"Successfully imported {rows_processed} clients. Were unable to import some. <a href=\"{url_for('file_ops.download_rejected_records', rejected_id=rejected_id)}\" class=\"underline font-medium\">View errors</a>."
                session['has_html'] = True
            else:
                # Simple success message with no errors
                session['success_message'] = f"Successfully imported {rows_processed} clients."
            
            print(f"Import summary: {rows_processed} records imported, {len(rejected_rows)} records rejected")
            
            # Redirect to dashboard to show the updated page with success message
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            session['error_message'] = f"Error processing CSV file: {str(e)}"
            return redirect(url_for('main.dashboard'))
    else:
        # Provide a clear error message for non-CSV files
        session['error_message'] = f"Invalid file type: {file.filename}. Only CSV files are supported."
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