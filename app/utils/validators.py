from fastapi import HTTPException, UploadFile
from app.core.config import settings

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    
    # Check file size
    if file.size > settings.max_file_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.max_file_size / 1024 / 1024:.1f}MB"
        )
    
    # Check file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = file.filename.split('.')[-1].lower()
    if file_extension not in settings.allowed_file_types_list:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.allowed_file_types_list)}"
        )
    return True

def validate_resume_id(resume_id: str) -> bool:
    if not resume_id or len(resume_id) < 10:
        raise HTTPException(status_code=400, detail="Invalid resume ID")
    return True