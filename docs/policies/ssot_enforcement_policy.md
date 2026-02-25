# SSOT Enforcement Policy

**Scope:** `agentic_core/L5_safety/config/structure_blueprint/` package + `structure_blueprint_config.py` shim
**Scan roots:** `agentic_core`, `apps_lic`, `apps_rg`, `apps_shared`, `artifacts`, `ops_scripts`, `tests`
**Enforced by:** `python -m agentic_core.L5_safety.config.structure_blueprint._verify`
**CI:** `.github/workflows/ssot_verify.yml`

---

## What is SSOT

The **Single Source of Truth** (SSOT) for project structure is the `structure_blueprint` package. It defines:

- `SOVEREIGN_TERRITORIES` — the canonical territory mapping (13 top-level directories)
- `ROOT_WHITELIST` — the set of allowed root directory names
- All derived registries, classification rules, and governance constants

Every structural decision in the codebase must trace back to this package.

---

## Immutable Structure Guarantees

| Object | Type | Guarantee |
| --- | --- | --- |
| `ROOT_WHITELIST` | `frozenset` | Cannot be mutated at runtime |
| `SOVEREIGN_TERRITORIES` | `MappingProxyType` (deep) | All nested dicts → `MappingProxyType`, lists → `tuple`, sets → `frozenset` |

The verifier runs `_assert_frozen()` — a full recursive walk that fails on the first mutable container found at any depth, printing the exact path to the violation.

Mutation attempts raise `TypeError` at runtime.

---

## Phantom Baseline Contract

Phantom imports are references to names that do not exist in the package (e.g., `SOVEREIGN_REGISTRY`, `SCRIPTS_DIR`). They are pre-existing baseline noise tracked in:

    docs/reports/plans/phantom_baseline.json

### Phantom Baseline Rules

| Condition | Result |
| --- | --- |
| `phantom_baseline.json` missing, no flag | **FAIL** |
| `phantom_baseline.json` missing, `--init-phantom-baseline` | Creates baseline, PASS |
| `phantom_baseline.json` corrupt, no flag | **FAIL** |
| `phantom_baseline.json` corrupt, `--repair-phantom-baseline` | Rewrites from scan, exits 0 immediately |
| Current phantoms == saved baseline | **PASS** (LOCKED) |
| Current phantoms < saved baseline (improvement), no flag | PASS with diff printed, not persisted |
| Current phantoms < saved, `--update-phantom-baseline` | Diff printed, baseline updated, PASS |
| Current phantoms > saved (count increased) | **FAIL** (no override, `--update-phantom-baseline` refused) |

Phantom increases are **NEVER** allowed. No flag overrides this. Fix the import or remove the reference.

### Phantom Diff Inspection

Use `--print-phantom-diff` to see the exact diff between the current scan and the saved baseline, then exit. Returns exit code 0 if no diff, 1 if any diff exists.

---

## Import Allowlist Contract

The `_constants.py` module may only import from the following stdlib modules:

    ALLOWED_MODULES = {__future__, collections, dataclasses, functools, itertools, types, typing}

### Allowlist Enforcement Rules

- Any `import` or `from X import` where `X` is not in the allowlist → **FAIL**
- Relative imports → **FAIL**
- Dynamic imports (`__import__`, `importlib.import_module`) → **FAIL**
- Forbidden calls (`os.getenv`, `open`, `Path.cwd`, `time.*`, `random.*`, etc.) → **FAIL**

### Allowlist Hash Lock

The allowlist is hashed (SHA-256, first 16 chars) and persisted to:

    docs/reports/plans/allowlist_hash.txt

| Condition | Result |
| --- | --- |
| Hash matches saved | **PASS** (LOCKED) |
| Hash changed, no flag | **FAIL** (prints old hash, new hash, and full current allowlist) |
| Hash changed, `--acknowledge-import-change` | Hash updated, exits 0 immediately (no other sections run) |

`--print-allowlist` outputs the current allowlist and hash deterministically, then exits. It is **pure read-only** — it does not read or write any lock files.

