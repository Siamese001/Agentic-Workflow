"""W4: correlated integrated cli_* runs → verified_external_refs (hash-only)."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from apps_rg.runtime.section_evidence_package import (
    CORRELATED_CLI_RUN_ENV,
    OWNER_VERIFIED_EXTERNAL_REF,
    REF_KIND_VERIFIED_EXTERNAL,
    W4_VERIFIED_EXTERNAL_ARTIFACTS,
    build_verified_external_refs_for_integrated,
    discover_integrated_correlation,
    finalize_section_evidence_package,
)
from apps_rg.runtime.section_l7_binding_manifest import build_section_l7_binding_manifest


def _write_trusted_l7_fixture(cli_dir: Path) -> None:
    (cli_dir / "agentic_core_how_trace.json").write_text(
        json.dumps(
            {
                "evidence_plane": "L7_AUDITABILITY",
                "runtime_subject": "agentic_core",
                "schema_version": "1.1",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (cli_dir / "agentic_core_l7_route_family_coverage.json").write_text(
        json.dumps(
            {
                "evidence_plane": "L7_AUDITABILITY",
                "evidence_class": "ROUTE_FAMILY_COVERAGE_MATRIX",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (cli_dir / "agentic_core_spine_proof.json").write_text(
        json.dumps(
            {"runtime_subject": "agentic_core", "proof_schema_version": "1.0.0"}
        )
        + "\n",
        encoding="utf-8",
    )
    (cli_dir / "integrated_runtime_artifact_manifest.json").write_text(
        json.dumps({"integrated_runtime_entrypoint_used": True}) + "\n",
        encoding="utf-8",
    )
    (cli_dir / "runtime_trace_snapshot.json").write_text(
        json.dumps({"producer_component": "agentic_core.runtime.emit"}) + "\n",
        encoding="utf-8",
    )
    (cli_dir / "RUN_BUNDLE_INDEX.json").write_text(
        json.dumps({"schema_version": "1", "entries": []}) + "\n",
        encoding="utf-8",
    )


def _section_run_layout(repo: Path, run_id: str = "exec_summary_w4") -> Path:
    ad = repo / "artifacts/apps_rg/runtime_proofs/executive_summary/real" / run_id
    ad.mkdir(parents=True)
    (repo / "artifacts/apps_rg/runs").mkdir(parents=True, exist_ok=True)
    (ad / "RUN_BUNDLE_INDEX.json").write_text(
        json.dumps(
            {
                "schema_version": "1",
                "run_id": run_id,
                "lane": "executive_summary",
                "root_path": f"artifacts/apps_rg/runtime_proofs/executive_summary/real/{run_id}",
                "entries": [],
            }
        ),
        encoding="utf-8",
    )
    return ad


def test_w4_env_correlates_and_populates_verified_external_refs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path
    section_ad = _section_run_layout(repo)
    cli = repo / "artifacts/apps_rg/runs/cli_w4_test"
    cli.mkdir(parents=True)
    _write_trusted_l7_fixture(cli)
    monkeypatch.setenv(CORRELATED_CLI_RUN_ENV, "cli_w4_test")

    corr = discover_integrated_correlation(repo, section_ad, section_id="executive_summary")
    assert corr.integrated_dir == cli
    assert corr.correlation_method == "env_APPS_RG_CORRELATED_CLI_RUN"
    assert corr.correlation_missing_reason is None

    refs = build_verified_external_refs_for_integrated(repo, cli, section_artifact_dir=section_ad)
    assert len(refs) >= len(W4_VERIFIED_EXTERNAL_ARTIFACTS)
    for ref in refs:
        assert ref["ref_kind"] == REF_KIND_VERIFIED_EXTERNAL
        assert ref["local_path"] is None
        assert ref["source_path"]
        assert ref["sha256"]
        assert ref["runtime_authority_claimed"] is False
        if ref["artifact_name"] in W4_VERIFIED_EXTERNAL_ARTIFACTS:
            assert ref["owner_class"] in (OWNER_VERIFIED_EXTERNAL_REF, "DRIFT")
            assert ref["owner_class"] != "APP_DOMAIN_EVIDENCE"


def test_w4_modular_pointer_correlates(tmp_path: Path) -> None:
    repo = tmp_path
    section_ad = _section_run_layout(repo, "exec_mod_ptr")
    section_rel = "artifacts/apps_rg/runtime_proofs/executive_summary/real/exec_mod_ptr"
    cli = repo / "artifacts/apps_rg/runs/cli_mod_ptr"
    cli.mkdir(parents=True)
    _write_trusted_l7_fixture(cli)
    ptr_dir = cli / "modular_r4/sections/executive_summary"
    ptr_dir.mkdir(parents=True)
    (ptr_dir / "latest_real_run.json").write_text(
        json.dumps({"run_dir": section_rel}) + "\n",
        encoding="utf-8",
    )

    corr = discover_integrated_correlation(repo, section_ad, section_id="executive_summary")
    assert corr.integrated_dir == cli
    assert corr.correlation_method == "modular_r4_latest_real_run_pointer"


def test_w4_uncorrelated_emits_correlation_missing_reason(tmp_path: Path) -> None:
    repo = tmp_path
    section_ad = _section_run_layout(repo, "exec_no_corr")
    binding = build_section_l7_binding_manifest(
        repo_root=repo,
        artifact_dir=section_ad,
        section_id="executive_summary",
        run_id="exec_no_corr",
    )
    summary = finalize_section_evidence_package(
        repo_root=repo,
        artifact_dir=section_ad,
        section_id="executive_summary",
        run_id="exec_no_corr",
        binding_manifest=binding,
    )
    pkg = json.loads(
        (section_ad / "evidence_package_index.json").read_text(encoding="utf-8")
    )
    assert pkg["verified_external_refs"] == []
    assert pkg["correlation_missing_reason"]
    assert "no correlated integrated cli_*" in pkg["correlation_missing_reason"]
    bind = json.loads(
        (section_ad / "section_l7_binding_manifest.json").read_text(encoding="utf-8")
    )
    assert bind.get("correlation_missing_reason")
    assert summary["correlation_missing_reason"]


def test_w4_does_not_copy_l7_into_section_folder(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path
    section_ad = _section_run_layout(repo, "exec_no_copy")
    cli = repo / "artifacts/apps_rg/runs/cli_no_copy"
    cli.mkdir(parents=True)
    _write_trusted_l7_fixture(cli)
    monkeypatch.setenv(CORRELATED_CLI_RUN_ENV, str(cli))

    binding = build_section_l7_binding_manifest(
        repo_root=repo,
        artifact_dir=section_ad,
        section_id="executive_summary",
        run_id="exec_no_copy",
    )
    finalize_section_evidence_package(
        repo_root=repo,
        artifact_dir=section_ad,
        section_id="executive_summary",
        run_id="exec_no_copy",
        binding_manifest=binding,
    )
    for name in W4_VERIFIED_EXTERNAL_ARTIFACTS:
        assert not (section_ad / name).is_file()


def test_w4_binding_manifest_99_and_cache_not_claimed(tmp_path: Path) -> None:
    repo = tmp_path
    section_ad = _section_run_layout(repo, "exec_claims")
    doc = build_section_l7_binding_manifest(
        repo_root=repo,
        artifact_dir=section_ad,
        section_id="executive_summary",
        run_id="exec_claims",
    )
    assert doc["runtime_proof_bundle_99_emitted"] is False
    non_claims = " ".join(doc.get("explicit_non_claims") or [])
    assert "99" in non_claims or "RuntimeProofBundle" in non_claims
    assert doc["design_law_owner_classifications"]["runtime_proof_bundle.json"] == "DESIGN_ONLY"
