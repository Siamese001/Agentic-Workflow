"""Direct OTel runtime-ADG verifier — proof-of-traces for any mission.

Bypasses the otel_mcp MCP server and reads the file-backed snapshot store
directly. Use this when:
  - the running otel_mcp server is bound to a different repo path
    (precedent: 2026-04-30 apps_rg trace-visibility blackout — the MCP read
    from C:\\Git\\Agentic-Workflow while the pipeline wrote to
    C:\\Git\\Agentic-Workflow-FRESH);
  - the MCP cache is cold and you need cold-start proof;
  - you want a deterministic, reproducible audit artifact (the MCP cache
    layer is in-memory only).

Output schema mirrors what `mcp8_otel_spans_by_agent` would return so a
downstream consumer (e.g. the run_report.json) can be wired the same way.

Usage::

    python -m tools.otel.verify_apps_rg_traces --agent apps_rg --limit 20
    python -m tools.otel.verify_apps_rg_traces --since 2026-04-29T20:00:00Z
    python -m tools.otel.verify_apps_rg_traces --json   # machine-readable

Exit codes::

    0  — proof found (≥1 snapshot matched filter)
    2  — no matching snapshots (the run is unverifiable per the
         "without otel traces the run never happened" invariant)
    3  — store unreachable / corrupted
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TraceVerificationResult:
    agent: str
    store_path: Path
    snapshots_total: int
    snapshots_matched: int
    spans_total: int
    earliest_utc: int | None
    latest_utc: int | None
    sample_traces: list[dict[str, Any]]
    components_seen: dict[str, int]
    layers_seen: dict[str, int]


def _resolve_store_path(explicit: str | None) -> Path:
    """Pick the runtime-ADG dir, with the same precedence as `otel_config.py`."""
    if explicit:
        return Path(explicit).expanduser().resolve()
    import os

    explicit_dir = os.environ.get("OTEL_MCP_RUNTIME_ADG_DIR")
    if explicit_dir:
        return Path(explicit_dir).expanduser().resolve()
    # Default: derive from this file's repo. Matches `otel_config.py` precedence
    # exactly so the verifier reads the same store the in-process bridge writes.
    # Intentionally does NOT honor AGENTIC_REPO_ROOT (legacy editor may set it to a
    # different clone than the running Python process).
    return (
        Path(__file__).resolve().parents[2]
        / "agentic_core" / "L4_state" / "memory" / "runtime_adg"
    )


def _matches(
    snapshot: Any,
    *,
    agent: str,
    since_utc: int | None,
    until_utc: int | None,
) -> bool:
    # Time filter — but ALWAYS admit snapshots with started_at_utc==0 because
    # the in-process bridge currently emits unstamped spans (see
    # docs/architecture/adr/ADR-XXX runtime-adg-bridge-timestamp.md). Excluding
    # them here would hide every apps_rg trace.
    if snapshot.started_at_utc and since_utc is not None and snapshot.started_at_utc < since_utc:
        return False
    if snapshot.started_at_utc and until_utc is not None and snapshot.started_at_utc > until_utc:
        return False
    # Match on mission OR on any node component/name containing the agent token.
    needle = agent.lower()
    if needle == "*":
        return True
    if needle in (snapshot.mission or "").lower():
        return True
    for node in snapshot.nodes:
        comp = (node.component or "").lower()
        name = (node.name or "").lower()
        if needle in comp or needle in name:
            return True
    return False


def verify(
    agent: str = "apps_rg",
    *,
    store_dir: str | None = None,
    since: str | None = None,
    until: str | None = None,
    sample_limit: int = 5,
) -> TraceVerificationResult:
    base_dir = _resolve_store_path(store_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"runtime_adg store does not exist: {base_dir}")

    # Lazy-import so the script starts even if system_learning has import-side
    # effects (it does — `_emit_engine_lifecycle` etc.).
    from agentic_core.L6_system_learning.store import FileBackedRuntimeADGStore

    store = FileBackedRuntimeADGStore(base_dir=base_dir)
    version_ids = store.list_snapshots()

    since_utc = _parse_iso(since)
    until_utc = _parse_iso(until)

    matched: list[Any] = []
    components: dict[str, int] = {}
    layers: dict[str, int] = {}
    spans_total = 0
    earliest_utc: int | None = None
    latest_utc: int | None = None

    for vid in version_ids:
        snapshot = store.load_snapshot(vid)
        if snapshot is None:
            continue
        if not _matches(snapshot, agent=agent, since_utc=since_utc, until_utc=until_utc):
            continue
        matched.append(snapshot)
        spans_total += len(snapshot.nodes)
        if earliest_utc is None or snapshot.started_at_utc < earliest_utc:
            earliest_utc = snapshot.started_at_utc
        if latest_utc is None or snapshot.started_at_utc > latest_utc:
            latest_utc = snapshot.started_at_utc
        for node in snapshot.nodes:
            if node.component:
                components[node.component] = components.get(node.component, 0) + 1
            if node.layer:
                layers[node.layer] = layers.get(node.layer, 0) + 1

    # Sample most-recent first.
    matched.sort(key=lambda s: s.started_at_utc, reverse=True)
    sample = []
    for snapshot in matched[:sample_limit]:
        sample.append({
            "trace_id": snapshot.trace_id,
            "mission": snapshot.mission,
            "started_at_utc": snapshot.started_at_utc,
            "ended_at_utc": snapshot.ended_at_utc,
            "duration_s": snapshot.ended_at_utc - snapshot.started_at_utc,
            "n_nodes": len(snapshot.nodes),
            "n_edges": len(snapshot.edges),
            "first_node": (
                {
                    "node_id": snapshot.nodes[0].node_id,
                    "name": snapshot.nodes[0].name,
                    "component": snapshot.nodes[0].component,
                    "layer": snapshot.nodes[0].layer,
                    "status": snapshot.nodes[0].status,
                }
                if snapshot.nodes else None
            ),
        })

    return TraceVerificationResult(
        agent=agent,
        store_path=base_dir,
        snapshots_total=len(version_ids),
        snapshots_matched=len(matched),
        spans_total=spans_total,
        earliest_utc=earliest_utc,
        latest_utc=latest_utc,
        sample_traces=sample,
        components_seen=dict(sorted(components.items(), key=lambda x: -x[1])[:10]),
        layers_seen=dict(sorted(layers.items(), key=lambda x: -x[1])),
    )


def _parse_iso(raw: str | None) -> int | None:
    if not raw:
        return None
    # Accept Z-suffix or timezone-aware; coerce to epoch seconds.
    s = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Snapshots store started_at_utc as ms-since-epoch; match that scale.
    return int(dt.timestamp() * 1000)


def _to_iso(epoch_value: int | None) -> str:
    """Format a timestamp robustly. Snapshots use ms-since-epoch; older paths
    used seconds. Auto-detect: anything > 1e11 is treated as ms."""
    if epoch_value is None:
        return "?"
    seconds = epoch_value / 1000.0 if epoch_value > 1e11 else float(epoch_value)
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()
    except (OSError, OverflowError, ValueError):
        return f"epoch={epoch_value}"


def _format_human(result: TraceVerificationResult) -> str:
    lines: list[str] = []
    lines.append("OTel Runtime-ADG Verifier")
    lines.append("-" * 60)
    lines.append(f"Store path:        {result.store_path}")
    lines.append(f"Agent filter:      {result.agent}")
    lines.append(f"Snapshots total:   {result.snapshots_total}")
    lines.append(f"Snapshots matched: {result.snapshots_matched}")
    lines.append(f"Spans total:       {result.spans_total}")
    if result.earliest_utc and result.latest_utc:
        lines.append(f"Time range:        {_to_iso(result.earliest_utc)} -> {_to_iso(result.latest_utc)}")
    if result.layers_seen:
        lines.append(f"Layers:            {result.layers_seen}")
    if result.components_seen:
        lines.append("Top components:")
        for comp, n in result.components_seen.items():
            lines.append(f"  {n:>5}  {comp}")
    if result.sample_traces:
        lines.append("")
        lines.append(f"Most-recent {len(result.sample_traces)} matching snapshot(s):")
        for st in result.sample_traces:
            ts = _to_iso(st["started_at_utc"])
            lines.append(
                f"  {ts}  trace_id={st['trace_id'][:16]}...  "
                f"mission={st['mission'][:40]}  "
                f"nodes={st['n_nodes']} edges={st['n_edges']}"
            )
            if st["first_node"]:
                fn = st["first_node"]
                lines.append(
                    f"    first: {fn['component']} / {fn['layer']} / "
                    f"{fn['name'][:60]}  [status={fn['status']}]"
                )
    if result.snapshots_matched == 0:
        lines.append("")
        lines.append("VERDICT: No matching traces. Per 'no traces, no run' "
                     "invariant, this run is UNVERIFIED.")
    else:
        lines.append("")
        lines.append(f"VERDICT: {result.snapshots_matched} snapshots / "
                     f"{result.spans_total} spans confirm {result.agent} ran.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--agent", default="apps_rg",
                   help="Agent token to match (mission/component/name substring). '*' matches all. Default: apps_rg")
    p.add_argument("--store-dir", default=None,
                   help="Override runtime_adg directory. Falls back to OTEL_MCP_RUNTIME_ADG_DIR env, then this repo.")
    p.add_argument("--since", default=None, help="ISO-8601 lower bound, e.g. 2026-04-29T20:00:00Z")
    p.add_argument("--until", default=None, help="ISO-8601 upper bound")
    p.add_argument("--limit", type=int, default=5, help="Max sample traces to print (default 5)")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable text")
    args = p.parse_args(argv)

    try:
        result = verify(
            agent=args.agent,
            store_dir=args.store_dir,
            since=args.since,
            until=args.until,
            sample_limit=args.limit,
        )
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3
    except ImportError as exc:
        print(f"ERROR: failed to import store backend: {exc}", file=sys.stderr)
        return 3

    if args.json:
        payload = {
            "agent": result.agent,
            "store_path": str(result.store_path),
            "snapshots_total": result.snapshots_total,
            "snapshots_matched": result.snapshots_matched,
            "spans_total": result.spans_total,
            "earliest_utc": result.earliest_utc,
            "latest_utc": result.latest_utc,
            "components_seen": result.components_seen,
            "layers_seen": result.layers_seen,
            "sample_traces": result.sample_traces,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_human(result))

    return 0 if result.snapshots_matched > 0 else 2


if __name__ == "__main__":
    sys.exit(main())
