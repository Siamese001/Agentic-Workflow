# ============================================================
# CANONICAL COMMAND CAPTURE SNIPPETS
# Usage: copy-paste into your phase execution session.
# All outputs MUST be captured via Tee-Object 2>&1.
# ============================================================

# --- SETUP: Define evidence file path ONCE at session start ---
$E = "docs/reports/plans/<phase_evidence_file>.md"

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
# ============================================================
pytest --collect-only -q 2>&1 | Tee-Object -FilePath $E -Append
pytest -xvv 2>&1 | Tee-Object -FilePath $E -Append
# Record: collected count vs executed count. STOP if mismatch unexplained.

# Scoped test run (only when phase acceptance criteria explicitly narrows scope):
pytest -xvv tests/governance/ 2>&1 | Tee-Object -FilePath $E -Append

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
