"""
Quarantine manifest governance contract.

Enforced invariants:
    1. Every test file under tests/_quarantine/ is listed in QUARANTINE_MANIFEST.json.
    2. The manifest has no stale entries (files listed but not on disk).
    3. Every entry has a valid category from the allowed enum.
    4. Every entry has non-empty primary_dep and re_enable fields.
    5. Total quarantine count must not exceed the declared ceiling.
    6. Per-category counts must not exceed their declared ceilings.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import TESTS_DIR

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]
QUARANTINE_DIR = ROOT / TESTS_DIR / "_quarantine"
MANIFEST_PATH = QUARANTINE_DIR / "QUARANTINE_MANIFEST.json"

VALID_CATEGORIES = frozenset(
    {
        "missing_dep",
        "missing_module",
        "assertion_rot",
        "infra_required",
        "runtime_error",
    },
)


def _load_manifest() -> dict:
    """Load and parse the quarantine manifest."""
    assert MANIFEST_PATH.exists(), (
        f"QUARANTINE_MANIFEST.json not found at {MANIFEST_PATH}.\n"
        "Quarantine governance requires a manifest. See docs/testing/TEST_CONTRACT.md."
    )
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _get_disk_files() -> set[str]:
    """Return set of test_*.py paths under _quarantine, relative to repo root, forward-slash."""
    result = set()
    for f in QUARANTINE_DIR.rglob("test_*.py"):
        rel = f.relative_to(ROOT)
        result.add(str(rel).replace("\\", "/"))
    return result


def _get_manifest_paths(manifest: dict) -> set[str]:
    """Return set of paths declared in the manifest."""
    return {entry["path"] for entry in manifest["entries"]}


class TestManifestCompleteness:
    """Every quarantined test file must be listed in the manifest."""

    def test_no_unlisted_quarantine_files(self) -> None:
        manifest = _load_manifest()
        on_disk = _get_disk_files()
        in_manifest = _get_manifest_paths(manifest)
        unlisted = on_disk - in_manifest
        assert not unlisted, (
            f"Found {len(unlisted)} quarantined test file(s) NOT in manifest:\n"
            + "\n".join(f"  {p}" for p in sorted(unlisted))
            + "\nUpdate QUARANTINE_MANIFEST.json before adding files to _quarantine."
        )


class TestManifestNoStaleEntries:
    """Manifest must not reference files that no longer exist on disk."""

    def test_no_stale_manifest_entries(self) -> None:
        manifest = _load_manifest()
        on_disk = _get_disk_files()
        in_manifest = _get_manifest_paths(manifest)
        stale = in_manifest - on_disk
        assert not stale, (
            f"Found {len(stale)} stale manifest entries (file not on disk):\n"
            + "\n".join(f"  {p}" for p in sorted(stale))
            + "\nRemove these entries from QUARANTINE_MANIFEST.json."
        )


class TestManifestEntrySchema:
    """Every manifest entry must have valid category, primary_dep, and re_enable."""

    def test_categories_are_valid(self) -> None:
        manifest = _load_manifest()
        invalid = []
        for entry in manifest["entries"]:
            cat = entry.get("category", "")
            if cat not in VALID_CATEGORIES:
                invalid.append(f"  {entry['path']}: category={cat!r}")
        assert not invalid, (
            f"Found {len(invalid)} entries with invalid category:\n"
            + "\n".join(invalid)
            + f"\nValid categories: {sorted(VALID_CATEGORIES)}"
        )

    def test_required_fields_non_empty(self) -> None:
        manifest = _load_manifest()
        bad = []
        for entry in manifest["entries"]:
            for field in ("path", "category", "primary_dep", "re_enable"):
                val = entry.get(field, "")
                if not val or not val.strip():
                    bad.append(f"  {entry.get('path', '???')}: {field} is empty")
        assert not bad, f"Found {len(bad)} entries with empty required fields:\n" + "\n".join(bad)

    def test_governance_fields_present(self) -> None:
        manifest = _load_manifest()
        bad = []
        for entry in manifest["entries"]:
            for field in ("introduced_commit", "owner_agent"):
                val = entry.get(field, "")
                if not val or not val.strip():
                    bad.append(f"  {entry.get('path', '???')}: {field} is missing or empty")
        assert not bad, (
            f"Found {len(bad)} entries missing governance fields (introduced_commit/owner_agent):\n"
            + "\n".join(bad)
            + "\nBackfill using: python ops_scripts/general/backfill_quarantine_governance.py"
        )


class TestManifestBidirectionalSync:
    """Disk and manifest must be in exact 1:1 correspondence."""

    def test_disk_manifest_exact_match(self) -> None:
        manifest = _load_manifest()
        on_disk = _get_disk_files()
        in_manifest = _get_manifest_paths(manifest)
        assert on_disk == in_manifest, (
            f"Disk/manifest mismatch.\n"
            f"  On disk only: {sorted(on_disk - in_manifest)}\n"
            f"  In manifest only: {sorted(in_manifest - on_disk)}"
        )


# ---------------------------------------------------------------------------
# 5-6. Non-increasing quarantine ceilings
# ---------------------------------------------------------------------------


class TestQuarantineCeiling:
    """Quarantine count must not exceed declared ceilings (total + per-category)."""

    def test_total_ceiling(self) -> None:
        manifest = _load_manifest()
        ceiling = manifest.get("ceiling", {})
        total_ceiling = ceiling.get("total")
        assert total_ceiling is not None, "Manifest missing ceiling.total. Add a ceiling section."
        actual = len(manifest["entries"])
        assert actual <= total_ceiling, (
            f"Quarantine total ceiling breached: {actual} > {total_ceiling}.\n"
            "To raise: update ceiling.total in QUARANTINE_MANIFEST.json + add rationale to commit message."
        )

    def test_per_category_ceiling(self) -> None:
        manifest = _load_manifest()
        ceiling = manifest.get("ceiling", {})
        by_category = ceiling.get("by_category", {})
        assert by_category, "Manifest missing ceiling.by_category. Add per-category ceilings."

        from collections import Counter

        actual_counts = Counter(e["category"] for e in manifest["entries"])
        breaches: list[str] = []
        for cat, count in sorted(actual_counts.items()):
            cat_ceiling = by_category.get(cat)
            if cat_ceiling is None:
                breaches.append(f"  {cat}: no ceiling defined (count={count})")
            elif count > cat_ceiling:
                breaches.append(f"  {cat}: {count} > {cat_ceiling}")

        assert not breaches, (
            "Per-category quarantine ceiling breached:\n"
            + "\n".join(breaches)
            + "\nTo raise: update ceiling.by_category in QUARANTINE_MANIFEST.json + add rationale to commit message."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
