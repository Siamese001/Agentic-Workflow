"""
Phase 7 L6 Vigilance Dispatcher Evidence Generator
Python-only evidence capture for L6 observability modules.
"""

import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path:
    """Find repository root by walking up to find .git directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find repository root")


def run_command(cmd: list[str], cwd: Path) -> str:
    """Run command and capture stdout+stderr."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout + result.stderr


def scan_forbidden_tokens(file_path: Path, forbidden_tokens: list[str]) -> list[str]:
    """Scan file for forbidden tokens."""
    try:
        content = file_path.read_text(encoding="utf-8")
        found = []
        for token in forbidden_tokens:
            if token in content:
                found.append(token)
        return found
    except FileNotFoundError:
        return []
    except UnicodeDecodeError:
        return []


def main():
    """Generate Phase 7 L6 Vigilance Dispatcher evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase7_l6_vigilance_dispatcher_evidence.md"

    # Ensure evidence directory exists
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating Phase 7 evidence at: {evidence_file}")

    # Collect evidence sections
    sections = []

    # 1) git rev-parse HEAD
    print("Collecting git HEAD...")
    sections.append("# Git HEAD\n")
    sections.append("```")
    sections.append(run_command(["git", "rev-parse", "HEAD"], repo_root).strip())
    sections.append("```\n\n")

    # 2) git status --porcelain
    print("Collecting git status...")
    sections.append("# Git Status\n")
    sections.append("```")
    sections.append(run_command(["git", "status", "--porcelain"], repo_root).strip())
    sections.append("```\n\n")

    # 3) pytest - vigilance dispatcher tests
    print("Running vigilance dispatcher tests...")
    sections.append("# Vigilance Dispatcher Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/L6_observability/test_vigilance_dispatcher.py",
                "-m",
                "unit",
            ],
            repo_root,
        )
    )
    sections.append("```\n\n")

    # 4) pytest - all L6 observability tests
    print("Running all L6 observability tests...")
    sections.append("# All L6 Observability Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [sys.executable, "-m", "pytest", "-q", "tests/unit/L6_observability", "-m", "unit"], repo_root
        )
    )
    sections.append("```\n\n")

    # 5) Token scan for wall-clock and forbidden authority/import tokens
    print("Scanning for forbidden tokens...")
    dispatcher_file = repo_root / "agentic_core" / "L6_observability" / "engines" / "vigilance_dispatcher.py"

    wall_clock_tokens = [
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "perf_counter",
        "monotonic",
        "pendulum",
        "arrow.",
    ]
    forbidden_authority_tokens = [
        "agentic_core.L4_state",
        "agentic_core.L2_execution",
        "agentic_core.L5_safety",
    ]

    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")

    # Check wall-clock tokens
    wall_clock_found = scan_forbidden_tokens(dispatcher_file, wall_clock_tokens)

    # Check forbidden authority/import tokens
    authority_found = scan_forbidden_tokens(dispatcher_file, forbidden_authority_tokens)

    if wall_clock_found:
        sections.append(f"WALL-CLOCK TOKENS FOUND: {wall_clock_found}")
    else:
        sections.append("No wall-clock tokens found")

    if authority_found:
        sections.append(f"FORBIDDEN AUTHORITY TOKENS FOUND: {authority_found}")
    else:
        sections.append("No forbidden L4/L2/L5 imports found")

    sections.append("```\n\n")

    # 6) git show --stat
    print("Collecting git show --stat...")
    sections.append("# Git Show --stat\n")
    sections.append("```")
    sections.append(run_command(["git", "show", "--stat"], repo_root))
    sections.append("```\n\n")

    # Write evidence file
    print(f"Writing evidence to {evidence_file}...")
    evidence_content = "".join(sections)
    evidence_file.write_text(evidence_content, encoding="utf-8")

    print("Phase 7 L6 Vigilance Dispatcher evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
