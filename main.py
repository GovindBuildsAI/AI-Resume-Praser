# ============================================
# RESUME PARSER AI PROJECT
# Simple implementation using the required tech stack
# Tech Stack: Flask, PyResparser, spaCy, TF-IDF, SQLite
# ============================================

# ============================================
# STEP 1: INSTALLATION INSTRUCTIONS
# ============================================
# Run these commands in your terminal first:
#!pip install flask
#!pip install pyresparser
#!pip install spacy
#!pip install scikit-learn
#!pip install pdfminer.six
#!pip install python-docx
#!python -m spacy download en_core_web_sm


import nltk

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")


# ============================================
# STEP 2: IMPORT REQUIRED LIBRARIES
# ============================================

from flask import Flask, render_template_string, request, jsonify
from pyresparser import ResumeParser
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3
import os
import json


# ============================================
# STEP 3: INITIALIZE FLASK APP AND SPACY
# ============================================

# Create Flask application
app = Flask(__name__)

# Load spaCy model for NLP processing
nlp = spacy.load('en_core_web_sm')


# Folder to store uploaded resumes temporarily
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ============================================
# STEP 4: CREATE SQLITE DATABASE
# ============================================

def init_database():
    """
    Creates SQLite database and table to store parsed resume data
    Table: resumes
    Columns: id, name, email, phone, skills, education, experience
    """
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")

# Initialize database when app starts
init_database()


# ============================================
# STEP 5: PARSING MODULE - Extract Resume Data
# ============================================

def parse_resume(file_path):
    """
    Uses PyResparser to extract information from resume
    
    Parameters:
    - file_path: Path to the uploaded resume file
    
    Returns:
    - Dictionary containing extracted data (name, email, skills, etc.)
    """
    try:
        # PyResparser automatically extracts information
        data = ResumeParser(file_path).get_extracted_data()
        
        # Format the extracted data
        parsed_data = {
            'name': data.get('name', 'Not found'),
            'email': data.get('email', 'Not found'),
            'phone': data.get('mobile_number', 'Not found'),
            'skills': ', '.join(data.get('skills', [])) if data.get('skills') else 'Not found',
            'education': ', '.join([str(edu) for edu in data.get('degree', [])]) if data.get('degree') else 'Not found',
            'experience': str(data.get('total_experience', 'Not found'))
        }
        
        return parsed_data
    
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return None


# ============================================
# STEP 6: SAVE DATA TO SQLITE DATABASE
# ============================================

def save_to_database(data):
    """
    Saves parsed resume data to SQLite database
    
    Parameters:
    - data: Dictionary containing resume information
    """
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO resumes (name, email, phone, skills, education, experience)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['email'],
        data['phone'],
        data['skills'],
        data['education'],
        data['experience']
    ))
    
    conn.commit()
    conn.close()
    print("✓ Data saved to database")


# ============================================
# STEP 7: MATCHING MODULE - TF-IDF & Cosine Similarity
# ============================================

def calculate_match_score(resume_text, job_description):
    """
    Calculates similarity between resume and job description
    Uses TF-IDF (Term Frequency-Inverse Document Frequency) 
    and Cosine Similarity
    
    Parameters:
    - resume_text: Text extracted from resume
    - job_description: Job requirements text
    
    Returns:
    - Match score as percentage (0-100)
    """
    if not job_description or not resume_text:
        return 0
    
    # Combine resume and job description into a list
    documents = [resume_text, job_description]
    
    # Create TF-IDF vectors
    # This converts text into numerical vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    
    # Calculate cosine similarity
    # Measures how similar the two vectors are (0 = not similar, 1 = identical)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    
    # Convert to percentage
    match_score = round(similarity[0][0] * 100, 2)
    
    return match_score


# ============================================
# STEP 8: FLASK ROUTES - WEB INTERFACE
# ============================================

