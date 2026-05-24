"""Contract tests for X1D judge packet coherence and provider transport parity.

These would have caught the Brown & Brown Claude-only soft-fail (runs 001344/014222/005722):
same packet, X2 all PASS, Gemini/OpenAI PASS, Claude FAIL ~2.8.

Tests assert zero violations from audit_* helpers — they FAIL on current code until
exec-summary-x1d-transport-parity-d8f2a1 plan lands.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    GRAPH_ONLY_GRADE_ONLY_RUBRIC,
    SRFS_GRADE_ONLY_RUBRIC,
    judge_contract_hash,
    reconcile_grade_only_judge_result,
    reconcile_judge_result_against_deterministic_gate_closures,
)
from apps_rg.runtime.judges.executive_summary_x1d import _make_model_backed_output, build_x1d_judge_system_prompt
from apps_rg.runtime.sections.executive_summary_x1d_judge_contract import (
    CLAUDE_001344_GATE_CLOSURE_ONLY_FINDINGS,
    CLAUDE_001344_JUDGE_RESULT,
    CLAUDE_001344_RESIDUAL_QUALITY_FINDINGS,
    audit_active_graph_rubric_x2_supremacy,
    audit_evidence_utilization_prompt_coherence,
    audit_executive_summary_x1d_judge_coherence,
    audit_identical_judge_json_same_pass_all_providers,
    audit_judge_packet_coherence,
    audit_provider_transport_parity,
    audit_reconcile_claude_class_soft_fail,
    audit_rubric_soft_penalties_when_gates_pass,
    build_brown_brown_six_sentence_packet,
    load_frozen_post_x2_packet,
)

_REPO = Path(__file__).resolve().parents[3]


def _violation_codes(violations: list) -> list[str]:
    return [getattr(v, "code", getattr(v, "kind", "")) for v in violations]


# --- Would-have-caught: rubric / packet instruction conflict -----------------


def test_graph_rubric_includes_x2_supremacy_dim8_like_srfs() -> None:
    """SRFS has dim 8; active GRAPH rubric used on lane must match."""
    assert "penalize gates that show" in SRFS_GRADE_ONLY_RUBRIC.lower()
    violations = audit_active_graph_rubric_x2_supremacy()
    assert violations == [], _violation_codes(violations)


def test_graph_rubric_no_soft_penalty_on_passed_credential_gate() -> None:
    packet = build_brown_brown_six_sentence_packet()
    gates = packet["deterministic_gate_summary"]
    assert gates["x2_exec_summary_no_credential_dump"]["pass"] is True
    violations = audit_rubric_soft_penalties_when_gates_pass(packet)
    assert violations == [], _violation_codes(violations)


def test_graph_rubric_no_penalize_unused_when_util_gate_passed() -> None:
    packet = build_brown_brown_six_sentence_packet()
    gates = packet["deterministic_gate_summary"]
    assert gates["x2_exec_summary_evidence_utilization"]["pass"] is True
    eu = packet["evidence_utilization"]
    assert eu.get("unused_fact_count", 0) >= 1
    violations = audit_evidence_utilization_prompt_coherence(packet)
    assert violations == [], _violation_codes(violations)


def test_brown_synthetic_packet_full_coherence_audit() -> None:
    packet = build_brown_brown_six_sentence_packet()
    violations = audit_judge_packet_coherence(packet)
    assert violations == [], _violation_codes(violations)


@pytest.mark.skipif(
    not (
        _REPO
        / "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_summary_20260524_001344/executive_summary_judge_packet_post_x2.json"
    ).is_file(),
    reason="frozen 001344 post-X2 packet not on disk",
)
def test_frozen_001344_post_x2_packet_coherence() -> None:
    packet = load_frozen_post_x2_packet(_REPO)
    assert packet is not None
    packet = dict(packet)
    packet["rubric"] = GRAPH_ONLY_GRADE_ONLY_RUBRIC
    summary = packet.get("deterministic_gate_summary") or {}
    failed = [k for k, v in summary.items() if isinstance(v, dict) and v.get("pass") is False]
    assert failed == [], f"fixture assumption broken: X2 fails {failed}"
    violations = audit_judge_packet_coherence(packet)
    assert violations == [], _violation_codes(violations)


# --- Would-have-caught: provider transport asymmetry -------------------------


def test_provider_transport_parity_zero_violations() -> None:
    violations = audit_provider_transport_parity()
    assert violations == [], _violation_codes(violations)


# --- Would-have-caught: reconcile gap for Claude 001344 class ----------------


def test_reconcile_claude_001344_class_findings_when_all_x2_pass() -> None:
    violations = audit_reconcile_claude_class_soft_fail()
    assert violations == [], _violation_codes(violations)


def test_reconcile_positive_gate_closure_only_findings_pass() -> None:
    gate_summary = {
        gid: {"pass": True, "detail": "ok"}
        for gid in (
            "x2_exec_summary_sentence_count_6",
            "x2_exec_summary_evidence_utilization",
            "x2_exec_summary_no_credential_dump",
            "x2_exec_summary_no_mechanism_inventory",
        )
    }
    body = dict(CLAUDE_001344_JUDGE_RESULT)
    body["findings"] = list(CLAUDE_001344_GATE_CLOSURE_ONLY_FINDINGS)
    out = reconcile_judge_result_against_deterministic_gate_closures(body, gate_summary)
    assert float(out["score"]) >= float(out["threshold"])
    assert out.get("pass") is True
    receipt = out.get("reconciliation_receipt") or {}
    assert receipt.get("suppressed_findings")


def test_reconcile_negative_control_preserves_residual_quality_fail() -> None:
    gate_summary = {
        "x2_exec_summary_no_credential_dump": {"pass": True, "detail": "ok"},
        "x2_exec_summary_evidence_utilization": {"pass": True, "detail": "ok"},
    }
    body = {
        "score_scale": "0_to_5",
        "score": 2.5,
        "threshold": 4.0,
        "pass": False,
        "decisive_failure": False,
        "findings": list(CLAUDE_001344_RESIDUAL_QUALITY_FINDINGS),
        "cited_sentence_indexes": [1, 2],
        "remediation_suggestions": [],
    }
    out = reconcile_judge_result_against_deterministic_gate_closures(body, gate_summary)
    assert float(out["score"]) < float(out["threshold"])
    assert out.get("pass") is False
    preserved = out.get("findings") or []
    assert len(preserved) >= 1


def test_canonical_contract_hash_stable_for_same_packet() -> None:
    packet_a = build_brown_brown_six_sentence_packet()
    packet_b = build_brown_brown_six_sentence_packet()
    assert judge_contract_hash(packet_a) == judge_contract_hash(packet_b)


def test_write_judge_packet_emits_canonical_contract_artifact(tmp_path: Path) -> None:
    from apps_rg.runtime.judges.executive_summary_judge_packet import (
        write_executive_summary_judge_packet,
    )

    packet = build_brown_brown_six_sentence_packet()
    pkt_path = tmp_path / "executive_summary_judge_packet.json"
    write_executive_summary_judge_packet(pkt_path, packet)
    canon_path = tmp_path / "canonical_judge_contract.json"
    assert canon_path.is_file()
    body = json.loads(canon_path.read_text(encoding="utf-8"))
    assert body["judge_contract_hash"] == judge_contract_hash(packet)
    assert body["canonical_judge_contract"]["judge_task"] == "GRADE_ONLY"


def test_build_x1d_judge_system_prompt_includes_score_schema() -> None:
    system = build_x1d_judge_system_prompt()
    assert "JUDGE_SCORE_SCHEMA" in system or "score_scale" in system
    assert "0_to_5" in system


# --- Sanity: pass math is provider-neutral for identical JSON ----------------


def test_identical_judge_json_same_pass_all_providers() -> None:
    violations = audit_identical_judge_json_same_pass_all_providers()
    assert violations == []


def test_make_model_backed_output_parity_explicit() -> None:
    body = {
        "score_scale": "0_to_5",
        "score": 3.5,
        "threshold": 4.0,
        "pass": False,
        "decisive_failure": False,
        "findings": ["metric stack"],
        "cited_sentence_indexes": [2],
        "remediation_suggestions": [],
    }
    gate_summary = {"x2_exec_summary_no_credential_dump": {"pass": True, "detail": "ok"}}
    statuses = {}
    for key in ("gemini_pro", "openai_chatgpt", "anthropic_claude"):
        out = _make_model_backed_output(
            key, "h", "m", dict(body), deterministic_gate_summary=gate_summary
        )
        statuses[key] = (out.provider_status, out.normalized_score, out.pass_)
    assert statuses["gemini_pro"] == statuses["openai_chatgpt"] == statuses["anthropic_claude"]


# --- CI-shaped aggregate (feeds drift gate when wired) -----------------------


def test_executive_summary_x1d_judge_coherence_aggregate() -> None:
    violations = audit_executive_summary_x1d_judge_coherence()
    assert violations == [], "\n".join(f"[{v.kind}] {v.detail}" for v in violations)


def test_active_rubric_is_graph_only() -> None:
    packet = build_brown_brown_six_sentence_packet()
    assert packet["rubric"] == GRAPH_ONLY_GRADE_ONLY_RUBRIC
