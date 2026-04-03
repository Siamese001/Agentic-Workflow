#!/usr/bin/env python3
"""
Windsurf Skill: PowerShell Guard
Validates that shell commands use subprocess.run(shell=False) instead of PowerShell.
"""

import re
import sys

# guardian: allow-silent-swallower -- Exception handling for subprocess validation
# guardian: allow-magic-configuration -- Command pattern matching for PowerShell detection


def validate_command(command: str, file_path: str) -> tuple[bool, list[str]]:
    """Validate that command doesn't use PowerShell syntax."""
    issues = []

    # PowerShell indicators
    powershell_patterns = [
        r"powershell\.exe",
        r"pwsh\.exe",
        r"cmd\.exe.*\/c",
        r"\$[a-zA-Z_]",
        r"Get-",
        r"Set-",
        r"New-",
        r"Remove-",
        r"Invoke-",
        r"\|\s*Where-Object",
        r"\|\s*Select-Object",
        r"\|\s*ForEach-Object",
    ]

    for pattern in powershell_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            issues.append(f"PowerShell syntax detected: {pattern}")

    # Check for shell=True with subprocess
    if "subprocess.run" in command and "shell=True" in command:
        issues.append("subprocess.run with shell=True detected - use shell=False")

    # Check for direct os.system or os.popen
    if "os.system" in command or "os.popen" in command:
        issues.append("Direct os.system/os.popen detected - use subprocess.run(shell=False)")

    return len(issues) == 0, issues


def main():
    """Main entry point for the skill."""
    if len(sys.argv) == 2 and sys.argv[1] == "--health-check":
        print("[PASS] PowerShell guard health check")
        sys.exit(0)

    if len(sys.argv) != 3:
        print("Usage: python main.py <command> <file_path>")
        sys.exit(1)

    command = sys.argv[1]
    file_path = sys.argv[2]

    is_valid, issues = validate_command(command, file_path)

    if not is_valid:
        print("❌ PowerShell Guard Validation Failed:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n💡 Recommended fix:")
        print("  Use subprocess.run([cmd, arg1, arg2], shell=False, encoding='utf-8')")
        sys.exit(1)
    else:
        print("[PASS] Command passes PowerShell guard validation")
        sys.exit(0)


if __name__ == "__main__":
    main()
