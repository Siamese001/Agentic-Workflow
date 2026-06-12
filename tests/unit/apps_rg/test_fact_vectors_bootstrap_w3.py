"""W3: `bootstrap fact-vectors` builds C0.2 fact_vectors from the tracked ledger (G2/G3/G10/G14).

Plan: apps-rg-e2e-gap-remediation-7e2d9c.

Dry-run / unit coverage of the bootstrap: ledger-only sourcing (never base resume), generated-lane
assignment, locked EY/InsurTech exclusion, manifest shape + deterministic checksum, and strict
fail-loud on an empty build. The live build + the doctor round-trip (absent -> present) are proven
separately. Pure product-mode test.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime import fact_vectors_bootstrap as fvb
from apps_rg.runtime.cli_exit_codes import EXIT_GENERIC_FAILURE, EXIT_SUCCESS


@pytest.fixture
def _no_side_effects(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(fvb, "_write_manifest", lambda root, manifest: Path("dummy_manifest.json"))
    monkeypatch.setattr(
        "apps_rg.runtime.embedding_settings.bootstrap_apps_rg_embedding_env",
        lambda **kwargs: {},
    )


def test_assign_sections_ibm_unify_and_cross_section() -> None:
    ibm = fvb.assign_sections_for_fact({"company": "IBM"})
    assert "ibm_bullets" in ibm and "ibm_narrative" in ibm
    assert "competencies" in ibm  # cross-section enrichment
    assert "unify_bullets" in fvb.assign_sections_for_fact({"company": "Unify Platform"})
    role = fvb.assign_sections_for_fact({"role_families_supported": ["ENGINEERING_PLATFORM"]})
    assert "unify_bullets" in role


def test_locked_ey_insurtech_lanes_never_assigned() -> None:
    assert not (set(fvb.GENERATED_LANES) & set(fvb.LOCKED_DETERMINISTIC_LANES))
    for company in ("EY", "InsurTech Co", "Ernst & Young"):
        assigned = set(fvb.assign_sections_for_fact({"company": company}))
        assert not (assigned & set(fvb.LOCKED_DETERMINISTIC_LANES))


def test_build_section_atoms_sources_tracked_ledger() -> None:
    atoms, summary = fvb.build_section_atoms()
    assert summary["eligible_atoms"] > 0
    assert "candidate_fact_ledger" in summary["ledger_path"] or summary["ledger_path"].endswith(".json")
    # Every generated lane is represented in the manifest; locked lanes never appear.
    assert set(summary["per_section_target_counts"]) == set(fvb.GENERATED_LANES)
    assert summary["per_section_target_counts"]["competencies"] > 0
    for locked in fvb.LOCKED_DETERMINISTIC_LANES:
        assert locked not in summary["per_section_target_counts"]


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
    assert len(manifest["manifest_checksum"]) == 64
    assert "base resume is NOT a source" in manifest["source"]
    assert manifest["ledger_version_hash"]


def test_strict_fails_loud_on_zero_eligible_atoms(_no_side_effects, monkeypatch) -> None:
    empty_summary = {
        "ledger_path": "x",
        "total_ledger_facts": 0,
        "eligible_atoms": 0,
        "skipped_count": 0,
        "skipped": [],
        "per_section_target_counts": {lane: 0 for lane in fvb.GENERATED_LANES},
    }
    monkeypatch.setattr(fvb, "build_section_atoms", lambda **kwargs: ([], empty_summary))
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
