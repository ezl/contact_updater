from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # This is just a placeholder - we'll implement backend functionality later
    contacts = []  # Empty list for now
    return render_template('dashboard.html', contacts=contacts)

@app.route('/download/sample_csv')
def download_sample():
    return send_from_directory('static', 'sample_contacts.csv')

if __name__ == '__main__':
    app.run(debug=True) 