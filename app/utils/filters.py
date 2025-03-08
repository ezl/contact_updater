from datetime import datetime
import holidays

def register_filters(app):
    """Register custom template filters with the Flask app"""
    
    @app.template_filter('format_date')
    def format_date(date_str):
        """Format a date string to a more readable format"""
        if not date_str:
            return ""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%b %d, %Y')
        except ValueError:
            return date_str
    
    @app.template_filter('date')
    def format_date_obj(value):
        """Format a datetime object to a readable date"""
        if value is None:
            return ""
        return value.strftime('%b %d, %Y')
    
    @app.template_filter('formatBirthday')
    def format_birthday(value):
        """Format a birthday string (MM-DD) to a more readable format"""
        if not value:
            return ""
        try:
            # Parse the MM-DD format
            month, day = value.split('-')
            month_int = int(month)
            day_int = int(day)
            
            # Create a datetime object for the current year
            current_year = datetime.now().year
            date_obj = datetime(current_year, month_int, day_int)
            
            # Format as "MMM D" (3-letter month abbreviation)
            return date_obj.strftime('%b %-d')
        except (ValueError, AttributeError):
            return value 