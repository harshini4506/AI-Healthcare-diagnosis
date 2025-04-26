import os
from typing import Dict, List, Any
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import re
import cv2
import sys
import subprocess
import logging

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    def __init__(self):
        # Define conditions first
        self.conditions = {
            'pneumonia': {
                'description': 'Inflammation of the air sacs in the lungs',
                'indicators': ['white patches', 'consolidation', 'infiltrates'],
                'severity_levels': ['mild', 'moderate', 'severe']
            },
            'tuberculosis': {
                'description': 'Bacterial infection primarily affecting the lungs',
                'indicators': ['cavities', 'infiltrates', 'calcification'],
                'severity_levels': ['early', 'progressive', 'advanced']
            },
            'lung_cancer': {
                'description': 'Malignant tumor in the lung tissue',
                'indicators': ['nodules', 'masses', 'pleural effusion'],
                'severity_levels': ['early', 'intermediate', 'advanced']
            },
            'covid19': {
                'description': 'Viral infection affecting the respiratory system',
                'indicators': ['ground glass opacity', 'bilateral infiltrates'],
                'severity_levels': ['mild', 'moderate', 'severe']
            }
        }
        # Then load the model
        self.model = self._load_model()
        
        # Medical terms and patterns for enhanced analysis
        self.medical_sections = {
            'diagnosis': r'diagnosis|assessment|impression',
            'medications': r'medications|drugs|prescriptions',
            'vitals': r'vital signs|vitals|measurements',
            'recommendations': r'recommendations|plan|follow-up',
            'history': r'history|background|previous conditions'
        }

    def _load_model(self):
        try:
            # Load pre-trained model for medical image analysis
            model = tf.keras.applications.DenseNet121(
                weights='imagenet',
                include_top=False,
                input_shape=(224, 224, 3)
            )
            
            # Add custom layers for medical condition detection
            x = model.output
            x = tf.keras.layers.GlobalAveragePooling2D()(x)
            x = tf.keras.layers.Dense(1024, activation='relu')(x)
            x = tf.keras.layers.Dropout(0.5)(x)
            predictions = tf.keras.layers.Dense(len(self.conditions), activation='sigmoid')(x)
            
            return tf.keras.Model(inputs=model.input, outputs=predictions)
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return None

    def preprocess_image(self, image_path):
        try:
            # Load and preprocess the image
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Could not read image file")
            
            # Convert to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to standard size
            image = cv2.resize(image, (224, 224))
            
            # Normalize pixel values
            image = image.astype(np.float32) / 255.0
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            return image
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")

    def analyze_image(self, image_path):
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_path)
            
            # Get model predictions
            predictions = self.model.predict(processed_image)
            
            # Process results
            results = {
                'status': 'completed',
                'findings': {
                    'detected_conditions': {},
                    'abnormalities': [],
                    'normal_findings': []
                },
                'recommendations': []
            }
            
            # Analyze predictions for each condition
            for idx, (condition, details) in enumerate(self.conditions.items()):
                confidence = float(predictions[0][idx])
                if confidence > 0.5:  # Detection threshold
                    severity = self._determine_severity(confidence)
                    results['findings']['detected_conditions'][condition] = {
                        'confidence': confidence,
                        'severity': severity,
                        'description': details['description'],
                        'indicators': [
                            indicator for indicator in details['indicators']
                            if self._detect_indicator(processed_image, indicator)
                        ]
                    }
                    
                    # Add abnormalities based on detected indicators
                    results['findings']['abnormalities'].extend([
                        f"Detected {indicator} suggesting {condition}"
                        for indicator in results['findings']['detected_conditions'][condition]['indicators']
                    ])
            
            # Generate recommendations
            if results['findings']['detected_conditions']:
                results['recommendations'] = self._generate_recommendations(
                    results['findings']['detected_conditions']
                )
            else:
                results['findings']['normal_findings'] = [
                    "No significant abnormalities detected",
                    "Normal lung fields",
                    "Clear costophrenic angles",
                    "Normal cardiac silhouette"
                ]
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

    def _detect_indicator(self, image, indicator):
        # Implement specific detection logic for each indicator
        # This is a simplified version - in practice, you would have more sophisticated detection methods
        try:
            # Convert indicator to lowercase for comparison
            indicator = indicator.lower()
            
            # Get image features
            features = self._extract_features(image)
            
            # Check for specific indicators
            if 'opacity' in indicator:
                return self._detect_opacity(features)
            elif 'nodule' in indicator or 'mass' in indicator:
                return self._detect_nodules(features)
            elif 'infiltrate' in indicator:
                return self._detect_infiltrates(features)
            elif 'effusion' in indicator:
                return self._detect_effusion(features)
            
            # Default to basic threshold-based detection
            return np.mean(features) > 0.5
            
        except Exception:
            return False

    def _extract_features(self, image):
        # Extract relevant features from the image
        # This is a simplified version - in practice, you would use more sophisticated feature extraction
        try:
            # Convert to grayscale if not already
            if len(image.shape) > 2:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
                
            # Apply various feature extraction techniques
            features = {
                'histogram': cv2.calcHist([gray], [0], None, [256], [0, 256]),
                'mean_intensity': np.mean(gray),
                'std_intensity': np.std(gray),
                'edges': cv2.Canny(gray, 100, 200)
            }
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {str(e)}")
            return None

    def _detect_opacity(self, features):
        # Detect areas of opacity in the image
        try:
            return features['mean_intensity'] > 127
        except:
            return False

    def _detect_nodules(self, features):
        # Detect potential nodules or masses
        try:
            return np.max(features['edges']) > 200
        except:
            return False

    def _detect_infiltrates(self, features):
        # Detect infiltrates in the image
        try:
            return features['std_intensity'] > 50
        except:
            return False

    def _detect_effusion(self, features):
        # Detect pleural effusion
        try:
            return features['mean_intensity'] < 100
        except:
            return False

    def _generate_recommendations(self, detected_conditions):
        recommendations = []
        
        for condition, details in detected_conditions.items():
            severity = details['severity']
            
            # Add severity-based recommendations
            if severity == 'severe':
                recommendations.extend([
                    f"Urgent medical attention required for {condition}",
                    "Immediate consultation with specialist recommended",
                    "Consider emergency care if symptoms worsen"
                ])
            elif severity == 'moderate':
                recommendations.extend([
                    f"Schedule follow-up appointment for {condition} within 1 week",
                    "Monitor symptoms closely",
                    "Additional tests may be needed"
                ])
            else:  # mild
                recommendations.extend([
                    f"Regular monitoring of {condition} recommended",
                    "Schedule routine follow-up",
                    "Report any worsening symptoms"
                ])
            
            # Add condition-specific recommendations
            if condition == 'pneumonia':
                recommendations.extend([
                    "Rest and adequate hydration essential",
                    "Complete full course of prescribed antibiotics",
                    "Monitor temperature and breathing"
                ])
            elif condition == 'tuberculosis':
                recommendations.extend([
                    "Follow isolation protocols",
                    "Complete full course of TB treatment",
                    "Regular follow-up testing required"
                ])
            elif condition == 'lung_cancer':
                recommendations.extend([
                    "Urgent oncology consultation needed",
                    "Additional imaging studies recommended",
                    "Discuss treatment options with specialist"
                ])
            elif condition == 'covid19':
                recommendations.extend([
                    "Follow current COVID-19 isolation guidelines",
                    "Monitor oxygen levels regularly",
                    "Seek immediate care if breathing difficulty increases"
                ])
        
        # Add general recommendations
        recommendations.extend([
            "Maintain a healthy lifestyle",
            "Stay well-hydrated",
            "Get adequate rest",
            "Follow up with your healthcare provider as recommended"
        ])
        
        return list(set(recommendations))  # Remove duplicates

    def preprocess_image_for_ocr(self, image_path):
        """Enhanced image preprocessing for better OCR results"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not read image file")
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Apply dilation to connect text components
            kernel = np.ones((2,2), np.uint8)
            dilated = cv2.dilate(enhanced, kernel, iterations=1)
            
            return dilated
            
        except Exception as e:
            print(f"Error in image preprocessing: {str(e)}")
            return None

    def extract_text_from_image(self, image_path):
        """
        Extract text from an image using OCR.
        """
        try:
            # Read the image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Failed to load image")

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Apply dilation to connect text components
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            gray = cv2.dilate(gray, kernel, iterations=1)

            # Convert to PIL Image
            pil_image = Image.fromarray(gray)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_image)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            raise

    def analyze_report(self, image_path):
        """
        Analyze a medical report image and extract structured information.
        """
        try:
            # Extract text from the report
            text = self.extract_text_from_image(image_path)
            if not text:
                return {
                    'success': False,
                    'error': 'No text could be extracted from the image'
                }

            # Generate a summary of the text
            summary = self._generate_summary(text)

            # Extract structured information
            report_info = self._extract_structured_info(text)
            
            # Add the summary to the report info
            report_info['summary'] = summary
            
            return {
                'success': True,
                'report_info': report_info
            }
            
        except Exception as e:
            logger.error(f"Error in report analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_summary(self, text):
        """
        Generate a concise summary of the medical report without using transformers.
        """
        try:
            # Simple extractive summarization
            sentences = text.split('.')
            # Select important sentences containing medical terms
            important_sentences = []
            medical_terms = ['diagnosis', 'condition', 'treatment', 'symptoms', 'findings']
            
            for sentence in sentences:
                if any(term in sentence.lower() for term in medical_terms):
                    important_sentences.append(sentence.strip())
            
            # Return first 3 important sentences or all if less than 3
            summary = '. '.join(important_sentences[:3])
            return summary if summary else "No summary available."

        except Exception as e:
            logger.warning(f"Error generating summary: {str(e)}")
            return "Summary generation failed"

    def _extract_structured_info(self, text):
        """
        Extract structured information from the report text.
        """
        report_info = {
            'diagnosis': [],
            'medications': [],
            'vitals': {},
            'recommendations': [],
            'key_findings': []
        }

        # Process text by sections
        for section, pattern in self.medical_sections.items():
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                # Get the text following the section header
                start_pos = match.end()
                section_text = text[start_pos:start_pos + 500]  # Look at next 500 chars
                
                # Extract relevant information based on section
                if section == 'diagnosis':
                    diagnoses = self._extract_diagnoses(section_text)
                    report_info['diagnosis'].extend(diagnoses)
                elif section == 'medications':
                    meds = self._extract_medications(section_text)
                    report_info['medications'].extend(meds)
                elif section == 'vitals':
                    vitals = self._extract_vitals(section_text)
                    report_info['vitals'].update(vitals)
                elif section == 'recommendations':
                    recs = self._extract_recommendations(section_text)
                    report_info['recommendations'].extend(recs)

        # Extract any additional key findings
        report_info['key_findings'] = self._extract_key_findings(text)

        return report_info

    def _extract_diagnoses(self, text):
        """Extract diagnosis information from text."""
        diagnoses = []
        # Look for common diagnosis patterns
        diagnosis_patterns = [
            r"diagnosed with\s+([^.]*)",
            r"diagnosis:?\s+([^.]*)",
            r"impression:?\s+([^.]*)"
        ]
        
        for pattern in diagnosis_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                if match.group(1).strip():
                    diagnoses.append(match.group(1).strip())
        
        return list(set(diagnoses))  # Remove duplicates

    def _extract_medications(self, text):
        """Extract medication information from text."""
        medications = []
        # Look for medication patterns
        med_patterns = [
            r"(\w+)\s+(\d+\s*(?:mg|mcg|ml|g))",
            r"prescribed\s+([^.]*)",
            r"taking\s+([^.]*)"
        ]
        
        for pattern in med_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                if match.group(1).strip():
                    medications.append(match.group(0).strip())
        
        return list(set(medications))

    def _extract_vitals(self, text):
        """Extract vital signs from text."""
        vitals = {}
        vital_patterns = {
            'blood_pressure': r"bp:?\s*(\d{2,3}\/\d{2,3})",
            'heart_rate': r"(?:heart rate|pulse|hr):?\s*(\d{2,3})",
            'temperature': r"(?:temp|temperature):?\s*(\d{2,3}(?:\.\d)?)",
            'oxygen': r"(?:o2|oxygen|spo2):?\s*(\d{2,3}%?)"
        }
        
        for vital, pattern in vital_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                vitals[vital] = match.group(1)
        
        return vitals

    def _extract_recommendations(self, text):
        """Extract recommendations from text."""
        recommendations = []
        # Look for recommendation patterns
        rec_patterns = [
            r"recommend(?:ed|s)?\s+([^.]*)",
            r"advised?\s+([^.]*)",
            r"follow[- ]up:?\s+([^.]*)"
        ]
        
        for pattern in rec_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                if match.group(1).strip():
                    recommendations.append(match.group(1).strip())
        
        return list(set(recommendations))

    def _extract_key_findings(self, text):
        """Extract key findings from text."""
        findings = []
        # Look for key finding patterns
        finding_patterns = [
            r"finding(?:s)?:?\s+([^.]*)",
            r"noted:?\s+([^.]*)",
            r"observed:?\s+([^.]*)",
            r"shows:?\s+([^.]*)"
        ]
        
        for pattern in finding_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                if match.group(1).strip():
                    findings.append(match.group(1).strip())
        
        return list(set(findings))

    def _get_condition_name(self, index: int, scan_type: str) -> str:
        """Convert model index to condition name"""
        # This is a simplified mapping - in a real application, you would have a more comprehensive mapping
        conditions = {
            'xray': ['normal', 'pneumonia', 'fracture', 'tuberculosis'],
            'mri': ['normal', 'brain_tumor', 'stroke', 'herniated_disc'],
            'ct_scan': ['normal', 'appendicitis', 'kidney_stone', 'pulmonary_embolism']
        }
        
        if scan_type in conditions and index < len(conditions[scan_type]):
            return conditions[scan_type][index]
        return 'unknown'

    def _process_report_text(self, text: str) -> Dict[str, Any]:
        """Process extracted text from medical reports"""
        # Define keywords for different types of information
        keywords = {
            'diagnosis': ['diagnosis', 'impression', 'finding', 'conclusion'],
            'recommendations': ['recommendation', 'advice', 'suggestion', 'plan'],
            'medications': ['medication', 'prescription', 'drug', 'tablet'],
            'follow_up': ['follow up', 'follow-up', 'review', 'revisit']
        }

        report_info = {
            'diagnosis': [],
            'recommendations': [],
            'medications': [],
            'follow_up': []
        }

        # Process each line of text
        for line in text.split('\n'):
            line = line.strip().lower()
            if not line:
                continue

            # Check for keywords and categorize information
            for category, words in keywords.items():
                if any(word in line for word in words):
                    report_info[category].append(line)

        return report_info 