#!/usr/bin/env python3
"""
Run validation and output complete results in table format.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from windsurf_validator import WindsurfValidator

def main():
    validator = WindsurfValidator()
    results = validator.validate_all()
    
    print("WINDSURF VALIDATION RESULTS - COMPLETE KEY TABLE")
    print("=" * 100)
    print(f"{'KEY':<60} {'STATUS':<8} {'CATEGORY':<20}")
    print("-" * 100)
    
    total_keys = 0
    passing_keys = 0
    
    for category, category_results in results.items():
        for key, value in category_results.items():
            status = "PASS" if value else "FAIL"
            print(f"{key:<60} {status:<8} {category:<20}")
            total_keys += 1
            if value:
                passing_keys += 1
        
        print(f"\n{category.upper()} SUMMARY: {sum(1 for v in category_results.values() if v)}/{len(category_results)} ({sum(1 for v in category_results.values() if v)/len(category_results)*100:.1f}%)")
        print("-" * 100)
    
    print(f"\nOVERALL TOTAL: {passing_keys}/{total_keys} ({passing_keys/total_keys*100:.1f}%)")

if __name__ == "__main__":
    main()
