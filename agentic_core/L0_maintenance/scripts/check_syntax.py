#!/usr/bin/env python3
"""Quick syntax check to identify the 3 remaining errors."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic_core.L5_safety.unified.UnifiedCodeValidatorAgent import UnifiedCodeValidatorAgent

def main():
    project_root = Path(__file__).parent.parent
    agent = UnifiedCodeValidatorAgent(project_root=project_root)
    result = agent.validate_repository()

    print(f"Total errors: {result['total_violations']}")
    print()

    for v in result.get('violations', []):
        print(f"{v.file_path}:{v.line_number}:{v.column} - {v.error_message}")

if __name__ == '__main__':
    main()
