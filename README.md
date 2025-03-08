# Contact Updater

A Flask web application for managing contacts with CSV import/export functionality and email campaign capabilities.

## Features

- Add, edit, and delete contacts
- Import contacts from CSV files
- Export contacts to CSV files
- View rejected records from imports
- Track contact information updates
- View birthdays and holidays in a calendar
- Remove duplicate contacts
- Create and send email campaigns to contacts

## Project Structure

The application is organized into a modular structure using the Flask factory pattern:

```
contact_updater/
├── app/                      # Application package
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── contact_model.py  # Contact and DeletedContact models
│   │   └── email_campaign_model.py # Email campaign models
│   ├── routes/               # Route handlers
│   │   ├── __init__.py
│   │   ├── main.py           # Main routes (dashboard, events)
│   │   ├── contacts.py       # Contact CRUD operations
│   │   ├── file_operations.py # File import/export operations
│   │   └── email_campaigns.py # Email campaign operations
│   ├── services/             # Service layer
│   │   └── email_service.py  # Email service for campaigns
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── filters.py        # Template filters
│   │   └── helpers.py        # Helper functions
│   ├── static/               # Static files (CSS, JS)
│   ├── templates/            # HTML templates
│   └── __init__.py           # Application factory
├── flask_session/            # Session files
├── uploads/                  # Upload directory
├── run.py                    # Application entry point
├── init_db.py                # Database initialization script
├── reset_db.py               # Database reset script
├── cleanup_deleted_contacts.py # Script to clean up old deleted contacts
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/contact_updater.git
   cd contact_updater
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## CSV Import Format

The application accepts CSV files with the following columns:
- name
- cell
- email
- mailing_address
- notes
- birthday (formats: MM-DD, DD-MMM, MM/DD/YYYY, YYYY-MM-DD)
- facebook
- instagram
- twitter

You can download a sample CSV template from the application.

## Email Campaigns

The application allows you to:
1. Select contacts to include in an email campaign
2. Compose an email with a rich text editor
3. Review the campaign before sending
4. Send the campaign and track opens, clicks, and bounces
5. View campaign statistics and recipient status

## Maintenance

### Cleaning Up Deleted Contacts

The application stores deleted contacts temporarily to support undo functionality. To clean up old deleted contacts, run:

```
python cleanup_deleted_contacts.py
```

By default, this will remove contacts deleted more than 30 minutes ago. You can specify a custom time threshold:

```
python cleanup_deleted_contacts.py --minutes 60
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
