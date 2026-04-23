"""Green-path proof for gate J1 (plan W1.3).

Demonstrates that the CanonicalPipelineWiringGate CORRECTLY returns no
violation when a stage's module has fan-in from the allowed ingress layer.

We build a synthetic one-stage pipeline pointing at
`agentic_core/L0_routing/config/path_constants.py`, which is an L0 module
widely imported from L0/L1/L2 consumers in the current ADG snapshot.

Run: python tools/debug/_w1_j1_green_path_proof.py
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    connect_snapshot,
    latest_snapshot,
)
from ops_scripts.ci.check_canonical_pipeline_wiring import (  # noqa: E402
    CanonicalPipelineWiringGate,
)


def main() -> int:
    snap = latest_snapshot()
    print(f"snapshot: {snap.name}")

    gate = CanonicalPipelineWiringGate(snapshot=snap)

    # Override manifest in-memory with a known-wired target.
    gate.manifest = {
        "version": 1,
        "pipelines": [
            {
                "id": "Synthetic_wired_pipeline",
                "doc": "none",
                "ingress_layer": "L0",
                "stages": [
                    {
                        "id": "S01_wired",
                        "description": "A known-wired L0 module — path_constants.py",
                        "module": "agentic_core/L0_routing/config/path_constants.py",
                        "min_fanin_from_layers": ["L0"],
                        "status": "active",
                    }
                ],
            }
        ],
    }

    conn = connect_snapshot(snap)
    try:
        violations = gate.run(conn)
    finally:
        conn.close()

    print(f"violations: {len(violations)}")
    for v in violations:
        print(f"  - {v.severity} {v.subject} :: {v.rule} — {v.detail}")

    if len(violations) == 0:
        print("GREEN_PATH_PROOF: gate returns no violations when stage is wired.")
        return 0
    print("GREEN_PATH_PROOF: UNEXPECTED FAILURE — gate reported violations.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
