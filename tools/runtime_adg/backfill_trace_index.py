"""Back-fill the Runtime ADG `_trace_index.json` from on-disk snapshot payloads.

Plan: `docs/archive/windsurf/legacy-tree/plans/runtime-adg-tier1-trace-binding-c9b84d.md` (Phase W1.P3)

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
import hashlib
import json
import os
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L6_system_learning.store import _deserialise_snapshot  # noqa: E402
from agentic_core.L6_system_learning.stores.index_file_lock import (  # noqa: E402
    atomic_write_json_mapping,
    runtime_adg_index_lock,
)


@dataclass(frozen=True)
class BackfillReport:
    scanned: int
    bound_recovered: int  # snapshots with a real trace_id we can bind
    already_bound: int  # existing trace_index entry already correct
    empty_payload: int  # 0 nodes AND 0 edges — archive candidates
    unreadable: int  # deserialise failed — leave alone
    new_bindings: dict[str, str]  # trace_id -> version_id  (version_id == content hash[:??])
    recovered_version_index: dict[str, str] | None  # missing-index recovery plan
    authoritative_trace_bindings: dict[str, str]
    trace_bindings_to_remove: tuple[str, ...]
    trace_conflicts: dict[str, tuple[str, ...]]
    trace_index_state_hash: str
    version_index_state_hash: str
    shard_inventory_state_hash: str

    @property
    def trace_conflict_count(self) -> int:
        return len(self.trace_conflicts)

    def summary(self) -> str:
        return "\n".join(
            [
                f"Scanned snapshots:       {self.scanned}",
                f"Newly bound trace IDs:   {len(self.new_bindings)}",
                f"Recoverable bindings:    {self.bound_recovered}",
                f"Already-correct:         {self.already_bound}",
                f"Empty payload candidates:{self.empty_payload}",
                f"Unreadable payloads:     {self.unreadable}",
                f"Recovered version index: {len(self.recovered_version_index or {})}",
                f"Trace conflicts:        {self.trace_conflict_count}",
                *[
                    f"  {trace_id}: {', '.join(version_ids)}"
                    for trace_id, version_ids in sorted(self.trace_conflicts.items())
                ],
            ]
        )


def _iter_snapshot_files(base_dir: Path) -> Iterable[Path]:
    """Yield content-addressed snapshot files (`<hex[:2]>/<hex>.json`)."""
    for sub in sorted(base_dir.iterdir(), key=lambda path: path.name):
        if not sub.is_dir():
            continue
        if len(sub.name) != 2:
            continue
        yield from sorted(sub.glob("*.json"), key=lambda path: path.name)


def _verified_shard_with_source_bytes(path: Path) -> tuple[str, str, bytes, bytes]:
    """Return verified shard metadata and the exact validated source bytes."""
    try:
        source_bytes = path.read_bytes()
        raw = json.loads(source_bytes.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed runtime ADG shard {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"malformed runtime ADG shard {path}: metadata must be an object")

    version_id = raw.get("version_id")
    content_hash = raw.get("content_hash")
    payload_hex = raw.get("payload_hex")
    if not all(isinstance(value, str) and value for value in (version_id, content_hash, payload_hex)):
        raise ValueError(
            f"malformed runtime ADG shard {path}: version_id, content_hash, and payload_hex are required"
        )
    expected_hash = path.stem.lower()
    if len(expected_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_hash):
        raise ValueError(f"invalid content_hash filename for runtime ADG shard {path}")
    if path.parent.name.lower() != expected_hash[:2]:
        raise ValueError(f"content_hash shard prefix mismatch for {path}")
    if content_hash.lower() != expected_hash:
        raise ValueError(f"content_hash metadata mismatch for {path}: {content_hash!r} != {expected_hash!r}")
    try:
        payload = bytes.fromhex(payload_hex)
    except ValueError as exc:
        raise ValueError(f"malformed payload_hex for runtime ADG shard {path}") from exc
    observed_hash = hashlib.sha256(payload).hexdigest()
    if observed_hash != expected_hash:
        raise ValueError(f"content_hash payload mismatch for {path}: {observed_hash!r} != {expected_hash!r}")
    expected_version_id = f"v_{expected_hash[:16]}"
    if version_id != expected_version_id:
        raise ValueError(
            f"version_id metadata mismatch for {path}: {version_id!r} != {expected_version_id!r}"
        )
    return version_id, expected_hash, payload, source_bytes


def _verified_shard(path: Path) -> tuple[str, str, bytes]:
    """Return verified ``(version_id, content_hash, payload)`` metadata."""
    version_id, content_hash, payload, _source_bytes = _verified_shard_with_source_bytes(path)
    return version_id, content_hash, payload


def _verified_snapshot_with_source_bytes(path: Path):  # noqa: ANN202
    """Deserialize one exact shard read and return its validated source bytes."""
    version_id, content_hash, payload, source_bytes = _verified_shard_with_source_bytes(path)
    try:
        snapshot = _deserialise_snapshot(payload)
    except (KeyError, TypeError, ValueError, UnicodeDecodeError) as exc:
        raise ValueError(f"semantic verification failed for runtime ADG shard {path}: {exc}") from exc
    if snapshot.snapshot_id != content_hash or snapshot.snapshot_hash != content_hash:
        raise ValueError(
            "semantic verification failed for runtime ADG shard "
            f"{path}: snapshot identity does not match content hash"
        )
    if snapshot.canonical_bytes() != payload:
        raise ValueError(
            f"semantic verification failed for runtime ADG shard {path}: canonical bytes do not round-trip"
        )
    return version_id, content_hash, snapshot, source_bytes


def _verified_snapshot(path: Path):  # noqa: ANN202
    """Deserialize a shard and prove its semantic identity matches its bytes."""
    version_id, content_hash, snapshot, _source_bytes = _verified_snapshot_with_source_bytes(path)
    return version_id, content_hash, snapshot


def _reconstruct_version_index(base_dir: Path) -> dict[str, str]:
    """Build a deterministic version index only from fully verified shards."""
    recovered: dict[str, str] = {}
    for shard in _iter_snapshot_files(base_dir):
        version_id, content_hash, _payload = _verified_shard(shard)
        prior = recovered.get(version_id)
        if prior is not None and prior != content_hash:
            raise ValueError(f"version_id collision while recovering _index.json: {version_id!r}")
        recovered[version_id] = content_hash
    return dict(sorted(recovered.items()))


def _atomic_publish_json_if_absent(path: Path, payload: dict[str, str]) -> None:
    """Publish fully-written JSON without ever replacing an existing path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temp_path = Path(handle.name)
        # A same-filesystem hard link is an atomic create-if-absent operation:
        # unlike Path.replace(), it raises FileExistsError if a live writer
        # published the destination after our revalidation checks.
        os.link(temp_path, path)
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass


