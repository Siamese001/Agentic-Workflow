"""C0 Policy Weekly Report — Automation (W5)

W5 c0-policy-rectification-phase2-deferred-a3f7e2:
    Automated weekly report generation for C0 policy metrics.
    Generates markdown reports with trends, anomalies, and recommendations.

Usage:
    python -m ops_scripts.monitoring.c0_policy_weekly_report \
        --output-dir docs/reports/c0_policy/ \
        --week 2026-W19

Outputs:
- docs/reports/c0_policy/<YYYY-Www>.md (markdown report)
- artifacts/c0_policy/weekly/<YYYY-Www>.json (machine-readable)

DS-7: Weekly reporting automation for C0 policy.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .c0_policy_dashboard import collect_metrics, format_prometheus


def generate_weekly_report(
    week_str: str,
    metrics: dict[str, Any],
    prev_week_metrics: dict[str, Any] | None = None,
) -> str:
    """Generate markdown weekly report."""

    year, week = week_str.split("-W")
    week_num = int(week)

    # Calculate deltas if previous week available
    deltas = {}
    if prev_week_metrics:
        for key in ["c0_policy_none_rate", "bypass_typed_ratio", "pa_boundary_rejection_rate"]:
            curr = metrics.get(key, 0)
            prev = prev_week_metrics.get(key, 0)
            deltas[key] = curr - prev

    report = f"""# C0 Policy Weekly Report — {week_str}

> **Generated**: {datetime.utcnow().isoformat()} UTC  
> **Collection Window**: {metrics.get('collection_window_hours', 168)} hours (full week)

## Executive Summary

| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| Contracts with C0 Policy | {metrics.get('contracts_with_c0_policy', 0):,} / {metrics.get('total_contracts', 0):,} | >95% | {'✅' if metrics.get('c0_policy_none_rate', 1.0) < 0.05 else '⚠️'} |
| Typed Bypass Ratio | {metrics.get('bypass_typed_ratio', 0):.1%} | >90% | {'✅' if metrics.get('bypass_typed_ratio', 0) > 0.9 else '⚠️'} |
| PA Boundary Rejection Rate | {metrics.get('pa_boundary_rejection_rate', 0):.2%} | <5% | {'✅' if metrics.get('pa_boundary_rejection_rate', 0) < 0.05 else '⚠️'} |
| L0/L1 Disagreement Rate | {metrics.get('l0_l1_disagreement_rate', 0):.2%} | <1% | {'✅' if metrics.get('l0_l1_disagreement_rate', 0) < 0.01 else '⚠️'} |

## DS-5: Migration Progress

**Goal**: <1% of contracts without c0_policy

- **Total Contracts**: {metrics.get('total_contracts', 0):,}
- **With C0 Policy**: {metrics.get('contracts_with_c0_policy', 0):,} ({1 - metrics.get('c0_policy_none_rate', 0):.1%})
- **Without C0 Policy**: {metrics.get('contracts_without_c0_policy', 0):,} ({metrics.get('c0_policy_none_rate', 0):.1%})

{'✅ **MIGRATION COMPLETE**' if metrics.get('c0_policy_none_rate', 1.0) < 0.01 else f'⚠️ Migration in progress: {(metrics.get("c0_policy_none_rate", 0) * 100):.1f}% remaining'}

## DS-3: Bypass Reason Distribution

**Goal**: >90% typed bypass reasons (legacy <10%)

| Type | Count | Ratio |
|------|-------|-------|
| Typed (preferred) | {metrics.get('bypass_typed_count', 0):,} | {metrics.get('bypass_typed_ratio', 0):.1%} |
| Legacy (deprecated) | {metrics.get('bypass_legacy_count', 0):,} | {metrics.get('bypass_legacy_ratio', 0):.1%} |

**Typed Reasons**: BYPASS_PRELOADED_CONTEXT, BYPASS_CACHE_RETURN, BYPASS_FALLBACK, NOT_REQUIRED  
**Legacy Reasons**: GROUNDING_NOT_REQUIRED, TERMINAL_SHORTCIRCUIT_NO_RETRIEVAL, etc.

## DS-4: PA Boundary Health

**Goal**: Rejection rate <5% (excluding intentional blocks)

