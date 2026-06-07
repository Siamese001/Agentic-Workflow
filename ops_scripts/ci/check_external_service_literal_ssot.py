#!/usr/bin/env python3
"""Gate AUDIT-3 — external-service literal SSOT ratchet.

Detects hardcoded NOTION/OpenAI/Anthropic API versions, base URLs, and
data-source / page IDs in source files OUTSIDE designated SSOT modules.

Allowlisted SSOT locations (configurable via SSOT_ALLOWLIST below):
    .claude/governance/scripts/_notion_constants.py        (target SSOT W3.1)
    apps_shared/config/environment_config.py
    agentic_core/L0_routing/config/path_constants.py
    agentic_core/L0_routing/config/external_apis_config.py

Tier R (ratchet). Baseline locks current count of out-of-SSOT literals.
"""

from __future__ import annotations

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
    connect_snapshot,
    latest_snapshot,
)

# Match the LITERAL VALUES, not identifier names. Identifier references in
# importing files are legitimate post-consolidation; only hardcoded literal
# values outside SSOT modules are violations.
LITERAL_PATTERNS = (
    "2025-09-03",  # Notion API version literal
    "api.notion.com",  # Notion endpoint literal
    "anthropic.com",
    "openai.com",
    # Wave/Phase DB IDs (UUID4 prefixes — first 8 hex are unique enough)
    "aa8d2507-101e-4384",  # WAVE_PHASE_DB_ID
    "fc7f6bf4-6a73-43cd",  # WAVE_PHASE_DATA_SOURCE_ID
    "6ed25e12-bd92-4352",  # ADR_REGISTRY_DB_ID
    "e59d7640-dc09-48f9",  # ADR_REGISTRY_DS_ID
)

SSOT_ALLOWLIST = (
    ".claude/governance/scripts/_notion_constants.py",
    "apps_shared/config/environment_config.py",
    "agentic_core/L0_routing/config/path_constants.py",
    "agentic_core/L0_routing/config/external_apis_config.py",
)


class ExternalServiceLiteralSsotGate(WiringGate):
    gate_id = "AUDIT_3_external_service_literal_ssot"
    tier = "R"
    baseline_filename = "audit_external_service_literal_ssot.json"

    def run(self, conn: sqlite3.Connection) -> list[Violation]:
        cur = conn.cursor()
        violations: list[Violation] = []
        seen: set[tuple[str, int, str]] = set()
        for pat in LITERAL_PATTERNS:
            cur.execute(
                """
                SELECT file_path, line_no, evidence, severity
                FROM violations
                WHERE evidence LIKE ?
                  AND file_path NOT LIKE 'tests/%'
                  AND file_path NOT LIKE 'archives/%'
                  AND file_path NOT LIKE '%scratch%'
                """,
                (f"%{pat}%",),
            )
            for file_path, line_no, evidence, severity in cur.fetchall():
                # Skip allowlisted SSOT modules
                if any(file_path == ok or file_path.endswith("/" + ok) for ok in SSOT_ALLOWLIST):
                    continue
                key = (file_path, line_no, evidence)
                if key in seen:
                    continue
                seen.add(key)
                violations.append(
                    Violation(
                        gate_id=self.gate_id,
                        tier=self.tier,
                        subject=f"{file_path}:{line_no}",
                        rule="external_service_literal_outside_ssot",
                        detail=f"pattern={pat} evidence={evidence}",
                        extra={
                            "file_path": file_path,
                            "line_no": line_no,
                            "evidence": evidence,
                            "matched_pattern": pat,
                            "source_severity": severity,
                        },
                    )
                )
        return violations


def main() -> int:
    gate = ExternalServiceLiteralSsotGate()
    if "--seed" in sys.argv:
        conn = connect_snapshot(latest_snapshot())
        try:
            raw = gate.run(conn)
        finally:
            conn.close()
        gate.seed_baseline(len(raw))
        print(f"[{gate.gate_id}] baseline seeded: count={len(raw)}")
        return 0
    result = gate.execute()
    if result.baseline_count is not None:
        print(f"[{gate.gate_id}] current={len(result.violations)} baseline={result.baseline_count}")
    return cli_exit(result)


if __name__ == "__main__":
    sys.exit(main())
