import pandas as pd
import os
from typing import Dict, List, Set

class DataLoader:
    def __init__(self):
        """Initialize DataLoader and load datasets"""
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'datasets')
        self.disease_data = None
        self.precautions_data = None
        self.doctors_data = None
        self.load_data()

    def load_data(self):
        """Load all datasets"""
        try:
            # Load disease dataset
            disease_file = os.path.join(self.data_dir, 'disease_dataset.csv')
            self.disease_data = pd.read_csv(disease_file)

            # Load precautions dataset
            precautions_file = os.path.join(self.data_dir, 'precautions_dataset.csv')
            self.precautions_data = pd.read_csv(precautions_file)

            # Load doctors dataset
            doctors_file = os.path.join(self.data_dir, 'doctors_dataset.csv')
            self.doctors_data = pd.read_csv(doctors_file)
            
            print("Successfully loaded all datasets")
        except Exception as e:
            print(f"Error loading datasets: {str(e)}")
            raise

    def get_all_symptoms(self) -> Set[str]:
        """Get all unique symptoms from the disease dataset"""
        symptoms = set()
        symptom_columns = [col for col in self.disease_data.columns if col.startswith('Symptom_')]
        for col in symptom_columns:
            symptoms.update(self.disease_data[col].dropna().unique())
        return symptoms

    def get_disease_symptoms(self) -> Dict[str, List[str]]:
        """Get symptoms for each disease"""
        disease_symptoms = {}
        symptom_columns = [col for col in self.disease_data.columns if col.startswith('Symptom_')]
        
        for _, row in self.disease_data.iterrows():
            disease = row['Disease']
            symptoms = [row[col] for col in symptom_columns if pd.notna(row[col])]
            disease_symptoms[disease] = symptoms
            
        return disease_symptoms

    def get_disease_precautions(self, disease: str) -> List[str]:
        """Get precautions for a specific disease"""
        try:
            # Find the precautions for the disease
            precautions = self.precautions_data[self.precautions_data['Disease'].str.lower() == disease.lower()]
            
            if precautions.empty:
                return ["No specific precautions found for this condition. Please consult a doctor."]
            
            # Get the first row of precautions for this disease
            first_precautions = precautions.iloc[0]
            
            # Get unique precautions (excluding the Disease column)
            unique_precautions = set(first_precautions[1:].unique())  # Skip the Disease column
            
            # Remove any NaN values and format the precautions
            formatted_precautions = [p for p in unique_precautions if pd.notna(p)]
            
            if not formatted_precautions:
                return ["No specific precautions found for this condition. Please consult a doctor."]
                
            return sorted(formatted_precautions)  # Sort for consistent ordering
            
        except Exception as e:
            print(f"Error getting precautions: {str(e)}")
            return ["Error retrieving precautions. Please consult a doctor."]

    def get_doctors_for_disease(self, disease: str) -> List[Dict]:
        """Get recommended doctors for a specific disease"""
        try:
            # Find doctors for this disease
            doctors = self.doctors_data[self.doctors_data['Disease'].str.lower() == disease.lower()]
            
            if doctors.empty:
                # If no exact match, return general practitioners
                doctors = self.doctors_data[self.doctors_data['Specialization'].str.contains('General', case=False, na=False)]
            
            # Convert to list of dictionaries
            doctors_list = []
            for _, doctor in doctors.iterrows():
                doctors_list.append({
                    'name': doctor['Doctor Name'],
                    'specialization': doctor['Specialization'],
                    'experience': doctor['Experience'],
                    'contact': doctor['Phone Number'],
                    'location': doctor['Hospital'],
                    'rating': f"{doctor['Rating']}/5.0",
                    'availability': doctor['Availability Time']
                })
            
            # Sort by rating (highest first) and take top 5
            doctors_list = sorted(doctors_list, key=lambda x: float(x['rating'].split('/')[0]), reverse=True)[:5]
            
            return doctors_list if doctors_list else [
                {
                    'name': 'General Physician',
                    'specialization': 'General Medicine',
                    'experience': 'Please consult hospital',
                    'contact': 'Please contact hospital',
                    'location': 'Please visit nearest hospital',
                    'rating': 'N/A',
                    'availability': 'Contact hospital for timings'
                }
            ]
        except Exception as e:
            print(f"Error getting doctors: {str(e)}")
            return [
                {
                    'name': 'Error',
                    'specialization': 'Error retrieving doctor information',
                    'contact': 'Please contact hospital directly',
                    'location': 'N/A',
                    'rating': 'N/A',
                    'availability': 'N/A'
                }
            ]

    def get_all_diseases(self) -> List[str]:
        """Get a list of all unique diseases"""
        if self.disease_data is None:
            return []
        return sorted(self.disease_data['Disease'].unique().tolist()) 