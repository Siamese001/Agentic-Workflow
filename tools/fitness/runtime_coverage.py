"""Architectural Fitness Functions for runtime behavioral coverage.

Per Building Evolutionary Architectures (Ford/Parsons) — fitness functions
are *"any mechanism that performs an objective integrity assessment of some
architecture characteristic."* This module computes 5 such functions over
the REQ Coverage Exemplar Ledger and the latest static ADG snapshot.

Outputs:

  * Markdown report: ``docs/reports/calibration/fitness_<YYYY_WNN>.md``
  * JSON metrics:    ``artifacts/runtime/fitness.json`` (optional)

The 5 fitness functions and their target thresholds:

| Function                      | Target  | Metric                                          |
|-------------------------------|---------|-------------------------------------------------|
| behavioral_coverage_per_app   | ≥ 0.85  | runtime_observed_REQs / declared_REQs           |
| layer_emission_breadth        | ≥ 7/9   | distinct layer values seen in last week        |
| static_runtime_coverage       | ≥ 0.70  | runtime_observed_static_nodes / total_static    |
| req_freshness_p50_days        | ≤ 7     | median age of last-seen exemplar per declared REQ |
| orphan_ingest_count           | == 0    | L5/L6 symbols with runtime_fan_in == 0         |
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
import sys
import time
from contextlib import closing
from pathlib import Path
from typing import Any

from tools.audits.static_runtime_gap import compute_gap, latest_static_snapshot
from tools.runtime_evidence.contract_verifier import (
    DEFAULT_CONTRACTS_DIR,
    load_contracts,
)
from tools.runtime_evidence.ledger_writer import DEFAULT_LEDGER_PATH

REPO_ROOT = Path(__file__).resolve().parents[2]

# Canonical layer set (LayerSegment in lifecycle_trace_contract).
_ALL_LAYERS = {
    "L0_ROUTING",
    "L1_REASONING",
    "L2_EXECUTION",
    "L3_ORCHESTRATION",
    "L4_STATE",
    "L5_POLICY",
    "L6_OBSERVABILITY",
    "U0_INPUT",
    "C0_RETRIEVAL_PLAN",
    "PA_BOM_RESOLUTION",
}

# Targets — calibration via the existing weekly cadence (ADR-050).
TARGETS = {
    "behavioral_coverage_per_app": 0.85,
    "layer_emission_breadth": 7,
    "static_runtime_coverage": 0.70,
    "req_freshness_p50_days": 7.0,
    "orphan_ingest_count": 0,
}


def _ledger_freshness(ledger_path: Path, lookback_days: int) -> dict[str, Any]:
    """Per-REQ_ID freshness summary."""
    if not ledger_path.exists():
        return {}
    cutoff = int(time.time()) - lookback_days * 24 * 3600
    with closing(sqlite3.connect(ledger_path)) as con:
        rows = con.execute(
            """
            SELECT req_id, MAX(observed_at), COUNT(*),
                   GROUP_CONCAT(DISTINCT app_id),
                   GROUP_CONCAT(DISTINCT layer)
            FROM req_emission
            WHERE observed_at >= ?
            GROUP BY req_id
            """,
            (cutoff,),
        ).fetchall()
    return {
        r[0]: {
            "latest": r[1],
            "count": r[2],
            "apps": (r[3] or "").split(","),
            "layers": (r[4] or "").split(","),
        }
        for r in rows
    }


def fitness_behavioral_coverage_per_app(
    declared_reqs_per_app: dict[str, set[str]],
    freshness: dict[str, Any],
) -> dict[str, float]:
    """Per-app: fraction of declared REQs that fired in the freshness window."""
    observed_reqs_per_app: dict[str, set[str]] = {}
    for req_id, info in freshness.items():
        for app in info.get("apps", []):
            if app:
                observed_reqs_per_app.setdefault(app, set()).add(req_id)

    out: dict[str, float] = {}
    for app, declared in declared_reqs_per_app.items():
        if not declared:
            out[app] = 1.0
            continue
        observed = observed_reqs_per_app.get(app, set())
        out[app] = round(len(observed & declared) / len(declared), 3)
    return out


def fitness_layer_emission_breadth(freshness: dict[str, Any]) -> dict[str, Any]:
    """How many layers were observed in the freshness window."""
    seen: set[str] = set()
    for info in freshness.values():
        for layer in info.get("layers", []):
            if layer:
                seen.add(layer)
    return {
        "observed_count": len(seen),
        "total_canonical": len(_ALL_LAYERS),
        "observed": sorted(seen),
        "missing": sorted(_ALL_LAYERS - seen),
    }


def fitness_req_freshness(freshness: dict[str, Any], declared_reqs: set[str]) -> dict[str, float]:
    """Median + p90 age (days) of last observation across ALL declared REQs.

    REQs with no observation contribute their full freshness_sla_days as
    the age (treated as "stale at the SLA boundary"). This makes the
    metric monotonic — adding a never-fired REQ raises the median.
    """
    now_ts = int(time.time())
    ages_days: list[float] = []
    for req_id in declared_reqs:
        info = freshness.get(req_id)
        if info and info.get("latest"):
            age = (now_ts - int(info["latest"])) / 86_400.0
        else:
            age = 30.0  # cold REQ — treat as 30 days old
        ages_days.append(age)

    if not ages_days:
        return {"p50_days": 0.0, "p90_days": 0.0, "n": 0}
    p50 = statistics.median(ages_days)
    p90 = statistics.quantiles(ages_days, n=10)[-1] if len(ages_days) >= 10 else max(ages_days)
    return {
        "p50_days": round(p50, 2),
        "p90_days": round(p90, 2),
        "n": len(ages_days),
    }


def compute_all(
    *,
    contracts_dir: Path = DEFAULT_CONTRACTS_DIR,
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    lookback_days: int = 7,
) -> dict[str, Any]:
    """Compute every fitness function. Pure."""
    contracts = load_contracts(contracts_dir)
    declared_reqs = {c["req_id"] for c in contracts}
    declared_reqs_per_app: dict[str, set[str]] = {}
    for c in contracts:
        for app in (c.get("expects_spans", {}).get("apps") or []):
            declared_reqs_per_app.setdefault(app, set()).add(c["req_id"])

    freshness = _ledger_freshness(ledger_path, lookback_days)

    coverage_per_app = fitness_behavioral_coverage_per_app(
        declared_reqs_per_app, freshness,
    )
    layer_breadth = fitness_layer_emission_breadth(freshness)
    req_freshness_stats = fitness_req_freshness(freshness, declared_reqs)
    static_runtime = compute_gap(lookback_days=lookback_days, limit=200)
    orphan_count = (
        static_runtime.get("orphan_count", 0) if static_runtime.get("ok") else None
    )
    static_runtime_coverage = (
        static_runtime.get("observability_coverage", 0.0)
        if static_runtime.get("ok") else None
    )

    # Pass/fail per fitness function vs target.
    verdicts: dict[str, dict[str, Any]] = {}
    verdicts["behavioral_coverage_per_app"] = {
        "values": coverage_per_app,
        "target": TARGETS["behavioral_coverage_per_app"],
        "min_observed": (min(coverage_per_app.values()) if coverage_per_app else 0.0),
        "passes": all(
            v >= TARGETS["behavioral_coverage_per_app"]
            for v in coverage_per_app.values()
        ) if coverage_per_app else False,
    }
    verdicts["layer_emission_breadth"] = {
        "value": layer_breadth["observed_count"],
        "target": TARGETS["layer_emission_breadth"],
        "passes": layer_breadth["observed_count"] >= TARGETS["layer_emission_breadth"],
        "missing": layer_breadth["missing"],
    }
    verdicts["static_runtime_coverage"] = {
        "value": static_runtime_coverage,
        "target": TARGETS["static_runtime_coverage"],
        "passes": (
            static_runtime_coverage is not None
            and static_runtime_coverage >= TARGETS["static_runtime_coverage"]
        ),
    }
    verdicts["req_freshness_p50_days"] = {
        "value": req_freshness_stats["p50_days"],
        "p90": req_freshness_stats["p90_days"],
        "target": TARGETS["req_freshness_p50_days"],
        "passes": (
            req_freshness_stats["p50_days"] <= TARGETS["req_freshness_p50_days"]
        ),
    }
    verdicts["orphan_ingest_count"] = {
        "value": orphan_count,
        "target": TARGETS["orphan_ingest_count"],
        "passes": orphan_count == TARGETS["orphan_ingest_count"]
        if orphan_count is not None else False,
    }

    overall_pass = all(v.get("passes") for v in verdicts.values())
    return {
        "ok": True,
        "generated_at": int(time.time()),
        "lookback_days": lookback_days,
        "declared_reqs": sorted(declared_reqs),
        "declared_count": len(declared_reqs),
        "fitness_functions": verdicts,
        "overall_pass": overall_pass,
        "raw": {
            "coverage_per_app": coverage_per_app,
            "layer_breadth": layer_breadth,
            "req_freshness": req_freshness_stats,
            "static_snapshot": str(latest_static_snapshot() or ""),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(report["generated_at"]))
    lines = [
        "# Runtime Coverage Fitness Report",
        "",
        f"- **Generated:** {ts}",
        f"- **Lookback:** {report['lookback_days']} days",
        f"- **Declared REQs:** {report['declared_count']}",
        f"- **Overall:** {'PASS' if report['overall_pass'] else 'FAIL'}",
        "",
        "## Fitness Functions",
        "",
        "| Function | Target | Observed | Verdict |",
        "|---|---|---|:---:|",
    ]
    f = report["fitness_functions"]
    lines.append(
        f"| behavioral_coverage_per_app | ≥ {f['behavioral_coverage_per_app']['target']} "
        f"| min={f['behavioral_coverage_per_app']['min_observed']} "
        f"| {'✅' if f['behavioral_coverage_per_app']['passes'] else '❌'} |"
    )
    lines.append(
        f"| layer_emission_breadth | ≥ {f['layer_emission_breadth']['target']} "
        f"| {f['layer_emission_breadth']['value']} "
        f"| {'✅' if f['layer_emission_breadth']['passes'] else '❌'} |"
    )
    lines.append(
        f"| static_runtime_coverage | ≥ {f['static_runtime_coverage']['target']} "
        f"| {f['static_runtime_coverage']['value']} "
        f"| {'✅' if f['static_runtime_coverage']['passes'] else '❌'} |"
    )
    lines.append(
        f"| req_freshness_p50_days | ≤ {f['req_freshness_p50_days']['target']} "
        f"| {f['req_freshness_p50_days']['value']} "
        f"(p90={f['req_freshness_p50_days']['p90']}) "
        f"| {'✅' if f['req_freshness_p50_days']['passes'] else '❌'} |"
    )
    lines.append(
        f"| orphan_ingest_count | == {f['orphan_ingest_count']['target']} "
        f"| {f['orphan_ingest_count']['value']} "
        f"| {'✅' if f['orphan_ingest_count']['passes'] else '❌'} |"
    )
    lines.extend([
        "",
        "## Behavioral Coverage by App",
        "",
        "| App | Coverage |",
        "|---|---:|",
    ])
    for app, val in sorted(report["raw"]["coverage_per_app"].items()):
        lines.append(f"| `{app}` | {val:.1%} |")

    if f["layer_emission_breadth"]["missing"]:
        lines.extend([
            "",
            "## Missing Layers",
            "",
            "Layers with **zero** runtime exemplars in the freshness window:",
            "",
        ])
        for layer in f["layer_emission_breadth"]["missing"]:
            lines.append(f"- `{layer}`")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lookback-days", type=int, default=7)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT
        / "docs" / "reports" / "calibration"
        / f"fitness_{time.strftime('%Y_W%V')}.md",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit 1 if any fitness function fails.",
    )
    args = parser.parse_args(argv)

    report = compute_all(lookback_days=args.lookback_days)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_markdown(report), encoding="utf-8")
    print(f"[fitness] wrote {args.out}")

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[fitness] wrote {args.json_out}")

    f = report["fitness_functions"]
    print(
        f"  coverage(min)={f['behavioral_coverage_per_app']['min_observed']}  "
        f"breadth={f['layer_emission_breadth']['value']}/{len(_ALL_LAYERS)}  "
        f"static_runtime={f['static_runtime_coverage']['value']}  "
        f"freshness_p50={f['req_freshness_p50_days']['value']}d  "
        f"orphans={f['orphan_ingest_count']['value']}  "
        f"overall={'PASS' if report['overall_pass'] else 'FAIL'}"
    )
    if args.strict and not report["overall_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
