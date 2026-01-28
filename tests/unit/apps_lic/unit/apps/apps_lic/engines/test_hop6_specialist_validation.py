"""
HOP-6 Specialist Validation Test Suite.

Tests for Phase 16: LIC-E001, LIC-E015, LIC-E008 Rule Enforcement.
Requirement: 100% Pass Rate for Validation Gate.
"""

from apps_lic.engines.HOP6ValidationAgent import HOP6ValidationAgent
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry


class TestHOP6SpecialistValidation:
    """
    Mandatory Test Suite for Phase 16.
    Requirement: 100% Pass Language Included.
    """

    def test_placeholder_critical_failure(self):
        """Verify LIC-E001: Any [bracketed] content must fail validation."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "AI Strategy"})
        buffer.write_once(
            "hop5_generation",
            {"selected_draft": {"text": "Hi [Name], I noticed your work on [Company]."}},
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        assert report["passed"] is False, "Draft with placeholders should fail"
        assert any(r["rule_id"] == "LIC-E001" for r in report["validation_results"])

        # Verify the specific rule failed
        lic_e001 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E001")
        assert lic_e001["passed"] is False
        assert lic_e001["severity"] == "CRITICAL"

    def test_placeholder_curly_braces(self):
        """Verify LIC-E001: {curly} placeholders also fail validation."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Cloud Strategy"})
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "Hello {FirstName}, your work at {CompanyName} is impressive."
                }
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        assert report["passed"] is False

        lic_e001 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E001")
        assert lic_e001["passed"] is False

    def test_placeholder_angle_brackets(self):
        """Verify LIC-E001: <angle> placeholders also fail validation."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Innovation"})
        buffer.write_once(
            "hop5_generation", {"selected_draft": {"text": "Dear <Recipient>, I noticed <Topic>."}}
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        assert report["passed"] is False

    def test_strategic_alignment_factual_check(self):
        """Verify LIC-E015: Lack of keyword overlap triggers a failing report."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once(
            "hop2_research", {"strategic_brief": "Regulated industries compliance security"}
        )
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {"text": "We sell coffee machines to startups."}  # No overlap
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # This failure should eventually be classified as FACTUAL_FAILURE by HOP-7
        assert report["passed"] is False

        lic_e015 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E015")
        assert lic_e015["passed"] is False
        assert lic_e015["severity"] == "CRITICAL"

    def test_strategic_alignment_pass(self):
        """Verify LIC-E015: Draft with keyword overlap passes."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once(
            "hop2_research", {"strategic_brief": "Cloud migration strategy enterprise"}
        )
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "I see your focus on cloud migration strategy for enterprise clients."
                }
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")

        lic_e015 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E015")
        assert lic_e015["passed"] is True

    def test_clean_draft_pass(self):
        """Verify a compliant draft passes all specialist gates."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Cloud migration strategy"})
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "I see your focus on cloud migration strategy for enterprise."
                }
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        assert report["passed"] is True
        assert report["stats"]["critical"] == 0

    def test_forbidden_verbs_medium_severity(self):
        """Verify LIC-E008: Forbidden verbs trigger medium severity warning."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Digital transformation"})
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "We will revolutionize your digital transformation and disrupt the market."
                }
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")

        # Medium severity should not fail the draft (only CRITICAL and HIGH fail)
        # But the rule should be marked as failed
        lic_e008 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E008")
        assert lic_e008["passed"] is False
        assert lic_e008["severity"] == "MEDIUM"

        # Draft should still pass because MEDIUM doesn't block
        assert report["passed"] is True

    def test_forbidden_verbs_detection(self):
        """Verify LIC-E008: All forbidden verbs are detected."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Business strategy"})
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "Let's leverage our synergies to optimize and transform your business."
                }
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")

        lic_e008 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E008")
        assert lic_e008["passed"] is False
        assert "leverage" in lic_e008["message"].lower()

    def test_no_strategic_brief_skips_alignment(self):
        """Verify LIC-E015: Missing strategic brief skips alignment check."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {})  # No strategic_brief
        buffer.write_once(
            "hop5_generation", {"selected_draft": {"text": "Generic outreach message."}}
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")

        lic_e015 = next(r for r in report["validation_results"] if r["rule_id"] == "LIC-E015")
        assert lic_e015["passed"] is True
        assert "skipping" in lic_e015["message"].lower()

    def test_validation_stats_accuracy(self):
        """Verify validation stats are calculated correctly."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Innovation"})
        buffer.write_once(
            "hop5_generation",
            {"selected_draft": {"text": "Hi [Name], let's revolutionize innovation."}},
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")

        # Should have 2 critical failures: placeholder + no strategic alignment
        assert report["stats"]["critical"] == 2
        assert report["stats"]["total_checked"] == 3
        assert report["passed"] is False

    def test_trace_logging_validation_flow(self):
        """Verify trace registry logs validation flow correctly."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Strategy"})
        buffer.write_once(
            "hop5_generation", {"selected_draft": {"text": "Clean draft about strategy."}}
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        traces = [t["type"] for t in registry.get_traces()]

        assert "PHASE_START" in traces
        assert "PHASE_STEP" in traces
        assert "DECISION_FINAL" in traces

    def test_multiple_critical_failures(self):
        """Verify multiple critical failures are all reported."""
        buffer = ImmutableStagingBuffer()
        registry = TraceRegistry()

        buffer.write_once("hop2_research", {"strategic_brief": "Compliance security"})
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "Hi [Name], we sell coffee."
                }  # Placeholder + no alignment
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")

        # Both LIC-E001 and LIC-E015 should fail
        failed_rules = [r["rule_id"] for r in report["validation_results"] if not r["passed"]]
        assert "LIC-E001" in failed_rules
        assert "LIC-E015" in failed_rules
        assert report["stats"]["critical"] == 2
