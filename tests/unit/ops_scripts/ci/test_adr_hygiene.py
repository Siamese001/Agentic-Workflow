"""Tests for ADR liveness inventory and hygiene checks."""

from __future__ import annotations

from ops_scripts.ci import check_adr_hygiene as hygiene
from ops_scripts.ci import inventory_adr_liveness as inventory


def _record(
    path: str,
    *,
    location: str = "canonical",
    number: str | None = None,
    status: str | None = "Accepted",
) -> inventory.AdrRecord:
    return inventory.AdrRecord(
        path=path,
        location=location,
        number=number,
        status=status,
        duplicate_group_size=0,
        inbound_reference_count=0,
        active_reference_count=0,
        active_references=[],
        stale_markers=[],
        liveness="unbound_review",
    )


def test_extract_number_normalizes_zero_padded_names() -> None:
    assert inventory.extract_number(inventory.Path("ADR-081-example.md")) == "ADR-081"
    assert inventory.extract_number(inventory.Path("adr-0042-skills.md")) == "ADR-042"
    assert inventory.extract_number(inventory.Path("ADR-PROMPT-ASSEMBLY.md")) is None


def test_extract_status_handles_bulleted_bold_status() -> None:
    text = "# ADR\n\n- **Status:** ACCEPTED\n"
    assert inventory.extract_status(text) == "ACCEPTED"


def test_active_references_ignores_own_allowlist_files() -> None:
    refs = inventory.active_references(
        [
            "ops_scripts/ci/check_adr_hygiene.py",
            "ops_scripts/ci/inventory_adr_liveness.py",
            "ops_scripts/ci/check_apps_folder_taxonomy.py",
            "docs/architecture/adr/README.md",
        ]
    )
    assert refs == ["ops_scripts/ci/check_apps_folder_taxonomy.py"]


def test_liveness_marks_stale_unbound_canonical_as_historical() -> None:
    assert inventory.classify_liveness("canonical", active_count=0, stale_count=1) == "historical_stale_marker"
    assert inventory.classify_liveness("canonical", active_count=1, stale_count=1) == "live_bound"
    assert inventory.classify_liveness("legacy_docs_adr", active_count=0, stale_count=0) == "noncanonical"


def test_hygiene_flags_new_noncanonical_file() -> None:
    findings = hygiene.evaluate_hygiene(
        [
            _record(
                "docs/adr/ADR-999-new.md",
                location="legacy_docs_adr",
                number="ADR-999",
            )
        ]
    )
    assert len(findings) == 1
    assert findings[0].rule == "new_noncanonical_adr"
    assert findings[0].severity == "error"


def test_hygiene_known_duplicate_is_warning() -> None:
    findings = hygiene.evaluate_hygiene(
        [
            _record("docs/architecture/adr/ADR-081-a.md", number="ADR-081"),
            _record("docs/architecture/adr/ADR-081-b.md", number="ADR-081"),
        ]
    )
    assert len(findings) == 1
    assert findings[0].rule == "duplicate_adr_number"
    assert findings[0].severity == "warning"


def test_hygiene_new_duplicate_is_error() -> None:
    findings = hygiene.evaluate_hygiene(
        [
            _record("docs/architecture/adr/ADR-777-a.md", number="ADR-777"),
            _record("docs/architecture/adr/ADR-777-b.md", number="ADR-777"),
        ]
    )
    assert len(findings) == 1
    assert findings[0].rule == "duplicate_adr_number"
    assert findings[0].severity == "error"


def test_hygiene_warns_on_missing_canonical_status() -> None:
    findings = hygiene.evaluate_hygiene(
        [_record("docs/architecture/adr/ADR-777-a.md", number="ADR-777", status=None)]
    )
    assert len(findings) == 1
    assert findings[0].rule == "canonical_status_missing"
    assert findings[0].severity == "warning"
