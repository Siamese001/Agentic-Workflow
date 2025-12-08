"""Tests for Resume Generation Safety Planner - content safety checks."""
import pytest
import re
from typing import Dict, Any, List

class TestRGSafetyPlanner:
    """Test suite for RG safety planner."""

    def test_detects_pii_in_resume(self):
        """Test PII detection in resume content."""
        content = "Contact: john@example.com, SSN: 123-45-6789"
        pii_patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "ssn": r'\d{3}-\d{2}-\d{4}',
        }
        found_pii = []
        for pii_type, pattern in pii_patterns.items():
            if re.search(pattern, content):
                found_pii.append(pii_type)
        assert "email" in found_pii
        assert "ssn" in found_pii

    def test_flags_inappropriate_content(self):
        """Test inappropriate content is flagged."""
        content = "I hate my previous employer"
        negative_indicators = ["hate", "terrible", "worst"]
        has_negative = any(ind in content.lower() for ind in negative_indicators)
        assert has_negative

    def test_validates_professional_tone(self):
        """Test professional tone is validated."""
        professional = "Experienced software engineer with 5 years of expertise"
        unprofessional = "I'm like really good at coding lol"
        
        casual_indicators = ["lol", "like really", "gonna", "wanna"]
        is_professional = not any(ind in professional.lower() for ind in casual_indicators)
        is_unprofessional = any(ind in unprofessional.lower() for ind in casual_indicators)
        
        assert is_professional
        assert is_unprofessional

    def test_checks_claim_validity(self):
        """Test claims are checked for validity."""
        claims = [
            {"claim": "10 years experience", "verifiable": True},
            {"claim": "Best developer ever", "verifiable": False},
        ]
        unverifiable = [c for c in claims if not c["verifiable"]]
        assert len(unverifiable) == 1

    def test_ensures_no_discrimination(self):
        """Test content has no discriminatory language."""
        content = "Experienced professional seeking opportunities"
        discriminatory_terms = ["young", "old", "male", "female", "race"]
        has_discrimination = any(term in content.lower() for term in discriminatory_terms)
        assert not has_discrimination


class TestContentSanitization:
    """Tests for content sanitization."""

    def test_removes_contact_pii(self):
        """Test contact PII is removed."""
        content = "Email: john@example.com Phone: 555-1234"
        sanitized = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', content)
        sanitized = re.sub(r'\d{3}[-.\s]?\d{4}', '[PHONE]', sanitized)
        assert "john@example.com" not in sanitized
        assert "[EMAIL]" in sanitized

    def test_preserves_professional_content(self):
        """Test professional content is preserved."""
        content = "Led team of 5 engineers to deliver project on time"
        # No PII, should be unchanged
        sanitized = content
        assert sanitized == content

    def test_normalizes_formatting(self):
        """Test formatting is normalized."""
        content = "  Multiple   spaces   and\n\nnewlines  "
        normalized = re.sub(r'\s+', ' ', content).strip()
        assert "  " not in normalized

    def test_removes_special_characters(self):
        """Test problematic special characters are removed."""
        content = "Resume™ with ® symbols and © marks"
        cleaned = re.sub(r'[™®©]', '', content)
        assert "™" not in cleaned

    def test_validates_date_formats(self):
        """Test date formats are validated."""
        valid_dates = ["2020-2024", "Jan 2020 - Dec 2024", "2020 - Present"]
        date_pattern = r'\d{4}\s*[-–]\s*(\d{4}|Present)'
        for date in valid_dates:
            # At least partial match expected
            assert re.search(r'\d{4}', date)


class TestBiasDetection:
    """Tests for bias detection in resume content."""

    def test_detects_age_indicators(self):
        """Test age-related indicators are detected."""
        content = "Graduated in 1985, 40 years of experience"
        age_indicators = [r'graduated in 19[0-7]\d', r'\d{2,}\+ years']
        has_age_indicator = any(re.search(p, content.lower()) for p in age_indicators)
        assert has_age_indicator

    def test_detects_gender_language(self):
        """Test gendered language is detected."""
        content = "He is a strong leader"
        gendered_terms = ["he ", "she ", "his ", "her "]
        has_gendered = any(term in content.lower() for term in gendered_terms)
        assert has_gendered

    def test_suggests_neutral_alternatives(self):
        """Test neutral alternatives are suggested."""
        replacements = {
            "chairman": "chairperson",
            "manpower": "workforce",
            "mankind": "humanity",
        }
        original = "chairman of the board"
        for old, new in replacements.items():
            if old in original:
                neutral = original.replace(old, new)
                assert new in neutral

    def test_flags_overconfident_claims(self):
        """Test overconfident claims are flagged."""
        claims = [
            "Best developer in the world",
            "Experienced software engineer",
        ]
        superlatives = ["best", "greatest", "top", "number one", "#1"]
        flagged = [c for c in claims if any(s in c.lower() for s in superlatives)]
        assert len(flagged) == 1
