// API Configuration - Update with your Railway URL
const API_BASE_URL = 'https://interview-agent-production.up.railway.app'; // Your Railway URL here

// Global state
let currentInterviewId = null;
let questionCount = 0;
let scores = [];

// Utility Functions
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('active');
}

function showError(message) {
    alert('Error: ' + message);
}

// Start Interview
async function startInterview(event) {
    event.preventDefault();
    
    const formData = {
        candidate_name: document.getElementById('candidateName').value,
        candidate_email: document.getElementById('candidateEmail').value,
        job_role: document.getElementById('jobRole').value,
        experience_years: parseInt(document.getElementById('experienceYears').value),
        job_description: document.getElementById('jobDescription').value || `${document.getElementById('jobRole').value} position`,
        resume_summary: document.getElementById('resumeSummary').value || ''
    };
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/interview/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentInterviewId = data.interview_id;
            questionCount = 1;
            
            // Update UI
            document.getElementById('displayName').textContent = formData.candidate_name;
            document.getElementById('currentPhase').textContent = capitalizeFirst(data.phase);
            document.getElementById('questionCounter').textContent = `Question ${questionCount}`;
            
            // Add first question to chat
            addMessageToChat('interviewer', data.first_question);
            
            // Update phase
            updatePhase(data.phase);
            
            // Show interview screen
            showScreen('interviewScreen');
        } else {
            showError(data.message || 'Failed to start interview');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to connect to server. Make sure the backend is running.');
    } finally {
        hideLoading();
    }
}

