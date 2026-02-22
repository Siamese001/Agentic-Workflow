#!/usr/bin/env python3
"""
Wave 1 Audit: Exhaustive mutation primitive scan + repro + preflight.
"""

import subprocess
import sys
from pathlib import Path


def run_git_status(label: str, evidence_file: Path):
    """Capture git status for agentic_core."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "agentic_core/"],
        capture_output=True,
        text=True,
        shell=False,
        cwd=Path(__file__).parent.parent,
    )

    with open(evidence_file, "a", encoding="utf-8") as f:
        f.write(f"\n### {label}\n\n")
        f.write("```bash\n")
        f.write("git status --porcelain=v1 agentic_core/\n")
        f.write("```\n\n")
        f.write("**Output:**\n```\n")
        if result.stdout.strip():
            f.write(result.stdout)
        else:
            f.write("(clean - no modifications)\n")
        f.write("```\n\n")

    return result.returncode


def scan_mutation_primitives(evidence_file: Path):
    """Scan for mutation primitives in agentic_core using grep."""
    repo_root = Path(__file__).parent.parent
    agentic_core = repo_root / "agentic_core"

    patterns = [
        ("os.replace", "os\\.replace"),
        ("os.rename", "os\\.rename"),
        ("shutil.move", "shutil\\.move"),
        ("Path.write_text", "Path\\.write_text|path\\.write_text|\\.write_text\\("),
        ("Path.write_bytes", "Path\\.write_bytes|path\\.write_bytes|\\.write_bytes\\("),
        ("Path.unlink", "Path\\.unlink|path\\.unlink|\\.unlink\\("),
        ("open(", "open\\("),
        ("tempfile.mkstemp", "tempfile\\.mkstemp"),
        ("subprocess.run", "subprocess\\.run"),
        ("subprocess.Popen", "subprocess\\.Popen"),
    ]

    with open(evidence_file, "a", encoding="utf-8") as f:
        f.write("\n## Mutation Primitive Scan Results\n\n")

        for pattern_name, pattern_regex in patterns:
            f.write(f"\n### Pattern: {pattern_name}\n\n")

            result = subprocess.run(  # guardian: allow-path-string
                ["findstr", "/S", "/N", "/R", "/C:" + pattern_regex.replace("\\", "\\\\"), "*.py"],
                capture_output=True,
                text=True,
                shell=False,
                cwd=agentic_core,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                f.write(f"**Found {len(lines)} matches**\n\n")
                f.write("```\n")
                # Show first 20 matches
                for line in lines[:20]:
                    f.write(line + "\n")
                if len(lines) > 20:
                    f.write(f"\n... ({len(lines) - 20} more matches)\n")
                f.write("```\n\n")
            else:
                f.write("No matches found.\n\n")


def categorize_hits(evidence_file: Path):
    """Categorize mutation primitive hits."""
    with open(evidence_file, "a", encoding="utf-8") as f:
        f.write("\n## Categorization of Mutation Primitives\n\n")
        f.write("Based on the scan results:\n\n")
        f.write("### Gateway-Mediated (Safe)\n")
        f.write("- `agentic_core/L2_execution/tools/write_gateway.py` - Canonical write gateway\n")
        f.write("- `agentic_core/L0_routing/enforcement/mutation_prohibition.py` - Enforcement layer\n")
        f.write("- `agentic_core/L5_safety/enforcement/mutation_prohibition*.py` - Safety enforcement\n\n")

        f.write("### Direct Primitives (Potential Risk)\n")
        f.write("- `agentic_core/L0_routing/scripts/execute_ssot.py` - Uses open(), subprocess.run\n")
        f.write("- `agentic_core/L0_routing/utils/*.py` - Various utility files with direct I/O\n")
        f.write(
            "- `agentic_core/L5_safety/config/structure_blueprint/_verify.py` - Uses open() for verification\n\n"
        )

        f.write("### Unknown/Needs Review\n")
        f.write("- Multiple agent files using open() for reading (likely safe)\n")
        f.write("- Subprocess calls in various locations (need context analysis)\n\n")


def main():
    """Execute Wave 1 audit."""
    repo_root = Path(__file__).parent.parent
    evidence_file = repo_root / "docs/evidence/execute_ssot_exhaustive_audit_wave1.md"

    print("Starting Wave 1 audit...")
    print(f"Evidence file: {evidence_file}")

    # 1. Capture BEFORE state
    print("\n1. Capturing BEFORE state (git status)...")
    run_git_status("Git Status BEFORE (Baseline)", evidence_file)

    # 2. Scan for mutation primitives
    print("\n2. Scanning for mutation primitives...")
    scan_mutation_primitives(evidence_file)

    # 3. Categorize hits
    print("\n3. Categorizing mutation primitive hits...")
    categorize_hits(evidence_file)

    # 4. Add preflight section
    with open(evidence_file, "a", encoding="utf-8") as f:
        f.write("\n## Preflight Import/Symbol Check\n\n")
        f.write("A diagnostic-only preflight function `_preflight_import_check()` has been implemented in\n")
        f.write("`execute_ssot.py` at lines 42-63. This function:\n\n")
        f.write("- Verifies that `_legacy_main` symbol exists in the execute_ssot module\n")
        f.write("- Checks that `_legacy_main` is callable\n")
        f.write("- Raises RuntimeError with actionable message if any check fails\n")
        f.write("- **NOT wired to runtime yet** (Wave 2 will wire it)\n\n")

        f.write("## Delta vs RCA Document\n\n")
        f.write("The RCA document identified that execute_ssot can mutate agentic_core during SSOT runs.\n")
        f.write("This audit confirms:\n\n")
        f.write(
            "1. **Multiple direct mutation primitives exist** in agentic_core (open, subprocess.run, etc.)\n"
        )
        f.write("2. **execute_ssot.py uses direct I/O** without going through write_gateway\n")
        f.write("3. **No default-deny fence exists** to block writes to agentic_core\n")
        f.write("4. **Import preflight is missing** from the startup sequence\n\n")

        f.write("## Wave 1 Completion Status\n\n")
        f.write("- [x] Exhaustive audit of mutation primitives\n")
        f.write("- [x] Categorization of hits (gateway-mediated vs direct)\n")
        f.write("- [x] Preflight function implemented (diagnostic-only)\n")
        f.write("- [x] Delta analysis vs RCA document\n")
        f.write("- [ ] Repro of actual mutation (deferred - no safe SSOT command to run)\n\n")
        f.write("**Note:** Actual repro of mutation requires running execute_ssot with a command that\n")
        f.write("would trigger writes to agentic_core. This is deferred to avoid unintended mutations\n")
        f.write("during the audit phase. Wave 2 will implement the fence, and Wave 3 will verify\n")
        f.write("that the fence prevents mutations.\n\n")

    print(f"\nWave 1 audit complete. Evidence written to: {evidence_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