`--acknowledge-import-change` is a **maintenance mode** — it updates the hash file and exits immediately without running any other verification sections. It never touches `phantom_baseline.json`. **Safety constraint:** ack is refused if `phantom_baseline.json` is missing or corrupt, preventing it from masking other failures.

---

## Shim Structural Contract

The `structure_blueprint_config.py` shim must contain **only**:

- `Import` / `ImportFrom` statements
- Exactly one `Assign` to `__all__`
- A module docstring (`Expr` with `Constant`)

### Forbidden at top level

- `FunctionDef` / `AsyncFunctionDef`
- `ClassDef`
- `Call` expressions
- Control flow (`If`, `For`, `While`, `Try`, `With`)
- Any assignment other than `__all__`

Any violation → **FAIL**.

---

## How to Modify Baseline Safely

### Reducing phantom imports (fixing references)

1. Fix the import in the consuming file
2. Run: `python -m agentic_core.L5_safety.config.structure_blueprint._verify`
3. Observe diff output showing removed phantoms
4. Run: `python -m agentic_core.L5_safety.config.structure_blueprint._verify --update-phantom-baseline`
5. Commit the updated `phantom_baseline.json`

### Adding a new allowed import module

1. Add the module to `ALLOWED_MODULES` in `_verify.py`
2. Run verifier — it will print hash mismatch with old/new allowlist diff
3. Run: `python -m agentic_core.L5_safety.config.structure_blueprint._verify --acknowledge-import-change`
4. Commit both `_verify.py` and `docs/reports/plans/allowlist_hash.txt`

### First-time baseline creation

Only needed once per repository clone if `phantom_baseline.json` is missing:

    python -m agentic_core.L5_safety.config.structure_blueprint._verify --init-phantom-baseline

### Recovering from a corrupt baseline

If `phantom_baseline.json` becomes unparseable (JSON parse error, wrong schema, absolute paths, backslashes, or `..` segments):

    python -m agentic_core.L5_safety.config.structure_blueprint._verify --repair-phantom-baseline

`--repair-phantom-baseline` **refuses** if the baseline is valid JSON with correct schema. Use `--update-phantom-baseline` for baseline drift instead.

---

## Lock Files

| File | Purpose |
| --- | --- |
| `docs/reports/plans/phantom_baseline.json` | Frozen set of known phantom import references (repo-relative, forward-slash, no `..`, no absolute) |
| `docs/reports/plans/allowlist_hash.txt` | SHA-256 hash of `ALLOWED_MODULES` |

Both files must be committed to the repository. CI verifies their presence before running the verifier.

---

## All Flags

| Flag | Purpose |
| --- | --- |
| `--init-phantom-baseline` | Create `phantom_baseline.json` (first time only, file must not exist) |
| `--update-phantom-baseline` | Persist a reduced phantom baseline (refused if count increases) |
| `--print-phantom-diff` | Print phantom diff vs baseline and exit (exit 0 = no diff, 1 = diff) |
| `--repair-phantom-baseline` | Rewrite corrupt/unreadable baseline from current scan (refuses if valid) |
| `--acknowledge-import-change` | Update allowlist hash and exit immediately (refused if baseline is missing/corrupt) |
| `--print-allowlist` | Print current allowlist + hash and exit (pure read-only, no lock file I/O) |

No flag silently modifies any locked artifact. Phantom increases are never accepted.

---

## CI Behavior

The `.github/workflows/ssot_verify.yml` workflow:

- **Triggers on:** pull requests touching `structure_blueprint/`, `structure_blueprint_config.py`, `phantom_baseline.json`, `allowlist_hash.txt`, or `ssot_enforcement_policy.md`
- **Python version:** 3.11
- **Pre-check:** Verifies `phantom_baseline.json` and `allowlist_hash.txt` exist before running
- **Install:** Stdlib-only by default; only installs from `requirements-ssot-verify.txt` if it exists
- **Runs:** `python -m agentic_core.L5_safety.config.structure_blueprint._verify`
- **Fails the build** if any invariant fails

CI runs without override flags. A **guard step** (stdlib-only Python script using `re`) extracts all `run:` blocks, filters to those containing `_verify`, and asserts:
1. **At least one** verifier invocation exists (prevents silent misconfiguration)
2. **None** contain forbidden maintenance flags (`--init-phantom-baseline`, `--update-phantom-baseline`, `--repair-phantom-baseline`, `--acknowledge-import-change`)

