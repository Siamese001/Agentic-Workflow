"""Gate 8: P0 Infrastructure Wiring Gate.

Blocks direct infrastructure imports (redis, chromadb, sqlite3, boto3,
openai, anthropic, httpx, requests, neo4j, prometheus_client, aiohttp,
google) in production layers. Sanctioned adapter files and directories
(``tools/``, ``infrastructure/``, ``apps_shared``, and the adapter
allowlist in ``infra_wiring_scan.py``) may freely import raw SDKs.

Detection (delegated to ``ops_scripts/ci/infra_wiring_scan.py``):

  * ``scan_directory`` — AST-style line scan of production trees
    (agentic_core + apps_*), honouring the sanctioned-adapter allowlist.

Source views:
    Raw ADG tables (``nodes``, ``edges``) — the gate does not depend on
    a materialized view. The standalone script *does* also check the
    ``v_p0_l1_direct_infra`` view when present, but that is advisory;
    the file scan is authoritative and snapshot-independent.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _bootstrap_repo_root() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    return repo_root


_REPO_ROOT = _bootstrap_repo_root()

from ops_scripts.ci.adg_gates.gate_base import (  # noqa: E402
    ADGGateBase,
    GateResult,
    GateViolation,
)
from ops_scripts.ci.infra_wiring_scan import scan_directory  # noqa: E402

# Map each forbidden import prefix to a short infra tag for reporting.
_INFRA_TAG_RE = re.compile(r"(?:import|from)\s+([a-zA-Z0-9_]+)")


def _infer_infra(import_pattern: str) -> str:
    match = _INFRA_TAG_RE.match(import_pattern.strip())
    return match.group(1) if match else "unknown"


def _shorten_path(path: Path) -> str:
    try:
        return str(path.relative_to(_REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


class InfraWiringGate(ADGGateBase):
    """P0 gate blocking direct infrastructure imports in production layers.

    Wraps the standalone ``infra_wiring_scan.py`` detection so it
    participates in the ADG suite with provenance and artifact emission,
    and auto-runs on every ``generate_full_adg.py`` invocation.
    """

    gate_family = "infra_wiring"
    severity = "P0"
    source_views: list[str] = ["nodes", "edges"]

    def _execute_gate_logic(self) -> GateResult:
        summary: dict[str, Any] = {
            "total_violations": 0,
            "files_with_violations": 0,
            "in_modified_area": 0,
            "by_infra": {},
        }

        raw_violations = scan_directory(_REPO_ROOT)

        violations: list[GateViolation] = []
        by_infra: dict[str, int] = {}
        idx = 0

        for abs_path_str, file_violations in raw_violations.items():
            rel_path = _shorten_path(Path(abs_path_str))
            for line_num, import_pattern in file_violations:
                infra = _infer_infra(import_pattern)
                by_infra[infra] = by_infra.get(infra, 0) + 1

                in_mod = self._is_in_modified_area(rel_path)
                if in_mod:
                    summary["in_modified_area"] += 1

                violations.append(
                    GateViolation(
                        violation_id=f"infra_wiring_{idx:03d}_{infra}_{Path(rel_path).stem}",
                        source_view="file_scan",
                        source_node=None,
                        source_edge=None,
                        file=rel_path,
                        line=line_num,
                        layer_src=None,
                        layer_dst=None,
                        path_id=None,
                        first_illegal_hop=f"direct_{infra}_import",
                        # Direct infra imports in production are always sink-class:
                        # they bypass sovereign adapters and break layer sovereignty.
                        path_criticality=3.7,
                        in_modified_area=in_mod,
                        message=(
                            f"Direct {infra!r} import in production layer at line {line_num}: "
                            f"'{import_pattern}'. Route through a sanctioned adapter "
                            f"(see SANCTIONED_ADAPTER_FILES in ops_scripts/ci/infra_wiring_scan.py)."
                        ),
                        extra={"infra": infra, "import_pattern": import_pattern},
                        path_criticality_class="sink",
                    )
                )
                idx += 1

        summary["total_violations"] = len(violations)
        summary["files_with_violations"] = len(raw_violations)
        summary["by_infra"] = by_infra

        status = "blocked" if violations else "passed"

        return GateResult(
            gate_family=self.gate_family,
            severity=self.severity,
            snapshot_id=self._snapshot_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            violations=violations,
            summary=summary,
            policy=self.execution_policy,
        )


def main() -> int:
    gate = InfraWiringGate()
    return gate.run_and_exit()


if __name__ == "__main__":
    sys.exit(main())
