#!/usr/bin/env python3
"""Export runtime ADG snapshot store -> ``artifacts/otel/spans.jsonl``.

Walks the content-addressed runtime ADG store at
``agentic_core/L4_state/memory/runtime_adg/<sha-prefix>/<sha>.json``,
decodes each snapshot's hex-encoded payload, and emits one JSONL line
per observed span name (the ``name`` field of every RuntimeADGNode).

Pairs with `ops_scripts/calibration/otel_span_poller.py` — that poller
reads the JSONL produced here. Pairs with
`ops_scripts/ci/check_l3_runtime_reconciliation.py` — that gate
consumes the poller's output to detect manifest/runtime drift.

Snapshot format (per `system_learning/runtime_adg/snapshot.py`):
  * Outer separator: ``\\x1f`` (RECORD SEPARATOR)
  * Inner field separator: ``\\x1e`` (UNIT SEPARATOR)
  * Header: trace_id, mission, started_at_utc, ended_at_utc
  * Node: node_id, name, kind, layer, component, started, duration_ms,
          status, attributes_json
  * Edge: src_id, dst_id, relation

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
DEFAULT_OUT = REPO / "artifacts" / "otel" / "spans.jsonl"

# Heuristic: extract span names that look like Python qualnames
# (Class.method or module.function) — these match the manifest format
# in `config/observability/required_spans.yaml`.
def _looks_like_qualname(s: str) -> bool:
    if "." not in s:
        return False
    if " " in s or "\n" in s:
        return False
    if s.startswith("_") or s.startswith("synth_") or s.startswith("synthetic"):
        return False
    parts = s.split(".")
    # Want at least one Class-like (capitalized) segment.
    return any(p[:1].isupper() for p in parts if p)


def _decode_snapshot(json_path: Path) -> tuple[set[str], dict] | None:
    """Decode one snapshot file. Returns (span_names, metadata) or None."""
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    # Some snapshots store as list-of-records; others as a single dict.
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get("payload_hex"):
                data = item
                break
        else:
            return None
    if not isinstance(data, dict):
        return None
    payload_hex = data.get("payload_hex")
    if not payload_hex:
        return None
    try:
        raw = bytes.fromhex(payload_hex)
    except ValueError:
        return None

    # Split by outer separator \x1f.
    records = raw.split(b"\x1f")
    if not records:
        return None
    # Header is records[0..3]: trace_id, mission, started, ended.
    # Subsequent records are nodes (9 fields, \x1e-separated) and edges
    # (3 fields). Extract node names — index 1 in node records.
    span_names: set[str] = set()
    for rec in records:
        fields = rec.split(b"\x1e")
        if len(fields) >= 9:
            # Node — extract name (field index 1).
            try:
                name = fields[1].decode("utf-8", errors="ignore")
            except Exception:  # noqa: BLE001
                continue
            if _looks_like_qualname(name):
                span_names.add(name)
    return span_names, {
        "version_id": data.get("version_id"),
        "content_hash": data.get("content_hash"),
        "type": data.get("type"),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                   help=f"Runtime ADG store directory (default: {DEFAULT_SOURCE.relative_to(REPO).as_posix()})")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT,
                   help=f"Output JSONL path (default: {DEFAULT_OUT.relative_to(REPO).as_posix()})")
    p.add_argument("--filter-app-prefix", action="append", default=None,
                   help="Only export spans whose qualname matches one of these prefixes "
                        "(e.g. 'apps_eval', 'apps_rg'). Default: all qualnames.")
    args = p.parse_args(argv)

    if not args.source.is_dir():
        print(f"[export] runtime ADG store not found: {args.source}", file=sys.stderr)
        return 4

    snapshot_files = list(args.source.rglob("*.json"))
    print(f"[export] scanning {len(snapshot_files)} runtime ADG snapshots...")

    all_spans: dict[str, int] = {}  # name -> observation count
    skipped = 0
    for f in snapshot_files:
        result = _decode_snapshot(f)
        if result is None:
            skipped += 1
            continue
        span_names, _meta = result
        for name in span_names:
            all_spans[name] = all_spans.get(name, 0) + 1

    if args.filter_app_prefix:
        prefixes = tuple(args.filter_app_prefix)
        all_spans = {
            n: c for n, c in all_spans.items()
            if any(p in n for p in prefixes)
        }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for name in sorted(all_spans):
            f.write(json.dumps({
                "op_name": name,
                "observation_count": all_spans[name],
                "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }) + "\n")

    print(f"[export] wrote {args.out.relative_to(REPO).as_posix()}")
    print(f"  unique_spans={len(all_spans)} snapshots_scanned={len(snapshot_files)} "
          f"skipped={skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
