import google.generativeai as genai
from typing import Dict, Any
from app.core.config import settings

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def analyze_resume(resume_text: str, ai_provider: str = "gemini") -> Dict[str, Any]:
    """Analyze resume content using AI"""
    try:
        if ai_provider == "gemini":
            return await analyze_with_gemini(resume_text)
        elif ai_provider == "deepseek":
            return await analyze_with_deepseek(resume_text)
        else:
            raise ValueError(f"Unsupported AI provider: {ai_provider}")
    
    except Exception as e:
        raise Exception(f"Error analyzing resume: {str(e)}")

async def analyze_with_gemini(resume_text: str) -> Dict[str, Any]:
    """Analyze resume using Google Gemini"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Analyze the following resume and provide detailed feedback:

        Resume Content:
        {resume_text}

        Please provide:
        1. Overall assessment and rating (1-10)
        2. Strengths and weaknesses
        3. Specific suggestions for improvement
        4. Technical skills assessment
        5. Experience relevance
        6. Educational background evaluation
        7. Overall presentation and formatting feedback

        Format your response as a structured analysis with clear sections.
        """
        
        response = model.generate_content(prompt)
        
        # Parse the response into structured format
        analysis = parse_ai_response(response.text)
        
        return analysis
    
    except Exception as e:
        raise Exception(f"Error with Gemini API: {str(e)}")

async def analyze_with_deepseek(resume_text: str) -> Dict[str, Any]:
    """Analyze resume using DeepSeek API"""
    # Implementation for DeepSeek API
    # This would require the DeepSeek API client
    
    return {
        "feedback": "DeepSeek analysis not implemented yet",
        "suggestions": ["Implement DeepSeek API integration"],
        "technical_skills": [],
        "experience_rating": 5.0,
        "education_rating": 5.0
    }

def parse_ai_response(response_text: str) -> Dict[str, Any]:
    """Parse AI response into structured format"""
    try:
        # This is a simplified parser - you might want to use more sophisticated parsing
        analysis = {
            "feedback": response_text,
            "suggestions": extract_suggestions(response_text),
            "technical_skills": extract_technical_skills(response_text),
            "experience_rating": extract_rating(response_text, "experience"),
            "education_rating": extract_rating(response_text, "education")
        }
        
        return analysis
    
    except Exception as e:
        return {
            "feedback": response_text,
            "suggestions": [],
            "technical_skills": [],
            "experience_rating": 5.0,
            "education_rating": 5.0
        }

def extract_suggestions(text: str) -> list:
    """Extract suggestions from AI response"""
    suggestions = []
    
    # Look for numbered suggestions or bullet points
    lines = text.split('\n')
    for line in lines:
        if any(indicator in line.lower() for indicator in ['suggest', 'improve', 'recommend', 'should']):
            suggestions.append(line.strip())
    
    return suggestions[:5]  # Limit to top 5 suggestions

def extract_technical_skills(text: str) -> list:
    """Extract mentioned technical skills"""
    skills = []
    
    # Common technical skills to look for
    tech_skills = [
        'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'HTML', 'CSS',
        'Git', 'Docker', 'AWS', 'Azure', 'MongoDB', 'PostgreSQL', 'FastAPI'
    ]
    
    text_lower = text.lower()
    for skill in tech_skills:
        if skill.lower() in text_lower:
            skills.append(skill)
    
    return list(set(skills))

def extract_rating(text: str, category: str) -> float:
    """Extract rating for specific category"""
    import re
    
    # Look for patterns like "8/10", "7 out of 10", etc.
    rating_patterns = [
        r'(\d+)/10',
        r'(\d+) out of 10',
        r'rating.*?(\d+)',
        r'score.*?(\d+)'
    ]
    
    for pattern in rating_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                return float(matches[0])
            except:
                continue
    
    return 5.0 