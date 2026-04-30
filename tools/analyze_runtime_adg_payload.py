"""Pragmatic apps_rg runtime ADG payload analyzer.

The materialized RuntimeADGSnapshot uses a tab/control-char delimited binary
format (\\x1f field separator, \\x1e record separator, plain JSON for the
attributes blob). Rather than parse the bespoke format, this script does
text-pattern counts that are sufficient for end-to-end evidence:

  * total span count (records)
  * edge_kind distribution
  * layer distribution
  * presence of req_evidence emissions
  * presence of full L0..L6 lifecycle coverage
"""
from __future__ import annotations

import json
import pathlib
import re
import time
from collections import Counter

BASE = pathlib.Path("agentic_core/L4_state/memory/runtime_adg")
CUTOFF = time.time() - 30 * 60


def main() -> int:
    cands: list[tuple[float, pathlib.Path]] = []
    for d in BASE.iterdir():
        if d.is_dir() and len(d.name) == 2:
            for f in d.rglob("*.json"):
                if f.is_file() and f.stat().st_mtime > CUTOFF and f.stat().st_size > 100_000:
                    cands.append((f.stat().st_mtime, f))
    cands.sort()
    if not cands:
        print("[!] no large recent files")
        return 1

    print(f"=== Apps_RG Runtime ADG Snapshot Analysis ===")
    print(f"large_recent_files={len(cands)}")
    print()

    for mt, target in cands:
        ts = time.strftime("%H:%M:%S", time.localtime(mt))
        raw = json.loads(target.read_text(encoding="utf-8"))
        payload_hex = raw.get("payload_hex", "")
        size = len(payload_hex) // 2
        print(f"--- snapshot: {target.relative_to(BASE)} ({ts}, {size:,} bytes) ---")
        print(f"  version_id={raw.get('version_id')}")
        payload_bytes = bytes.fromhex(payload_hex)
        text = payload_bytes.decode("utf-8", errors="replace")

        # Mission line is the second \x1f-separated header field
        header_fields = text.split("\x1f", maxsplit=4)
        if len(header_fields) >= 2:
            print(f"  mission={header_fields[1]}")

        # Record separator is \x1e — count records (-1 because first is in header)
        rec_count = text.count("\x1e")
        # Each record starts with trace_id then \x1e + edge_kind. Count
        # occurrences of `adg.<edge_kind>` to estimate edge-kind frequency.
        ek_pattern = re.compile(r"adg\.([a-z_]+)")
        ek_hits = ek_pattern.findall(text)
        ek_counts = Counter(ek_hits)

        # Layer mentions in attribute JSON
        layer_pattern = re.compile(r'"agentic\.layer"\s*:\s*"([^"]+)"')
        layer_hits = layer_pattern.findall(text)
        layer_counts = Counter(layer_hits)

        # Op (function-level) mentions
        op_pattern = re.compile(r'"agentic\.op"\s*:\s*"([^"]+)"')
        ops = op_pattern.findall(text)
        op_counts = Counter(ops)

        # Req evidence
        req_pattern = re.compile(r"REQ-[A-Z0-9-]+")
        req_hits = sorted(set(req_pattern.findall(text)))

        print(f"  rec_separators(\\x1e)={rec_count:,}")
        print(f"  edge_kind_total_mentions={sum(ek_counts.values()):,}")
        print(f"  unique_edge_kinds={len(ek_counts)}")
        print(f"  unique_layers={len(layer_counts)}")
        print(f"  unique_ops={len(op_counts)}")
        print(f"  REQs_emitted={req_hits}")
        print()
        print(f"  TOP-15 edge_kinds:")
        for k, v in ek_counts.most_common(15):
            print(f"    {v:6d}  adg.{k}")
        print()
        print(f"  Layer distribution:")
        for k, v in layer_counts.most_common():
            print(f"    {v:6d}  {k}")
        print()
        print(f"  TOP-15 ops (function-level):")
        for k, v in op_counts.most_common(15):
            print(f"    {v:6d}  {k}")
        print()

        # Presence test — full lifecycle U0..L4
        lifecycle_kinds = [
            ("U0/intake", ["pulls_context", "reads_runtime_state"]),
            ("L0/routing", ["routes_through", "routes_to_agent", "routes_to_capability"]),
            ("L1/cognition", ["agent_executes_agent", "verifies_policy", "transcripts_response"]),
            ("L2/execution", ["authorize_and_execute", "writes_via_uwg", "blocks_direct_write"]),
            ("L3/orchestration", ["dispatches_agent", "coordinates_agents", "orchestrates_workflow"]),
            ("L4/state+meta", ["stores_embedding", "updates_meta_learning_state", "feeds_meta_learning"]),
            ("L5/safety", ["validated_by_safety_plane", "applies_guardrail", "verifies_boundary"]),
            ("L6/observability", ["records_telemetry_event", "captures_runtime_anomaly", "emits_metric_event"]),
        ]
        print(f"  Lifecycle coverage (U0->L4 + safety/obs):")
        for layer, kinds in lifecycle_kinds:
            counts = [(k, ek_counts.get(k, 0)) for k in kinds]
            present = [c for c in counts if c[1] > 0]
            status = "PRESENT" if present else "MISSING"
            total = sum(c[1] for c in counts)
            print(f"    [{status:7s}] {layer:25s} total={total:5d}  {[f'{k}={v}' for k,v in counts]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
