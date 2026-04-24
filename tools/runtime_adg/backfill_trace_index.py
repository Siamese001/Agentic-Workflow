"""Back-fill the Runtime ADG `_trace_index.json` from on-disk snapshot payloads.

Plan: `.windsurf/plans/runtime-adg-tier1-trace-binding-c9b84d.md` (Phase W1.P3)

Why
---
The pre-Tier-1 persist() logic locked out 88 of 89 snapshots from the trace
index because a bug treated `if "" in trace_index` as "already bound." This
script repairs the damage by:

  1. Reading every `<hash[:2]>/<hash>.json` payload in the runtime_adg dir
  2. Deserializing each snapshot and extracting the REAL trace_id from its header
  3. Rewriting `_trace_index.json` with all discovered bindings
  4. Optionally archiving snapshots whose payload has both empty trace_id
     AND empty nodes AND empty edges — truly useless residue

Usage
-----
    # Dry run (default) — report only, no writes
    python tools/runtime_adg/backfill_trace_index.py --report

    # Apply — rewrite _trace_index.json and archive empties
    python tools/runtime_adg/backfill_trace_index.py --apply

    # Custom runtime_adg dir
    python tools/runtime_adg/backfill_trace_index.py --runtime-adg-dir <path> --apply
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from system_learning.runtime_adg.store import _deserialise_snapshot  # noqa: E402


@dataclass(frozen=True)
class BackfillReport:
    scanned: int
    bound_recovered: int  # snapshots with a real trace_id we can bind
    already_bound: int  # existing trace_index entry already correct
    empty_payload: int  # 0 nodes AND 0 edges — archive candidates
    unreadable: int  # deserialise failed — leave alone
    new_bindings: dict[str, str]  # trace_id -> version_id  (version_id == content hash[:??])

    def summary(self) -> str:
        return "\n".join(
            [
                f"Scanned snapshots:       {self.scanned}",
                f"Newly bound trace IDs:   {len(self.new_bindings)}",
                f"Recoverable bindings:    {self.bound_recovered}",
                f"Already-correct:         {self.already_bound}",
                f"Empty payload candidates:{self.empty_payload}",
                f"Unreadable payloads:     {self.unreadable}",
            ]
        )


def _iter_snapshot_files(base_dir: Path) -> Iterable[Path]:
    """Yield content-addressed snapshot files (`<hex[:2]>/<hex>.json`)."""
    for sub in base_dir.iterdir():
        if not sub.is_dir():
            continue
        if len(sub.name) != 2:
            continue
        for f in sub.glob("*.json"):
            yield f


def _read_index(base_dir: Path) -> dict[str, str]:
    path = base_dir / "_index.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return {str(k): str(v) for k, v in raw.items()}


def _read_trace_index(base_dir: Path) -> dict[str, str]:
    path = base_dir / "_trace_index.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    # Strip stale empty-string keys/values from the legacy bug.
    return {str(k): str(v) for k, v in raw.items() if k and v}


def build_backfill(base_dir: Path) -> BackfillReport:
    """Scan the runtime_adg directory and compute a back-fill plan."""
    version_index = _read_index(base_dir)  # version_id -> content_hash
    # Invert for quick content_hash -> version_id lookup.
    hash_to_version: dict[str, str] = {}
    for vid, content_hash in version_index.items():
        hash_to_version[content_hash] = vid

    existing_trace_index = _read_trace_index(base_dir)
    # Reverse-lookup: which version_id is already bound to something non-empty?
    already_bound_versions = set(existing_trace_index.values())

    new_bindings: dict[str, str] = {}
    bound_recovered = 0
    already_bound = 0
    empty_payload = 0
    unreadable = 0
    scanned = 0

    for f in _iter_snapshot_files(base_dir):
        scanned += 1
        content_hash = f.stem
        version_id = hash_to_version.get(content_hash)
        try:
            meta = json.loads(f.read_text(encoding="utf-8"))
            payload = bytes.fromhex(meta["payload_hex"])
            snap = _deserialise_snapshot(payload)
        except (OSError, ValueError, KeyError, UnicodeDecodeError):
            unreadable += 1
            continue

        is_empty = not snap.nodes and not snap.edges
        if is_empty:
            empty_payload += 1

        if not snap.trace_id:
            # Nothing to bind — leave for archival step below.
            continue

        if version_id is None:
            # Orphaned file: on disk but not referenced by _index.json.
            # Don't fabricate a version_id; skip.
            unreadable += 1
            continue

        current = existing_trace_index.get(snap.trace_id)
        if current == version_id:
            already_bound += 1
        else:
            bound_recovered += 1
            new_bindings[snap.trace_id] = version_id
            # Also bind snapshot_id -> version_id if not already.
            if snap.snapshot_id and existing_trace_index.get(snap.snapshot_id) != version_id:
                new_bindings[snap.snapshot_id] = version_id

    return BackfillReport(
        scanned=scanned,
        bound_recovered=bound_recovered,
        already_bound=already_bound,
        empty_payload=empty_payload,
        unreadable=unreadable,
        new_bindings=new_bindings,
    )


def apply_backfill(base_dir: Path, report: BackfillReport, archive_empty: bool = True) -> dict[str, int]:
    """Apply a back-fill plan: rewrite trace_index, archive empty snapshots."""
    # 1) Rewrite _trace_index.json with cleaned existing + new bindings.
    existing = _read_trace_index(base_dir)
    merged = dict(existing)
    merged.update(report.new_bindings)
    trace_index_path = base_dir / "_trace_index.json"
    trace_index_path.write_text(
        json.dumps(merged, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    archived = 0
    if archive_empty and report.empty_payload > 0:
        # 2) Move empty-payload files to an archive subfolder for forensic review.
        archive_dir = base_dir / "_archive_empty_payloads"
        archive_dir.mkdir(exist_ok=True)

        version_index = _read_index(base_dir)
        hash_to_version: dict[str, str] = {str(v): str(k) for k, v in version_index.items()}

        versions_to_remove: list[str] = []
        for f in _iter_snapshot_files(base_dir):
            content_hash = f.stem
            try:
                meta = json.loads(f.read_text(encoding="utf-8"))
                snap = _deserialise_snapshot(bytes.fromhex(meta["payload_hex"]))
            except (OSError, ValueError, KeyError, UnicodeDecodeError):
                continue
            if snap.nodes or snap.edges:
                continue
            # Empty — archive the file and mark its version for removal.
            dest = archive_dir / f"{content_hash}.json"
            if not dest.exists():
                shutil.move(str(f), str(dest))
            # Clean up empty parent dir if possible.
            try:
                f.parent.rmdir()
            except OSError:
                pass
            archived += 1
            vid = hash_to_version.get(content_hash)
            if vid:
                versions_to_remove.append(vid)

        # Rewrite _index.json without archived versions.
        if versions_to_remove:
            new_version_index = {k: v for k, v in version_index.items() if k not in versions_to_remove}
            (base_dir / "_index.json").write_text(
                json.dumps(new_version_index, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            # Also strip any trace_index entry that pointed to a removed version.
            stripped_trace_index = {k: v for k, v in merged.items() if v not in versions_to_remove}
            trace_index_path.write_text(
                json.dumps(stripped_trace_index, indent=2, sort_keys=True),
                encoding="utf-8",
            )

    return {
        "new_bindings_written": len(report.new_bindings),
        "empty_payloads_archived": archived,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    default_dir = _REPO_ROOT / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
    ap.add_argument("--runtime-adg-dir", type=Path, default=default_dir)
    ap.add_argument("--report", action="store_true", help="Dry run (default)")
    ap.add_argument("--apply", action="store_true", help="Rewrite trace_index and archive empty payloads")
    ap.add_argument(
        "--no-archive", action="store_true", help="Do not archive empty-payload snapshots on --apply"
    )
    args = ap.parse_args()

    base = args.runtime_adg_dir.resolve()
    if not base.exists():
        print(f"runtime_adg dir does not exist: {base}", file=sys.stderr)
        return 2

    print(f"Scanning: {base}")
    t0 = time.time()
    report = build_backfill(base)
    print(f"(scan took {time.time() - t0:.2f}s)")
    print("=" * 60)
    print("BACKFILL PLAN")
    print("=" * 60)
    print(report.summary())
    print()

    if not args.apply:
        print("(dry run — re-run with --apply to execute)")
        return 0

    result = apply_backfill(base, report, archive_empty=not args.no_archive)
    print("=" * 60)
    print("APPLIED")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k:<30} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
