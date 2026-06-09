"""W0 characterization tests for apps_lic canonical hardening.

These tests intentionally describe the hardened behavior before W1-W7 land.
They are strict xfails so the current unsafe behavior is documented without
blocking W0, and an unexpected pass becomes visible during hardening.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apps_lic.engines.validation_engine import ValidationEngine
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import ready_governed_opportunity_facts


def _load_json(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    assert path.is_file(), f"missing canonical artifact: {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _run_stubbed_spine(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    manual_brief: str = "Enterprise outreach context for a named executive.",
    campaign_objective: str | None = None,
    lead_profile: dict[str, Any] | None = None,
    include_governed_readiness: bool = True,
) -> Any:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief=manual_brief,
        campaign_objective=campaign_objective,
        governed_opportunity_facts=(
            ready_governed_opportunity_facts()
            if include_governed_readiness
            else None
        ),
        lead_profile=lead_profile
        or {
            "verified_name": "Jane Smith",
            "title": "Chief Digital Officer",
            "seniority_class": "UNKNOWN",
            "company_name": "Acme",
            "industry": "Technology",
            "consent_attested": True,
        },
    )
    return run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "run")


def test_current_inline_c0_named_outreach_should_not_pass_after_hardening(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_stubbed_spine(
        tmp_path,
        monkeypatch,
        include_governed_readiness=False,
    )
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")

    assert manifest["evidence_support_status"] != "PASS", (
        "Hardened C0 must not treat inline user-supplied lead/campaign data "
        "as sufficient governed opportunity evidence."
    )
    assert manifest["pa_invoked"] is False
    assert manifest["l2_executed"] is False
    assert manifest["outcome_authorized"] is False


@pytest.mark.xfail(
    strict=True,
    reason=(
        "W0 gap: PA reads lead_profile.seniority_class from L1 and defaults "
        "unknown values to recruiter instead of consuming C0-derived class."
    ),
)
def test_current_pa_unknown_class_falls_back_to_recruiter_gap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_stubbed_spine(tmp_path, monkeypatch)
    pa = _load_json(result.artifact_dir, "pa_receipt.json")
    prompt_blocks = pa["payload"]["prompt_blocks"]
    prompt_text = "\n".join(str(block.get("content") or "") for block in prompt_blocks)

    assert '"recipient_class":"recruiter"' not in prompt_text, (
        "Hardened PA/L2 must block or use C0-derived recipient class; it must "
        "not default UNKNOWN seniority_class to recruiter."
    )


def test_current_canonical_dispatch_does_not_call_app_x2_gap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_lic.engines import validation_exit

    calls: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
    original = validation_exit.run_x2_validation

    def _spy(*args: Any, **kwargs: Any) -> Any:
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(validation_exit, "run_x2_validation", _spy)
    _run_stubbed_spine(tmp_path, monkeypatch)

    assert calls, "Canonical dispatch must invoke apps_lic X2 before Exit clearance."


@pytest.mark.xfail(
    strict=True,
    reason=(
        "W0 gap: Exit review packet still fabricates C0 PASS and perfect "
        "groundedness/faithfulness/citation precision from generic defaults."
    ),
)
def test_current_exit_hardcodes_c0_pass_gap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from apps_lic.runtime.bindings import exit_binding

    packets: list[Any] = []
    original = exit_binding.run_all_x1_gates

    def _spy(packet: Any) -> Any:
        packets.append(packet)
        return original(packet)

    monkeypatch.setattr(exit_binding, "run_all_x1_gates", _spy)
    _run_stubbed_spine(tmp_path, monkeypatch)

    assert packets, "Exit should produce an inspectable review packet."
    packet = packets[0]
    assert packet.final_evidence_contract.get("c0_status") != "PASS", (
        "Exit must consume actual apps_lic C0 proof; a synthetic PASS is not "
        "valid hardening evidence."
    )
    assert packet.output.get("groundedness") != 1.0
    assert packet.output.get("faithfulness") != 1.0
    assert packet.output.get("citation_precision") != 1.0


def test_current_sc3_candidate_count_materializes_candidate_batch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_stubbed_spine(
        tmp_path,
        monkeypatch,
        manual_brief="AIG executive agentic AI briefing for a C-level recipient.",
        campaign_objective=(
            "Draft a concise LinkedIn message about AIG's VP Global Head of "
            "Agentic AI Solutions opportunity."
        ),
        lead_profile={
            "verified_name": "Scott Hallworth",
            "title": "Executive Vice President and Chief Digital Officer",
            "seniority_class": "",
            "company_name": "AIG",
            "industry": "Insurance",
            "consent_attested": True,
        },
    )
    l2 = _load_json(result.artifact_dir, "l2_execution_receipt.json")
    w4 = _load_json(result.artifact_dir, "w4_candidate_batch.json")
    draft = json.loads(l2["payload"]["generated_content"])

    assert isinstance(draft.get("candidates"), list), (
        "SC-3 must persist candidate objects, not only candidate_count metadata."
    )
    assert len(draft["candidates"]) == 3
    assert draft.get("selected_candidate_id")
    assert w4["payload"]["status"] == "W4_CANDIDATE_BATCH_READY"
    assert w4["payload"]["candidate_count_materialized"] == 3


def test_non_aig_message_does_not_require_aig_terms(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    result = _run_stubbed_spine(
        tmp_path,
        monkeypatch,
        manual_brief="Neo4j product leadership outreach context.",
        campaign_objective="Draft a concise LinkedIn message for a Neo4j product leader.",
        lead_profile={
            "verified_name": "Maya Patel",
            "title": "VP Product Management",
            "seniority_class": "EXECUTIVE",
            "company_name": "Neo4j",
            "industry": "Graph Data Platform",
            "consent_attested": True,
        },
    )
    assert result.terminal_r5 is False

    report = ValidationEngine().execute(
        {
            "draft_message": {
                "channel": "linkedin",
                "recipient_class": "executive",
                "message_text": (
                    "Hi Maya, your graph data platform leadership maps well to "
                    "senior engineering work in production systems. Open to a "
                    "brief chat about the product leadership role?"
                ),
                "unsupported_claims": [],
            },
            "evidence_bundle": {"support_status": "PASS", "count": 3},
            "reasoning_policy": {
                "fail_closed_on_empty_evidence": True,
                "max_candidates": 1,
            },
        }
    )["validation_report"]

    assert report["passed"], (
        "A non-AIG message with sufficient generic proof should not require "
        f"AIG/insurance terms; issues={report['issues']}"
    )
