"""
Test RG Pydantic Types.
"""
import unittest

from pydantic import ValidationError

from apps_rg.types import (
    ExperienceEntry,
    ResumeConfig,
    ResumeRequest,
    ResumeResult,
    ResumeRunSummary,
    ResumeSection,
    SkillMatch,
)


class TestSkillMatch(unittest.TestCase):
    """Test cases for SkillMatch Pydantic model."""

    def test_skill_creation(self):
        """Test skill match creation."""
        skill = SkillMatch(
            skill_name="Python",
            match_score=0.95,
            evidence="5 years of experience",
        )
        self.assertEqual(skill.skill_name, "Python")
        self.assertEqual(skill.match_score, 0.95)

    def test_match_score_bounds(self):
        """Test match score bounds."""
        with self.assertRaises(ValidationError):
            SkillMatch(skill_name="Test", match_score=1.5)


class TestExperienceEntry(unittest.TestCase):
    """Test cases for ExperienceEntry Pydantic model."""

    def test_entry_creation(self):
        """Test entry creation."""
        entry = ExperienceEntry(
            company="Tech Corp",
            title="Senior Engineer",
            duration_months=36,
            achievements=["Led team of 5", "Shipped product"],
        )
        self.assertEqual(entry.company, "Tech Corp")
        self.assertEqual(entry.duration_months, 36)


class TestResumeSection(unittest.TestCase):
    """Test cases for ResumeSection Pydantic model."""

    def test_section_creation(self):
        """Test section creation."""
        section = ResumeSection(
            section_id="sec-001",
            section_type="summary",
            content="This is a professional summary that meets minimum requirements.",
            word_count=50,
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertEqual(section.word_count, 50)

    def test_content_validation(self):
        """Test content minimum length (20 chars)."""
        with self.assertRaises(ValidationError):
            ResumeSection(section_id="s1", section_type="summary", content="Too short")


class TestResumeConfig(unittest.TestCase):
    """Test cases for ResumeConfig Pydantic model."""

    def test_config_defaults(self):
        """Test config default values."""
        config = ResumeConfig()
        self.assertEqual(config.target_format, "standard")
        self.assertTrue(config.ats_optimization)
        self.assertEqual(config.max_length_words, 500)

    def test_max_length_bounds(self):
        """Test max length bounds."""
        with self.assertRaises(ValidationError):
            ResumeConfig(max_length_words=50)


class TestResumeRequest(unittest.TestCase):
    """Test cases for ResumeRequest Pydantic model."""

    def test_request_creation(self):
        """Test request creation."""
        request = ResumeRequest(
            candidate_name="Jane Smith",
            target_role="Senior Software Engineer",
            target_industry="tech",
            experience_level="senior",
        )
        self.assertEqual(request.candidate_name, "Jane Smith")
        self.assertEqual(request.target_role, "Senior Software Engineer")

    def test_name_validation(self):
        """Test name validation."""
        with self.assertRaises(ValidationError):
            ResumeRequest(candidate_name="", target_role="Engineer")

    def test_config_nested(self):
        """Test nested config."""
        request = ResumeRequest(
            candidate_name="Test",
            target_role="Role",
            config=ResumeConfig(max_length_words=700),
        )
        self.assertEqual(request.config.max_length_words, 700)


class TestResumeResult(unittest.TestCase):
    """Test cases for ResumeResult Pydantic model."""

    def test_result_creation(self):
        """Test result creation."""
        result = ResumeResult(
            trace_id="rg-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
        )
        self.assertEqual(result.trace_id, "rg-001")
        self.assertEqual(result.ats_score, 85.5)

    def test_passed_gate_property(self):
        """Test passed_gate property."""
        result_pass = ResumeResult(status="complete", gate_violations=[])
        self.assertTrue(result_pass.passed_gate)

        result_fail = ResumeResult(status="complete", gate_violations=["error"])
        self.assertFalse(result_fail.passed_gate)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            ResumeResult(quality_score=1.5)


class TestResumeRunSummary(unittest.TestCase):
    """Test cases for ResumeRunSummary Pydantic model."""

    def test_summary_creation(self):
        """Test summary creation."""
        summary = ResumeRunSummary(
            trace_id="trace-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
        )
        self.assertEqual(summary.trace_id, "trace-001")
        self.assertEqual(summary.app, "apps_rg")

    def test_to_dict(self):
        """Test to_dict method."""
        summary = ResumeRunSummary(trace_id="trace-001", quality_score=0.88)
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["quality_score"], 0.88)


if __name__ == "__main__":
    unittest.main()
