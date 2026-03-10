"""Phase 5: L0 Router Blast-Radius scoring.

Inputs:
  - changed modules (git diff)
  - reachable downstream dependents (reverse import graph)
  - layer criticality weights (deterministic, precomputed)

Outputs:
  - ImpactDigest: sha256(sorted impacted nodes + weights)
  - risk_score: integer
  - route_mode: NORMAL | RESTRICTED | HUMAN_REVIEW

Layer criticality weights:
  L0: 100  L1: 80  L2: 90  L3: 70  L4: 60
  L5: 85   L6: 50  L_APP: 40  L_SL: 45
  L_TOOLS: 30  L_OPS: 20  L_UNKNOWN: 10
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from agentic_core.adg.client.mcp_client import ADGMCPClient
from agentic_core.adg.schema import canonical_name, module_path_to_layer

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult

logger = logging.getLogger(__name__)

RouteMode = Literal["NORMAL", "RESTRICTED", "HUMAN_REVIEW"]

_LAYER_WEIGHTS: dict[str, int] = {
    "L0": 100,
    "L1": 80,
    "L2": 90,
    "L3": 70,
    "L4": 60,
    "L5": 85,
    "L6": 50,
    "L_APP": 40,
    "L_SL": 45,
    "L_TOOLS": 30,
    "L_OPS": 20,
    "L_UNKNOWN": 10,
}

_RESTRICTED_THRESHOLD = 300
_HUMAN_REVIEW_THRESHOLD = 700


@dataclass
class BlastRadiusResult:
    """Output of blast-radius scoring for a commit."""

    changed_modules: list[str]
    impacted_modules: list[str]
    risk_score: int
    route_mode: RouteMode
    impact_digest: str
    commit_sha: str = ""

    def print_summary(self) -> None:
        print(
            f"ADG-BLAST-RADIUS: commit={self.commit_sha or 'none'} "
            f"risk_score={self.risk_score} route_mode={self.route_mode} "
            f"impact_digest={self.impact_digest} "
            f"changed={len(self.changed_modules)} impacted={len(self.impacted_modules)}"
        )


def _module_rel(adg_name: str) -> str:
    prefix = "ADG::Module::"
    return adg_name[len(prefix) :] if adg_name.startswith(prefix) else adg_name


def compute_blast_radius(
    changed_files: list[str],
    result: ScanResult,
    commit_sha: str = "",
    client: ADGMCPClient | None = None,
    run_id: str = "",
) -> BlastRadiusResult:
    """Compute deterministic blast-radius score for a set of changed files."""
    from agentic_core.adg.extraction.static_scanner import ADGStaticScanner

    scanner = ADGStaticScanner.__new__(ADGStaticScanner)
    reverse_graph = scanner.build_reverse_import_graph(result)

    changed_adg = [canonical_name("Module", f.replace("\\", "/")) for f in sorted(changed_files)]

    impacted: set[str] = set(changed_adg)
    frontier: list[str] = list(changed_adg)

    while frontier:
        current = frontier.pop()
        sym_name = canonical_name("Symbol", _module_rel(current))
        for dependents_key in (current, sym_name):
            for dependent in reverse_graph.get(dependents_key, []):
                if dependent not in impacted:
                    impacted.add(dependent)
                    frontier.append(dependent)

    impacted_sorted = sorted(impacted)

    score_lines = []
    total_weight = 0
    for adg_name in impacted_sorted:
        rel = _module_rel(adg_name)
        layer = module_path_to_layer(rel)
        weight = _LAYER_WEIGHTS.get(layer, 10)
        total_weight += weight
        score_lines.append(f"{adg_name}:{weight}")

    impact_digest = hashlib.sha256("\n".join(score_lines).encode("utf-8")).hexdigest()

    if total_weight >= _HUMAN_REVIEW_THRESHOLD:
        route_mode: RouteMode = "HUMAN_REVIEW"
    elif total_weight >= _RESTRICTED_THRESHOLD:
        route_mode = "RESTRICTED"
    else:
        route_mode = "NORMAL"

    br_result = BlastRadiusResult(
        changed_modules=sorted(changed_files),
        impacted_modules=[_module_rel(n) for n in impacted_sorted],
        risk_score=total_weight,
        route_mode=route_mode,
        impact_digest=impact_digest,
        commit_sha=commit_sha,
    )

    if client is not None and (commit_sha or run_id):
        _persist_blast_radius(br_result, client, run_id, commit_sha)

    return br_result


def _persist_blast_radius(
    br: BlastRadiusResult,
    client: ADGMCPClient,
    run_id: str,
    commit_sha: str,
) -> None:
    if run_id:
        run_node = canonical_name("Run", run_id)
        client.upsert_entity(
            run_node,
            "scan_run",
            [
                f"commit:{commit_sha}",
                f"risk_score:{br.risk_score}",
                f"route_mode:{br.route_mode}",
                f"impact_digest:{br.impact_digest}",
                f"impacted_count:{len(br.impacted_modules)}",
            ],
        )
    if commit_sha:
        snap_node = canonical_name("Snapshot", commit_sha, "blast_radius")
        client.upsert_entity(
            snap_node,
            "snapshot",
            [
                f"commit:{commit_sha}",
                f"risk_score:{br.risk_score}",
                f"route_mode:{br.route_mode}",
                f"impact_digest:{br.impact_digest}",
                f"impacted_count:{len(br.impacted_modules)}",
            ],
        )


__all__ = ["compute_blast_radius", "BlastRadiusResult", "RouteMode"]
