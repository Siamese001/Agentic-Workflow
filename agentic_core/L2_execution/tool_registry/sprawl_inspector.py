#!/usr/bin/env python3
"""
Sprawl Inspector - Pre-Flight Architectural Survey
Identifies low-density folders and excessive breadth for consolidation.
Implements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).
"""

import json
import os
from datetime import datetime
from pathlib import Path

class SprawlInspector:
    def __init__(self, target_path="agentic_core"):
        self.root = Path(target_path)
        self.MAX_BREADTH = 7  # Maximum sibling folders (Cognitive Load limit)
        self.MIN_FILES = 3    # Minimum files to justify a separate folder
        self.report = {
            "metadata": {
                "target": target_path,
                "timestamp": datetime.now().isoformat(),
                "user": os.getenv("USERNAME", "unknown")
            },
            "violations": [],
            "flattening_candidates": []
        }

    def inspect(self):
        """Scan directory tree for sprawl violations."""
        for root, dirs, files in os.walk(self.root):
            p = Path(root)
            py_files = [f for f in files if f.endswith('.py')]
            
            # Metric 1: Breadth (Sprawl)
            if len(dirs) > self.MAX_BREADTH:
                self.report["violations"].append({
                    "path": str(p),
                    "type": "Breadth Violation",
                    "count": len(dirs),
                    "msg": f"Found {len(dirs)} subfolders. Violates 'Magic 7' rule."
                })

            # Metric 2: Density (Signal)
            # Flag folders that have 1-2 files but no subfolders (Fragmented)
            if 0 < len(py_files) < self.MIN_FILES and not dirs and p != self.root:
                self.report["flattening_candidates"].append({
                    "folder": str(p),
                    "files": py_files,
                    "file_count": len(py_files),
                    "reason": "Low Signal Density (Fragmented)"
                })

        return self.report

    def print_summary(self):
        """Print human-readable summary."""
        print("\n" + "="*70)
        print("🔍 PROJECT SPRAWL REPORT")
        print("="*70)
        print(f"Target: {self.report['metadata']['target']}")
        print(f"Timestamp: {self.report['metadata']['timestamp']}")
        print()
        print(f"📊 Breadth Violations: {len(self.report['violations'])}")
        print(f"📁 Flattening Candidates: {len(self.report['flattening_candidates'])}")
        
        if self.report['violations']:
            print("\n[BREADTH VIOLATIONS]")
            for v in self.report['violations']:
                print(f"  • {v['path']}: {v['count']} subfolders (max: {self.MAX_BREADTH})")
        
        if self.report['flattening_candidates']:
            print("\n[FLATTENING CANDIDATES]")
            for c in self.report['flattening_candidates'][:10]:  # Show first 10
                print(f"  • {c['folder']}: {c['file_count']} files - {c['reason']}")
            if len(self.report['flattening_candidates']) > 10:
                print(f"  ... and {len(self.report['flattening_candidates']) - 10} more")
        
        print("="*70)

if __name__ == "__main__":
    inspector = SprawlInspector("agentic_core")
    data = inspector.inspect()
    
    # Print summary to console
    inspector.print_summary()
    
    # Save detailed report to JSON
    with open("sprawl_report.json", "w") as f:
        json.dump(data, f, indent=4)
    print("\n[OK] Detailed sprawl map saved to sprawl_report.json")
    print("    Use this report to guide architectural consolidation.")
