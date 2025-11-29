#!/usr/bin/env python3
"""
Show only failing validation keys.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from windsurf_validator import WindsurfValidator

def main():
    validator = WindsurfValidator()
    results = validator.validate_all()
    
    print("FAILING VALIDATION KEYS")
    print("=" * 80)
    print(f"{'KEY':<60} {'CATEGORY':<20}")
    print("-" * 80)
    
    total_keys = 0
    failing_keys = 0
    
    for category, category_results in results.items():
        for key, value in category_results.items():
            total_keys += 1
            if not value:
                print(f"{key:<60} {category:<20}")
                failing_keys += 1
    
    print(f"\nTOTAL FAILING: {failing_keys}/{total_keys} ({(total_keys-failing_keys)/total_keys*100:.1f}% passing)")

if __name__ == "__main__":
    main()
