from app import create_app, db
from app.models import DeletedContact
from datetime import datetime, timedelta
import argparse

def cleanup_deleted_contacts(minutes=None):
    """Clean up old deleted contacts based on expiration time"""
    app = create_app()
    with app.app_context():
        # Calculate the expiration time
        if minutes is None:
            # Use the app's configured value
            expiration_minutes = app.config.get('UNDO_EXPIRATION_MINUTES', 30)
        else:
            expiration_minutes = minutes
            
        expiration_time = datetime.utcnow() - timedelta(minutes=expiration_minutes)
        
        # Count records before deletion
        total_records = DeletedContact.query.count()
        expired_records = DeletedContact.query.filter(DeletedContact.deleted_at < expiration_time).count()
        
        # Delete expired records
        DeletedContact.query.filter(DeletedContact.deleted_at < expiration_time).delete()
        db.session.commit()
        
        # Print summary
        print(f"Cleanup summary:")
        print(f"- Total records before cleanup: {total_records}")
        print(f"- Expired records deleted: {expired_records}")
        print(f"- Records remaining: {total_records - expired_records}")
        print(f"- Expiration threshold: {expiration_minutes} minutes")
        print(f"- Expiration time: {expiration_time}")

if __name__ == '__main__':
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Clean up old deleted contacts')
    parser.add_argument('--minutes', type=int, help='Override the expiration time in minutes')
    args = parser.parse_args()
    
    # Run the cleanup
    cleanup_deleted_contacts(args.minutes) 