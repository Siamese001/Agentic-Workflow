from __future__ import annotations

"""
Sovereign Guard: Block Raw Prompt Strings
Enforces that all prompts must be registered in sovereign_prompt_constitution.py

Usage: Called automatically by pre-commit hook
"""
import re
import sys
from pathlib import Path
from typing import Any

exempt: Any = {
    "agentic_core/prompt_governance/meta_prompts/sovereign_prompt_constitution.py",
    "test_",
    "tests/",
}
prompt_patterns: Any = [
    '""".*You are.*"""',
    "'''.*You are.*'''",
    '{"role":\\s*"system",\\s*"content":\\s*"',
    'f""".*You are.*"""',
    "f\\'\\'\\'.*You are.*\\'\\'\\'",
]


def check_file(filepath: Any) -> Any:
    """Check a single file for hardcoded prompt strings."""
    normalized_path: Any = str(Path(filepath)).replace("\\", "/")
    if any(exempt in normalized_path for exempt in EXEMPT):
        return True
    try:
        with open(filepath, encoding="utf-8") as f:
            content: Any = f.read()
        violations: Any = []
        lines: Any = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line.strip().startswith("#"):
                continue
            for pattern in PROMPT_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE | re.DOTALL):
                    if "You are" in line or "you are" in line:
                        violations.append({"line": i, "content": line.strip()[:80]})
                        break
        if violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for Violation in violations:
                print(f"  Line {Violation['line']}: {Violation['content']}...")
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
    all_passed: Any = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed: Any = False
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Hardcoded prompts detected.")
        print("   All prompts must be centralized in sovereign_prompt_constitution.py")
        sys.exit(1)
    sys.exit(0)
