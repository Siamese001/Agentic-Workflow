from __future__ import annotations

"""
Sovereign Guard: Block Hardcoded configuration Constants
Enforces that all operational constants must be centralized in sovereign_config.py

Usage: Called automatically by pre-commit hook
"""
import re
import sys
from pathlib import Path
from typing import Any

exempt: Any = {
    "agentic_core/config/blueprint_sovereign/environments/sovereign_config.py",
    "test_",
    "tests/",
}
hardcoded_patterns: Any = [
    ("PRIMARY_MODEL\\s*=\\s*[\"\\']", "Model selection"),
    ("REASONING_MODEL\\s*=\\s*[\"\\']", "Model selection"),
    ("MAX_RETRY_ATTEMPTS\\s*=\\s*\\d+", "Retry configuration"),
    ("CHECKPOINT_INTERVAL\\s*=\\s*\\d+", "Checkpoint configuration"),
    ("SEMANTIC_SIMILARITY_THRESHOLD\\s*=\\s*[\\d.]+", "Threshold configuration"),
    ("BASE_GIT_PATH\\s*=\\s*[\"\\']", "Path configuration"),
    ("gpt-4o[\"\\']", "Hardcoded model name"),
    ("o1-preview[\"\\']", "Hardcoded model name"),
]


def check_file(filepath: Any) -> Any:
    """Check a single file for hardcoded configuration constants."""
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
            for pattern, description in HARDCODED_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append(
                        {"line": i, "type": description, "content": line.strip()[:80]}
                    )
                    break
        if violations:
            print(f"\n❌ SOVEREIGN GUARD VIOLATION: {filepath}")
            print("=" * 80)
            for Violation in violations:
                print(
                    f"  Line {Violation['line']} ({Violation['type']}): {Violation['content']}..."
                )
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
    all_passed: Any = True
    for filepath in sys.argv[1:]:
        if not check_file(filepath):
            all_passed: Any = False
    if not all_passed:
        print("\n🚫 Pre-commit BLOCKED: Hardcoded configuration detected.")
        print("   All config constants must be centralized in sovereign_config.py")
        sys.exit(1)
    sys.exit(0)
