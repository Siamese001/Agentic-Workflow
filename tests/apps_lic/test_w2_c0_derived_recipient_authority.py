"""W2 recipient-class authority migration for apps_lic canonical dispatch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.engines.governed_opportunity_ingestion import STATUS_MISSING
from apps_lic.engines.recipient_classification import CLASS_CEO, STATUS_DERIVED
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import (
    ready_governed_opportunity_facts,
)


def _load_json(run_dir: Path, name: str) -> dict:
    path = run_dir / name
    assert path.is_file(), f"missing {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def test_w2_c0_derived_ceo_overrides_recruiter_u0_hint(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Draft a concise note for a CEO target.",
        lead_profile={
            "verified_name": "Taylor Morgan",
            "title": "Technical Recruiter",
            "seniority_class": "RECRUITER",
            "company_name": "Acme",
            "industry": "Technology",
            "consent_attested": True,
        },
        governed_opportunity_facts=ready_governed_opportunity_facts(
            contact_text="Taylor Morgan | Chief Executive Officer | Acme",
            role_ownership_text="Current CEO and accountable executive for AI strategy.",
        ),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "ceo")

    assert result.pa_invoked is True
    assert result.l2_executed is True
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    c0_summary = _load_json(result.artifact_dir, "fec_summary.json")
    pa = _load_json(result.artifact_dir, "pa_receipt.json")
    l2 = _load_json(result.artifact_dir, "l2_execution_receipt.json")
    draft = json.loads(l2["payload"]["generated_content"])

    assert manifest["c0_recipient_class_status"] == STATUS_DERIVED
    assert manifest["derived_recipient_class"] == CLASS_CEO
    assert c0_summary["u0_recipient_class_hint"] == "RECRUITER"
    assert c0_summary["u0_recipient_class_hint_authority"] == "false"
    assert c0_summary["derived_recipient_class"] == CLASS_CEO
    assert c0_summary["recipient_class_reason_codes"]

    prompt_text = "\n".join(
        str(block.get("content") or "")
        for block in pa["payload"]["prompt_blocks"]
    )
    assert '"recipient_class":"ceo"' in prompt_text
    assert '"recipient_class":"recruiter"' not in prompt_text
    assert "U0 recipient class hint: RECRUITER" in prompt_text
    assert "C0-derived recipient class: CEO" in prompt_text
    assert draft["recipient_class"] == "ceo"
    assert draft["recipient_category"] == CLASS_CEO


def test_w2_u0_ceo_hint_without_governed_evidence_still_blocks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Inline-only CEO hint must not bypass C0.",
        lead_profile={
            "verified_name": "Taylor Morgan",
            "title": "Chief Executive Officer",
            "seniority_class": "CEO",
            "company_name": "Acme",
            "industry": "Technology",
            "consent_attested": True,
        },
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "no_c0")

    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    c0_summary = _load_json(result.artifact_dir, "fec_summary.json")
    assert manifest["terminal_c0_block"] is True
    assert manifest["c0_block_status"] == STATUS_MISSING
    assert manifest["pa_invoked"] is False
    assert manifest["l2_executed"] is False
    assert c0_summary["u0_recipient_class_hint"] == "CEO"
    assert c0_summary["u0_recipient_class_hint_authority"] == "false"
    assert not (result.artifact_dir / "pa_receipt.json").exists()
    assert not (result.artifact_dir / "l2_execution_receipt.json").exists()
