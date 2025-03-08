from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from dotenv import load_dotenv
import os

# Initialize extensions
db = SQLAlchemy()
csrf = CSRFProtect()

# Load environment variables from .env file
load_dotenv()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key_here')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'csv'}
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///contacts.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UNDO_EXPIRATION_MINUTES'] = 30  # How long undo actions are available
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_FILE_DIR'] = 'flask_session'
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    Session(app)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Import and register blueprints
    from app.routes.main import main_bp
    from app.routes.contacts import contacts_bp
    from app.routes.file_operations import file_ops_bp
    from app.routes.email_campaigns import email_campaigns_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(file_ops_bp)
    app.register_blueprint(email_campaigns_bp)
    
    # Import models to ensure they're registered with SQLAlchemy
    from app.models import contact_model
    
    # Register template filters
    from app.utils.filters import register_filters
    register_filters(app)
    
    return app 