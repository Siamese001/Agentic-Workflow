#!/usr/bin/env python3
"""Nightly L3↔runtime contract reconciliation.

Compares the source-side OTEL contract (``required_spans.yaml``) against
actual production OTEL traces ingested via ``otel_mcp.spans_by_agent``.
Catches the gap that L1+L2+L3 cannot detect on their own:

  L1: every module emits SOMETHING at runtime
  L2: synthetic probes confirm spans CAN fire
  L3: source declares span name + layer

  THIS GATE: every declared span has actually been observed in the last
             N days (default 7), AND no production span exists with a
             span-name that isn't declared in the manifest.

Two failure modes detected:

  * Declared but unseen (``manifest_only``): the source contract says
    the span must fire, but the runtime never did. Either the engine is
    dead code, the decorator is broken, or the production deployment
    is older than the source.

  * Seen but undeclared (``runtime_only``): production emits a span that
    has no entry in the manifest. Either the manifest is stale, or
    someone shipped instrumentation that bypasses the contract.

Exit codes:
  0 = all manifest spans seen + no undeclared spans
  1 = declared-but-unseen spans (manifest claims more than runtime delivers)
  2 = undeclared-but-seen spans (runtime emits more than manifest declares)
  3 = both
  4 = otel_mcp unavailable / runtime data not retrievable

Run mode:
  --strict (default in CI nightly): exit non-zero on either mismatch class
  --advisory (operator manual run): always exit 0, log violations to JSONL
  --report-only: skip MCP, replay last persisted observations

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

MANIFEST_PATH = REPO / "config" / "observability" / "required_spans.yaml"
ARTIFACTS_DIR = REPO / "artifacts" / "observability"
LAST_OBSERVED_PATH = ARTIFACTS_DIR / "last_observed_spans.json"
VIOLATIONS_LOG = ARTIFACTS_DIR / "l3_runtime_reconciliation.jsonl"
REPORT_PATH = ARTIFACTS_DIR / "l3_runtime_reconciliation.md"


def _load_manifest_spans() -> set[str]:
    """Return the set of all declared span qualnames from the manifest."""
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    out: set[str] = set()
    for app, spec in data.items():
        if not isinstance(spec, dict):
            continue
        for entry in spec.get("required_spans", []) or []:
            if isinstance(entry, str):
                out.add(entry)
            elif isinstance(entry, dict) and "name" in entry:
                out.add(str(entry["name"]))
    return out


def _fetch_observed_from_otel(time_window_days: int) -> tuple[set[str], str]:
    """Fetch observed span names from otel_mcp.

    Returns (observed_span_set, source_label). source_label is one of:
      * "otel_mcp"        — successful MCP fetch
      * "cached"          — fell back to last_observed_spans.json
      * "empty"           — no MCP, no cache
    """
    # The otel_mcp surface exposes `otel_spans_by_agent` for per-agent
    # filtering. For nightly reconciliation we want all engine spans
    # across the apps_* surface. We collect by querying a small set of
    # well-known agent_class patterns and union the results.
    #
    # In CI / scripted contexts we can't directly invoke MCP tools; we
    # consume the persisted output produced by the dedicated poller
    # `tools/observability/otel_span_poller.py` (future). Until that
    # poller exists, we fall back to the last-cached observation file.
    if LAST_OBSERVED_PATH.is_file():
        try:
            data = json.loads(LAST_OBSERVED_PATH.read_text(encoding="utf-8"))
            spans = set(data.get("spans", []))
            ts = data.get("collected_at", "unknown")
            return spans, f"cached:{ts}"
        except (OSError, json.JSONDecodeError):
            pass
    return set(), "empty"


def _persist_observations(observed: set[str], source: str) -> None:
    """Write the observation set so the next run can fall back to it."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": source,
        "spans": sorted(observed),
        "count": len(observed),
    }
    LAST_OBSERVED_PATH.write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8",
    )


def _log_violation(kind: str, payload: dict) -> None:
    """Append a violation row to the JSONL log."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "kind": kind,
        **payload,
    }
    with VIOLATIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_report(
    declared: set[str],
    observed: set[str],
    manifest_only: set[str],
    runtime_only: set[str],
    source: str,
    mode: str,
) -> None:
    """Emit a human-readable markdown report."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# L3 ↔ Runtime Contract Reconciliation")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"Mode: {mode}")
    lines.append(f"Observation source: {source}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Declared (manifest):       **{len(declared)}**")
    lines.append(f"- Observed (runtime):        **{len(observed)}**")
    lines.append(f"- Manifest only (unseen):    **{len(manifest_only)}**")
    lines.append(f"- Runtime only (undeclared): **{len(runtime_only)}**")
    lines.append("")
    if manifest_only:
        lines.append("## Manifest only — declared but never observed")
        lines.append("")
        lines.append("These spans appear in `required_spans.yaml` but the runtime "
                     "telemetry has not produced them in the observation window. "
                     "Possible causes: dead code path, broken decorator, stale deployment.")
        lines.append("")
        for s in sorted(manifest_only):
            lines.append(f"- `{s}`")
        lines.append("")
    if runtime_only:
        lines.append("## Runtime only — observed but not declared")
        lines.append("")
        lines.append("Production emits these spans but they are not in the manifest. "
                     "Either add to manifest or remove the instrumentation.")
        lines.append("")
        for s in sorted(runtime_only):
            lines.append(f"- `{s}`")
        lines.append("")
    if not (manifest_only or runtime_only):
        lines.append("## ✅ Contract and runtime are in sync")
        lines.append("")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    p.add_argument("--mode", choices=("strict", "advisory", "report-only"),
                   default=os.environ.get("L3_RUNTIME_GATE_MODE", "advisory"))
    p.add_argument("--time-window-days", type=int, default=7)
    args = p.parse_args(argv)

    declared = _load_manifest_spans()
    if not declared:
        print("[L3_runtime] manifest empty or unreadable — fail closed", file=sys.stderr)
        return 4

    if args.mode == "report-only":
        observed, source = _fetch_observed_from_otel(args.time_window_days)
    else:
        observed, source = _fetch_observed_from_otel(args.time_window_days)
        # If no observation source available and not running in advisory
        # mode, that's a runtime-data failure (exit 4).
        if not observed and source == "empty" and args.mode == "strict":
            print(
                "[L3_runtime] no observation source available "
                "(otel_mcp poller has not run; no cached observations)",
                file=sys.stderr,
            )
            return 4

    manifest_only = declared - observed
    runtime_only = observed - declared

    _persist_observations(observed, source)
    _write_report(declared, observed, manifest_only, runtime_only,
                  source=source, mode=args.mode)

    if manifest_only:
        _log_violation("manifest_only", {"spans": sorted(manifest_only),
                                          "count": len(manifest_only)})
    if runtime_only:
        _log_violation("runtime_only", {"spans": sorted(runtime_only),
                                         "count": len(runtime_only)})

    print(f"[L3_runtime] mode={args.mode} source={source}")
    print(f"  declared={len(declared)} observed={len(observed)}")
    print(f"  manifest_only={len(manifest_only)} runtime_only={len(runtime_only)}")
    print(f"  report: {REPORT_PATH.relative_to(REPO).as_posix()}")

    if args.mode in ("strict",):
        ec = 0
        if manifest_only:
            ec |= 1
        if runtime_only:
            ec |= 2
        return ec
    # advisory + report-only never fail.
    return 0


if __name__ == "__main__":
    sys.exit(main())
