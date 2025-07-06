// Results page functionality
class ResultsManager {
    constructor() {
        this.resultsGrid = document.getElementById('results-grid');
        this.loading = document.getElementById('loading');
        this.noResults = document.getElementById('no-results');
        this.modal = document.getElementById('results-modal');
        this.modalBody = document.getElementById('modal-body');
        this.closeModal = document.getElementById('close-modal');
        this.filterButtons = document.querySelectorAll('.filter-btn');
        
        this.resumes = [];
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadResumes();
    }

    setupEventListeners() {
        // Filter buttons
        this.filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.filterButtons.forEach(b => {
                    b.classList.remove('active');
                    b.setAttribute('aria-selected', 'false');
                });
                btn.classList.add('active');
                btn.setAttribute('aria-selected', 'true');
                this.currentFilter = btn.dataset.filter;
                this.filterResumes();
            });
        });

        // Modal close
        this.closeModal.addEventListener('click', () => {
            this.modal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.modal.style.display = 'none';
            }
        });
    }

    async loadResumes() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/api/v1/resumes');
            if (!response.ok) {
                throw new Error('Failed to load resumes');
            }

            this.resumes = await response.json();
            this.displayResumes();
            
        } catch (error) {
            console.error('Error loading resumes:', error);
            this.showError('Failed to load resumes. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }

    displayResumes() {
        if (this.resumes.length === 0) {
            this.showNoResults();
            return;
        }

        this.resultsGrid.innerHTML = '';
        
        this.resumes.forEach(resume => {
            const card = this.createResumeCard(resume);
            this.resultsGrid.appendChild(card);
        });
    }

    createResumeCard(resume) {
        const card = document.createElement('article');
        card.className = 'result-card';
        
        const statusClass = resume.is_analyzed ? 'status-analyzed' : 'status-pending';
        const statusText = resume.is_analyzed ? 'Analyzed' : 'Pending';
        
        const uploadDate = new Date(resume.upload_date).toLocaleDateString();
        const fileSize = this.formatFileSize(resume.file_size);
        
        let scoreHtml = '';
        if (resume.analysis) {
            scoreHtml = `
                <div class="result-score">
                    <span class="score-label">Overall Score:</span>
                    <span class="score-value" aria-label="Overall score ${resume.analysis.overall_score} out of 10">${resume.analysis.overall_score}/10</span>
                </div>
            `;
        }

        card.innerHTML = `
            <header class="result-header">
                <h3 class="result-title">${resume.filename}</h3>
                <span class="result-status ${statusClass}" aria-label="Status: ${statusText}">${statusText}</span>
            </header>
            <div class="result-info">
                <p><strong>Uploaded:</strong> ${uploadDate}</p>
                <p><strong>Size:</strong> ${fileSize}</p>
                ${scoreHtml}
            </div>
            <footer class="result-actions">
                ${resume.is_analyzed ? 
                    `<button class="btn btn-small btn-primary" onclick="resultsManager.viewDetails('${resume.id}')" aria-label="View details for ${resume.filename}">View Details</button>` :
                    `<button class="btn btn-small btn-primary" onclick="resultsManager.analyzeResume('${resume.id}')" aria-label="Analyze ${resume.filename}">Analyze Now</button>`
                }
                <button class="btn btn-small btn-secondary" onclick="resultsManager.deleteResume('${resume.id}')" aria-label="Delete ${resume.filename}">Delete</button>
            </footer>
        `;
        
        return card;
    }

    filterResumes() {
        const filteredResumes = this.resumes.filter(resume => {
            switch (this.currentFilter) {
                case 'analyzed':
                    return resume.is_analyzed;
                case 'pending':
                    return !resume.is_analyzed;
                default:
                    return true;
            }
        });

        this.resultsGrid.innerHTML = '';
        
        if (filteredResumes.length === 0) {
            this.showNoResults();
            return;
        }

        filteredResumes.forEach(resume => {
            const card = this.createResumeCard(resume);
            this.resultsGrid.appendChild(card);
        });
    }

    async viewDetails(resumeId) {
        try {
            const response = await fetch(`/api/v1/resumes/${resumeId}`);
            if (!response.ok) {
                throw new Error('Failed to load resume details');
            }

            const resume = await response.json();
            this.showModal(resume);
            
        } catch (error) {
            console.error('Error loading resume details:', error);
            this.showError('Failed to load resume details.');
        }
    }

    async analyzeResume(resumeId) {
        try {
            const response = await fetch(`/api/v1/analyze/${resumeId}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Analysis failed');
            }

            const result = await response.json();
            this.showAnalysisSuccess(result);
            
            // Reload resumes to update the display
            setTimeout(() => {
                this.loadResumes();
            }, 1000);
            
        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Analysis failed. Please try again.');
        }
    }

    async deleteResume(resumeId) {
        if (!confirm('Are you sure you want to delete this resume?')) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/resumes/${resumeId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error('Delete failed');
            }

            // Remove from local array and reload
            this.resumes = this.resumes.filter(r => r.id !== resumeId);
            this.displayResumes();
            
        } catch (error) {
            console.error('Delete error:', error);
            this.showError('Failed to delete resume.');
        }
    }

    showModal(resume) {
        const analysis = resume.analysis;
        let modalContent = `
            <header>
                <h2 id="modal-title">${resume.filename}</h2>
            </header>
            <section class="resume-details">
                <p><strong>Upload Date:</strong> ${new Date(resume.upload_date).toLocaleString()}</p>
                <p><strong>File Size:</strong> ${this.formatFileSize(resume.file_size)}</p>
            </section>
        `;

        if (analysis) {
            modalContent += `
                <section class="analysis-details">
                    <h3>Analysis Results</h3>
                    <div class="overall-score">
                        <h4>Overall Score: <span aria-label="Overall score ${analysis.overall_score} out of 10">${analysis.overall_score}/10</span></h4>
                    </div>
                    <section class="category-scores">
                        <h4>Category Scores:</h4>
                        <div class="score-grid" role="list" aria-label="Category scores">
                            <div class="score-item" role="listitem">
                                <span>Completeness:</span>
                                <span aria-label="Completeness score ${analysis.category_scores.completeness} out of 10">${analysis.category_scores.completeness}/10</span>
                            </div>
                            <div class="score-item" role="listitem">
                                <span>Technical Skills:</span>
                                <span aria-label="Technical skills score ${analysis.category_scores.technical_skills} out of 10">${analysis.category_scores.technical_skills}/10</span>
                            </div>
                            <div class="score-item" role="listitem">
                                <span>Experience:</span>
                                <span aria-label="Experience score ${analysis.category_scores.experience} out of 10">${analysis.category_scores.experience}/10</span>
                            </div>
                            <div class="score-item" role="listitem">
                                <span>Education:</span>
                                <span aria-label="Education score ${analysis.category_scores.education} out of 10">${analysis.category_scores.education}/10</span>
                            </div>
                            <div class="score-item" role="listitem">
                                <span>Presentation:</span>
                                <span aria-label="Presentation score ${analysis.category_scores.presentation} out of 10">${analysis.category_scores.presentation}/10</span>
                            </div>
                        </div>
                    </section>
                    <section class="feedback-section">
                        <h4>Feedback:</h4>
                        <p>${analysis.feedback}</p>
                    </section>
                    <section class="suggestions-section">
                        <h4>Suggestions:</h4>
                        <ul>
                            ${analysis.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    </section>
                </section>
            `;
        } else {
            modalContent += `
                <section class="no-analysis">
                    <p>This resume hasn't been analyzed yet.</p>
                    <button class="btn btn-primary" onclick="resultsManager.analyzeResume('${resume.id}')" aria-label="Analyze ${resume.filename}">Analyze Now</button>
                </section>
            `;
        }

        this.modalBody.innerHTML = modalContent;
        this.modal.style.display = 'block';
    }

    showAnalysisSuccess(result) {
        // Show a temporary success message
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `
            <div class="success-content">
                <h3>Analysis Complete!</h3>
                <p>Resume has been analyzed successfully.</p>
            </div>
        `;
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    showLoading(show) {
        this.loading.style.display = show ? 'block' : 'none';
        this.resultsGrid.style.display = show ? 'none' : 'grid';
    }

    showNoResults() {
        this.noResults.style.display = 'block';
        this.resultsGrid.style.display = 'none';
    }

    showError(message) {
        // Show error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <div class="error-content">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
        
        document.body.appendChild(errorDiv);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

// Initialize results manager when page loads
let resultsManager;
document.addEventListener('DOMContentLoaded', () => {
    resultsManager = new ResultsManager();
});
