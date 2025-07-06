import os
import json
import uuid
import csv
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from app.core.config import settings
from app.storage.data_models import ResumeMetadata, AnalysisResult, BatchResult, RankedBatchResult

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

    # New batch processing methods
    def save_batch_result(self, batch_result: BatchResult) -> str:
        """Save batch processing result"""
        batch_file = self.metadata_dir / f"batch_{batch_result.id}.json"
        with open(batch_file, 'w') as f:
            json.dump(batch_result.dict(), f, indent=2, default=str)
        return str(batch_file)

    def get_batch_result(self, batch_id: str) -> Optional[BatchResult]:
        """Get batch processing result by ID"""
        batch_file = self.metadata_dir / f"batch_{batch_id}.json"
        if batch_file.exists():
            with open(batch_file, 'r') as f:
                data = json.load(f)
                return BatchResult(**data)
        return None

    def save_ranked_batch_result(self, ranked_result: RankedBatchResult) -> str:
        """Save ranked batch result"""
        ranked_file = self.metadata_dir / f"ranked_{ranked_result.batch_id}.json"
        with open(ranked_file, 'w') as f:
            json.dump(ranked_result.dict(), f, indent=2, default=str)
        return str(ranked_file)

    def get_ranked_batch_result(self, batch_id: str) -> Optional[RankedBatchResult]:
        """Get ranked batch result by ID"""
        ranked_file = self.metadata_dir / f"ranked_{batch_id}.json"
        if ranked_file.exists():
            with open(ranked_file, 'r') as f:
                data = json.load(f)
                return RankedBatchResult(**data)
        return None

    def save_ranked_results_csv(self, ranked_result: RankedBatchResult) -> str:
        """Save ranked results as CSV file"""
        csv_file = self.metadata_dir / f"ranked_{ranked_result.batch_id}.csv"
        
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Rank', 'Filename', 'Score', 'Completeness', 'Technical Skills', 
                'Experience', 'Education', 'Presentation', 'Top Skills', 'Strengths'
            ])
            
            # Write data
            for candidate in ranked_result.ranked_candidates:
                writer.writerow([
                    candidate.rank,
                    candidate.original_filename,
                    candidate.score,
                    candidate.category_scores.get('completeness', 0),
                    candidate.category_scores.get('technical_skills', 0),
                    candidate.category_scores.get('experience', 0),
                    candidate.category_scores.get('education', 0),
                    candidate.category_scores.get('presentation', 0),
                    ', '.join(candidate.highlights.get('top_skills', [])[:3]),
                    ', '.join(candidate.highlights.get('strengths', [])[:2])
                ])
        
        return str(csv_file)

    def get_all_batch_results(self) -> List[BatchResult]:
        """Get all batch processing results"""
        batches = []
        for batch_file in self.metadata_dir.glob("batch_*.json"):
            try:
                with open(batch_file, 'r') as f:
                    data = json.load(f)
                    batches.append(BatchResult(**data))
            except Exception as e:
                print(f"Error reading {batch_file}: {e}")
        return sorted(batches, key=lambda x: x.created_date, reverse=True)

    def delete_batch_result(self, batch_id: str) -> bool:
        """Delete batch result and associated files"""
        try:
            # Delete batch result
            batch_file = self.metadata_dir / f"batch_{batch_id}.json"
            if batch_file.exists():
                batch_file.unlink()
            
            # Delete ranked result
            ranked_file = self.metadata_dir / f"ranked_{batch_id}.json"
            if ranked_file.exists():
                ranked_file.unlink()
            
            # Delete CSV file
            csv_file = self.metadata_dir / f"ranked_{batch_id}.csv"
            if csv_file.exists():
                csv_file.unlink()
            
            return True
        except Exception as e:
            print(f"Error deleting batch {batch_id}: {e}")
            return False
    
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
