"""
Sovereign Guard: Block Raw Prompt Strings
Enforces that all prompts must be registered in sovereign_prompt_constitution.py

Usage: Called automatically by pre-commit hook
"""
import re
import sys
from pathlib import Path

# Files exempt from this check (the SSOT itself and test files)
EXEMPT = {
    "agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py",
    "test_",
    "tests/"
}

# Patterns that indicate hardcoded prompts
PROMPT_PATTERNS = [
    r'""".*You are.*"""',  # Triple-quoted strings with "You are"
    r"'''.*You are.*'''",  # Single-quoted strings with "You are"
    r'{"role":\s*"system",\s*"content":\s*"',  # Message dictionaries
    r'f""".*You are.*"""',  # F-strings with prompts
    r'f\'\'\'.*You are.*\'\'\'',
]

def check_file(filepath):
    """Check a single file for hardcoded prompt strings."""
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
            # Skip comments and docstrings at module level
            if line.strip().startswith("#"):
                continue
            
            # Check for prompt patterns
            for pattern in PROMPT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE | re.DOTALL):
                    # Additional check: must contain "You are" to be a prompt
                    if "You are" in line or "you are" in line:
                        violations.append({
                            "line": i,
                            "content": line.strip()[:80]  # First 80 chars
                        })
                        break
        
        if violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for violation in violations:
                print(f"  Line {violation['line']}: {violation['content']}...")
            print("\n💡 SOLUTION: Register this prompt in:")
            print("   agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py")
            print("   Then use: get_prompt('YOUR_PROMPT_ID')")
            print("=" * 80)
            return False
        
        return True
    
    except Exception as e:
        print(f"⚠️  Warning: Could not parse {filepath}: {e}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sovereign_precommit_no_raw_prompts.py <file1> <file2> ...")
        sys.exit(0)
    
    all_passed = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed = False
    
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Hardcoded prompts detected.")
        print("   All prompts must be centralized in sovereign_prompt_constitution.py")
        sys.exit(1)
    
    sys.exit(0)
