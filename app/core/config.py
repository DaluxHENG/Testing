from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # AI APIs
    gemini_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    
    # Security
    secret_key: str = "your_secret_key_here_make_it_long_and_random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File handling
    upload_dir: str = "model/resume/uploads"
    parsed_dir: str = "model/resume/parsed"
    data_dir: str = "data"
    resumes_dir: str = "data/resumes"
    analyses_dir: str = "data/analyses"
    metadata_dir: str = "data/metadata"
    
    max_file_size: int = 10485760  # 10MB
    allowed_file_types: str = "pdf,docx,doc"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return self.allowed_file_types.split(",")
    
    class Config:
        env_file = ".env"

settings = Settings()
