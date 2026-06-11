---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\lcd-migration-remediation-6997c4.md'
original_relative_path: 'lcd-migration-remediation-6997c4.md'
source_sha256: 24a45a30a90b945c57a609416e9029f3488a0b14c27f94ef6f812a5c123a216c
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-17'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LCD+ Migration Failure Remediation Plan

Remediate the 8 systemic root causes identified in `RCA_LCD_MIGRATION_FAILURES_2026-02-07.md` by hardening `FileClassificationAgent`, `structure_blueprint_config`, and adding pre-commit enforcement.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Phase 1 (P0): Compound Suffix Pre-Validation Gate

**Goal:** Prevent files with multiple architectural suffixes (`*_types_config.py`, `*_validator_util.py`, etc.) from passing classification.

### Step 1.1 — Add `FORBIDDEN_COMPOUND_PATTERNS` to `structure_blueprint_config.py`
- **File:** `agentic_core/L5_safety/config/structure_blueprint_config.py` (~line 2190, after `FORBIDDEN_FILENAME_PATTERNS`)
- Add a new `Final` constant:
  ```python
  KNOWN_ARCHITECTURAL_SUFFIXES: Final[Sequence[str]] = [
      "_types", "_config", "_validator", "_script", "_util", "_mixin",
      "_protocol", "_strategy", "_adapter", "_factory", "_orchestrator",
      "_engine", "_gateway", "_sensor",
  ]

  FORBIDDEN_COMPOUND_PATTERNS: Final[Sequence[str]] = [
      r".*_types_config\.py$",
      r".*_validator_util\.py$",
      r".*_types_validator\.py$",
      r".*_config_util\.py$",
      r".*_validator_script\.py$",
      r".*_config_script\.py$",
  ]
  ```

### Step 1.2 — Add `validate_single_suffix()` to `FileClassificationAgent`
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- Add a new method that checks a filename against `KNOWN_ARCHITECTURAL_SUFFIXES` and raises/logs if >1 suffix is found.
- Call it at the top of `_orchestrate_audit()` loop (before `classify_file()`), right after the `path.exists()` check (~line 322).
- If a compound suffix is detected, log a `[COMPOUND_SUFFIX]` warning and attempt auto-rename by keeping only the **primary** suffix (determined by content scoring from Phase 2, or by rightmost suffix as interim).

### Step 1.3 — Add `SUFFIX_TO_FOLDER` mapping to `structure_blueprint_config.py`
- Explicit canonical mapping from suffix to LCD folder:
  ```python
  SUFFIX_TO_FOLDER: Final[Mapping[str, str]] = {
      "_config.py": "config",
      "_types.py": "types",
      "_validator.py": "validators",
      "_script.py": "enforcement",  # L0: scripts/
      "_util.py": "utils",
      "_mixin.py": "GLOBAL_MIXINS",  # agentic_core/mixins/
      "Agent.py": "reasoning",
  }
  ```
- This makes the suffix-to-folder contract explicit and importable by all agents.

### Step 1.4 — Add `L5_ENFORCEMENT_ALLOWED_SUFFIXES` to blueprint config
- Document L5's intentional domain-specialized suffixes (Category 8 from RCA):
  ```python
  L5_ENFORCEMENT_ALLOWED_SUFFIXES: Final[Sequence[str]] = [
      "_script.py", "_guardrail.py", "_enforcer.py", "_gate.py", "_manager.py",
  ]
  ```
- This codifies that Category 8 is NOT a bug.

---

## Phase 2 (P1): Content-Weighted Classification Scoring

**Goal:** Replace suffix-only classification with AST-based content scoring so a file named `*_config.py` containing only `@dataclass` definitions is correctly classified as TYPES.

### Step 2.1 — Add `_compute_content_scores()` method
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- New private method that walks the AST and returns a `dict[str, int]` of weighted scores:
  - **TYPES:** `+10` per `@dataclass`, `+10` per `BaseModel` subclass, `+10` per `Enum` subclass, `+15` per `Protocol`
  - **CONFIG:** `+5` per `UPPER_CASE` constant assignment, `+3` per settings dict
  - **AGENT:** `+20` per class ending in `Agent` or inheriting from `*Agent`
  - **UTILITY:** `+3` per standalone function (not a method)
  - **VALIDATOR:** `+5` per `validate_`/`check_` function

