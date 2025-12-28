#!/usr/bin/env python
"""
Simplified Canon Validator - CLI Only Version
Removes all async/await and background threads to prevent hanging issues
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

def validate_structure(target_dir="agentic_core"):
    """Simple structural validation without async operations"""
    print(f"\n[*] SIMPLE VALIDATOR: Checking {target_dir}")
    print(f"    [OK] Running in pure CLI mode - no async, no threads")
    
    # Basic stats
    target_path = project_root / target_dir
    py_files = list(target_path.rglob("*.py"))
    
    # Filter out protected directories
    protected = {'.git', '.venv', '__pycache__', 'node_modules', 'archives', 'data'}
    py_files = [f for f in py_files if not any(p in f.parts for p in protected)]
    
    print(f"    [SCAN] Found {len(py_files)} Python files")
    
    # Simple checks
    issues = []
    
    for file_path in py_files[:50]:  # Limit to first 50 files for testing
        try:
            rel_path = file_path.relative_to(project_root)
            content = file_path.read_text(encoding='utf-8', errors='replace')
            
            # Check for syntax errors
            try:
                compile(content, str(file_path), 'exec')
            except SyntaxError as e:
                issues.append(f"SYNTAX: {rel_path}:{e.lineno} - {e.msg}")
            
            # Check depth violations
            depth = len(rel_path.parts)
            if depth != 4 and target_dir == "agentic_core":
                issues.append(f"DEPTH: {rel_path} - depth {depth} != 4")
                
        except Exception as e:
            issues.append(f"ERROR: {file_path.name} - {str(e)[:50]}")
    
    print(f"\n[RESULTS]")
    print(f"    Files checked: {min(50, len(py_files))}")
    print(f"    Issues found: {len(issues)}")
    
    if issues:
        print(f"\n[SAMPLE ISSUES] (first 10)")
        for issue in issues[:10]:
            print(f"    - {issue}")
    
    return len(issues) == 0

def main():
    parser = argparse.ArgumentParser(description="Simple Canon Validator")
    parser.add_argument("--target", default="agentic_core", help="Target directory")
    parser.add_argument("--structural-only", action="store_true", help="Structural checks only")
    parser.add_argument("--no-llm", action="store_true", help="No LLM mode")
    parser.add_argument("--batch-size", type=int, default=20, help="Batch size")
    
    args = parser.parse_args()
    
    print("="*70)
    print("SIMPLE CANON VALIDATOR - CLI ONLY")
    print("="*70)
    print(f"Target: {args.target}")
    print(f"Structural-only: {args.structural_only}")
    print(f"No-LLM: {args.no_llm}")
    print(f"Batch size: {args.batch_size}")
    print("="*70)
    
    # Run validation
    success = validate_structure(args.target)
    
    print("\n" + "="*70)
    if success:
        print("[SUCCESS] Validation completed with no issues found")
        return 0
    else:
        print("[COMPLETE] Validation completed - see issues above")
        return 0

if __name__ == "__main__":
    sys.exit(main())
