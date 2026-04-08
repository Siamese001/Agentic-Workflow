#!/usr/bin/env python3
"""
Security Hardening — Secret Detection Gate

Enforces security-hardening rule §1: No hardcoded secrets in production code.
Blocks commits if staged files contain:
- Hardcoded passwords, API keys, tokens, or credentials
- Hardcoded database connection strings with credentials
- Hardcoded private keys or certificates

Allowed patterns:
- References to environment variables: os.environ.get("API_KEY")
- References to config files: config.get_api_key()
- Placeholder values in tests: "test_api_key" or "dummy_secret"
- Documentation examples with clear "YOUR_KEY_HERE" markers
"""

import re
import sys
from pathlib import Path

# Patterns that indicate hardcoded secrets
SECRET_PATTERNS = [
    r'password\s*=\s*["\'][^"\']{8,}["\']',  # password = "long_string"
    r'api[_-]?key\s*=\s*["\'][^"\']{8,}["\']',  # api_key = "long_string"
    r'secret[_-]?key\s*=\s*["\'][^"\']{8,}["\']',  # secret_key = "long_string"
    r'token\s*=\s*["\'][^"\']{8,}["\']',  # token = "long_string"
    r'private[_-]?key\s*=\s*["\'][^"\']{20,}["\']',  # private_key = "very_long_string"
    r'connection_string\s*=\s*["\'][^"\']*password[^"\']*["\']',  # connection string with password
    r'mongodb://[^:]+:[^@]+@',  # MongoDB URI with password
    r'postgres://[^:]+:[^@]+@',  # PostgreSQL URI with password
    r'mysql://[^:]+:[^@]+@',  # MySQL URI with password
]

# Patterns that are allowed (test placeholders, env refs, etc.)
ALLOWED_PATTERNS = [
    r'(test_|dummy_|mock_|placeholder)_',  # test placeholders
    r'YOUR_KEY_HERE',  # documentation placeholders
    r'os\.environ\.get\(',  # environment variable references
    r'config\.get_\w+\(',  # config file references
    r'\$\{\w+\}',  # shell variable references
]


def is_allowed_match(line: str, _match: re.Match) -> bool:
    """Check if a potential secret match is actually an allowed pattern."""
    for pattern in ALLOWED_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def scan_file(file_path: Path) -> list[tuple[int, str]]:
    """Scan a single file for hardcoded secrets."""
    violations = []
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern in SECRET_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    if not is_allowed_match(line, match):
                        violations.append((line_num, line.strip()))
                        break  # Only report first violation per line
    except (OSError, UnicodeDecodeError):
        pass  # Skip files that can't be read

    return violations


def main():
    """Scan staged files for hardcoded secrets."""
    # Get staged files from git
    import subprocess
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print("ERROR: Failed to get staged files")
        sys.exit(1)

    staged_files = result.stdout.strip().split('\n')
    staged_files = [f for f in staged_files if f and not f.startswith('.')]

    violations = []
    self_rel_path = Path(__file__).resolve().relative_to(Path.cwd().resolve())

    for file_path in staged_files:
        path = Path(file_path)
        if path == self_rel_path:
            continue
        if len(path.parts) >= 2 and path.parts[:2] == ("ops_scripts", "ci") and path.name.startswith("check_") and path.suffix == ".py":
            continue
        if path.suffix in ('.py', '.yaml', '.yml', '.json', '.env'):
            file_violations = scan_file(path)
            for line_num, line in file_violations:
                violations.append((str(path), line_num, line))

    if violations:
        print("[FAIL] SECURITY VIOLATION: Hardcoded secrets detected in staged files")
        print()
        for file_path, line_num, line in violations:
            print(f"  {file_path}:{line_num}: {line}")
        print()
        print("Fix required:")
        print("  1. Move secrets to environment variables: os.environ.get('API_KEY')")
        print("  2. Use config files: config.get_api_key()")
        print("  3. For tests: use 'test_api_key' or 'dummy_secret' placeholders")
        sys.exit(1)

    print("[OK] No hardcoded secrets detected in staged files")
    sys.exit(0)


if __name__ == '__main__':
    main()
