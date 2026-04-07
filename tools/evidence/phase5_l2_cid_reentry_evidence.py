"""
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_1")
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_2")
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_3")
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_4")
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_5")
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_6")
_emit_reads_through("l4", "phase5_l2_cid_reentry_evidence", "urg_read_7")
Phase 5 L2 CID+ReEntry Evidence Generator
Python-only evidence capture for L2 execution modules.
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import REPORTS_DIR


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
    except FileNotFoundError:    # guardian: File operations should check existence before access
        return []
    except UnicodeDecodeError:    # guardian: Encoding errors should specify fallback encoding strategy
        return []


def main():
    """Generate Phase 5 L2 CID+ReEntry evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / REPORTS_DIR / "plans" / "phase5_l2_cid_reentry_evidence.md"

    # Ensure evidence directory exists
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating Phase 5 evidence at: {evidence_file}")

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

    # 3) pytest - all L2 execution tests
    print("Running all L2 execution tests...")
    sections.append("# All L2 Execution Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [sys.executable, "-m", "pytest", "-q", "tests/unit/L2_execution", "-m", "unit"], repo_root,
        ),
    )
    sections.append("```\n\n")

    # 4) Token scan for wall-clock tokens
    print("Scanning for wall-clock tokens...")
    cid_registry_file = repo_root / AGENTIC_CORE_DIR / "L2_execution" / "cid_registry.py"
    reentry_loop_file = repo_root / AGENTIC_CORE_DIR / "L2_execution" / "reentry_loop.py"

    wall_clock_tokens = [
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "perf_counter",
        "monotonic",
        "sleep",
        "time.sleep",
    ]

    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")

    # Check cid_registry.py
    cid_wall_clock = scan_forbidden_tokens(cid_registry_file, wall_clock_tokens)

    # Check reentry_loop.py
    reentry_wall_clock = scan_forbidden_tokens(reentry_loop_file, wall_clock_tokens)

    all_wall_clock = cid_wall_clock + reentry_wall_clock

    if all_wall_clock:
        sections.append(f"WALL-CLOCK TOKENS FOUND: {all_wall_clock}")
    else:
        sections.append("No wall-clock tokens found in L2 modules")

    sections.append("```\n\n")

    # 5) git show --stat
    print("Collecting git show --stat...")
    sections.append("# Git Show --stat\n")
    sections.append("```")
    sections.append(run_command(["git", "show", "--stat"], repo_root))
    sections.append("```\n\n")

    # Write evidence file
    print(f"Writing evidence to {evidence_file}...")
    evidence_content = "".join(sections)
    evidence_file.write_text(evidence_content, encoding="utf-8")

    print("Phase 5 L2 CID+ReEntry evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