### Step 2.2 — Add `ClassificationResult` dataclass
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` (near top, after imports)
- Fields: `file_type: str`, `confidence: float`, `signals: list[str]`, `warnings: list[str]`

### Step 2.3 — Add `classify_file_with_confidence()` method
- Wraps `_compute_content_scores()` and returns a `ClassificationResult`.
- If `confidence < 0.6`, adds an ambiguity warning.
- This is a **new method** that does NOT replace `classify_file()` yet — it's additive.

### Step 2.4 — Integrate content scoring as tiebreaker in `classify_file()`
- When suffix-based classification disagrees with content scoring (e.g., filename says CONFIG but content says TYPES), content scoring wins.
- Specifically targets the gap at lines 684-686 where `_detect_config_patterns()` relies on filename indicators — add a content-score override:
  ```python
  # If filename says CONFIG but content is overwhelmingly TYPES, override
  content_scores = self._compute_content_scores(path)
  if content_scores.get('TYPES', 0) > content_scores.get('CONFIG', 0) * 2:
      return "TYPES"
  ```

---

## Phase 3 (P2): Recursive Territory Enforcement

**Goal:** Fix the "layer root only" restriction so files already in wrong subfolders are validated and moved.

### Step 3.1 — Remove depth gate in `enforce_kernel_structure()`
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`, line 266
- Current code:
  ```python
  if file_depth != layer_idx + 1:
      return None
  ```
- Replace with recursive validation that checks **every** file against the correct folder for its type:
  ```python
  # Validate files at ANY depth, not just layer root
  current_subfolder = path.parent.name
  correct_folder = self._get_correct_folder_for_type(filename, layer_root)
  if correct_folder and current_subfolder != correct_folder:
      return layer_root / correct_folder / filename
  ```

### Step 3.2 — Add `_get_correct_folder_for_type()` helper
- Consults `SUFFIX_TO_FOLDER` mapping (from Step 1.3) and falls back to `classify_file()` result.
- Handles L0 `scripts/` nuance (scripts in L0 go to `scripts/`, not `enforcement/`).

### Step 3.3 — Update `check_territory_violation()` core_rules
- **Lines 2357-2371:** Current `core_rules` dict allows AGENT in both `reasoning` AND `enforcement`.
- Tighten to: AGENT -> `{"reasoning"}` only (remove `enforcement` from allowed set).
- The RCA shows 41 agents misplaced in enforcement/validators/memory — this fix prevents recurrence.
- **Exception:** Files already in `enforcement/` that are classified as AGENT remain (enforcement immunity at line 2515 is kept).

---

## Phase 4 (P2): Global Mixin Routing

**Goal:** Ensure ALL mixins route to `agentic_core/mixins/` regardless of current location.

### Step 4.1 — Add hard mixin routing in `enforce_kernel_structure()`
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- Before any layer-specific routing, add:
  ```python
  # GLOBAL OVERRIDE: Mixins always go to agentic_core/mixins/
  if filename.endswith("_mixin.py") or "Mixin" in filename:
      agentic_root = ... # resolve agentic_core path
      target = agentic_root / "mixins" / filename
      if file_path.parent != target.parent:
          return target
      return None
  ```

### Step 4.2 — Update `check_territory_violation()` MIXIN routing
- **Line 2366:** Change `"MIXIN": {"utils", "mixins"}` to `"MIXIN": {"mixins"}` in `core_rules`.
- **Line 177:** Change `app_territory_map` MIXIN from `["utils", "shared", "mixins"]` to `["mixins"]`.
- Add special-case: if mixin is in a layer's `utils/`, flag for move to `agentic_core/mixins/`.

---

## Phase 5 (P1): Folder-Suffix Consistency Enforcement

**Goal:** Files in `types/` must end with `_types.py`; files in `utils/` must end with `_util.py`.

