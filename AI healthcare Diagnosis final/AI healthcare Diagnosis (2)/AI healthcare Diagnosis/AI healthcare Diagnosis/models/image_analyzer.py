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

class ImageAnalyzer:
    def __init__(self):
        """Initialize the image analyzer with pre-trained models and OCR configuration"""
        # Initialize ResNet50 model for scan analysis
        self.model = ResNet50(weights='imagenet')
        
        # Configure Tesseract path for Windows
        if sys.platform == 'win32':
            tesseract_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
            ]
            for path in tesseract_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        
        # Define conditions for different scan types
        self.scan_conditions = {
            'xray': {
                'conditions': [
                    'pneumonia', 'fracture', 'tuberculosis', 'lung_cancer',
                    'bronchitis', 'emphysema', 'pleural_effusion'
                ],
                'keywords': [
                    'lung', 'chest', 'bone', 'joint', 'spine', 'rib',
                    'opacity', 'consolidation', 'infiltrate', 'mass'
                ]
            },
            'mri': {
                'conditions': [
                    'brain_tumor', 'stroke', 'multiple_sclerosis',
                    'herniated_disc', 'aneurysm', 'brain_hemorrhage'
                ],
                'keywords': [
                    'brain', 'spine', 'neural', 'tissue', 'mass',
                    'lesion', 'hemorrhage', 'disc', 'vertebra'
                ]
            },
            'ct_scan': {
                'conditions': [
                    'kidney_stone', 'liver_tumor', 'appendicitis',
                    'pancreatic_cancer', 'lung_nodule', 'colon_cancer'
                ],
                'keywords': [
                    'abdomen', 'liver', 'kidney', 'pancreas', 'lung',
                    'nodule', 'mass', 'stone', 'inflammation'
                ]
            }
        }
        
        # Define keywords for report analysis
        self.report_keywords = {
            'diagnosis': [
                'diagnosis:', 'diagnosed with', 'assessment:', 'impression:',
                'findings:', 'condition:', 'medical condition:', 'clinical findings:',
                'diagnostic impression:', 'final diagnosis:', 'diagnosed', 'finding',
                'condition', 'assessment', 'impression', 'clinical diagnosis'
            ],
            'recommendations': [
                'recommendations:', 'recommended:', 'advised:', 'suggestions:',
                'treatment plan:', 'plan:', 'medical advice:', 'instructions:',
                'follow these instructions:', 'patient instructions:', 'advice',
                'suggestion', 'recommendation', 'treatment', 'plan', 'instruction'
            ],
            'medications': [
                'medications:', 'medicine:', 'prescribed medications:',
                'drugs:', 'prescriptions:', 'current medications:',
                'medication list:', 'prescribed drugs:', 'drug name:',
                'medication', 'prescription', 'drug', 'tablet', 'capsule'
            ],
            'follow_up': [
                'follow up:', 'follow-up:', 'next appointment:',
                'return visit:', 'review after:', 'check up after:',
                'next review:', 'follow up plan:', 'schedule review:',
                'follow up', 'appointment', 'review', 'check up', 'return visit'
            ]
        }

    def preprocess_image(self, image):
        """Preprocess image for model input"""
        # Resize image to 224x224
        image = image.resize((224, 224))
        # Convert to array and preprocess
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = tf.expand_dims(img_array, 0)
        img_array = tf.keras.applications.resnet50.preprocess_input(img_array)
        return img_array

    def analyze_scan(self, image_path, scan_type):
        """Analyze medical scan image with improved detection"""
        try:
            # Load and preprocess image
            img = Image.open(image_path)
            img = img.resize((224, 224))
            img_array = np.array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = tf.keras.applications.resnet50.preprocess_input(img_array)
            
            # Get model predictions
            predictions = self.model.predict(img_array)
            decoded_predictions = tf.keras.applications.resnet50.decode_predictions(predictions, top=10)[0]
            
            # Filter and process predictions
            scan_info = self.scan_conditions.get(scan_type.lower(), {})
            if not scan_info:
                return {
                    'success': False,
                    'error': f"Invalid scan type: {scan_type}"
                }
            
            relevant_predictions = []
            for pred in decoded_predictions:
                pred_name = pred[1].lower().replace('_', ' ')
                confidence = float(pred[2])
                
                # Check if prediction matches any conditions or keywords
                is_relevant = any(cond.lower() in pred_name for cond in scan_info['conditions'])
                is_relevant = is_relevant or any(keyword in pred_name for keyword in scan_info['keywords'])
                
                if is_relevant and confidence > 0.1:  # Filter low confidence predictions
                    finding = {
                        'condition': pred_name.title(),
                        'confidence': round(confidence * 100, 2),
                        'severity': self._get_severity(confidence),
                        'description': self._get_finding_description(pred_name, scan_type)
                    }
                    relevant_predictions.append(finding)
            
            if not relevant_predictions:
                return {
                    'success': True,
                    'message': 'No significant findings detected. Please consult a healthcare professional for accurate interpretation.',
                    'predictions': []
                }
            
            return {
                'success': True,
                'predictions': relevant_predictions,
                'message': 'Potential findings detected. Please consult a healthcare professional for accurate diagnosis.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error analyzing scan: {str(e)}"
            }

    def _get_severity(self, confidence):
        """Determine severity based on confidence score"""
        if confidence > 0.8:
            return "High"
        elif confidence > 0.5:
            return "Medium"
        return "Low"

    def _get_finding_description(self, finding, scan_type):
        """Generate a description for the finding"""
        descriptions = {
            'xray': {
                'opacity': 'Possible area of dense tissue or fluid in the lungs',
                'mass': 'Abnormal growth or lesion detected',
                'fracture': 'Possible bone break or crack',
                'pneumonia': 'Signs of lung infection or inflammation',
                'tuberculosis': 'Possible signs of TB infection',
                'effusion': 'Fluid accumulation in the pleural space'
            },
            'mri': {
                'tumor': 'Abnormal tissue growth detected',
                'lesion': 'Area of abnormal tissue',
                'hemorrhage': 'Signs of bleeding',
                'stroke': 'Area of restricted blood flow',
                'herniation': 'Displacement of tissue or structure'
            },
            'ct_scan': {
                'stone': 'Dense mineral formation',
                'mass': 'Abnormal tissue growth',
                'inflammation': 'Area of swelling or infection',
                'nodule': 'Small round or oval-shaped growth'
            }
        }
        
        # Find matching description
        scan_descriptions = descriptions.get(scan_type, {})
        for key, desc in scan_descriptions.items():
            if key in finding.lower():
                return desc
        
        return "Abnormal finding requiring professional medical interpretation"

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
        """Extract text from image with improved OCR configuration"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image_for_ocr(image_path)
            if processed_image is None:
                return "Error: Could not process image"
            
            # Configure Tesseract parameters for better text extraction
            custom_config = r'--oem 3 --psm 6 -l eng'
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=custom_config)
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            text = text.strip()
            
            return text
            
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def analyze_report(self, image_path):
        """Analyze medical report with improved text processing"""
        try:
            # Extract text from image
            text = self.extract_text_from_image(image_path)
            
            if text.startswith("Error"):
                return {
                    'success': False,
                    'error': text
                }
            
            # Initialize report information
            report_info = {
                'diagnosis': [],
                'recommendations': [],
                'medications': [],
                'follow_up': []
            }
            
            # Split text into lines and process
            lines = text.split('\n')
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Convert to lowercase for matching
                line_lower = line.lower()
                
                # Check for section headers
                for section, keywords in self.report_keywords.items():
                    if any(keyword in line_lower for keyword in keywords):
                        current_section = section
                        # Extract content after the keyword
                        for keyword in keywords:
                            if keyword in line_lower:
                                content = line.split(keyword, 1)[1].strip()
                                if content and content not in report_info[section]:
                                    report_info[section].append(content)
                                break
                        break
                else:
                    # If no section header found, add to current section
                    if current_section and line not in report_info[current_section]:
                        report_info[current_section].append(line)
            
            # Clean up and validate extracted information
            for section in report_info:
                # Remove empty strings and duplicates
                report_info[section] = list(filter(None, report_info[section]))
                # Remove very short strings (likely noise)
                report_info[section] = [item for item in report_info[section] if len(item) > 3]
                # Remove duplicates while preserving order
                report_info[section] = list(dict.fromkeys(report_info[section]))
            
            # If no information was extracted, try to include meaningful lines
            if not any(report_info.values()):
                meaningful_lines = []
                for line in lines:
                    line = line.strip()
                    if len(line) > 20 and not line.isupper():  # Basic heuristics for meaningful content
                        meaningful_lines.append(line)
                
                if meaningful_lines:
                    report_info['diagnosis'] = meaningful_lines[:3]  # Add first 3 meaningful lines as diagnosis
            
            return {
                'success': True,
                'report_info': report_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error analyzing report: {str(e)}"
            }

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