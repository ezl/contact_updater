from functools import wraps
from flask import session, redirect, url_for, current_app, request, flash
from itsdangerous import URLSafeTimedSerializer

def login_required(f):
    """Our own login_required decorator, not using Flask-Login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Store the requested URL in the session
            session['next_url'] = request.url
            flash('You need to be logged in to view that page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_serializer(secret_key):
    return URLSafeTimedSerializer(secret_key)

def is_authenticated():
    """Check if user is authenticated"""
    return 'user_id' in session

def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')

def login_user(user):
    """Log in a user by setting session data"""
    session['user_id'] = user.id
    session['user_email'] = user.email

def logout_user():
    """Log out a user by clearing session"""
    session.clear()

def generate_magic_link(email, secret_key):
    """Generate a secure magic link for the given email"""
    s = get_serializer(secret_key)
    token = s.dumps(email, salt='login-key')
    return token

def verify_magic_link(token, secret_key, max_age=3600):
    """Verify a magic link token"""
    try:
        s = get_serializer(secret_key)
        email = s.loads(token, salt='login-key', max_age=max_age)
        return email
    except:
        return None 