### Step 5.1 — Add `validate_folder_suffix_consistency()` method
- **File:** `agentic_core/L5_safety/reasoning/FileClassificationAgent.py`
- New method that checks:
  - Files in `types/` → must end with `_types.py` or `_protocol.py` or match `I*Protocol.py`
  - Files in `utils/` → must end with `_util.py` or `_mixin.py` or `_helper.py`
  - Files in `config/` → must end with `_config.py` or `_settings.py` or `_blueprint.py`
  - Files in `reasoning/` → must end with `Agent.py` or other reasoning suffixes from blueprint
- Returns a rename suggestion if suffix is wrong.

### Step 5.2 — Call from `_orchestrate_audit()` after territory enforcement
- Insert call after line 394 (after territory move), before `get_compliant_name()`.

---

## Phase 6 (P3): Pre-commit Hook for Compound Suffix Validation

**Goal:** Block commits containing compound-suffix files.

### Step 6.1 — Create pre-commit script
- **File:** `ops_scripts/hooks/check_compound_suffix_script.py`
- Standalone script that:
  1. Scans staged `.py` files
  2. Checks against `KNOWN_ARCHITECTURAL_SUFFIXES` for compound violations
  3. Exits non-zero if any violations found

### Step 6.2 — Register in pre-commit config
- **Note:** `.pre-commit-config.yaml` does not currently exist at project root. Either create it or integrate into existing git hooks infrastructure. Verify with user how hooks are managed.

---

## Testing Strategy

### New Tests Required
| Test File | What It Validates |
|-----------|-------------------|
| `tests/unit/agentic_core/L5_safety/reasoning/test_compound_suffix_validation.py` | `validate_single_suffix()` rejects compound suffixes |
| `tests/unit/agentic_core/L5_safety/reasoning/test_content_scoring.py` | `_compute_content_scores()` correctly weights AST elements |
| `tests/unit/agentic_core/L5_safety/reasoning/test_recursive_territory.py` | `enforce_kernel_structure()` validates files at all depths |
| `tests/unit/agentic_core/L5_safety/reasoning/test_mixin_routing.py` | Mixins always route to `agentic_core/mixins/` |
| `tests/unit/agentic_core/L5_safety/reasoning/test_folder_suffix_consistency.py` | Files in typed folders have correct suffixes |
| `tests/unit/agentic_core/L5_safety/reasoning/test_classification_confidence.py` | Confidence scoring flags ambiguous files |

### Regression Safety
- Run existing `pytest tests/unit/test_location_semantic_lock.py` after each phase
- Run `python -m agentic_core.L0_maintenance.scripts.full_agent_discovery` after Phases 3-4 to update manifest

---

## Files Modified (Summary)

| File | Changes |
|------|---------|
| `agentic_core/L5_safety/config/structure_blueprint_config.py` | Add `KNOWN_ARCHITECTURAL_SUFFIXES`, `FORBIDDEN_COMPOUND_PATTERNS`, `SUFFIX_TO_FOLDER`, `L5_ENFORCEMENT_ALLOWED_SUFFIXES` |
| `agentic_core/L5_safety/reasoning/FileClassificationAgent.py` | Add `validate_single_suffix()`, `_compute_content_scores()`, `ClassificationResult`, `classify_file_with_confidence()`, `validate_folder_suffix_consistency()`, `_get_correct_folder_for_type()`; modify `enforce_kernel_structure()` (remove depth gate), `check_territory_violation()` (tighten MIXIN/AGENT rules), `classify_file()` (add content-score tiebreaker), `_orchestrate_audit()` (add compound-suffix and folder-suffix checks) |
| `ops_scripts/hooks/check_compound_suffix_script.py` | New pre-commit hook script |

---

## Implementation Order

1. **Phase 1** — Compound suffix gate (low risk, high value, blocks new violations)
2. **Phase 5** — Folder-suffix consistency (complements Phase 1)
3. **Phase 2** — Content-weighted scoring (additive, no breaking changes)
4. **Phase 3** — Recursive territory enforcement (higher risk, needs careful testing)
5. **Phase 4** — Global mixin routing (targeted scope)
6. **Phase 6** — Pre-commit hook (final enforcement layer)

Each phase should be committed independently with its corresponding tests passing.

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

