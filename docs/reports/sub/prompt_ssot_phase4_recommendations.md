# Prompt SSOT Phase 4: Findings → Recommendations

## 1. Inputs

**Phase 2 Evidence**: Duplication inference based on filename symmetry and cross-root citation only; no hash-level duplicate proof available.
**Phase 3 Evidence**: `docs/reports/sub/prompt_ssot_phase3_coupling.md` - Complete coupling analysis with 192 prompt artifacts across 4 root directories

## 2. Findings (P0/P1/P2)

### P0 Findings

**P0-001: Runtime SSOT Fragmentation**

- **What is happening**: Code-critical runtime configuration references `data/prompt_governance` while `agentic_core/prompt_governance/meta_prompts` remains unused
- **Why it matters**: Creates ambiguous ownership - runtime depends on data/ location while meta/ location suggests architectural authority
- **Evidence**:
  - `agentic_core/config/core/injection_layer_config.py:6` → `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md` (config_ref, code_critical)
  - 18/19 files in `agentic_core/prompt_governance/meta_prompts` are unused (Phase 3 authority summary)

### P1 Findings

**P1-001: Cross-Root Naming Symmetry**

- **What is happening**: Symmetric naming suggests potential duplication; content equality not verified.
- **Why it matters**: Creates update burden and risk of divergence - two locations must be kept in sync manually
- **Evidence**:
  - `data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md` ↔ `data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
  - `data/prompt_governance/prompt_injections/Prompt Assembly.md` ↔ `data/prompt_libraries/injections/Prompt Assembly.md`
  - `data/prompt_governance/prompt_injections/Dependency & Prompt Injection Patterns.md` ↔ `data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
  - Cross-root citations in `agentic_core/prompt_governance/meta_prompts/INSTRUCTIONAL_INJECTION_PATTERNS.md:127-129`

**P1-002: Meta-Prompts as Documentation Only**

- **What is happening**: `agentic_core/prompt_governance/meta_prompts` contains 18 unused documentation files and 1 test-only reference
- **Why it matters**: Suggests architectural ownership but provides no runtime value, creating confusion about actual SSOT location
- **Evidence**:
  - 18/19 files in `agentic_core/prompt_governance/meta_prompts` marked as "unused" (Phase 3 authority summary)
  - 1 file (`INSTRUCTIONAL_INJECTION_PATTERNS.md`) referenced only by `tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py:247`

### P2 Findings

**P2-001: Orphaned Prompt Collections**

- **What is happening**: `data/prompts` (4 files) and most of `data/prompt_libraries` (5/8 unused) have no runtime or test references
- **Why it matters**: Dead code increases maintenance burden and creates confusion about which prompts are actually active
- **Evidence**:
  - `data/prompts`: 4 files, all unused (Phase 3 authority summary)
  - `data/prompt_libraries`: 5 unused files, 3 doc_only files (Phase 3 authority summary)

**P2-002: Test-Only Governance Artifacts**

- **What is happening**: 10 files in `data/prompt_governance` are referenced only by SSOT compliance tests, not by actual runtime code
- **Why it matters**: Creates artificial dependency - test infrastructure references artifacts that production doesn't use
- **Evidence**:
  - 10 files in `data/prompt_governance` marked as "test_only" (Phase 3 authority summary)
  - All referenced by `tests/guardian/test_ssot_compliance.py:348`

## 3. SSOT Ownership Model

### Canonical Locations by Function

**agentic_core/prompt_governance/meta_prompts**

- **Purpose**: Architectural documentation, design patterns, and meta-reference material
- **What belongs**: Design documentation, pattern catalogs, architectural decision records
- **What must not**: Runtime-critical prompts, executable templates, configuration files
- **Enforcement**: Documentation-only, no direct code imports

**data/prompt_governance**

- **Purpose**: Runtime SSOT for all critical prompt templates and governance configurations
- **What belongs**: All prompts referenced by production code, injection patterns, governance rules
- **What must not**: Documentation-only files, test-only artifacts, duplicate content
- **Enforcement**: Code-critical references only, single source of truth

**data/prompt_libraries**

- **Purpose**: Candidate for consolidation into `data/prompt_governance`
- **What belongs**: Files pending Wave 3 validation and Wave 1/2 consolidation
- **What must not**: New runtime-critical files
- **Enforcement**: Candidate for removal pending Wave 3 validation.

**data/prompts**

- **Purpose**: Candidate for removal
- **What belongs**: Files pending Wave 3 validation
- **What must not**: New runtime-critical files
- **Enforcement**: Candidate for removal pending Wave 3 validation.

### Ownership Rules

