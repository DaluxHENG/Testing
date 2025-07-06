from fastapi import APIRouter, HTTPException
from typing import List
from app.storage.file_manager import file_manager
from app.storage.data_models import ResumeResponse

router = APIRouter()

@router.get("/resumes/{resume_id}/details")
async def get_resume_details(resume_id: str):
    """Get detailed resume information including parsed content"""
    try:
        # Get metadata
        metadata = file_manager.get_resume_metadata(resume_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Get parsed content
        parsed_content = file_manager.get_parsed_content(resume_id)
        
        # Get analyses
        from pathlib import Path
        from app.core.config import settings
        
        analyses = []
        for analysis_file in Path(settings.analyses_dir).glob("*.json"):
            try:
                analysis = file_manager.get_analysis_result(analysis_file.stem)
                if analysis and analysis.resume_id == resume_id:
                    analyses.append(analysis.dict())
            except:
                continue
        
        return {
            "metadata": metadata.dict(),
            "parsed_content": parsed_content,
            "analyses": analyses
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_stats():
    """Get platform statistics"""
    try:
        resumes = file_manager.get_all_resumes()
        
        total_resumes = len(resumes)
        analyzed_resumes = sum(1 for r in resumes if r.is_analyzed)
        parsed_resumes = sum(1 for r in resumes if r.is_parsed)
        
        return {
            "total_resumes": total_resumes,
            "analyzed_resumes": analyzed_resumes,
            "parsed_resumes": parsed_resumes,
            "analysis_rate": round(analyzed_resumes / total_resumes * 100, 1) if total_resumes > 0 else 0
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

