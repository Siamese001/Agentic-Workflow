"""
MANDATORY Test Suite: HOP 3-5 Foundation & Generation Hardening
100% Pass Requirement for Windsurf Execution.

Focus Areas:
- HOP-3: Whitelist Purity Extraction
- HOP-4: Gate 6 Premium Mismatch Detection
- HOP-5: K.5A Provenance Distribution (3V-3T-1S)
- HOP-5: K.7 Signature Immutability & Checksum
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from apps_lic.shared.core.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.core.trace_registry import TraceRegistry

from apps_lic.engines.HOP3SenderGroundingAgent import HOP3SenderGroundingAgent
from apps_lic.engines.HOP4RoutingAgent import HOP4RoutingAgent
from apps_lic.engines.HOP5GenerationAgent import HOP5GenerationAgent


class TestFoundationAndCrucible:
    """
    Sovereign Foundation Test Suite (HOP 3-5).
    MANDATORY: 100% PASS REQUIREMENT.
    """

    def test_hop3_whitelist_purity_extraction(self):
        """Verify HOP-3: Only whitelisted entities are extracted from grounding files."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        agent = HOP3SenderGroundingAgent()

        # Simulate data with non-whitelisted keys
        mock_data = {"products": ["AI Engine"], "forbidden_notes": "Internal only"}
        grounding_map = {"products": [], "team_members": [], "achievements": [], "case_studies": []}

        agent._extract_grounded_entities(mock_data, grounding_map, registry)

        # Verify 100% Pass: Non-whitelisted keys must not exist in extraction map
        assert "AI Engine" in grounding_map["products"], "Whitelisted product should be extracted"
        assert "forbidden_notes" not in grounding_map, "Non-whitelisted key should not appear"

    def test_hop3_metric_mapping_categorization(self):
        """Verify HOP-3: Achievements are correctly categorized by metric type."""
        agent = HOP3SenderGroundingAgent()

        achievements = [
            "Increased revenue by $5M",
            "Reduced costs by 30%",
            "Expanded market share by 15%",
            "Launched new product line",
        ]

        metric_map = agent._map_metrics(achievements)

        # Verify: Correct categorization
        assert len(metric_map["revenue"]) >= 1, "Revenue achievement should be categorized"
        assert len(metric_map["efficiency"]) >= 1, "Efficiency achievement should be categorized"
        assert len(metric_map["growth"]) >= 1, "Growth achievement should be categorized"

    def test_hop4_gate_6_premium_block(self):
        """Verify HOP-4: Gate 6 must raise ValueError if INMAIL is override target but premium is false."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "EXECUTIVE"})
        buffer.write_once(
            "mission_input",
            {
                "route_override": "INMAIL",
                "premium_available": False,  # CONFLICT
            },
        )

        agent = HOP4RoutingAgent()
        # Verify 100% Pass: System must terminal halt to prevent token drain
        # LICAgentBase wraps ValueError as RuntimeError with agent name
        with pytest.raises(RuntimeError, match="HOP4RoutingAgent execution failed"):
            agent.run_phase(buffer, registry)

        # Verify the underlying error was about Gate 6
        traces = registry.get_traces()
        gate6_trace = next((t for t in traces if t.get("type") == "GATE_6_FAILED"), None)
        assert gate6_trace is not None, "Should have GATE_6_FAILED trace"

    def test_hop4_gate_6_premium_pass(self):
        """Verify HOP-4: Gate 6 passes when INMAIL route has premium available."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "EXECUTIVE"})
        buffer.write_once(
            "mission_input",
            {
                "route_override": "INMAIL",
                "premium_available": True,  # VALID
            },
        )

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        # Verify: Route should be INMAIL and premium validated
        assert result["route"] == "INMAIL", "Route should be INMAIL"
        assert result["metadata"]["premium_validated"] == True, "Premium should be validated"

    def test_hop4_route_selection_priority(self):
        """Verify HOP-4: Route selection follows override > connected > premium priority."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER"})

        # Test 1: Override takes priority
        buffer.write_once(
            "mission_input",
            {
                "route_override": "FOLLOW_UP",
                "connection_status": "NOT_CONNECTED",
                "premium_available": True,
            },
        )

        agent = HOP4RoutingAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop4_routing")
        assert result["route"] == "FOLLOW_UP", "Override should take priority"

    def test_hop5_provenance_distribution_3v3t1s(self):
        """Verify HOP-5: K.5A must generate exactly 7 bullets following 3V-3T-1S rule."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Seed dependencies
        hop3_data = {
            "sender_grounding": {
                "products": ["Product A", "Product B", "Product C"],
                "capabilities": ["Cap 1", "Cap 2"],
            }
        }
        hop2_data = {
            "strategic_signals": ["AI Strategy", "Cloud Migration", "Digital Transformation"]
        }

        agent = HOP5GenerationAgent()
        # Test helper method directly for distribution accuracy
        result = agent._run_k5a_bullet_generation(hop3_data, hop2_data, registry)

        # Verify 100% Pass: Count must match the LIC v2.5 standard
        assert len(result["bullets"]) == 7, "Must generate exactly 7 bullets"
        assert result["labels"].count("V") == 3, "Must have 3 Verbatim bullets"
        assert result["labels"].count("T") == 3, "Must have 3 Transformed bullets"
        assert result["labels"].count("S") == 1, "Must have 1 Synthetic bullet"

    def test_hop5_k7_signature_immutability(self):
        """Verify HOP-5: Signature must be the final 4 lines of the code fence."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        agent = HOP5GenerationAgent()

        res = agent._assemble_k7_final_message("Body", ["B1"], "CTA", {}, registry)
        lines = res["full_text"].strip().split("\n")

        # Verify 100% Pass: 4-line signature + closing fence
        assert lines[0] == "```", "Should start with opening fence"
        assert lines[-5] == "Regards,", "Line -5 should be 'Regards,'"
        assert lines[-2] == "linkedin.com/in/[profile]", "Line -2 should be LinkedIn URL"
        assert lines[-1] == "```", "Should end with closing fence"

    def test_hop5_k7_checksum_generation(self):
        """Verify HOP-5: K.7 assembly returns SHA256 checksum for integrity."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        agent = HOP5GenerationAgent()

        res = agent._assemble_k7_final_message("Test Body", ["• Bullet 1"], "CTA", {}, registry)

        # Verify: Checksum exists and is valid SHA256
        assert "checksum" in res, "Must include checksum"
        assert len(res["checksum"]) == 64, "SHA256 checksum must be 64 chars"
        assert res["checksum"].isalnum(), "Checksum must be alphanumeric"

    def test_hop5_k7_fenced_block_format(self):
        """Verify HOP-5: K.7 assembly wraps message in code fence."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        agent = HOP5GenerationAgent()

        res = agent._assemble_k7_final_message("Body text", ["• Item"], "CTA", {}, registry)

        # Verify: Fenced block format
        assert res["full_text"].startswith("```\n"), "Must start with opening fence"
        assert res["full_text"].endswith("\n```"), "Must end with closing fence"
        assert "Body text" in res["full_text"], "Must contain body"
        assert "• Item" in res["full_text"], "Must contain bullets"

    def test_hop5_k3_archetype_transition_phrases(self):
        """Verify HOP-5: K.3 uses archetype-specific transition phrases."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()

        # Test C_LEVEL transition
        hop1_c = {"Archetype": "C_LEVEL", "recipient_company": "TechCorp"}
        hop2 = {"strategic_signals": ["AI Innovation"]}

        result_c = agent._run_k3_body_generation(hop1_c, hop2, registry)

        # Verify: C_LEVEL gets specific transition phrase
        assert "Two strategic insights" in result_c["transition_phrase"], (
            "C_LEVEL should use strategic insights phrase"
        )
        assert "TechCorp" in result_c["transition_phrase"], "Should include company name"

    def test_hop5_k5_cta_word_limit_compliance(self):
        """Verify HOP-5: K.5 CTA respects word count constraints by route."""
        agent = HOP5GenerationAgent()
        registry = TraceRegistry()

        # Test CONNECTION_REQ (5 word limit)
        hop4_conn = {"route": "CONNECTION_REQ"}
        result_conn = agent._run_k5_cta_generation(hop4_conn, registry)

        word_count_conn = len(result_conn["text"].split())
        assert word_count_conn <= 5, "CONNECTION_REQ CTA must be <= 5 words"

        # Test INMAIL (10 word limit)
        hop4_inmail = {"route": "INMAIL"}
        result_inmail = agent._run_k5_cta_generation(hop4_inmail, registry)

        word_count_inmail = len(result_inmail["text"].split())
        assert word_count_inmail <= 10, "INMAIL CTA must be <= 10 words"

    def test_hop5_candidate_generation_integration(self):
        """Verify HOP-5: Full candidate generation includes checksum in output."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        # Seed all dependencies
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER", "recipient_company": "TestCo"})
        buffer.write_once("hop2_research", {"strategic_signals": ["Growth"]})
        buffer.write_once(
            "hop3_sender_grounding",
            {"sender_grounding": {"products": ["P1", "P2", "P3"], "capabilities": []}},
        )
        buffer.write_once("hop4_routing", {"route": "INMAIL", "constraints": {"char_limit": 2000}})

        agent = HOP5GenerationAgent()
        agent.run_phase(buffer, registry)

        result = buffer.read("hop5_generation")

        # Verify: Selected draft has checksum
        assert "selected_draft" in result, "Must have selected draft"
        assert "checksum" in result["selected_draft"], "Selected draft must include checksum"
        assert len(result["selected_draft"]["checksum"]) == 64, "Checksum must be SHA256"

    def test_hop3_empty_source_files_validation(self):
        """Verify HOP-3: Raises error if source_files config is empty."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        # Mock config with empty source files
        agent = HOP3SenderGroundingAgent()
        agent.config.sender_grounding_agent.source_files = []

        # Verify: Should raise RuntimeError (LICAgentBase wraps with agent name)
        with pytest.raises(RuntimeError, match="HOP3SenderGroundingAgent execution failed"):
            agent.run_phase(buffer, registry)

    def test_hop4_missing_mission_input_halt(self):
        """Verify HOP-4: Raises RuntimeError if mission_input is missing."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()
        # Don't write mission_input

        agent = HOP4RoutingAgent()

        # Verify: Should halt on missing input (LICAgentBase wraps with agent name)
        with pytest.raises(RuntimeError, match="HOP4RoutingAgent execution failed"):
            agent.run_phase(buffer, registry)

    def test_hop5_missing_upstream_inputs_halt(self):
        """Verify HOP-5: Raises RuntimeError if any upstream HOP output is missing."""
        buffer, registry = ImmutableStagingBuffer(), TraceRegistry()

        # Only provide partial inputs
        buffer.write_once("hop1_analysis", {"Archetype": "MANAGER"})
        # Missing hop2, hop3, hop4

        agent = HOP5GenerationAgent()

        # Verify: Should halt on missing upstream state (LICAgentBase wraps with agent name)
        with pytest.raises(RuntimeError, match="HOP5GenerationAgent execution failed"):
            agent.run_phase(buffer, registry)


def run_tests():
    """Execute test suite with detailed reporting."""
    print("=" * 80)
    print("HOP 3-5 FOUNDATION & GENERATION TEST SUITE")
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
        print("HOP 3-5 Foundation is ready for deployment")
    else:
        print("❌ TEST FAILURES DETECTED")
        print("DO NOT DEPLOY until all tests pass")
    print("=" * 80)

    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
