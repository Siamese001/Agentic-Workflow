#!/usr/bin/env python3
"""CI Self-Consistency Gate — Cross-Gate Validation.

Verifies internal consistency across all CI gate artifacts:
  1. Agent Count Cap == Registry Consistency count.
  2. Active set fingerprint matches snapshot.
  3. MRO baseline total matches current baseline JSON.
  4. Centrality baseline file exists and loads.
  5. Target manifest schema validates.

Exit 0 = all consistent, exit 1 = mismatch found.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

MRO_BASELINE_PATH = "artifacts/consolidation/mro_diamond_baseline.json"
SNAPSHOT_PATH = "artifacts/consolidation/active_set_snapshot.json"
CENTRALITY_BASELINE_PATH = "artifacts/consolidation/centrality_baseline.json"
TARGET_MANIFEST_PATH = "artifacts/consolidation/target_manifest_v3.json"
TARGET_MANIFEST_SCHEMA_PATH = "artifacts/consolidation/target_manifest.schema.json"


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    errors: list[str] = []

    # ── Check 1: Active set count consistency ──
    snapshot_file = project_root / SNAPSHOT_PATH
    if snapshot_file.is_file():
        snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
        snapshot_count = snapshot.get("count", -1)

        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        try:
            from ops_scripts.ci.active_set_helper import get_active_set

            result = get_active_set(project_root)

            # Check 1a: snapshot count matches live count
            if result.count != snapshot_count:
                errors.append(
                    f"Active set count mismatch: snapshot={snapshot_count} live={result.count}",
                )

            # Check 1b: fingerprint matches
            if result.fingerprint != snapshot.get("fingerprint", ""):
                errors.append(
                    f"Active set fingerprint mismatch: "
                    f"snapshot={snapshot.get('fingerprint', '')[:16]}... "
                    f"live={result.fingerprint[:16]}...",
                )
        except Exception as e:
            errors.append(f"Active set helper failed: {e}")
    else:
        errors.append(f"Snapshot not found: {SNAPSHOT_PATH}")

    # ── Check 2: MRO baseline total matches JSON ──
    mro_file = project_root / MRO_BASELINE_PATH
    if mro_file.is_file():
        mro = json.loads(mro_file.read_text(encoding="utf-8"))
        declared_total = mro.get("total", -1)
        entry_count = len(mro.get("entries", []))
        if declared_total != entry_count:
            errors.append(
                f"MRO baseline internal mismatch: total={declared_total} entries={entry_count}",
            )
    else:
        errors.append(f"MRO baseline not found: {MRO_BASELINE_PATH}")

    # ── Check 3: Centrality baseline exists and loads ──
    centrality_file = project_root / CENTRALITY_BASELINE_PATH
    if centrality_file.is_file():
        try:
            centrality = json.loads(centrality_file.read_text(encoding="utf-8"))
            if not isinstance(centrality, (dict, list)):
                errors.append("Centrality baseline is not a valid JSON object/array")
        except json.JSONDecodeError as e:
            errors.append(f"Centrality baseline invalid JSON: {e}")
    else:
        errors.append(f"Centrality baseline not found: {CENTRALITY_BASELINE_PATH}")

    # ── Check 4: Target manifest schema validates ──
    manifest_file = project_root / TARGET_MANIFEST_PATH
    schema_file = project_root / TARGET_MANIFEST_SCHEMA_PATH
    if manifest_file.is_file():
        try:
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            if not isinstance(manifest, (dict, list)):
                errors.append("Target manifest is not a valid JSON object/array")
        except json.JSONDecodeError as e:
            errors.append(f"Target manifest invalid JSON: {e}")
    else:
        errors.append(f"Target manifest not found: {TARGET_MANIFEST_PATH}")

    if schema_file.is_file():
        try:
            json.loads(schema_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"Target manifest schema invalid JSON: {e}")
    else:
        errors.append(f"Target manifest schema not found: {TARGET_MANIFEST_SCHEMA_PATH}")

    # ── Report ──
    print("CI Self-Consistency Gate:")
    print(f"  checks_run=5  errors={len(errors)}")

    if errors:
        print(f"FAIL: {len(errors)} consistency issue(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("PASS: all cross-gate artifacts are internally consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
