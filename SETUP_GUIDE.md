# 🚀 VS Code Setup Guide – AI Resume Analyzer

## What You'll Need
- Python 3.9 or higher
- VS Code (any recent version)
- Internet connection (to download packages)

---

## STEP 1 — Install Python

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 (recommended)
3. During install → ✅ CHECK "Add Python to PATH"
4. Click "Install Now"

Verify in terminal:
```
python --version
```
Should print: Python 3.11.x

---

## STEP 2 — Install VS Code

1. Go to https://code.visualstudio.com/
2. Download and install for your OS
3. Open VS Code

Install these VS Code Extensions (optional but helpful):
- Python (by Microsoft)
- Pylance
- Flask Snippets

---

## STEP 3 — Open the Project in VS Code

1. Extract the ZIP file you downloaded
2. Open VS Code
3. Click: File → Open Folder
4. Select the extracted "resume_analyzer" folder
5. Click "Open"

You should see this file structure in the left panel:
```
resume_analyzer/
├── app.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── nlp_processor.py
│   ├── parser.py
│   ├── scorer.py
│   └── suggester.py
└── templates/
    └── index.html
```

---

## STEP 4 — Open Terminal in VS Code

Press: Ctrl + ` (backtick key, top-left of keyboard)
OR go to: Terminal → New Terminal

You should see a terminal at the bottom of VS Code.

---

## STEP 5 — Create Virtual Environment

In the terminal, type these commands ONE BY ONE:

**Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

After activation, you'll see (venv) at the start of your terminal line.
This means the virtual environment is active. ✅

---

## STEP 6 — Install Dependencies

With (venv) active, run:
```
pip install flask werkzeug spacy nltk pdfplumber python-docx
```

This will take 2-5 minutes. You'll see packages downloading.

---

## STEP 7 — Download spaCy Language Model

```
python -m spacy download en_core_web_sm
```

Wait for it to finish. You'll see "✔ Download and installation successful"

---

## STEP 8 — Download NLTK Data

```
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('averaged_perceptron_tagger'); nltk.download('punkt_tab')"
```

---

## STEP 9 — Run the App

```
python app.py
```

You will see:
```
==================================================
  AI Resume Analyzer
  Running at: http://localhost:5000
==================================================
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

---

## STEP 10 — Open in Browser

Open your browser and go to:
```
http://localhost:5000
```

The ATS Resume Analyzer dashboard will load! 🎉

---

## How to Stop the Server

Press Ctrl + C in the terminal.

---

## How to Start Again Next Time

1. Open VS Code → Open the resume_analyzer folder
2. Open Terminal (Ctrl + `)
3. Activate virtual environment:
   - Windows: venv\Scripts\activate
   - Mac/Linux: source venv/bin/activate
4. Run: python app.py
5. Open http://localhost:5000

---

## Troubleshooting

**"python is not recognized"**
→ Python not added to PATH. Reinstall Python and check "Add to PATH"

**"No module named flask"**
→ Virtual environment not activated. Run: venv\Scripts\activate (Windows)

**"spacy model not found"**
→ Run: python -m spacy download en_core_web_sm

**Port 5000 already in use**
→ Change port in app.py last line: app.run(debug=True, port=5001)
→ Then open http://localhost:5001

**PDF not parsing**
→ Make sure pdfplumber is installed: pip install pdfplumber

---

## Project File Descriptions

| File | Purpose |
|------|---------|
| app.py | Main Flask server, routes, API endpoints |
| requirements.txt | List of Python packages needed |
| utils/parser.py | Reads PDF, DOCX, TXT files and extracts text |
| utils/nlp_processor.py | spaCy + NLTK NLP engine for skill/keyword extraction |
| utils/scorer.py | Calculates the ATS compatibility score (0-100) |
| utils/suggester.py | Generates improvement suggestions |
| templates/index.html | The entire frontend (HTML + CSS + JavaScript) |
