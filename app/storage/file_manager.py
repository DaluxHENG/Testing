import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.core.config import settings
from app.storage.data_models import ResumeMetadata, AnalysisResult

class FileManager:
    def __init__(self):
        self.resumes_dir = Path(settings.resumes_dir)
        self.analyses_dir = Path(settings.analyses_dir)
        self.metadata_dir = Path(settings.metadata_dir)
        self.upload_dir = Path(settings.upload_dir)
        self.parsed_dir = Path(settings.parsed_dir)

    def save_resume_metadata(self, metadata: ResumeMetadata) -> str:
        """Save resume metadata to JSON file"""
        metadata_file = self.metadata_dir / f"{metadata.id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata.dict(), f, indent=2, default=str)
        return str(metadata_file)

    def get_resume_metadata(self, resume_id: str) -> Optional[ResumeMetadata]:
        """Get resume metadata by ID"""
        metadata_file = self.metadata_dir / f"{resume_id}.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                return ResumeMetadata(**data)
        return None

    def save_analysis_result(self, analysis: AnalysisResult) -> str:
        """Save analysis result to JSON file"""
        analysis_file = self.analyses_dir / f"{analysis.id}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis.dict(), f, indent=2, default=str)
        return str(analysis_file)

    def get_analysis_result(self, analysis_id: str) -> Optional[AnalysisResult]:
        """Get analysis result by ID"""
        analysis_file = self.analyses_dir / f"{analysis_id}.json"
        if analysis_file.exists():
            with open(analysis_file, 'r') as f:
                data = json.load(f)
                return AnalysisResult(**data)
        return None

    def get_all_resumes(self) -> List[ResumeMetadata]:
        """Get all resume metadata"""
        resumes = []
        for metadata_file in self.metadata_dir.glob("*.json"):
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    resumes.append(ResumeMetadata(**data))
            except Exception as e:
                print(f"Error reading {metadata_file}: {e}")
        return sorted(resumes, key=lambda x: x.upload_date, reverse=True)

    def delete_resume(self, resume_id: str) -> bool:
        """Delete resume and associated files"""
        try:
            # Delete metadata
            metadata_file = self.metadata_dir / f"{resume_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Delete analysis files
            for analysis_file in self.analyses_dir.glob(f"*{resume_id}*.json"):
                analysis_file.unlink()
            
            # Delete uploaded file
            metadata = self.get_resume_metadata(resume_id)
            if metadata and metadata.file_path:
                file_path = Path(metadata.file_path)
                if file_path.exists():
                    file_path.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting resume {resume_id}: {e}")
            return False

    def save_parsed_content(self, resume_id: str, content: Dict[str, Any]) -> str:
        """Save parsed resume content"""
        parsed_file = self.parsed_dir / f"{resume_id}.json"
        with open(parsed_file, 'w') as f:
            json.dump(content, f, indent=2, default=str)
        return str(parsed_file)

    def get_parsed_content(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """Get parsed resume content"""
        parsed_file = self.parsed_dir / f"{resume_id}.json"
        if parsed_file.exists():
            with open(parsed_file, 'r') as f:
                return json.load(f)
        return None
    
    def ensure_directories():
        os.makedirs("model/resume/upload", exist_ok=True)
        os.makedirs("model/resume/analysis", exist_ok=True)

def ensure_directories():
    """Create all required directories"""
    directories = [
        settings.upload_dir,
        settings.parsed_dir,
        settings.data_dir,
        settings.resumes_dir,
        settings.analyses_dir,
        settings.metadata_dir
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)



# Global file manager instance
file_manager = FileManager()