The guard does not self-match against its own flag list. Any change that would require a flag must be committed with the updated lock file in the same PR.

---

## Verification Sections

| # | Section | What it checks |
| --- | --- | --- |
| 1 | Import Cycle Detection | Zero cycles in package dependency graph |
| 2 | API Surface | 163/163 exact match between package and shim `__all__` |
| 3 | Deep Immutability + Identity | `_assert_frozen()` recursive walk, `frozenset`, `MappingProxyType`, identity |
| 4 | Backward Compatibility | 18 excluded names importable, 0 leaked into `__all__` |
| 5 | Import Linter + Phantom Baseline | 0 policy violations (incl. SyntaxError = hard FAIL), phantom baseline locked, BASELINE_ONLY/CURRENT_ONLY diff enforced |
| 6 | Shim Structural Hard Lock | No forbidden AST nodes in shim |
| 7 | Stdlib Allowlist | Hash-locked import allowlist for `_constants.py` |
| 8 | Compat Name Consumer Report | Who imports the 18 internal names |
| 9 | Phantom Debt Register | Generates `docs/reports/plans/phantom_debt.md` (deterministic, no timestamps) |

---

## Scan Scope Contract

The verifier scans a **bounded, deterministic** file set:

- **SCAN_ROOTS:** `agentic_core`, `apps_lic`, `apps_rg`, `apps_shared`, `artifacts`, `ops_scripts`, `tests`
- **SCAN_EXTENSIONS:** `.py`
- **SCAN_EXCLUDES:** `.venv`, `venv`, `__pycache__`, `.git`, `dist`, `build`, `.pytest_cache`, `node_modules`

No heuristic string-contains filtering is used. All `.py` files under scan roots are parsed; SyntaxErrors in any scanned file are a hard FAIL.

### SCAN_ROOTS Governance Lock

- Every `SCAN_ROOT` directory **must exist** at verification time. Missing roots cause a hard FAIL.
- Every phantom baseline path must start with one of `SCAN_ROOTS`. Out-of-scope paths cause a CORRUPT baseline error.
- `SCAN_ROOTS` changes require an explicit code change in `_verify.py` — there is no auto-expansion.

---

## Simulation Harness

Run: `python -m agentic_core.L5_safety.config.structure_blueprint._simulate_verify`

Executes automated A–F style simulations using **temp copies** of lock files. Never edits committed files in-place.

**Enforced clean state:** After all simulations, the harness verifies **byte-equal restoration** of `phantom_baseline.json`, `allowlist_hash.txt`, and `phantom_debt.md`. It also runs `git diff --exit-code` on lock files when git is available. Any byte difference causes a FAIL.

---

## Phantom Debt Register

- **Path:** `docs/reports/plans/phantom_debt.md`
- **Source:** Derived from `PHANTOM_CURRENT_SET` (deduplicated current scan), keyed by `(path, name)`
- **Lifecycle:** Generated on every verifier run. It is a **generated artifact**, not a committed lock file. CI does not fail due to uncommitted changes to this file.
- **Count invariants (normal run):**
  - `debt_rows == current_count` (enforced by assertion)
  - `current_count == baseline_count` (printed, enforced by BASELINE_ONLY/CURRENT_ONLY diff)
- **Deterministic:** Sorted by `(path, name)`, no timestamps

---

## Canonical Path Normalization

All repo-relative paths are normalized via `_canonical_repo_path()`:
- Backslashes → forward slashes
- `.` segments collapsed
- `..` segments → **ValueError** (rejected)
- Absolute paths → **ValueError** (rejected)
- Used for: baseline validation, phantom set generation, SCAN_ROOT containment, debt report

---

## Baseline/Current Diff Enforcement

When baseline and current phantom sets differ:
- **Baseline-only entries** (stale baseline): printed with `-` prefix
- **Current-only entries** (new phantoms): printed with `+` prefix
- Any diff → **FAIL** (unless only baseline-only and `--update-phantom-baseline` provided)
