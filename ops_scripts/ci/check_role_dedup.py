#!/usr/bin/env python3
"""Gate D2 — role duplication with orphans (plan W3.4).

Groups production modules by common *role suffix* (e.g. ``*_reranker``,
``*_retriever``, ``*_planner``, ``*_router``). For every role cluster
with more than one module, if any member has ``fan_in=0`` on imports,
flag the whole cluster as a WARN — this is the signature of a shadow
SSOT being rebuilt alongside the real one, which the C0 Context
Engine failure demonstrated (three ``*_reranker`` modules, two
orphaned).

Tier: W (warn). Never fails CI; surfaces a signal for human review.
The D1_layer_doc_binding gate already occupies tier W for doc drift;
this gate uses a distinct gate_id (D2_role_duplication_warn).
"""

from __future__ import annotations

# W6 ADG consumer mode declaration (per .windsurf/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import re
import sqlite3
import sys
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)

# Role-suffix patterns. Keep tight: overly generic suffixes like ``_engine``
# or ``_manager`` would flood the warn channel and drown the real signal.
ROLE_SUFFIXES = (
    "_reranker",
    "_retriever",
    "_planner",
    "_router",
    "_dispatcher",
    "_classifier",
    "_ranker",
    "_selector",
    "_scorer",
    "_extractor",
)

_STEM_RE = re.compile(r"([A-Za-z0-9_]+)\.py$")


def _role_for(path: str) -> str | None:
    m = _STEM_RE.search(path)
    if not m:
        return None
    stem = m.group(1).lower()
    for suffix in ROLE_SUFFIXES:
        if stem.endswith(suffix):
            return suffix.lstrip("_")
    return None


class RoleDedupGate(WiringGate):
    gate_id = "D2_role_duplication_warn"
    tier = "W"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        # Pull every production module with its fan-in count on imports.
        rows = conn.execute(
            """
            SELECT n.resolved_path,
                   n.layer,
                   COALESCE((
                       SELECT COUNT(*) FROM edges e
                       WHERE e.dst_id = n.id AND e.relation_type = 'imports'
                   ), 0) AS fan_in
            FROM nodes n
            WHERE n.entity_type = 'module'
              AND n.resolved_path IS NOT NULL
              AND n.resolved_path NOT LIKE 'tests/%'
              AND n.resolved_path NOT LIKE 'archives/%'
              AND n.resolved_path NOT LIKE '%/archive/%'
            """
        ).fetchall()

        clusters: dict[str, list[tuple[str, str, int]]] = {}
        for resolved_path, layer, fan_in in tqdm(rows, desc="D2_role_dedup_scan", unit="mod"):
            role = _role_for(resolved_path)
            if not role:
                continue
            clusters.setdefault(role, []).append((resolved_path, layer, fan_in))

        violations: list[Violation] = []
        for role, members in tqdm(list(clusters.items()), desc="D2_role_dedup_cluster", unit="role"):
            if len(members) < 2:
                continue
            orphans = [m for m in members if m[2] == 0]
            if not orphans:
                continue
            # Emit one violation row per orphaned member — downstream
            # reporting will group by the ``role_cluster`` in ``extra``.
            for path, layer, fan_in in tqdm(orphans, desc=f"D2_orphans[{role}]", unit="mod", leave=False):
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=path,
                        rule="role_cluster_has_orphan",
                        severity="warn",
                        detail=(
                            f"role={role}; cluster_size={len(members)}; this_fan_in={fan_in}; layer={layer}"
                        ),
                        extra={
                            "role_cluster": role,
                            "cluster_size": len(members),
                            "cluster_members": [m[0] for m in members],
                            "layer": layer,
                        },
                    )
                )
        return violations


def main() -> int:
    gate = RoleDedupGate()
    result = gate.execute()
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
