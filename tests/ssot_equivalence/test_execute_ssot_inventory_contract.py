"""Phase 1 — Inventory + bucket map contract tests.

Assertions:
- Inventory JSON exists and is valid JSON list.
- All entries have required keys and types.
- Bucket map covers 100% of inventory qualnames.
- No bucket == "TBD" and no parity_requirement == "TBD".
- No duplicate qualname keys.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

INVENTORY_PATH = REPO_ROOT / "docs" / "specs" / "execute_ssot_inventory.json"
BUCKET_MAP_PATH = REPO_ROOT / "docs" / "specs" / "execute_ssot_bucket_map.json"

VALID_KINDS = {"function", "class", "method", "constant"}
VALID_BUCKETS = {
    "L5_GUARDIAN",
    "L3_HIL",
    "L2_HEALER_PIPE",
    "L0_ROUTER",
    "L6_OBSERVABILITY",
    "CI_GATE",
    "RETIRED",
}
VALID_BEHAVIOR_TYPES = {"detection", "remediation", "control", "artifact"}
VALID_PARITY = {"REQUIRED", "ALLOWED_DELTA"}

REQUIRED_INVENTORY_KEYS = {
    "kind",
    "name",
    "qualname",
    "lineno",
    "end_lineno",
    "writes_repo",
    "side_effects",
}

REQUIRED_BUCKET_MAP_KEYS = {
    "qualname",
    "bucket",
    "behavior_type",
    "replacement_target",
    "replacement_artifact",
    "parity_requirement",
    "notes",
}


def _load_json(path: Path) -> list:
    assert path.exists(), f"File not found: {path}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list), f"Expected JSON list, got {type(data).__name__}"
    return data


# ── Inventory tests ──────────────────────────────────────────────


def test_inventory_exists_and_is_nonempty():
    data = _load_json(INVENTORY_PATH)
    assert len(data) > 0, "Inventory is empty"


def test_inventory_entries_have_required_keys():
    data = _load_json(INVENTORY_PATH)
    for i, entry in enumerate(data):
        missing = REQUIRED_INVENTORY_KEYS - set(entry.keys())
        assert not missing, f"Entry {i} ({entry.get('qualname', '?')}) missing keys: {missing}"


def test_inventory_kinds_are_valid():
    data = _load_json(INVENTORY_PATH)
    for entry in data:
        assert entry["kind"] in VALID_KINDS, f"{entry['qualname']}: invalid kind '{entry['kind']}'"


def test_inventory_lineno_types():
    data = _load_json(INVENTORY_PATH)
    for entry in data:
        assert isinstance(entry["lineno"], int), f"{entry['qualname']}: lineno must be int"
        assert isinstance(entry["end_lineno"], int), f"{entry['qualname']}: end_lineno must be int"
        assert entry["end_lineno"] >= entry["lineno"], f"{entry['qualname']}: end_lineno < lineno"


def test_inventory_no_duplicate_qualnames():
    data = _load_json(INVENTORY_PATH)
    qualnames = [e["qualname"] for e in data]
    dupes = [q for q in qualnames if qualnames.count(q) > 1]
    assert not dupes, f"Duplicate qualnames: {sorted(set(dupes))}"


def test_inventory_writes_repo_types():
    data = _load_json(INVENTORY_PATH)
    for entry in data:
        wr = entry["writes_repo"]
        assert wr in (True, False, "unknown"), (
            f"{entry['qualname']}: writes_repo must be bool or 'unknown', got {wr!r}"
        )
        se = entry["side_effects"]
        assert se in (True, False, "unknown"), (
            f"{entry['qualname']}: side_effects must be bool or 'unknown', got {se!r}"
        )


# ── Bucket map tests ─────────────────────────────────────────────


def test_bucket_map_exists_and_is_nonempty():
    data = _load_json(BUCKET_MAP_PATH)
    assert len(data) > 0, "Bucket map is empty"


def test_bucket_map_entries_have_required_keys():
    data = _load_json(BUCKET_MAP_PATH)
    for i, entry in enumerate(data):
        missing = REQUIRED_BUCKET_MAP_KEYS - set(entry.keys())
        assert not missing, f"Entry {i} ({entry.get('qualname', '?')}) missing keys: {missing}"


def test_bucket_map_buckets_are_valid():
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        assert entry["bucket"] in VALID_BUCKETS, f"{entry['qualname']}: invalid bucket '{entry['bucket']}'"


def test_bucket_map_no_tbd_bucket():
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        assert entry["bucket"] != "TBD", f"{entry['qualname']}: bucket must not be TBD"


def test_bucket_map_no_tbd_parity():
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        assert entry["parity_requirement"] != "TBD", (
            f"{entry['qualname']}: parity_requirement must not be TBD"
        )


def test_bucket_map_parity_values_are_valid():
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        assert entry["parity_requirement"] in VALID_PARITY, (
            f"{entry['qualname']}: invalid parity '{entry['parity_requirement']}'"
        )


def test_bucket_map_behavior_types_are_valid():
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        assert entry["behavior_type"] in VALID_BEHAVIOR_TYPES, (
            f"{entry['qualname']}: invalid behavior_type '{entry['behavior_type']}'"
        )


def test_bucket_map_no_duplicate_qualnames():
    data = _load_json(BUCKET_MAP_PATH)
    qualnames = [e["qualname"] for e in data]
    dupes = [q for q in qualnames if qualnames.count(q) > 1]
    assert not dupes, f"Duplicate qualnames: {sorted(set(dupes))}"


def test_allowed_delta_entries_have_notes():
    """Every ALLOWED_DELTA entry must have a non-empty notes field."""
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        if entry["parity_requirement"] == "ALLOWED_DELTA":
            notes = entry.get("notes", "")
            assert notes and notes.strip(), f"{entry['qualname']}: ALLOWED_DELTA entry missing notes"


def test_allowed_delta_notes_max_10_words():
    """ALLOWED_DELTA notes must be <= 10 words."""
    data = _load_json(BUCKET_MAP_PATH)
    for entry in data:
        if entry["parity_requirement"] == "ALLOWED_DELTA":
            word_count = len(entry["notes"].split())
            assert word_count <= 10, (
                f"{entry['qualname']}: ALLOWED_DELTA notes has {word_count} words "
                f"(max 10): {entry['notes']!r}"
            )


# ── Cross-reference tests ────────────────────────────────────────


def test_bucket_map_covers_all_inventory():
    """Every inventory qualname must appear in the bucket map."""
    inv = _load_json(INVENTORY_PATH)
    bm = _load_json(BUCKET_MAP_PATH)
    inv_qualnames = {e["qualname"] for e in inv}
    bm_qualnames = {e["qualname"] for e in bm}
    missing = inv_qualnames - bm_qualnames
    assert not missing, f"{len(missing)} inventory entries not in bucket map: {sorted(missing)}"


def test_bucket_map_has_no_extras():
    """Bucket map must not contain qualnames absent from inventory."""
    inv = _load_json(INVENTORY_PATH)
    bm = _load_json(BUCKET_MAP_PATH)
    inv_qualnames = {e["qualname"] for e in inv}
    bm_qualnames = {e["qualname"] for e in bm}
    extra = bm_qualnames - inv_qualnames
    assert not extra, f"{len(extra)} bucket map entries not in inventory: {sorted(extra)}"


def test_counts_match():
    """Inventory and bucket map must have equal entry counts."""
    inv = _load_json(INVENTORY_PATH)
    bm = _load_json(BUCKET_MAP_PATH)
    assert len(inv) == len(bm), f"Count mismatch: inventory={len(inv)}, bucket_map={len(bm)}"
