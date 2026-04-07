"""ruff_severity_gate.py — Tiered Ruff severity gate for pre-commit.

Runs Ruff in two passes:
  Pass 1 (BLOCKING)     — P0 (CRITICAL) + P1 (HIGH) rules → exits 1 on violations
  Pass 2 (NON-BLOCKING) — P2 (MEDIUM) + P3 (LOW) rules   → always exits 0

This preserves the original 4-hook severity semantics in a single subprocess-
efficient wrapper while keeping the pre-commit hook count at 1 instead of 4.

SEVERITY SSOT: agentic_core.L5_safety.config.severity.SeverityLevel
P-NUMBER NAMESPACES:
  Ruff:  P0=CRITICAL  P1=HIGH  P2=MEDIUM  P3=LOW
  ADG:   CRITICAL     HIGH     MEDIUM     LOW  (legacy aliases: P1/P2/P3/P4)
"""

import subprocess
import sys

# ---------------------------------------------------------------------------
# Rule sets — sourced from priority_definitions.json SSOT
# B904 appears in both P0 and P1; deduplicated here (included in P0 only).
# ---------------------------------------------------------------------------

# P0: CRITICAL — Security / Safety / Runtime  → BLOCKING
_P0_RULES = "F821,F401,B012,B904,S102,S307,S601,F541,B013,B015"

# P1: HIGH — Bug Patterns / Code Quality       → BLOCKING
_P1_RULES = "B002,B006,B009,B010,B019,B027,S105,S106,S107,S108,S311,S324,S603,S607,UP028,C401,C402,C403,C404"

# P2: MEDIUM — Style / Organisation            → NON-BLOCKING (warn only)
_P2_RULES = "E402,E721,E731,F811,B007,B011,B023,B024,B028,C405,C406,C408,C409,C410,C411,COM812,COM819,I001"

# P3: LOW — Formatting / Python3 modernisation → NON-BLOCKING (info only)
_P3_RULES = "E501,W291,W292,W293,W505,T201,T203,UP001,UP003,UP004,UP005,UP008,UP009,UP010"

_BLOCKING_RULES = f"{_P0_RULES},{_P1_RULES}"
_NONBLOCKING_RULES = f"{_P2_RULES},{_P3_RULES}"

_EXCLUDE = "ops_scripts/ci/check_anti_patterns.py"


def _run_ruff(select: str, extra_args: list[str], files: list[str]) -> int:
    cmd = [
        sys.executable,
        "-m",
        "ruff",
        "check",
        f"--select={select}",
        "--fix",
        f"--exclude={_EXCLUDE}",
        *extra_args,
        *files,
    ]
    result = subprocess.run(cmd)
    return result.returncode


def main() -> int:
    # Files passed by pre-commit via stdin / positional args.
    # pre-commit sets pass_filenames: false so we target the whole repo
    # (ruff will respect its own exclude settings).
    files: list[str] = sys.argv[1:]

    # --- Pass 1: BLOCKING (P0 + P1) ---
    rc_blocking = _run_ruff(_BLOCKING_RULES, [], files)

    # --- Pass 2: NON-BLOCKING (P2 + P3) ---
    _run_ruff(_NONBLOCKING_RULES, ["--exit-zero"], files)

    # Exit code is driven entirely by the blocking pass.
    return rc_blocking


if __name__ == "__main__":
    sys.exit(main())
