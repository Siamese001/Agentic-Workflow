#!/usr/bin/env python3
"""
Check Canonical Project Structure - Pre-commit Hook
Ensures required canonical directories exist.
"""

import sys
import os


def main():
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
        print(f"ERROR: Missing canonical directories: {', '.join(missing_dirs)}")
        print("Canonical project structure must be maintained")
        sys.exit(1)
    
    print("Canonical structure OK - all required directories present")
    sys.exit(0)


if __name__ == "__main__":
    main()
