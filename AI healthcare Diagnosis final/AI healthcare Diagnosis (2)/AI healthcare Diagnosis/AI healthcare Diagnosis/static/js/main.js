// Store selected symptoms
let selectedSymptoms = new Set();

// Load common symptoms when the page loads
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/symptoms');
        const data = await response.json();
        
        if (data.symptoms) {
            const symptomsContainer = document.querySelector('.symptom-checkboxes');
            data.symptoms.forEach(symptom => {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-2';
                
                const div = document.createElement('div');
                div.className = 'form-check';
                
                const input = document.createElement('input');
                input.type = 'checkbox';
                input.className = 'form-check-input';
                input.id = `symptom-${symptom}`;
                input.value = symptom;
                
                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = `symptom-${symptom}`;
                label.textContent = symptom;
                
                div.appendChild(input);
                div.appendChild(label);
                col.appendChild(div);
                symptomsContainer.appendChild(col);
                
                // Add event listener for checkbox
                input.addEventListener('change', (e) => {
                    if (e.target.checked) {
                        selectedSymptoms.add(symptom);
                    } else {
                        selectedSymptoms.delete(symptom);
                    }
                    updateSelectedSymptoms();
                });
            });
        }
    } catch (error) {
        console.error('Error loading symptoms:', error);
    }
});

// Handle manual symptom input
document.getElementById('addSymptom').addEventListener('click', () => {
    const input = document.getElementById('symptomInput');
    const symptom = input.value.trim();
    
    if (symptom) {
        selectedSymptoms.add(symptom);
        input.value = '';
        updateSelectedSymptoms();
    }
});

// Update the display of selected symptoms
function updateSelectedSymptoms() {
    const container = document.getElementById('selectedSymptoms');
    container.innerHTML = '';
    
    selectedSymptoms.forEach(symptom => {
        const tag = document.createElement('span');
        tag.className = 'badge bg-primary me-2 mb-2';
        tag.textContent = symptom;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn-close btn-close-white ms-2';
        removeBtn.setAttribute('aria-label', 'Remove');
        removeBtn.onclick = () => {
            selectedSymptoms.delete(symptom);
            // Uncheck corresponding checkbox if it exists
            const checkbox = document.getElementById(`symptom-${symptom}`);
            if (checkbox) checkbox.checked = false;
            updateSelectedSymptoms();
        };
        
        tag.appendChild(removeBtn);
        container.appendChild(tag);
    });
}

