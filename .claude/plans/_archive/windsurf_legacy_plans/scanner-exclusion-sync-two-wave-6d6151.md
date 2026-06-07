# Scanner Exclusion Synchronization — Two-Wave SVP Plan

A Two-Wave approach that closes immediate exclusion gaps in Wave 1, then builds YAML-driven synchronization infrastructure in Wave 2 to prevent recurrence.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | W1.1 | Immediate gap closure: add missing entries to SOVEREIGN_EXCLUDED_FOLDERS | 15K | ssot.py exists, constants load correctly | 🟢 READY | coverage_html/.test_artifacts in exclusion list; regression test pass |
| Wave 2 | W2.1-W2.3 | YAML infrastructure: config/excluded_paths.yaml + loader + CI gate | 45K | YAML parsing available, CI system functional | 🟢 READY | YAML drives both .gitignore and scanner constants; CI enforces sync |

**Total: 60K tokens across 2 waves, both GREEN** 🟢

---

## Gap Register

**GAP-1: coverage_html/ excluded from git but not scanner**
- `.gitignore` has `coverage_html/` from pytest-cov
- `SOVEREIGN_EXCLUDED_FOLDERS` only has `htmlcov` (alternate name)
- Risk: Scanner processes coverage reports if they exist locally

**GAP-2: .test_artifacts/ excluded from git but not scanner**
- `.gitignore` has `.test_artifacts/`
- `GLOBAL_EXCLUDED_DIRS` has `test_artifacts` (without leading dot)
- Risk: Hidden test artifact directories scanned unnecessarily

**GAP-3: Divergence will recur without automation**
- New tools add `.gitignore` entries
- Scanner constants manually updated = guaranteed drift
- No CI enforcement of consistency

---

## Execution Plan

### Wave 1 — Immediate Gap Closure (W1.1)
**Scope**: Patch `SOVEREIGN_EXCLUDED_FOLDERS` in ssot.py to add missing entries; archive the manual fix.

**Files touched**:
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py` — add `coverage_html`, `.test_artifacts`
- `tools/archive/exclusion_gaps_manual_fix_2026.md` — document last manual patch per SVP archival discipline

**Commands**:
```bash
# Verify gaps exist
python -c "from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS; print('coverage_html' in SOVEREIGN_EXCLUDED_FOLDERS, '.test_artifacts' in SOVEREIGN_EXCLUDED_FOLDERS)"

# Regression test
python -m pytest tests/unit/agentic_core/adg/test_static_scanner.py -v
python tools/generate_full_adg.py --dry-run  # Verify scanner still functional
```

**Acceptance**:
- [ ] `coverage_html` ∈ `SOVEREIGN_EXCLUDED_FOLDERS`
- [ ] `.test_artifacts` ∈ `SOVEREIGN_EXCLUDED_FOLDERS`  
- [ ] Scanner tests pass (19/19)
- [ ] ADG generation produces valid output
- [ ] Archive document records this manual fix

---

### Wave 2 — YAML Synchronization Infrastructure (W2.1-W2.3)
**Scope**: Build SSOT YAML that drives both .gitignore and scanner constants, with CI enforcement.

#### W2.1 — YAML Schema and Loader
**Files**:
- `config/excluded_paths.yaml` — canonical exclusion list (folders, patterns)
- `agentic_core/L5_safety/config/exclusion_loader.py` — loads YAML into Python constants

**Key design** (SVP simplicity):
```yaml
# config/excluded_paths.yaml
version: "1.0.0"
build_cache_dirs:
  - "__pycache__"
  - ".pytest_cache"
  - "coverage_html"  # Gap-1 fixed
  - ".test_artifacts"  # Gap-2 fixed
version_control_dirs:
  - ".git"
  - ".github"
virtual_env_dirs:
  - ".venv"
  - "venv"
```

Loader converts to frozenset at import time (no runtime file I/O during scan).

#### W2.2 — .gitignore Generation
**Files**:
- `tools/generate_gitignore.py` — generates `.gitignore` from YAML
- `.gitignore` — becomes generated file (header comment: `# Generated from config/excluded_paths.yaml`)

**Command**:
```bash
python tools/generate_gitignore.py --check  # CI mode: fail if out of sync
python tools/generate_gitignore.py --write  # Update .gitignore
```

