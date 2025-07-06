from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class ResumeMetadata(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    file_type: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    is_parsed: bool = False
    is_analyzed: bool = False

class ParsedResume(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resume_id: str
    extracted_text: str
    parsed_data: Dict[str, Any]
    parsing_method: str
    parsed_date: datetime = Field(default_factory=datetime.utcnow)

class AnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resume_id: str
    ai_provider: str
    overall_score: float
    category_scores: Dict[str, float]
    feedback: str
    suggestions: List[str]
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

class ResumeResponse(BaseModel):
    id: str
    filename: str
    upload_date: datetime
    file_size: int
    is_parsed: bool
    is_analyzed: bool
    analysis: Optional[AnalysisResult] = None

# New models for batch processing
class BatchUploadRequest(BaseModel):
    files: List[str]  # List of file paths
    batch_name: Optional[str] = None

class BatchResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    batch_name: Optional[str] = None
    total_files: int
    processed_files: int
    failed_files: int
    created_date: datetime = Field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None
    status: str = "processing"  # processing, completed, failed
    results: List[Dict[str, Any]] = []

class ScoredResume(BaseModel):
    resume_id: str
    filename: str
    original_filename: str
    score: float
    category_scores: Dict[str, float]
    highlights: Dict[str, Any]
    analysis: AnalysisResult
    rank: Optional[int] = None

class RankedBatchResult(BaseModel):
    batch_id: str
    batch_name: Optional[str]
    total_candidates: int
    created_date: datetime
    ranked_candidates: List[ScoredResume]
    summary_stats: Dict[str, Any]

class BatchUploadResponse(BaseModel):
    batch_id: str
    message: str
    total_files: int
    status: str

class RankedResultsResponse(BaseModel):
    batch_id: str
    batch_name: Optional[str]
    total_candidates: int
    ranked_candidates: List[ScoredResume]
    summary_stats: Dict[str, Any]