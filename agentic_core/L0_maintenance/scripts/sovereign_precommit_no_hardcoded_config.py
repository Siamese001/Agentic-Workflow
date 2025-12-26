"""
Sovereign Guard: Block Hardcoded Configuration Constants
Enforces that all operational constants must be centralized in sovereign_config.py

Usage: Called automatically by pre-commit hook
"""
import ast
import re
import sys
from pathlib import Path

# Files exempt from this check (the SSOT itself)
EXEMPT = {
    "agentic_core/config/blueprint_sovereign/environments/sovereign_config.py",
    "test_",
    "tests/"
}

# Patterns that indicate hardcoded configuration
HARDCODED_PATTERNS = [
    (r'PRIMARY_MODEL\s*=\s*["\']', "Model selection"),
    (r'REASONING_MODEL\s*=\s*["\']', "Model selection"),
    (r'MAX_RETRY_ATTEMPTS\s*=\s*\d+', "Retry configuration"),
    (r'CHECKPOINT_INTERVAL\s*=\s*\d+', "Checkpoint configuration"),
    (r'SEMANTIC_SIMILARITY_THRESHOLD\s*=\s*[\d.]+', "Threshold configuration"),
    (r'BASE_GIT_PATH\s*=\s*["\']', "Path configuration"),
    (r'gpt-4o["\']', "Hardcoded model name"),
    (r'o1-preview["\']', "Hardcoded model name"),
]

def check_file(filepath):
    """Check a single file for hardcoded configuration constants."""
    # Normalize path for comparison
    normalized_path = str(Path(filepath)).replace("\\", "/")
    
    # Skip exempt files
    if any(exempt in normalized_path for exempt in EXEMPT):
        return True
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        violations = []
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("#"):
                continue
            
            # Check for hardcoded patterns
            for pattern, description in HARDCODED_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        "line": i,
                        "type": description,
                        "content": line.strip()[:80]
                    })
                    break
        
        if violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for violation in violations:
                print(f"  Line {violation['line']} ({violation['type']}): {violation['content']}...")
            print("\n💡 SOLUTION: Centralize this constant in:")
            print("   agentic_core/config/blueprint_sovereign/environments/sovereign_config.py")
            print("   Then use: from sovereign_config import config")
            print("=" * 80)
            return False
        
        return True
    
    except Exception as e:
        print(f"⚠️  Warning: Could not parse {filepath}: {e}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sovereign_precommit_no_hardcoded_config.py <file1> <file2> ...")
        sys.exit(0)
    
    all_passed = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed = False
    
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Hardcoded configuration detected.")
        print("   All config constants must be centralized in sovereign_config.py")
        sys.exit(1)
    
    sys.exit(0)
