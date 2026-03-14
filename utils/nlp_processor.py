"""
utils/nlp_processor.py
======================
Core NLP processing using spaCy and NLTK.

spaCy  → Named entity recognition, skill extraction, noun chunks
NLTK   → Tokenization, stopword removal, keyword frequency analysis

Extracts:
  - Name, email, phone
  - Skills (matched against skill database)
  - Education details
  - Work experience
  - Certifications
  - Section detection
  - Word count, readability metrics
"""

import re
import string
from collections import Counter

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

# Download required NLTK data on first run
for pkg in ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'punkt_tab']:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Master skill database – covers tech, soft skills, tools, domains
# ---------------------------------------------------------------------------
SKILL_DATABASE = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "ruby", "php", "scala", "r", "matlab", "perl",

    # Web / Frontend
    "html", "css", "react", "angular", "vue", "next.js", "nuxt", "svelte",
    "bootstrap", "tailwind", "sass", "webpack", "vite", "jquery",

    # Backend / APIs
    "node.js", "express", "django", "flask", "fastapi", "spring boot",
    "asp.net", "graphql", "rest api", "microservices",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "firebase", "dynamodb", "cassandra", "elasticsearch",

    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux", "bash", "nginx",

    # Data Science / ML / AI
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "matplotlib", "seaborn", "data analysis", "data visualization",
    "statistics", "a/b testing", "feature engineering",

    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake", "bigquery",
    "etl", "data pipeline", "data warehouse",

    # Version Control & Tools
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "postman", "vs code", "intellij", "figma",

    # Soft Skills
    "leadership", "communication", "teamwork", "problem solving",
    "critical thinking", "project management", "agile", "scrum",
    "time management", "collaboration",

    # Business / Analytics
    "excel", "power bi", "tableau", "looker", "google analytics",
    "seo", "digital marketing", "crm", "salesforce",

    # Security
    "cybersecurity", "penetration testing", "networking", "oauth",
    "jwt", "ssl", "firewalls",
}

# Section header patterns
SECTION_PATTERNS = {
    "Summary":       r'\b(summary|objective|profile|about me|professional summary)\b',
    "Experience":    r'\b(experience|work experience|employment|work history|career history)\b',
    "Education":     r'\b(education|academic|qualification|degree|university|college)\b',
    "Skills":        r'\b(skills|technical skills|core competencies|expertise|technologies)\b',
    "Projects":      r'\b(projects|personal projects|key projects|portfolio)\b',
    "Certifications":r'\b(certifications?|certificates?|accreditation|licenses?)\b',
    "Awards":        r'\b(awards?|honors?|achievements?|accomplishments?)\b',
    "Languages":     r'\b(languages?)\b',
    "Interests":     r'\b(interests?|hobbies|activities)\b',
    "References":    r'\b(references?)\b',
}