// Handle form submission
document.getElementById('symptomForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (selectedSymptoms.size === 0) {
        alert('Please select at least one symptom');
        return;
    }
    
    const loadingSpinner = document.getElementById('loadingSpinner');
    const diagnosisResult = document.getElementById('diagnosisResult');
    const precautionsSection = document.getElementById('precautionsSection');
    const doctorSection = document.getElementById('doctorSection');
    
    loadingSpinner.classList.remove('d-none');
    diagnosisResult.classList.add('d-none');
    
    try {
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                symptoms: Array.from(selectedSymptoms)
            })
        });
        
        const data = await response.json();
        
        loadingSpinner.classList.add('d-none');
        diagnosisResult.classList.remove('d-none');
        
        if (data.error) {
            document.getElementById('predictedDisease').innerHTML = `
                <div class="alert alert-danger">${data.error}</div>
            `;
            return;
        }
        
        // Display predicted disease and possible conditions
        let diagnosisHtml = `
            <div class="alert alert-info">
                <h5>Primary Diagnosis:</h5>
                <p class="mb-2">${data.predicted_disease}</p>
                <p class="mb-0">Confidence: ${(data.confidence * 100).toFixed(1)}%</p>
            </div>`;

        if (data.possible_conditions && data.possible_conditions.length > 1) {
            diagnosisHtml += `
                <div class="mt-3">
                    <h5>Other Possible Conditions:</h5>
                    <ul class="list-group">
                        ${data.possible_conditions.slice(1).map(condition => `
                            <li class="list-group-item d-flex justify-content-between align-items-center">
                                ${condition.disease}
                                <span class="badge bg-primary rounded-pill">${condition.probability}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>`;
        }
        
        document.getElementById('predictedDisease').innerHTML = diagnosisHtml;
        
        // Show precautions and doctor sections
        precautionsSection.classList.remove('d-none');
        doctorSection.classList.remove('d-none');
        
        // Reset buttons
        document.getElementById('showPrecautions').classList.remove('d-none');
        document.getElementById('showDoctors').classList.remove('d-none');
        document.getElementById('precautions').innerHTML = '';
        document.getElementById('doctors').innerHTML = '';
        
    } catch (error) {
        console.error('Error:', error);
        loadingSpinner.classList.add('d-none');
        document.getElementById('predictedDisease').innerHTML = `
            <div class="alert alert-danger">An error occurred while processing your request.</div>
        `;
    }
});

// Handle precautions button click
document.getElementById('showPrecautions').addEventListener('click', async () => {
    const precautionsList = document.getElementById('precautions');
    const button = document.getElementById('showPrecautions');
    
    try {
        const disease = document.querySelector('#predictedDisease p').textContent.trim();
        const response = await fetch('/api/precautions?' + new URLSearchParams({
            disease: disease
        }));
        
        const data = await response.json();
        
        if (data.precautions && data.precautions.length > 0) {
            // Ensure at least 3 precautions
            let precautions = data.precautions;
            while (precautions.length < 3) {
                precautions.push("Consult with your healthcare provider for additional precautions");
            }
            
            precautionsList.innerHTML = `
                <div class="alert alert-success">
                    <h6 class="mb-3">
                        <i class="fas fa-shield-alt me-2"></i>
                        Recommended precautions for ${disease}:
                    </h6>
                    <div class="precautions-list">
                        ${precautions.map((precaution, index) => `
                            <div class="d-flex align-items-start mb-3">
                                <div class="precaution-number bg-success text-white rounded-circle me-3">
                                    ${index + 1}
                                </div>
                                <div class="precaution-text">
                                    ${precaution}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        } else {
            precautionsList.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No specific precautions found for this condition. Please consult a healthcare provider.
                </div>
            `;
        }
        button.classList.add('d-none');
    } catch (error) {
        console.error('Error loading precautions:', error);
        precautionsList.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Error loading precautions. Please try again.
            </div>
        `;
    }
});

// Handle doctors button click
document.getElementById('showDoctors').addEventListener('click', async () => {
    const doctorsList = document.getElementById('doctors');
    const button = document.getElementById('showDoctors');
    
    try {
        const disease = document.getElementById('predictedDisease').querySelector('p').textContent.trim();
        const response = await fetch('/api/doctors?' + new URLSearchParams({
            disease: disease
        }));
        
        const data = await response.json();
        
        if (data.doctors && data.doctors.length > 0) {
            doctorsList.innerHTML = `
                <div class="alert alert-info mb-3">
                    <h6 class="mb-3">Recommended doctors for ${disease}:</h6>
                    ${data.doctors.map(doctor => `
                        <div class="card mb-2">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-top">
                                    <div>
                                        <h6 class="card-title">
                                            <i class="fas fa-user-md me-2"></i>${doctor.name}
                                            <span class="badge bg-success ms-2">${doctor.rating}</span>
                                        </h6>
                                        <p class="card-text mb-1">
                                            <i class="fas fa-stethoscope me-2"></i>
                                            <span class="text-muted">Specialization:</span> ${doctor.specialization}
                                        </p>
                                        <p class="card-text mb-1">
                                            <i class="fas fa-clock me-2"></i>
                                            <span class="text-muted">Experience:</span> ${doctor.experience}
                                        </p>
                                        <p class="card-text mb-1">
                                            <i class="fas fa-hospital me-2"></i>
                                            <span class="text-muted">Hospital:</span> ${doctor.location}
                                        </p>
                                        <p class="card-text mb-1">
                                            <i class="fas fa-calendar-alt me-2"></i>
                                            <span class="text-muted">Available:</span> ${doctor.availability}
                                        </p>
                                        <p class="card-text mb-0">
                                            <i class="fas fa-phone me-2"></i>
                                            <span class="text-muted">Contact:</span> ${doctor.contact}
                                        </p>
                                    </div>
                                    <div class="ms-3">
                                        <a href="tel:${doctor.contact}" class="btn btn-outline-primary btn-sm">
                                            <i class="fas fa-phone"></i> Call
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } else {
            doctorsList.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    No specific doctors found for this condition. Please visit your nearest hospital.
                </div>
            `;
        }
        button.classList.add('d-none');
    } catch (error) {
        console.error('Error loading doctors:', error);
        doctorsList.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Error loading doctor information. Please try again.
            </div>
        `;
    }
});

// Handle medical scan analysis
document.getElementById('scanForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const scanFile = document.getElementById('scanFile').files[0];
    const scanType = document.getElementById('scanType').value;
    const scanResult = document.getElementById('scanResult');
    const scanPredictions = document.getElementById('scanPredictions');
    
    if (!scanFile) {
        alert('Please select a scan image');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', scanFile);
    formData.append('scan_type', scanType);
    
    try {
        const response = await fetch('/api/analyze-scan', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            scanPredictions.innerHTML = `
                <div class="alert alert-danger">${data.error}</div>
            `;
            scanResult.classList.remove('d-none');
            return;
        }
        
        displayScanResults(data, scanPredictions);
        scanResult.classList.remove('d-none');
        
    } catch (error) {
        console.error('Error analyzing scan:', error);
        scanPredictions.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Error analyzing scan. Please try again.
            </div>
        `;
        scanResult.classList.remove('d-none');
    }
});

