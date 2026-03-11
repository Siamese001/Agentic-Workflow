#!/usr/bin/env python3
"""Quick syntax check to identify the 3 remaining errors."""

import sys
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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
