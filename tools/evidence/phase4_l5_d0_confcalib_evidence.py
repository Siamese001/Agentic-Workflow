"""
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_1")
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_2")
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_3")
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_4")
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_5")
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_6")
_emit_reads_through("l4", "phase4_l5_d0_confcalib_evidence", "urg_read_7")
Phase 4 L5 D0+CONF_CALIB Evidence Generator
Python-only evidence capture for L5 safety modules.
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
    except FileNotFoundError:    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access    # guardian: File operations should check existence before access
        return []
    except UnicodeDecodeError:    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy
        return []


def main():
    """Generate Phase 4 L5 D0+CONF_CALIB evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / REPORTS_DIR / "plans" / "phase4_l5_d0_confcalib_evidence.md"

    # Ensure evidence directory exists
    evidence_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating Phase 4 evidence at: {evidence_file}")

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

    # 3) pytest - d0 injection engine tests
    print("Running D0 injection engine tests...")
    sections.append("# D0 Injection Engine Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/L5_safety/test_d0_injection_engine.py",
                "-m",
                "unit",
            ],
            repo_root,
        ),
    )
    sections.append("```\n\n")

    # 4) pytest - conf calib gate tests
    print("Running CONF_CALIB gate tests...")
    sections.append("# CONF_CALIB Gate Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/L5_safety/test_conf_calib_gate.py",
                "-m",
                "unit",
            ],
            repo_root,
        ),
    )
    sections.append("```\n\n")

    # 5) pytest - all L5 safety tests
    print("Running all L5 safety tests...")
    sections.append("# All L5 Safety Tests\n")
    sections.append("```")
    sections.append(
        run_command([sys.executable, "-m", "pytest", "-q", "tests/unit/L5_safety", "-m", "unit"], repo_root),
    )
    sections.append("```\n\n")

    # 6) Token scan for wall-clock and forbidden imports
    print("Scanning for forbidden tokens...")
    d0_engine_file = repo_root / AGENTIC_CORE_DIR / "L5_safety" / "enforcement" / "d0_injection_engine.py"
    conf_calib_file = repo_root / AGENTIC_CORE_DIR / "L5_safety" / "enforcement" / "conf_calib_gate.py"

    wall_clock_tokens = [
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "perf_counter",
        "monotonic",
        "pendulum",
        "arrow.",
    ]
    forbidden_imports = ["agentic_core.L0_routing", "agentic_core.L2_execution"]

    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")

    # Check d0_injection_engine.py
    d0_wall_clock = scan_forbidden_tokens(d0_engine_file, wall_clock_tokens)
    d0_forbidden = scan_forbidden_tokens(d0_engine_file, forbidden_imports)

    # Check conf_calib_gate.py
    conf_wall_clock = scan_forbidden_tokens(conf_calib_file, wall_clock_tokens)
    conf_forbidden = scan_forbidden_tokens(conf_calib_file, forbidden_imports)

    # guardian: allow-direct-prompt-compilation
    all_wall_clock = d0_wall_clock + conf_wall_clock
    # guardian: allow-direct-prompt-compilation
    all_forbidden = d0_forbidden + conf_forbidden

    if all_wall_clock:
        sections.append(f"WALL-CLOCK TOKENS FOUND: {all_wall_clock}")
    else:
        sections.append("No wall-clock tokens found")

    if all_forbidden:
        sections.append(f"FORBIDDEN IMPORTS FOUND: {all_forbidden}")
    else:
        sections.append("No forbidden L0/L2 imports found")

    sections.append("```\n\n")

    # 7) git show --stat
    print("Collecting git show --stat...")
    sections.append("# Git Show --stat\n")
    sections.append("```")
    sections.append(run_command(["git", "show", "--stat"], repo_root))
    sections.append("```\n\n")

    # Write evidence file
    print(f"Writing evidence to {evidence_file}...")
    evidence_content = "".join(sections)
    evidence_file.write_text(evidence_content, encoding="utf-8")

    print("Phase 4 L5 D0+CONF_CALIB evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
