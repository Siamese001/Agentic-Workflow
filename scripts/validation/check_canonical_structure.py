

logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Check Canonical Project Structure - Pre-commit Hook
Ensures required canonical directories exist.
"""

import sys
import os
import logging

def main() -> None:
    """Check if all required canonical directories exist."""
    required_dirs = [
        '01_agentic_core',
        '02_domains',
        '03_runtime',
        '04_interfaces',
        '05_capabilities',
        '06_data',
        '07_eval',
        '08_scripts',
        '09_testing'
    ]

    missing_dirs = []

    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            missing_dirs.append(dir_name)

    if missing_dirs:

        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