// Handle medical report analysis
document.getElementById('reportForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const reportFile = document.getElementById('reportFile').files[0];
    const reportResult = document.getElementById('reportResult');
    const reportInfo = document.getElementById('reportInfo');
    
    if (!reportFile) {
        alert('Please select a report image');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', reportFile);
    
    try {
        const response = await fetch('/api/analyze-report', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            reportInfo.innerHTML = `
                <div class="alert alert-danger">${data.error}</div>
            `;
            reportResult.classList.remove('d-none');
            return;
        }
        
        displayReportResults(data, reportInfo);
        reportResult.classList.remove('d-none');
        
    } catch (error) {
        console.error('Error analyzing report:', error);
        reportInfo.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Error analyzing report. Please try again.
            </div>
        `;
        reportResult.classList.remove('d-none');
    }
});

function displayScanResults(data, resultDiv) {
    if (!data.predictions || data.predictions.length === 0) {
        resultDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                No significant findings detected in the scan. Please consult a healthcare professional for a complete evaluation.
            </div>`;
        return;
    }

    let html = `
        <div class="alert alert-info mb-4">
            <i class="fas fa-microscope me-2"></i>
            <strong>Scan Analysis Complete</strong>
            <p class="mb-0 mt-2">${data.message || 'Analysis has detected the following findings:'}</p>
        </div>
        <div class="findings-list">`;

    data.predictions.forEach(finding => {
        const severityClass = getSeverityClass(finding.severity);
        html += `
            <div class="finding-card">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <h5 class="mb-0 text-primary">
                        <i class="fas fa-file-medical me-2"></i>${finding.condition}
                    </h5>
                    <span class="badge bg-${severityClass}">
                        ${finding.severity.toUpperCase()} (${finding.confidence}%)
                    </span>
                </div>
                <p class="mb-0">${finding.description}</p>
                ${finding.recommendations ? `
                    <div class="mt-3">
                        <h6 class="text-muted mb-2">Recommendations:</h6>
                        <ul class="list-unstyled">
                            ${finding.recommendations.map(rec => `
                                <li><i class="fas fa-check-circle text-success me-2"></i>${rec}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>`;
    });

    html += '</div>';
    resultDiv.innerHTML = html;
}

function displayReportResults(data, resultDiv) {
    if (!data.report_info || Object.keys(data.report_info).length === 0) {
        resultDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No information could be extracted from the report. Please ensure the image is clear and contains readable text.
            </div>`;
        return;
    }

    let html = '<div class="report-sections">';
    const sections = {
        'diagnosis': { icon: 'stethoscope', title: 'Diagnosis', color: 'primary' },
        'medications': { icon: 'pills', title: 'Medications', color: 'success' },
        'recommendations': { icon: 'list-check', title: 'Recommendations', color: 'info' },
        'follow_up': { icon: 'calendar-check', title: 'Follow-up Plan', color: 'warning' }
    };

    // Check if any section has content
    const hasContent = Object.values(data.report_info).some(items => items && items.length > 0);
    
    if (!hasContent) {
        html = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                No structured information could be extracted from the report. Please ensure the image is clear and contains standard medical report sections.
            </div>`;
    } else {
        Object.entries(sections).forEach(([key, section]) => {
            const items = data.report_info[key] || [];
            if (items.length > 0) {
                html += `
                    <div class="report-section mb-4">
                        <div class="d-flex align-items-center mb-3">
                            <i class="fas fa-${section.icon} text-${section.color} me-2 fa-lg"></i>
                            <h5 class="mb-0">${section.title}</h5>
                        </div>
                        <div class="list-group">
                            ${items.map(item => `
                                <div class="list-group-item">
                                    <div class="d-flex align-items-start">
                                        <i class="fas fa-check-circle text-${section.color} me-2 mt-1"></i>
                                        <span>${item}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>`;
            }
        });
    }

    html += '</div>';
    resultDiv.innerHTML = html;
}

// File Upload Handling
document.addEventListener('DOMContentLoaded', () => {
    const dropZones = document.querySelectorAll('.drop-zone');
    
    dropZones.forEach(dropZone => {
        const fileInput = dropZone.querySelector('.file-input');
        const chooseFileBtn = dropZone.querySelector('.choose-file-btn');
        
        // Click handler for the choose file button
        chooseFileBtn.addEventListener('click', () => {
            fileInput.click();
        });
        
        // File input change handler
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleUploadedFile(dropZone, fileInput.files[0]);
            }
        });
        
        // Drag and drop handlers
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, () => {
                dropZone.classList.remove('dragover');
            });
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const file = e.dataTransfer.files[0];
            if (file) {
                fileInput.files = e.dataTransfer.files;
                handleUploadedFile(dropZone, file);
            }
        });
    });
});

function handleUploadedFile(dropZone, file) {
    const uploadType = dropZone.dataset.uploadType;
    const resultDiv = document.getElementById(`${uploadType}-results`);
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading state
    resultDiv.innerHTML = `
        <div class="loading">
            <i class="fas fa-spinner fa-spin me-2"></i>
            Analyzing ${uploadType}...
        </div>
    `;
    
    // Add scan type if it's a scan upload
    if (uploadType === 'scan') {
        const scanType = document.getElementById('scan-type').value;
        formData.append('scan_type', scanType);
    }
    
    // Update the drop zone content to show the selected file
    const dropZoneContent = dropZone.querySelector('.drop-zone-content');
    dropZoneContent.innerHTML = `
        <i class="fas fa-file-medical fa-3x mb-3 text-${uploadType === 'scan' ? 'primary' : 'info'}"></i>
        <h5 class="mb-2">Selected File:</h5>
        <p class="text-muted mb-3">${file.name}</p>
        <button type="button" class="btn btn-${uploadType === 'scan' ? 'primary' : 'info'} choose-file-btn">
            <i class="fas fa-sync-alt me-2"></i>Choose Different File
        </button>
    `;
    
    // Make API call
    fetch(`/api/analyze-${uploadType}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (uploadType === 'scan') {
            displayScanResults(data, resultDiv);
        } else {
            displayReportResults(data, resultDiv);
        }
    })
    .catch(error => {
        console.error(`Error analyzing ${uploadType}:`, error);
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                Error analyzing ${uploadType}. Please try again.
            </div>
        `;
    });
}

function getSeverityClass(severity) {
    switch (severity.toLowerCase()) {
        case 'high':
            return 'danger';
        case 'medium':
            return 'warning';
        case 'low':
            return 'success';
        default:
            return 'info';
    }
}