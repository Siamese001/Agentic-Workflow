"""W4 (AIG E2E remediation, E2E-07/E2E-08) — competency bundle coverage + empty-selection guard.

Deterministic, hermetic. No provider calls. Guards the two data/diagnostic invariants:

1. Coverage invariant: every taxonomy category_id in executive_capability_taxonomy.yaml is the
   target of >=1 competency bundle (no orphaned category — the llmops_reliability orphan that
   produced the AIG competencies X2 gap).
2. E2E-08: competencies_pool_x1d_judge_rows emits an explicit BLOCKED/diagnostic row (not a
   silent score=0.0 model-quality-looking failure) when the selection input is empty/absent.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
BUNDLES = REPO / "apps_rg" / "fact_inventory" / "competency_capability_bundles.json"
TAXONOMY = REPO / "apps_rg" / "config" / "competencies" / "executive_capability_taxonomy.yaml"


def _taxonomy_category_ids() -> set[str]:
    doc = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))
    acc: list[str] = []

    def walk(o: object) -> None:
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("category_id", "id") and isinstance(v, str):
                    acc.append(v)
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(doc)
    return set(acc)


def _bundle_covered_category_ids() -> set[str]:
    doc = json.loads(BUNDLES.read_text(encoding="utf-8"))
    covered: set[str] = set()
    for b in doc.get("bundles", []):
        covered.update(str(c) for c in (b.get("target_taxonomy_category_ids") or []))
    return covered


def test_every_taxonomy_category_is_targeted_by_a_bundle() -> None:
    """No orphaned taxonomy category (the E2E-07 llmops_reliability gap)."""
    cats = _taxonomy_category_ids()
    covered = _bundle_covered_category_ids()
    assert cats, "taxonomy yielded no category_ids — fixture/path drift"
    orphans = sorted(cats - covered)
    assert not orphans, (
        f"taxonomy categories with no competency bundle target: {orphans} — "
        "every category_id must appear in >=1 bundle's target_taxonomy_category_ids"
    )


def test_llmops_reliability_category_is_covered() -> None:
    """Regression pin for the specific orphan this wave closed."""
    assert "llmops_reliability" in _bundle_covered_category_ids()


def test_bundles_json_is_valid_and_nonempty() -> None:
    doc = json.loads(BUNDLES.read_text(encoding="utf-8"))
    assert isinstance(doc.get("bundles"), list) and doc["bundles"], "bundles missing/empty"


def test_empty_selection_emits_blocked_diagnostic_row(tmp_path: Path) -> None:
    """E2E-08: empty/absent selection -> explicit BLOCKED_NO_SELECTION diagnostic, not silent 0."""
    from apps_rg.runtime.reasoning.employment_bullet_pool import competencies_pool_x1d_judge_rows

    # No bullet_pool_selection.json in tmp_path => empty selection input.
    rows = competencies_pool_x1d_judge_rows(
        artifact_dir=tmp_path, section_id="competencies", gen_meta={}
    )
    assert len(rows) == 1
    row = rows[0]
    assert row.get("empty_selection") is True
    assert row.get("provider_status") == "BLOCKED_NO_SELECTION"
    assert row.get("diagnostic_reason") == "no_selection_input_artifact"
    assert row.get("pass") is False and row.get("pass_") is False
    # The finding must name the upstream cause, not read as a model-quality failure.
    joined = " ".join(str(f) for f in (row.get("findings") or []))
    assert "selector" in joined.lower() and "not a model-quality" in joined.lower()


def test_empty_selection_file_present_but_no_rows(tmp_path: Path) -> None:
    """Selection artifact present but zero selections -> selector_returned_no_candidates."""
    from apps_rg.runtime.reasoning.employment_bullet_pool import competencies_pool_x1d_judge_rows

    (tmp_path / "bullet_pool_selection.json").write_text(
        json.dumps({"selections": []}), encoding="utf-8"
    )
    rows = competencies_pool_x1d_judge_rows(
        artifact_dir=tmp_path, section_id="competencies", gen_meta={}
    )
    row = rows[0]
    assert row.get("empty_selection") is True
    assert row.get("diagnostic_reason") == "selector_returned_no_candidates"
    assert row.get("selection_file_present") is True
