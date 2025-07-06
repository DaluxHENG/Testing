from typing import Dict, Any, List
import re
from app.storage.data_models import AnalysisResult

class ScoringEngine:
    def __init__(self):
        # Define scoring weights for different categories
        self.weights = {
            "completeness": 0.20,
            "technical_skills": 0.25,
            "experience": 0.25,
            "education": 0.15,
            "presentation": 0.15
        }
        
        # Define scoring criteria
        self.criteria = {
            "completeness": self._score_completeness,
            "technical_skills": self._score_technical_skills,
            "experience": self._score_experience,
            "education": self._score_education,
            "presentation": self._score_presentation
        }

    def score_resume(self, parsed_data: Dict[str, Any], analysis: AnalysisResult) -> Dict[str, Any]:
        """
        Score a resume based on multiple criteria
        Returns a dictionary with overall score and category scores
        """
        try:
            category_scores = {}
            
            # Calculate scores for each category
            for category, scoring_func in self.criteria.items():
                category_scores[category] = scoring_func(parsed_data, analysis)
            
            # Calculate weighted overall score
            overall_score = sum(
                category_scores[category] * self.weights[category]
                for category in self.weights.keys()
            )
            
            # Generate highlights
            highlights = self._generate_highlights(parsed_data, analysis, category_scores)
            
            return {
                "overall_score": round(overall_score, 2),
                "category_scores": category_scores,
                "highlights": highlights
            }
            
        except Exception as e:
            # Return default scores if scoring fails
            return {
                "overall_score": 50.0,
                "category_scores": {
                    "completeness": 50.0,
                    "technical_skills": 50.0,
                    "experience": 50.0,
                    "education": 50.0,
                    "presentation": 50.0
                },
                "highlights": {
                    "top_skills": [],
                    "experience_summary": "Unable to analyze",
                    "education_summary": "Unable to analyze"
                }
            }

    def _score_completeness(self, parsed_data: Dict[str, Any], analysis: AnalysisResult) -> float:
        """Score resume completeness (0-100)"""
        score = 50.0  # Base score
        
        # Check for essential sections
        sections = ["contact_info", "skills", "experience", "education"]
        present_sections = sum(1 for section in sections if parsed_data.get(section))
        score += (present_sections / len(sections)) * 30
        
        # Check for contact information completeness
        contact_info = parsed_data.get("contact_info", {})
        if contact_info.get("email"):
            score += 10
        if contact_info.get("phone"):
            score += 5
        if contact_info.get("linkedin"):
            score += 5
        
        return min(score, 100.0)

    def _score_technical_skills(self, parsed_data: Dict[str, Any], analysis: AnalysisResult) -> float:
        """Score technical skills (0-100)"""
        score = 50.0  # Base score
        
        # Count technical skills
        skills = parsed_data.get("skills", [])
        if skills:
            score += min(len(skills) * 5, 30)  # Up to 30 points for skill count
        
        # Check for in-demand skills (bonus points)
        in_demand_skills = [
            "python", "java", "javascript", "react", "node.js", "sql", 
            "aws", "docker", "kubernetes", "machine learning", "ai"
        ]
        
        found_in_demand = sum(1 for skill in skills if skill.lower() in in_demand_skills)
        score += found_in_demand * 2  # 2 points per in-demand skill
        
        # Use AI analysis if available
        if analysis and analysis.category_scores.get("technical_skills"):
            ai_score = analysis.category_scores["technical_skills"]
            score = (score + ai_score) / 2  # Average with AI score
        
        return min(score, 100.0)

    def _score_experience(self, parsed_data: Dict[str, Any], analysis: AnalysisResult) -> float:
        """Score work experience (0-100)"""
        score = 50.0  # Base score
        
        # Count experience entries
        experience = parsed_data.get("experience", [])
        if experience:
            score += min(len(experience) * 8, 40)  # Up to 40 points for experience count
        
        # Look for years of experience in text
        text = parsed_data.get("extracted_text", "").lower()
        years_patterns = [
            r'(\d+)\s*years?\s*of\s*experience',
            r'experience.*?(\d+)\s*years?',
            r'(\d+)\s*years?\s*in'
        ]
        
        for pattern in years_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    years = int(matches[0])
                    score += min(years * 3, 20)  # Up to 20 points for years
                    break
                except:
                    continue
        
        # Use AI analysis if available
        if analysis and analysis.category_scores.get("experience"):
            ai_score = analysis.category_scores["experience"]
            score = (score + ai_score) / 2
        
        return min(score, 100.0)

    def _score_education(self, parsed_data: Dict[str, Any], analysis: AnalysisResult) -> float:
        """Score education background (0-100)"""
        score = 50.0  # Base score
        
        # Check for education entries
        education = parsed_data.get("education", [])
        if education:
            score += min(len(education) * 10, 30)  # Up to 30 points for education entries
        
        # Look for degree levels
        text = parsed_data.get("extracted_text", "").lower()
        degree_scores = {
            "phd": 20,
            "doctorate": 20,
            "master": 15,
            "bachelor": 10,
            "associate": 5
        }
        
        for degree, points in degree_scores.items():
            if degree in text:
                score += points
                break
        
        # Use AI analysis if available
        if analysis and analysis.category_scores.get("education"):
            ai_score = analysis.category_scores["education"]
            score = (score + ai_score) / 2
        
        return min(score, 100.0)

    def _score_presentation(self, parsed_data: Dict[str, Any], analysis: AnalysisResult) -> float:
        """Score presentation and formatting (0-100)"""
        score = 50.0  # Base score
        
        text = parsed_data.get("extracted_text", "")
        
        # Check text length (not too short, not too long)
        text_length = len(text)
        if 500 <= text_length <= 2000:
            score += 20
        elif 2000 < text_length <= 3000:
            score += 15
        elif text_length > 3000:
            score += 10
        
        # Check for structured formatting
        lines = text.split('\n')
        if len(lines) > 20:  # Good structure
            score += 15
        
        # Check for bullet points or structured lists
        bullet_patterns = [r'^\s*[-•*]\s', r'^\s*\d+\.\s']
        bullet_count = sum(1 for line in lines if any(re.match(pattern, line) for pattern in bullet_patterns))
        if bullet_count > 5:
            score += 15
        
        # Use AI analysis if available
        if analysis and analysis.category_scores.get("presentation"):
            ai_score = analysis.category_scores["presentation"]
            score = (score + ai_score) / 2
        
        return min(score, 100.0)

    def _generate_highlights(self, parsed_data: Dict[str, Any], analysis: AnalysisResult, category_scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate highlights for the resume"""
        highlights = {
            "top_skills": parsed_data.get("skills", [])[:5],  # Top 5 skills
            "experience_summary": f"{len(parsed_data.get('experience', []))} positions",
            "education_summary": f"{len(parsed_data.get('education', []))} education entries",
            "strengths": [],
            "areas_for_improvement": []
        }
        
        # Identify strengths and areas for improvement
        for category, score in category_scores.items():
            if score >= 80:
                highlights["strengths"].append(f"Strong {category}")
            elif score <= 40:
                highlights["areas_for_improvement"].append(f"Improve {category}")
        
        # Add AI feedback if available
        if analysis and analysis.feedback:
            highlights["ai_feedback"] = analysis.feedback[:200] + "..." if len(analysis.feedback) > 200 else analysis.feedback
        
        return highlights

# Global scoring engine instance
scoring_engine = ScoringEngine()