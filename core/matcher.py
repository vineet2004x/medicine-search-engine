from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match_score(resume_text, job_description_text):
    """
    Calculates a match score between the resume and the job description
    using TF-IDF and cosine similarity.
    """
    if not resume_text or not job_description_text:
        return 0.0
        
    documents = [resume_text, job_description_text]
    
    # Create the TF-IDF matrix
    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # Calculate cosine similarity between the two documents
        # tfidf_matrix[0:1] is the resume, tfidf_matrix[1:2] is the job description
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        
        # Extract the score and convert to percentage
        match_score = cosine_sim[0][0] * 100
        return round(match_score, 2)
    except Exception as e:
        print(f"Error calculating match score: {e}")
        return 0.0

def calculate_ats_score(skill_match_score, similarity_score):
    """
    Calculates a basic composite ATS score.
    For Phase 1 MVP, we use a simple weighted average.
    - Skill match: 50%
    - Keyword similarity: 50%
    """
    # Skill match score is a percentage (e.g., 80.0)
    # Similarity score is a percentage (e.g., 60.0)
    composite_score = (skill_match_score * 0.5) + (similarity_score * 0.5)
    return round(composite_score, 2)
