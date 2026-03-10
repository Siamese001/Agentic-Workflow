"""V15 Review Summary Generator.

Reads existing evidence JSON (P3–P6) and guardian_report.json, produces a
deterministic human-readable markdown summary for approval workflows.

Usage:
    python ops_scripts/review/generate_v15_review_summary.py \\
        --out docs/reports/plans/v15_review_summary.md

Exit codes:
    0 — Summary generated (even with partial missing inputs)
    1 — ALL input files missing (nothing to summarize)
"""

from __future__ import annotations

import argparse
import json
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
# Constants
# ---------------------------------------------------------------------------
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root
from agentic_core.L0_routing.types.integration_contract_types import (
    Finding,
    ResultEnvelope,
)

REPO_ROOT = get_validated_project_root()

EVIDENCE_FILES = {
    "P3": REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "v15_p3_evidence.json",
    "P4": REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "v15_p4_evidence.json",
    "P5": REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "v15_p5_evidence.json",
    "P6": REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "v15_p6_evidence.json",
}

GUARDIAN_REPORT_PATHS = [
    REPO_ROOT / "docs" / REPORTS_DIR / "plans" / "guardian_report.json",
    REPO_ROOT / AGENTIC_CORE_DIR / "L0_routing" / "logs" / "guardian_report.json",
]


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> dict | None:
    """Load a JSON file; return None if missing or unparseable."""
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _load_guardian_report() -> dict | None:
    """Try multiple known locations for guardian_report.json."""
    for p in GUARDIAN_REPORT_PATHS:
        data = _load_json(p)
        if data is not None:
            return data
    return None


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------


def generate_summary(
    evidence_files: dict[str, Path] | None = None,
    guardian_report_paths: list[Path] | None = None,
) -> tuple[str, int]:
    """Build the markdown summary string.

    Returns:
        (markdown_string, exit_code)
        exit_code 0 = ok (partial missing allowed)
        exit_code 1 = ALL inputs missing
    """
    if evidence_files is None:
        evidence_files = EVIDENCE_FILES
    if guardian_report_paths is None:
        guardian_report_paths = GUARDIAN_REPORT_PATHS

    # Load evidence
    evidence: dict[str, dict | None] = {}
    for phase, path in sorted(evidence_files.items()):
        evidence[phase] = _load_json(path)

    # Load guardian report
    guardian = None
    for p in guardian_report_paths:
        guardian = _load_json(p)
        if guardian is not None:
            break

    # Check if ALL missing
    all_evidence_missing = all(v is None for v in evidence.values())
    if all_evidence_missing and guardian is None:
        return "", 1

    lines: list[str] = []
    lines.append("# V15 Review Summary")
    lines.append("")

    # --- Section 1: Inputs ---
    lines.append("## 1. Inputs")
    lines.append("")
    found_phases = []
    missing_phases = []
    for phase in sorted(evidence.keys()):
        if evidence[phase] is not None:
            found_phases.append(phase)
        else:
            missing_phases.append(phase)

    if found_phases:
        lines.append(f"- **Found**: {', '.join(found_phases)}")
    if missing_phases:
        lines.append(f"- **Missing**: {', '.join(missing_phases)}")

    guardian_status = "found" if guardian is not None else "missing"
    lines.append(f"- **Guardian report**: {guardian_status}")
    lines.append("")

    # --- Section 2: Gate Results ---
    lines.append("## 2. Gate Results (P3\u2013P6)")
    lines.append("")
    lines.append("| Phase | Gate | Passed | Violations | Total | Status |")
    lines.append("|-------|------|--------|------------|-------|--------|")

    all_gates_pass = True
    for phase in sorted(evidence.keys()):
        data = evidence[phase]
        if data is None:
            lines.append(f"| {phase} | — | — | — | — | MISSING |")
            all_gates_pass = False
            continue
        gate = data.get("gate", "unknown")
        passed = data.get("passed", 0)
        violations = data.get("violations", 0)
        total = data.get("total_checks", 0)
        blocking = data.get("blocking", False)
        status = "FAIL" if violations > 0 or blocking else "PASS"
        if status == "FAIL":
            all_gates_pass = False
        lines.append(f"| {phase} | {gate} | {passed} | {violations} | {total} | {status} |")

    lines.append("")

    # --- Section 3: Violation Details ---
    has_violations = False
    for phase in sorted(evidence.keys()):
        data = evidence[phase]
        if data is None:
            continue
        viols = data.get("violation_details", [])
        if viols:
            has_violations = True

    if has_violations:
        lines.append("## 3. Violation Details")
        lines.append("")
        for phase in sorted(evidence.keys()):
            data = evidence[phase]
            if data is None:
                continue
            viols = data.get("violation_details", [])
            for v in viols:
                check = v.get("check", "unknown")
                detail = v.get("detail", "no detail")
                lines.append(f"- **{phase}** / `{check}`: {detail}")
        lines.append("")
    else:
        lines.append("## 3. Violation Details")
        lines.append("")
        lines.append("No violations recorded.")
        lines.append("")

    # --- Section 4: Guardian Report ---
    lines.append("## 4. Guardian Report")
    lines.append("")
    if guardian is None:
        lines.append("Guardian report not available.")
    else:
        status = guardian.get("status", "UNKNOWN")
        meta = guardian.get("metadata", {})
        total_tests = meta.get("total_tests", 0)
        passed_tests = meta.get("passed_tests", 0)
        failed_tests = meta.get("failed_tests", 0)
        skipped_tests = meta.get("skipped_tests", 0)

        lines.append(f"- **Status**: {status}")
        lines.append(f"- **Total tests**: {total_tests}")
        lines.append(f"- **Passed**: {passed_tests}")
        lines.append(f"- **Failed**: {failed_tests}")
        lines.append(f"- **Skipped**: {skipped_tests}")

        failed_by_cat = meta.get("failed_by_category", {})
        non_empty_cats = {k: v for k, v in sorted(failed_by_cat.items()) if v}
        if non_empty_cats:
            lines.append("")
            lines.append("### Failed by Category")
            lines.append("")
            for cat, items in non_empty_cats.items():
                lines.append(f"- **{cat}**: {len(items)} failure(s)")
    lines.append("")

    # --- Section 5: Approval Decision ---
    lines.append("## 5. Approval Decision")
    lines.append("")

    guardian_pass = guardian is not None and guardian.get("status") == "PASS"
    ready = all_gates_pass and guardian_pass

    if ready:
        lines.append("**Ready for human approval: YES**")
    else:
        reasons = []
        if not all_gates_pass:
            reasons.append("gate failures or missing evidence")
        if not guardian_pass:
            reasons.append("guardian report not PASS")
        lines.append("**Ready for human approval: NO**")
        lines.append("")
        lines.append(f"Reason(s): {'; '.join(reasons)}")
    lines.append("")

    return "\n".join(lines), 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_envelope(
    exit_code: int,
    evidence_files: dict[str, Path],
    guardian_report_paths: list[Path],
    out_path: str | None,
    all_gates_pass: bool,
    guardian_pass: bool,
) -> ResultEnvelope:
    """Build a ResultEnvelope for the review summary run."""
    env = ResultEnvelope(tool="review_summary", exit_code=exit_code)

    # Inputs
    for phase, path in sorted(evidence_files.items()):
        env.inputs[f"evidence_{phase.lower()}"] = {
            "path": path.name,
            "present": path.is_file(),
        }
    guardian_present = any(p.is_file() for p in guardian_report_paths)
    env.inputs["guardian_report"] = {
        "path": guardian_report_paths[0].name if guardian_report_paths else "guardian_report.json",
        "present": guardian_present,
    }

    # Outputs
    if out_path:
        env.outputs["markdown"] = {"path": Path(out_path).name}

    # Findings
    if exit_code == 1:
        env.findings.append(
            Finding(
                code="ALL_INPUTS_MISSING",
                severity="ERROR",
                message="All input files missing, nothing to summarize",
            ),
        )
        return env

    for phase, path in sorted(evidence_files.items()):
        if not path.is_file():
            env.findings.append(
                Finding(
                    code="INPUT_MISSING",
                    severity="WARN",
                    message=f"Evidence file missing: {phase}",
                    context={"phase": phase},
                ),
            )
    if not guardian_present:
        env.findings.append(
            Finding(
                code="INPUT_MISSING",
                severity="WARN",
                message="Guardian report not found",
            ),
        )
    if not all_gates_pass:
        env.findings.append(
            Finding(
                code="APPROVAL_NO",
                severity="WARN",
                message="Gate failures or missing evidence",
            ),
        )
    if not guardian_pass:
        env.findings.append(
            Finding(
                code="APPROVAL_NO",
                severity="WARN",
                message="Guardian report not PASS",
            ),
        )

    return env


