# /windsurf_rules/04_testing_autorepair.md
## Testing Standards, Continuous Re-Run, Auto-Repair Loop (Condensed)

### 1. Testing Requirements
- Must pass: imports, pytest, ruff, mypy.
- No regressions allowed in RAG, drafting, QA, safety, HYDE, ExecutionContext.
- Each agent requires: functional, schema, edge-case, determinism, failure-mode, and no-op detection tests.

### 2. Zero-Failure Mandate
- Partial passes count as failures.
- No skips, xfail, or placeholders unless explicitly approved.
- All tests MUST pass 100% before any command may complete.

### 3. Continuous Auto-Retry Loop
- After any failure, the ENTIRE test suite must automatically re-run.
- Windsurf must apply corrective patches between runs.
- The test loop must continue indefinitely until all tests pass.
- Windsurf must not stop, pause, or return control until the suite is fully green.

### 4. Mandatory Console Review
- Windsurf must parse the full test console after each run.
- Must extract all failing tests, error types, tracebacks, file paths, and failure summaries.
- Auto-repair logic must use parsed diagnostics.

### 5. Pycache Clearance (Mandatory)
- Before EVERY test run (initial or re-run), Windsurf MUST:
  - Delete all `__pycache__/` directories.
  - Delete all `.pyc` files across the entire repository.
- No test cycle may begin until repository is free of bytecode caches.
- Ensures deterministic imports and prevents stale-module behavior.

### 6. Deterministic Completion Gate
- Only acceptable terminal condition:
  - 0 failures  
  - 0 errors  
  - 0 warnings (unless permitted)  
  - 0 skipped (unless sanctioned)
