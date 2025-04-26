import os
import json
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.densenet import DenseNet121, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
import cv2
from models.image_analyzer import ImageAnalyzer

class ScanAnalyzer:
    def __init__(self):
        self.image_analyzer = ImageAnalyzer()
        self.model = self._load_model()
        self.scan_types = {
            'xray': {
                'conditions': {
                    'pneumonia': {
                        'description': 'Inflammation of the lungs',
                        'indicators': ['opacity', 'consolidation', 'infiltrates'],
                        'severity_levels': ['mild', 'moderate', 'severe']
                    },
                    'tuberculosis': {
                        'description': 'Bacterial infection affecting lungs',
                        'indicators': ['cavities', 'infiltrates', 'calcification'],
                        'severity_levels': ['early', 'progressive', 'advanced']
                    },
                    'lung_cancer': {
                        'description': 'Malignant tumor in lung tissue',
                        'indicators': ['nodules', 'masses', 'pleural effusion'],
                        'severity_levels': ['early', 'intermediate', 'advanced']
                    },
                    'covid19': {
                        'description': 'Viral infection affecting respiratory system',
                        'indicators': ['ground glass opacity', 'bilateral infiltrates'],
                        'severity_levels': ['mild', 'moderate', 'severe']
                    }
                }
            },
            'mri': {
                'conditions': {
                    'brain_tumor': {
                        'description': 'Abnormal growth in brain tissue',
                        'indicators': ['mass effect', 'enhancement', 'edema'],
                        'severity_levels': ['early', 'intermediate', 'advanced']
                    },
                    'stroke': {
                        'description': 'Blood flow disruption to brain',
                        'indicators': ['infarct', 'hemorrhage', 'edema'],
                        'severity_levels': ['acute', 'subacute', 'chronic']
                    }
                }
            },
            'ct': {
                'conditions': {
                    'liver_disease': {
                        'description': 'Abnormalities in liver tissue',
                        'indicators': ['lesions', 'cirrhosis', 'masses'],
                        'severity_levels': ['mild', 'moderate', 'severe']
                    },
                    'kidney_stones': {
                        'description': 'Mineral deposits in kidneys',
                        'indicators': ['calcifications', 'hydronephrosis'],
                        'severity_levels': ['small', 'moderate', 'large']
                    }
                }
            }
        }

    def _load_model(self):
        try:
            base_model = DenseNet121(
                weights='imagenet',
                include_top=False,
                input_shape=(224, 224, 3)
            )
            
            x = base_model.output
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            x = tf.keras.layers.Dense(1024, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.5)(x)
            predictions = tf.keras.layers.Dense(4, activation='sigmoid')(x)
            
            model = tf.keras.Model(inputs=base_model.input, outputs=predictions)
            return model
        except Exception as e:
            raise Exception(f"Error loading model: {str(e)}")

    def preprocess_scan(self, image_path):
        try:
            # Load and preprocess the image
            img = Image.open(image_path).convert('RGB')
            img = img.resize((224, 224))
            img_array = img_to_array(img)
            
            # Apply CLAHE for better contrast
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            enhanced = cv2.merge((cl,a,b))
            img_array = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
            
            # Normalize and expand dimensions
            img_array = preprocess_input(img_array)
            img_array = np.expand_dims(img_array, axis=0)
            
            return img_array
        except Exception as e:
            raise Exception(f"Error preprocessing scan: {str(e)}")

    def analyze_scan(self, image_path, scan_type='xray'):
        try:
            # Validate scan type
            scan_type = scan_type.lower()
            if scan_type not in self.scan_types:
                return {
                    'error': f'Unsupported scan type: {scan_type}. Supported types: {", ".join(self.scan_types.keys())}'
                }

            # Preprocess the scan
            processed_image = self.preprocess_scan(image_path)
            
            # Get model predictions
            predictions = self.model.predict(processed_image)
            
            # Process results
            results = {
                'status': 'completed',
                'scan_type': scan_type,
                'findings': {
                    'detected_conditions': {},
                    'abnormalities': [],
                    'normal_findings': []
                },
                'recommendations': []
            }
            
            # Analyze predictions for each condition
            conditions_found = False
            for idx, (condition, details) in enumerate(self.scan_types[scan_type]['conditions'].items()):
                confidence = float(predictions[0][idx])
                if confidence > 0.5:  # Detection threshold
                    conditions_found = True
                    severity = self._determine_severity(confidence)
                    results['findings']['detected_conditions'][condition] = {
                        'confidence': round(confidence * 100, 2),
                        'severity': severity,
                        'description': details['description'],
                        'indicators': self._detect_indicators(processed_image, details['indicators'])
                    }
                    
                    # Add detected abnormalities
                    results['findings']['abnormalities'].extend([
                        f"Detected {indicator} suggesting {condition}"
                        for indicator in results['findings']['detected_conditions'][condition]['indicators']
                    ])
            
            # Generate recommendations based on findings
            if conditions_found:
                results['recommendations'] = self._generate_recommendations(
                    results['findings']['detected_conditions'],
                    scan_type
                )
            else:
                results['findings']['normal_findings'] = self._get_normal_findings(scan_type)
                results['recommendations'] = [
                    "No immediate medical attention required",
                    "Continue regular check-ups as scheduled",
                    "Maintain healthy lifestyle practices"
                ]
            
            return results
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f"Analysis failed: {str(e)}"
            }

    def _determine_severity(self, confidence):
        if confidence > 0.8:
            return 'severe'
        elif confidence > 0.65:
            return 'moderate'
        else:
            return 'mild'

    def _detect_indicators(self, image, indicators):
        detected = []
        try:
            # Extract features from the image
            features = self._extract_features(image)
            
            for indicator in indicators:
                if self._check_indicator(features, indicator):
                    detected.append(indicator)
            
            return detected
        except Exception:
            return detected

    def _extract_features(self, image):
        try:
            # Convert to grayscale
            if len(image.shape) > 3:
                image = image[0]
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Calculate various features
            features = {
                'mean_intensity': np.mean(gray),
                'std_intensity': np.std(gray),
                'histogram': cv2.calcHist([gray], [0], None, [256], [0, 256]),
                'edges': cv2.Canny(np.uint8(gray * 255), 100, 200)
            }
            
            return features
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return None

    def _check_indicator(self, features, indicator):
        try:
            if 'opacity' in indicator.lower():
                return features['mean_intensity'] > 0.6
            elif 'nodule' in indicator.lower() or 'mass' in indicator.lower():
                return np.sum(features['edges']) > 1000
            elif 'infiltrate' in indicator.lower():
                return features['std_intensity'] > 0.2
            elif 'effusion' in indicator.lower():
                hist = features['histogram']
                dark_regions = np.sum(hist[:128]) / np.sum(hist)
                return dark_regions > 0.6
            return False
        except:
            return False

    def _get_normal_findings(self, scan_type):
        normal_findings = {
            'xray': [
                "No significant abnormalities detected",
                "Normal lung fields",
                "Clear costophrenic angles",
                "Normal cardiac silhouette"
            ],
            'mri': [
                "No acute intracranial abnormality",
                "Normal brain parenchyma",
                "No mass effect or midline shift",
                "Normal ventricle size"
            ],
            'ct': [
                "No acute findings",
                "Normal organ appearance",
                "No masses or lesions",
                "Normal tissue density"
            ]
        }
        return normal_findings.get(scan_type, ["No abnormalities detected"])

    def _generate_recommendations(self, detected_conditions, scan_type):
        recommendations = []
        
        for condition, details in detected_conditions.items():
            severity = details['severity']
            confidence = details['confidence']
            
            # Add severity-based recommendations
            if severity == 'severe':
                recommendations.extend([
                    f"URGENT: Immediate medical attention required for {condition} (Confidence: {confidence}%)",
                    "Schedule emergency consultation with specialist",
                    "Consider hospital admission for monitoring"
                ])
            elif severity == 'moderate':
                recommendations.extend([
                    f"Important: Follow-up required for {condition} (Confidence: {confidence}%)",
                    "Schedule appointment within 1-2 days",
                    "Monitor symptoms closely"
                ])
            else:  # mild
                recommendations.extend([
                    f"Follow-up recommended for {condition} (Confidence: {confidence}%)",
                    "Schedule routine check-up",
                    "Monitor for worsening symptoms"
                ])
        
        # Add general recommendations
        recommendations.extend([
            "Follow up with your healthcare provider",
            "Maintain a record of symptoms",
            "Seek immediate care if condition worsens"
        ])
        
        return list(set(recommendations))  # Remove duplicates 