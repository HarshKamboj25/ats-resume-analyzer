"""
AI Resume Analyzer - Main Flask Application
==========================================
Run with: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os

from utils.parser import extract_text_from_file
from utils.nlp_processor import ResumeNLPProcessor
from utils.scorer import ATSScorer
from utils.suggester import ResumeSuggester

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'resume-analyzer-secret-key'

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

nlp_processor = ResumeNLPProcessor()
scorer = ATSScorer()
suggester = ResumeSuggester()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    resume_text = ""
    filename = ""

    # Handle file upload
    if 'resume_file' in request.files and request.files['resume_file'].filename:
        file = request.files['resume_file']
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT.'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        resume_text = extract_text_from_file(filepath)
        os.remove(filepath)  # Clean up after extraction

    elif 'resume_text' in request.form and request.form['resume_text'].strip():
        resume_text = request.form['resume_text'].strip()
    else:
        return jsonify({'error': 'Please upload a file or paste resume text.'}), 400

    if not resume_text or len(resume_text.strip()) < 50:
        return jsonify({'error': 'Could not extract enough text. Please paste your resume manually.'}), 400

    job_description = request.form.get('job_description', '').strip()

    # --- Core Analysis Pipeline ---
    # 1. NLP Processing
    parsed = nlp_processor.parse_resume(resume_text)

    # 2. ATS Scoring
    score_data = scorer.calculate_score(parsed, job_description)

    # 3. Suggestions
    suggestions = suggester.generate_suggestions(parsed, score_data)

    return jsonify({
        'success': True,
        'filename': filename,
        'ats_score': score_data['ats_score'],
        'score_breakdown': score_data['breakdown'],
        'verdict': score_data['verdict'],
        'parsed': parsed,
        'suggestions': suggestions,
        'job_match': score_data.get('job_match', {}),
    })


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Resume Analyzer API is running'})


if __name__ == '__main__':
    print("=" * 50)
    print("  AI Resume Analyzer")
    print("  Running at: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
