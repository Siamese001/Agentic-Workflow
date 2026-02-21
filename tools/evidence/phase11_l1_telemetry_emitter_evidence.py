"""
Phase 11 L1 Telemetry Emitter Evidence Generator
Python-only evidence capture for L1 cognition telemetry emission.
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
    """Generate Phase 11 L1 Telemetry Emitter evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase11_l1_telemetry_emitter_evidence.md"

    # Ensure evidence directory exists
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating Phase 11 evidence at: {evidence_file}")

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

    # 3) pytest - telemetry emitter tests
    print("Running telemetry emitter tests...")
    sections.append("# Telemetry Emitter Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/L1_cognition/test_telemetry_emitter.py",
                "-m",
                "unit",
            ],
            repo_root,
        )
    )
    sections.append("```\n\n")

    # 4) pytest - all L1 cognition tests
    print("Running all L1 cognition tests...")
    sections.append("# All L1 Cognition Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [sys.executable, "-m", "pytest", "-q", "tests/unit/L1_cognition", "-m", "unit"], repo_root
        )
    )
    sections.append("```\n\n")

    # 5) Token scans over telemetry_emitter.py
    print("Scanning for forbidden tokens...")
    emitter_file = repo_root / "agentic_core" / "L1_cognition" / "telemetry" / "telemetry_emitter.py"

    wall_clock_tokens = [
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "perf_counter",
        "monotonic",
        "pendulum",
        "arrow.",
    ]
    forbidden_coupling_tokens = ["agentic_core.L2_execution", "agentic_core.L5_safety"]
    forbidden_io_tokens = ["open(", "Path(", "write_text", "write_bytes"]

    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")

    # Check wall-clock tokens
    wall_clock_found = scan_forbidden_tokens(emitter_file, wall_clock_tokens)

    # Check forbidden coupling tokens
    coupling_found = scan_forbidden_tokens(emitter_file, forbidden_coupling_tokens)

    # Check forbidden I/O tokens
    io_found = scan_forbidden_tokens(emitter_file, forbidden_io_tokens)

    if wall_clock_found:
        sections.append(f"WALL-CLOCK TOKENS FOUND: {wall_clock_found}")
    else:
        sections.append("No wall-clock tokens found")

    if coupling_found:
        sections.append(f"FORBIDDEN COUPLING TOKENS FOUND: {coupling_found}")
    else:
        sections.append("No forbidden L2/L5 coupling tokens found")

    if io_found:
        sections.append(f"FORBIDDEN I/O TOKENS FOUND: {io_found}")
    else:
        sections.append("No forbidden I/O tokens found")

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

    print("Phase 11 L1 Telemetry Emitter evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
