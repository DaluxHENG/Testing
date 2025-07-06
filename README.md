# SmartRecruit - AI-Powered Resume Screening Platform

A full-stack AI-powered resume screening platform built with FastAPI (Python) and file-based storage. The system allows users to upload resumes, extract text, analyze content using AI, and generate comprehensive feedback and scoring.

## 🚀 Features

- **Resume Upload**: Support for PDF and DOCX files
- **AI Analysis**: Integration with Google Gemini API for intelligent resume analysis
- **Smart Scoring**: Multi-category scoring system (completeness, technical skills, experience, education, presentation)
- **File-based Storage**: Simple and efficient file storage for resumes, parsed content, and analysis results
- **RESTful API**: Clean FastAPI endpoints for all operations
- **Modern Frontend**: Responsive HTML/CSS/JavaScript interface
- **Real-time Feedback**: Instant analysis and actionable suggestions

## 🏗️ Architecture

```
smartrecruit/
├── app/
│   ├── api/                 # FastAPI route handlers
│   │   ├── routes_upload.py
│   │   ├── routes_analysis.py
│   │   └── routes_resume.py
│   ├── core/               # Configuration and core modules
│   │   ├── config.py
│   │   └── security.py
│   ├── services/           # Business logic
│   │   ├── ai_analyzer.py
│   │   ├── resume_parser.py
│   │   └── scoring_engine.py
│   ├── storage/            # Data storage and models
│   │   ├── data_models.py
│   │   └── file_manager.py
│   └── utils/              # Utility functions
│       ├── file_handler.py
│       └── validators.py
├── frontend/               # Static frontend files
│   ├── css/
│   ├── js/
│   └── *.html
├── model/                  # File storage
│   └── resume/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
└── env.example            # Environment variables template
```

## 🛠️ Setup Instructions

### Prerequisites

- Python 3.8+
- Google Gemini API key

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd smartrecruit

# Run the startup script (creates venv, installs deps, starts server)
./start.sh
```

### Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp env.example .env
# Edit .env with your API keys

# 4. Run the application
python main.py
```

Required environment variables:
```env
# AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Security
SECRET_KEY=your_secret_key_here_make_it_long_and_random

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

The application will be available at:
- **API**: http://localhost:8000
- **Frontend**: http://localhost:8000/static/index.html
- **API Documentation**: http://localhost:8000/docs

## 📚 API Endpoints

### Resume Management
- `POST /api/v1/upload` - Upload a resume file
- `GET /api/v1/resumes` - Get all resumes
- `GET /api/v1/resumes/{resume_id}` - Get specific resume
- `DELETE /api/v1/resumes/{resume_id}` - Delete resume

### Analysis
- `POST /api/v1/analyze/{resume_id}` - Analyze resume with AI
- `GET /api/v1/analysis/{analysis_id}` - Get analysis result
- `GET /api/v1/resumes/{resume_id}/analysis` - Get resume analyses

## 🔧 Configuration

### File Upload Settings
- **Max file size**: 10MB (configurable in `.env`)
- **Supported formats**: PDF, DOCX, DOC
- **Storage location**: `model/resume/uploads/`

### AI Analysis
- **Primary provider**: Google Gemini
- **Fallback provider**: DeepSeek (configurable)
- **Analysis categories**: Technical skills, experience, education, presentation

### Scoring System
- **Overall score**: Weighted average of all categories
- **Category weights**:
  - Completeness: 20%
  - Technical Skills: 25%
  - Experience: 30%
  - Education: 15%
  - Presentation: 10%

## 🎨 Frontend Features

- **Responsive Design**: Works on desktop and mobile
- **Real-time Upload**: Drag-and-drop file upload
- **Progress Tracking**: Upload and analysis progress indicators
- **Results Dashboard**: Comprehensive analysis display
- **Statistics**: Platform usage statistics

## 🔒 Security Features

- **File Validation**: Type and size validation
- **CORS Configuration**: Configurable cross-origin requests
- **Error Handling**: Comprehensive error management
- **Input Sanitization**: Protection against malicious inputs

## 🚀 Deployment

### Production Considerations
1. Configure proper CORS origins
2. Set up reverse proxy (nginx)
3. Enable HTTPS
4. Configure logging and monitoring
5. Set up file backup strategy

### Simple Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your configuration

# Run the application
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information

## 🔄 Changelog

### v1.0.0
- Initial release
- FastAPI backend with file-based storage
- AI-powered resume analysis
- Modern frontend interface
- Comprehensive scoring system
