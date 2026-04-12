#!/usr/bin/env python3
"""
Batch fix remaining broken test files.
"""

if __name__ == "__main__":
    import sys

    wave = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    batch_fix_remaining(wave)