def _atomic_replace_trace_index_if_unchanged(
    path: Path,
    payload: dict[str, str],
    *,
    expected_state_hash: str,
) -> None:
    """Replace a trace index under the shared writer lock after state CAS."""
    current = _read_trace_index_path(path)
    if _mapping_state_hash(current) != expected_state_hash:
        raise ValueError("trace index changed during atomic publication")
    atomic_write_json_mapping(path, payload)


def _mapping_state_hash(payload: dict[str, str]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _read_index(base_dir: Path) -> dict[str, str]:
    path = base_dir / "_index.json"
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed runtime ADG version index {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"malformed runtime ADG version index {path}: expected an object")
    index: dict[str, str] = {}
    for version_id, content_hash in raw.items():
        if not isinstance(version_id, str) or not isinstance(content_hash, str):
            raise ValueError(f"malformed runtime ADG version index {path}: keys and values must be strings")
        normalized_hash = content_hash.lower()
        if (
            len(normalized_hash) != 64
            or any(char not in "0123456789abcdef" for char in normalized_hash)
            or version_id != f"v_{normalized_hash[:16]}"
        ):
            raise ValueError(
                f"malformed runtime ADG version index {path}: invalid mapping "
                f"{version_id!r} -> {content_hash!r}"
            )
        index[version_id] = normalized_hash
    if len(set(index.values())) != len(index):
        raise ValueError(f"malformed runtime ADG version index {path}: duplicate content hashes")
    return index


def _read_trace_index(base_dir: Path) -> dict[str, str]:
    return _read_trace_index_path(base_dir / "_trace_index.json")


def _read_trace_index_path(path: Path) -> dict[str, str]:
    """Read and validate one trace-index path."""
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed runtime ADG trace index {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"malformed runtime ADG trace index {path}: expected an object")
    # Strip stale empty-string keys/values from the legacy bug.
    cleaned: dict[str, str] = {}
    for trace_id, version_id in raw.items():
        if not isinstance(trace_id, str) or not isinstance(version_id, str):
            raise ValueError(f"malformed runtime ADG trace index {path}: keys and values must be strings")
        if trace_id and version_id:
            cleaned[trace_id] = version_id
    return cleaned


def build_backfill(base_dir: Path) -> BackfillReport:
    """Scan the runtime_adg directory and compute a back-fill plan."""
    index_missing = not (base_dir / "_index.json").exists()
    recovered_version_index = _reconstruct_version_index(base_dir) if index_missing else None
    version_index = recovered_version_index if recovered_version_index is not None else _read_index(base_dir)
    # Invert for quick content_hash -> version_id lookup.
    hash_to_version: dict[str, str] = {}
    for vid, content_hash in version_index.items():
        hash_to_version[content_hash] = vid

    existing_trace_index = _read_trace_index(base_dir)
    trace_candidates: dict[str, set[str]] = {}
    snapshot_candidates: dict[str, set[str]] = {}
    empty_payload = 0
    unreadable = 0
    scanned = 0
    shard_inventory: list[str] = []
    observed_version_index: dict[str, str] = {}

    for f in _iter_snapshot_files(base_dir):
        scanned += 1
        content_hash = f.stem
        version_id = hash_to_version.get(content_hash)
        metadata_version_id, verified_hash, snap, shard_bytes = _verified_snapshot_with_source_bytes(f)

        shard_inventory.append(
            f"{f.relative_to(base_dir).as_posix()}:{hashlib.sha256(shard_bytes).hexdigest()}"
        )

        if version_id is None:
            raise ValueError(f"verified runtime ADG shard {f} is not represented by _index.json")
        if metadata_version_id != version_id:
            raise ValueError(
                f"runtime ADG version index disagrees with shard metadata for {f}: "
                f"{version_id!r} != {metadata_version_id!r}"
            )
        observed_version_index[version_id] = verified_hash

        is_empty = not snap.trace_id and not snap.nodes and not snap.edges
        if is_empty:
            empty_payload += 1

        if snap.snapshot_id:
            snapshot_candidates.setdefault(snap.snapshot_id, set()).add(version_id)
        if not snap.trace_id:
            # Snapshot identity remains recoverable even when trace authority
            # is absent; only the trace alias is skipped.
            continue

        trace_candidates.setdefault(snap.trace_id, set()).add(version_id)

    if observed_version_index != version_index:
        missing_shards = sorted(set(version_index) - set(observed_version_index))
        raise ValueError(
            "runtime ADG version index references missing or unverified shards: " + ", ".join(missing_shards)
        )

    new_bindings: dict[str, str] = {}
    authoritative_trace_bindings: dict[str, str] = {}
    trace_bindings_to_remove: list[str] = []
    trace_conflicts: dict[str, tuple[str, ...]] = {}

    for trace_id in sorted(trace_candidates):
        candidates = tuple(sorted(trace_candidates[trace_id]))
        current = existing_trace_index.get(trace_id)
        if current in candidates:
            authoritative_trace_bindings[trace_id] = current
        elif len(candidates) == 1:
            new_bindings[trace_id] = candidates[0]
        else:
            trace_conflicts[trace_id] = candidates
            if current is not None:
                trace_bindings_to_remove.append(trace_id)

    # Snapshot IDs share the physical index but remain independently
    # recoverable when their content-addressed candidate is unique. Never let
    # a snapshot-ID alias overwrite a trace authority or unresolved conflict.
    protected_trace_keys = set(trace_candidates)
    for snapshot_id in sorted(snapshot_candidates):
        if snapshot_id in protected_trace_keys:
            continue
        candidates = tuple(sorted(snapshot_candidates[snapshot_id]))
        current = existing_trace_index.get(snapshot_id)
        if current in candidates:
            continue
        if len(candidates) == 1:
            new_bindings[snapshot_id] = candidates[0]

    return BackfillReport(
        scanned=scanned,
        bound_recovered=sum(1 for key in new_bindings if key in trace_candidates),
        already_bound=len(authoritative_trace_bindings),
        empty_payload=empty_payload,
        unreadable=unreadable,
        new_bindings=dict(sorted(new_bindings.items())),
        recovered_version_index=recovered_version_index,
        authoritative_trace_bindings=dict(sorted(authoritative_trace_bindings.items())),
        trace_bindings_to_remove=tuple(sorted(trace_bindings_to_remove)),
        trace_conflicts=dict(sorted(trace_conflicts.items())),
        trace_index_state_hash=_mapping_state_hash(existing_trace_index),
        version_index_state_hash=_mapping_state_hash(version_index),
        shard_inventory_state_hash=hashlib.sha256("\n".join(shard_inventory).encode("utf-8")).hexdigest(),
    )


def _revalidate_report(base_dir: Path, report: BackfillReport) -> None:
    """Rebuild and compare every planning input while holding the shared lock."""
    current_report = build_backfill(base_dir)
    if current_report.trace_index_state_hash != report.trace_index_state_hash:
        raise ValueError("trace index changed after backfill planning")
    if current_report.version_index_state_hash != report.version_index_state_hash:
        raise ValueError("runtime ADG version index changed after backfill planning")
    if current_report.shard_inventory_state_hash != report.shard_inventory_state_hash:
        raise ValueError("runtime ADG shard inventory changed after backfill planning")
    if (
        current_report.scanned != report.scanned
        or current_report.empty_payload != report.empty_payload
        or current_report.unreadable != report.unreadable
        or current_report.new_bindings != report.new_bindings
        or current_report.authoritative_trace_bindings != report.authoritative_trace_bindings
        or current_report.trace_bindings_to_remove != report.trace_bindings_to_remove
        or current_report.trace_conflicts != report.trace_conflicts
        or current_report.recovered_version_index != report.recovered_version_index
    ):
        raise ValueError("runtime ADG conflict or authority state changed after backfill planning")


def _archive_copy_plan(base_dir: Path) -> list[tuple[Path, bytes]]:
    """Preflight every forensic archive copy from one verified source read."""
    archive_dir = base_dir / "_archive_empty_payloads"
    candidates: list[tuple[Path, bytes]] = []
    for shard in _iter_snapshot_files(base_dir):
        _version_id, content_hash, snapshot, source_bytes = _verified_snapshot_with_source_bytes(shard)
        if snapshot.trace_id or snapshot.nodes or snapshot.edges:
            continue
        destination = archive_dir / f"{content_hash}.json"
        if destination.exists() and destination.read_bytes() != source_bytes:
            raise ValueError(f"archive destination differs from verified source: {destination}")
        candidates.append((destination, source_bytes))
    return candidates


def _publish_archive_copies(candidates: list[tuple[Path, bytes]]) -> int:
    """Publish preflighted forensic bytes without replacing any destination."""
    if not candidates:
        return 0
    candidates[0][0].parent.mkdir(exist_ok=True)
    for destination, source_bytes in candidates:
        if not destination.exists():
            temp_path: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=destination.parent,
                    prefix=destination.name + ".",
                    suffix=".tmp",
                    delete=False,
                ) as handle:
                    handle.write(source_bytes)
                    handle.flush()
                    os.fsync(handle.fileno())
                    temp_path = Path(handle.name)
                os.link(temp_path, destination)
            except FileExistsError:
                pass
            finally:
                if temp_path is not None:
                    temp_path.unlink(missing_ok=True)
        if destination.read_bytes() != source_bytes:
            raise ValueError(f"archive destination differs from verified source: {destination}")
    return len(candidates)