// Submit Answer
async function submitAnswer() {
    const answerInput = document.getElementById('answerInput');
    const answer = answerInput.value.trim();
    
    if (!answer) {
        alert('Please enter your answer');
        return;
    }
    
    // Disable input while processing
    answerInput.disabled = true;
    document.getElementById('sendBtn').disabled = true;
    
    // Add answer to chat
    addMessageToChat('candidate', answer);
    
    // Clear input
    answerInput.value = '';
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/interview/answer`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                interview_id: currentInterviewId,
                answer: answer
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (data.interview_complete) {
                // Interview is complete, show report
                displayReport(data.final_report);
                showScreen('reportScreen');
            } else {
                // Continue interview
                questionCount++;
                document.getElementById('questionCounter').textContent = `Question ${questionCount}`;
                
                // Update phase if changed
                updatePhase(data.phase);
                
                // Add next question to chat
                addMessageToChat('interviewer', data.next_question);
                
                // Update feedback
                if (data.feedback) {
                    displayFeedback(data.feedback, data.score);
                }
                
                // Update score
                if (data.score) {
                    scores.push(data.score);
                    updateAverageScore();
                }
            }
        } else {
            showError(data.message || 'Failed to submit answer');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to submit answer');
    } finally {
        hideLoading();
        answerInput.disabled = false;
        document.getElementById('sendBtn').disabled = false;
        answerInput.focus();
    }
}

// Add message to chat
function addMessageToChat(role, message) {
    const chatContainer = document.getElementById('chatContainer');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const avatar = role === 'interviewer' ? '🤖' : '👤';
    const sender = role === 'interviewer' ? 'AI Interviewer' : 'You';
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-sender">${sender}</div>
            <div class="message-text">${message}</div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Update phase indicator
function updatePhase(phase) {
    document.getElementById('currentPhase').textContent = capitalizeFirst(phase.replace('_', ' '));
    
    // Update progress sidebar
    document.querySelectorAll('.phase-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.phase === phase) {
            item.classList.add('active');
        }
    });
}

// Display feedback
function displayFeedback(feedback, score) {
    const feedbackArea = document.getElementById('feedbackArea');
    
    const scoreClass = score >= 75 ? 'excellent' : score >= 60 ? 'good' : score >= 45 ? 'average' : 'needs-improvement';
    
    feedbackArea.innerHTML = `
        <div class="feedback-item">
            <div class="feedback-score ${scoreClass}">
                <strong>Score:</strong> ${score}/100
            </div>
            <div class="feedback-text">
                ${feedback}
            </div>
        </div>
    `;
}

// Update average score
function updateAverageScore() {
    if (scores.length === 0) return;
    
    const avgScore = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    document.getElementById('currentScore').textContent = avgScore;
}

// Display report
function displayReport(report) {
    const reportContent = document.getElementById('reportContent');
    
    const overallScore = Math.round(report.overall_score);
    const scoreClass = overallScore >= 75 ? 'excellent' : overallScore >= 60 ? 'good' : overallScore >= 45 ? 'average' : 'needs-improvement';
    
    let html = `
        <div class="report-section">
            <h3>Overall Performance</h3>
            <div style="text-align: center; padding: 20px;">
                <div style="display: inline-block; width: 150px; height: 150px; border-radius: 50%; 
                     background: linear-gradient(135deg, #4F46E5, #4338CA); 
                     display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3);">
                    <span style="font-size: 48px; font-weight: 700; color: white;">${overallScore}</span>
                </div>
                <p style="margin-top: 20px; font-size: 18px; color: #6B7280;">
                    <strong>Recommendation:</strong> ${report.recommendation || 'Pending Review'}
                </p>
            </div>
        </div>
        
        <div class="report-section">
            <h3>Dimension Scores</h3>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
    `;
    
    if (report.dimension_scores) {
        for (const [dimension, score] of Object.entries(report.dimension_scores)) {
            const dimName = capitalizeFirst(dimension.replace(/_/g, ' '));
            html += `
                <div style="padding: 15px; background: #F9FAFB; border-radius: 8px;">
                    <strong>${dimName}:</strong> ${Math.round(score)}/100
                    <div style="background: #E5E7EB; height: 8px; border-radius: 4px; margin-top: 8px;">
                        <div style="background: #4F46E5; height: 100%; width: ${score}%; border-radius: 4px;"></div>
                    </div>
                </div>
            `;
        }
    }
    
    html += `
            </div>
        </div>
        
        <div class="report-section">
            <h3>Strengths</h3>
            <ul style="list-style: none; padding: 0;">
    `;
    
    if (report.strengths && report.strengths.length > 0) {
        report.strengths.forEach(strength => {
            html += `<li style="padding: 8px 0; color: #059669;">✓ ${strength}</li>`;
        });
    } else {
        html += '<li>Information not available</li>';
    }
    
    html += `
            </ul>
        </div>
        
        <div class="report-section">
            <h3>Areas for Improvement</h3>
            <ul style="list-style: none; padding: 0;">
    `;
    
    if (report.weaknesses && report.weaknesses.length > 0) {
        report.weaknesses.forEach(weakness => {
            html += `<li style="padding: 8px 0; color: #DC2626;">• ${weakness}</li>`;
        });
    } else {
        html += '<li>No major areas identified</li>';
    }
    
    html += `
            </ul>
        </div>
        
        <div class="report-section">
            <h3>Detailed Assessment</h3>
            <p><strong>Technical Level:</strong> ${report.technical_assessment || 'Not assessed'}</p>
            <p><strong>Communication Quality:</strong> ${report.communication_quality || 'Not assessed'}</p>
            <p><strong>Interview Duration:</strong> ${report.duration_estimate || 'N/A'}</p>
            <p><strong>Total Questions:</strong> ${report.total_questions || questionCount}</p>
        </div>
        
        <div class="report-section">
            <h3>Next Steps</h3>
            <p>${report.reasoning || 'Detailed feedback will be provided by the hiring team.'}</p>
    `;
    
    if (report.next_steps && report.next_steps.length > 0) {
        html += '<ul>';
        report.next_steps.forEach(step => {
            html += `<li>${step}</li>`;
        });
        html += '</ul>';
    }
    
    html += `
        </div>
    `;
    
    reportContent.innerHTML = html;
}

// Download report
function downloadReport() {
    alert('Report download feature - would export as PDF in production');
}

// Dashboard functions
async function showDashboard() {
    showScreen('dashboardScreen');
    await loadDashboardData();
}

function hideDashboard() {
    showScreen('startScreen');
}

async function loadDashboardData() {
    showLoading();
    
    try {
        // Load statistics
        const statsResponse = await fetch(`${API_BASE_URL}/api/interviews/list?limit=50`);
        const statsData = await statsResponse.json();
        
        if (statsData.success) {
            const interviews = statsData.interviews;
            
            // Calculate stats
            const total = interviews.length;
            const completed = interviews.filter(i => i.status === 'completed').length;
            const inProgress = total - completed;
            
            // Update stats cards
            document.getElementById('totalInterviews').textContent = total;
            document.getElementById('completedInterviews').textContent = completed;
            document.getElementById('inProgressInterviews').textContent = inProgress;
            
            // Populate table
            const tbody = document.getElementById('interviewsTableBody');
            tbody.innerHTML = '';
            
            interviews.slice(0, 10).forEach(interview => {
                const row = document.createElement('tr');
                const date = new Date(interview.created_at).toLocaleDateString();
                const statusBadge = interview.status === 'completed' ? 
                    '<span style="color: #059669;">✓ Completed</span>' : 
                    '<span style="color: #F59E0B;">⏳ In Progress</span>';
                
                row.innerHTML = `
                    <td>${interview.candidate_name}</td>
                    <td>${interview.job_role}</td>
                    <td>${date}</td>
                    <td>${statusBadge}</td>
                    <td><button class="btn-secondary" style="padding: 6px 12px; font-size: 14px;" onclick="viewReport('${interview.interview_id}')">View</button></td>
                `;
                
                tbody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    } finally {
        hideLoading();
    }
}

async function viewReport(interviewId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/interview/${interviewId}/report`);
        const data = await response.json();
        
        if (data.success) {
            displayReport(data.report);
            showScreen('reportScreen');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Failed to load report');
    } finally {
        hideLoading();
    }
}

// Handle Enter key in textarea
function handleKeyPress(event) {
    if (event.ctrlKey && event.key === 'Enter') {
        submitAnswer();
    }
}

// Utility function
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Interview Agent Frontend Loaded');
    
    // Focus on first input
    document.getElementById('candidateName').focus();
});