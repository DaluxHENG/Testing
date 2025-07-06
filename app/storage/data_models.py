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