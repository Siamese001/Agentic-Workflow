"""V15 Incident Bundle Generator.

_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_1")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_2")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_3")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_4")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_5")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_6")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_7")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_8")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_9")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_10")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_11")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_12")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_13")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_14")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_15")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_16")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_17")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_18")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_19")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_20")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_21")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_22")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_23")
_emit_reads_through("l4", "create_v15_incident_bundle", "urg_read_24")
Creates a deterministic incident bundle directory structure with
placeholder files for evidence collection and analysis.

Usage:
    python ops_scripts/incident/create_v15_incident_bundle.py \\
        --out-dir incident_INC001 --incident-id INC001

Exit codes:
    0 — Bundle created (or already exists, idempotent)
    2 — Directory exists and is non-empty without --force
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SENTINEL = "<!-- V15_INCIDENT_PLACEHOLDER -->"


def _readme(incident_id: str) -> str:
    return f"{SENTINEL}\n# V15 Incident Bundle: {incident_id}\n\n## Incident ID\n\n`{incident_id}`\n\n## Status\n\n- [ ] Triage complete\n- [ ] Root cause identified\n- [ ] Remediation applied\n- [ ] Validation passed\n- [ ] Postmortem written\n\n## Evidence Collection Commands\n\n```bash\n# P1 compliance gate\npython -m pytest tests/guardian/test_v15_p1_compliance.py -q\n\n# P6 refinement gate\npython -m pytest tests/guardian/test_v15_p6_refinement.py -q\n\n# Full guardian suite\npython -m pytest tests/guardian/ -q\n\n# Generate review summary\npython ops_scripts/review/generate_v15_review_summary.py \\\n    --out artifacts/review_summary.md \\\n    --json-out artifacts/review_envelope.json\n\n# Validate policy pack\npython ops_scripts/policy/validate_v15_policy_pack.py \\\n    --path agentic_core/L0_routing/policy/v15_policy_pack.json \\\n    --json-out artifacts/policy_envelope.json\n```\n\n## Bundle Contents\n\n- `inputs/` — Environment snapshot and command log\n- `artifacts/` — Collected evidence (guardian report, review summary, policy pack)\n- `analysis/` — Triage, root cause, and remediation notes\n\n## Playbook\n\nSee `docs/runbooks/v15_incident_playbook.md` for the full incident response procedure.\n"


def _env_snapshot() -> str:
    return f"{SENTINEL}\n# Environment Snapshot\n\nCapture the following and paste here:\n\n- V15_ENFORCEMENT value: <value>\n- Python version: <version>\n- Branch: <branch>\n- Last commit hash: <hash>\n- Agent count (from discovery): <count>\n"


def _command_log() -> str:
    return f"{SENTINEL}\n# Command Log\n\nRecord commands executed during incident response:\n\n1. <command and output>\n2. <command and output>\n"


def _guardian_report_placeholder() -> str:
    return f"{SENTINEL}\nCopy the guardian_report.json from:\n  agentic_core/L0_routing/logs/guardian_report.json\n\nOr generate fresh:\n  python -m pytest tests/guardian/ -q\n"


def _review_summary_placeholder() -> str:
    return f"{SENTINEL}\nGenerate and copy here:\n  python ops_scripts/review/generate_v15_review_summary.py \\\n      --out artifacts/review_summary.md\n"


def _policy_pack_placeholder() -> str:
    return f"{SENTINEL}\nCopy the policy pack from:\n  agentic_core/L0_routing/config/v15_policy_pack.json\n"


def _triage() -> str:
    return f"{SENTINEL}\n# Triage\n\n## Violation Type\n\n- [ ] PIPE (pipe-order violation)\n- [ ] POLICY (policy-config mutation)\n- [ ] HASH (rollback hash mismatch)\n- [ ] CLOCK (semantic clock anomaly)\n\n## Severity\n\n- [ ] SEV-1 (HARD_FAIL)\n- [ ] SEV-2 (SOFT_FAIL)\n- [ ] SEV-3 (LOG_ONLY)\n\n## Affected Components\n\n- Manifest correlation_id: <id>\n- Gateway trace_id: <id>\n- Agent(s): <list>\n\n## Initial Assessment\n\n<notes>\n"


def _root_cause() -> str:
    return f"{SENTINEL}\n# Root Cause Analysis\n\n## Summary\n\n<one-line summary>\n\n## Technical Details\n\n<detailed explanation>\n\n## Contributing Factors\n\n- <factor 1>\n- <factor 2>\n"


def _remediation() -> str:
    return f'{SENTINEL}\n# Remediation\n\n## Fix Description\n\n<what was changed>\n\n## Validation\n\n- [ ] P1 gate passes\n- [ ] P6 gate passes\n- [ ] No new violations in LOG_ONLY mode\n- [ ] Review summary: "Ready for human approval: YES"\n\n## Commit Reference\n\n<commit hash>\n'


BUNDLE_FILES: dict[str, callable] = {
    "inputs/env_snapshot.txt": _env_snapshot,
    "inputs/command_log.txt": _command_log,
    "artifacts/guardian_report.json": _guardian_report_placeholder,
    "artifacts/review_summary.md": _review_summary_placeholder,
    "artifacts/policy_pack.json": _policy_pack_placeholder,
    "analysis/triage.md": _triage,
    "analysis/root_cause.md": _root_cause,
    "analysis/remediation.md": _remediation,
}


def create_bundle(out_dir: Path, incident_id: str, force: bool = False) -> tuple[int, list[str]]:
    """Create an incident bundle.

    Returns:
        (exit_code, messages)
        0 = created or idempotent no-op
        2 = non-empty dir without --force
    """
    messages: list[str] = []
    if out_dir.is_dir() and any(out_dir.iterdir()):
        if not force:
            readme = out_dir / "README.md"
            if readme.is_file() and SENTINEL in readme.read_text(encoding="utf-8"):
                messages.append(f"Bundle already exists at {out_dir.name} (idempotent, no changes)")
                return (0, messages)
            messages.append(f"Directory {out_dir.name} exists and is non-empty. Use --force to overwrite.")
            return (2, messages)
    for subdir in ["inputs", "artifacts", "analysis"]:
        (out_dir / subdir).mkdir(parents=True, exist_ok=True)
    readme_path = out_dir / "README.md"
    _write_if_placeholder(readme_path, _readme(incident_id), force)
    for rel_path, content_fn in sorted(BUNDLE_FILES.items()):
        file_path = out_dir / rel_path
        _write_if_placeholder(file_path, content_fn(), force)
    messages.append(f"Bundle created at {out_dir.name} for incident {incident_id}")
    return (0, messages)


def _write_if_placeholder(path: Path, content: str, force: bool) -> None:
    """Write content only if file is missing or contains our sentinel (placeholder).

    Never overwrites user-edited content (sentinel removed), even with --force.
    --force only controls whether the bundle is created in a non-empty dir.
    """
    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        if SENTINEL in existing:
            path.write_text(content, encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a V15 incident bundle.")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory for the bundle")
    parser.add_argument("--incident-id", type=str, required=True, help="Incident identifier")
    parser.add_argument("--force", action="store_true", help="Overwrite existing non-empty directory")
    args = parser.parse_args()
    exit_code, messages = create_bundle(
        out_dir=Path(args.out_dir), incident_id=args.incident_id, force=args.force
    )
    for msg in messages:
        if exit_code == 0:
            print(msg)
        else:
            print(msg, file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
