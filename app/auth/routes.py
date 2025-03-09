from flask import render_template, request, url_for, redirect, flash, session, current_app
from app import db
from app.auth import auth_bp
from app.auth.models import User
from app.auth.utils import generate_magic_link, verify_magic_link, login_user, logout_user
from datetime import datetime

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        if not email:
            flash('Please enter your email address.', 'error')
            return redirect(url_for('auth.login'))

        # Create or get user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email)
            db.session.add(user)
            db.session.commit()

        # Generate magic link token
        token = generate_magic_link(email, current_app.config['SECRET_KEY'])
        magic_link = url_for('auth.verify', token=token, _external=True)

        # Generate email content
        email_text = render_template('email/magic_link.txt', magic_link=magic_link)

        # In development, store the magic link in session for display
        if current_app.debug:
            session['dev_magic_link'] = magic_link
            session['dev_email_text'] = email_text

        # For production, this is where you would send the email
        # send_magic_link(email, magic_link)
        
        flash('Check your email for a magic link to log in!', 'success')
        return redirect(url_for('auth.login'))

    # Get development data from session
    dev_magic_link = session.get('dev_magic_link')
    dev_email_text = session.get('dev_email_text')
    
    return render_template('auth/login.html', 
                         dev_magic_link=dev_magic_link,
                         dev_email_text=dev_email_text)

@auth_bp.route('/verify/<token>')
def verify(token):
    email = verify_magic_link(token, current_app.config['SECRET_KEY'])
    if not email:
        flash('The magic link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if user:
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)
        
        # Get the next URL from session
        next_url = session.pop('next_url', None)
        
        # Clear development magic link data
        session.pop('dev_magic_link', None)
        session.pop('dev_email_text', None)
        
        # Redirect to the stored URL or dashboard
        return redirect(next_url or url_for('main.dashboard'))

    flash('User not found.', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 