#!/usr/bin/env python3
"""Test the .gitignore pattern loading function."""
from pathlib import Path

project_root = Path(__file__).parent

def load_gitignore_patterns():
    """Dynamically ingest Sovereign Protection rules from .gitignore."""
    patterns = {'.git', '__pycache__', '.env'}  # Hard defaults
    gitignore_path = project_root / ".gitignore"
    if gitignore_path.exists():
        for line in gitignore_path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract folder name from patterns like 'data/cache/', 'logs/', '*.pyc'
                clean_pattern = line.rstrip('/')
                # For patterns with paths, take the first component
                if '/' in clean_pattern:
                    clean_pattern = clean_pattern.split('/')[0]
                # Remove wildcards but keep the base name
                clean_pattern = clean_pattern.replace('*', '').strip()
                if clean_pattern and not clean_pattern.startswith('.'):
                    patterns.add(clean_pattern)
                # Also add the full pattern without wildcards for exact matches
                full_pattern = line.rstrip('/').replace('*', '').strip()
                if full_pattern:
                    patterns.add(full_pattern)
    return patterns

# Test the function
patterns = load_gitignore_patterns()
print(f"Loaded {len(patterns)} protection patterns from .gitignore:")
print("\nPatterns (first 20):")
for i, pattern in enumerate(sorted(patterns)[:20], 1):
    print(f"  {i:2}. {pattern}")

print(f"\n... and {len(patterns) - 20} more patterns")

# Verify key patterns are present
expected = ['archives', 'data', 'venv', '.venv', 'logs', 'cache', 'core']
print("\nVerifying expected patterns:")
for exp in expected:
    status = "✓" if exp in patterns else "✗"
    print(f"  {status} {exp}")
