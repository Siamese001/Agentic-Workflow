"""Tests for `.codex/governance/scripts/post_agent_router_decision_audit.py`.

Constitutional §28 / closed-loop-router-enforcement.md.
Audits Cursor Agent responses for missing/malformed router-decision evidence.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
SCRIPT = REPO / ".codex" / "governance" / "scripts" / "post_agent_router_decision_audit.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("post_agent_router_decision_audit", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def audit_mod():
    return _load_module()


@pytest.fixture
def isolated_log(tmp_path, monkeypatch, audit_mod):
    """Redirect VIOLATIONS_LOG to a tmp file."""
    log = tmp_path / "router_enforcement_violations.jsonl"
    monkeypatch.setattr(audit_mod, "VIOLATIONS_LOG", log)
    return log


# ---------------------------------------------------------------------------
# Audit A — router edits without evidence
# ---------------------------------------------------------------------------


class TestRouterFilesWithoutEvidence:
    def test_edit_intent_with_router_file_no_evidence_violates(self, audit_mod):
        text = (
            "I edited `agentic_core/L6_observability/flywheel_promoter.py` to "
            "tighten the promotion threshold. No marker emitted in this response."
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "router_files_without_evidence" in kinds

    def test_edit_intent_with_marker_does_not_violate(self, audit_mod):
        text = (
            "I edited agentic_core/L6_observability/flywheel_promoter.py.\n"
            "ROUTER_DECISION: layer=L6 router=promo decision_id=abc123 "
            "trace_id=t1 route_id=r1 selected=arm_a verdict=promote "
            "wilson_lower=0.7 z_score=2.5 uplift=0.1 n=50"
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "router_files_without_evidence" not in kinds

    def test_edit_intent_with_library_call_does_not_violate(self, audit_mod):
        text = (
            "I edited agentic_core/L6_observability/regret_accounting.py.\n"
            'The hook now calls `emit_ledger_event(ledger="router_l6_regret", '
            'event_kind="regret_cycle", prediction={"top": "L3"})`.'
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "router_files_without_evidence" not in kinds

    def test_router_file_mentioned_without_edit_intent_does_not_violate(self, audit_mod):
        text = "Reading agentic_core/L6_observability/flywheel_promoter.py for context only."
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "router_files_without_evidence" not in kinds


# ---------------------------------------------------------------------------
# Audit B — promote verdict floor (Wilson + z + uplift + n)
# ---------------------------------------------------------------------------


class TestPromoteWithoutFloor:
    BASE = (
        "ROUTER_DECISION: layer=L6 router=promo decision_id=p1 "
        "trace_id=t1 route_id=r1 selected=cand_a verdict=promote "
    )

    def test_all_four_fields_pass(self, audit_mod):
        text = self.BASE + "wilson_lower=0.65 z_score=2.10 uplift=0.05 n=42"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert floor_v == []

    def test_wilson_below_floor_violates(self, audit_mod):
        text = self.BASE + "wilson_lower=0.40 z_score=2.10 uplift=0.05 n=42"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert len(floor_v) == 1
        assert any("wilson_lower:0.40<0.60" in g for g in floor_v[0]["gaps"])

    def test_z_below_floor_violates(self, audit_mod):
        text = self.BASE + "wilson_lower=0.65 z_score=1.50 uplift=0.05 n=42"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert len(floor_v) == 1
        assert any("z_score:1.50<1.96" in g for g in floor_v[0]["gaps"])

    def test_uplift_zero_violates(self, audit_mod):
        text = self.BASE + "wilson_lower=0.65 z_score=2.10 uplift=0.0 n=42"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert len(floor_v) == 1
        assert any("uplift" in g for g in floor_v[0]["gaps"])

    def test_n_below_floor_violates(self, audit_mod):
        text = self.BASE + "wilson_lower=0.65 z_score=2.10 uplift=0.05 n=20"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert len(floor_v) == 1
        assert any("n:20<30" in g for g in floor_v[0]["gaps"])

    def test_all_missing_lists_all_gaps(self, audit_mod):
        text = self.BASE + "selected=x"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert len(floor_v) == 1
        gap_str = " ".join(floor_v[0]["gaps"])
        assert "wilson_lower:missing" in gap_str
        assert "z_score:missing" in gap_str
        assert "uplift:missing" in gap_str
        assert "n:missing" in gap_str

    def test_promote_violation_has_blocking_severity(self, audit_mod):
        text = self.BASE + "wilson_lower=0.40 z_score=2.10 uplift=0.05 n=42"
        violations = audit_mod.audit_response(text)
        floor_v = [v for v in violations if v["kind"] == "promote_without_floor"]
        assert floor_v[0]["severity"] == "blocking"


# ---------------------------------------------------------------------------
# Audit C — regret without by_layer attribution
# ---------------------------------------------------------------------------


class TestRegretWithoutAttribution:
    def test_empty_by_layer_violates(self, audit_mod):
        text = (
            "ROUTER_DECISION: layer=L6 router=regret decision_id=rg1 "
            "trace_id=t1 route_id=r1 selected=cycle_42 by_layer_json={}"
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "regret_without_attribution" in kinds

    def test_missing_by_layer_violates(self, audit_mod):
        text = (
            "ROUTER_DECISION: layer=L6 router=regret decision_id=rg1 "
            "trace_id=t1 route_id=r1 selected=cycle_42"
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "regret_without_attribution" in kinds

    def test_populated_by_layer_passes(self, audit_mod):
        text = (
            "ROUTER_DECISION: layer=L6 router=regret decision_id=rg1 "
            "trace_id=t1 route_id=r1 selected=cycle_42 "
            'by_layer_json={"L0":0.1,"L3":0.4}'
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "regret_without_attribution" not in kinds


# ---------------------------------------------------------------------------
# Audit D — required-field gaps in marker
# ---------------------------------------------------------------------------


class TestMarkerRequiredFields:
    def test_missing_trace_id_violates(self, audit_mod):
        text = "ROUTER_DECISION: layer=L0 router=bandit decision_id=b1 route_id=r1 selected=arm_a"
        violations = audit_mod.audit_response(text)
        gaps = [v for v in violations if v["kind"] == "marker_missing_required_field"]
        assert len(gaps) == 1
        assert "trace_id:missing" in gaps[0]["gaps"]

    def test_missing_route_id_violates(self, audit_mod):
        text = "ROUTER_DECISION: layer=L0 router=bandit decision_id=b1 trace_id=t1 selected=arm_a"
        violations = audit_mod.audit_response(text)
        gaps = [v for v in violations if v["kind"] == "marker_missing_required_field"]
        assert len(gaps) == 1
        assert "route_id:missing" in gaps[0]["gaps"]

    def test_missing_selected_violates(self, audit_mod):
        text = "ROUTER_DECISION: layer=L0 router=bandit decision_id=b1 trace_id=t1 route_id=r1"
        violations = audit_mod.audit_response(text)
        gaps = [v for v in violations if v["kind"] == "marker_missing_required_field"]
        assert len(gaps) == 1
        assert "selected:missing" in gaps[0]["gaps"]

    def test_complete_marker_passes(self, audit_mod):
        text = "ROUTER_DECISION: layer=L0 router=bandit decision_id=b1 trace_id=t1 route_id=r1 selected=arm_a"
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "marker_missing_required_field" not in kinds


# ---------------------------------------------------------------------------
# Multiple markers / multiple violations in one response
# ---------------------------------------------------------------------------


class TestMultipleMarkers:
    def test_two_markers_each_audited(self, audit_mod):
        text = (
            "ROUTER_DECISION: layer=L6 router=promo decision_id=p1 "
            "trace_id=t1 route_id=r1 selected=cand_a verdict=promote "
            "wilson_lower=0.40 z_score=2.10 uplift=0.05 n=42\n"
            "ROUTER_DECISION: layer=L6 router=regret decision_id=rg1 "
            "trace_id=t1 route_id=r1 selected=cycle_1 by_layer_json={}"
        )
        violations = audit_mod.audit_response(text)
        kinds = [v["kind"] for v in violations]
        assert "promote_without_floor" in kinds
        assert "regret_without_attribution" in kinds


# ---------------------------------------------------------------------------
# Bypass + entrypoint
# ---------------------------------------------------------------------------


class TestEntrypoint:
    def test_bypass_short_circuits(self, audit_mod, monkeypatch, isolated_log, capsys):
        monkeypatch.setenv("ROUTER_ENFORCEMENT_BYPASS", "1")
        monkeypatch.setattr(
            "sys.stdin",
            _FakeStdin(
                json.dumps(
                    {
                        "tool_info": {
                            "response": "edited agentic_core/L6_observability/regret_accounting.py"
                        },
                    }
                )
            ),
        )
        rc = audit_mod.main()
        assert rc == 0
        # Should record exactly one bypass row
        assert isolated_log.exists()
        lines = [json.loads(line) for line in isolated_log.read_text(encoding="utf-8").splitlines()]
        assert len(lines) == 1
        assert lines[0]["kind"] == "bypass"

    def test_main_writes_violations(self, audit_mod, monkeypatch, isolated_log):
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        payload = {
            "tool_info": {
                "response": (
                    "I edited agentic_core/L6_observability/promotion_gates.py to tune the threshold."
                )
            }
        }
        monkeypatch.setattr("sys.stdin", _FakeStdin(json.dumps(payload)))
        rc = audit_mod.main()
        assert rc == 0
        lines = [json.loads(line) for line in isolated_log.read_text(encoding="utf-8").splitlines()]
        kinds = [r["kind"] for r in lines]
        assert "router_files_without_evidence" in kinds

    def test_main_handles_empty_stdin(self, audit_mod, monkeypatch, isolated_log):
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        monkeypatch.setattr("sys.stdin", _FakeStdin(""))
        rc = audit_mod.main()
        assert rc == 0
        assert not isolated_log.exists()  # no writes for empty input

    def test_main_handles_non_json_stdin(self, audit_mod, monkeypatch, isolated_log):
        monkeypatch.delenv("ROUTER_ENFORCEMENT_BYPASS", raising=False)
        monkeypatch.setattr("sys.stdin", _FakeStdin("Plain text. No router file. No violations."))
        rc = audit_mod.main()
        assert rc == 0
        # No router-file-edit pattern → no violations.
        assert not isolated_log.exists() or isolated_log.read_text(encoding="utf-8").strip() == ""


class _FakeStdin:
    """Minimal stdin substitute supporting .read() and .isatty()."""

    def __init__(self, payload: str) -> None:
        self._payload = payload

    def read(self) -> str:
        return self._payload

    def isatty(self) -> bool:
        return False
