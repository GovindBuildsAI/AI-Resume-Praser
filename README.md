AI RESUME PARSER
A college mini project using Flask, NLP, and Machine Learning.
AI Resume Parser is a web application that allows users to upload resumes (PDF, DOCX, TXT) and automatically extract key information such as:
Name
Email
Phone number
Skills
Education
Total experience
The system also compares the resume with a job description using TF-IDF + Cosine Similarity to generate a match score. All extracted data is stored in a SQLite database.
The backend uses Flask, PyResparser, spaCy, NLTK, and scikit-learn. The frontend uses HTML, CSS, and JavaScript.
TECH STACK
Backend:
Python
Flask
PyResparser
spaCy
NLTK
scikit-learn (TF-IDF + Cosine Similarity)
PDF/DOCX Processing:
pdfminer.six
python-docx
Database:
SQLite
Frontend:
HTML5
CSS3
JavaScript (Fetch API)
PROJECT STRUCTURE
Resume-Parser-AI/
│
├── main.py (Main Flask application)
├── resumes.db (SQLite database, auto-created)
├── uploads/ (Temporary folder for resume uploads)
├── README.md (Project documentation)
└── requirements.txt (Optional dependencies list)
SETUP INSTRUCTIONS
Step 1: Create environment (PyResparser compatibility requirement)
conda create -n resume_env python=3.8 -y
conda activate resume_env
Step 2: Install dependencies
pip install flask
pip install pyresparser
pip install "spacy<3.0,>=2.1.4"
pip install scikit-learn
pip install pdfminer.six
pip install python-docx
pip install nltk
Step 3: Download spaCy model
python -m spacy download en_core_web_sm
Step 4: Download required NLTK datasets
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger'); nltk.download('maxent_ne_chunker'); nltk.download('words')"
RUNNING THE APP
Activate environment:
conda activate resume_env
Run the server:
python main.py
Open in browser:
http://127.0.0.1:5000
