"""
CANONICAL COMMAND CAPTURE SNIPPETS
Usage: copy-paste patterns from this file into evidence generation scripts.
All outputs MUST be captured via subprocess.run with stdout/stderr to evidence file.
PowerShell invocation is FORBIDDEN per §2.1.
"""

import subprocess
import sys
from pathlib import Path

# --- SETUP: Define evidence file path ONCE at session start ---
E = Path(".windsurf/plans/<evidence_file>.md")

# ============================================================
# CORE CAPTURE HELPER
# Use this for every command executed during a work unit.
# ============================================================

def capture(args: list[str], evidence_path: Path, cwd: Path | None = None) -> int:
    """
    Run a command and append stdout+stderr to the evidence file.

    Args:
        args: Command as list of strings (shell=False, no PowerShell)
        evidence_path: Path to the evidence .md file
        cwd: Working directory (defaults to repo root)

    Returns:
        Return code of the command
    """
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        shell=False,
    )
    with open(evidence_path, "a", encoding="utf-8") as f:
        f.write(f"\n$ {' '.join(str(a) for a in args)}\n")
        if result.stdout:
            f.write(result.stdout)
        if result.stderr:
            f.write(result.stderr)
    return result.returncode


# ============================================================
# MANDATORY: AST DEPENDENCY GRAPH (§0 DEFAULT ANALYSIS MODE)
# Build BEFORE any code investigation or modification
# ============================================================

# Option 1: Use repository-specific dependency graph tools
capture([sys.executable, "tools/dep_graph_db.py", "build", "--roots", "<file1.py>", "<file2.py>"], E)
capture([sys.executable, "tools/dep_graph_db.py", "query", "--downstream", "<file.py>"], E)
capture([sys.executable, "tools/dep_graph_db.py", "query", "--upstream", "<file.py>"], E)

# Option 2: Use AST analysis scripts
capture([sys.executable, "ops_scripts/ci/_ast_process_map_gap_analyzer.py"], E)

# REQUIRED: Document DEPENDENCY_GRAPH section with:
# - Graph roots
# - Upstream dependencies
# - Downstream dependents
# - Test coverage edges
# - Cross-layer edges
# - Cycle/boundary findings

# ============================================================
# PREFLIGHT
# ============================================================
capture(["git", "branch", "--show-current"], E)
capture(["git", "status", "--porcelain"], E)
capture(["git", "diff", "--name-only", "HEAD"], E)

# ============================================================
# SAFE PYTHON INVOCATION PATTERNS
# Use ONLY these patterns. Do NOT create runner scripts.
# ============================================================

# Pattern 1: Direct file invocation (preferred when __main__ exists)
capture([sys.executable, "path/to/existing_file.py"], E)

# Pattern 2: Module invocation (when -m is the sanctioned entrypoint)
capture([sys.executable, "-m", "existing.module.path"], E)

# FORBIDDEN: Do NOT create new runner scripts or wrapper files.

# ============================================================
# PYTEST — COLLECTION + EXECUTION (always capture both)
# PREREQUISITE: Identify tests via dependency graph (§5.2)
# ============================================================

# STEP 1: Use dependency graph to identify required tests
# (Graph must show test → production coverage edges)

# STEP 2: Collect first, then execute — verify counts match (§1.12)
capture([sys.executable, "-m", "pytest", "--collect-only", "-q", "--color=no"], E)
capture([sys.executable, "-m", "pytest", "-xvv", "--color=no"], E)
# Record: collected count vs executed count. STOP if mismatch unexplained.

# Scoped test run — MUST be justified by dependency graph
capture([sys.executable, "-m", "pytest", "-xvv", "--color=no", "<scoped_test_ids>"], E)

# STEP 3: Verify test coverage matches dependency graph
# Compare: tests identified by graph vs tests actually run
# Any mismatch = coverage gap or graph incompleteness

# ============================================================
# PRE-COMMIT
# ============================================================
capture([sys.executable, "-m", "pre_commit", "run", "--all-files"], E)

# ============================================================
# SCOPE VERIFICATION
# ============================================================
capture(["git", "diff", "--name-only", "HEAD"], E)
capture(["git", "diff", "--name-status", "HEAD"], E)

# ============================================================
# POST-COMMIT VERIFICATION
# ============================================================
capture(["git", "status", "--porcelain"], E)
capture(["git", "show", "--name-only", "HEAD"], E)
capture(["git", "show", "--stat", "HEAD"], E)
