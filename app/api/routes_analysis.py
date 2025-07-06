from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime

from app.storage.file_manager import file_manager
from app.storage.data_models import AnalysisResult
from app.services.resume_parser import parse_resume
from app.services.ai_analyzer import analyze_resume
from app.services.scoring_engine import scoring_engine

router = APIRouter()

@router.post("/analyze/{resume_id}")
async def analyze_resume_endpoint(resume_id: str, ai_provider: str = "gemini"):
    """Analyze a resume using AI"""
    try:
        # Get resume metadata
        metadata = file_manager.get_resume_metadata(resume_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Parse resume if not already parsed
        parsed_content = file_manager.get_parsed_content(resume_id)
        if not parsed_content:
            parsed_content = await parse_resume(metadata.file_path)
            file_manager.save_parsed_content(resume_id, parsed_content)
            
            # Update metadata
            metadata.is_parsed = True
            file_manager.save_resume_metadata(metadata)
        
        # Analyze with AI
        ai_analysis = await analyze_resume(parsed_content["extracted_text"], ai_provider)
        ai_analysis.resume_id = resume_id
        
        # Calculate scores using the new scoring engine
        scoring_result = scoring_engine.score_resume(parsed_content["parsed_data"], ai_analysis)
        
        # Create analysis result
        analysis = AnalysisResult(
            resume_id=resume_id,
            ai_provider=ai_provider,
            overall_score=scoring_result["overall_score"],
            category_scores=scoring_result["category_scores"],
            feedback=ai_analysis.feedback,
            suggestions=ai_analysis.suggestions
        )
        
        # Save analysis
        file_manager.save_analysis_result(analysis)
        
        # Update metadata
        metadata.is_analyzed = True
        file_manager.save_resume_metadata(metadata)
        
        return {
            "message": "Analysis completed successfully",
            "analysis_id": analysis.id,
            "analysis": analysis.dict()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis result by ID"""
    try:
        analysis = file_manager.get_analysis_result(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/resumes/{resume_id}/analysis")
async def get_resume_analysis(resume_id: str):
    """Get analysis for a specific resume"""
    try:
        # Find analysis files for this resume
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
        
        return analyses
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))