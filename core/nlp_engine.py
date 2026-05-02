import pandas as pd
import re
import os

def load_skills(file_path='data/skills.csv'):
    """
    Load predefined skills from a CSV file.
    """
    try:
        df = pd.read_csv(file_path)
        # Convert all skills to lowercase for case-insensitive matching
        skills = [str(skill).strip().lower() for skill in df['skill'].tolist()]
        return skills
    except Exception as e:
        print(f"Error loading skills: {e}")
        return []

def extract_skills(text, skills_list):
    """
    Extract skills from the given text based on the predefined skills list.
    """
    if not text:
        return []
    
    extracted_skills = set()
    text_lower = text.lower()
    
    # We use regex to find whole words matching the skills
    for skill in skills_list:
        # Escape special characters in skill (like C++)
        escaped_skill = re.escape(skill)
        # Word boundary \b is tricky for symbols like +, so we check if skill is in text simply, 
        # or use a more robust regex. Let's use simple string search for MVP to avoid regex \b issues with C++
        
        # Simple inclusion check is often better for technical terms like C++ or .NET
        if skill in text_lower:
            extracted_skills.add(skill.title()) # Capitalize for display
            
    return list(extracted_skills)
