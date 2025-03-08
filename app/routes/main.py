from flask import Blueprint, render_template, request, session, jsonify
from datetime import datetime
from app.models import Contact
from app.utils.helpers import get_holidays_for_month, get_holidays_for_year

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route"""
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard route"""
    # Get messages from session
    success_message = session.pop('success_message', None)
    error_message = session.pop('error_message', None)
    
    # If no success message in session, check query parameters
    if not success_message:
        success_message = request.args.get('success_message')
    
    # Get undo parameters
    undo_action = request.args.get('undo_action')
    undo_id = request.args.get('undo_id')
    
    # Debug print
    print(f"Dashboard route - success_message: {success_message}")
    print(f"Dashboard route - error_message: {error_message}")
    print(f"Dashboard route - undo_action: {undo_action}")
    print(f"Dashboard route - undo_id: {undo_id}")
    
    # Check for HTML content in success message
    has_html = False
    if success_message and ('<' in success_message and '>' in success_message):
        has_html = True
    
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

@main_bp.route('/events', methods=['GET'])
def events():
    """Events calendar route"""
    # Get all contacts
    contacts = Contact.query.all()
    
    # Get current month and year
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get month and year from query parameters if provided
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    view = request.args.get('view', 'month')  # Default to month view
    
    # Use current month and year if not provided
    if not month:
        month = current_month
    if not year:
        year = current_year
    
    # Initialize data for the template
    month_name = datetime(year, month, 1).strftime('%B')
    events = []
    year_events = {}
    
    if view == 'year':
        # Get all birthdays for the year
        year_birthdays = {month: [] for month in range(1, 13)}
        for contact in contacts:
            if contact.birthday:
                try:
                    # Parse the MM-DD format
                    bday_month, bday_day = contact.birthday.split('-')
                    bday_month = int(bday_month)
                    bday_day = int(bday_day)
                    
                    # Add to the appropriate month
                    year_birthdays[bday_month].append({
                        'date': bday_day,
                        'title': f"{contact.name}'s Birthday",
                        'type': 'birthday'
                    })
                except (ValueError, AttributeError):
                    # Skip invalid birthday formats
                    continue
        
        # Get all holidays for the year
        year_holidays = get_holidays_for_year(year)
        
        # Combine birthdays and holidays for each month
        month_names = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        year_events = {}
        for m in range(1, 13):
            month_events = []
            
            # Add birthdays for this month
            for birthday in year_birthdays[m]:
                month_events.append({
                    'date': birthday['date'],
                    'title': birthday['title'],
                    'type': 'birthday'
                })
            
            # Add holidays for this month
            for holiday in year_holidays[m]:
                month_events.append({
                    'date': holiday['date'],
                    'title': holiday['name'],
                    'type': 'holiday'
                })
            
            # Sort events by date
            month_events.sort(key=lambda x: x['date'])
            
            # Add to year events
            year_events[m] = {
                'name': month_names[m-1],
                'events': month_events
            }
    else:
        # Get birthdays for the month
        birthdays = []
        for contact in contacts:
            if contact.birthday:
                try:
                    # Parse the MM-DD format
                    bday_month, bday_day = contact.birthday.split('-')
                    bday_month = int(bday_month)
                    bday_day = int(bday_day)
                    
                    # Check if the birthday is in the current month
                    if bday_month == month:
                        birthdays.append({
                            'date': bday_day,
                            'name': contact.name,
                            'type': 'birthday'
                        })
                except (ValueError, AttributeError):
                    # Skip invalid birthday formats
                    continue
        
        # Get holidays for the month
        holidays_list = get_holidays_for_month(month, year)
        
        # Combine birthdays and holidays
        events = []
        for birthday in birthdays:
            events.append({
                'date': birthday['date'],
                'title': f"{birthday['name']}'s Birthday",
                'type': 'birthday'
            })
        
        for holiday in holidays_list:
            events.append({
                'date': holiday['date'],
                'title': holiday['name'],
                'type': 'holiday'
            })
        
        # Sort events by date
        events.sort(key=lambda x: x['date'])
    
    return render_template('events.html', 
                          events=events, 
                          year_events=year_events,
                          month=month,
                          year=year,
                          month_name=month_name,
                          current_month=current_month,
                          current_year=current_year,
                          view=view)

@main_bp.route('/debug_session')
def debug_session():
    """Debug route to check session contents"""
    session['test_message'] = "This is a test message"
    return jsonify({
        'session_contents': dict(session),
        'session_id': session.sid if hasattr(session, 'sid') else None
    }) 