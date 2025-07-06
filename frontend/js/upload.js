// Upload page functionality
class ResumeUploader {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadProgress = document.getElementById('upload-progress');
        this.uploadResult = document.getElementById('upload-result');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.resultTitle = document.getElementById('result-title');
        this.resultMessage = document.getElementById('result-message');
        this.analyzeBtn = document.getElementById('analyze-btn');
        this.uploadAnotherBtn = document.getElementById('upload-another');
        
        this.currentResumeId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });

        // Click to upload
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Result buttons
        this.analyzeBtn.addEventListener('click', () => {
            if (this.currentResumeId) {
                this.analyzeResume(this.currentResumeId);
            }
        });

        this.uploadAnotherBtn.addEventListener('click', () => {
            this.resetUpload();
        });
    }

    handleFile(file) {
        // Validate file
        if (!this.validateFile(file)) {
            return;
        }

        // Show progress
        this.showProgress();
        
        // Upload file
        this.uploadFile(file);
    }

    validateFile(file) {
        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        if (!allowedTypes.includes(file.type)) {
            this.showError('Please select a valid file type (PDF, DOCX, or DOC)');
            return false;
        }

        if (file.size > maxSize) {
            this.showError('File size must be less than 10MB');
            return false;
        }

        return true;
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/v1/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.currentResumeId = result.resume_id;
            this.showSuccess(result);

        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Upload failed. Please try again.');
        }
    }

    async analyzeResume(resumeId) {
        this.analyzeBtn.disabled = true;
        this.analyzeBtn.textContent = 'Analyzing...';

        try {
            const response = await fetch(`/api/v1/analyze/${resumeId}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            const result = await response.json();
            this.showAnalysisSuccess(result);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Analysis failed. Please try again.');
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.textContent = 'Analyze Resume';
        }
    }

    showProgress() {
        this.uploadArea.style.display = 'none';
        this.uploadProgress.style.display = 'block';
        this.uploadResult.style.display = 'none';
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 30;
            if (progress >= 100) {
                progress = 100;
                clearInterval(interval);
            }
            this.updateProgress(progress);
        }, 200);
    }

    updateProgress(percent) {
        this.progressFill.style.width = `${percent}%`;
        this.progressFill.setAttribute('aria-valuenow', Math.round(percent));
        this.progressText.textContent = `${Math.round(percent)}%`;
    }

    showSuccess(result) {
        this.uploadProgress.style.display = 'none';
        this.uploadResult.style.display = 'block';
        
        this.resultTitle.textContent = 'Upload Successful!';
        this.resultMessage.textContent = `Resume "${result.filename}" uploaded successfully. Ready for analysis.`;
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.textContent = 'Analyze Resume';
    }

    showAnalysisSuccess(result) {
        this.resultTitle.textContent = 'Analysis Complete!';
        this.resultMessage.textContent = 'Your resume has been analyzed successfully. View detailed results below.';
        
        // Show analysis results
        this.displayAnalysisResults(result.analysis);
    }

    displayAnalysisResults(analysis) {
        const resultDiv = document.createElement('div');
        resultDiv.className = 'analysis-results';
        resultDiv.innerHTML = `
            <div class="score-overview">
                <h4>Overall Score: ${analysis.overall_score}/100</h4>
                <div class="category-scores">
                    <div class="score-item">
                        <span>Completeness:</span>
                        <span>${analysis.category_scores.completeness}/100</span>
                    </div>
                    <div class="score-item">
                        <span>Technical Skills:</span>
                        <span>${analysis.category_scores.technical_skills}/100</span>
                    </div>
                    <div class="score-item">
                        <span>Experience:</span>
                        <span>${analysis.category_scores.experience}/100</span>
                    </div>
                    <div class="score-item">
                        <span>Education:</span>
                        <span>${analysis.category_scores.education}/100</span>
                    </div>
                    <div class="score-item">
                        <span>Presentation:</span>
                        <span>${analysis.category_scores.presentation}/100</span>
                    </div>
                </div>
            </div>
            <div class="feedback-section">
                <h4>Feedback</h4>
                <p>${analysis.feedback}</p>
            </div>
            <div class="suggestions-section">
                <h4>Suggestions</h4>
                <ul>
                    ${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                </ul>
            </div>
            <div class="result-actions">
                <button class="btn btn-primary" onclick="window.location.href='results.html'">View All Results</button>
                <button class="btn btn-secondary" onclick="uploader.resetUpload()">Upload Another</button>
            </div>
        `;
        
        this.uploadResult.appendChild(resultDiv);
    }

    showError(message) {
        this.uploadProgress.style.display = 'none';
        this.uploadResult.style.display = 'block';
        
        this.resultTitle.textContent = 'Upload Failed';
        this.resultTitle.style.color = '#e74c3c';
        this.resultMessage.textContent = message;
        
        this.analyzeBtn.style.display = 'none';
        this.uploadAnotherBtn.textContent = 'Try Again';
    }

    resetUpload() {
        this.uploadArea.style.display = 'block';
        this.uploadProgress.style.display = 'none';
        this.uploadResult.style.display = 'none';
        
        this.fileInput.value = '';
        this.currentResumeId = null;
        this.progressFill.style.width = '0%';
        this.progressText.textContent = '0%';
        
        this.resultTitle.style.color = '';
        this.analyzeBtn.style.display = 'inline-block';
        this.analyzeBtn.disabled = false;
        this.analyzeBtn.textContent = 'Analyze Resume';
        this.uploadAnotherBtn.textContent = 'Upload Another';
        
        // Remove analysis results if they exist
        const analysisResults = this.uploadResult.querySelector('.analysis-results');
        if (analysisResults) {
            analysisResults.remove();
        }
    }
}

// Initialize uploader when page loads
let uploader;
document.addEventListener('DOMContentLoaded', () => {
    uploader = new ResumeUploader();
});
