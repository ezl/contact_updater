# Client Magic

A web application for managing contact information. Import contacts from CSV files, view, edit, and manage your contacts in one place.

## Features

The application uses SQLite for data storage. The database file is named `sqlite3.db` and is created in the root directory of the project.

- Import contacts from CSV files
- View all contacts in a table
- Edit contact information
- Delete contacts
- Remove duplicate contacts
- Search contacts
- View contact details
- Download all contacts as CSV

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize the database: `python init_db.py`
6. Run the application: `python app.py`
7. Open your browser and navigate to `http://127.0.0.1:5000`

## Usage

1. Navigate to the dashboard
2. Import contacts from a CSV file
3. View and manage your contacts
4. Click on a contact to view details
5. Edit contact information by clicking on the fields in the detail view

## File Structure

- `app.py`: Main application file
- `init_db.py`: Database initialization script
- `reset_db.py`: Database reset script
- `templates/`: HTML templates
- `static/`: Static files (CSS, JS, images)
- `uploads/`: Temporary storage for uploaded files
