#!/usr/bin/env python3
"""Quick script to check violations in CanonBaseAgent.py"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agentic_core.L5_safety.validators.GravityValidatorAgent import GravityValidatorAgent

async def main():
    project_root = Path(__file__).parent
    validator = GravityValidatorAgent(project_root)
    
    file_path = project_root / "agentic_core" / "L1_cognition" / "thought_engine" / "CanonBaseAgent.py"
    
    violations = await validator.detect_violations(file_path)
    
    print(f"\n📊 Violations in CanonBaseAgent.py: {len(violations)}")
    for v in violations:
        print(f"  Line {v.line_number}: {v.violation_type} (severity {v.severity}/10)")
        print(f"    Import: {v.import_line}")
        print(f"    Action: {v.suggested_action}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
