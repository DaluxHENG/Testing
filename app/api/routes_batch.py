from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.storage.file_manager import file_manager
from app.storage.data_models import RankedResultsResponse, ScoredResume

router = APIRouter()

@router.get("/batch/ranked_results/{batch_id}", response_model=RankedResultsResponse)
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

@router.get("/batch/results")
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

@router.get("/batch/{batch_id}/candidates")
async def get_batch_candidates(
    batch_id: str,
    min_score: Optional[float] = Query(None, description="Minimum score filter"),
    max_score: Optional[float] = Query(None, description="Maximum score filter"),
    category: Optional[str] = Query(None, description="Category to filter by"),
    category_min_score: Optional[float] = Query(None, description="Minimum category score"),
    limit: Optional[int] = Query(50, description="Maximum number of candidates to return")
):
    """Get candidates from a batch with optional filtering"""
    try:
        ranked_result = file_manager.get_ranked_batch_result(batch_id)
        if not ranked_result:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        candidates = ranked_result.ranked_candidates
        
        # Apply filters
        if min_score is not None:
            candidates = [c for c in candidates if c.score >= min_score]
        
        if max_score is not None:
            candidates = [c for c in candidates if c.score <= max_score]
        
        if category and category_min_score is not None:
            candidates = [c for c in candidates if c.category_scores.get(category, 0) >= category_min_score]
        
        # Apply limit
        if limit:
            candidates = candidates[:limit]
        
        return {
            "batch_id": batch_id,
            "total_candidates": len(candidates),
            "candidates": [
                {
                    "rank": c.rank,
                    "resume_id": c.resume_id,
                    "filename": c.original_filename,
                    "score": c.score,
                    "category_scores": c.category_scores,
                    "highlights": c.highlights
                }
                for c in candidates
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{batch_id}/top_candidates")
async def get_top_candidates(
    batch_id: str,
    top_n: int = Query(10, description="Number of top candidates to return")
):
    """Get top N candidates from a batch"""
    try:
        ranked_result = file_manager.get_ranked_batch_result(batch_id)
        if not ranked_result:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        top_candidates = ranked_result.ranked_candidates[:top_n]
        
        return {
            "batch_id": batch_id,
            "top_candidates": [
                {
                    "rank": c.rank,
                    "resume_id": c.resume_id,
                    "filename": c.original_filename,
                    "score": c.score,
                    "category_scores": c.category_scores,
                    "highlights": c.highlights,
                    "analysis_summary": c.analysis.feedback[:200] + "..." if len(c.analysis.feedback) > 200 else c.analysis.feedback
                }
                for c in top_candidates
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/batch/{batch_id}/statistics")
async def get_batch_statistics(batch_id: str):
    """Get detailed statistics for a batch"""
    try:
        ranked_result = file_manager.get_ranked_batch_result(batch_id)
        if not ranked_result:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        return {
            "batch_id": batch_id,
            "batch_name": ranked_result.batch_name,
            "statistics": ranked_result.summary_stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/batch/{batch_id}")
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

@router.get("/batch/{batch_id}/download_csv")
async def download_batch_csv(batch_id: str):
    """Download batch results as CSV file"""
    try:
        ranked_result = file_manager.get_ranked_batch_result(batch_id)
        if not ranked_result:
            raise HTTPException(status_code=404, detail="Batch not found")
        
        # Check if CSV file exists, if not create it
        csv_file_path = file_manager.save_ranked_results_csv(ranked_result)
        
        return {
            "message": "CSV file generated successfully",
            "file_path": csv_file_path,
            "download_url": f"/api/v1/batch/{batch_id}/download_csv"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 