import PyPDF2
from docx import Document
from typing import Dict, Any
import os
import re
from pathlib import Path

async def parse_resume(file_path: str) -> Dict[str, Any]:
    """Parse resume and extract text content"""
    try:
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension == '.pdf':
            extracted_text = extract_text_from_pdf(file_path)
        elif file_extension in ['.docx', '.doc']:
            extracted_text = extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Parse structured data
        parsed_data = parse_structured_data(extracted_text)
        
        return {
            "extracted_text": extracted_text,
            "parsed_data": parsed_data,
            "parsing_method": f"{file_extension[1:]}_parser"
        }
    
    except Exception as e:
        raise Exception(f"Error parsing resume: {str(e)}")

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")
    
    return text.strip()

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        raise Exception(f"Error reading DOCX: {str(e)}")
    
    return text.strip()

def parse_structured_data(text: str) -> Dict[str, Any]:
    """Parse structured data from resume text"""
    data = {
        "contact_info": extract_contact_info(text),
        "skills": extract_skills(text),
        "experience": extract_experience(text),
        "education": extract_education(text),
        "summary": extract_summary(text)
    }
    
    return data

def extract_contact_info(text: str) -> Dict[str, str]:
    """Extract contact information"""
    contact_info = {}
    
    # Email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info['email'] = email_match.group()
    
    # Phone
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info['phone'] = phone_match.group()
    
    # LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group()
    
    return contact_info

def extract_skills(text: str) -> list:
    """Extract skills from resume text"""
    skills = []
    
    # Common technical skills
    tech_skills = [
        'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'HTML', 'CSS',
        'Git', 'Docker', 'AWS', 'Azure', 'MongoDB', 'PostgreSQL', 'FastAPI',
        'Django', 'Flask', 'Machine Learning', 'AI', 'Data Science'
    ]
    
    text_lower = text.lower()
    for skill in tech_skills:
        if skill.lower() in text_lower:
            skills.append(skill)
    
    return list(set(skills))

def extract_experience(text: str) -> list:
    """Extract work experience"""
    experience = []
    
    # Look for common experience indicators
    experience_patterns = [
        r'(.*?)\s*[-–—]\s*(\d{4}.*?)(?:\n|$)',
        r'(\d{4}.*?)\s*[-–—]\s*(.*?)(?:\n|$)'
    ]
    
    lines = text.split('\n')
    for line in lines:
        if any(word in line.lower() for word in ['experience', 'work', 'employment', 'position']):
            experience.append(line.strip())
    
    return experience

def extract_education(text: str) -> list:
    """Extract education information"""
    education = []
    
    # Look for education keywords
    education_keywords = ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'phd']
    
    lines = text.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in education_keywords):
            education.append(line.strip())
    
    return education

def extract_summary(text: str) -> str:
    """Extract resume summary/objective"""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if any(word in line.lower() for word in ['summary', 'objective', 'profile', 'about']):
            # Return next few lines as summary
            summary_lines = lines[i:i+3]
            return ' '.join(summary_lines).strip()
    