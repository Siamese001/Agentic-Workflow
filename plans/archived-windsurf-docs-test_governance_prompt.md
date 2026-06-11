---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\test_governance_prompt.md'
original_relative_path: 'test_governance_prompt.md'
source_sha256: 9ff7a092e123cae51f2047dcfe3c4189ac3b2447a854133e265288cbb04d44a7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test Structure & MRO Safety — Windsurf Governance Prompt v2.0

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Constitutional Preamble

This prompt governs all Windsurf actions related to test structure enforcement,
import/MRO safety, and scope management. It is the SSOT for test governance
policy. All phases are sequential; no phase may be skipped.

---

## PHASE 0 — SCOPE AUTHORITY LOCK

### Inputs
1. Read `pytest.ini` → extract `testpaths`, `norecursedirs`, `addopts`.
2. Run `git status --porcelain` → identify untracked files.
3. Run `pytest --collect-only -q` → extract collected item count.
4. Run `git ls-files <testpath>` for each configured testpath → extract tracked test files.

### Outputs — `test_scope_snapshot.json`

The snapshot MUST contain **both** measures:

| Field | Source | Description |
|---|---|---|
| `tracked_test_files_in_scope` | `git ls-files` ∩ `testpaths` | List of tracked `test_*.py` files under configured testpaths |
| `tracked_test_files_in_scope_count` | derived | Count of the above |
| `pytest_collected_items_in_scope` | `pytest --collect-only -q` | Number of test items (parametrized cases expand file count) |
| `pytest_collected_item_ids` | `pytest --collect-only -q` | Full list of `file::class::test` IDs |
| `untracked_test_files` | `git status --porcelain` | Any `??` entries under `tests/` |
| `integrity_hash` | SHA-256 of tracked file list | Drift detection |

### Hard Rules

- **Never report "N in-scope files" if `pytest -q` says "M collected"** — those are
  different measures. Always report both: file count and collected-item count.
- `scoped_testpaths` is authoritative. Only files under these paths are "in-scope for CI".
- Untracked test files (`??` in `git status`) are **out-of-scope by default**.

### Snapshot Artifact Policy

| Flag | Default | Effect |
|---|---|---|
| `COMMIT_SCOPE_SNAPSHOTS` | `false` | Snapshot is ephemeral evidence |

- **Default (`false`)**: write snapshot to `docs/reports/plans/_artifacts/test_scope_snapshot.json`.
  This path is in `.gitignore`. No commit required.
- **If `true`**: write to `tests/_contracts/test_scope_snapshot.json` and commit.
  Only enable if the repo explicitly mandates versioned scope tracking.

### Acceptance Criteria
- [ ] `pytest.ini` testpaths extracted and recorded.
- [ ] Both `tracked_test_files_in_scope_count` and `pytest_collected_items_in_scope` present.
- [ ] `untracked_test_files` enumerated (may be empty).
- [ ] Snapshot written to the correct path per `COMMIT_SCOPE_SNAPSHOTS` policy.
- [ ] `git status` is clean (no forced commits from snapshot generation).

---

## PHASE 1 — TEST SCOPE EXPANSION RULE

### Rule
- `pytest.ini testpaths` defines the authoritative CI scope.
- Tests outside `testpaths` are **not collected** and **not required**.
- Widening `testpaths` requires:
  1. All new tests are tracked (`git ls-files`).
  2. All new tests pass (`pytest -q`).
  3. Explicit approval (not automatic).

### Hard Rules
- Never treat untracked generated tests as obligations.
- Never widen `testpaths` silently.
- Never add directories to `testpaths` that contain failing tests.

### Acceptance Criteria
- [ ] `testpaths` unchanged from committed state (or explicitly approved expansion).
- [ ] Zero untracked test files treated as required coverage.

---

## PHASE 2 — MIRROR STRUCTURE CONTRACT

### Scope Classification

