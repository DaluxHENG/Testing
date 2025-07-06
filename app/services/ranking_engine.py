from typing import List, Dict, Any
from app.storage.data_models import ScoredResume, RankedBatchResult
import statistics
from datetime import datetime

class RankingEngine:
    def __init__(self):
        pass

    def rank_resumes(self, scored_resumes: List[Dict[str, Any]]) -> RankedBatchResult:
        """
        Rank resumes by score and generate comprehensive results
        """
        try:
            # Convert to ScoredResume objects
            resume_objects = []
            for resume_data in scored_resumes:
                scored_resume = ScoredResume(
                    resume_id=resume_data["resume_id"],
                    filename=resume_data["filename"],
                    original_filename=resume_data["original_filename"],
                    score=resume_data["score"],
                    category_scores=resume_data["category_scores"],
                    highlights=resume_data["highlights"],
                    analysis=resume_data["analysis"]
                )
                resume_objects.append(scored_resume)
            
            # Sort by score in descending order
            ranked_resumes = sorted(resume_objects, key=lambda x: x.score, reverse=True)
            
            # Assign ranks
            for i, resume in enumerate(ranked_resumes):
                resume.rank = i + 1
            
            # Generate summary statistics
            summary_stats = self._generate_summary_stats(ranked_resumes)
            
            # Create ranked batch result
            ranked_result = RankedBatchResult(
                batch_id=scored_resumes[0].get("batch_id", "unknown") if scored_resumes else "unknown",
                batch_name=scored_resumes[0].get("batch_name") if scored_resumes else None,
                total_candidates=len(ranked_resumes),
                created_date=datetime.utcnow(),
                ranked_candidates=ranked_resumes,
                summary_stats=summary_stats
            )
            
            return ranked_result
            
        except Exception as e:
            # Return empty result if ranking fails
            return RankedBatchResult(
                batch_id="error",
                batch_name=None,
                total_candidates=0,
                created_date=datetime.utcnow(),
                ranked_candidates=[],
                summary_stats={"error": str(e)}
            )

    def _generate_summary_stats(self, ranked_resumes: List[ScoredResume]) -> Dict[str, Any]:
        """Generate comprehensive summary statistics"""
        if not ranked_resumes:
            return {
                "total_candidates": 0,
                "average_score": 0,
                "score_range": {"min": 0, "max": 0},
                "score_distribution": {},
                "top_performers": [],
                "category_averages": {}
            }
        
        # Basic statistics
        scores = [resume.score for resume in ranked_resumes]
        category_scores = {
            "completeness": [],
            "technical_skills": [],
            "experience": [],
            "education": [],
            "presentation": []
        }
        
        # Collect category scores
        for resume in ranked_resumes:
            for category, score in resume.category_scores.items():
                if category in category_scores:
                    category_scores[category].append(score)
        
        # Calculate statistics
        stats = {
            "total_candidates": len(ranked_resumes),
            "average_score": round(statistics.mean(scores), 2),
            "median_score": round(statistics.median(scores), 2),
            "score_range": {
                "min": round(min(scores), 2),
                "max": round(max(scores), 2)
            },
            "score_distribution": self._calculate_score_distribution(scores),
            "top_performers": self._get_top_performers(ranked_resumes),
            "category_averages": self._calculate_category_averages(category_scores),
            "percentiles": self._calculate_percentiles(scores)
        }
        
        return stats

    def _calculate_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution in ranges"""
        distribution = {
            "90-100": 0,
            "80-89": 0,
            "70-79": 0,
            "60-69": 0,
            "50-59": 0,
            "40-49": 0,
            "30-39": 0,
            "0-29": 0
        }
        
        for score in scores:
            if score >= 90:
                distribution["90-100"] += 1
            elif score >= 80:
                distribution["80-89"] += 1
            elif score >= 70:
                distribution["70-79"] += 1
            elif score >= 60:
                distribution["60-69"] += 1
            elif score >= 50:
                distribution["50-59"] += 1
            elif score >= 40:
                distribution["40-49"] += 1
            elif score >= 30:
                distribution["30-39"] += 1
            else:
                distribution["0-29"] += 1
        
        return distribution

    def _get_top_performers(self, ranked_resumes: List[ScoredResume], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get top performing candidates"""
        top_performers = []
        for resume in ranked_resumes[:top_n]:
            top_performers.append({
                "rank": resume.rank,
                "name": resume.original_filename,
                "score": resume.score,
                "top_skills": resume.highlights.get("top_skills", [])[:3],
                "strengths": resume.highlights.get("strengths", [])[:2]
            })
        return top_performers

    def _calculate_category_averages(self, category_scores: Dict[str, List[float]]) -> Dict[str, float]:
        """Calculate average scores for each category"""
        averages = {}
        for category, scores in category_scores.items():
            if scores:
                averages[category] = round(statistics.mean(scores), 2)
            else:
                averages[category] = 0.0
        return averages

    def _calculate_percentiles(self, scores: List[float]) -> Dict[str, float]:
        """Calculate percentile scores"""
        if not scores:
            return {}
        
        sorted_scores = sorted(scores)
        return {
            "p25": round(sorted_scores[int(len(sorted_scores) * 0.25)], 2),
            "p50": round(sorted_scores[int(len(sorted_scores) * 0.50)], 2),
            "p75": round(sorted_scores[int(len(sorted_scores) * 0.75)], 2),
            "p90": round(sorted_scores[int(len(sorted_scores) * 0.90)], 2)
        }

    def filter_by_score_range(self, ranked_resumes: List[ScoredResume], min_score: float = 0, max_score: float = 100) -> List[ScoredResume]:
        """Filter resumes by score range"""
        return [resume for resume in ranked_resumes if min_score <= resume.score <= max_score]

    def filter_by_category_score(self, ranked_resumes: List[ScoredResume], category: str, min_score: float = 0) -> List[ScoredResume]:
        """Filter resumes by minimum category score"""
        return [resume for resume in ranked_resumes if resume.category_scores.get(category, 0) >= min_score]

    def get_candidates_by_rank_range(self, ranked_resumes: List[ScoredResume], start_rank: int, end_rank: int) -> List[ScoredResume]:
        """Get candidates within a specific rank range"""
        return [resume for resume in ranked_resumes if resume.rank and start_rank <= resume.rank <= end_rank]

# Global ranking engine instance
ranking_engine = RankingEngine() 