from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from models.diagnosis import DiagnosisModel
from models.data_loader import DataLoader
from models.image_analyzer import ImageAnalyzer
from services.hospital_service import HospitalService
from services.doctor_service import DoctorService
import os
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')  # For session management

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize services
data_loader = DataLoader()
diagnosis_model = DiagnosisModel()
hospital_service = HospitalService()
doctor_service = DoctorService()
image_analyzer = ImageAnalyzer()

def load_users():
    """Load users from JSON file"""
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": []}

def save_users(users_data):
    """Save users to JSON file"""
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(users_data, f, indent=4)

def verify_user(username, password):
    """Verify user credentials"""
    users_data = load_users()
    for user in users_data['users']:
        if user['username'] == username and user['password'] == password:
            return True
    return False

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page"""
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_user(username, password):
            session['user'] = username
            return redirect(url_for('index'))
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')
        
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        # Check if username already exists
        users_data = load_users()
        for user in users_data['users']:
            if user['username'] == username:
                return render_template('register.html', error='Username already exists')
        
        # Add new user
        users_data['users'].append({
            'username': username,
            'email': email,
            'password': password
        })
        save_users(users_data)
        
        return render_template('login.html', success='Registration successful! Please login.')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Handle user logout"""
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of all symptoms"""
    try:
        symptoms = data_loader.get_all_symptoms()
        return jsonify({"symptoms": sorted(list(symptoms))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """API endpoint for disease diagnosis"""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        
        if not symptoms:
            return jsonify({
                "error": "Please provide at least one symptom"
            }), 400

        # Get diagnosis from model
        diagnosis_result = diagnosis_model.predict(symptoms)
        
        if "error" in diagnosis_result:
            return jsonify(diagnosis_result), 400

        # Get nearby hospitals
        if diagnosis_result.get('predicted_disease'):
            hospitals = hospital_service.get_nearby_hospitals(
                diagnosis_result['predicted_disease']
            )
            diagnosis_result['hospitals'] = hospitals

        return jsonify(diagnosis_result)

    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/precautions', methods=['GET'])
def get_precautions():
    """Get precautions for a specific disease"""
    try:
        disease = request.args.get('disease')
        if not disease:
            return jsonify({"error": "Disease parameter is required"}), 400

        precautions = data_loader.get_disease_precautions(disease)
        return jsonify({"precautions": precautions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/doctors', methods=['GET'])
def get_doctors():
    """Get doctors for a specific disease"""
    try:
        disease = request.args.get('disease')
        if not disease:
            return jsonify({"error": "Disease parameter is required"}), 400

        doctors = data_loader.get_doctors_for_disease(disease)
        return jsonify({"doctors": doctors})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                "error": "Please provide a message"
            }), 400

        # Get response from chatbot
        response = doctor_service.get_chatbot_response(message)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}"
        }), 500

@app.route('/api/upload-scan', methods=['POST'])
def upload_scan():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        scan_type = request.form.get('scan_type', '').lower()
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        if not scan_type:
            return jsonify({'success': False, 'error': 'Scan type not specified'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze scan
        result = image_analyzer.analyze_scan(filepath, scan_type)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/upload-report', methods=['POST'])
def upload_report():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze report
        result = image_analyzer.analyze_report(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 