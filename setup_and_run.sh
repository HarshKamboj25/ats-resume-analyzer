#!/bin/bash
# ==============================================
#  AI Resume Analyzer – Setup & Run Script
#  Run this once to install everything, then start
# ==============================================

echo ""
echo "=========================================="
echo "  AI Resume Analyzer – Setup"
echo "=========================================="
echo ""

# 1. Create virtual environment
echo "[1/5] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install Python packages
echo "[2/5] Installing Python packages..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 3. Download spaCy model
echo "[3/5] Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# 4. Download NLTK data
echo "[4/5] Downloading NLTK data..."
python -c "
import nltk
for pkg in ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'punkt_tab']:
    nltk.download(pkg, quiet=True)
print('NLTK data downloaded.')
"

# 5. Create uploads directory
echo "[5/5] Creating uploads directory..."
mkdir -p uploads

echo ""
echo "================================================"
echo "  Setup complete! Starting server..."
echo "  Open: http://localhost:5000"
echo "================================================"
echo ""

# Start Flask app
python app.py