def generate_summary_with_envelope(
    evidence_files: dict[str, Path] | None = None,
    guardian_report_paths: list[Path] | None = None,
    out_path: str | None = None,
) -> tuple[str, int, ResultEnvelope]:
    """Generate summary and build envelope in one call."""
    if evidence_files is None:
        evidence_files = EVIDENCE_FILES
    if guardian_report_paths is None:
        guardian_report_paths = GUARDIAN_REPORT_PATHS

    md, exit_code = generate_summary(evidence_files, guardian_report_paths)

    # Compute gate/guardian status for envelope
    evidence: dict[str, dict | None] = {}
    for phase, path in sorted(evidence_files.items()):
        evidence[phase] = _load_json(path)
    guardian = None
    for p in guardian_report_paths:
        guardian = _load_json(p)
        if guardian is not None:
            break

    all_gates_pass = True
    for phase in sorted(evidence.keys()):
        data = evidence[phase]
        if data is None:
            all_gates_pass = False
        elif data.get("violations", 0) > 0 or data.get("blocking", False):
            all_gates_pass = False

    guardian_pass = guardian is not None and guardian.get("status") == "PASS"

    env = _build_envelope(
        exit_code,
        evidence_files,
        guardian_report_paths,
        out_path,
        all_gates_pass,
        guardian_pass,
    )
    return md, exit_code, env


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate V15 review summary markdown.")
    parser.add_argument(
        "--out",
        type=str,
        required=True,
        help="Output markdown file path",
    )
    parser.add_argument(
        "--json-out",
        type=str,
        default=None,
        help="Optional: write JSON result envelope to this path",
    )
    args = parser.parse_args()

    md, exit_code, env = generate_summary_with_envelope(out_path=args.out)

    if args.json_out:
        env.write_json(Path(args.json_out))

    if exit_code != 0:
        print("ERROR: All input files missing. Nothing to summarize.", file=sys.stderr)
        return exit_code

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Review summary written to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