The mirror contract test lives at `tests/_contracts/test_structure_mirror_contract.py`.
This path is **outside** `pytest.ini testpaths`.

### Standalone Audit Mode

When `tests/_contracts/**` is outside `pytest.ini testpaths`:

1. It **may** be executed as a standalone audit:
   ```
   pytest -q tests/_contracts/test_structure_mirror_contract.py -vv
   ```
2. Failures MUST be reported with the scope banner:
   ```
   SCOPE: OUT-OF-CI (pytest.ini excludes tests/_contracts)
   ```
3. Failures in standalone audits are **"audit failures"**, NOT **"suite failures"**.
4. Never conflate audit results with CI suite results.

### Legacy Root Policy

| Policy | Description |
|---|---|
| `STRICT` | No non-canonical test roots allowed anywhere under `tests/`. Requires full repo cleanup. |
| `BASELINE-AWARE` **(default)** | Allow configured legacy roots with a freeze rule: file count must not increase beyond recorded baseline. |

**Default: `BASELINE-AWARE`**

Legacy roots and their frozen baselines are configured in
`test_no_tests_in_non_canonical_locations()` inside the mirror contract test.
The freeze rule prevents growth: if `tests/core/` had 15 files at policy adoption,
it may never exceed 15. Any increase is a hard failure.

To switch to `STRICT`: set `LEGACY_ROOT_POLICY = "STRICT"` in the test function.
This will fail on ALL non-canonical roots, requiring full cleanup before passing.

### Acceptance Criteria
- [ ] Mirror contract runs standalone (3/3 pass) OR failures reported with `SCOPE: OUT-OF-CI` banner.
- [ ] Legacy root policy is explicitly set (`BASELINE-AWARE` or `STRICT`).
- [ ] No legacy root exceeds its frozen baseline count.

---

## PHASE 3 — IMPORT/MRO SAFETY GATE (CRITICAL LIST + PREFLIGHT)

### Requirements

The guard gate must be:
1. **Committed** (tracked by git)
2. **Under scoped testpaths** (`tests/integration/agentic_core/`)
3. **Driven by a tracked Critical Module List** (not hardcoded inline)
4. **Preflighted** (compile + import) before counting any remediation progress
5. **Asserting** no MRO TypeError + no redundant SubatomicTestingMixin direct base for **all** allowlisted modules

### Guard Test Location

```
tests/integration/agentic_core/test_imports_no_mro_error.py
```

### MANDATORY ARTIFACT — Critical Module List

- File (tracked): `tests/integration/agentic_core/critical_modules.txt`
- Format:
  - One dotted module path per line
  - Comments allowed with `#`
  - Optional explicit exclusions with reason:
    - `# EXCLUDE <dotted.path> :: <reason>`
- Rule: The guard test MUST read from this file. Inline allowlists are forbidden.

### MANDATORY PREFLIGHT — Compile + Import Gate

Before claiming "progress" from any structural remediation or mirror generation, run:
  - `python -m compileall agentic_core apps_*`
  - `pytest -q -k "imports_no_mro_error" -vv`
- Failure in either gate is a hard stop (no mirrored coverage claims allowed).

### Guard Test Acceptance

- Must pass for ALL modules listed in `critical_modules.txt`
- Must fail if a listed module import raises (ImportError/ModuleNotFoundError/MRO TypeError)
- Must assert redundant-base anti-pattern is absent for ALL listed modules:
  - If `SubatomicTestingMixin` is in `cls.__mro__` via base, it must not appear in `cls.__bases__`

### Acceptance Criteria

- [ ] Guard test file is tracked (`git ls-files` returns it).
- [ ] Guard test is under a configured testpath.
- [ ] `critical_modules.txt` is tracked and non-empty.
- [ ] Guard test loads the list and asserts on every entry.
- [ ] All parametrized cases pass (`pytest -q -k "imports_no_mro_error" -vv`).
- [ ] Redundant-base assertion covers ALL allowlisted agents (not only L6).
- [ ] Modules excluded from the list have documented justification.

