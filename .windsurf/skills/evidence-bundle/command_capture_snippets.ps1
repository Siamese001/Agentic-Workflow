# ============================================================
# CANONICAL COMMAND CAPTURE SNIPPETS
# Usage: copy-paste into your phase execution session.
# All outputs MUST be captured via Tee-Object 2>&1.
# ============================================================

# --- SETUP: Define evidence file path ONCE at session start ---
$E = ".windsurf/plans/<phase_evidence_file>.md"

# ============================================================
# MANDATORY: AST DEPENDENCY GRAPH (§0 DEFAULT ANALYSIS MODE)
# Build BEFORE any code investigation or modification
# ============================================================

# Option 1: Use repository-specific dependency graph tools
python tools/dep_graph_db.py build --roots <file1.py> <file2.py> 2>&1 | Tee-Object -FilePath $E -Append
python tools/dep_graph_db.py query --downstream <file.py> 2>&1 | Tee-Object -FilePath $E -Append
python tools/dep_graph_db.py query --upstream <file.py> 2>&1 | Tee-Object -FilePath $E -Append

# Option 2: Use AST analysis scripts
python ops_scripts/ci/_ast_process_map_gap_analyzer.py 2>&1 | Tee-Object -FilePath $E -Append

# Option 3: Build custom AST graph for specific files
python -c "
import ast
import sys
from pathlib import Path

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read(), filename=filepath)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    print(f'File: {filepath}')
    print(f'Imports: {imports}')
    return imports

analyze_file(sys.argv[1])
" <file.py> 2>&1 | Tee-Object -FilePath $E -Append

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
git branch --show-current 2>&1 | Tee-Object -FilePath $E -Append
git status --porcelain 2>&1 | Tee-Object -FilePath $E -Append
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append

# ============================================================
# SAFE PYTHON INVOCATION PATTERNS
# Use ONLY these patterns. Do NOT create runner scripts.
# ============================================================

# Pattern 1: Direct file invocation (preferred when __main__ exists)
python path/to/existing_file.py [args] 2>&1 | Tee-Object -FilePath $E -Append

# Pattern 2: Module invocation (use when direct invocation is blocked
#            or when the module specifies -m as its sanctioned entrypoint)
python -m existing.module.path [args] 2>&1 | Tee-Object -FilePath $E -Append

# FORBIDDEN: Do NOT do any of the following:
#   python run_something.py          <- new runner script
#   python tmp_invoke.py             <- temporary wrapper
#   python scripts/launch_agent.py  <- wrapper that calls another file

# ============================================================
# PYTEST — COLLECTION + EXECUTION (always capture both)
# PREREQUISITE: Identify tests via dependency graph (§5.2)
# ============================================================

# STEP 1: Use dependency graph to identify required tests
# (Graph should show test → production coverage edges)

# STEP 2: Run pytest with collection verification
pytest --collect-only -q 2>&1 | Tee-Object -FilePath $E -Append
pytest -xvv 2>&1 | Tee-Object -FilePath $E -Append
# Record: collected count vs executed count. STOP if mismatch unexplained.

# Scoped test run (only when phase acceptance criteria explicitly narrows scope):
# MUST be justified by dependency graph showing these are the only affected tests
pytest -xvv tests/governance/ 2>&1 | Tee-Object -FilePath $E -Append

# STEP 3: Verify test coverage matches dependency graph
# Compare: tests identified by graph vs tests actually run
# Any mismatch = coverage gap or graph incompleteness

# ============================================================
# PRE-COMMIT
# ============================================================
pre-commit run --all-files 2>&1 | Tee-Object -FilePath $E -Append

# ============================================================
# SCOPE VERIFICATION
# ============================================================
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git diff --name-status HEAD 2>&1 | Tee-Object -FilePath $E -Append

# ============================================================
# POST-COMMIT VERIFICATION
# ============================================================
git status --porcelain 2>&1 | Tee-Object -FilePath $E -Append
git show --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git show --stat HEAD 2>&1 | Tee-Object -FilePath $E -Append
