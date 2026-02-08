"""
Quarantine manifest governance contract.

Enforced invariants:
    1. Every test file under tests/_quarantine/ is listed in QUARANTINE_MANIFEST.json.
    2. The manifest has no stale entries (files listed but not on disk).
    3. Every entry has a valid category from the allowed enum.
    4. Every entry has non-empty primary_dep and re_enable fields.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit_min_deps

ROOT = Path(__file__).resolve().parents[2]
QUARANTINE_DIR = ROOT / "tests" / "_quarantine"
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