---

## PHASE 4 — SOURCE FIX RULE (NO BYPASS)

### Forbidden Patterns
Any of the following in the diff of modified source files constitutes a **HARD FAIL**:

| Pattern | Description |
|---|---|
| `# import ...` (commented-out import) | Hiding a dependency to make tests pass |
| `Any` replacing a real type | Placeholder type to avoid import |
| `# type: ignore` (newly added) | Suppressing type errors instead of fixing |
| `pass` as sole function body (newly added) | Stub replacing real logic |
| `noqa` (newly added) | Suppressing linter instead of fixing |
| Subtree added to `norecursedirs` | Hiding failing tests from discovery |

### Verification
```bash
git diff HEAD~1 -- agentic_core/ | grep "^+" | grep -E "# type: ignore|pass\s*$|placeholder|FIXME|HACK|bypass|noqa"
```
Must return empty for new additions.

### Acceptance Criteria
- [ ] Zero bypass patterns in the diff of modified source files.
- [ ] All fixes are minimal upstream corrections (added imports, fixed paths, removed redundant bases).

---

## PHASE 5 — FINAL VERIFICATION

### Required Evidence

#### 1. Suite Green (configured scope)
```bash
pytest -q
```
Claim: **"Suite green"** requires raw stdout showing `N passed` with exit code 0.

#### 2. Guard Green (MRO safety)
```bash
pytest -q -k "imports_no_mro_error" -vv
```
Claim: **"Guard green"** requires raw stdout showing all parametrized cases passed.

#### 3. Audit Green (standalone, if applicable)
```bash
pytest -q tests/_contracts/test_structure_mirror_contract.py -vv
```
Claim: **"Audit green"** requires raw stdout with `SCOPE: OUT-OF-CI` banner.
Audit failures do NOT block the "Suite green" claim.

#### 4. Git Status Clean
```bash
git status --porcelain
```
Must return empty (no untracked files, no uncommitted changes).
Exception: if `COMMIT_SCOPE_SNAPSHOTS = false`, the snapshot artifact is gitignored
and will not appear in `git status`.

### Reporting Rule

| Claim | Requires | Source |
|---|---|---|
| "Suite green" | `pytest -q` exit 0 under configured `testpaths` | CI scope |
| "Audit green" | `pytest -q <audit_path>` exit 0 | Standalone audit |
| "Guard green" | `pytest -q -k "imports_no_mro_error"` exit 0 | CI scope subset |

**Never conflate "Suite green" with "Audit green".** They are independent claims
with independent evidence. A failing audit does not make the suite red.
A green suite does not make the audit green.

### Acceptance Criteria
- [ ] `pytest -q` → all passed, exit 0.
- [ ] Guard test → all passed.
- [ ] `git status --porcelain` → empty.
- [ ] If audit run: failures reported with `SCOPE: OUT-OF-CI` banner, not as suite failures.

---

## INVARIANTS (ALWAYS ENFORCED)

1. `pytest.ini testpaths` is the sole authority for CI scope.
2. "In-scope count" always means BOTH tracked-file count AND pytest-collected-item count.
3. Snapshot artifacts are ephemeral by default (`COMMIT_SCOPE_SNAPSHOTS = false`).
4. Contract tests outside `testpaths` are audits, not CI gates.
5. Legacy roots are frozen at their baseline count (`BASELINE-AWARE` policy).
6. No bypass fixes: no commented imports, no placeholder types, no `noqa` additions.
7. "Green" claims require raw stdout evidence and must specify scope (CI vs audit).
8. Guard test allowlist MUST be externalized to a tracked `critical_modules.txt` file.
9. Redundant-base anti-pattern assertion MUST cover ALL allowlisted agents, not only L6.
10. Import preflight gate MUST verify `compile + import` succeeds before claiming remediation progress.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

