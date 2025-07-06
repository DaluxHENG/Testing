import google.generativeai as genai
import re
from typing import Dict, Any
from app.core.config import settings
from app.storage.data_models import AnalysisResult

# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)

async def analyze_resume(resume_text: str, ai_provider: str = "gemini") -> AnalysisResult:
    try:
        if ai_provider == "gemini":
            return await analyze_with_gemini(resume_text)
        elif ai_provider == "deepseek":
            return await analyze_with_deepseek(resume_text)
        else:
            raise ValueError(f"Unsupported AI provider: {ai_provider}")
    
    except Exception as e:
        # Return default analysis if AI analysis fails
        return AnalysisResult(
            resume_id="",
            ai_provider=ai_provider,
            overall_score=50.0,
            category_scores={
                "completeness": 50.0,
                "technical_skills": 50.0,
                "experience": 50.0,
                "education": 50.0,
                "presentation": 50.0
            },
            feedback=f"AI analysis failed: {str(e)}",
            suggestions=["Please check the resume format and content"]
        )

async def analyze_with_gemini(resume_text: str) -> AnalysisResult:
    try:
        # Use correct Gemini 2.0 model
        model = genai.GenerativeModel('gemini-2.0-flash')

        prompt = f"""
        Analyze the following resume and provide a structured assessment with scores.

        Resume Content:
        {resume_text}

        Please provide your analysis in the following JSON format:
        {{
            "overall_score": <score from 0-100>,
            "category_scores": {{
                "completeness": <score from 0-100>,
                "technical_skills": <score from 0-100>,
                "experience": <score from 0-100>,
                "education": <score from 0-100>,
                "presentation": <score from 0-100>
            }},
            "feedback": "<detailed feedback about the resume>",
            "suggestions": ["<suggestion 1>", "<suggestion 2>", "<suggestion 3>"]
        }}

        Scoring criteria:
        - Completeness: How complete is the resume (contact info, sections, etc.)
        - Technical Skills: Quality and relevance of technical skills
        - Experience: Quality and relevance of work experience
        - Education: Quality and relevance of education background
        - Presentation: Overall formatting, structure, and readability

        Provide only the JSON response, no additional text.
        """

        # Make Gemini call (sync model works fine even in async function)
        response = model.generate_content(prompt)

        import json
        analysis_data = json.loads(response.text)

        return AnalysisResult(
            resume_id="",
            ai_provider="gemini",
            overall_score=float(analysis_data.get("overall_score", 50.0)),
            category_scores={
                "completeness": float(analysis_data.get("category_scores", {}).get("completeness", 50.0)),
                "technical_skills": float(analysis_data.get("category_scores", {}).get("technical_skills", 50.0)),
                "experience": float(analysis_data.get("category_scores", {}).get("experience", 50.0)),
                "education": float(analysis_data.get("category_scores", {}).get("education", 50.0)),
                "presentation": float(analysis_data.get("category_scores", {}).get("presentation", 50.0))
            },
            feedback=analysis_data.get("feedback", "No feedback provided"),
            suggestions=analysis_data.get("suggestions", [])
        )

    except json.JSONDecodeError:
        return parse_ai_response_fallback(response.text)

    except Exception as e:
        raise Exception(f"Error with Gemini API: {str(e)}")


async def analyze_with_deepseek(resume_text: str) -> AnalysisResult:
    """Analyze resume using DeepSeek API"""
    # Implementation for DeepSeek API
    # This would require the DeepSeek API client
    
    return AnalysisResult(
        resume_id="",
        ai_provider="deepseek",
        overall_score=50.0,
        category_scores={
            "completeness": 50.0,
            "technical_skills": 50.0,
            "experience": 50.0,
            "education": 50.0,
            "presentation": 50.0
        },
        feedback="DeepSeek analysis not implemented yet",
        suggestions=["Implement DeepSeek API integration"]
    )

def parse_ai_response_fallback(response_text: str) -> AnalysisResult:
    """Fallback parser for AI response when JSON parsing fails"""
    try:
        # Extract scores using regex patterns
        import re
        
        # Look for overall score
        overall_score = 50.0
        overall_patterns = [
            r'overall.*?(\d+)',
            r'score.*?(\d+)',
            r'rating.*?(\d+)'
        ]
        
        for pattern in overall_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            if matches:
                try:
                    overall_score = float(matches[0])
                    break
                except:
                    continue
        
        # Extract category scores
        category_scores = {
            "completeness": 50.0,
            "technical_skills": 50.0,
            "experience": 50.0,
            "education": 50.0,
            "presentation": 50.0
        }
        
        # Look for category-specific scores
        category_patterns = {
            "completeness": [r'completeness.*?(\d+)', r'complete.*?(\d+)'],
            "technical_skills": [r'technical.*?(\d+)', r'skills.*?(\d+)'],
            "experience": [r'experience.*?(\d+)', r'work.*?(\d+)'],
            "education": [r'education.*?(\d+)', r'degree.*?(\d+)'],
            "presentation": [r'presentation.*?(\d+)', r'format.*?(\d+)']
        }
        
        for category, patterns in category_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, response_text, re.IGNORECASE)
                if matches:
                    try:
                        category_scores[category] = float(matches[0])
                        break
                    except:
                        continue
        
        # Extract suggestions
        suggestions = extract_suggestions(response_text)
        
        return AnalysisResult(
            resume_id="",
            ai_provider="gemini",
            overall_score=overall_score,
            category_scores=category_scores,
            feedback=response_text[:500] + "..." if len(response_text) > 500 else response_text,
            suggestions=suggestions
        )
    
    except Exception as e:
        return AnalysisResult(
            resume_id="",
            ai_provider="gemini",
            overall_score=50.0,
            category_scores={
                "completeness": 50.0,
                "technical_skills": 50.0,
                "experience": 50.0,
                "education": 50.0,
                "presentation": 50.0
            },
            feedback=f"Failed to parse AI response: {str(e)}",
            suggestions=["Please review the resume manually"]
        )

def extract_suggestions(text: str) -> list:
    """Extract suggestions from AI response"""
    suggestions = []
    
    # Look for numbered suggestions or bullet points
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if any(indicator in line.lower() for indicator in ['suggest', 'improve', 'recommend', 'should', 'consider']):
            # Clean up the suggestion
            suggestion = re.sub(r'^\d+\.\s*', '', line)  # Remove numbering
            suggestion = re.sub(r'^[-•*]\s*', '', suggestion)  # Remove bullets
            if suggestion and len(suggestion) > 10:  # Only add meaningful suggestions
                suggestions.append(suggestion)
    
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