- **Total Boundary Checks**: {metrics.get('pa_boundary_total', 0):,}
- **Passed**: {metrics.get('pa_boundary_passed', 0):,}
- **Failed**: {metrics.get('pa_boundary_failed', 0):,}
- **Rejection Rate**: {metrics.get('pa_boundary_rejection_rate', 0):.2%}

## DS-1: C0 Preflight Eligibility

**Goal**: >95% eligibility rate for R3 routes

- **Total Preflight Checks**: {metrics.get('preflight_total', 0):,}
- **Eligible**: {metrics.get('preflight_eligible', 0):,}
- **Ineligible**: {metrics.get('preflight_ineligible', 0):,}
- **Eligibility Rate**: {metrics.get('preflight_eligibility_rate', 0):.1%}

## DS-2: L0/L1 Agreement

**Goal**: <1% disagreement rate (L0 authority respected)

- **Total Checks**: {metrics.get('l0_l1_total_checks', 0):,}
- **Disagreements**: {metrics.get('l0_l1_disagreements', 0)}
- **Disagreement Rate**: {metrics.get('l0_l1_disagreement_rate', 0):.2%}

{'✅ L0 authority consistently respected' if metrics.get('l0_l1_disagreement_rate', 0) < 0.01 else '⚠️ Investigate L0/L1 disagreement cases'}

## Trends vs Previous Week

"""

    if prev_week_metrics and deltas:
        report += f"""| Metric | This Week | Last Week | Delta |
|--------|-----------|-----------|-------|
| C0 Policy None Rate | {metrics.get('c0_policy_none_rate', 0):.2%} | {prev_week_metrics.get('c0_policy_none_rate', 0):.2%} | {deltas.get('c0_policy_none_rate', 0):+.2%} |
| Typed Bypass Ratio | {metrics.get('bypass_typed_ratio', 0):.1%} | {prev_week_metrics.get('bypass_typed_ratio', 0):.1%} | {deltas.get('bypass_typed_ratio', 0):+.1%} |
| PA Rejection Rate | {metrics.get('pa_boundary_rejection_rate', 0):.2%} | {prev_week_metrics.get('pa_boundary_rejection_rate', 0):.2%} | {deltas.get('pa_boundary_rejection_rate', 0):+.2%} |

"""
    else:
        report += "_No previous week data available for comparison._\n\n"

    report += """## Action Items

"""

    # Auto-generate action items based on thresholds
    actions = []

    if metrics.get('c0_policy_none_rate', 0) > 0.05:
        actions.append(f"- [ ] **HIGH PRIORITY**: {metrics.get('c0_policy_none_rate', 0):.1%} contracts lack C0 policy. Run eager migration: `python -m tools.c0_migration.background_contract_updater --source-db contracts.db`")

    if metrics.get('bypass_legacy_ratio', 0) > 0.10:
        actions.append(f"- [ ] **MEDIUM**: {metrics.get('bypass_legacy_ratio', 0):.1%} legacy bypass reasons detected. Audit entrypoints: `python ops_scripts/ci/check_c0_bypass_reasons.py`")

    if metrics.get('pa_boundary_rejection_rate', 0) > 0.05:
        actions.append(f"- [ ] **MEDIUM**: PA boundary rejection rate {metrics.get('pa_boundary_rejection_rate', 0):.1%} exceeds 5%. Investigate evidence contract quality.")

    if metrics.get('l0_l1_disagreement_rate', 0) > 0.01:
        actions.append(f"- [ ] **HIGH PRIORITY**: L0/L1 disagreement rate {metrics.get('l0_l1_disagreement_rate', 0):.2%} exceeds 1%. L0 authority not being respected.")

    if not actions:
        report += "✅ **No action items** — all metrics within target ranges.\n"
    else:
        report += "\n".join(actions) + "\n"

    report += f"""
## References

