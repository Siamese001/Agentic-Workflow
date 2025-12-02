#!/usr/bin/env python3
"""
Script to extract list of failed schema files
"""

import subprocess
import sys

def get_failed_files():
    """Get list of failed files from validation output"""
    try:
        result = subprocess.run([sys.executable, 'validate_phase1c_schemas.py'], 
                              capture_output=True, text=True, cwd='.')
        
        lines = result.stdout.split('\n')
        failed_files = []
        
        for line in lines:
            if line.startswith('✗ FAIL:'):
                # Extract filename after "FAIL: "
                file_path = line.split('FAIL:')[1].strip()
                failed_files.append(file_path)
        
        return failed_files
    
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    failed_files = get_failed_files()
    print(f"Found {len(failed_files)} failed files:")
    for f in failed_files:
        print(f"  {f}")
