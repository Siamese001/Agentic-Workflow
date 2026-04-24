"""Causal chain "why did this happen" tool.

Combines three runtime signals to explain a failure:
    1. Static ADG — who imports/flows to this node? what swallows its errors?
    2. Runtime ADG — did a span touch this node? what surrounded it?
    3. Decision ledgers — has a similar failure / fix been recorded before?

Usage (library)::

    from tools.adg.causal_chain import CausalChain
    cc = CausalChain()
    report = cc.explain_node("agentic_core.L5_safety.guardrail")

CLI::

    python tools/adg/causal_chain.py explain agentic_core.L5_safety.guardrail
    python tools/adg/causal_chain.py span <trace_id>     # requires otel ledger

Output is structured JSON by default; pass ``--format=text`` for a
human-readable synopsis.

Design:
- Pure read. Never mutates any store.
- Fail-soft — each signal is optional. A missing ledger or runtime ADG
  simply drops that section from the report instead of erroring.
- No MCP hops — direct SQLite to stay fast and thread-safe.
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT_FOR_IMPORT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT_FOR_IMPORT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT_FOR_IMPORT))

from tools.adg.runtime_query import RuntimeADGQuery, get_default_query  # noqa: E402

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = REPO_ROOT / "artifacts" / "ledgers"
REFACTOR_OUTCOME_LEDGER = LEDGER_DIR / "refactor_outcome.sqlite"


@dataclass
class CausalReport:
    """Structured output of a causal-chain explanation."""

    target: str
    snapshot_id: str | None
    resolved: dict[str, Any] = field(default_factory=dict)
    blast_radius: dict[str, Any] = field(default_factory=dict)
    upstream_callers: list[dict[str, Any]] = field(default_factory=list)
    swallow_sites: list[dict[str, Any]] = field(default_factory=list)
    centrality: dict[str, Any] = field(default_factory=dict)
    precedent: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "snapshot_id": self.snapshot_id,
            "resolved": self.resolved,
            "blast_radius": self.blast_radius,
            "upstream_callers": self.upstream_callers,
            "swallow_sites": self.swallow_sites,
            "centrality": self.centrality,
            "precedent": self.precedent,
            "summary": self.summary,
        }


class CausalChain:
    """Assemble a causal-chain report for a symbol."""

    def __init__(
        self,
        query: RuntimeADGQuery | None = None,
        ledger_path: Path | None = None,
    ) -> None:
        self._q = query if query is not None else get_default_query()
        self._ledger = ledger_path or REFACTOR_OUTCOME_LEDGER

    # ---------- public ----------

    def explain_node(self, identifier: str, *, swallow_depth: int = 3, max_callers: int = 5) -> CausalReport:
        """Return a causal chain explanation for a single node."""
        report = CausalReport(target=identifier, snapshot_id=None)
        if self._q is None:
            report.summary = "ADG snapshot unavailable; cannot compute causal chain."
            return report

        env = self._q.blast_radius(identifier)
        report.snapshot_id = env.snapshot_id
        report.resolved = {
            "node_id": env.node_id,
            "adg_name": env.adg_name,
            "file_path": env.file_path,
            "layer": env.layer,
        }
        report.blast_radius = {
            "fan_in": env.fan_in,
            "fan_out": env.fan_out,
            "archetype": env.archetype,
            "risk_band": env.risk_band,
            "impact_score": env.impact_score,
            "error": env.error,
        }
        if env.node_id is None:
            report.summary = f"Node {identifier!r} not found in snapshot {env.snapshot_id}."
            return report

        report.upstream_callers = self._q.upstream_callers(env.node_id, k=max_callers)
        report.swallow_sites = self._q.swallow_sites_reaching(env.node_id, depth=swallow_depth, max_hits=10)
        report.centrality = self._q.hotspot_info(identifier)
        report.precedent = self._lookup_precedent(env)
        report.summary = self._summarize(env, report)
        return report

    def explain_span(self, trace_id: str) -> dict[str, Any]:
        """Placeholder for runtime-ADG span explanation.

        When the runtime ADG store (``system_learning/runtime_adg``) exposes
        a stable read API keyed on trace_id, wire it here. For now, surface
        a guidance stub so CLI callers get a structured answer rather than
        a silent failure — true to the fail-soft contract.
        """
        return {
            "trace_id": trace_id,
            "status": "runtime_adg_read_path_not_wired",
            "guidance": (
                "Use mcp7 `otel_trace` or `otel_healing_chain` to pull the span, "
                "then pipe resolved nodes through `explain_node(<adg_name>)`."
            ),
        }

    # ---------- precedent ledger join ----------

    def _lookup_precedent(self, env: Any) -> list[dict[str, Any]]:
        """Return up to 5 prior refactor-outcome rows for this file / adg_name.

        The ``refactor_outcome`` ledger stores predicted vs. actual deltas for
        committed refactors. Matching the current file / layer surface prior
        work helps the reviewer reason about "has this been touched before?"
        """
        if not self._ledger.exists():
            return []
        if env.file_path is None:
            return []
        try:
            with sqlite3.connect(
                f"file:{self._ledger.as_posix()}?mode=ro&immutable=1", uri=True, timeout=0.5
            ) as conn:
                conn.row_factory = sqlite3.Row
                # Schema may evolve — use a liberal SELECT and tolerate missing cols.
                cur = conn.execute(
                    "SELECT * FROM sqlite_master WHERE type='table' AND name='refactor_outcome' LIMIT 1"
                )
                if cur.fetchone() is None:
                    return []
                rows = conn.execute(
                    "SELECT * FROM refactor_outcome "
                    "WHERE file_path = ? OR target_adg_name = ? "
                    "ORDER BY created_at DESC LIMIT 5",
                    (env.file_path, env.adg_name),
                ).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error as exc:
            logger.debug("precedent lookup failed: %s", exc)
            return []

    # ---------- summary ----------

    @staticmethod
    def _summarize(env: Any, report: CausalReport) -> str:
        parts: list[str] = []
        parts.append(
            f"{env.adg_name} [{env.layer}] "
            f"archetype={env.archetype} band={env.risk_band} "
            f"(fan_in={env.fan_in}, fan_out={env.fan_out}, impact={env.impact_score})"
        )
        if report.swallow_sites:
            kinds = {s["antipattern_kind"] for s in report.swallow_sites}
            parts.append(f"{len(report.swallow_sites)} swallow site(s) reachable: {sorted(kinds)}")
        else:
            parts.append("no swallow sites detected within depth")
        crit = report.centrality.get("criticality_score")
        if crit:
            parts.append(f"criticality={crit}")
        if report.precedent:
            parts.append(f"{len(report.precedent)} precedent row(s) in refactor_outcome ledger")
        if env.fan_in >= 20:
            parts.append("HIGH fan-in: a failure here is amplified across many callers")
        return " | ".join(parts)


# ---------- CLI ----------


def _cmd_explain(args: argparse.Namespace) -> int:
    cc = CausalChain()
    report = cc.explain_node(
        args.identifier,
        swallow_depth=args.swallow_depth,
        max_callers=args.max_callers,
    )
    if args.format == "text":
        print(report.summary)
        print()
        print(f"  target  : {report.target}")
        print(f"  node_id : {report.resolved.get('node_id')}")
        print(f"  file    : {report.resolved.get('file_path')}")
        print(f"  layer   : {report.resolved.get('layer')}")
        if report.upstream_callers:
            print(f"  top upstream callers ({len(report.upstream_callers)}):")
            for c in report.upstream_callers:
                print(f"    - {c.get('adg_name')} [{c.get('layer')}]")
        if report.swallow_sites:
            print(f"  swallow sites ({len(report.swallow_sites)}):")
            for s in report.swallow_sites:
                print(f"    - hops={s.get('hops')} {s.get('antipattern_kind')} at {s.get('adg_name')}")
        if report.precedent:
            print(f"  precedent ({len(report.precedent)} refactor-outcome rows)")
        return 0
    print(json.dumps(report.to_dict(), indent=2, default=str))
    return 0


def _cmd_span(args: argparse.Namespace) -> int:
    cc = CausalChain()
    result = cc.explain_span(args.trace_id)
    print(json.dumps(result, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("explain", help="Explain a node by adg_name or node_id")
    pe.add_argument("identifier")
    pe.add_argument("--swallow-depth", type=int, default=3)
    pe.add_argument("--max-callers", type=int, default=5)
    pe.add_argument("--format", choices=["json", "text"], default="json")
    pe.set_defaults(func=_cmd_explain)

    ps = sub.add_parser("span", help="Explain a runtime span by trace_id")
    ps.add_argument("trace_id")
    ps.set_defaults(func=_cmd_span)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
