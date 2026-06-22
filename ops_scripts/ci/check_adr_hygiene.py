#!/usr/bin/env python3
"""ADR hygiene gate.

Default mode is advisory because the current tree has known duplicate ADR
numbers and noncanonical ADR-like files. Strict mode is available for future
cleanup waves and for testing new drift rules.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from ops_scripts.ci.inventory_adr_liveness import AdrRecord, build_inventory

REPO_ROOT = Path(__file__).resolve().parents[2]

KNOWN_NONCANONICAL_ALLOWLIST = {
    "docs/adr/ADR-00C-7-gate-verdict-ssot-b8e4f2.md",
    "docs/adr/ADR-081-apps-e2e-spine-cert-wireup.md",
    "docs/adr/ADR-082-multi-provider-judge-panel-harness.md",
    "docs/adr/ADR-085-same-authority-incremental-regen.md",
    "docs/adr/ADR-086-judge-directed-regen-apps-orchestrator.md",
    "docs/adr/ADR-apps-rg-spine-only-unification.md",
    "docs/adr/RCA_WINDSURF_PWSH_EXIT_CODE_1.md",
    "docs/adr/gate-promotion/AG-PURITY-advisory-to-strict.md",
    "docs/adr/semantic_cache_threshold_recalibration.md",
    "docs/architecture/context_assembly_adr.md",
    "docs/architecture/healing_dispatch_routing_adr.md",
    "docs/architecture/l3_l4_stabilization_adr.md",
    "docs/architecture/l3_orchestration_charter_adr.md",
    "docs/architecture/memory_cli_static_audit_adr.md",
    "docs/architecture/sovereign_healing_architecture_adr.md",
    "docs/architecture/unrecoverable_failure_escalation_adr.md",
}

KNOWN_DUPLICATE_NUMBER_ALLOWLIST = {
    "ADR-023",
    "ADR-038",
    "ADR-042",
    "ADR-043",
    "ADR-051",
    "ADR-061",
    "ADR-079",
    "ADR-081",
    "ADR-082",
    "ADR-085",
    "ADR-086",
    "ADR-088",
    "ADR-093",
    "ADR-094",
    "ADR-095",
    "ADR-096",
    "ADR-097",
    "ADR-100",
}


@dataclass(frozen=True)
class HygieneFinding:
    severity: str
    rule: str
    path: str
    detail: str


def duplicate_groups(records: list[AdrRecord]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = defaultdict(list)
    for record in records:
        if record.number:
            groups[record.number].append(record.path)
    return {number: sorted(paths) for number, paths in groups.items() if len(paths) > 1}


def evaluate_hygiene(records: list[AdrRecord]) -> list[HygieneFinding]:
    findings: list[HygieneFinding] = []

    for record in records:
        if record.location != "canonical" and record.path not in KNOWN_NONCANONICAL_ALLOWLIST:
            findings.append(
                HygieneFinding(
                    severity="error",
                    rule="new_noncanonical_adr",
                    path=record.path,
                    detail="ADR-like file is outside docs/architecture/adr and is not allowlisted.",
                )
            )
        if record.location == "canonical" and not record.status:
            findings.append(
                HygieneFinding(
                    severity="warning",
                    rule="canonical_status_missing",
                    path=record.path,
                    detail="Canonical ADR has no parseable Status line; normalize before treating as current truth.",
                )
            )

    for number, paths in duplicate_groups(records).items():
        if number in KNOWN_DUPLICATE_NUMBER_ALLOWLIST:
            severity = "warning"
            detail = "Known duplicate ADR number; cleanup requires cross-reference migration."
        else:
            severity = "error"
            detail = "New duplicate ADR number outside the known cleanup allowlist."
        findings.append(
            HygieneFinding(
                severity=severity,
                rule="duplicate_adr_number",
                path=number,
                detail=f"{detail} Files: {', '.join(paths)}",
            )
        )

    return sorted(findings, key=lambda f: (f.severity, f.rule, f.path))


def findings_payload(findings: list[HygieneFinding], records: list[AdrRecord]) -> dict:
    return {
        "summary": {
            "records": len(records),
            "findings": len(findings),
            "errors": sum(1 for finding in findings if finding.severity == "error"),
            "warnings": sum(1 for finding in findings if finding.severity == "warning"),
        },
        "findings": [asdict(finding) for finding in findings],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check ADR hygiene.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true", help="Exit nonzero on errors.")
    mode.add_argument("--advisory", action="store_true", help="Always exit zero after reporting.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--output", type=Path, default=None, help="Optional report path.")
    args = parser.parse_args(argv)

    records = build_inventory(REPO_ROOT)
    findings = evaluate_hygiene(records)
    payload = findings_payload(findings, records)

    if args.json:
        output = json.dumps(payload, indent=2, sort_keys=True)
    else:
        lines = [
            "[adr_hygiene] "
            f"records={payload['summary']['records']} "
            f"errors={payload['summary']['errors']} "
            f"warnings={payload['summary']['warnings']}"
        ]
        for finding in findings:
            lines.append(f"[{finding.severity}] {finding.rule}: {finding.path} — {finding.detail}")
        output = "\n".join(lines)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    if args.strict and payload["summary"]["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
