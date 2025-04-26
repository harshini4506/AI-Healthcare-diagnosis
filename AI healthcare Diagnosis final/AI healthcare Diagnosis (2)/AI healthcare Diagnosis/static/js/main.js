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

// Chat functionality
let chatHistory = [];
let isProcessing = false;

document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
});

function initializeChat() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const suggestionsContainer = document.getElementById('chat-suggestions');

    // Add welcome message
    appendMessage('assistant', 'Hello! I\'m your mental health assistant. How can I help you today?');
    
    // Initialize suggestions
    updateSuggestions([
        "I'm feeling anxious",
        "I'm having trouble sleeping",
        "I feel lonely",
        "I'm stressed about work",
        "I need relationship advice",
        "How can you help me?"
    ]);

    chatForm.addEventListener('submit', handleChatSubmit);
    chatInput.addEventListener('keypress', handleInputKeypress);
}

async function handleChatSubmit(e) {
    e.preventDefault();
    
    if (isProcessing) return;
    
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Clear input and disable processing
    chatInput.value = '';
    isProcessing = true;
    
    try {
        // Add user message
        appendMessage('user', message);
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send message to server
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        // Remove typing indicator
        hideTypingIndicator();
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            appendMessage('error', data.error);
            return;
        }
        
        // Display bot response
        if (data.messages && data.messages.length > 0) {
            data.messages.forEach(msg => {
                if (msg.role === 'assistant') {
                    appendMessage('assistant', msg.content);
                }
            });
        }
        
        // Update suggestions
        if (data.suggestions) {
            updateSuggestions(data.suggestions);
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        hideTypingIndicator();
        appendMessage('error', 'I apologize, but I encountered a technical difficulty. Please try again.');
    } finally {
        isProcessing = false;
    }
}

function handleInputKeypress(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
    }
}

function appendMessage(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    if (role === 'error') {
        messageDiv.innerHTML = `
            <div class="alert alert-danger mb-0">
                <i class="fas fa-exclamation-circle me-2"></i>${content}
            </div>
        `;
    } else {
        const icon = role === 'user' ? 'fa-user' : 'fa-robot';
        messageDiv.innerHTML = `
            <div class="message-content">
                <i class="fas ${icon} message-icon"></i>
                <div class="message-text">${formatMessageContent(content)}</div>
            </div>
        `;
    }
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function formatMessageContent(content) {
    // Format crisis resources
    if (content.includes('IMMEDIATE ACTIONS:')) {
        return `<div class="crisis-message">${content}</div>`;
    }
    
    // Convert bullet points to HTML list
    content = content.replace(/^- (.+)$/gm, '<li>$1</li>');
    if (content.includes('<li>')) {
        content = '<ul>' + content + '</ul>';
    }
    
    // Convert numbered points to HTML ordered list
    content = content.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');
    if (content.includes('<li>')) {
        content = content.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
    }
    
    // Format coping strategies
    if (content.includes('coping strategies:')) {
        content = `<div class="coping-strategies">${content}</div>`;
    }
    
    // Format resource lists
    if (content.includes('resources:')) {
        content = `<div class="resources-list">${content}</div>`;
    }
    
    // Convert line breaks to paragraphs
    content = content.split('\n\n').map(para => 
        para.trim().startsWith('<') ? para : `<p>${para}</p>`
    ).join('');
    
    return content;
}

function updateSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('chat-suggestions');
    if (!suggestionsContainer) return;
    
    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const button = document.createElement('button');
        button.className = 'suggestion-btn';
        button.textContent = suggestion;
        button.onclick = () => {
            document.getElementById('chat-input').value = suggestion;
            document.getElementById('chat-form').dispatchEvent(new Event('submit'));
        };
        suggestionsContainer.appendChild(button);
    });
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <i class="fas fa-robot message-icon"></i>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
}

function hideTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Handle file uploads for both scan and report
document.querySelectorAll('.drop-zone').forEach(dropZone => {
    const fileInput = dropZone.querySelector('.file-input');
    const uploadType = dropZone.dataset.uploadType;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle clicked files
    fileInput.addEventListener('change', function(e) {
        handleFiles(this.files);
    });
    
    // Handle button click
    dropZone.querySelector('.choose-file-btn').addEventListener('click', () => {
        fileInput.click();
    });
    
    function preventDefaults (e) {
    e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight(e) {
        dropZone.classList.add('dragover');
    }
    
    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    function handleFiles(files) {
        if (files.length) {
            const file = files[0];
            uploadFile(file);
        }
    }
    
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        if (uploadType === 'scan') {
            const scanType = document.getElementById('scan-type').value;
            formData.append('scan_type', scanType);
        }
        
        const resultContainer = document.getElementById(`${uploadType}-results`);
        
        // Show loading state
        resultContainer.innerHTML = `
            <div class="loading">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Analyzing ${uploadType}...
            </div>
        `;
        
        // Update drop zone content
        const dropZoneContent = dropZone.querySelector('.drop-zone-content');
        dropZoneContent.innerHTML = `
            <i class="fas fa-file-medical fa-3x mb-3"></i>
            <h5>Selected File:</h5>
            <p class="text-muted mb-3">${file.name}</p>
            <button type="button" class="btn btn-${uploadType === 'scan' ? 'primary' : 'info'} choose-file-btn">
                Choose Different File
            </button>
        `;
        
        // Make API call
        fetch(`/api/upload-${uploadType}`, {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
        if (data.error) {
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${data.error}
                    </div>
            `;
            return;
        }
        
            if (uploadType === 'scan') {
                displayScanResults(data, resultContainer);
            } else {
                displayReportResults(data, resultContainer);
            }
        })
        .catch(error => {
            console.error(`Error analyzing ${uploadType}:`, error);
            resultContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                    Error analyzing ${uploadType}. Please try again.
            </div>
        `;
        });
    }
});

function displayScanResults(data, container) {
    let html = '<div class="analysis-results">';
    
    // Main Analysis Summary
    html += `
        <div class="section">
            <h3>Analysis Summary</h3>
            <div class="alert alert-info">
                <p class="mb-2"><strong>${data.analysis_summary.main_finding}</strong></p>
                <p class="mb-2">${data.analysis_summary.confidence}</p>
                <p class="mb-0">${data.analysis_summary.severity_level}</p>
            </div>
        </div>
    `;
    
    // Detailed Findings
    html += '<div class="section">';
    html += '<h3>Detailed Findings</h3>';

    // Primary Condition and Severity
        html += `
        <div class="mb-3">
            <h4>Primary Condition</h4>
            <div class="d-flex align-items-center">
                <span class="severity ${data.findings.severity.toLowerCase()}">
                    ${data.findings.severity.toUpperCase()}
                    </span>
                <span class="ms-3">${data.findings.primary_condition}</span>
                </div>
            <p class="mt-2">Confidence Score: ${(data.findings.confidence_score * 100).toFixed(1)}%</p>
                    </div>
    `;
    
    // Add findings
    if (data.findings.normal_structures.length > 0) {
        html += '<div class="mb-3">';
        html += '<h4>Normal Findings</h4>';
        html += '<ul>';
        data.findings.normal_structures.forEach(structure => {
            html += `<li><i class="fas fa-check-circle"></i> ${structure}</li>`;
    });
        html += '</ul>';
    html += '</div>';
    }
    
    if (data.findings.abnormalities.length > 0) {
        html += '<div class="mb-3">';
        html += '<h4>Abnormal Findings</h4>';
        html += '<ul>';
        data.findings.abnormalities.forEach(abnormality => {
            html += `<li><i class="fas fa-exclamation-triangle"></i> ${abnormality}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    html += '</div>';
    
    // Recommendations
    if (data.recommendations.length > 0) {
        html += '<div class="section">';
        html += '<h3>Recommendations</h3>';
        html += '<ul>';
        data.recommendations.forEach(recommendation => {
            html += `<li><i class="fas fa-clipboard-list"></i> ${recommendation}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }

    html += '</div>';
    container.innerHTML = html;
}

function displayReportResults(data, container) {
    let html = '<div class="analysis-results">';
    
    // Patient Summary
    html += `
        <div class="section">
            <h3>Patient Summary</h3>
            <div class="alert alert-info">
                <p class="mb-2"><strong>Condition: </strong>${data.patient_summary.condition}</p>
                <div class="mt-3">
                    <h4>Vital Signs</h4>
                    <ul class="list-unstyled">
                        <li><i class="fas fa-heartbeat me-2"></i>Blood Pressure: ${data.patient_summary.vital_signs.blood_pressure}</li>
                        <li><i class="fas fa-heart me-2"></i>Heart Rate: ${data.patient_summary.vital_signs.heart_rate}</li>
                        <li><i class="fas fa-thermometer-half me-2"></i>Temperature: ${data.patient_summary.vital_signs.temperature}</li>
                    </ul>
                </div>
            </div>
        </div>
    `;
        
    // Medical History
    if (data.medical_history.length > 0) {
        html += '<div class="section">';
        html += '<h3>Medical History</h3>';
        html += '<ul>';
        data.medical_history.forEach(item => {
            html += `<li><i class="fas fa-history"></i> ${item}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    // Current Status
    html += '<div class="section">';
    html += '<h3>Current Status</h3>';
    
    if (data.current_status.symptoms.length > 0) {
        html += '<h4>Symptoms</h4>';
        html += '<ul>';
        data.current_status.symptoms.forEach(symptom => {
            html += `<li><i class="fas fa-notes-medical"></i> ${symptom}</li>`;
        });
        html += '</ul>';
    }
    
    if (data.current_status.medications.length > 0) {
        html += '<h4>Medications</h4>';
        html += '<ul>';
        data.current_status.medications.forEach(medication => {
            html += `<li><i class="fas fa-pills"></i> ${medication}</li>`;
        });
        html += '</ul>';
    }
    html += '</div>';
    
    // Treatment Plan
    html += '<div class="section">';
    html += '<h3>Treatment Plan</h3>';
    
    if (data.treatment_plan.immediate_actions.length > 0) {
        html += '<h4>Immediate Actions</h4>';
        html += '<ul>';
        data.treatment_plan.immediate_actions.forEach(action => {
            html += `<li><i class="fas fa-check"></i> ${action}</li>`;
        });
        html += '</ul>';
    }
    
    if (data.treatment_plan.long_term_goals.length > 0) {
        html += '<h4>Long-term Goals</h4>';
        html += '<ul>';
        data.treatment_plan.long_term_goals.forEach(goal => {
            html += `<li><i class="fas fa-bullseye"></i> ${goal}</li>`;
        });
        html += '</ul>';
    }
    html += '</div>';
    
    // Recommendations
    if (data.recommendations.length > 0) {
        html += '<div class="section">';
        html += '<h3>Recommendations</h3>';
        html += '<ul>';
        data.recommendations.forEach(recommendation => {
            html += `<li><i class="fas fa-clipboard-list"></i> ${recommendation}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    html += '</div>';
    container.innerHTML = html;
}

async function handleScanAnalysis(event) {
    event.preventDefault();
    
    const fileInput = document.getElementById('scan-file');
    const scanType = document.getElementById('scan-type').value;
    const resultsDiv = document.getElementById('scan-results');
    const loadingDiv = document.getElementById('loading-indicator');
    
    if (!fileInput.files.length) {
        showError('Please select a file to analyze');
        return;
    }
    
    // Prevent multiple submissions
    if (loadingDiv.style.display === 'block') {
        return;
    }
    
    try {
        // Show loading indicator
        loadingDiv.style.display = 'block';
        resultsDiv.innerHTML = '';
    
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        formData.append('scan_type', scanType);
        
        const response = await fetch('/api/upload-scan', {
                    method: 'POST',
            body: formData
                });
    
                const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Analysis failed');
        }
        
        if (data.status === 'error') {
            throw new Error(data.message);
        }
        
        const results = data.data;
        
        // Create results HTML
        let resultsHTML = `
            <div class="analysis-results">
                <h3>Scan Analysis Results</h3>
                <div class="result-section">
                    <h4>Primary Findings</h4>
                    <p class="confidence">Confidence Level: ${(results.findings.confidence_score * 100).toFixed(1)}%</p>
                    <p class="severity ${results.findings.severity.toLowerCase()}">
                        Severity: ${results.findings.severity.toUpperCase()}
                    </p>
                </div>`;
        
        if (results.findings.normal_structures && results.findings.normal_structures.length > 0) {
            resultsHTML += `
                <div class="result-section">
                    <h4>Normal Findings</h4>
                    <ul class="normal-findings">
                        ${results.findings.normal_structures.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>`;
        }
        
        if (results.findings.abnormalities && results.findings.abnormalities.length > 0) {
            resultsHTML += `
                <div class="result-section">
                    <h4>Detected Abnormalities</h4>
                    <ul class="abnormalities">
                        ${results.findings.abnormalities.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>`;
        }
        
        resultsHTML += `
            <div class="result-section">
                <h4>Analysis Summary</h4>
                <p class="main-finding">${results.analysis_summary.main_finding}</p>
                <div class="key-observations">
                    <h5>Key Observations:</h5>
                    <ul>
                        ${results.analysis_summary.key_observations.map(item => `<li>${item}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div class="result-section">
                <h4>Recommendations</h4>
                <ul class="recommendations">
                    ${results.recommendations.map(item => `<li>${item}</li>`).join('')}
                </ul>
            </div>
        </div>`;
        
        resultsDiv.innerHTML = resultsHTML;
        
    } catch (error) {
        showError(error.message || 'An error occurred during analysis');
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function showError(message) {
    const resultsDiv = document.getElementById('scan-results');
    resultsDiv.innerHTML = `<div class="error-message">${message}</div>`;
}

// Add event listener to file input
document.getElementById('scan-file').addEventListener('change', handleScanAnalysis);