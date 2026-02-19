"""
Generate deterministic SHA256 manifest of unit mirror duplicates.

Compares tests/unit/<subtree> vs tests/<subtree> for the four mirror pairs:
  - agentic_core
  - apps_lic
  - apps_rg
  - apps_shared

Outputs:
  tests/scripts/manifest_unit_mirror_duplicates.json

Each entry has:
  unit_path, canonical_path, identical (bool), sha256_unit, sha256_canonical, size_unit, size_canonical

Summary section lists:
  identical_count, different_count, unit_only_count, canonical_only_count
"""

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TESTS_ROOT = REPO_ROOT / "tests"
UNIT_ROOT = TESTS_ROOT / "unit"

MIRROR_SUBTREES = ["agentic_core", "apps_lic", "apps_rg", "apps_shared"]

STALE_RENAME_MAP = {
    "L0_maintenance": "L0_routing",
}

OUTPUT_PATH = Path(__file__).resolve().parent / "manifest_unit_mirror_duplicates.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_relative_py_files(root: Path) -> dict[str, Path]:
    """Return {relative_posix_path: absolute_path} for all .py files under root."""
    result = {}
    for p in sorted(root.rglob("*.py")):
        if ".mypy_cache" in p.parts:
            continue
        rel = p.relative_to(root).as_posix()
        result[rel] = p
    return result


def apply_stale_rename(rel: str) -> str:
    """Apply L0_maintenance -> L0_routing rename for canonical path lookup."""
    for stale, canonical in STALE_RENAME_MAP.items():
        rel = rel.replace(stale + "/", canonical + "/")
    return rel


def main() -> None:
    pairs = []
    unit_only = []
    canonical_only_by_subtree: dict[str, list[str]] = {}

    for subtree in MIRROR_SUBTREES:
        unit_dir = UNIT_ROOT / subtree
        canonical_dir = TESTS_ROOT / subtree

        if not unit_dir.exists():
            print(f"[SKIP] unit/{subtree} does not exist", file=sys.stderr)
            continue
        if not canonical_dir.exists():
            print(f"[SKIP] tests/{subtree} does not exist", file=sys.stderr)
            continue

        unit_files = collect_relative_py_files(unit_dir)
        canonical_files = collect_relative_py_files(canonical_dir)

        canonical_only = []

        for rel, unit_path in sorted(unit_files.items()):
            canonical_rel = apply_stale_rename(rel)
            if canonical_rel in canonical_files:
                canonical_path = canonical_files[canonical_rel]
                sha_u = sha256_file(unit_path)
                sha_c = sha256_file(canonical_path)
                identical = sha_u == sha_c
                pairs.append(
                    {
                        "subtree": subtree,
                        "unit_path": f"tests/unit/{subtree}/{rel}",
                        "canonical_path": f"tests/{subtree}/{canonical_rel}",
                        "stale_rename_applied": rel != canonical_rel,
                        "identical": identical,
                        "sha256_unit": sha_u,
                        "sha256_canonical": sha_c,
                        "size_unit": unit_path.stat().st_size,
                        "size_canonical": canonical_path.stat().st_size,
                    }
                )
            else:
                unit_only.append(
                    {
                        "subtree": subtree,
                        "unit_path": f"tests/unit/{subtree}/{rel}",
                        "canonical_path_would_be": f"tests/{subtree}/{canonical_rel}",
                        "stale_rename_applied": rel != canonical_rel,
                        "sha256_unit": sha256_file(unit_path),
                        "size_unit": unit_path.stat().st_size,
                    }
                )

        for rel, canonical_path in sorted(canonical_files.items()):
            unit_rel = rel
            for canonical_name, stale_name in {v: k for k, v in STALE_RENAME_MAP.items()}.items():
                unit_rel = unit_rel.replace(canonical_name + "/", stale_name + "/")
            if unit_rel not in unit_files and rel not in unit_files:
                canonical_only.append(f"tests/{subtree}/{rel}")

        if canonical_only:
            canonical_only_by_subtree[subtree] = canonical_only

    identical_count = sum(1 for p in pairs if p["identical"])
    different_count = sum(1 for p in pairs if not p["identical"])
    unit_only_count = len(unit_only)
    canonical_only_count = sum(len(v) for v in canonical_only_by_subtree.values())

    manifest = {
        "summary": {
            "identical_count": identical_count,
            "different_count": different_count,
            "unit_only_count": unit_only_count,
            "canonical_only_count": canonical_only_count,
            "total_pairs": len(pairs),
            "stale_rename_map": STALE_RENAME_MAP,
        },
        "pairs": sorted(pairs, key=lambda x: x["unit_path"]),
        "unit_only": sorted(unit_only, key=lambda x: x["unit_path"]),
        "canonical_only": {k: sorted(v) for k, v in sorted(canonical_only_by_subtree.items())},
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=False)

    print(f"Manifest written to: {OUTPUT_PATH}")
    print(f"  identical_count   : {identical_count}")
    print(f"  different_count   : {different_count}")
    print(f"  unit_only_count   : {unit_only_count}")
    print(f"  canonical_only_cnt: {canonical_only_count}")
    print(f"  total_pairs       : {len(pairs)}")


if __name__ == "__main__":
    main()
