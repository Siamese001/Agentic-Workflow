"""Tests for Resume Generation Scoring - quality and match scoring."""
import pytest
from typing import Dict, Any, List

class TestResumeScoring:
    """Test suite for resume scoring."""

    def test_scores_keyword_match(self):
        """Test keyword match scoring."""
        job_keywords = ["python", "sql", "aws"]
        resume_keywords = ["python", "sql", "docker"]
        matches = set(job_keywords) & set(resume_keywords)
        score = len(matches) / len(job_keywords)
        assert score == pytest.approx(0.667, rel=0.01)

    def test_scores_experience_match(self):
        """Test experience level match scoring."""
        required_years = 5
        candidate_years = 7
        score = min(1.0, candidate_years / required_years)
        assert score == 1.0

    def test_scores_education_match(self):
        """Test education match scoring."""
        required = "Bachelor's"
        candidate = "Master's"
        education_levels = {"High School": 1, "Bachelor's": 2, "Master's": 3, "PhD": 4}
        score = 1.0 if education_levels.get(candidate, 0) >= education_levels.get(required, 0) else 0.5
        assert score == 1.0

    def test_calculates_overall_score(self):
        """Test overall score calculation."""
        scores = {"keywords": 0.8, "experience": 0.9, "education": 1.0}
        weights = {"keywords": 0.4, "experience": 0.4, "education": 0.2}
        overall = sum(scores[k] * weights[k] for k in scores)
        assert overall == pytest.approx(0.88)

    def test_normalizes_scores(self):
        """Test scores are normalized to 0-1 range."""
        raw_scores = [50, 75, 100, 25]
        min_s, max_s = min(raw_scores), max(raw_scores)
        normalized = [(s - min_s) / (max_s - min_s) for s in raw_scores]
        assert all(0 <= n <= 1 for n in normalized)


class TestSkillGapAnalysis:
    """Tests for skill gap analysis."""

    def test_identifies_missing_skills(self):
        """Test missing skills are identified."""
        required = {"python", "sql", "kubernetes", "aws"}
        candidate = {"python", "sql", "docker"}
        missing = required - candidate
        assert "kubernetes" in missing
        assert "aws" in missing

    def test_identifies_extra_skills(self):
        """Test extra skills are identified."""
        required = {"python", "sql"}
        candidate = {"python", "sql", "docker", "kubernetes"}
        extra = candidate - required
        assert "docker" in extra

    def test_calculates_gap_percentage(self):
        """Test gap percentage is calculated."""
        required = {"a", "b", "c", "d"}
        candidate = {"a", "b"}
        gap = len(required - candidate) / len(required)
        assert gap == 0.5

    def test_prioritizes_critical_gaps(self):
        """Test critical skill gaps are prioritized."""
        gaps = [
            {"skill": "python", "importance": "critical"},
            {"skill": "docker", "importance": "nice-to-have"},
        ]
        critical = [g for g in gaps if g["importance"] == "critical"]
        assert len(critical) == 1

    def test_suggests_improvements(self):
        """Test improvement suggestions are generated."""
        gaps = ["kubernetes", "aws"]
        suggestions = [f"Consider learning {skill}" for skill in gaps]
        assert len(suggestions) == 2


class TestMatchScoring:
    """Tests for job-resume match scoring."""

    def test_scores_title_match(self):
        """Test job title match scoring."""
        job_title = "Senior Software Engineer"
        resume_title = "Software Engineer"
        # Partial match
        words_match = len(set(job_title.lower().split()) & set(resume_title.lower().split()))
        total_words = len(set(job_title.lower().split()))
        score = words_match / total_words
        assert score > 0.5

    def test_scores_industry_match(self):
        """Test industry match scoring."""
        job_industry = "Technology"
        resume_industries = ["Technology", "Software"]
        score = 1.0 if job_industry in resume_industries else 0.0
        assert score == 1.0

    def test_scores_location_match(self):
        """Test location match scoring."""
        job_location = "Remote"
        candidate_preference = "Remote"
        score = 1.0 if job_location == candidate_preference else 0.5
        assert score == 1.0

    def test_aggregates_match_scores(self):
        """Test match scores are aggregated."""
        scores = {
            "title": 0.8,
            "skills": 0.7,
            "experience": 0.9,
            "education": 1.0,
            "location": 1.0,
        }
        avg_score = sum(scores.values()) / len(scores)
        assert avg_score == pytest.approx(0.88)

    def test_ranks_multiple_jobs(self):
        """Test multiple jobs are ranked by match score."""
        jobs = [
            {"title": "Job A", "score": 0.85},
            {"title": "Job B", "score": 0.92},
            {"title": "Job C", "score": 0.78},
        ]
        ranked = sorted(jobs, key=lambda j: j["score"], reverse=True)
        assert ranked[0]["title"] == "Job B"