def recover_version_index_only(base_dir: Path, report: BackfillReport) -> dict[str, int]:
    """Recover only deterministic version authority; never bind a trace alias."""
    if report.recovered_version_index is None:
        raise ValueError("version-index-only recovery requires a missing planned _index.json")
    if report.unreadable:
        raise ValueError("unreadable runtime ADG shards prevent version-index recovery")
    with runtime_adg_index_lock(base_dir):
        if (base_dir / "_index.json").exists():
            raise ValueError("_index.json appeared after recovery planning; refusing concurrent overwrite")
        _revalidate_report(base_dir, report)
        existing_trace_index = _read_trace_index(base_dir)
        _atomic_publish_json_if_absent(base_dir / "_index.json", report.recovered_version_index)
    conflicts_with_existing_binding = sum(
        1 for trace_id in report.trace_conflicts if trace_id in existing_trace_index
    )
    return {
        "new_bindings_written": 0,
        "empty_payloads_archived": 0,
        "version_index_entries_recovered": len(report.recovered_version_index),
        "trace_conflicts_left_unbound": report.trace_conflict_count - conflicts_with_existing_binding,
        "trace_conflicts_with_existing_binding": conflicts_with_existing_binding,
    }


def apply_backfill(base_dir: Path, report: BackfillReport, archive_empty: bool = True) -> dict[str, int]:
    """Apply a back-fill plan: rewrite trace_index, archive empty snapshots."""
    if report.trace_conflicts:
        raise ValueError("unresolved trace conflicts prevent backfill apply")
    if report.unreadable:
        raise ValueError("unreadable runtime ADG shards prevent backfill apply")

    with runtime_adg_index_lock(base_dir):
        recovered_version_count = 0
        if report.recovered_version_index is not None and (base_dir / "_index.json").exists():
            raise ValueError("_index.json appeared after backfill planning; refusing concurrent overwrite")

        # Compare-and-swap guard: reconstruct the complete plan while holding
        # the same lock used by every live version/trace writer.
        _revalidate_report(base_dir, report)

        existing = _read_trace_index(base_dir)
        if _mapping_state_hash(existing) != report.trace_index_state_hash:
            raise ValueError("trace index changed during backfill revalidation")
        merged = dict(existing)
        for trace_id in report.trace_bindings_to_remove:
            merged.pop(trace_id, None)
        for binding_id, version_id in report.new_bindings.items():
            authoritative_version = report.authoritative_trace_bindings.get(binding_id)
            if authoritative_version is not None and authoritative_version != version_id:
                raise ValueError(f"refusing to overwrite valid trace authority for {binding_id!r}")
            merged[binding_id] = version_id

        trace_index_path = base_dir / "_trace_index.json"
        archive_copies = _archive_copy_plan(base_dir) if archive_empty else []
        archived = _publish_archive_copies(archive_copies)
        if report.recovered_version_index is not None:
            recovered_version_count = len(report.recovered_version_index)
            _atomic_publish_json_if_absent(
                base_dir / "_index.json",
                report.recovered_version_index,
            )
        _atomic_replace_trace_index_if_unchanged(
            trace_index_path,
            merged,
            expected_state_hash=report.trace_index_state_hash,
        )

        # Sources are intentionally retained and remain indexed.

    return {
        "new_bindings_written": len(report.new_bindings),
        "empty_payloads_archived": archived,
        "version_index_entries_recovered": recovered_version_count,
        "trace_conflicts_left_unbound": report.trace_conflict_count,
        "trace_conflicts_with_existing_binding": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    default_dir = _REPO_ROOT / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
    ap.add_argument("--runtime-adg-dir", type=Path, default=default_dir)
    action = ap.add_mutually_exclusive_group()
    action.add_argument("--report", action="store_true", help="Dry run (default)")
    action.add_argument("--apply", action="store_true", help="Rewrite trace_index and archive empty payloads")
    action.add_argument(
        "--recover-version-index-only",
        action="store_true",
        help="Recover only missing _index.json; leave all trace conflicts unbound",
    )
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

    if not args.apply and not args.recover_version_index_only:
        print("(dry run — re-run with --apply to execute)")
        return 0

    if args.recover_version_index_only:
        if args.no_archive:
            ap.error("--no-archive is valid only with --apply")
        result = recover_version_index_only(base, report)
    else:
        result = apply_backfill(base, report, archive_empty=not args.no_archive)
    print("=" * 60)
    print("APPLIED")
    print("=" * 60)
    for k, v in result.items():
        print(f"  {k:<30} {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
