"""
Sovereign SSOT Auditor - Architecture Guardian (L6 Observability)
Verifies that no legacy dashboard artifacts or duplicate templates exist.
"""
import sys
from pathlib import Path

def audit_dashboard_sovereignty():
    """Audit the repository for architectural violations and ghost code."""
    project_root = Path(__file__).parent.parent.parent.parent.parent
    violations = []

    # 1. Check for Shadow Templates
    legacy_template = project_root / "agentic_core/config/validators/dashboard_template.html"
    if legacy_template.exists():
        violations.append(f"🔴 SSOT VIOLATION: Legacy template still exists at {legacy_template}")

    # 2. Check for Duplicate Servers
    metrics_server = project_root / "agentic_core/observability/metrics/dashboard_server.py"
    if metrics_server.exists():
        violations.append(f"🔴 ARCHITECTURE VIOLATION: Duplicate server implementation at {metrics_server}")

    # 3. Check for 0-byte Placeholder Files
    empty_template = project_root / "agentic_core/observability/dashboard/dashboard_template.html"
    if empty_template.exists() and empty_template.stat().st_size == 0:
        violations.append(f"🟡 HYGIENE VIOLATION: 0-byte placeholder found at {empty_template}")

    # 4. Verify Unified Script Presence
    canonical_gen = project_root / "agentic_core/observability/dashboard/scripts/generate.py"
    if not canonical_gen.exists():
        violations.append("🔴 CRITICAL: Canonical L6 generator script missing.")

    if violations:
        print(f"🛡️ Sovereign Audit FAILED for {project_root}")
        for v in violations:
            print(f"  {v}")
        print("\nAction: Execute the 'Great Purge' commands to restore SSOT.")
        sys.exit(1)
    else:
        print(f"✅ Sovereign Audit PASSED: Dashboard architecture is 100% consolidated.")
        sys.exit(0)

if __name__ == "__main__":
    audit_dashboard_sovereignty()
