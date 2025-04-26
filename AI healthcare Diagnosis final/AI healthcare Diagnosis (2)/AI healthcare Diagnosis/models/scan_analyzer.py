import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
import logging
from typing import Dict, List, Tuple, Union
import json
import os

logger = logging.getLogger(__name__)

class ScanAnalyzer:
    def __init__(self):
        self.model = None
        self.labels = self._load_labels()
        self.image_size = (224, 224)
        
        # Initialize the model
        try:
            self.model = tf.keras.applications.DenseNet121(
                weights='imagenet',
                include_top=False,
                input_shape=(224, 224, 3)
            )
            
            # Add classification layers
            x = self.model.output
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            x = tf.keras.layers.Dense(1024, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.5)(x)
            
            # Create final layer with number of classes based on labels
            total_conditions = sum(len(conditions) for conditions in self.labels.values())
            self.predictions = tf.keras.layers.Dense(total_conditions, activation='sigmoid')(x)
            
            self.model = tf.keras.Model(inputs=self.model.input, outputs=self.predictions)
            
        except Exception as e:
            logger.error(f"Error initializing model: {str(e)}")
            self.model = None

    def _load_labels(self) -> Dict[str, List[str]]:
        """Load condition labels for different scan types."""
        try:
            labels_path = os.path.join(os.path.dirname(__file__), 'labels.json')
            with open(labels_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading labels: {str(e)}")
            return {
                'xray': ['Normal', 'Pneumonia'],
                'mri': ['Normal', 'Tumor'],
                'ct': ['Normal', 'Abnormal']
            }

    def analyze_scan(self, image_path: str, scan_type: str) -> Dict:
        """Analyze a medical scan image and return findings."""
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': 'Image file not found'
                }

            if scan_type not in self.labels:
                return {
                    'success': False,
                    'error': f'Unsupported scan type: {scan_type}'
                }

            # Load and preprocess image
            image = self._load_and_preprocess_image(image_path)
            if image is None:
                return {
                    'success': False,
                    'error': 'Failed to process image'
                }

            # Get predictions
            predictions = self._get_predictions(image)
            if predictions is None:
                return {
                    'success': False,
                    'error': 'Failed to analyze image'
                }

            # Process results
            findings = self._process_predictions(predictions, scan_type)
            
            return {
                'success': True,
                'scan_type': scan_type,
                'findings': findings,
                'recommendations': self._generate_recommendations(findings),
                'confidence_score': float(np.max(predictions))
            }

        except Exception as e:
            logger.error(f"Error in scan analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _load_and_preprocess_image(self, image_path: str) -> np.ndarray:
        """Load and preprocess the image for analysis."""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Failed to load image")

            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize
            image = cv2.resize(image, self.image_size)
            
            # Normalize
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image

        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return None

    def _get_predictions(self, image: np.ndarray) -> np.ndarray:
        """Get model predictions for the image."""
        try:
            if self.model is None:
                raise ValueError("Model not initialized")
            
            predictions = self.model.predict(image)
            return predictions[0]  # Remove batch dimension

        except Exception as e:
            logger.error(f"Error getting predictions: {str(e)}")
            return None

    def _process_predictions(self, predictions: np.ndarray, scan_type: str) -> Dict:
        """Process model predictions into meaningful findings."""
        findings = {
            'detected_conditions': [],
            'normal_findings': [],
            'abnormalities': []
        }

        try:
            conditions = self.labels[scan_type]
            threshold = 0.5  # Confidence threshold

            for i, condition in enumerate(conditions):
                confidence = float(predictions[i])
                if confidence > threshold:
                    if condition.lower() == 'normal':
                        findings['normal_findings'].append({
                            'condition': 'Normal',
                            'confidence': round(confidence * 100, 2)
                        })
                    else:
                        findings['detected_conditions'].append({
                            'condition': condition,
                            'confidence': round(confidence * 100, 2),
                            'severity': self._determine_severity(confidence)
                        })

            if not findings['detected_conditions'] and not findings['normal_findings']:
                findings['normal_findings'].append({
                    'condition': 'No significant findings',
                    'confidence': 0.0
                })

            return findings

        except Exception as e:
            logger.error(f"Error processing predictions: {str(e)}")
            return findings

    def _determine_severity(self, confidence: float) -> str:
        """Determine condition severity based on confidence score."""
        if confidence > 0.8:
            return 'Severe'
        elif confidence > 0.6:
            return 'Moderate'
        else:
            return 'Mild'

    def _generate_recommendations(self, findings: Dict) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        if findings['detected_conditions']:
            for condition in findings['detected_conditions']:
                severity = condition['severity']
                cond_name = condition['condition']
                
                if severity == 'Severe':
                    recommendations.append(f"Urgent: Immediate medical attention recommended for {cond_name}")
                    recommendations.append("Schedule emergency consultation with specialist")
                elif severity == 'Moderate':
                    recommendations.append(f"Important: Follow-up required for {cond_name}")
                    recommendations.append("Schedule appointment within 1-2 weeks")
                else:
                    recommendations.append(f"Monitor: Regular follow-up recommended for {cond_name}")
                    recommendations.append("Schedule routine check-up")
        else:
            recommendations.extend([
                "No immediate medical attention required",
                "Continue regular check-ups as scheduled",
                "Maintain healthy lifestyle practices"
            ])

        return recommendations 