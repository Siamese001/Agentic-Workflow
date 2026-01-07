#!/usr/bin/env python3
"""Check violations in fix_all_imports.py and fix_all_agentic_imports.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.L5_safety.validators.GravityValidatorAgent import GravityValidatorAgent

async def main():
    project_root = Path(__file__).parent
    validator = GravityValidatorAgent(project_root)
    
    files_to_check = [
        project_root / "agentic_core" / "L0_maintenance" / "scripts" / "fix_all_imports.py",
        project_root / "agentic_core" / "L0_maintenance" / "scripts" / "fix_all_agentic_imports.py",
    ]
    
    for file_path in files_to_check:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue
        
        violations = await validator.detect_violations(file_path)
        
        print(f"\n📊 Violations in {file_path.name}: {len(violations)}")
        for v in violations:
            print(f"  Line {v.line_number}: {v.violation_type} (severity {v.severity}/10)")
            print(f"    Import: {v.import_line}")
            print(f"    Action: {v.suggested_action}")
            print()

if __name__ == "__main__":
    asyncio.run(main())
