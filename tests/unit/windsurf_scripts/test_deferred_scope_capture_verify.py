#!/usr/bin/env python3
"""Verification test for W3: Backlog Items writeback (post_agent_deferred_scope_capture.py).

Tests the three key capabilities:
1. Marker parsing (DEFERRED_SCOPE: ...)
2. P-band scoring via deferred_scope_scorer
3. Notion payload building (correct shape for Backlog Items DB)

These are integration-style tests that verify the hook components work
correctly without requiring actual Notion API calls.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / ".claude" / "governance/scripts" / "_legacy_windsurf"))

# Import the hook module components (not main() to avoid stdin issues)
from post_agent_deferred_scope_capture import (
    _parse_marker,
    _validate_marker,
    _build_notion_payload,
    MARKER_RE,
    REQUIRED_FIELDS,
)

# Import scorer for direct verification
from tools.priority.deferred_scope_scorer import score_deferred_scope


class TestMarkerParsing:
    """Verify DEFERRED_SCOPE marker parsing (DoD-3 requirement 1)."""

    def test_marker_regex_extracts_body(self):
        response = "Some text\nDEFERRED_SCOPE: plan=test-123456 wave=W1 phase=P1.1 layer=L3 fan_in=5 surface=Execution coverage_gap_pct=45.0 est_tokens=3000 reason=test marker\nMore text"
        matches = list(MARKER_RE.finditer(response))
        assert len(matches) == 1
        assert matches[0].group("body").startswith("plan=test-123456")

    def test_parse_marker_extracts_all_fields(self):
        body = "plan=test-123456 wave=W1 phase=P1.1 layer=L3 fan_in=5 surface=Execution coverage_gap_pct=45.0 est_tokens=3000 reason=this is the reason"
        fields = _parse_marker(body)
        assert fields["plan"] == "test-123456"
        assert fields["wave"] == "W1"
        assert fields["phase"] == "P1.1"
        assert fields["layer"] == "L3"
        assert fields["fan_in"] == "5"
        assert fields["surface"] == "Execution"
        assert fields["coverage_gap_pct"] == "45.0"
        assert fields["est_tokens"] == "3000"
        assert fields["reason"] == "this is the reason"

    def test_validate_marker_detects_missing_fields(self):
        incomplete = {"plan": "test", "wave": "W1"}  # Missing many required fields
        missing = _validate_marker(incomplete)
        assert len(missing) > 0
        assert "phase" in missing
        assert "layer" in missing

    def test_validate_marker_passes_complete(self):
        complete = {f: "test" for f in REQUIRED_FIELDS}
        missing = _validate_marker(complete)
        assert missing == []


class TestPriorityScoring:
    """Verify P1..P5 scoring (DoD-3 requirement 2)."""

    def test_score_produces_band_and_impact(self):
        result = score_deferred_scope(
            layer="L3",
            fan_in=8,
            surface="Execution",
            coverage_gap_pct=45.0,
        )
        assert result.band in ["P1", "P2", "P3", "P4", "P5"]
        assert isinstance(result.impact_score, float)
        assert result.impact_score >= 0

    def test_high_impact_items_get_p1_or_p2(self):
        # L5 (high multiplier) + Security (high boost) + high coverage gap
        result = score_deferred_scope(
            layer="L5",
            fan_in=20,
            surface="Security",
            coverage_gap_pct=90.0,
        )
        assert result.band in ["P1", "P2"], f"Expected P1/P2 for high-impact item, got {result.band}"
        assert result.impact_score > 200

    def test_low_impact_items_get_p4_or_p5(self):
        # L6 (low multiplier) + None surface + low coverage gap
        result = score_deferred_scope(
            layer="L6",
            fan_in=1,
            surface="None",
            coverage_gap_pct=5.0,
        )
        assert result.band in ["P4", "P5"], f"Expected P4/P5 for low-impact item, got {result.band}"


class TestNotionPayloadBuilding:
    """Verify Backlog Items DB payload shape (DoD-3 requirement 3)."""

    def test_payload_has_required_properties(self):
        fields = {
            "plan": "test-plan-123456",
            "wave": "W1",
            "phase": "P1.1",
            "layer": "L3",
            "fan_in": "8",
            "surface": "Execution",
            "coverage_gap_pct": "45.0",
            "est_tokens": "3000",
            "reason": "Test deferred scope item",
        }
        payload = _build_notion_payload(fields, "P2", 200.5, token=None)

        # Check parent database
        assert payload["parent"]["database_id"]  # Should have a database ID

        props = payload["properties"]

        # Identity axis
        assert "Phase Title" in props
        assert "Phase ID" in props
        assert "Wave ID" in props
        assert "Plan File" in props

        # Classification axis
        assert props["P-Band"]["select"]["name"] == "P2"
        assert props["Layer"]["select"]["name"] == "L3"
        assert props["Surface"]["select"]["name"] == "Execution"
        assert props["Impact Score"]["number"] == 200.5

        # Lifecycle axis
        assert props["Status"]["select"]["name"] == "Not Started"
        assert props["Est Tokens"]["number"] == 3000

        # Outcome
        assert "Evidence" in props

    def test_payload_plan_relation_with_token(self):
        # This test would need mocking or a real token to fully test
        # For now, we verify the code path doesn't crash
        fields = {
            "plan": "notion-wave-lifecycle-autosync-f4a2b8",
            "wave": "W1",
            "phase": "P1.1",
            "layer": "L3",
            "fan_in": "8",
            "surface": "Execution",
            "coverage_gap_pct": "45.0",
            "est_tokens": "3000",
            "reason": "Test with plan relation",
        }
        # Pass None token - should skip relation but not crash
        payload = _build_notion_payload(fields, "P2", 200.5, token=None)
        assert "Plan" not in payload["properties"]  # No relation without token


class TestIntegrationVerification:
    """End-to-end verification that hook components work together."""

    def test_full_flow_from_marker_to_payload(self):
        """Simulate what the hook does: parse → validate → score → build payload."""
        marker_text = "plan=test-integration-123456 wave=W2 phase=P2.1 layer=L5 fan_in=15 surface=Security coverage_gap_pct=80.0 est_tokens=5000 reason=integration test of full flow"

        # Step 1: Parse
        fields = _parse_marker(marker_text)
        assert fields["plan"] == "test-integration-123456"

        # Step 2: Validate
        missing = _validate_marker(fields)
        assert missing == []

        # Step 3: Score
        result = score_deferred_scope(
            layer=fields["layer"],
            fan_in=int(fields["fan_in"]),
            surface=fields["surface"],
            coverage_gap_pct=float(fields["coverage_gap_pct"]),
        )
        assert result.band in ["P1", "P2"]  # High impact should be P1/P2

        # Step 4: Build payload
        payload = _build_notion_payload(fields, result.band, result.impact_score, token=None)
        assert payload["properties"]["P-Band"]["select"]["name"] == result.band
        assert payload["properties"]["Impact Score"]["number"] == result.impact_score


def run_tests():
    """Run all tests and report results."""
    import traceback

    test_classes = [TestMarkerParsing, TestPriorityScoring, TestNotionPayloadBuilding, TestIntegrationVerification]
    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        print(f"\n=== {cls.__name__} ===")
        instance = cls()
        for name in dir(instance):
            if name.startswith("test_"):
                total += 1
                try:
                    getattr(instance, name)()
                    print(f"  ✓ {name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  ✗ {name}: {e}")
                    failed += 1
                except Exception as e:
                    print(f"  ✗ {name}: {type(e).__name__}: {e}")
                    traceback.print_exc()
                    failed += 1

    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
