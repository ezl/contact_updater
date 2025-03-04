# Client Joy

A Flask application for managing contact information with CSV import/export capabilities.

## Database Management

The application uses SQLite for data storage. The database file is named `sqlite3.db` and is created in the root directory of the project.

### Database Scripts

Several scripts are provided to manage the database:

- `init_db.py`: Initialize the database by creating all required tables (if they don't exist)
- `reset_db.py`: Reset the database by dropping all tables and recreating them (WARNING: This deletes all data!)
- `check_db.py`: Check the database status, including existence, size, and number of contacts

### How to Use

1. **Initialize the database** (first-time setup):
   ```
   python init_db.py
   ```

2. **Check database status**:
   ```
   python check_db.py
   ```

3. **Reset the database** (will delete all data):
   ```
   python reset_db.py
   ```
   You'll be required to type 'YES' to confirm the deletion.

## Running the Application

To start the application:

```
python app.py
```

The server will start at http://127.0.0.1:5000

## Features

- Import contacts from CSV files
- View and manage contacts in a dashboard
- Delete individual contacts
- Download a sample CSV template
