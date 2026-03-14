# AI Resume Analyzer – ATS Score Predictor

A full-stack Python web application that analyzes resumes using **spaCy** and **NLTK**,
calculates an ATS compatibility score, and provides improvement suggestions.

---

## Project Structure

```
resume_analyzer/
│
├── app.py                    ← Flask application entry point
├── requirements.txt          ← Python dependencies
├── setup_and_run.sh          ← One-click setup + run script
│
├── utils/
│   ├── __init__.py
│   ├── parser.py             ← PDF / DOCX / TXT text extraction
│   ├── nlp_processor.py      ← spaCy + NLTK NLP engine
│   ├── scorer.py             ← ATS score calculator
│   └── suggester.py          ← Improvement suggestions generator
│
├── templates/
│   └── index.html            ← Frontend (HTML + CSS + JavaScript)
│
└── uploads/                  ← Temporary file storage (auto-created)
```

---

## Quick Start

### Option A – One command (Linux / macOS)
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Option B – Manual setup
```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download spaCy English model
python -m spacy download en_core_web_sm

# 4. Download NLTK data
python -c "import nltk; [nltk.download(p) for p in ['punkt','stopwords','averaged_perceptron_tagger','punkt_tab']]"

# 5. Run the app
python app.py
```

Open your browser at **http://localhost:5000**

---

## How It Works

### 1. File Upload & Parsing (`utils/parser.py`)
- **PDF** files are parsed using `pdfplumber` (handles multi-page, columns)
- **DOCX** files are parsed using `python-docx` (paragraphs + tables)
- **TXT** files are read directly

### 2. NLP Processing (`utils/nlp_processor.py`)

| Component | Library | What it does |
|-----------|---------|--------------|
| Skill extraction | spaCy + regex | Matches 100+ skills from a curated database |
| Named entities | spaCy NER | Extracts organizations, locations, dates |
| Name detection | spaCy PERSON | Finds candidate name from text |
| Tokenization | NLTK word_tokenize | Splits text into individual tokens |
| Keyword analysis | NLTK Counter | Top 20 keywords by frequency |
| Stop word removal | NLTK stopwords | Removes "the", "and", "is", etc. |
| Readability | Custom metric | Avg. sentence length → Easy/Moderate/Complex |

### 3. ATS Scoring (`utils/scorer.py`)

| Dimension | Weight | How it's calculated |
|-----------|--------|---------------------|
| Skills presence | 30% | Detected skills / 20 target skills |
| Section completeness | 20% | Sections found / 6 ideal sections |
| Keyword density | 20% | Unique keywords / total word count |
| Readability | 15% | Easy=100, Moderate=75, Complex=45 |
| Contact info | 15% | Email + phone + LinkedIn |

When a **job description** is provided, keyword matching is blended in
(70% base score + 30% JD match score).

### 4. Suggestions (`utils/suggester.py`)
Generates prioritized (High / Medium / Low) suggestions based on:
- Missing contact info
- Missing resume sections
- Low skill count
- No measurable achievements (no numbers found)
- Resume too short or too long
- Job description keyword gaps

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web interface |
| POST | `/analyze` | Analyze a resume (multipart/form-data) |
| GET | `/health` | Health check |

### POST `/analyze` – Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resume_file` | File | Optional* | PDF, DOCX, or TXT file |
| `resume_text` | String | Optional* | Plain text resume |
| `job_description` | String | Optional | JD for keyword matching |

*At least one of `resume_file` or `resume_text` is required.

### POST `/analyze` – Response JSON

```json
{
  "success": true,
  "ats_score": 78,
  "verdict": "Good – Solid resume with minor improvements recommended.",
  "score_breakdown": {
    "skills": 85,
    "sections": 80,
    "keywords": 70,
    "readability": 75,
    "contact": 100
  },
  "parsed": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1 555-0100",
    "linkedin": "linkedin.com/in/johndoe",
    "skills": {
      "found": ["python", "react", "sql", "aws"],
      "missing": ["docker", "kubernetes"],
      "count": 4
    },
    "sections_detected": ["Summary", "Experience", "Education", "Skills"],
    "keywords": ["engineer", "developed", "built", "system", "team"],
    "word_count": 512,
    "readability": "Moderate",
    "experience": { "estimated_years": 4.5, "job_titles": ["Software Engineer"] },
    "education": { "degrees": ["B.Tech Computer Science"], "years": ["2022", "2018"] },
    "certifications": ["AWS Certified Developer"],
    "entities": {
      "organizations": ["Google", "Infosys"],
      "locations": ["Bangalore"],
      "dates": ["2022", "2020 - 2022"]
    }
  },
  "suggestions": [
    {
      "priority": "high",
      "category": "Impact",
      "title": "Add measurable achievements",
      "detail": "Use numbers: 'Improved performance by 40%', 'Led team of 8', etc."
    }
  ],
  "job_match": {
    "match_score": 65,
    "matched_skills": ["python", "sql"],
    "missing_skills": ["docker", "terraform"],
    "matched_keywords": ["engineer", "backend"],
    "missing_keywords": ["microservices", "gcp"]
  }
}
```

---

## Technologies Used

| Category | Technology |
|----------|------------|
| Language | Python 3.9+ |
| Web Framework | Flask 3.x |
| NLP – Core | spaCy 3.x (en_core_web_sm) |
| NLP – Tokenization | NLTK 3.x |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| Frontend | HTML5, CSS3, Vanilla JavaScript |

---

## Future Improvements
- ML model (scikit-learn) for more accurate scoring
- Resume template recommendations
- AI-generated rewrite suggestions
- Integration with LinkedIn Jobs API
- User accounts and history tracking
- Resume export with improvements applied
