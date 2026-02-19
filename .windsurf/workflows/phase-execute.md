---
description: Execute a single phase with evidence bundling, scope gating, and integrity verification
---

# Phase Execute Workflow

Enforces single-phase stop discipline. References skills — does not duplicate them.

---

## Wave 1: Lock

1. Set evidence file path:
   ```powershell
   $E = "docs/reports/plans/<phase_name>_evidence.md"
   ```

2. Run preflight (capture to evidence):
   ```powershell
   git branch --show-current 2>&1 | Tee-Object -FilePath $E -Append
   git status --porcelain 2>&1 | Tee-Object -FilePath $E -Append
   git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
   ```

3. Declare scope in evidence — exact file list + N count.
   See skill: `scope-guard/scope_precheck.md`

4. Confirm guardrails:
   - No runner scripts will be added.
   - No changes to `.windsurfrules`.
   - No changes to tooling configs.

5. STOP if working tree has staged files outside declared scope.

---

## Wave 2: Change

1. Execute only this phase's declared steps. No future steps.

2. For any Python invocation, follow:
   See skill: `script-sprawl-guard/entrypoint_decision_tree.md`

3. Capture all command outputs:
   See skill: `evidence-bundle/command_capture_snippets.ps1`

4. After each file modification, check scope has not expanded:
   ```powershell
   git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
   ```
   If unexpected files appear → run `scope-decontaminate` workflow. STOP.

---

## Wave 3: Verify

1. Run pytest integrity check when tests are in scope:
   See skill: `pytest-integrity/collection_vs_execution_protocol.md`

2. Run pre-commit:
   ```powershell
   pre-commit run --all-files 2>&1 | Tee-Object -FilePath $E -Append
   ```

3. Final scope audit before commit:
   Run `scope-audit` workflow.

4. Commit only scoped files + evidence file:
   ```powershell
   git add <declared_files> $E
   git commit -m "<phase description>"
   ```

5. Run post-commit verification:
   See skill: `evidence-bundle/post_commit_verification_block.md`

6. STOP. Do not begin next phase.

---

## Phase End Output (ONLY)

- Evidence file path
- Commit hash
- `git show --stat` output
- STOP
