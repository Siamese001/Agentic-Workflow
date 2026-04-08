#!/usr/bin/env python3
"""
Security Hardening — Sensitive Data in Logs Gate

Enforces security-hardening rule §2: No sensitive data in log output.
Blocks commits if staged files log:
- API keys, tokens, passwords
- Personal identifiable information (PII)
- Credit card numbers or financial data
- Session tokens or cookies
- Database connection strings with credentials

Required masking:
- Mask sensitive values: "API_KEY: ***" or "password: [REDACTED]"
- Log only non-sensitive identifiers: user_id, request_id
"""

import re
import sys
from pathlib import Path

# Patterns that indicate sensitive data in logs
SENSITIVE_LOG_PATTERNS = [
    # Logging statements with sensitive data
    r"logger\.(debug|info|warning|error|critical)\([^)]*password[^)]*\)",  # logger.info(f"password: {pwd}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*api[_-]?key[^)]*\)",  # logger.info(f"api_key: {key}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*token[^)]*\)",  # logger.info(f"token: {token}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*secret[^)]*\)",  # logger.info(f"secret: {secret}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*credit[_-]?card[^)]*\)",  # logger.info(f"credit_card: {cc}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*ssn[^)]*\)",  # logger.info(f"ssn: {ssn}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*session[^)]*\)",  # logger.info(f"session: {session}")
    r"logger\.(debug|info|warning|error|critical)\([^)]*cookie[^)]*\)",  # logger.info(f"cookie: {cookie}")
    # Print statements with sensitive data
    r"print\([^)]*password[^)]*\)",  # print(f"password: {pwd}")
    r"print\([^)]*api[_-]?key[^)]*\)",  # print(f"api_key: {key}")
    r"print\([^)]*token[^)]*\)",  # print(f"token: {token}")
    # Connection strings in logs
    r"logger\.(debug|info|warning|error|critical)\([^)]*mongodb://[^:]+:[^@]+@[^)]*\)",  # MongoDB URI with password
    r"logger\.(debug|info|warning|error|critical)\([^)]*postgres://[^:]+:[^@]+@[^)]*\)",  # PostgreSQL URI
    r"logger\.(debug|info|warning|error|critical)\([^)]*mysql://[^:]+:[^@]+@[^)]*\)",  # MySQL URI
]

# Patterns that are allowed (masked values, non-sensitive identifiers)
ALLOWED_LOG_PATTERNS = [
    r"\*\*\*",  # Masked values: "password: ***"
    r"\[REDACTED\]",  # Masked values: "password: [REDACTED]"
    r"<hidden>",  # Masked values: "password: <hidden>"
    r"<redacted>",  # Masked values: "password: <redacted>"
    r"user_id",  # Non-sensitive identifiers
    r"request_id",  # Non-sensitive identifiers
    r"trace_id",  # Non-sensitive identifiers
    r"correlation_id",  # Non-sensitive identifiers
]


def is_allowed_log(line: str, _match: re.Match) -> bool:
    """Check if a potential sensitive log is actually masked or safe."""
    for pattern in ALLOWED_LOG_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def scan_file(file_path: Path) -> list[tuple[int, str]]:
    """Scan a single file for sensitive data in logs."""
    violations = []
    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for pattern in SENSITIVE_LOG_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    if not is_allowed_log(line, match):
                        violations.append((line_num, line.strip()))
                        break  # Only report first violation per line
    except (OSError, UnicodeDecodeError):
        pass  # Skip files that can't be read

    return violations


def main():
    """Scan staged files for sensitive data in logs."""
    import subprocess

    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        print("ERROR: Failed to get staged files")
        sys.exit(1)

    staged_files = result.stdout.strip().split("\n")
    staged_files = [
        f for f in staged_files if f and not f.startswith(".") and not f.startswith("tools/archive/")
    ]

    violations = []
    self_rel_path = Path(__file__).resolve().relative_to(Path.cwd().resolve())
    for file_path in staged_files:
        path = Path(file_path)
        if path == self_rel_path:
            continue
        if (
            len(path.parts) >= 2
            and path.parts[:2] == ("ops_scripts", "ci")
            and path.name.startswith("check_")
            and path.suffix == ".py"
        ):
            continue
        if path.suffix in (".py", ".yaml", ".yml"):
            file_violations = scan_file(path)
            for line_num, line in file_violations:
                violations.append((str(path), line_num, line))

    if violations:
        print("[FAIL] SECURITY VIOLATION: Sensitive data in logs detected in staged files")
        print()
        for file_path, line_num, line in violations:
            print(f"  {file_path}:{line_num}: {line}")
        print()
        print("Fix required:")
        print("  1. Mask sensitive values: logger.info(f'API_KEY: ***')")
        print("  2. Use redaction: logger.info(f'password: [REDACTED]')")
        print("  3. Log only non-sensitive identifiers: user_id, request_id, trace_id")
        sys.exit(1)

    print("[OK] No sensitive data in logs detected in staged files")
    sys.exit(0)


if __name__ == "__main__":
    main()