- Parent Plan: [c0-policy-rectification-deferred-f7b2a9](https://www.notion.so/c0-policy-rectification-deferred-f7b2a9)
- Phase 2 Plan: [c0-policy-rectification-phase2-deferred-a3f7e2](https://www.notion.so/c0-policy-rectification-phase2-deferred-a3f7e2)
- Migration Guide: [docs/operations/C0_POLICY_MIGRATION.md](../../../docs/operations/C0_POLICY_MIGRATION.md)
- Incident Runbook: [docs/runbooks/C0_POLICY_INCIDENT_RESPONSE.md](../../../docs/runbooks/C0_POLICY_INCIDENT_RESPONSE.md)

---
*Report generated by C0 Policy Weekly Report Automation*  
*Plan: c0-policy-rectification-phase2-deferred-a3f7e2 (W5)*
"""

    return report


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for weekly report generation."""
    parser = argparse.ArgumentParser(description="C0 Policy Weekly Report")
    parser.add_argument(
        "--week",
        help="ISO week string (YYYY-Www), defaults to current week",
    )
    parser.add_argument(
        "--output-dir",
        default="docs/reports/c0_policy",
        help="Directory for markdown reports",
    )
    parser.add_argument(
        "--artifacts-dir",
        default="artifacts/c0_policy/weekly",
        help="Directory for JSON artifacts",
    )
    parser.add_argument(
        "--contracts-db",
        default="contracts.db",
        help="Path to contracts database",
    )
    parser.add_argument(
        "--bypass-log",
        default="artifacts/c0_bypass_log.jsonl",
        help="Path to bypass log",
    )

    args = parser.parse_args(argv)

    # Determine week
    if args.week:
        week_str = args.week
    else:
        today = datetime.utcnow()
        year, week, _ = today.isocalendar()
        week_str = f"{year}-W{week:02d}"

    print(f"Generating C0 Policy Weekly Report for {week_str}...")

    # Collect metrics
    metrics = collect_metrics(
        contracts_db=args.contracts_db,
        bypass_log=args.bypass_log,
        window_hours=168,  # Full week
    )
    metrics_dict = {
        "collected_at": metrics.collected_at,
        "collection_window_hours": metrics.collection_window_hours,
        "total_contracts": metrics.total_contracts,
        "contracts_with_c0_policy": metrics.contracts_with_c0_policy,
        "contracts_without_c0_policy": metrics.contracts_without_c0_policy,
        "c0_policy_none_rate": metrics.c0_policy_none_rate,
        "bypass_typed_count": metrics.bypass_typed_count,
        "bypass_legacy_count": metrics.bypass_legacy_count,
        "bypass_typed_ratio": metrics.bypass_typed_ratio,
        "bypass_legacy_ratio": metrics.bypass_legacy_ratio,
        "pa_boundary_total": metrics.pa_boundary_total,
        "pa_boundary_passed": metrics.pa_boundary_passed,
        "pa_boundary_failed": metrics.pa_boundary_failed,
        "pa_boundary_rejection_rate": metrics.pa_boundary_rejection_rate,
        "preflight_total": metrics.preflight_total,
        "preflight_eligible": metrics.preflight_eligible,
        "preflight_ineligible": metrics.preflight_ineligible,
        "preflight_eligibility_rate": metrics.preflight_eligibility_rate,
        "l0_l1_total_checks": metrics.l0_l1_total_checks,
        "l0_l1_disagreements": metrics.l0_l1_disagreements,
        "l0_l1_disagreement_rate": metrics.l0_l1_disagreement_rate,
    }

    # Load previous week for comparison
    prev_week = datetime.utcnow() - timedelta(weeks=1)
    prev_year, prev_week_num, _ = prev_week.isocalendar()
    prev_week_str = f"{prev_year}-W{prev_week_num:02d}"

    prev_metrics = None
    prev_artifacts_path = Path(args.artifacts_dir) / f"{prev_week_str}.json"
    if prev_artifacts_path.exists():
        with open(prev_artifacts_path) as f:
            prev_metrics = json.load(f)

    # Generate markdown report
    report = generate_weekly_report(week_str, metrics_dict, prev_metrics)

    # Write markdown
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{week_str}.md"
    with open(md_path, "w") as f:
        f.write(report)
    print(f"Markdown report: {md_path}")

    # Write JSON artifact
    artifacts_dir = Path(args.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    json_path = artifacts_dir / f"{week_str}.json"
    with open(json_path, "w") as f:
        json.dump(metrics_dict, f, indent=2)
    print(f"JSON artifact: {json_path}")

    # Generate prometheus metrics
    prom_output = format_prometheus(metrics)
    prom_path = artifacts_dir / f"{week_str}.prom"
    with open(prom_path, "w") as f:
        f.write(prom_output)
    print(f"Prometheus metrics: {prom_path}")

    print("\nReport generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