# HTML Template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Resume Parser AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .upload-section, .job-section, .results-section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 20px;
        }
        input[type="file"] {
            display: block;
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border: 2px dashed #667eea;
            border-radius: 5px;
            background: white;
        }
        textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            resize: vertical;
            font-family: Arial, sans-serif;
        }
        button {
            background: #667eea;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
            margin-top: 10px;
        }
        button:hover {
            background: #5568d3;
        }
        .result-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .result-label {
            font-weight: bold;
            color: #667eea;
            display: block;
            margin-bottom: 5px;
        }
        .match-score {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .score-high { color: #28a745; }
        .score-medium { color: #ffc107; }
        .score-low { color: #dc3545; }
        .hidden { display: none; }
        .loading {
            text-align: center;
            padding: 20px;
            color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Resume Parser AI</h1>
        <p class="subtitle">Upload resume and match with job description</p>
        
        <!-- UPLOAD SECTION -->
        <div class="upload-section">
            <h2>📄 Step 1: Upload Resume</h2>
            <input type="file" id="resumeFile" accept=".pdf,.docx,.txt">
            <small>Supported formats: PDF, DOCX, TXT</small>
        </div>
        
        <!-- JOB DESCRIPTION SECTION -->
        <div class="job-section">
            <h2>💼 Step 2: Job Description (Optional)</h2>
            <textarea id="jobDescription" rows="6" placeholder="Paste job description here to calculate match score..."></textarea>
        </div>
        
        <!-- PROCESS BUTTON -->
        <button onclick="processResume()">Parse Resume</button>
        
        <!-- LOADING -->
        <div id="loading" class="loading hidden">
            Processing resume...
        </div>
        
        <!-- RESULTS SECTION -->
        <div id="results" class="results-section hidden">
            <h2>✅ Parsed Results</h2>
            
            <div id="matchScoreDiv" class="hidden">
                <div class="match-score" id="matchScore"></div>
            </div>
            
            <div class="result-item">
                <span class="result-label">Name:</span>
                <span id="name"></span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Email:</span>
                <span id="email"></span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Phone:</span>
                <span id="phone"></span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Skills:</span>
                <span id="skills"></span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Education:</span>
                <span id="education"></span>
            </div>
            
            <div class="result-item">
                <span class="result-label">Experience:</span>
                <span id="experience"></span>
            </div>
        </div>
    </div>
    
    <script>
        // Function to process the uploaded resume
        function processResume() {
            const fileInput = document.getElementById('resumeFile');
            const jobDesc = document.getElementById('jobDescription').value;
            
            if (!fileInput.files[0]) {
                alert('Please upload a resume file first!');
                return;
            }
            
            // Create form data to send to server
            const formData = new FormData();
            formData.append('resume', fileInput.files[0]);
            formData.append('job_description', jobDesc);
            
            // Show loading, hide results
            document.getElementById('loading').classList.remove('hidden');
            document.getElementById('results').classList.add('hidden');
            
            // Send data to Flask backend
            fetch('/parse', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                document.getElementById('loading').classList.add('hidden');
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                // Display results
                document.getElementById('results').classList.remove('hidden');
                document.getElementById('name').textContent = data.name;
                document.getElementById('email').textContent = data.email;
                document.getElementById('phone').textContent = data.phone;
                document.getElementById('skills').textContent = data.skills;
                document.getElementById('education').textContent = data.education;
                document.getElementById('experience').textContent = data.experience;
                
                // Display match score if available
                if (data.match_score !== null) {
                    const scoreDiv = document.getElementById('matchScore');
                    const score = data.match_score;
                    let scoreClass = 'score-low';
                    if (score >= 60) scoreClass = 'score-high';
                    else if (score >= 40) scoreClass = 'score-medium';
                    
                    scoreDiv.innerHTML = `<span class="${scoreClass}">Match Score: ${score}%</span>`;
                    document.getElementById('matchScoreDiv').classList.remove('hidden');
                } else {
                    document.getElementById('matchScoreDiv').classList.add('hidden');
                }
            })
            .catch(error => {
                document.getElementById('loading').classList.add('hidden');
                alert('Error processing resume: ' + error);
            });
        }
    </script>
</body>
</html>
'''

# Route 1: Home page
@app.route('/')
def home():
    """
    Displays the main web interface
    """
    return render_template_string(HTML_TEMPLATE)


# Route 2: Parse resume endpoint
@app.route('/parse', methods=['POST'])
def parse():
    """
    Handles resume upload and processing
    
    Process:
    1. Receives uploaded resume file
    2. Saves file temporarily
    3. Parses resume using PyResparser
    4. Calculates match score if job description provided
    5. Saves data to SQLite database
    6. Returns results as JSON
    """
    try:
        # Get uploaded file
        if 'resume' not in request.files:
            return jsonify({'error': 'No file uploaded'})
        
        file = request.files['resume']
        job_description = request.form.get('job_description', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'})
        
        # Save file temporarily
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # PARSING MODULE: Extract data from resume
        print("Parsing resume...")
        parsed_data = parse_resume(file_path)
        
        if not parsed_data:
            return jsonify({'error': 'Failed to parse resume'})
        
        # MATCHING MODULE: Calculate match score
        match_score = None
        if job_description:
            print("Calculating match score...")
            resume_text = f"{parsed_data['name']} {parsed_data['skills']} {parsed_data['education']}"
            match_score = calculate_match_score(resume_text, job_description)
        
        # Save to database
        save_to_database(parsed_data)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Return results
        result = {
            'name': parsed_data['name'],
            'email': parsed_data['email'],
            'phone': parsed_data['phone'],
            'skills': parsed_data['skills'],
            'education': parsed_data['education'],
            'experience': parsed_data['experience'],
            'match_score': match_score
        }
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)})


# Route 3: View all parsed resumes from database
@app.route('/view')
def view_resumes():
    """
    Displays all resumes stored in the database
    """
    conn = sqlite3.connect('resumes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM resumes')
    resumes = cursor.fetchall()
    conn.close()
    
    html = '<h1>All Parsed Resumes</h1>'
    for resume in resumes:
        html += f'<div style="border:1px solid #ccc; padding:10px; margin:10px;">'
        html += f'<p><b>ID:</b> {resume[0]}</p>'
        html += f'<p><b>Name:</b> {resume[1]}</p>'
        html += f'<p><b>Email:</b> {resume[2]}</p>'
        html += f'<p><b>Phone:</b> {resume[3]}</p>'
        html += f'<p><b>Skills:</b> {resume[4]}</p>'
        html += f'<p><b>Education:</b> {resume[5]}</p>'
        html += f'<p><b>Experience:</b> {resume[6]}</p>'
        html += '</div>'
    
    return html



# ============================================
# STEP 9: RUN THE APPLICATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("RESUME PARSER AI - Starting Application")
    print("=" * 50)
    print("✓ Flask server starting...")
    print("✓ Open your browser and go to: http://127.0.0.1:5000")
    print("✓ Upload a resume (PDF/DOCX/TXT) to test the parser")
    print("=" * 50)

    app.run(host="127.0.0.1", port=5000, debug=False)
