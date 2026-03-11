"""
Phase 9 Outcome Logger Evidence Generator
Python-only evidence capture for L6 observability outcome logging.
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, get_validated_project_root


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def get_repo_root() -> Path:
    return get_validated_project_root()


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
    """Generate Phase 9 Outcome Logger evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / REPORTS_DIR / "plans" / "phase9_outcome_logger_evidence.md"

    # Ensure evidence directory exists
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating Phase 9 evidence at: {evidence_file}")

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

    # 3) pytest - outcome logger tests
    print("Running outcome logger tests...")
    sections.append("# Outcome Logger Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/L6_observability/test_outcome_logger.py",
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

    # 5) Token scan for wall-clock, disk I/O, and forbidden L4 tokens
    print("Scanning for forbidden tokens...")
    outcome_logger_file = (
        repo_root / AGENTIC_CORE_DIR / "L6_observability" / "enforcement" / "outcome_logger.py"
    )

    wall_clock_tokens = [
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "perf_counter",
        "monotonic",
        "pendulum",
        "arrow.",
    ]
    disk_io_tokens = ["open(", "Path(", "write_text", "write_bytes"]
    forbidden_l4_tokens = ["agentic_core.L4_state"]

    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")

    # Check wall-clock tokens
    wall_clock_found = scan_forbidden_tokens(outcome_logger_file, wall_clock_tokens)

    # Check disk I/O tokens
    disk_io_found = scan_forbidden_tokens(outcome_logger_file, disk_io_tokens)

    # Check forbidden L4 tokens
    l4_found = scan_forbidden_tokens(outcome_logger_file, forbidden_l4_tokens)

    if wall_clock_found:
        sections.append(f"WALL-CLOCK TOKENS FOUND: {wall_clock_found}")
    else:
        sections.append("No wall-clock tokens found")

    if disk_io_found:
        sections.append(f"DISK I/O TOKENS FOUND: {disk_io_found}")
    else:
        sections.append("No disk I/O tokens found")

    if l4_found:
        sections.append(f"FORBIDDEN L4 TOKENS FOUND: {l4_found}")
    else:
        sections.append("No direct L4 coupling tokens found")

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

    print("Phase 9 Outcome Logger evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