1. **Runtime Rule**: If code imports or references a prompt file, it must be in `data/prompt_governance`
2. **Documentation Rule**: If a prompt file is design documentation only, it belongs in `agentic_core/prompt_governance/meta_prompts`
3. **Uniqueness Rule**: No duplicate content across root directories
4. **Test Rule**: Test-only artifacts should be evaluated for relocation if they are not semantically part of governance model

## 4. Migration Waves

### Wave 0: Compatibility Mapping / Redirect Strategy

- **Goal**: Establish compatibility layer without breaking existing references
- **File Operations**:
  - Create redirect symlinks/aliases for all cross-root references
  - Map `data/prompt_libraries/*` → `data/prompt_governance/*` equivalents
  - Document all current reference patterns
- **Compatibility Strategy**:

  - Add import redirection in `agentic_core/config/core/injection_layer_config.py` if needed
  - Maintain both locations temporarily with clear deprecation notices

- **Verification Commands**:

  ```bash
  rg -n "data/prompt_libraries" --type py agentic_core/ apps_*/ tests/
  rg -n "data/prompts" --type py agentic_core/ apps_*/ tests/
  rg -n "agentic_core/prompt_governance/meta_prompts" --type py agentic_core/ apps_*/
  ```

### Wave 1: Consolidate Named Duplicates

- **Goal**: Establish canonical location for symmetrically-named files
- **File Operations**:
  - `mv data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md data/prompt_governance/prompt_injections/` (if not already canonical)
  - `mv data/prompt_libraries/injections/Prompt\ Assembly.md data/prompt_governance/prompt_injections/`
  - `mv data/prompt_libraries/injections/Dependency\ &\ Prompt\ Injection\ Patterns.md data/prompt_governance/prompt_injections/`
- **Compatibility Strategy**:

  - Update cross-root citations in `INSTRUCTIONAL_INJECTION_PATTERNS.md` to point to canonical location
  - Add temporary redirect symlinks for any external consumers

- **Verification Commands**:

  ```bash
  rg -n "data/prompt_libraries" docs/ agentic_core/
  diff data/prompt_governance/prompt_injections/Instructional_Injection_Enhanced_v5.md data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md || echo "Files differ or missing"
  ```

### Wave 2: Resolve NAME Collisions with SSOT Naming Rules

- **Goal**: Establish clear naming conventions and eliminate ambiguous references
- **File Operations**:
  - Rename files in `data/prompt_governance/` to follow consistent naming pattern
  - Standardize on `kebab-case.md` for all prompt files
  - Consolidate test-only artifacts into dedicated `tests/fixtures/prompts/` directory
- **Compatibility Strategy**:

  - Update import references in test files
  - Add deprecation shims for any external API dependencies

- **Verification Commands**:

  ```bash
  find data/prompt_governance/ -name "*.md" | grep -E "[A-Z]"
  rg -n "test_tests_golden_state_test_datasets.py" --type py tests/
  ```

### Wave 3: Runtime Reachability Validation

- **Goal**: Confirm only referenced files are actually reachable by runtime systems before any deletions
- **Reachability Probes**:

  ```bash
  # Check for glob/listdir patterns that might load files dynamically
  rg -n "glob.*prompt|listdir.*prompt|walk.*prompt" --type py agentic_core/ apps_*/ tests/

  # Check for dynamic YAML loading patterns
  rg -n "yaml\.load|yaml\.safe_load.*prompt|\.yaml.*prompt" --type py agentic_core/ apps_*/ tests/

  # Check for registry patterns that might enumerate prompt files
  rg -n "registry.*prompt|register.*prompt|prompt.*registry" --type py agentic_core/ apps_*/ tests/

  # Execute injection_layer_config loader to confirm only referenced files load
  python -c "
  import sys
  sys.path.insert(0, '.')
  try:
    from agentic_core.config.core.injection_layer_config import get_injection_config
    config = get_injection_config()
    print('SUCCESS: Config loads without errors')
    print(f'Referenced file: {config.get(\"prompt_file\", \"NOT_FOUND\")}')
  except Exception as e:
    print(f'ERROR: Config loading failed: {e}')
  "
  ```

- **Validation Criteria**:
  - Zero runtime references to deprecated directories
  - Zero dynamic loading patterns that might reach orphaned files
  - All documented references resolve to canonical locations
  - Configuration loaders succeed without missing file errors

- **Gatekeeping Rule**: No directory deletion permitted until:
  - 0 static references (rg),
  - 0 dynamic loads (Wave 3 probes),
  - all existing tests pass.

### Wave 4: Guardrail Enforcement Proposal

