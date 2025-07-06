from typing import Dict, Any

def calculate_scores(parsed_content: Dict[str, Any], ai_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate various scores for the resume"""
    
    # Extract data
    extracted_text = parsed_content.get("extracted_text", "")
    parsed_data = parsed_content.get("parsed_data", {})
    
    # Calculate individual scores
    completeness_score = calculate_completeness_score(parsed_data)
    technical_score = calculate_technical_score(parsed_data)
    experience_score = ai_analysis.get("experience_rating", 5.0)
    education_score = ai_analysis.get("education_rating", 5.0)
    presentation_score = calculate_presentation_score(extracted_text)
    
    # Calculate category scores
    category_scores = {
        "completeness": completeness_score,
        "technical_skills": technical_score,
        "experience": experience_score,
        "education": education_score,
        "presentation": presentation_score
    }
    
    # Calculate overall score (weighted average)
    weights = {
        "completeness": 0.2,
        "technical_skills": 0.25,
        "experience": 0.3,
        "education": 0.15,
        "presentation": 0.1
    }
    
    overall_score = sum(category_scores[category] * weights[category] 
                       for category in category_scores)
    
    return {
        "overall_score": round(overall_score, 2),
        "category_scores": {k: round(v, 2) for k, v in category_scores.items()}
    }

def calculate_completeness_score(parsed_data: Dict[str, Any]) -> float:
    """Calculate completeness score based on available sections"""
    required_sections = ['contact_info', 'skills', 'experience', 'education']
    score = 0
    
    for section in required_sections:
        if section in parsed_data and parsed_data[section]:
            if isinstance(parsed_data[section], dict):
                score += 2.5 if parsed_data[section] else 0
            elif isinstance(parsed_data[section], list):
                score += 2.5 if len(parsed_data[section]) > 0 else 0
            else:
                score += 2.5 if parsed_data[section] else 0
    
    return min(score, 10.0)

def calculate_technical_score(parsed_data: Dict[str, Any]) -> float:
    """Calculate technical skills score"""
    skills = parsed_data.get('skills', [])
    
    if not skills:
        return 2.0
    
    # Score based on number and relevance of skills
    skill_count = len(skills)
    
    if skill_count >= 10:
        return 10.0
    elif skill_count >= 7:
        return 8.0
    elif skill_count >= 5:
        return 6.0
    elif skill_count >= 3:
        return 4.0
    else:
        return 2.0

def calculate_presentation_score(text: str) -> float:
    """Calculate presentation score based on text quality"""
    if not text:
        return 1.0
    
    score = 5.0  # Base score
    
    # Check text length
    if len(text) > 1000:
        score += 1.0
    elif len(text) > 500:
        score += 0.5
    
    # Check for proper formatting indicators
    if '\n' in text:  # Has line breaks
        score += 0.5
    
    # Check for contact information
    if '@' in text:  # Has email
        score += 0.5
    
    # Check for numbers (likely dates, phone numbers, etc.)
    import re
    if re.search(r'\d{4}', text):  # Has 4-digit numbers (years)
        score += 0.5
    
    return min(score, 10.0)