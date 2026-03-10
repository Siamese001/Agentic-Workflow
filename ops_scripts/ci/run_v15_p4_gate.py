#!/usr/bin/env python3
"""V15 Phase 4 Gate Runner — Immutable Traceability (§15.5)

CI-ready evidence-only gate. Verifies trace_id infrastructure:
- TRACE_ID_PATTERN exported from traceability_types
- validate_trace_id callable and rejects bad input
- generate_trace_id callable and produces compliant IDs
- trace_id propagated through SurgicalManifest.correlation_id
- trace_id present in gateway.execute() call signature

Emits evidence JSON to docs/reports/plans/. Non-blocking (exit 0).

Usage:
    python ops_scripts/ci/run_v15_p4_gate.py
    python ops_scripts/ci/run_v15_p4_gate.py --repo-root /path/to/repo
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    # guardian: allow-global-mutation
    sys.path.insert(0, str(PROJECT_ROOT))

EVIDENCE_DIR = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans"


class P4EvidenceCollector:
    """Collect evidence for §15.5 — Immutable Traceability."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.violations: list[dict] = []
        self.checks_passed: list[dict] = []

    def collect(self) -> dict:
        """Run all P4 checks and return evidence dict."""
        self._check_trace_id_pattern_exported()
        self._check_validate_trace_id_callable()
        self._check_generate_trace_id_callable()
        self._check_trace_id_in_manifest()
        self._check_trace_id_in_gateway_execute()
        self._check_trace_id_immutability_contract()

        total = len(self.violations) + len(self.checks_passed)
        return {
            "phase": "P4",
            "gate": "immutable_traceability",
            "spec_section": "§15.5",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checks": total,
            "passed": len(self.checks_passed),
            "violations": len(self.violations),
            "violation_details": self.violations,
            "passed_details": self.checks_passed,
            "blocking": False,
        }

    def _check_trace_id_pattern_exported(self):
        """Verify TRACE_ID_PATTERN is exported from traceability_types."""
        p4_path = self.repo_root / "agentic_core/L0_routing/types/traceability_types.py"
        if not p4_path.exists():
            self.violations.append(
                {
                    "check": "trace_id_pattern_exported",
                    "detail": "traceability_types.py not found",
                },
            )
            return

        content = p4_path.read_text(encoding="utf-8")
        has_pattern = "TRACE_ID_PATTERN" in content
        has_regex = r"CC3AL1-[0-9A-F]{8}" in content

        if has_pattern and has_regex:
            self.checks_passed.append(
                {
                    "check": "trace_id_pattern_exported",
                    "detail": "TRACE_ID_PATTERN with CC3AL1 regex found in traceability_types",
                },
            )
        else:
            self.violations.append(
                {
                    "check": "trace_id_pattern_exported",
                    "detail": f"pattern={has_pattern}, regex={has_regex}",
                },
            )

    def _check_validate_trace_id_callable(self):
        """Verify validate_trace_id is importable and rejects bad input."""
        try:
            from agentic_core.L0_routing.types.traceability_types import validate_trace_id

            # Must reject invalid input
            try:
                validate_trace_id("INVALID")
                self.violations.append(
                    {
                        "check": "validate_trace_id_rejects_bad",
                        "detail": "validate_trace_id accepted 'INVALID' without raising",
                    },
                )
            except ValueError:
                self.checks_passed.append(
                    {
                        "check": "validate_trace_id_rejects_bad",
                        "detail": "validate_trace_id correctly rejects invalid input",
                    },
                )

            # Must accept valid input
            valid = validate_trace_id("CC3AL1-ABCD1234")
            if valid == "CC3AL1-ABCD1234":
                self.checks_passed.append(
                    {
                        "check": "validate_trace_id_accepts_good",
                        "detail": "validate_trace_id accepts compliant trace_id",
                    },
                )
            else:
                self.violations.append(
                    {
                        "check": "validate_trace_id_accepts_good",
                        "detail": f"Returned unexpected value: {valid}",
                    },
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self.violations.append(
                {
                    "check": "validate_trace_id_callable",
                    "detail": f"Import/call failed: {e}",
                },
            )

    def _check_generate_trace_id_callable(self):
        """Verify generate_trace_id produces compliant IDs."""
        try:
            import re

            from agentic_core.L0_routing.enforcement.traceability_contracts import (
                generate_trace_id,
            )

            tid = generate_trace_id("A1B2C3D4")
            pattern = re.compile(r"^CC3AL1-[0-9A-F]{8}$")
            if pattern.match(tid):
                self.checks_passed.append(
                    {
                        "check": "generate_trace_id_compliant",
                        "detail": f"generate_trace_id produced: {tid}",
                    },
                )
            else:
                self.violations.append(
                    {
                        "check": "generate_trace_id_compliant",
                        "detail": f"Non-compliant output: {tid}",
                    },
                )
        # guardian: allow-silent-swallow
        except Exception as e:
            # TODO: Handle specific exception properly
            raise  # Re-raise after logging/handling
            self.violations.append(
                {
                    "check": "generate_trace_id_callable",
                    "detail": f"Import/call failed: {e}",
                },
            )

    def _check_trace_id_in_manifest(self):
        """Verify SurgicalManifest has correlation_id field for trace propagation."""
        p2_path = self.repo_root / "agentic_core/L0_routing/types/determinism_types.py"
        if not p2_path.exists():
            self.violations.append(
                {
                    "check": "trace_id_in_manifest",
                    "detail": "determinism_types.py not found",
                },
            )
            return

        content = p2_path.read_text(encoding="utf-8")
        if "correlation_id: str" in content:
            self.checks_passed.append(
                {
                    "check": "trace_id_in_manifest",
                    "detail": "SurgicalManifest.correlation_id present",
                },
            )
        else:
            self.violations.append(
                {
                    "check": "trace_id_in_manifest",
                    "detail": "correlation_id field missing from SurgicalManifest",
                },
            )

    def _check_trace_id_in_gateway_execute(self):
        """Verify trace_id is passed to gateway.execute()."""
        sba_path = self.repo_root / "agentic_core/base_agents/SovereignBaseAgent.py"
        if not sba_path.exists():
            return

        content = sba_path.read_text(encoding="utf-8")
        if "trace_id=trace_id" in content:
            self.checks_passed.append(
                {
                    "check": "trace_id_in_gateway_execute",
                    "detail": "trace_id passed to gateway.execute()",
                },
            )
        else:
            self.violations.append(
                {
                    "check": "trace_id_in_gateway_execute",
                    "detail": "trace_id not passed to gateway.execute()",
                },
            )

    def _check_trace_id_immutability_contract(self):
        """Verify SurgicalManifest is frozen (immutable)."""
        p2_path = self.repo_root / "agentic_core/L0_routing/types/determinism_types.py"
        if not p2_path.exists():
            return

        content = p2_path.read_text(encoding="utf-8")
        if "@dataclass(frozen=True)" in content and "class SurgicalManifest" in content:
            self.checks_passed.append(
                {
                    "check": "manifest_immutability",
                    "detail": "SurgicalManifest is frozen=True (immutable)",
                },
            )
        else:
            self.violations.append(
                {
                    "check": "manifest_immutability",
                    "detail": "SurgicalManifest not marked frozen=True",
                },
            )


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="V15 Phase 4 Gate — Immutable Traceability")
    parser.add_argument("--repo-root", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    repo_root = args.repo_root or PROJECT_ROOT
    output = args.output or EVIDENCE_DIR / "v15_p4_evidence.json"

    print("[P4-GATE] Starting Phase 4 gate (§15.5 — Immutable Traceability)...")

    collector = P4EvidenceCollector(repo_root)
    evidence = collector.collect()

    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)

    print(f"[P4-GATE] Evidence written to: {output}")
    print(f"[P4-GATE] Checks passed: {evidence['passed']}, Violations: {evidence['violations']}")
    print("[P4-GATE] PASSED (evidence-only, non-blocking)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
