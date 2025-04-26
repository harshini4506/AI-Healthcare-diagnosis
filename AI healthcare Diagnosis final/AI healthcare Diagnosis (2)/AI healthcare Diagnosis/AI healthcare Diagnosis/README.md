# AI Healthcare Diagnosis System

An AI-powered healthcare diagnosis system that helps users identify potential health conditions based on their symptoms and provides recommendations for medical care.

## Features

- Symptom-based disease prediction
- List of precautions and management tips
- Nearby hospital recommendations
- Doctor recommendations based on condition
- Real-time chat with virtual doctor
- User-friendly web interface

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-healthcare-diagnosis
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
ai-healthcare-diagnosis/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── models/
│   └── diagnosis.py      # Disease prediction model
├── services/
│   ├── hospital_service.py  # Hospital recommendation service
│   └── doctor_service.py    # Doctor recommendation service
├── static/
│   ├── css/
│   │   └── style.css     # CSS styles
│   └── js/
│       └── main.js       # Frontend JavaScript
└── templates/
    └── index.html        # Main HTML template
```

## Usage

1. Select your symptoms from the dropdown menu
2. Click "Get Diagnosis" to receive:
   - Predicted condition
   - Possible conditions
   - Recommended precautions
   - Nearby hospitals
   - Recommended doctors
3. Use the chat feature to interact with the virtual doctor

## Note

This is a prototype system and should not be used as a substitute for professional medical advice. Always consult with healthcare professionals for accurate diagnosis and treatment.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 