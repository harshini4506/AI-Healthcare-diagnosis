import os
from dotenv import load_dotenv

load_dotenv()

# Sample doctor data (in a real application, this would come from a database or API)
SAMPLE_DOCTORS = {
    'Common Cold': [
        {
            'name': 'Dr. Sarah Johnson',
            'specialty': 'General Medicine',
            'rating': 4.7,
            'experience': '15 years',
            'availability': 'Mon-Fri, 9AM-5PM',
            'phone': '(555) 111-2222'
        },
        {
            'name': 'Dr. Michael Chen',
            'specialty': 'Family Medicine',
            'rating': 4.6,
            'experience': '12 years',
            'availability': 'Mon-Thu, 10AM-6PM',
            'phone': '(555) 333-4444'
        }
    ],
    'COVID-19': [
        {
            'name': 'Dr. Emily Rodriguez',
            'specialty': 'Infectious Disease',
            'rating': 4.9,
            'experience': '20 years',
            'availability': 'Mon-Sun, 24/7',
            'phone': '(555) 555-6666'
        }
    ],
    'Flu': [
        {
            'name': 'Dr. James Wilson',
            'specialty': 'Internal Medicine',
            'rating': 4.8,
            'experience': '18 years',
            'availability': 'Mon-Fri, 8AM-4PM',
            'phone': '(555) 777-8888'
        }
    ]
}

def get_doctor_recommendations(disease):
    """
    Get recommended doctors based on the diagnosed disease
    """
    try:
        # In a real application, this would:
        # 1. Query a real doctor database
        # 2. Filter by specialty and availability
        # 3. Consider location and insurance coverage
        
        return SAMPLE_DOCTORS.get(disease, [
            {
                'name': 'Dr. General Practitioner',
                'specialty': 'General Medicine',
                'rating': 4.5,
                'experience': '10 years',
                'availability': 'Mon-Fri, 9AM-5PM',
                'phone': '(555) 999-0000'
            }
        ])
        
    except Exception as e:
        print(f"Error getting doctor recommendations: {str(e)}")
        return []

def get_doctor_details(doctor_id):
    """
    Get detailed information about a specific doctor
    """
    # In a real application, this would query a database
    for disease, doctors in SAMPLE_DOCTORS.items():
        for doctor in doctors:
            if doctor['name'].lower().replace(' ', '_') == doctor_id.lower():
                return doctor
    return None

class DoctorService:
    def __init__(self):
        # Dummy doctor data for demonstration
        self.doctors = {
            'Common Cold': [
                {
                    'name': 'Dr. Sarah Johnson',
                    'specialty': 'General Medicine',
                    'rating': 4.7,
                    'experience': '15 years',
                    'availability': 'Mon-Fri, 9AM-5PM'
                },
                {
                    'name': 'Dr. Michael Chen',
                    'specialty': 'Family Medicine',
                    'rating': 4.5,
                    'experience': '10 years',
                    'availability': 'Mon-Sat, 8AM-6PM'
                }
            ],
            'Flu': [
                {
                    'name': 'Dr. Emily Brown',
                    'specialty': 'Internal Medicine',
                    'rating': 4.8,
                    'experience': '20 years',
                    'availability': 'Mon-Fri, 9AM-5PM'
                }
            ],
            'COVID-19': [
                {
                    'name': 'Dr. James Wilson',
                    'specialty': 'Infectious Diseases',
                    'rating': 4.9,
                    'experience': '25 years',
                    'availability': 'Mon-Sun, 24/7'
                }
            ],
            'Bronchitis': [
                {
                    'name': 'Dr. Lisa Anderson',
                    'specialty': 'Pulmonology',
                    'rating': 4.6,
                    'experience': '18 years',
                    'availability': 'Mon-Fri, 9AM-5PM'
                }
            ],
            'Pneumonia': [
                {
                    'name': 'Dr. Robert Taylor',
                    'specialty': 'Pulmonology',
                    'rating': 4.8,
                    'experience': '22 years',
                    'availability': 'Mon-Sun, 24/7'
                }
            ],
            'Gastroenteritis': [
                {
                    'name': 'Dr. David Lee',
                    'specialty': 'Gastroenterology',
                    'rating': 4.7,
                    'experience': '16 years',
                    'availability': 'Mon-Fri, 9AM-5PM'
                }
            ],
            'Dengue Fever': [
                {
                    'name': 'Dr. Maria Garcia',
                    'specialty': 'Infectious Diseases',
                    'rating': 4.9,
                    'experience': '23 years',
                    'availability': 'Mon-Sun, 24/7'
                }
            ],
            'Malaria': [
                {
                    'name': 'Dr. Thomas Wright',
                    'specialty': 'Infectious Diseases',
                    'rating': 4.8,
                    'experience': '21 years',
                    'availability': 'Mon-Sun, 24/7'
                }
            ]
        }

    def get_recommended_doctors(self, disease):
        # Return recommended doctors for the given disease
        return self.doctors.get(disease, []) 