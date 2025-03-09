from app.auth.utils import login_required

@main_bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html') 