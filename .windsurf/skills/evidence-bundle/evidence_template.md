# Phase N / Wave N — [Short Description]

## 1. Phase/Wave Header

- **Phase**: N
- **Wave**: N/total
- **Branch**: `<output of: git branch --show-current>`
- **Objective**: One sentence.

---

## 2. Scope Declaration

Declared files (exact paths, no wildcards):

| # | Path | Intent (add/remove/replace) |
|---|------|-----------------------------|
| 1 | `path/to/file.py` | replace lines 10-20 |

**N (planned file count)**: _

Guardrails confirmed:
- [ ] No runner scripts added anywhere in repo.
- [ ] No changes to `.windsurfrules`.
- [ ] No changes to tooling configs (`.vscode`, `markdownlint`, CI, pre-commit).

---

## 3. DEPENDENCY_GRAPH

**MANDATORY per §3.4, §3.7, §4.4**

### Graph Roots
```
- path/to/file1.py
- path/to/file2.py
```

### Node Types Included
```
- module imports
- symbol imports
- class inheritance
- function/method calls
- registry/factory edges
- test coverage edges
```

### Edge Types Analyzed
```
- import edges: <count>
- call edges: <count>
- inheritance edges: <count>
- registry edges: <count>
- test edges: <count>
```

### Impacted Nodes
```
Total impacted nodes: <count>
Direct changes: <list>
Indirect impacts: <list>
```

### Upstream Dependencies
```
file1.py imports:
  - common/utils.py
  - config/settings.py

file2.py imports:
  - file1.py
  - agentic_core/L2_execution/base.py
```

### Downstream Dependents
```
file1.py used by:
  - file2.py (direct import)
  - apps_lic/engines/control_plane.py (indirect via file2.py)
  - tests/test_file1.py (test coverage)

file2.py used by:
  - apps_rg/reasoning/SomeAgent.py (direct import)
  - tests/test_file2.py (test coverage)
```

### Cross-Layer Edges
```
None detected
OR
- file1.py → agentic_core/L2_execution/base.py (L5→L2, VALID per architecture)
```

### Cycle/SCC Findings
```
No cycles detected
OR
- Cycle detected: file1.py → file2.py → file1.py (HARD FAIL per §4.3)
```

### Boundary Violations
```
None detected
OR
- Layer inversion: apps_lic/reasoning/Agent.py → tools/evidence/helper.py (HARD FAIL)
```

### Test Surface Implications
```
Required test files (graph-backed per §5.2):
  - tests/test_file1.py (direct import edge exists)
  - tests/test_file2.py (direct import edge exists)
  - tests/integration/test_control_plane.py (downstream dependent)

Coverage gaps:
  - file1.py::new_function has no test coverage edge → MUST add test
```

### Scope Justification
```
Each changed file MUST be justified by dependency graph:

file1.py:
  - Reason: Direct modification to core logic
  - Graph evidence: Called by file2.py::process_data (call edge)
  - Impact: 3 downstream dependents require regression testing

file2.py:
  - Reason: Refactoring state machine logic
  - Graph evidence: Inherits from common/base.py::BaseStateMachine (inheritance edge)
  - Impact: 2 downstream dependents in apps_rg/

Any file NOT justified by graph = scope contamination per §3.7
```

**FORBIDDEN METHODS (§3.5):**
- ❌ grep/ripgrep for impact analysis
- ❌ filename similarity guessing
- ❌ text search for dependency inference
- ✅ ONLY AST-derived graph edges

**FAIL-CLOSED DISCIPLINE (§3.6):**
If AST parsing fails:
  - [ ] Exact parse errors recorded: <errors>
  - [ ] Blocked files identified: <list>
  - [ ] Conclusions marked as PARTIAL
  - [ ] NO silent fallback to text search

---

## 4. Pre-Change Diff Snapshot

### Command
```powershell
$E = ".windsurf/plans/<this_file>.md"
git diff --name-only HEAD | Tee-Object -FilePath $E -Append
```

### Raw Output
```
<paste verbatim>
```

---

## 5. Commands Executed

All commands captured via:
```powershell
<command> 2>&1 | Tee-Object -FilePath $E -Append
```

List each command in execution order:

```powershell
# Example:
python agentic_core/L5_safety/enforcement/system_enforcer.py 2>&1 | Tee-Object -FilePath $E -Append
python -m agentic_core.L5_safety.enforcement.system_enforcer 2>&1 | Tee-Object -FilePath $E -Append
pytest -xvv tests/governance/ 2>&1 | Tee-Object -FilePath $E -Append
pre-commit run --all-files 2>&1 | Tee-Object -FilePath $E -Append
git diff --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git show --stat 2>&1 | Tee-Object -FilePath $E -Append
```

---

## 6. Raw Outputs (NO TRUNCATION)

### [Command 1 label]
```
<verbatim output — no "..." truncation>
```

### [Command 2 label]
```
<verbatim output — no "..." truncation>
```

Exit codes MUST be visible. Include `$LASTEXITCODE` or `$?` after each command.

---

## 7. Post-Commit Verification Block

See skill: `scope-guard/post_commit_verification_block.md`

### Commands
```powershell
git status --porcelain 2>&1 | Tee-Object -FilePath $E -Append
git show --name-only HEAD 2>&1 | Tee-Object -FilePath $E -Append
git show --stat HEAD 2>&1 | Tee-Object -FilePath $E -Append
```

### Raw Output
```
<verbatim>
```

**Commit hash**: `<hash>`
**Files in commit**: must match declared scope exactly.
**Working tree clean**: YES / NO (if NO — STOP, do not proceed to next phase)

---

## Evidence Authoritative Rules

- Evidence is authoritative. No claims without raw output.
- No "..." truncation within evidence scope.
- Claims like "pre-commit passes" MUST include actual pre-commit output.
- Any mismatch between claimed and actual results → IMMEDIATE FAIL.
