// Main page functionality
class MainPage {
    constructor() {
        this.statsContainer = document.getElementById('stats-container');
        this.totalResumes = document.getElementById('total-resumes');
        this.analyzedResumes = document.getElementById('analyzed-resumes');
        this.analysisRate = document.getElementById('analysis-rate');
        this.errorEl = null;  // For showing error messages
        
        this.init();
    }

    init() {
        this.loadStatistics();
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add any main page specific event listeners here
        console.log('Main page initialized');
    }

    async loadStatistics() {
        try {
            this.clearError();
            this.showLoading(true);
            
            const response = await fetch('/api/v1/resumes');
            if (!response.ok) {
                throw new Error(`Failed to load statistics: ${response.statusText}`);
            }

            const resumes = await response.json();
            this.updateStatistics(resumes);

        } catch (error) {
            this.showError(error.message || 'Failed to load statistics');
        } finally {
            this.showLoading(false);
        }
    }

    updateStatistics(resumes) {
        const total = resumes.length;
        const analyzed = resumes.filter(r => r.is_analyzed).length;
        const rate = total > 0 ? Math.round((analyzed / total) * 100) : 0;

        this.animateNumber(this.totalResumes, total);
        this.animateNumber(this.analyzedResumes, analyzed);
        this.analysisRate.textContent = `${rate}%`;
    }

    animateNumber(element, finalValue) {
        if (element._animationTimer) clearInterval(element._animationTimer);

        const duration = 1000;
        const fps = 60;
        const increment = finalValue / (duration / (1000 / fps));
        let currentValue = 0;

        element._animationTimer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(element._animationTimer);
                element._animationTimer = null;
            }
            element.textContent = Math.floor(currentValue);
        }, 1000 / fps);
    }

    showError(message) {
        console.error(message);
        if (!this.errorEl) {
            this.errorEl = document.createElement('div');
            this.errorEl.id = 'error-message';
            this.errorEl.style.color = 'red';
            this.errorEl.style.textAlign = 'center';
            this.errorEl.style.margin = '1rem auto';
            this.errorEl.style.maxWidth = '600px';
            this.errorEl.style.fontWeight = 'bold';
            document.body.prepend(this.errorEl);
        }
        this.errorEl.textContent = message;
    }

    clearError() {
        if (this.errorEl) {
            this.errorEl.textContent = '';
        }
    }

    showLoading(show) {
        if (!this.loadingEl) {
            this.loadingEl = document.createElement('div');
            this.loadingEl.id = 'loading-message';
            this.loadingEl.style.textAlign = 'center';
            this.loadingEl.style.margin = '1rem auto';
            this.loadingEl.style.fontStyle = 'italic';
            this.loadingEl.style.color = '#555';
            this.loadingEl.textContent = 'Loading statistics...';
            this.statsContainer.parentNode.insertBefore(this.loadingEl, this.statsContainer);
        }
        this.loadingEl.style.display = show ? 'block' : 'none';
    }
}

// Upload resume with error handling
const uploadResume = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/v1/upload", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }

        const data = await response.json();
        console.log("Upload result:", data);
        return data;

    } catch (error) {
        console.error('Error uploading resume:', error);
        alert(`Error uploading resume: ${error.message}`);
        return null;
    }
};

// Initialize main page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MainPage();
});
