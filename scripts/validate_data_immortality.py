#!/usr/bin/env python3
"""
Validate Data Immortality - Pre-commit Hook
Ensures no data files are modified after initial commit.
"""

import sys
import os

def main():
    """Check if any files being committed are in data/ directories."""
    files = sys.argv[1:] if len(sys.argv) > 1 else []
    
    data_patterns = ['data/', '06_data/']
    
    for file_path in files:
        # Check if file is in data directories
        for pattern in data_patterns:
            if file_path.startswith(pattern):

                sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
