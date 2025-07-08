# SmartRecruit - AI-Powered Resume Screening Platform

SmartRecruit is an advanced AI-powered resume screening platform that leverages the Google Gemini API to analyze, score, and rank resumes for efficient and data-driven hiring decisions.

---

## 🚀 Features

### Core Features
- AI-powered resume analysis using Google Gemini API
- Multi-category scoring: completeness, technical skills, experience, education, presentation
- Instant feedback with actionable suggestions
- Support for PDF and DOCX resume formats

### Batch Processing
- Batch upload of up to 20 resumes simultaneously
- Automated ranking of candidates based on overall scores
- Comprehensive batch statistics and insights
- CSV export of ranked results
- Filtering and search by score ranges and categories

---

## 🏗️ Architecture


```
SmartRecruit/
├── app/
│   ├── api/                    # FastAPI routes
│   │   ├── routes_upload.py    # Single and batch upload endpoints
│   │   ├── routes_batch.py     # Batch analysis and ranking endpoints
│   │   ├── routes_analysis.py  # Analysis endpoints
│   │   └── routes_resume.py    # Resume management endpoints
│   ├── core/                   # Configuration and security
│   ├── services/               # Business logic
│   │   ├── ai_analyzer.py      # Google Gemini AI integration
│   │   ├── resume_parser.py    # PDF/DOCX parsing
│   │   ├── scoring_engine.py   # Resume scoring system
│   │   └── ranking_engine.py   # Candidate ranking system
│   ├── storage/                # Data storage
│   │   ├── data_models.py      # Pydantic models
│   │   └── file_manager.py     # File-based storage
│   └── utils/                  # Utilities
├── frontend/                   # Web interface
├── data/                       # File storage
└── main.py                     # FastAPI application
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd smartrecruit
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
# Edit .env and add your Google Gemini API key
```

5. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## 📊 API Endpoints

### Single Resume Upload
- `POST /api/v1/upload` - Upload a single resume
- `GET /api/v1/resumes` - Get all uploaded resumes
- `GET /api/v1/resumes/{resume_id}` - Get specific resume details
- `DELETE /api/v1/resumes/{resume_id}` - Delete a resume


## 🎯 Scoring System

The platform uses a comprehensive scoring system with the following categories:

### Scoring Categories
1. **Completeness (20%)**: Contact info, sections, overall completeness
2. **Technical Skills (25%)**: Quality and relevance of technical skills
3. **Experience (25%)**: Work experience quality and duration
4. **Education (15%)**: Educational background and qualifications
5. **Presentation (15%)**: Formatting, structure, and readability

### Scoring Algorithm
- Base score of 100 points for each category
- Additional points based on content analysis
- AI analysis integration for enhanced accuracy
- Weighted average calculation for overall score

## 📈 Ranking System

### Ranking Features
- **Score-based Ranking**: Candidates ranked by overall score (descending)
- **Category Analysis**: Detailed breakdown of category scores
- **Statistical Insights**: Mean, median, percentiles, and distributions
- **Top Performers**: Automatic identification of top candidates
- **Filtering Options**: Filter by score ranges and categories

### HR Statistics
- Total candidates processed
- Average, median, and percentile scores
- Score distribution across ranges
- Category-wise averages
- Top performer highlights

## 🎨 Frontend Features

### Candidate Resume Upload
- Drag-and-drop file upload
- Real-time analysis progress
- Detailed scoring breakdown
- AI feedback and suggestions

### HR Upload Interface
- Multiple file selection
- Batch processing status
- Ranked candidate display
- Interactive statistics dashboard
- CSV download functionality

## 🔧 Configuration

### Environment Variables
```env
# AI APIs
GEMINI_API_KEY=your_gemini_api_key_here

# File handling
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES=pdf,docx,doc

# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### File Storage Structure
```
data/
├── resumes/          # Uploaded resume files
├── analyses/         # AI analysis results
└── metadata/         # Batch results and rankings
```

## 🔒 Security Features
- File type validation
- File size limits
- Secure file storage
- Input sanitization
- CORS configuration
