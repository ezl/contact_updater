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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define Contact model
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zipCode = db.Column(db.String(20))
    country = db.Column(db.String(100))
    company = db.Column(db.String(100))
    jobTitle = db.Column(db.String(100))
    notes = db.Column(db.Text)
    dateAdded = db.Column(db.DateTime, default=datetime.utcnow)
    lastModified = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
with app.app_context():
    db.create_all()

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
        contacts = Contact.query.order_by(Contact.lastName).all()
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
                
                # Process each row in the CSV
                rows_processed = 0
                for _, row in df.iterrows():
                    # Clean and prepare data
                    contact_data = {}
                    
                    # Map CSV columns to database fields
                    field_mapping = {
                        'First Name': 'firstName',
                        'Last Name': 'lastName',
                        'Email': 'email',
                        'Phone': 'phone',
                        'Address': 'address',
                        'City': 'city',
                        'State': 'state',
                        'Zip': 'zipCode',
                        'Country': 'country',
                        'Company': 'company',
                        'Job Title': 'jobTitle',
                        'Notes': 'notes'
                    }
                    
                    # Process each field if it exists in the CSV
                    for csv_field, db_field in field_mapping.items():
                        if csv_field in row and not pd.isna(row[csv_field]):
                            contact_data[db_field] = str(row[csv_field])
                    
                    # Create the contact record
                    contact = Contact(**contact_data)
                    db.session.add(contact)
                    rows_processed += 1
                
                # Commit all changes to the database
                db.session.commit()
                
                success_message = f"Successfully processed {rows_processed} contacts from the CSV file."
                
                # Refresh contacts list
                contacts = Contact.query.order_by(Contact.lastName).all()
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