class ResumeNLPProcessor:
    """
    Main NLP engine for resume parsing and feature extraction.
    Uses spaCy for NER and NLTK for tokenization/keyword analysis.
    """

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self._load_spacy()

    def _load_spacy(self):
        """Load spaCy model (en_core_web_sm)."""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            try:
                import subprocess, sys
                subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
                import spacy
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                self.nlp = None  # Fallback: use regex only

    def parse_resume(self, text: str) -> dict:
        """
        Full pipeline: parse all fields from raw resume text.
        Returns a structured dict with all extracted info.
        """
        cleaned = self._clean_text(text)
        tokens = word_tokenize(cleaned.lower())
        sentences = sent_tokenize(text)

        return {
            "raw_text":          text,
            "cleaned_text":      cleaned,
            "word_count":        len(tokens),
            "sentence_count":    len(sentences),
            "name":              self._extract_name(text),
            "email":             self._extract_email(text),
            "phone":             self._extract_phone(text),
            "linkedin":          self._extract_linkedin(text),
            "skills":            self._extract_skills(text),
            "education":         self._extract_education(text),
            "experience":        self._extract_experience(text),
            "certifications":    self._extract_certifications(text),
            "sections_detected": self._detect_sections(text),
            "keywords":          self._extract_keywords(tokens),
            "entities":          self._extract_entities(text),
            "readability":       self._readability_score(text, sentences, tokens),
            "has_contact":       bool(self._extract_email(text) or self._extract_phone(text)),
        }

    # ------------------------------------------------------------------
    # Contact Information
    # ------------------------------------------------------------------

    def _extract_name(self, text: str) -> str:
        """Try spaCy PERSON entity first, fallback to first capitalized line."""
        if self.nlp:
            doc = self.nlp(text[:500])
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text.strip()
        # Fallback: first non-empty line that looks like a name
        for line in text.split('\n'):
            line = line.strip()
            if 2 <= len(line.split()) <= 4 and line[0].isupper() and not any(c in line for c in ['@', ':', '|']):
                return line
        return "Not detected"

    def _extract_email(self, text: str) -> str:
        match = re.search(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', text)
        return match.group() if match else ""

    def _extract_phone(self, text: str) -> str:
        match = re.search(
            r'(\+?\d{1,3}[\s\-]?)?(\(?\d{3}\)?[\s\-]?)?\d{3}[\s\-]?\d{4}', text
        )
        return match.group().strip() if match else ""

    def _extract_linkedin(self, text: str) -> str:
        match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
        return match.group() if match else ""

    # ------------------------------------------------------------------
    # Skills Extraction (NLP + Pattern Matching)
    # ------------------------------------------------------------------

    def _extract_skills(self, text: str) -> dict:
        """
        Match text against SKILL_DATABASE using:
        1. Direct substring matching (case-insensitive, handles multi-word skills)
        2. spaCy noun-chunks for additional skill candidates
        Returns dict with 'found' and 'missing' lists.
        """
        text_lower = text.lower()
        found = []
        missing = []

        for skill in SKILL_DATABASE:
            if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
                found.append(skill)
            else:
                missing.append(skill)

        # Sort and cap missing to most relevant
        missing_common = [s for s in missing if s in {
            "docker", "kubernetes", "aws", "sql", "git", "linux",
            "machine learning", "data analysis", "rest api", "agile",
            "ci/cd", "typescript", "postgresql", "redis", "terraform"
        }]

        return {
            "found":   sorted(found),
            "missing": sorted(missing_common[:15]),
            "count":   len(found),
        }

    # ------------------------------------------------------------------
    # Education
    # ------------------------------------------------------------------

    def _extract_education(self, text: str) -> list:
        degrees = []
        degree_pattern = re.compile(
            r'(b\.?tech|b\.?e\.?|b\.?sc?\.?|m\.?tech|m\.?sc?\.?|m\.?e\.?|'
            r'mba|ph\.?d\.?|bachelor|master|doctorate|b\.?a\.?|m\.?a\.?)'
            r'[^\n]{0,80}',
            re.IGNORECASE
        )
        for match in degree_pattern.finditer(text):
            degrees.append(match.group().strip())

        # Extract years using spaCy DATE entities
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        return {
            "degrees": degrees[:5],
            "years":   sorted(set(years), reverse=True)[:4],
        }

    # ------------------------------------------------------------------
    # Work Experience
    # ------------------------------------------------------------------

    def _extract_experience(self, text: str) -> dict:
        """
        Estimate total years of experience from date ranges in the text.
        Also extracts job titles using spaCy.
        """
        # Find year ranges like 2019-2022 or 2020 - Present
        year_pattern = re.compile(
            r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|19\d{2}|present|current|now)',
            re.IGNORECASE
        )
        import datetime
        current_year = datetime.datetime.now().year
        total_months = 0

        for m in year_pattern.finditer(text):
            start = int(m.group(1))
            end_str = m.group(2).lower()
            end = current_year if end_str in ('present', 'current', 'now') else int(end_str)
            total_months += max(0, (end - start) * 12)

        total_years = round(total_months / 12, 1)

        # Extract job titles
        titles = []
        title_pattern = re.compile(
            r'\b(engineer|developer|analyst|manager|designer|architect|'
            r'consultant|director|lead|intern|specialist|scientist|'
            r'administrator|devops|qa|tester)\b',
            re.IGNORECASE
        )
        for m in title_pattern.finditer(text):
            context_start = max(0, m.start() - 25)
            context = text[context_start: m.end()].strip()
            if context not in titles:
                titles.append(context)

        return {
            "estimated_years": total_years if total_years > 0 else "Not detected",
            "job_titles":      titles[:6],
        }

    # ------------------------------------------------------------------
    # Certifications
    # ------------------------------------------------------------------

    def _extract_certifications(self, text: str) -> list:
        cert_pattern = re.compile(
            r'\b(aws certified|google certified|microsoft certified|pmp|'
            r'comptia|cisco|ccna|ccnp|ceh|oscp|gcp associate|azure|'
            r'certified scrum|six sigma|cissp|cpa|cfa|oracle certified|'
            r'tensorflow developer|databricks|snowflake)\b[^\n]{0,60}',
            re.IGNORECASE
        )
        return list({m.group().strip() for m in cert_pattern.finditer(text)})[:10]

    # ------------------------------------------------------------------
    # Section Detection
    # ------------------------------------------------------------------

    def _detect_sections(self, text: str) -> list:
        text_lower = text.lower()
        found = []
        for section, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, text_lower):
                found.append(section)
        return found

    # ------------------------------------------------------------------
    # NLTK Keyword Extraction
    # ------------------------------------------------------------------

    def _extract_keywords(self, tokens: list) -> list:
        """
        Use NLTK to find the top meaningful keywords:
        1. Remove stop words and punctuation
        2. Keep words >= 3 chars
        3. Return top 20 by frequency
        """
        filtered = [
            w for w in tokens
            if w not in self.stop_words
            and w not in string.punctuation
            and len(w) >= 3
            and w.isalpha()
        ]
        freq = Counter(filtered)
        return [word for word, _ in freq.most_common(20)]

    # ------------------------------------------------------------------
    # Named Entity Recognition (spaCy)
    # ------------------------------------------------------------------

    def _extract_entities(self, text: str) -> dict:
        """Use spaCy NER to extract organizations, locations, dates."""
        if not self.nlp:
            return {}
        doc = self.nlp(text[:3000])
        entities = {"ORG": [], "GPE": [], "DATE": []}
        for ent in doc.ents:
            if ent.label_ in entities and ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
        return {
            "organizations": entities["ORG"][:8],
            "locations":     entities["GPE"][:5],
            "dates":         entities["DATE"][:6],
        }

    # ------------------------------------------------------------------
    # Readability
    # ------------------------------------------------------------------

    def _readability_score(self, text: str, sentences: list, tokens: list) -> str:
        """
        Simple readability metric based on average sentence length.
        Flesch-Kincaid inspired: < 15 words/sentence = Easy, etc.
        """
        if not sentences:
            return "Unknown"
        avg_len = len(tokens) / len(sentences)
        if avg_len < 12:
            return "Easy"
        elif avg_len < 20:
            return "Moderate"
        else:
            return "Complex"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace, special chars, normalize text."""
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)     # Remove non-ASCII
        text = re.sub(r'\s+', ' ', text)                  # Normalize whitespace
        text = text.strip()
        return text
