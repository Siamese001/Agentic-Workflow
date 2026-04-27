"""Per-app required artifact presence.

Each app must produce its app-specific artifacts to pass anti-cheat.
For Phase 1, the only enforced app is ``apps_underwriting_ai``.
"""

from __future__ import annotations

import json
from pathlib import Path


# Per master plan, apps_underwriting_ai required artifacts beyond the spine:
APPS_UNDERWRITING_AI_REQUIRED = (
    "decision_packet.json",
    "decision_memo.json",
    "audit_trace.json",
    "evidence_register.json",
    "exception_register.json",
)


def test_apps_underwriting_ai_required_artifacts(
    proof_dir: Path, run_manifest: dict
) -> None:
    if run_manifest.get("app_name") != "apps_underwriting_ai":
        return  # Test only applies to this app
    contracts = proof_dir / "contracts"
    missing = [
        name for name in APPS_UNDERWRITING_AI_REQUIRED
        if not (contracts / name).exists()
    ]
    assert not missing, (
        f"apps_underwriting_ai missing required app artifacts: {missing}"
    )


def test_decision_packet_payload_carries_recommendation(
    proof_dir: Path, run_manifest: dict
) -> None:
    if run_manifest.get("app_name") != "apps_underwriting_ai":
        return
    p = proof_dir / "contracts" / "decision_packet.json"
    assert p.exists(), "decision_packet.json missing"
    body = json.loads(p.read_text(encoding="utf-8"))
    payload = body.get("payload", body) if isinstance(body, dict) else body
    assert isinstance(payload, dict), "decision_packet payload not a dict"
    decision = payload.get("decision_state")
    assert decision in {
        "APPROVE", "APPROVE_WITH_CONDITIONS", "COUNTER_OFFER",
        "PEND_FOR_INFORMATION", "DECLINE", "ESCALATE_TO_HUMAN",
    }, f"decision_state={decision!r} not in allowed set"


def test_evidence_register_has_real_entries(
    proof_dir: Path, run_manifest: dict
) -> None:
    if run_manifest.get("app_name") != "apps_underwriting_ai":
        return
    p = proof_dir / "contracts" / "evidence_register.json"
    body = json.loads(p.read_text(encoding="utf-8"))
    payload = body.get("payload", body) if isinstance(body, dict) else body
    entries = payload.get("entries", []) if isinstance(payload, dict) else []
    assert entries, (
        "evidence_register has no entries — driver did not run real "
        "EvidenceRegisterEngine.collect_financial_evidence"
    )
