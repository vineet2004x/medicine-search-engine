import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from core.parser import extract_text
from core.nlp_engine import load_skills, extract_skills
from core.matcher import calculate_match_score, calculate_ats_score

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_phase_1' # Needed for flash messages
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load skills globally once at startup
PREDEFINED_SKILLS = load_skills('data/skills.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume' not in request.files:
            flash('No resume part')
            return redirect(request.url)
            
        file = request.files['resume']
        job_description = request.form.get('job_description', '').strip()
        
        # If user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        if not job_description:
            flash('Please provide a job description')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # --- Analysis Process ---
            
            # 1. Parse Resume
            resume_text = extract_text(filepath)
            
            # 2. Extract Skills from Resume
            extracted_resume_skills = extract_skills(resume_text, PREDEFINED_SKILLS)
            
            # 3. Extract Skills from Job Description (to calculate skill match score)
            jd_skills = extract_skills(job_description, PREDEFINED_SKILLS)
            
            # Calculate Skill Match Score
            if jd_skills:
                matched_skills = [skill for skill in extracted_resume_skills if skill in jd_skills]
                skill_match_score = (len(matched_skills) / len(jd_skills)) * 100
            else:
                skill_match_score = 0.0
                
            # 4. Job Description Matching (TF-IDF Similarity)
            similarity_score = calculate_match_score(resume_text, job_description)
            
            # 5. Composite ATS Score
            ats_score = calculate_ats_score(skill_match_score, similarity_score)
            
            # Clean up the uploaded file to save space (optional but good practice)
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error removing file: {e}")
                
            return render_template(
                'index.html',
                resume_text=resume_text, # Passed for debugging/verification, optional to display
                skills=extracted_resume_skills,
                similarity_score=similarity_score,
                skill_match_score=round(skill_match_score, 2),
                ats_score=ats_score,
                show_results=True
            )
        else:
            flash('Allowed file types are pdf, docx, doc')
            return redirect(request.url)

    return render_template('index.html', show_results=False)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
