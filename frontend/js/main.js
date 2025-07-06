// Main page functionality
class MainPage {
    constructor() {
        this.statsContainer = document.getElementById('stats-container');
        this.totalResumes = document.getElementById('total-resumes');
        this.analyzedResumes = document.getElementById('analyzed-resumes');
        this.analysisRate = document.getElementById('analysis-rate');
        
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
            const response = await fetch('/api/v1/resumes');
            if (!response.ok) {
                throw new Error('Failed to load statistics');
            }

            const resumes = await response.json();
            this.updateStatistics(resumes);
            
        } catch (error) {
            console.error('Error loading statistics:', error);
            this.showError('Failed to load statistics');
        }
    }

    updateStatistics(resumes) {
        const total = resumes.length;
        const analyzed = resumes.filter(r => r.is_analyzed).length;
        const rate = total > 0 ? Math.round((analyzed / total) * 100) : 0;

        this.totalResumes.textContent = total;
        this.analyzedResumes.textContent = analyzed;
        this.analysisRate.textContent = `${rate}%`;

        // Add animation to numbers
        this.animateNumber(this.totalResumes, total);
        this.animateNumber(this.analyzedResumes, analyzed);
    }

    animateNumber(element, finalValue) {
        const startValue = 0;
        const duration = 1000;
        const increment = finalValue / (duration / 16); // 60fps
        let currentValue = startValue;

        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= finalValue) {
                currentValue = finalValue;
                clearInterval(timer);
            }
            element.textContent = Math.floor(currentValue);
        }, 16);
    }

    showError(message) {
        console.error(message);
        // You can add a more sophisticated error display here
    }
}

// Initialize main page when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MainPage();
});
