from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.storage.file_manager import file_manager
from app.storage.data_models import ResumeMetadata, ResumeResponse
from app.utils.validators import validate_file
from app.utils.file_handler import save_uploaded_file

router = APIRouter()

@router.post("/upload", response_model=dict)
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file"""
    try:
        # Validate file
        validate_file(file)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1].lower() if file.filename else "pdf"
        filename = f"{file_id}.{file_extension}"
        
        # Save file
        file_path = await save_uploaded_file(file, filename)
        
        # Create metadata
        metadata = ResumeMetadata(
            id=file_id,
            filename=filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file.size or 0,
            file_type=file_extension
        )
        
        # Save metadata
        file_manager.save_resume_metadata(metadata)
        
        return {
            "message": "File uploaded successfully",
            "resume_id": file_id,
            "filename": file.filename,
            "size": file.size
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resumes", response_model=List[ResumeResponse])
async def get_all_resumes():
    """Get all uploaded resumes"""
    try:
        resumes = file_manager.get_all_resumes()
        response = []
        
        for resume in resumes:
            # Check if analysis exists
            analysis = None
            for analysis_file in Path(settings.analyses_dir).glob(f"*{resume.id}*.json"):
                try:
                    analysis = file_manager.get_analysis_result(analysis_file.stem)
                    break
                except:
                    continue
            
            response.append(ResumeResponse(
                id=resume.id,
                filename=resume.original_filename,
                upload_date=resume.upload_date,
                file_size=resume.file_size,
                is_parsed=resume.is_parsed,
                is_analyzed=resume.is_analyzed,
                analysis=analysis
            ))
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/resumes/{resume_id}")
async def delete_resume(resume_id: str):
    """Delete a resume and its associated data"""
    try:
        success = file_manager.delete_resume(resume_id)
        if success:
            return {"message": "Resume deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Resume not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: str):
    """Get resume details by ID"""
    try:
        metadata = file_manager.get_resume_metadata(resume_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Get analysis if exists
        analysis = None
        for analysis_file in Path(settings.analyses_dir).glob(f"*{resume_id}*.json"):
            try:
                analysis = file_manager.get_analysis_result(analysis_file.stem)
                break
            except:
                continue
        
        return ResumeResponse(
            id=metadata.id,
            filename=metadata.original_filename,
            upload_date=metadata.upload_date,
            file_size=metadata.file_size,
            is_parsed=metadata.is_parsed,
            is_analyzed=metadata.is_analyzed,
            analysis=analysis
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))