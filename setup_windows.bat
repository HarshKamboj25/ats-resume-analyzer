@echo off
echo.
echo ==================================================
echo   AI Resume Analyzer - Windows Setup
echo ==================================================
echo.

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.9+ and add to PATH.
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate

echo [3/6] Upgrading pip...
python -m pip install --upgrade pip --quiet

echo [4/6] Installing Python packages...
pip install flask werkzeug spacy nltk pdfplumber python-docx --quiet
if errorlevel 1 (
    echo ERROR: Package installation failed. Check your internet connection.
    pause
    exit /b 1
)

echo [5/6] Downloading spaCy English model...
python -m spacy download en_core_web_sm

echo [6/6] Downloading NLTK data...
python -c "import nltk; [nltk.download(p, quiet=True) for p in ['punkt','stopwords','averaged_perceptron_tagger','punkt_tab']]; print('NLTK data ready.')"

echo.
echo ==================================================
echo   Setup complete! Starting server...
echo   Open browser: http://localhost:5000
echo ==================================================
echo.

python app.py
pause
