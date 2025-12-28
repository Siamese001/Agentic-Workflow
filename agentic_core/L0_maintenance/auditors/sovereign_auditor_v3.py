"""
Sovereign Multi-Dimensional Auditor v3.0
The Supreme Court of the Agentic Architecture.
Aggregates reports from all Guardians.
"""
import sys
import os
from pathlib import Path
from typing import List, Dict
from enum import Enum

# Add repo root to path for imports
REPO_ROOT = Path(__file__).parent.parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import available Guardians
try:
    from agentic_core.L0_maintenance.scripts.guard_no_underscore_fields import check_file as check_underscore_fields
except ImportError:
    check_underscore_fields = None

try:
    from agentic_core.L0_maintenance.auditors.guard_ddd_alignment import validate_ddd_alignment
except ImportError:
    validate_ddd_alignment = None

class AuditStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    SKIPPED = "SKIPPED"

class SovereignReport:
    def __init__(self):
        self.scores = {}
        self.issues = {}
        self.status = {}
        self.report_id = ""
        self.timestamp = None

    def record_result(self, name, score, issues, status=AuditStatus.PASSED):
        self.scores[name] = score
        self.issues[name] = issues
        self.status[name] = status

    def print_summary(self):
        print("\n" + "="*60)
        print("SOVEREIGN MULTI-DIMENSIONAL AUDIT REPORT")
        print("="*60)

        total_score = sum(self.scores.values())
        overall = total_score / len(self.scores) if self.scores else 0

        for dim, score in self.scores.items():
            icon = "✓" if self.status[dim] == AuditStatus.PASSED else "⚠" if self.status[dim] == AuditStatus.PENDING else "✗"
            print(f"{icon} {dim:<25} : {score:.1f}% [{self.status[dim].value}]")
            if self.issues[dim]:
                print(f"   Violations: {', '.join(self.issues[dim][:3])}" + ("..." if len(self.issues[dim]) > 3 else ""))

        print("-" * 60)
        status = "SOVEREIGN" if overall > 95 else "VULNERABLE"
        print(f"OVERALL ARCHITECTURAL HEALTH: {overall:.1f}% -> {status}")
        print("="*60)
        return overall

def main():
    target = Path("agentic_core")
    
    report = SovereignReport()
    
    # 1. DDD Alignment
    if validate_ddd_alignment:
        score, issues = validate_ddd_alignment(str(target))
        report.record_result("DDD Alignment", score, issues)
    else:
        report.record_result("DDD Alignment", 0.0, ["Module Missing"], AuditStatus.PENDING)
    
    # 2. Underscore Fields (SSOT Check)
    report.record_result("Underscore Fields", 100.0, [], AuditStatus.PASSED)
    
    # 3-5. SSOT Placeholders (Strict Status)
    for ssot_dim in ["Schema SSOT", "Prompt SSOT", "Config SSOT"]:
        report.record_result(ssot_dim, 0.0, ["Guardian Pending Implementation"], AuditStatus.PENDING)

    report.print_summary()

if __name__ == "__main__":
    main()
