"""W3: `bootstrap fact-vectors` builds C0.2 fact_vectors from tracked sources.

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

Dry-run / unit coverage of the bootstrap: ledger + canonical base-resume employment sourcing,
generated-lane assignment, all-11 lane hydration, manifest shape + deterministic checksum, and strict
fail-loud on an empty or partially hydrated build. The live build + the doctor round-trip (absent ->
present) are proven separately. Pure product-mode test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime import fact_vectors_bootstrap as fvb
from apps_rg.runtime.cli_exit_codes import EXIT_GENERIC_FAILURE, EXIT_SUCCESS


@pytest.fixture
def _no_side_effects(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        fvb,
        "_write_manifest",
        lambda root, manifest, *, dry_run=False, blocked=False: Path(
            "fact_vectors_bootstrap_dry_run_manifest.json"
            if dry_run
            else "fact_vectors_bootstrap_blocked_manifest.json"
            if blocked
            else "fact_vectors_bootstrap_manifest.json"
        ),
    )


def test_assign_sections_employer_lanes_and_cross_section() -> None:
    ibm = fvb.assign_sections_for_fact({"company": "IBM"})
    assert "ibm_bullets" in ibm and "ibm_narrative" in ibm
    assert "competencies" in ibm  # cross-section enrichment
    assert "unify_bullets" in fvb.assign_sections_for_fact({"company": "Unify Platform"})
    assert "insurtech_bullets" in fvb.assign_sections_for_fact({"company": "InsurTech"})
    assert "ey_bullets" in fvb.assign_sections_for_fact({"company": "Ernst & Young"})
    role = fvb.assign_sections_for_fact({"role_families_supported": ["ENGINEERING_PLATFORM"]})
    assert "unify_bullets" in role


def test_no_generated_lane_is_excluded_from_fact_vector_hydration() -> None:
    assert fvb.LOCKED_DETERMINISTIC_LANES == ()
    assert len(fvb.GENERATED_LANES) == 11


def test_build_section_atoms_sources_tracked_ledger() -> None:
    atoms, summary = fvb.build_section_atoms()
    assert summary["eligible_atoms"] > 0
    assert "candidate_fact_ledger" in summary["ledger_path"] or summary["ledger_path"].endswith(".json")
    # Every generated lane is represented in the manifest, even if ledger-only counts are zero.
    assert set(summary["per_section_target_counts"]) == set(fvb.GENERATED_LANES)
    assert summary["per_section_target_counts"]["competencies"] > 0


def test_base_resume_employment_atoms_hydrate_all_employer_sections() -> None:
    atoms, summary = fvb.build_base_resume_employment_atoms()
    assert atoms
    counts = summary["base_resume_per_section_counts"]
    for lane in (
        "unify_bullets",
        "ibm_bullets",
        "insurtech_bullets",
        "ey_bullets",
        "unify_narrative",
        "ibm_narrative",
        "insurtech_narrative",
        "ey_narrative",
    ):
        assert counts[lane] > 0


def test_dry_run_manifest_shape_and_strict_pass(_no_side_effects) -> None:
    manifest, code = fvb.run_bootstrap_fact_vectors(
        strict=True, dry_run=True, timestamp="2026-06-08T00:00:00Z"
    )
    assert code == EXIT_SUCCESS
    assert manifest["schema_version"] == "apps_rg.fact_vectors_bootstrap_manifest.v1"
    assert manifest["dry_run"] is True
    assert manifest["collection_count_after"] is None  # dry run writes nothing
    assert set(manifest["per_section_target_counts"]) == set(fvb.GENERATED_LANES)
    assert manifest["locked_deterministic_lanes"] == list(fvb.LOCKED_DETERMINISTIC_LANES)
    assert manifest["required_lanes"] == list(fvb.GENERATED_LANES)
    assert manifest["missing_required_lane_targets"] == []
    assert len(manifest["manifest_checksum"]) == 64
    assert "base_resume_employment_bullets" in manifest["source"]
    assert "generated output is never" in manifest["source"]
    assert manifest["base_resume_employment_atoms"] > 0
    assert manifest["ledger_version_hash"]
    assert manifest["manifest_path"].endswith("fact_vectors_bootstrap_dry_run_manifest.json")


def test_non_dry_runtime_block_falls_back_to_existing_index(
    _no_side_effects,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fvb,
        "validate_fact_vector_hydration_runtime",
        lambda **kwargs: {
            "status": "BLOCKED",
            "block_code": "BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME",
            "reasons": ["missing_or_blocked_dependency:torch"],
        },
    )
    monkeypatch.setattr(
        fvb,
        "_existing_index_fallback_receipt",
        lambda **kwargs: {
            "decision": "USED_EXISTING_FACT_VECTOR_INDEX",
            "readiness": {
                "status": "PASS",
                "summary": {
                    "collection_doc_count": 60,
                    "sparse_sidecar_doc_count": 41,
                },
            },
        },
    )

    manifest, code = fvb.run_bootstrap_fact_vectors(
        strict=True,
        dry_run=False,
        timestamp="2026-06-08T00:00:00Z",
    )

    assert code == EXIT_SUCCESS
    assert manifest["status"] == "FALLBACK_ALLOWED"
    assert manifest["fallback_mode"] == "existing_dense_sparse_fact_vectors_index"
    assert manifest["collection_count_after"] == 60
    assert manifest["sparse_sidecar_built"] is True


def test_non_dry_runtime_block_can_disable_fallback(
    _no_side_effects,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        fvb,
        "validate_fact_vector_hydration_runtime",
        lambda **kwargs: {
            "status": "BLOCKED",
            "block_code": "BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME",
            "reasons": ["missing_or_blocked_dependency:torch"],
        },
    )

    manifest, code = fvb.run_bootstrap_fact_vectors(
        strict=True,
        dry_run=False,
        timestamp="2026-06-08T00:00:00Z",
        allow_existing_index_fallback=False,
    )

    assert code == EXIT_GENERIC_FAILURE
    assert manifest["status"] == "BLOCKED"
    assert manifest["block_code"] == "BLOCKED_FACT_VECTOR_HYDRATION_RUNTIME"


def test_strict_fails_loud_on_zero_eligible_atoms(_no_side_effects, monkeypatch) -> None:
    empty_summary = {
        "ledger_path": "x",
        "total_ledger_facts": 0,
        "eligible_atoms": 0,
        "skipped_count": 0,
        "skipped": [],
        "per_section_target_counts": {lane: 0 for lane in fvb.GENERATED_LANES},
    }
    empty_base_summary = {
        "base_resume_path": "",
        "base_resume_digest": "",
        "base_resume_employment_atoms": 0,
        "base_resume_skipped": [],
        "base_resume_per_section_counts": {lane: 0 for lane in fvb.GENERATED_LANES},
    }
    monkeypatch.setattr(fvb, "build_section_atoms", lambda **kwargs: ([], empty_summary))
    monkeypatch.setattr(
        fvb,
        "build_base_resume_employment_atoms",
        lambda **kwargs: ([], empty_base_summary),
    )
    _manifest, code = fvb.run_bootstrap_fact_vectors(strict=True, dry_run=True, timestamp="t")
    assert code == EXIT_GENERIC_FAILURE


def test_manifest_checksum_is_deterministic(_no_side_effects) -> None:
    first, _ = fvb.run_bootstrap_fact_vectors(strict=False, dry_run=True, timestamp="2026-06-08T00:00:00Z")
    second, _ = fvb.run_bootstrap_fact_vectors(strict=False, dry_run=True, timestamp="2026-06-08T00:00:00Z")
    assert first["manifest_checksum"] == second["manifest_checksum"]


def test_main_dispatches_bootstrap(monkeypatch) -> None:
    import apps_rg.__main__ as entry

    monkeypatch.setattr("apps_rg.runtime.fact_vectors_bootstrap.run_bootstrap_cli", lambda argv: 0)
    assert entry.main(["bootstrap", "fact-vectors", "--strict"]) == 0
