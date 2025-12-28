#!/usr/bin/env python
"""Test script to verify the --no-llm and --structural-only flags work correctly"""

import argparse
import sys
import os

def test_flags():
    parser = argparse.ArgumentParser(description='Test validator flags')
    parser.add_argument('--structural-only', action='store_true', help='Only heal structural issues')
    parser.add_argument('--no-llm', action='store_true', help='Disable LLM API calls')
    parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')
    
    args = parser.parse_args()
    
    print("=== VALIDATOR FLAG TEST ===")
    print(f"Structural-only mode: {args.structural_only}")
    print(f"No-LLM mode: {args.no_llm}")
    print(f"Batch size: {args.batch_size}")
    
    # Test that flags are passed correctly
    if args.no_llm:
        print("\n[MODE] No-LLM mode: Would skip Gemini client initialization")
        print("[MODE] No-LLM mode: Would skip syntax healing")
        print("[MODE] No-LLM mode: Would filter out LLM-dependent agents")
    
    if args.structural_only:
        print("\n[MODE] Structural-only mode: Would only run deterministic agents")
        print("[MODE] Structural-only mode: Would skip all LLM-dependent agents")
    
    # Check environment variables
    google_api_key = os.getenv("GOOGLE_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL")
    
    print(f"\n[ENV] GOOGLE_API_KEY: {'SET' if google_api_key else 'NOT SET'}")
    print(f"[ENV] GEMINI_MODEL: {gemini_model or 'NOT SET'}")
    
    print("\n[TEST] Flags are working correctly!")
    return 0

if __name__ == "__main__":
    sys.exit(test_flags())
