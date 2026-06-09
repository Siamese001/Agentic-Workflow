"""W1 live C0 readiness gate for apps_lic canonical dispatch."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_lic.engines.governed_opportunity_ingestion import (
    NAMESPACE_CONTACT,
    STATUS_BLOCKED,
    STATUS_CONFLICTED,
    STATUS_MISSING,
    STATUS_READY,
    STATUS_STALE,
)
from apps_lic.engines.recipient_classification import (
    STATUS_DERIVED,
    STATUS_LOW_CONFIDENCE,
)
from apps_lic.runtime.dispatch.canonical_dispatch import (
    build_cli_ingress_raw,
    run_canonical_apps_lic_spine,
)
from tests.apps_lic.canonical_readiness_fixtures import (
    conflicted_governed_opportunity_facts,
    fact_packet,
    low_confidence_recipient_facts,
    ready_governed_opportunity_facts,
)


def _load_json(run_dir: Path, name: str) -> dict:
    path = run_dir / name
    assert path.is_file(), f"missing {name}"
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_c0_blocked(run_dir: Path, expected_status: str) -> dict:
    manifest = _load_json(run_dir, "spine_run_manifest.json")
    proof = _load_json(run_dir, "runtime_proof_bundle.json")

    assert manifest["terminal_c0_block"] is True
    assert manifest["c0_block_status"] == expected_status
    assert manifest["pa_invoked"] is False
    assert manifest["l2_executed"] is False
    assert manifest["l3_participated"] is False
    assert manifest["outcome_authorized"] is False
    assert manifest["exit_status"] == "blocked"
    assert proof["status"] == "PASS"
    assert proof["proof_mode"] == "c0_block"
    for forbidden in (
        "pa_receipt.json",
        "l3_workflow_receipt.json",
        "l2_execution_receipt.json",
        "exit_disposition_receipt.json",
    ):
        assert not (run_dir / forbidden).exists()
    return manifest


def test_w1_missing_governed_readiness_blocks_pa_l2_and_exit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Rich inline briefing must not bypass governed C0 readiness.",
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "missing")

    assert result.c0_invoked is True
    assert result.pa_invoked is False
    assert result.l2_executed is False
    manifest = _assert_c0_blocked(result.artifact_dir, STATUS_MISSING)
    assert manifest["c0_readiness_status"] == STATUS_MISSING
    assert manifest["c0_recipient_class_status"] == STATUS_MISSING
    assert manifest["source_snapshot_ids"] == []


@pytest.mark.parametrize(
    ("facts", "expected_status"),
    [
        (ready_governed_opportunity_facts(freshness_date="2000-01-01T00:00:00+00:00"), STATUS_STALE),
        (conflicted_governed_opportunity_facts(), STATUS_CONFLICTED),
        (
            [
                fact_packet(
                    namespace=NAMESPACE_CONTACT,
                    document_id="blocked-contact",
                    fact_text="Blocked public evidence source.",
                    metadata={"blocked": True},
                )
            ],
            STATUS_BLOCKED,
        ),
    ],
)
def test_w1_non_ready_governed_evidence_statuses_block_generation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    facts: list[dict],
    expected_status: str,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Inline campaign detail is present but cannot override C0.",
        governed_opportunity_facts=facts,
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / expected_status)

    manifest = _assert_c0_blocked(result.artifact_dir, expected_status)
    assert manifest["c0_readiness_status"] == expected_status
    assert manifest["evidence_support_status"] != "PASS"


def test_w1_ready_governed_facts_allow_pa_l2_and_record_readiness_receipts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Governed AIG recruiter facts are ready for role-specific outreach.",
        governed_opportunity_facts=ready_governed_opportunity_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "ready")

    assert result.pa_invoked is True
    assert result.l2_executed is True
    manifest = _load_json(result.artifact_dir, "spine_run_manifest.json")
    assert manifest["terminal_c0_block"] is False
    assert manifest["c0_readiness_status"] == STATUS_READY
    assert manifest["c0_recipient_class_status"] == STATUS_DERIVED
    assert manifest["derived_recipient_class"] != "UNKNOWN"
    assert len(manifest["source_snapshot_ids"]) >= 4
    assert (result.artifact_dir / "pa_receipt.json").is_file()
    assert (result.artifact_dir / "l2_execution_receipt.json").is_file()


def test_w1_ready_opportunity_but_low_confidence_recipient_blocks_pa(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APPS_LIC_TEST_PROVIDER_STUB", "1")
    raw = build_cli_ingress_raw(
        manual_brief="Opportunity facts exist but recipient type cannot be derived.",
        governed_opportunity_facts=low_confidence_recipient_facts(),
    )

    result = run_canonical_apps_lic_spine(raw, artifact_root=tmp_path / "low_conf")

    manifest = _assert_c0_blocked(result.artifact_dir, STATUS_LOW_CONFIDENCE)
    assert manifest["c0_readiness_status"] == STATUS_READY
    assert manifest["c0_recipient_class_status"] == STATUS_LOW_CONFIDENCE
    assert manifest["derived_recipient_class"] == "UNKNOWN"
