from flask import Flask, render_template, send_from_directory, request, flash, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for flashing messages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    success_message = None
    contacts = []  # Empty list for now, will be populated when we implement the backend
    
    if request.method == 'POST':
        # This is a placeholder for when we implement the backend
        # We'll add a success message to demonstrate how it would work
        success_message = "CSV Upload feature will be implemented in the backend phase."
        
    return render_template('dashboard.html', 
                          contacts=contacts, 
                          success_message=success_message)

@app.route('/download/sample_csv')
def download_sample():
    return send_from_directory('static', 'sample_contacts.csv')

# Custom filter for formatting dates in templates
@app.template_filter('date')
def format_date(value):
    if value:
        return value.strftime('%Y-%m-%d')
    return ''

if __name__ == '__main__':
    app.run(debug=True) 