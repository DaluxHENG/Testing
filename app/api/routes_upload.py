from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.storage.file_manager import file_manager
from app.storage.data_models import ResumeMetadata, ResumeResponse, BatchUploadResponse, RankedResultsResponse
from app.utils.validators import validate_file
from app.utils.file_handler import save_uploaded_file
from app.services.resume_parser import parse_resume
from app.services.ai_analyzer import analyze_resume
from app.services.scoring_engine import scoring_engine
from app.services.ranking_engine import ranking_engine

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

@router.post("/batch_upload", response_model=BatchUploadResponse)
async def batch_upload_resumes(files: List[UploadFile] = File(...)):
    """Upload multiple resumes and process them in batch"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        if len(files) > 20:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 20 files allowed per batch")
        
        batch_id = str(uuid.uuid4())
        processed_files = 0
        failed_files = 0
        results = []
        
        # Process each file
        for file in files:
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
                
                # Parse resume
                parsed_data = await parse_resume(file_path)
                file_manager.save_parsed_content(file_id, parsed_data)
                
                # Analyze with AI
                analysis = await analyze_resume(parsed_data["extracted_text"])
                analysis.resume_id = file_id
                file_manager.save_analysis_result(analysis)
                
                # Score resume
                scoring_result = scoring_engine.score_resume(parsed_data["parsed_data"], analysis)
                
                # Prepare result
                result = {
                    "resume_id": file_id,
                    "filename": filename,
                    "original_filename": metadata.original_filename,
                    "score": scoring_result["overall_score"],
                    "category_scores": scoring_result["category_scores"],
                    "highlights": scoring_result["highlights"],
                    "analysis": analysis,
                    "batch_id": batch_id
                }
                
                results.append(result)
                processed_files += 1
                
                # Update metadata
                metadata.is_parsed = True
                metadata.is_analyzed = True
                file_manager.save_resume_metadata(metadata)
                
            except Exception as e:
                failed_files += 1
                print(f"Error processing file {file.filename}: {str(e)}")
                continue
        
        # Rank all processed resumes
        if results:
            ranked_result = ranking_engine.rank_resumes(results)
            ranked_result.batch_id = batch_id
            
            # Save ranked results
            file_manager.save_ranked_batch_result(ranked_result)
            file_manager.save_ranked_results_csv(ranked_result)
        
        return BatchUploadResponse(
            batch_id=batch_id,
            message=f"Batch processing completed. {processed_files} files processed, {failed_files} failed.",
            total_files=len(files),
            status="completed"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ranked_results/{batch_id}", response_model=RankedResultsResponse)
async def get_ranked_results(batch_id: str):
    """Get ranked results for a specific batch"""
    try:
        ranked_result = file_manager.get_ranked_batch_result(batch_id)
        if not ranked_result:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return RankedResultsResponse(
            batch_id=ranked_result.batch_id,
            batch_name=ranked_result.batch_name,
            total_candidates=ranked_result.total_candidates,
            ranked_candidates=ranked_result.ranked_candidates,
            summary_stats=ranked_result.summary_stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch_results")
async def get_all_batch_results():
    """Get all batch processing results"""
    try:
        batches = file_manager.get_all_batch_results()
        return {
            "batches": [
                {
                    "id": batch.id,
                    "batch_name": batch.batch_name,
                    "total_files": batch.total_files,
                    "processed_files": batch.processed_files,
                    "failed_files": batch.failed_files,
                    "status": batch.status,
                    "created_date": batch.created_date,
                    "completed_date": batch.completed_date
                }
                for batch in batches
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/batch_results/{batch_id}")
async def delete_batch_result(batch_id: str):
    """Delete a batch result and all associated data"""
    try:
        success = file_manager.delete_batch_result(batch_id)
        if success:
            return {"message": "Batch result deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Batch not found")
    
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