from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for
import os
import pandas as pd
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for flashing messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    cell = db.Column(db.String(20))
    email = db.Column(db.String(120))
    mailing_address = db.Column(db.String(300))
    notes = db.Column(db.Text)
    dateAdded = db.Column(db.DateTime, default=datetime.utcnow)
    lastModified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    success_message = None
    error_message = None
    
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
                        'notes': 'notes'
                    }
                    
                    # Process each field if it exists in the CSV
                    for csv_field, db_field in field_mapping.items():
                        if csv_field in row and not pd.isna(row[csv_field]):
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
                          error_message=error_message)

@app.route('/delete_contact/<int:id>', methods=['POST'])
def delete_contact(id):
    try:
        contact = Contact.query.get_or_404(id)
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting contact: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/download/sample_csv')
def download_sample():
    return send_from_directory('static', 'sample_contacts.csv')

# Custom filter for formatting dates in templates
@app.template_filter('date')
def format_date(value):
    if value:
        return value.strftime('%Y-%m-%d')
    return ''

if __name__ == '__main__':
    # Make sure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True) 