- **Goal**: Prevent reintroduction of duplicates and cross-root violations
- **Guardrail Check**: `agentic_core/L5_safety/enforcement/prompt_ssot_guardrail.py`

  - Scan for duplicate content across all prompt root directories
  - Validate that code references only point to `data/prompt_governance`
  - Check for cross-root citations in documentation
  - Verify no orphaned files in deprecated directories

- **Enforcement Rules**:

  - FAIL if any duplicate content detected across roots
  - FAIL if production code references non-canonical locations
  - WARN if documentation contains cross-root citations; FAIL only if production/runtime code references non-canonical locations
  - WARN if deprecated directories contain content prior to Wave 5.
  - FAIL if deprecated directories contain content after Wave 5.

- **Integration**: Add to `.github/workflows/prompt-governance.yml`

### Wave 5: Final Deprecation Cleanup

- **Goal**: Remove deprecated directories and unused content after all references validated
- **Pre-deletion Verification**:
  - Confirm zero runtime refs to deprecated directories
  - Confirm zero doc refs to deprecated directories
  - Confirm zero test refs to deprecated directories
- **File Operations**:
  - `rm -rf data/prompt_libraries/` (only after verification passes)
  - `rm -rf data/prompts/` (only after verification passes)
  - Clean up test-only artifacts from `data/prompt_governance/`
- **Compatibility Strategy**:

  - All references should already be updated in previous waves
  - No breaking changes expected

- **Verification Commands**:

  ```bash
  # Final verification - should show no references
  rg -n "data/prompt_libraries|data/prompts" --type py agentic_core/ apps_*/ tests/ && echo "FAIL: References remain" || echo "PASS: No references found"

  # Confirm directories removed
  test -d data/prompt_libraries && echo "FAIL: Directory still exists" || echo "PASS: Directory removed"
  test -d data/prompts && echo "FAIL: Directory still exists" || echo "PASS: Directory removed"
  ```

## 5. Verification Commands

### Pre-Migration Baseline

```bash
# Count current artifacts
find agentic_core/prompt_governance/meta_prompts/ -name "*.md" | wc -l
find data/prompt_governance/ -name "*.md" | wc -l
find data/prompt_libraries/ -name "*.md" | wc -l
find data/prompts/ -name "*.md" | wc -l

# Check cross-root references
rg -n "data/prompt_libraries" . --type md
rg -n "data/prompts" . --type md
rg -n "agentic_core/prompt_governance/meta_prompts" . --type py
```

### Post-Migration Validation

```bash
# Verify no cross-root citations
rg -n "data/prompt_libraries|data/prompts" agentic_core/ apps_*/ tests/ && echo "FAIL: Cross-root references remain" || echo "PASS: No cross-root references"

# Verify runtime references are canonical
rg -n "data/prompt_governance" agentic_core/config/core/injection_layer_config.py && echo "PASS: Runtime uses canonical location"

# Run existing tests
pytest tests/guardian/test_ssot_compliance.py -xvv
pytest tests/unit/agentic_core/context_engineering/test_phase0_contract_harness.py -xvv
```

### Guardian Integration Test

```bash
# Run proposed guardrail
python -m agentic_core.L5_safety.enforcement.prompt_ssot_guardrail

# Should output:
# PASS: No duplicate content across prompt roots
# PASS: All code references use canonical locations
# WARN: Documentation cross-root citations detected (non-blocking)
# PASS: No production/runtime cross-root violations
# WARN: Deprecated directories contain content prior to Wave 5.
# PASS: Deprecated directories removed after Wave 5.
```

## 6. Decision Summary

### Canonical SSOT Locations

- **Runtime Prompts**: `data/prompt_governance/` - Single source of truth for all production prompt templates
- **Documentation**: `agentic_core/prompt_governance/meta_prompts/` - Architectural documentation and design patterns only
- **Deprecated**: `data/prompt_libraries/` and `data/prompts/` - Candidate for removal pending Wave 3 validation

### What Becomes Deprecated

- Entire `data/prompt_libraries/` directory (content migrated to `data/prompt_governance/`) - Candidate for removal pending Wave 3 validation
- Entire `data/prompts/` directory (currently unused per static analysis; candidate for removal pending Wave 3 validation)
- Test-only artifacts in production directories (evaluated for relocation)

### What Will Be Enforced by Guardian

- No duplicate content across prompt root directories
- Production code may only reference `data/prompt_governance/`
- WARN on documentation cross-root citations; FAIL only on production/runtime violations
- WARN if deprecated directories contain content prior to Wave 5.
- FAIL if deprecated directories contain content after Wave 5.
- All runtime-critical prompts must be in canonical location

This migration establishes a clear, enforceable SSOT model that eliminates ambiguity while maintaining all necessary functionality through a structured, wave-based approach with runtime reachability validation preceding any deletion operations.
