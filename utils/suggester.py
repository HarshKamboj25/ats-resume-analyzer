"""
utils/suggester.py
==================
Generates prioritized resume improvement suggestions
based on parsed data and ATS score breakdown.

Each suggestion has:
  - priority : "high" | "medium" | "low"
  - category : area of improvement
  - title    : short action title
  - detail   : explanation
"""


IDEAL_SECTIONS = {"Summary", "Experience", "Education", "Skills", "Projects", "Certifications"}


class ResumeSuggester:
    """Generates actionable, prioritized resume improvement suggestions."""

    def generate_suggestions(self, parsed: dict, score_data: dict) -> list:
        suggestions = []
        breakdown = score_data.get("breakdown", {})
        sections  = set(parsed.get("sections_detected", []))
        skills    = parsed.get("skills", {})
        job_match = score_data.get("job_match", {})

        # ---- Contact Info ----
        if not parsed.get("email"):
            suggestions.append({
                "priority": "high",
                "category": "Contact",
                "title":    "Add your email address",
                "detail":   "ATS systems require an email address. Add it clearly at the top of your resume.",
            })
        if not parsed.get("phone"):
            suggestions.append({
                "priority": "high",
                "category": "Contact",
                "title":    "Add a phone number",
                "detail":   "A phone number is essential for recruiters to reach you.",
            })
        if not parsed.get("linkedin"):
            suggestions.append({
                "priority": "medium",
                "category": "Contact",
                "title":    "Add your LinkedIn URL",
                "detail":   "Including a LinkedIn profile URL improves credibility and ATS compatibility.",
            })

        # ---- Missing Sections ----
        missing_sections = IDEAL_SECTIONS - sections
        for sec in missing_sections:
            priority = "high" if sec in {"Experience", "Education", "Skills"} else "medium"
            suggestions.append({
                "priority": priority,
                "category": "Structure",
                "title":    f"Add a '{sec}' section",
                "detail":   f"Your resume is missing a dedicated {sec} section. ATS systems scan for clearly labeled sections.",
            })

        # ---- Skills ----
        if skills.get("count", 0) < 8:
            suggestions.append({
                "priority": "high",
                "category": "Skills",
                "title":    "Add more technical skills",
                "detail":   f"Only {skills.get('count', 0)} skills were detected. Aim for at least 12–15 relevant skills. Consider adding: {', '.join(skills.get('missing', [])[:5])}.",
            })
        elif skills.get("count", 0) < 15:
            suggestions.append({
                "priority": "medium",
                "category": "Skills",
                "title":    "Expand your skills section",
                "detail":   f"You have {skills.get('count', 0)} skills listed. Adding more relevant skills can improve your ATS score.",
            })

        # ---- Readability ----
        if parsed.get("readability") == "Complex":
            suggestions.append({
                "priority": "medium",
                "category": "Readability",
                "title":    "Simplify sentence structure",
                "detail":   "Your sentences are too long on average. Use bullet points and concise phrases (under 15 words per bullet).",
            })

        # ---- Word Count ----
        wc = parsed.get("word_count", 0)
        if wc < 300:
            suggestions.append({
                "priority": "high",
                "category": "Content",
                "title":    "Expand your resume content",
                "detail":   f"Your resume has only ~{wc} words. A strong resume typically has 400–700 words. Add project descriptions and achievements.",
            })
        elif wc > 900:
            suggestions.append({
                "priority": "low",
                "category": "Content",
                "title":    "Consider condensing your resume",
                "detail":   f"Your resume has ~{wc} words. Aim to keep it under 700 words (1–2 pages). Remove outdated or irrelevant content.",
            })

        # ---- Certifications ----
        if not parsed.get("certifications"):
            suggestions.append({
                "priority": "low",
                "category": "Certifications",
                "title":    "Add industry certifications",
                "detail":   "Certifications (AWS, Google, PMP, etc.) significantly improve ATS scores and recruiter confidence.",
            })

        # ---- Job Description Match ----
        if job_match:
            missing_jd_skills = job_match.get("missing_skills", [])
            if missing_jd_skills:
                suggestions.append({
                    "priority": "high",
                    "category": "Job Match",
                    "title":    "Add job-specific missing skills",
                    "detail":   f"The job description requires: {', '.join(missing_jd_skills[:6])}. Add these if you have experience with them.",
                })
            missing_kw = job_match.get("missing_keywords", [])
            if missing_kw:
                suggestions.append({
                    "priority": "medium",
                    "category": "Job Match",
                    "title":    "Mirror keywords from the job description",
                    "detail":   f"Use exact keywords from the JD in your resume: {', '.join(missing_kw[:6])}.",
                })

        # ---- Achievements ----
        raw = parsed.get("raw_text", "")
        has_numbers = any(char.isdigit() for char in raw)
        if not has_numbers:
            suggestions.append({
                "priority": "high",
                "category": "Impact",
                "title":    "Add measurable achievements",
                "detail":   "Use numbers and metrics to quantify your impact: 'Improved performance by 40%', 'Led a team of 8 engineers', etc.",
            })

        # Sort: high → medium → low
        order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: order[x["priority"]])

        return suggestions
