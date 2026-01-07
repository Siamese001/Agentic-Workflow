#!/usr/bin/env python3
"""
Unified SSOT Validator - Single Command for Complete Validation

Replaces 5 separate validation tools:
- audit_ssot.py
- audit_architectural_violations.py  
- HierarchyAgent validation
- LocationAgent validation
- FilesystemSSOTReconcilerAgent drift detection

Usage:
    python scripts/validate_ssot.py              # Run all validations
    python scripts/validate_ssot.py --markdown   # Output as Markdown file
    python scripts/validate_ssot.py --json       # Output as JSON
"""

from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
REPO = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(REPO))

from agentic_core.utils.core_extensions.unified_validator import UnifiedSSOTValidator


def main():
    """Run unified SSOT validation."""
    parser = argparse.ArgumentParser(
        description="Unified SSOT Validator - Complete system health check"
    )
    parser.add_argument(
        '--markdown',
        action='store_true',
        help='Save report as Markdown file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output report as JSON'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: auto-generated)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        default=True,
        help='Run all validation checks (default)'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("UNIFIED SSOT VALIDATOR")
    print("=" * 80)
    print("\nRunning comprehensive validation...")
    print("  • Gravity violations (physical location)")
    print("  • Import violations (upward dependencies)")
    print("  • Hierarchy violations (depth limits)")
    print("  • Drift violations (filesystem vs blueprint)")
    print()
    
    # Run validation
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    
    # Display summary
    print("=" * 80)
    print("VALIDATION COMPLETE")
    print("=" * 80)
    print(f"\nCompliance Score: {report.compliance_score:.1f}%")
    print(f"Total Violations: {report.total_violations}")
    print(f"Scan Duration: {report.scan_duration:.2f}s")
    print()
    
    # Breakdown
    print("Violation Breakdown:")
    print(f"  • Gravity:    {len(report.gravity_violations)}")
    print(f"  • Imports:    {len(report.import_violations)}")
    print(f"  • Hierarchy:  {len(report.hierarchy_violations)}")
    print(f"  • Drift:      {len(report.drift_violations)}")
    print()
    
    # Status
    if report.is_compliant:
        print("✅ Status: COMPLIANT")
        print("   All SSOT validation checks passed.")
    else:
        print("⚠️  Status: NON-COMPLIANT")
        print(f"   {report.total_violations} violations require attention.")
    
    print()
    
    # Output handling
    if args.markdown or args.output:
        # Generate Markdown report
        markdown_content = report.to_markdown()
        
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = REPO / f"SSOT_Health_Report_{timestamp}.md"
        
        output_path.write_text(markdown_content, encoding='utf-8')
        print(f"📄 Markdown report saved: {output_path}")
        print()
    
    if args.json:
        # Generate JSON report
        json_data = {
            'compliance_score': report.compliance_score,
            'total_violations': report.total_violations,
            'scan_duration': report.scan_duration,
            'total_agents': report.total_agents,
            'violations': {
                'gravity': [
                    {
                        'file': v.file_path,
                        'actual_layer': v.actual_layer,
                        'assigned_layer': v.assigned_layer,
                        'agent': v.agent_name
                    }
                    for v in report.gravity_violations
                ],
                'imports': [
                    {
                        'file': v.file_path,
                        'line': v.line_number,
                        'source_layer': v.source_layer,
                        'target_layer': v.target_layer,
                        'import': v.import_line
                    }
                    for v in report.import_violations
                ],
                'hierarchy': [
                    {
                        'folder': v.folder_path,
                        'actual_depth': v.actual_depth,
                        'max_depth': v.max_depth,
                        'root': v.root_folder
                    }
                    for v in report.hierarchy_violations
                ],
                'drift': [
                    {
                        'folder': v.folder_path,
                        'type': v.violation_type,
                        'parent': v.parent_folder
                    }
                    for v in report.drift_violations
                ]
            }
        }
        
        print(json.dumps(json_data, indent=2))
    
    # Exit code based on compliance
    sys.exit(0 if report.is_compliant else 1)


if __name__ == "__main__":
    main()
