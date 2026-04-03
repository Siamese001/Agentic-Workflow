"""
Test Exec Pydantic Types.
"""
import unittest

from pydantic import ValidationError

from apps_exec.types import (
    BriefSection,
    CapabilityEvidence,
    ExecBriefConfig,
    ExecBriefRequest,
    ExecBriefResult,
    RunSummary,
    StyleViolation,
)


class TestCapabilityEvidence(unittest.TestCase):
    """Test cases for CapabilityEvidence Pydantic model."""

    def test_capability_creation(self):
        """Test capability creation."""
        cap = CapabilityEvidence(
            capability_id="cap-001",
            label="Auto-scaling",
            description="Platform automatically scales based on workload demand",
            layer="infrastructure",
            emphasis_area="orchestration",
        )
        self.assertEqual(cap.capability_id, "cap-001")
        self.assertEqual(cap.layer, "infrastructure")

    def test_description_validation(self):
        """Test description minimum length."""
        with self.assertRaises(ValidationError):
            CapabilityEvidence(
                capability_id="c1",
                label="Test",
                description="short",
            )


class TestBriefSection(unittest.TestCase):
    """Test cases for BriefSection Pydantic model."""

    def test_section_creation(self):
        """Test section creation."""
        section = BriefSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for the brief.",
            word_count=150,
            why_this_matters="Critical for board approval",
        )
        self.assertEqual(section.section_id, "sec-001")
        self.assertEqual(section.word_count, 150)

    def test_body_validation(self):
        """Test body minimum length (50 chars)."""
        with self.assertRaises(ValidationError):
            BriefSection(section_id="s1", heading="Test", body="Too short")


class TestExecBriefConfig(unittest.TestCase):
    """Test cases for ExecBriefConfig Pydantic model."""

    def test_config_defaults(self):
        """Test config default values."""
        config = ExecBriefConfig()
        self.assertEqual(config.min_quality_score, 0.7)
        self.assertEqual(config.max_sections, 8)
        self.assertTrue(config.enforce_tone_consistency)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            ExecBriefConfig(min_quality_score=1.5)

    def test_max_sections_bounds(self):
        """Test max sections bounds."""
        with self.assertRaises(ValidationError):
            ExecBriefConfig(max_sections=50)


class TestExecBriefRequest(unittest.TestCase):
    """Test cases for ExecBriefRequest Pydantic model."""

    def test_request_creation(self):
        """Test request creation."""
        request = ExecBriefRequest(
            audience="board",
            tone="board-ready",
            emphasis_areas=["governance", "safety"],
            industry="healthcare",
        )
        self.assertEqual(request.audience, "board")
        self.assertEqual(request.tone, "board-ready")
        self.assertEqual(request.emphasis_areas, ["governance", "safety"])

    def test_config_nested(self):
        """Test nested config."""
        request = ExecBriefRequest(
            audience="cto",
            config=ExecBriefConfig(min_quality_score=0.8),
        )
        self.assertEqual(request.config.min_quality_score, 0.8)


class TestExecBriefResult(unittest.TestCase):
    """Test cases for ExecBriefResult Pydantic model."""

    def test_result_creation(self):
        """Test result creation."""
        result = ExecBriefResult(
            trace_id="exec-001",
            audience="board",
            tone="board-ready",
            status="complete",
            quality_score=0.85,
        )
        self.assertEqual(result.trace_id, "exec-001")
        self.assertEqual(result.quality_score, 0.85)

    def test_passed_gate_property(self):
        """Test passed_gate property."""
        result_pass = ExecBriefResult(status="complete", gate_violations=[])
        self.assertTrue(result_pass.passed_gate)

        result_fail = ExecBriefResult(status="complete", gate_violations=["error"])
        self.assertFalse(result_fail.passed_gate)

    def test_quality_score_bounds(self):
        """Test quality score bounds."""
        with self.assertRaises(ValidationError):
            ExecBriefResult(quality_score=1.5)


class TestRunSummary(unittest.TestCase):
    """Test cases for RunSummary Pydantic model."""

    def test_summary_creation(self):
        """Test summary creation."""
        summary = RunSummary(
            trace_id="trace-001",
            audience="board",
            status="complete",
            sections_generated=6,
            quality_score=0.85,
        )
        self.assertEqual(summary.trace_id, "trace-001")
        self.assertEqual(summary.app, "apps_exec")

    def test_to_dict(self):
        """Test to_dict method."""
        summary = RunSummary(trace_id="trace-001", quality_score=0.85)
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["quality_score"], 0.85)


class TestStyleViolation(unittest.TestCase):
    """Test cases for StyleViolation Pydantic model."""

    def test_violation_creation(self):
        """Test violation creation."""
        violation = StyleViolation(
            rule_id="style-001",
            severity="high",
            message="Section lacks business impact statement",
            section_id="sec-002",
        )
        self.assertEqual(violation.rule_id, "style-001")
        self.assertEqual(violation.severity, "high")

    def test_message_validation(self):
        """Test message minimum length."""
        with self.assertRaises(ValidationError):
            StyleViolation(rule_id="r1", severity="low", message="x")


if __name__ == "__main__":
    unittest.main()
