from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
from models.diagnosis import DiagnosisModel
from models.data_loader import DataLoader
from models.image_analyzer import ImageAnalyzer
from services.hospital_service import HospitalService
from services.doctor_service import DoctorService
import os
import json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import openai
import logging
from models.chatbot_responses import MentalHealthChatbot
from functools import wraps
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')


# Global variables to track initialization status
models_initialized = False
initialization_error = None

# Initialize services with lazy loading
data_loader = None
diagnosis_model = None
hospital_service = None
doctor_service = None
image_analyzer = None
chatbot = None

def init_services():
    global data_loader, diagnosis_model, hospital_service, doctor_service, image_analyzer, scan_analyzer, chatbot, models_initialized, initialization_error
    try:
        data_loader = DataLoader()
        diagnosis_model = DiagnosisModel()
        hospital_service = HospitalService()
        doctor_service = DoctorService()
        image_analyzer = ImageAnalyzer()
        chatbot = MentalHealthChatbot()
        models_initialized = True
    except Exception as e:
        initialization_error = str(e)
        logger.error(f"Error initializing services: {e}")

# Start initialization in a separate thread
threading.Thread(target=init_services).start()

def requires_initialization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not models_initialized:
            if initialization_error:
                flash(f"System initialization failed: {initialization_error}", "error")
                return render_template('error.html', error="System is currently unavailable. Please try again later.")
            return render_template('loading.html')
        return f(*args, **kwargs)
    return decorated_function

def load_users():
    try:
        with open('data/users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": []}

def save_users(users_data):
    os.makedirs('data', exist_ok=True)
    with open('data/users.json', 'w') as f:
        json.dump(users_data, f, indent=4)

def verify_user(username, password):
    users_data = load_users()
    for user in users_data['users']:
        if user['username'] == username and user['password'] == password:
            return True
    return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Dummy analysis logic for scan
def analyze_scan(filename):
    try:
        # Enhanced scan analysis with disease-specific findings
        analysis_result = {
            "status": "completed",
            "scan_type": "MRI",  # This would be determined from the file
            "findings": {
                "normal_structures": [
                    "Normal brain tissue structure",
                    "No signs of hemorrhage",
                    "Ventricles appear normal in size"
                ],
                "abnormalities": [
                    "Slight asymmetry in brain hemispheres",
                    "Minor calcification in left frontal lobe"
                ]
            },
            "disease_indicators": {
                "potential_conditions": [
                    "Early signs of neurological disorder",
                    "Possible onset of degenerative condition"
                ],
                "severity": "mild",
                "confidence_score": 0.85
            },
            "recommendations": [
                "Immediate consultation with neurologist recommended",
                "Follow-up scan in 3 months",
                "Consider additional diagnostic tests"
            ]
        }
        return analysis_result
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}

# Dummy analysis logic for report
def analyze_report(filename):
    try:
        with open(os.path.join(UPLOAD_FOLDER, filename), 'r', errors='ignore') as f:
            content = f.read()
        
        # Enhanced report analysis with structured medical summary
        report_summary = {
            "patient_summary": {
                "condition": "Stable with improvement",
                "vital_signs": {
                    "blood_pressure": "Slightly elevated",
                    "heart_rate": "Normal",
                    "temperature": "Normal"
                }
            },
            "medical_history": [
                "Previous diagnosis of condition X",
                "Ongoing treatment for Y",
                "History of Z"
            ],
            "current_status": {
                "symptoms": [
                    "Reduced pain levels",
                    "Improved mobility",
                    "Stable blood pressure"
                ],
                "medications": [
                    "Medication A - dosage adjusted",
                    "Medication B - continued as prescribed"
                ]
            },
            "treatment_plan": {
                "immediate_actions": [
                    "Adjust medication dosage",
                    "Schedule physical therapy",
                    "Follow-up appointment in 2 weeks"
                ],
                "long_term_goals": [
                    "Complete recovery within 6 months",
                    "Maintain stable condition",
                    "Prevent recurrence"
                ]
            },
            "recommendations": [
                "Continue current treatment plan",
                "Regular monitoring of vital signs",
                "Lifestyle modifications",
                "Regular follow-up appointments"
            ]
        }
        return report_summary
    except Exception as e:
        return {"error": f"Report analysis failed: {str(e)}"}

@app.route('/')
@requires_initialization
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if verify_user(username, password):
            session['user'] = username
            return redirect(url_for('index'))
        flash('Invalid credentials', 'error')
        return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        users_data = load_users()
        for user in users_data['users']:
            if user['username'] == username:
                flash('Username already exists', 'error')
                return render_template('register.html')

        users_data['users'].append({
            'username': username,
            'email': email,
            'password': password
        })
        save_users(users_data)
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    try:
        symptoms = data_loader.get_all_symptoms()
        return jsonify({"symptoms": sorted(list(symptoms))})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        if not symptoms:
            return jsonify({"error": "Please provide at least one symptom"}), 400

        diagnosis_result = diagnosis_model.predict(symptoms)

        if "error" in diagnosis_result:
            return jsonify(diagnosis_result), 400

        if diagnosis_result.get('predicted_disease'):
            hospitals = hospital_service.get_nearby_hospitals(diagnosis_result['predicted_disease'])
            diagnosis_result['hospitals'] = hospitals

        return jsonify(diagnosis_result)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/api/precautions', methods=['GET'])
def get_precautions():
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
    try:
        data = request.get_json()
        message = data.get('message', '')
        if not message:
            return jsonify({"error": "Please provide a message"}), 400

        response = doctor_service.get_chatbot_response(message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@app.route('/api/chatbot', methods=['POST'])
def chatbot_response():
    try:
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get response from chatbot
        response = chatbot.get_response(user_message)
        
        # Get contextual suggestions based on the current topic
        suggestions = chatbot.get_suggestions()

        return jsonify({
            'status': 'success',
            'response': {
                'messages': [
                    {'role': 'user', 'content': user_message},
                    {'role': 'assistant', 'content': response}
                ],
                'suggestions': suggestions,
                'current_topic': chatbot.current_topic
            }
        })

    except Exception as e:
        logger.error(f"Chatbot Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': 'I apologize, but I encountered an unexpected error. Please try again.'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
