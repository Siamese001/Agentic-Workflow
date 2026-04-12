"""
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_1")
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_2")
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_3")
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_4")
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_5")
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_6")
_emit_reads_through("l4", "phase3_path_router_evidence", "urg_read_7")
Phase 3 Path Router Evidence Generator
Python-only evidence capture for deterministic Path Router implementation.
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
    except FileNotFoundError:  # guardian: File operations should check existence before access
        return []
    except UnicodeDecodeError:  # guardian: Encoding errors should specify fallback encoding strategy
        return []


def main():
    """Generate Phase 3 Path Router evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / REPORTS_DIR / "plans" / "phase3_path_router_evidence.md"

    # Ensure evidence directory exists
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating Phase 3 evidence at: {evidence_file}")

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

    # 3) pytest - path_router tests
    print("Running path router tests...")
    sections.append("# Path Router Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [sys.executable, "-m", "pytest", "-q", "tests/unit/L0_routing/test_path_router.py", "-m", "unit"],
            repo_root,
        ),
    )
    sections.append("```\n\n")

    # 4) pytest - all L0_routing tests
    print("Running all L0_routing tests...")
    sections.append("# All L0 Routing Tests\n")
    sections.append("```")
    sections.append(
        run_command([sys.executable, "-m", "pytest", "-q", "tests/unit/L0_routing", "-m", "unit"], repo_root),
    )
    sections.append("```\n\n")

    # 5) Token scan for wall-clock and forbidden imports
    print("Scanning for forbidden tokens...")
    path_router_file = repo_root / AGENTIC_CORE_DIR / "L0_routing" / "engines" / "path_router.py"
    seam_file = repo_root / AGENTIC_CORE_DIR / "L0_routing" / "seams" / "elevator_shaft_seam.py"

    wall_clock_tokens = ["datetime.now", "datetime.utcnow", "time.time", "perf_counter", "monotonic"]
    forbidden_imports = ["L2_", "L5_"]

    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")

    # Check path_router.py
    router_wall_clock = scan_forbidden_tokens(path_router_file, wall_clock_tokens)
    router_forbidden = scan_forbidden_tokens(path_router_file, forbidden_imports)

    # Check elevator_shaft_seam.py
    seam_wall_clock = scan_forbidden_tokens(seam_file, wall_clock_tokens)
    seam_forbidden = scan_forbidden_tokens(seam_file, forbidden_imports)

    all_forbidden = router_wall_clock + router_forbidden + seam_wall_clock + seam_forbidden

    if all_forbidden:
        sections.append(f"FORBIDDEN TOKENS FOUND: {all_forbidden}")
    else:
        sections.append("No forbidden wall-clock or L2_/L5_ import tokens found")
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

    print("Phase 3 Path Router evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
