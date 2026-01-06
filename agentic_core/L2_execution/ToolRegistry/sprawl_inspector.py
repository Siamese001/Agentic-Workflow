from __future__ import annotations
"""
Sprawl Inspector - Pre-Flight Architectural Survey
Identifies low-density folders and excessive breadth for consolidation.
Implements Key 49 (Universal Depth Law) and Key 41 (Modular Atomicity).
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

class SprawlInspectorAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Brief description of functionality and purpose."""

    def __init__(self, target_path='agentic_core') -> None:
        self.root = Path(target_path)
        self.MAX_BREADTH = 7
        self.MIN_FILES = 3
        self.report = {'metadata': {'target': target_path, 'timestamp': datetime.now().isoformat(), 'user': os.getenv('USERNAME', 'unknown')}, 'violations': [], 'flattening_candidates': []}

    def inspect(self) -> Any:
        """Scan directory tree for sprawl violations."""
        for root, dirs, files in os.walk(self.root):
            p: Any = Path(root)
            py_files: Any = [f for f in files if f.endswith('.py')]
            if len(dirs) > self.MAX_BREADTH:
                self.report['violations'].append({'path': str(p), 'type': 'Breadth Violation', 'count': len(dirs), 'msg': f"Found {len(dirs)} subfolders. Violates 'Magic 7' rule."})
            if 0 < len(py_files) < self.MIN_FILES and (not dirs) and (p != self.root):
                self.report['flattening_candidates'].append({'folder': str(p), 'files': py_files, 'file_count': len(py_files), 'reason': 'Low Signal Density (Fragmented)'})
        return self.report

    def print_summary(self) -> Any:
        """Print human-readable summary."""
        print('\nfrom agentic_core.L2_execution.ToolRegistry.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nimport logging\n\nLogger = logging.getLogger(__name__)\n' + '=' * 70)
        print('🔍 PROJECT SPRAWL REPORT')
        print('=' * 70)
        print(f"Target: {self.report['metadata']['target']}")
        print(f"Timestamp: {self.report['metadata']['timestamp']}")
        print()
        print(f"📊 Breadth Violations: {len(self.report['violations'])}")
        print(f"📁 Flattening Candidates: {len(self.report['flattening_candidates'])}")
        if self.report['violations']:
            print('\n[BREADTH VIOLATIONS]')
            for v in self.report['violations']:
                print(f"  • {v['path']}: {v['count']} subfolders (max: {self.MAX_BREADTH})")
        if self.report['flattening_candidates']:
            print('\n[FLATTENING CANDIDATES]')
            for c in self.report['flattening_candidates'][:10]:
                print(f"  • {c['folder']}: {c['file_count']} files - {c['reason']}")
            if len(self.report['flattening_candidates']) > 10:
                print(f"  ... and {len(self.report['flattening_candidates']) - 10} more")
        print('=' * 70)

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()
if __name__ == '__main__':
    inspector: Any = SprawlInspectorAgent('agentic_core')
    data: Any = inspector.inspect()
    inspector.print_summary()
    with open('sprawl_report.json', 'w') as f:
        json.dump(data, f, indent=4)
    print('\n[OK] Detailed sprawl map saved to sprawl_report.json')
    print('    Use this report to guide architectural consolidation.')