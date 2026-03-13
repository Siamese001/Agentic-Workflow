"""Quick syntax check to identify the 3 remaining errors."""

import sys
from pathlib import Path

# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentic_core.L0_routing.utils.subprocess_runner_util import invoke_code_validator


def main():
    project_root = Path(__file__).parent.parent
    result = invoke_code_validator(action="validate", project_root=project_root)
    if result.get("success"):
        print(f"Total errors: {result.get('total_violations', 0)}")
        print()
        for v in result.get("violations", []):
            print(f"{v['file_path']}:{v['line_number']}:{v['column']} - {v['error_message']}")
    else:
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    main()
