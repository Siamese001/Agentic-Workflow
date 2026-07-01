"""Smoke tests for apps_lic canonical product dispatch."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_lic.runtime.dispatch.canonical_dispatch import (
    ROUTE_FAMILY_R4,
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from apps_lic.runtime.profile_builder_adapter import parse_payload
from tests.apps_lic.canonical_readiness_fixtures import ready_governed_opportunity_facts


def test_build_cli_ingress_r4_fresh_context() -> None:
    raw = build_cli_ingress_raw(manual_brief="Acme renewal briefing for Jane Smith.")
    inputs = (raw.get("personalization") or {}).get("inputs") or {}
    assert inputs.get("manual_brief")


def test_canonical_spine_r4_managed_workflow(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        run_id="phase0_canonical_lic_01",
        request_id="req_phase0_canonical_lic_01",
        manual_brief="Enterprise renewal outreach for VP Technology at Acme Corp.",
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )
    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "run")
    assert result.route_family == ROUTE_FAMILY_R4
    assert result.execution_form == "managed_workflow"
    assert result.terminal_r5 is False
    assert result.l3_participated is True
    assert result.c0_invoked is True
    assert result.pa_invoked is True
    manifest_path = result.artifact_dir / "spine_run_manifest.json"
    assert manifest_path.is_file()
    import json

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["x3_disposition"] == result.x3_disposition
    assert manifest["x3_disposition"] != "UNKNOWN"
    assert manifest["exit_status"] == result.exit_status
    assert manifest["outcome_authorized"] == result.outcome_authorized

    route = json.loads((result.artifact_dir / "route_contract.json").read_text(encoding="utf-8"))
    route_payload = route["payload"]
    assert "claude-sonnet-5" in route_payload["allowed_models"]
    assert "gpt-5.5" in route_payload["allowed_models"]
    assert "api.anthropic.com" in route_payload["allowed_networks"]
    assert "api.openai.com" in route_payload["allowed_networks"]


def test_canonical_spine_r5_without_context_or_research(tmp_path: Path) -> None:
    raw = build_cli_ingress_raw(manual_brief="", allow_research=False)
    result = run_canonical_apps_lic_spine(
        raw,
        artifact_root=tmp_path / "r5",
        skip_r3r4_research=True,
    )
    assert result.terminal_r5 is True
    assert result.execution_form == "terminal_fallback"
    assert result.exit_status == "blocked"
    assert result.outcome_authorized is False
    assert (result.artifact_dir / "exit_disposition_receipt.json").is_file()


def test_parse_payload_materializes_missing_brief(tmp_path: Path, monkeypatch) -> None:
    generated = tmp_path / "briefing.md"
    generated.write_text("Generated company brief for Acme.\n", encoding="utf-8")
    monkeypatch.setattr(
        "apps_lic.runtime.profile_builder_adapter._materialize_missing_brief",
        lambda payload: str(generated),
    )
    envelope = parse_payload(
        {
            "recipient_class": "recruiter",
            "channel": "linkedin",
            "outreach_mode": "cold",
            "target_company": "Acme",
            "request_id": "req-lic-brief",
            "run_id": "run-lic-brief",
            "trace_id": "trace-lic-brief",
        }
    )
    assert envelope is not None
    assert envelope.payload.briefing_artifact_ref == str(generated)
    assert envelope.payload.user_constraints["manual_brief"] == str(generated)