#### W2.3 — CI Enforcement Gate
**Files**:
- `ops_scripts/ci/exclusion_sync_gate.py` — CI gate
- `.github/workflows/exclusion-sync.yml` — workflow

**Gate logic**:
1. Load YAML
2. Load current `SOVEREIGN_EXCLUDED_FOLDERS` from ssot.py
3. Diff: YAML entries must be ⊆ Python constants
4. Diff: `.gitignore` must contain all YAML entries
5. Fail if divergence detected

---

## Rules

- **SVP Principle**: Wave 1 delivers value immediately; Wave 2 prevents recurrence
- **Zero-regression**: Each wave has isolated test scope; ADG generation validates scanner integrity
- **Archival discipline**: Manual fix documented before automation replaces it
- **Fail-closed**: CI gate blocks commits if YAML ↔ constants drift detected
- **Determinism**: Loader uses YAML mtime + content hash for cache invalidation

---

## Success Criteria

| Wave | Criteria | Verification |
|------|----------|--------------|
| W1.1 | Gaps closed | `python -c "from ssot import SOVEREIGN_EXCLUDED_FOLDERS; assert 'coverage_html' in SOVEREIGN_EXCLUDED_FOLDERS"` |
| W1.1 | No regressions | `pytest tests/unit/agentic_core/adg/test_static_scanner.py -v` passes |
| W2.1 | YAML valid | `python -c "import yaml; yaml.safe_load(open('config/excluded_paths.yaml'))"` |
| W2.1 | Loader works | `from agentic_core.L5_safety.config.exclusion_loader import EXCLUDED_FOLDERS` returns frozenset |
| W2.2 | Gitignore sync | `python tools/generate_gitignore.py --check` passes |
| W2.3 | CI enforcement | PR with divergent constants fails gate |

---

## Implementation Commands

```bash
# Wave 1 — Immediate fix
python ops_scripts/ci/run_contract_gates.py  # Pre-check
git checkout -b fix/scanner-exclusion-gaps
# [edit ssot.py: add coverage_html, .test_artifacts]
python -m pytest tests/unit/agentic_core/adg/ -v
python tools/generate_full_adg.py --dry-run
# [create tools/archive/exclusion_gaps_manual_fix_2026.md]
git commit -m "fix(scanner): add coverage_html, .test_artifacts to SOVEREIGN_EXCLUDED_FOLDERS"

# Wave 2 — YAML infrastructure
git checkout -b feat/yaml-exclusion-sync
# [create config/excluded_paths.yaml]
# [create agentic_core/L5_safety/config/exclusion_loader.py]
# [create tools/generate_gitignore.py]
# [create ops_scripts/ci/exclusion_sync_gate.py]
python tools/generate_gitignore.py --write
python ops_scripts/ci/exclusion_sync_gate.py
pytest tests/ -k "exclusion" -v
git commit -m "feat(scanner): YAML-driven exclusion sync with CI enforcement"
```

---

## Rollback Strategy

**Wave 1 rollback**:
```bash
git revert HEAD  # Single commit revert
python -m pytest tests/unit/agentic_core/adg/ -v  # Verify scanner still works
```

**Wave 2 rollback** (if YAML causes issues):
```bash
git revert --no-commit HEAD~2..HEAD  # Revert all Wave 2 commits
# Restore ssot.py to use hardcoded constants (Wave 1 state preserved)
git checkout HEAD~3 -- agentic_core/L5_safety/config/structure_blueprint/ssot.py
python -m pytest tests/unit/agentic_core/adg/ -v
```

---

## ADR Documentation

Per SVP documentation discipline, create:
- `docs/architecture/adr/026-yaml-exclusion-sync.md` — design decision record
- `docs/architecture/adr/025-scanner-exclusion-gaps.md` — Wave 1 gap closure record

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Exclusion gaps | 0 | `coverage_html`, `.test_artifacts` in SOVEREIGN_EXCLUDED_FOLDERS |
| Scanner test pass rate | 100% | 19/19 tests pass |
| YAML ↔ constants sync | Enforced | CI gate passes on PR |
| .gitignore coverage | 100% | `generate_gitignore.py --check` passes |
| ADG edge count delta | ±1% | Compare pre/post Wave 1 ADG generation |
