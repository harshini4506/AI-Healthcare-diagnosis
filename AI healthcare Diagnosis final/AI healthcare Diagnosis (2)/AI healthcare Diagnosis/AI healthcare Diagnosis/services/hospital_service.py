from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Sample hospital data (in a real application, this would come from a database or API)
SAMPLE_HOSPITALS = [
    {
        'name': 'City General Hospital',
        'address': '123 Main St, City',
        'phone': '(555) 123-4567',
        'specialties': ['Emergency', 'General Medicine', 'Cardiology'],
        'rating': 4.5,
        'coordinates': (40.7128, -74.0060)  # Example coordinates
    },
    {
        'name': 'Medical Center',
        'address': '456 Health Ave, City',
        'phone': '(555) 987-6543',
        'specialties': ['Pediatrics', 'Orthopedics', 'Neurology'],
        'rating': 4.8,
        'coordinates': (40.7580, -73.9855)  # Example coordinates
    }
]

def find_nearby_hospitals(location, radius_km=10):
    """
    Find nearby hospitals based on user location
    """
    try:
        # In a real application, you would:
        # 1. Use a proper geocoding service to convert address to coordinates
        # 2. Query a real hospital database or API
        # 3. Calculate actual distances and filter by radius
        
        # For this example, we'll return sample data
        return SAMPLE_HOSPITALS
        
    except Exception as e:
        print(f"Error finding hospitals: {str(e)}")
        return []

def get_hospital_details(hospital_id):
    """
    Get detailed information about a specific hospital
    """
    # In a real application, this would query a database
    for hospital in SAMPLE_HOSPITALS:
        if hospital['name'].lower().replace(' ', '_') == hospital_id.lower():
            return hospital
    return None

class HospitalService:
    def __init__(self):
        # Sample hospital data - in a real application, this would come from a database
        self.hospitals = {
            "fever": [
                {"name": "City General Hospital", "distance": "2.5 km", "contact": "123-456-7890"},
                {"name": "Apollo Hospital", "distance": "3.8 km", "contact": "123-456-7891"}
            ],
            "malaria": [
                {"name": "Tropical Disease Center", "distance": "4.2 km", "contact": "123-456-7892"},
                {"name": "Global Health Hospital", "distance": "5.1 km", "contact": "123-456-7893"}
            ],
            "diabetes": [
                {"name": "Diabetes Care Center", "distance": "3.0 km", "contact": "123-456-7894"},
                {"name": "Endocrine Specialty Hospital", "distance": "4.5 km", "contact": "123-456-7895"}
            ],
            "default": [
                {"name": "General Hospital", "distance": "3.0 km", "contact": "123-456-7896"},
                {"name": "Community Health Center", "distance": "2.8 km", "contact": "123-456-7897"}
            ]
        }

    def get_nearby_hospitals(self, disease):
        """Get nearby hospitals based on the disease"""
        # Convert disease to lowercase for case-insensitive matching
        disease = disease.lower()
        
        # Return disease-specific hospitals if available, otherwise return default hospitals
        return self.hospitals.get(disease, self.hospitals["default"]) 