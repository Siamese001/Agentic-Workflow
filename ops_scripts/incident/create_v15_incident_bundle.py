"""V15 Incident Bundle Generator.

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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Sentinel used to detect placeholder vs user-edited content
# ---------------------------------------------------------------------------

SENTINEL = "<!-- V15_INCIDENT_PLACEHOLDER -->"

# ---------------------------------------------------------------------------
# Bundle file contents (deterministic, no timestamps, no machine paths)
# ---------------------------------------------------------------------------


def _readme(incident_id: str) -> str:
    return f"""{SENTINEL}
# V15 Incident Bundle: {incident_id}

## Incident ID

`{incident_id}`

## Status

- [ ] Triage complete
- [ ] Root cause identified
- [ ] Remediation applied
- [ ] Validation passed
- [ ] Postmortem written

## Evidence Collection Commands

```bash
# P1 compliance gate
python -m pytest tests/guardian/test_v15_p1_compliance.py -q

# P6 refinement gate
python -m pytest tests/guardian/test_v15_p6_refinement.py -q

# Full guardian suite
python -m pytest tests/guardian/ -q

# Generate review summary
python ops_scripts/review/generate_v15_review_summary.py \\
    --out artifacts/review_summary.md \\
    --json-out artifacts/review_envelope.json

# Validate policy pack
python ops_scripts/policy/validate_v15_policy_pack.py \\
    --path agentic_core/L0_routing/policy/v15_policy_pack.json \\
    --json-out artifacts/policy_envelope.json
```

## Bundle Contents

- `inputs/` — Environment snapshot and command log
- `artifacts/` — Collected evidence (guardian report, review summary, policy pack)
- `analysis/` — Triage, root cause, and remediation notes

## Playbook

See `docs/runbooks/v15_incident_playbook.md` for the full incident response procedure.
"""


def _env_snapshot() -> str:
    return f"""{SENTINEL}
# Environment Snapshot

Capture the following and paste here:

- V15_ENFORCEMENT value: <value>
- Python version: <version>
- Branch: <branch>
- Last commit hash: <hash>
- Agent count (from discovery): <count>
"""


def _command_log() -> str:
    return f"""{SENTINEL}
# Command Log

Record commands executed during incident response:

1. <command and output>
2. <command and output>
"""


def _guardian_report_placeholder() -> str:
    return f"""{SENTINEL}
Copy the guardian_report.json from:
  agentic_core/L0_routing/logs/guardian_report.json

Or generate fresh:
  python -m pytest tests/guardian/ -q
"""


def _review_summary_placeholder() -> str:
    return f"""{SENTINEL}
Generate and copy here:
  python ops_scripts/review/generate_v15_review_summary.py \\
      --out artifacts/review_summary.md
"""


def _policy_pack_placeholder() -> str:
    return f"""{SENTINEL}
Copy the policy pack from:
  agentic_core/L0_routing/policy/v15_policy_pack.json
"""


def _triage() -> str:
    return f"""{SENTINEL}
# Triage

## Violation Type

- [ ] PIPE (pipe-order violation)
- [ ] POLICY (policy-config mutation)
- [ ] HASH (rollback hash mismatch)
- [ ] CLOCK (semantic clock anomaly)

## Severity

- [ ] SEV-1 (HARD_FAIL)
- [ ] SEV-2 (SOFT_FAIL)
- [ ] SEV-3 (LOG_ONLY)

## Affected Components

- Manifest correlation_id: <id>
- Gateway trace_id: <id>
- Agent(s): <list>

## Initial Assessment

<notes>
"""


def _root_cause() -> str:
    return f"""{SENTINEL}
# Root Cause Analysis

## Summary

<one-line summary>

## Technical Details

<detailed explanation>

## Contributing Factors

- <factor 1>
- <factor 2>
"""


def _remediation() -> str:
    return f"""{SENTINEL}
# Remediation

## Fix Description

<what was changed>

## Validation

- [ ] P1 gate passes
- [ ] P6 gate passes
- [ ] No new violations in LOG_ONLY mode
- [ ] Review summary: "Ready for human approval: YES"

## Commit Reference

<commit hash>
"""


# ---------------------------------------------------------------------------
# Bundle structure definition
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Core logic (importable for tests)
# ---------------------------------------------------------------------------


def create_bundle(
    out_dir: Path,
    incident_id: str,
    force: bool = False,
) -> tuple[int, list[str]]:
    """Create an incident bundle.

    Returns:
        (exit_code, messages)
        0 = created or idempotent no-op
        2 = non-empty dir without --force
    """
    messages: list[str] = []

    # Safety check: non-empty dir without --force
    if out_dir.is_dir() and any(out_dir.iterdir()):
        if not force:
            # Check if this is our own bundle (idempotent case)
            readme = out_dir / "README.md"
            if readme.is_file() and SENTINEL in readme.read_text(encoding="utf-8"):
                messages.append(f"Bundle already exists at {out_dir.name} (idempotent, no changes)")
                return 0, messages
            messages.append(
                f"Directory {out_dir.name} exists and is non-empty. Use --force to overwrite.",
            )
            return 2, messages

    # Create directories
    for subdir in ["inputs", "artifacts", "analysis"]:
        (out_dir / subdir).mkdir(parents=True, exist_ok=True)

    # Create README
    readme_path = out_dir / "README.md"
    _write_if_placeholder(readme_path, _readme(incident_id), force)

    # Create bundle files
    for rel_path, content_fn in sorted(BUNDLE_FILES.items()):
        file_path = out_dir / rel_path
        _write_if_placeholder(file_path, content_fn(), force)

    messages.append(f"Bundle created at {out_dir.name} for incident {incident_id}")
    return 0, messages


def _write_if_placeholder(path: Path, content: str, force: bool) -> None:
    """Write content only if file is missing or contains our sentinel (placeholder).

    Never overwrites user-edited content (sentinel removed), even with --force.
    --force only controls whether the bundle is created in a non-empty dir.
    """
    if path.is_file():
        existing = path.read_text(encoding="utf-8")
        if SENTINEL in existing:
            path.write_text(content, encoding="utf-8")
        # else: user-edited, leave it alone regardless of force
    else:
        path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a V15 incident bundle.")
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory for the bundle")
    parser.add_argument("--incident-id", type=str, required=True, help="Incident identifier")
    parser.add_argument("--force", action="store_true", help="Overwrite existing non-empty directory")
    args = parser.parse_args()

    exit_code, messages = create_bundle(
        out_dir=Path(args.out_dir),
        incident_id=args.incident_id,
        force=args.force,
    )

    for msg in messages:
        if exit_code == 0:
            print(msg)
        else:
            print(msg, file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
