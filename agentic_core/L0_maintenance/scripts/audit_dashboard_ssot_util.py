"""
Dashboard SSOT Audit Script
Identifies split-brain violations where metric definitions differ between scripts.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Core dashboard scripts to audit
CORE_SCRIPTS = [
    "scripts/full_agent_discovery.py",
    "scripts/regenerate_dashboard_full.py",
    "scripts/test_dashboard_end_to_end.py",
]

# Metrics to audit for SSOT violations
METRICS = [
    "has_tests",
    "has_healing",
    "mcp_hardened",
    "invocation",
    "typed_pct",
    "documented_pct",
    "proper_base_class",
    "schema_strictness",
]


def find_metric_definitions(script_path: Path, metric: str) -> list:
    """Find all lines where a metric is calculated or checked."""
    content = script_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    definitions = []
    for i, line in enumerate(lines, 1):
        # Look for assignment or calculation patterns
        if metric in line.lower() and ("=" in line or "sum(" in line or "for " in line):
            definitions.append({"line": i, "code": line.strip()[:120]})
    return definitions


def audit_script(script_path: Path) -> dict:
    """Audit a single script for metric definitions."""
    results = {}
    for metric in METRICS:
        defs = find_metric_definitions(script_path, metric)
        if defs:
            results[metric] = defs
    return results


def main():
    print("=" * 80)
    print("DASHBOARD SSOT AUDIT - Finding Split-Brain Violations")
    print("=" * 80)

    all_results = {}

    for script in CORE_SCRIPTS:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            print(f"\n📄 {script}")
            print("-" * 60)
            results = audit_script(script_path)
            all_results[script] = results

            for metric, defs in results.items():
                print(f"\n  {metric}: {len(defs)} definitions")
                for d in defs[:3]:  # Show first 3
                    print(f"    L{d['line']}: {d['code'][:80]}...")

    # Cross-script analysis
    print("\n" + "=" * 80)
    print("CROSS-SCRIPT ANALYSIS - Potential SSOT Violations")
    print("=" * 80)

    for metric in METRICS:
        scripts_with_metric = []
        for script, results in all_results.items():
            if metric in results:
                scripts_with_metric.append(script)

        if len(scripts_with_metric) > 1:
            print(f"\n⚠️  {metric} defined in {len(scripts_with_metric)} scripts:")
            for s in scripts_with_metric:
                print(f"    - {s}")
            print("   → POTENTIAL SPLIT-BRAIN VIOLATION")


if __name__ == "__main__":
    main()
