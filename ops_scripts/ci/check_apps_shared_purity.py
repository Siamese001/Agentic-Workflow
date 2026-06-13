#!/usr/bin/env python3
"""apps_shared purity gate — block any import from apps_shared/ into apps_<domain>/.

The point of apps_shared is to be the L_SHARED infrastructure layer with NO
domain logic. Domain apps (apps_eval, apps_exec, apps_lic, apps_research,
apps_underwriting_ai, apps_rg) MUST NOT be imported by apps_shared,
ever — otherwise we get a circular dependency between the shared layer and the
domain layer it claims to be below.

This gate uses direct SQLite queries against the canonical ADG snapshot
(per constitutional §28: SQLite-direct fallback supersedes grep). It does
NOT use grep, because grep would have false positives on string literals
that look like imports.

Tier: B (block) — any violation fails CI.

Bypass: WIRING_GATE_BYPASS=1
Snapshot pin: ADG_SNAPSHOT=<path>

Author-Gate: this gate is constitutional once it lands — relaxing it requires
an ADR and the SVP review documents (apps_shared/SVP_ENGINEERING_REVIEW.md)
must be updated to declare the new boundary.
"""

from __future__ import annotations

# W6 ADG consumer mode declaration.
__adg_consumer_mode__ = "inventory"


import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops_scripts.ci._adg_wiring_gate_base import (  # noqa: E402
    Violation,
    WiringGate,
    cli_exit,
)


# Domain apps — apps_shared MUST NOT import from these.
_DOMAIN_APPS: tuple[str, ...] = (
    "apps_eval",
    "apps_exec",
    "apps_lic",
    "apps_research",
    "apps_underwriting_ai",
    "apps_rg",
)


class AppsSharedPurityGate(WiringGate):
    gate_id = "B_apps_shared_purity"
    tier = "B"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        # Build the destination clause once.
        path_clauses = " OR ".join(
            [f"n.resolved_path LIKE '{a}/%'" for a in _DOMAIN_APPS]
        )
        name_clauses = " OR ".join(
            [f"n.adg_name LIKE '{a}%'" for a in _DOMAIN_APPS]
        )
        query = f"""
            SELECT e.source_file, n.adg_name, n.resolved_path, e.line_no
            FROM edges e
            LEFT JOIN nodes n ON n.id = e.dst_id
            WHERE e.relation_type = 'imports'
              AND e.source_file LIKE 'apps_shared/%'
              AND (({path_clauses}) OR ({name_clauses}))
        """
        violations: list[Violation] = []
        for source_file, adg_name, resolved_path, line_no in conn.execute(query):
            target = resolved_path or adg_name or "<unknown>"
            violations.append(
                Violation(
                    gate_id=self.gate_id,
                    tier=self.tier,
                    subject=f"{source_file}:{line_no}",
                    rule="apps_shared_imports_domain_app",
                    detail=(
                        f"apps_shared/{source_file.split('/', 1)[1] if '/' in source_file else source_file} "
                        f"imports from domain layer: {target}. "
                        "apps_shared must remain L_SHARED — domain logic belongs in the consuming app."
                    ),
                    extra={
                        "source_file": source_file,
                        "target_adg_name": adg_name,
                        "target_resolved_path": resolved_path,
                        "line_no": line_no,
                    },
                )
            )
        return violations


def main() -> int:
    return cli_exit(AppsSharedPurityGate().execute())


if __name__ == "__main__":
    sys.exit(main())
