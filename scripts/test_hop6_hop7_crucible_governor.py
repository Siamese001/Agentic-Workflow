"""
MANDATORY Test Suite: HOP 6-7 Crucible & Governor
100% Pass Requirement for Windsurf Execution.

Focus Areas:
- HOP-6: Specialist Rule Enforcement (LIC-E001, LIC-E015, LIC-E008)
- HOP-6: Externalized Rule configuration
- HOP-7: Governor Classification (Factual vs Creative)
- HOP-7: Stagnation Detection
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from apps_lic.engines.HOP6ValidationAgent import HOP6ValidationAgent
from apps_lic.engines.HOP7GateDecisionAgent import HOP7GateDecisionAgent
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry


class TestValidationCrucible:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Focus: Specialist Rule Enforcement, Governor Classification, Stagnation Safety.
    """

    def test_hop6_placeholder_critical_failure(self):
        """Verify LIC-E001: Any [bracketed] text must trigger a CRITICAL failure."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"strategic_brief": "Cloud systems"})
        buffer.write_once(
            "hop5_generation", {"selected_draft": {"text": "Hello [Name], I noticed your work."}}
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify 100% Pass: Placeholder detected, passed is False
        assert report["passed"] is False, "Report should fail with placeholders"
        assert any(
            r["rule_id"] == "LIC-E001" and not r["passed"] for r in report["validation_results"]
        ), "LIC-E001 should fail"

    def test_hop6_placeholder_pass_clean_text(self):
        """Verify LIC-E001: Clean text without placeholders passes."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"strategic_brief": "Cloud systems"})
        buffer.write_once(
            "hop5_generation",
            {"selected_draft": {"text": "Hello John, I noticed your work on cloud systems."}},
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify: LIC-E001 should pass
        lic_e001 = next(
            (r for r in report["validation_results"] if r["rule_id"] == "LIC-E001"), None
        )
        assert lic_e001 is not None, "LIC-E001 should be checked"
        assert lic_e001["passed"] is True, "LIC-E001 should pass with clean text"

    def test_hop6_strategic_alignment_failure(self):
        """Verify LIC-E015: Draft without strategic keywords fails."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "hop2_research", {"strategic_brief": "Cloud migration digital transformation"}
        )
        buffer.write_once("hop5_generation", {"selected_draft": {"text": "Hello, I sell widgets."}})

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify: LIC-E015 should fail (no keyword overlap)
        lic_e015 = next(
            (r for r in report["validation_results"] if r["rule_id"] == "LIC-E015"), None
        )
        assert lic_e015 is not None, "LIC-E015 should be checked"
        assert lic_e015["passed"] is False, "LIC-E015 should fail without keyword overlap"

    def test_hop6_strategic_alignment_pass(self):
        """Verify LIC-E015: Draft with strategic keywords passes."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "hop2_research", {"strategic_brief": "Cloud migration digital transformation"}
        )
        buffer.write_once(
            "hop5_generation",
            {
                "selected_draft": {
                    "text": "Your cloud migration initiatives align with our expertise."
                }
            },
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify: LIC-E015 should pass (keyword "cloud" matches)
        lic_e015 = next(
            (r for r in report["validation_results"] if r["rule_id"] == "LIC-E015"), None
        )
        assert lic_e015 is not None, "LIC-E015 should be checked"
        assert lic_e015["passed"] is True, "LIC-E015 should pass with keyword overlap"

    def test_hop6_forbidden_verbs_detection(self):
        """Verify LIC-E008: Forbidden verbs are detected."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"strategic_brief": "AI systems"})
        buffer.write_once(
            "hop5_generation", {"selected_draft": {"text": "We will revolutionize your business."}}
        )

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify: LIC-E008 should fail (contains "revolutionize")
        lic_e008 = next(
            (r for r in report["validation_results"] if r["rule_id"] == "LIC-E008"), None
        )
        assert lic_e008 is not None, "LIC-E008 should be checked"
        # Note: LIC-E008 is MEDIUM severity, doesn't block overall pass unless configured
        assert lic_e008["passed"] is False, "LIC-E008 should detect forbidden verb"

    def test_hop6_externalized_config_placeholder_regex(self):
        """Verify HOP-6: Uses externalized placeholder regex from config."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"strategic_brief": "Test"})
        buffer.write_once("hop5_generation", {"selected_draft": {"text": "Hello {Name}"}})

        agent = HOP6ValidationAgent()
        # Config should have default pattern that catches {Name}
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        lic_e001 = next(
            (r for r in report["validation_results"] if r["rule_id"] == "LIC-E001"), None
        )
        # Verify: Default pattern catches {Name}
        assert lic_e001["passed"] is False, "Should detect {Name} as placeholder"

    def test_hop7_factual_vs_creative_routing(self):
        """Verify HOP-7: Factual violations route to HOP-2, Creative to HOP-5."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Case: Factual failure (Strategic Alignment)
        buffer.write_once(
            "hop6_validation_report",
            {
                "passed": False,
                "validation_results": [
                    {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"}
                ],
            },
        )

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)

        decision = buffer.read("hop7_gate_decision")
        # Verify 100% Pass: LIC-E015 must trigger RETRY_HOP2
        assert decision["action"] == "RETRY_HOP2", "LIC-E015 should route to HOP-2"
        assert decision["decision"] == "FAIL_FACTUAL", "Should classify as factual failure"

        # Verify trace
        traces = registry.get_traces()
        assert any(t.get("type") == "FACTUAL_LOOP_TRIGGERED" for t in traces), (
            "Should log factual loop"
        )

    def test_hop7_creative_routing(self):
        """Verify HOP-7: Creative violations route to HOP-5."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Case: Creative failure (Placeholder)
        buffer.write_once(
            "hop6_validation_report",
            {
                "passed": False,
                "validation_results": [
                    {"rule_id": "LIC-E001", "passed": False, "severity": "CRITICAL"}
                ],
            },
        )

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)

        decision = buffer.read("hop7_gate_decision")
        # Verify: LIC-E001 should route to HOP-5 (creative)
        assert decision["action"] == "RETRY_HOP5", "LIC-E001 should route to HOP-5"
        assert decision["decision"] == "FAIL_CREATIVE", "Should classify as creative failure"

    def test_hop7_pass_decision(self):
        """Verify HOP-7: Clean validation report results in PASS."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once(
            "hop6_validation_report",
            {
                "passed": True,
                "validation_results": [
                    {"rule_id": "LIC-E001", "passed": True, "severity": "CRITICAL"},
                    {"rule_id": "LIC-E015", "passed": True, "severity": "CRITICAL"},
                ],
            },
        )

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)

        decision = buffer.read("hop7_gate_decision")
        # Verify: Should pass
        assert decision["decision"] == "PASS", "Should pass with clean report"
        assert decision["action"] == "PROCEED", "Should proceed"

    def test_hop7_stagnation_detection(self):
        """Verify HOP-7: Multiple factual retries are flagged for stagnation."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Seed traces with 2 prior factual loops
        registry.add_trace("FACTUAL_LOOP_TRIGGERED", {"rule": "LIC-E015"})
        registry.add_trace("FACTUAL_LOOP_TRIGGERED", {"rule": "LIC-E015"})

        buffer.write_once(
            "hop6_validation_report",
            {
                "passed": False,
                "validation_results": [
                    {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"}
                ],
            },
        )

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)

        # Verify 100% Pass: Stagnation trace must exist
        traces = registry.get_traces()
        stagnation_trace = next((t for t in traces if t.get("type") == "STAGNATION_DETECTED"), None)
        assert stagnation_trace is not None, "Should detect stagnation"
        assert stagnation_trace["details"]["count"] >= 2, "Should count factual retries"

    def test_hop6_missing_inputs_halt(self):
        """Verify HOP-6: Raises RuntimeError if HOP-5 or HOP-2 missing."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Don't write required inputs

        agent = HOP6ValidationAgent()

        # Verify: Should halt (LICAgentBase wraps with agent name)
        with pytest.raises(RuntimeError, match="HOP6ValidationAgent execution failed"):
            agent.run_phase(buffer, registry)

    def test_hop7_missing_report_halt(self):
        """Verify HOP-7: Raises RuntimeError if HOP-6 report missing."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Don't write hop6_validation_report

        agent = HOP7GateDecisionAgent()

        # Verify: Should halt (LICAgentBase wraps with agent name)
        with pytest.raises(RuntimeError, match="HOP7GateDecisionAgent execution failed"):
            agent.run_phase(buffer, registry)

    def test_hop6_all_rules_executed(self):
        """Verify HOP-6: All three rules are executed."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"strategic_brief": "Test"})
        buffer.write_once("hop5_generation", {"selected_draft": {"text": "Clean text"}})

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify: All 3 rules checked
        assert len(report["validation_results"]) == 3, "Should check all 3 rules"
        rule_ids = [r["rule_id"] for r in report["validation_results"]]
        assert "LIC-E001" in rule_ids, "Should check LIC-E001"
        assert "LIC-E015" in rule_ids, "Should check LIC-E015"
        assert "LIC-E008" in rule_ids, "Should check LIC-E008"

    def test_hop6_stats_tracking(self):
        """Verify HOP-6: Report includes stats for critical issues."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop2_research", {"strategic_brief": "Test"})
        buffer.write_once("hop5_generation", {"selected_draft": {"text": "[Name] placeholder"}})

        agent = HOP6ValidationAgent()
        agent.run_phase(buffer, registry)

        report = buffer.read("hop6_validation_report")
        # Verify: Stats present
        assert "stats" in report, "Should include stats"
        assert "critical" in report["stats"], "Should track critical issues"
        assert report["stats"]["critical"] >= 1, "Should count critical failure"

    def test_hop7_factual_priority_over_creative(self):
        """Verify HOP-7: Factual failures take priority over creative."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Both factual and creative failures
        buffer.write_once(
            "hop6_validation_report",
            {
                "passed": False,
                "validation_results": [
                    {"rule_id": "LIC-E001", "passed": False, "severity": "CRITICAL"},  # Creative
                    {"rule_id": "LIC-E015", "passed": False, "severity": "CRITICAL"},  # Factual
                ],
            },
        )

        agent = HOP7GateDecisionAgent()
        agent.run_phase(buffer, registry)

        decision = buffer.read("hop7_gate_decision")
        # Verify: Should prioritize factual
        assert decision["action"] == "RETRY_HOP2", "Should prioritize factual routing"
        assert decision["decision"] == "FAIL_FACTUAL", "Should classify as factual"


def run_tests():
    """Execute test suite with detailed reporting."""
    print("=" * 80)
    print("HOP 6-7 CRUCIBLE & GOVERNOR TEST SUITE")
    print("=" * 80)
    print()

    # Run pytest with verbose output
    exit_code = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--color=yes",
            "-W",
            "ignore::DeprecationWarning",
        ]
    )

    print()
    print("=" * 80)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED - 100% Pass Requirement Met")
        print("HOP 6-7 Crucible & Governor is ready for deployment")
    else:
        print("❌ TEST FAILURES DETECTED")
        print("DO NOT DEPLOY until all tests pass")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
