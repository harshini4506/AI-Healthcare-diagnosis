import numpy as np
from typing import List, Dict, Any
from .data_loader import DataLoader

class DiagnosisModel:
    def __init__(self):
        """Initialize the diagnosis model with data from DataLoader"""
        self.data_loader = DataLoader()
        self.symptoms = self.data_loader.get_all_symptoms()
        self.disease_symptoms = self.data_loader.get_disease_symptoms()
        self.diseases = list(self.disease_symptoms.keys())

    def _normalize_text(self, text: str) -> str:
        """Normalize text for better matching"""
        return text.lower().strip()

    def _calculate_symptom_match_score(self, input_symptoms: List[str], disease_symptoms: List[str]) -> float:
        """Calculate how well the input symptoms match with disease symptoms"""
        input_symptoms_set = set(map(self._normalize_text, input_symptoms))
        disease_symptoms_set = set(map(self._normalize_text, disease_symptoms))
        
        # Calculate intersection and union
        matching_symptoms = len(input_symptoms_set.intersection(disease_symptoms_set))
        total_symptoms = len(disease_symptoms_set)
        
        # Calculate score based on matching symptoms
        if total_symptoms == 0:
            return 0.0
        
        return matching_symptoms / total_symptoms

    def predict(self, symptoms: List[str]) -> Dict[str, Any]:
        """Predict disease based on input symptoms"""
        try:
            if not symptoms:
                return {"error": "No symptoms provided"}

            # Calculate match scores for each disease
            disease_scores = []
            for disease, disease_symptoms in self.disease_symptoms.items():
                score = self._calculate_symptom_match_score(symptoms, disease_symptoms)
                disease_scores.append((disease, score))

            # Sort diseases by score
            disease_scores.sort(key=lambda x: x[1], reverse=True)

            # Get top matches
            top_matches = disease_scores[:3]
            
            if top_matches[0][1] == 0:
                return {"error": "No matching diseases found for the given symptoms"}

            # Primary prediction
            predicted_disease = top_matches[0][0]
            confidence = top_matches[0][1]

            # Get precautions for the predicted disease
            precautions = self.data_loader.get_disease_precautions(predicted_disease)

            # Get possible conditions (diseases with score > 0.3)
            possible_conditions = [
                {"disease": disease, "probability": f"{score * 100:.1f}%"}
                for disease, score in top_matches
                if score > 0.3
            ]

            return {
                "predicted_disease": predicted_disease,
                "confidence": confidence,
                "possible_conditions": possible_conditions,
                "precautions": precautions
            }

        except Exception as e:
            return {"error": f"Error in disease prediction: {str(e)}"} 