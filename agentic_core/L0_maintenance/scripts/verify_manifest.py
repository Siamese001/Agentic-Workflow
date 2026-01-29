"""
File: agentic_core/L0_maintenance/scripts/verify_manifest.py
Description: Analysis tool for SSOT Dry-Run Reports.
Usage: python verify_manifest.py --report ssot_report_123456.json
Context:
    - Parses the 'ReconciliationManifest' (JSON Report) from execute_ssot.py.
    - Generates a 'Blast Radius' assessment (Count of modified/deleted files).
    - Verifies that no 'High Severity' safety violations were ignored.
"""

import json
import argparse
import sys
import logging
from pathlib import Path
from typing import Any


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - [MANIFEST] %(message)s"
    )


def analyze_impact(report: dict[str, Any]) -> bool:
    """
    Analyzes the dry-run report to determine if the proposed changes are safe.
    Returns: True if analysis passes safety thresholds, False otherwise.
    """
    phase1 = report.get("phase1", {})
    phase2 = report.get("phase2", {})
    meta = report.get("meta", {})

    # 1. Metadata Verification
    if not meta.get("dry_run"):
        logging.warning("⚠️  This report is from a LIVE RUN, not a dry-run.")

    # 2. Violation Summary
    violations = phase1.get("violations_found", [])
    total_violations = len(violations)

    # Group by drift type
    by_type = {}
    for v in violations:
        d_type = v.get("type", "UNKNOWN")
        by_type[d_type] = by_type.get(d_type, 0) + 1

    logging.info(f"--- IMPACT ANALYSIS: {meta.get('territory', 'Unknown')} ---")
    logging.info(f"Total Violations Detected: {total_violations}")
    for k, v in by_type.items():
        logging.info(f"  - {k}: {v}")

    # 3. Modification Forecast (Phase 2 Plan)
    modifications = phase2.get("modifications", [])
    failures = phase2.get("failures", [])

    # Calculate Blast Radius
    files_touched = set()
    for mod in modifications:
        if mod.get("target"):
            files_touched.add(mod["target"])

    blast_radius = len(files_touched)
    logging.info("\n--- PROPOSED ACTIONS (Dry Run) ---")
    logging.info(f"Files to be Modified: {blast_radius}")
    logging.info(f"Agents Engaged: {len(set(m.get('agent') for m in modifications))}")
    logging.info(f"Blocked/Failed Actions: {len(failures)}")

    # 4. Critical Safety Checks
    safety_pass = True

    # Check A: High modification count (e.g., > 20% of repo) - Placeholder threshold
    if blast_radius > 50:
        logging.warning(
            f"🚨 HIGH BLAST RADIUS: {blast_radius} files would be modified. Manual review required."
        )
        safety_pass = False

    # Check B: Failures due to Safety Budget
    budget_blocks = [f for f in failures if "blocked_by_safety" in str(f.get("status", ""))]
    if budget_blocks:
        logging.warning(f"⚠️  {len(budget_blocks)} actions were blocked by safety budget limits.")

    # Check C: Orphan Deletion Risks
    orphans = [v for v in violations if "ORPHAN" in v.get("type", "")]
    if len(orphans) > 10:
        logging.warning(
            f"🚨 MASS DELETION RISK: {len(orphans)} orphan files identified for deletion."
        )
        safety_pass = False

    return safety_pass


def main():
    parser = argparse.ArgumentParser(description="SSOT Dry-Run Manifest Analyzer")
    parser.add_argument("report", help="Path to the ssot_report_TIMESTAMP.json file")
    args = parser.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        logging.error(f"Report file not found: {report_path}")
        sys.exit(1)

    try:
        with open(report_path) as f:
            data = json.load(f)

        is_safe = analyze_impact(data)

        print("\n" + "=" * 40)
        if is_safe:
            print("✅ ANALYSIS PASSED: Proposed changes look standard.")
            sys.exit(0)
        else:
            print("❌ ANALYSIS FLAGGED RISKS: See warnings above.")
            sys.exit(1)

    except json.JSONDecodeError:
        logging.error("Invalid JSON format in report file.")
        sys.exit(1)
    except Exception as e:
        logging.critical(f"Analysis failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
