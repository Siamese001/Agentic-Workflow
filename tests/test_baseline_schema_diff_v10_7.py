import json
from pathlib import Path


# Paths are relative to this test file.
HERE = Path(__file__).resolve().parent
PREVIOUS_BASELINE = HERE / "baseline_outputs_previous.json"
V10_7_BASELINE = HERE / "baseline_outputs_v10_7.json"


def _load_baseline(path: Path) -> dict:
    assert path.exists(), f"Baseline file not found: {path}"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_baseline_files_exist():
    """
    Sanity check so a missing baseline file fails with a clear message,
    not a cryptic JSON/IO error.
    """
    assert PREVIOUS_BASELINE.exists(), f"Missing: {PREVIOUS_BASELINE}"
    assert V10_7_BASELINE.exists(), f"Missing: {V10_7_BASELINE}"


def test_top_level_sections_preserved():
    """
    API envelope invariant:
    All top-level sections that existed previously must still exist in v10.7.

    Example from your baselines:
      previous: {"strategy": {...}, "qa": {...}}
      v10.7:    {"strategy": {...}, "qa": {...}}
    """
    prev = _load_baseline(PREVIOUS_BASELINE)
    new = _load_baseline(V10_7_BASELINE)

    prev_keys = set(prev.keys())
    new_keys = set(new.keys())

    # No top-level section is allowed to disappear.
    missing = prev_keys - new_keys
    assert not missing, f"Top-level sections missing in v10.7: {sorted(missing)}"

    # Optional: you can assert no unexpected NEW top-level sections if desired:
    # extra = new_keys - prev_keys
    # assert not extra, f"Unexpected new top-level sections in v10.7: {sorted(extra)}"


def test_strategy_schema_evolution_superset():
    """
    Strategy schema evolution:

    previous:
      "strategy": {
        "fields": ["steps", "goal"],
        "version": "legacy"
      }

    v10.7:
      "strategy": {
        "fields": ["steps", "goal", "context"],
        "version": "v10.7",
        ...
      }

    Invariants:
      - All previous fields are still present.
      - New fields may be added (e.g., "context").
      - Version must change (no accidental reuse of "legacy").
    """
    prev = _load_baseline(PREVIOUS_BASELINE)["strategy"]
    new = _load_baseline(V10_7_BASELINE)["strategy"]

    prev_fields = set(prev.get("fields", []))
    new_fields = set(new.get("fields", []))

    # Superset guarantee: no field loss.
    missing_fields = prev_fields - new_fields
    assert not missing_fields, (
        f"v10.7 'strategy.fields' is missing fields from previous baseline: "
        f"{sorted(missing_fields)}"
    )

    # Explicitly assert the new field you introduced.
    assert "context" in new_fields, (
        "v10.7 'strategy.fields' must include the new 'context' field"
    )

    # Version should reflect the new implementation.
    assert prev.get("version") != new.get("version"), (
        "Strategy version did not change between previous and v10.7 baselines"
    )


def test_qa_schema_evolution_superset():
    """
    QA schema evolution:

    previous:
      "qa": {
        "fields": ["confidence", "summary"],
        "version": "legacy"
      }

    v10.7:
      "qa": {
        "fields": ["confidence", "summary", "issues"],
        "version": "v10.7",
        ...
      }

    Invariants:
      - All previous fields are still present.
      - New 'issues' field is required in v10.7.
      - Version must change.
    """
    prev = _load_baseline(PREVIOUS_BASELINE)["qa"]
    new = _load_baseline(V10_7_BASELINE)["qa"]

    prev_fields = set(prev.get("fields", []))
    new_fields = set(new.get("fields", []))

    # Superset guarantee: no field loss.
    missing_fields = prev_fields - new_fields
    assert not missing_fields, (
        f"v10.7 'qa.fields' is missing fields from previous baseline: "
        f"{sorted(missing_fields)}"
    )

    # Explicitly assert the new field you introduced.
    assert "issues" in new_fields, (
        "v10.7 'qa.fields' must include the new 'issues' field"
    )

    # Version must change to signal evolution.
    assert prev.get("version") != new.get("version"), (
        "QA version did not change between previous and v10.7 baselines"
    )


def test_no_contract_regression_on_fields():
    """
    Global contract check:

    For every top-level section that has a 'fields' array in the previous
    baseline, ensure that:

      - v10.7 still has that section
      - v10.7 still has all of those fields (superset)
    """
    prev = _load_baseline(PREVIOUS_BASELINE)
    new = _load_baseline(V10_7_BASELINE)

    for section_name, prev_section in prev.items():
        prev_fields = set(prev_section.get("fields", []))
        if not prev_fields:
            # Section without a 'fields' array; nothing to enforce here.
            continue

        assert section_name in new, (
            f"Section '{section_name}' missing from v10.7 baseline"
        )
        new_section = new[section_name]
        new_fields = set(new_section.get("fields", []))

        missing = prev_fields - new_fields
        assert not missing, (
            f"Section '{section_name}' in v10.7 is missing fields from previous "
            f"baseline: {sorted(missing)}"
        )
