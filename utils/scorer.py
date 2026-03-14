"""
utils/scorer.py
===============
Calculates the ATS Compatibility Score (0–100) based on:
  - Skills presence        (30%)
  - Section completeness   (20%)
  - Keyword density        (20%)
  - Readability            (15%)
  - Contact info           (15%)

When a job description is provided, adds:
  - Keyword match analysis
  - Job relevance score
"""

import re
from collections import Counter


# Weights for each scoring dimension
WEIGHTS = {
    "skills":       0.30,
    "sections":     0.20,
    "keywords":     0.20,
    "readability":  0.15,
    "contact":      0.15,
}

# Ideal section list for a strong resume
IDEAL_SECTIONS = {"Summary", "Experience", "Education", "Skills", "Projects", "Certifications"}

READABILITY_SCORES = {"Easy": 100, "Moderate": 75, "Complex": 45, "Unknown": 50}


class ATSScorer:
    """Calculates multi-dimensional ATS compatibility score."""

    def calculate_score(self, parsed: dict, job_description: str = "") -> dict:
        breakdown = {}

        # 1. Skills Score (0–100)
        skill_count = parsed["skills"]["count"]
        breakdown["skills"] = min(100, int((skill_count / 20) * 100))

        # 2. Sections Score (0–100)
        detected = set(parsed.get("sections_detected", []))
        matched_sections = IDEAL_SECTIONS & detected
        breakdown["sections"] = int((len(matched_sections) / len(IDEAL_SECTIONS)) * 100)

        # 3. Keyword Density Score (0–100)
        word_count = parsed.get("word_count", 0)
        keyword_count = len(parsed.get("keywords", []))
        if word_count > 0:
            density = keyword_count / word_count
            breakdown["keywords"] = min(100, int(density * 1500))
        else:
            breakdown["keywords"] = 0

        # 4. Readability Score (0–100)
        readability = parsed.get("readability", "Unknown")
        breakdown["readability"] = READABILITY_SCORES.get(readability, 50)

        # 5. Contact Info Score (0–100)
        contact_score = 0
        if parsed.get("has_contact"):
            contact_score += 50
        if parsed.get("email"):
            contact_score += 25
        if parsed.get("phone"):
            contact_score += 25
        breakdown["contact"] = contact_score

        # Weighted ATS Score
        ats_score = int(sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS))
        ats_score = max(0, min(100, ats_score))

        # Job Description Matching
        job_match = {}
        if job_description:
            job_match = self._match_job_description(parsed, job_description)
            # Blend JD match into final score (30% weight)
            ats_score = int(ats_score * 0.70 + job_match["match_score"] * 0.30)

        return {
            "ats_score":  ats_score,
            "breakdown":  breakdown,
            "verdict":    self._verdict(ats_score),
            "job_match":  job_match,
        }

    def _match_job_description(self, parsed: dict, jd: str) -> dict:
        """
        Compare resume keywords and skills against job description.
        Returns matching/missing keywords and a match percentage.
        """
        # Extract words from JD (clean, lowercase, no stopwords)
        jd_words = set(re.findall(r'\b[a-z][a-z+#.]{2,}\b', jd.lower()))

        resume_text_lower = parsed["raw_text"].lower()
        resume_skills = set(parsed["skills"]["found"])

        # JD keywords that appear in skills DB or are multi-char
        from utils.nlp_processor import SKILL_DATABASE
        jd_skills = {w for w in jd_words if w in SKILL_DATABASE}

        matched   = [s for s in jd_skills if s in resume_skills]
        missing   = [s for s in jd_skills if s not in resume_skills]

        # Also do plain keyword overlap
        jd_keywords = {w for w in jd_words if len(w) > 4}
        resume_words = set(re.findall(r'\b[a-z][a-z+#.]{4,}\b', resume_text_lower))
        kw_matched  = list(jd_keywords & resume_words)[:15]
        kw_missing  = list(jd_keywords - resume_words)[:15]

        total = len(jd_skills) if jd_skills else 1
        match_score = int((len(matched) / total) * 100) if total > 0 else 50

        return {
            "match_score":    match_score,
            "matched_skills": matched,
            "missing_skills": missing[:12],
            "matched_keywords": kw_matched,
            "missing_keywords": kw_missing[:12],
            "jd_word_count":  len(jd_words),
        }

    def _verdict(self, score: int) -> str:
        if score >= 80:
            return "Excellent – Strong ATS match. Your resume is well-optimized."
        elif score >= 65:
            return "Good – Solid resume with minor improvements recommended."
        elif score >= 45:
            return "Fair – Several areas need improvement for better ATS performance."
        else:
            return "Needs Work – Significant improvements required for ATS compatibility."
