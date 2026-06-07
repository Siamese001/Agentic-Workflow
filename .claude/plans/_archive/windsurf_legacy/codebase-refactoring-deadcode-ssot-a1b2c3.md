# Codebase Refactoring — Dead Code Removal, File Reorganization, and SSOT Updates

Comprehensive T3 architectural refactoring to remove dead code, reorganize file structures, eliminate root-level files, and update all SSOTs across system_learning/, agentic_core/, ops_scripts/, data/, docs/, infrastructure/, and tools/.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | 1.1-1.5 | system_learning/ (32 subdirs) | 45,000 🟢 | ADG signals accurate, no critical deps | Pending | Dead code removed, files reorganized, SSOT updated |
| Wave 2 | 2.1-2.4 | agentic_core/prompt_governance/ + runtime/ | 35,000 🟢 | Low coupling to other layers | Pending | Dead code removed, files reorganized, SSOT updated |
| Wave 3 | 3.1-3.6 | ops_scripts/ (13 subdirs) | 55,000 🟢 | Script isolation high | Pending | Dead code removed, files reorganized, SSOT updated |
| Wave 4 | 4.1-4.5 | data/, docs/, infrastructure/, tools/ | 65,000 🟢 | Data/docs mostly static | Pending | Dead code removed, files reorganized, SSOT updated |
| Wave 5 | 5.1-5.3 | Test mirroring and validation | 40,000 🟢 | Test infrastructure intact | Pending | Tests mirror structure, all tests pass |

**Total: 240,000 tokens across 5 waves, all GREEN**

---

## Gap Register

**GAP-1: ADG MCP server unavailable**
- ADG health check returns transport error
- Workaround: Use ADG snapshot JSON for dead code signals (unused_import: 16,653, dead_imports: 1,522, unreachable_after_raise: 17, duplicate_method: 11)
- Impact: Cannot query live database for specific file-level dependency analysis

**GAP-2: Token estimation unavailable**
- Token estimator script not yet executed
- Workaround: Manual estimation based on file counts and complexity
- Impact: Token budgets are estimates, may need adjustment during execution

**GAP-3: SSOT update scope unclear**
- Multiple SSOT files may need updates (excluded_paths.yaml, territories.yaml, layers.yaml, ast_signals.yaml)
- Workaround: Query all SSOT files after each wave to determine update requirements
- Impact: May require additional waves for SSOT synchronization

---

## Execution Plan

### Phase 1.1 — ADG Signal Analysis for system_learning/
**Scope**: Query ADG snapshot for dead code signals in system_learning/ directory (248 nodes per ADG)

**Commands**:
```python
# Parse ADG snapshot for dead code signals
python -c "
import json
with open('artifacts/adg/adg_snapshot_04062026_0952.json') as f:
    snapshot = json.load(f)
print(f'Unused imports: {snapshot[\"graph_plane_counts\"][\"unused_import\"]}')
print(f'Dead imports: {snapshot[\"graph_plane_counts\"][\"dead_imports\"]}')
print(f'Unreachable code: {snapshot[\"graph_plane_counts\"][\"unreachable_after_raise\"]}')
"
```

**Acceptance**: Dead code signals extracted and documented for system_learning/

### Phase 1.2 — File Structure Analysis for system_learning/
**Scope**: Analyze 32 subdirectories in system_learning/ for root-level files and organization issues

**Commands**:
```python
# Analyze directory structure
python tools/analysis/directory_structure_analyzer.py --target system_learning --output docs/reports/plans/system_learning_structure_analysis.md
```

**Acceptance**: Structure analysis report generated with recommendations

### Phase 1.3 — Dead Code Identification and Testing
**Scope**: Identify dead code in system_learning/ using ADG signals and create test coverage

**Commands**:
```python
# Identify dead code files
python tools/analysis/dead_code_detector.py --target system_learning --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/system_learning_dead_code.md

# Create tests for files to be removed
python tools/testing/test_generator.py --target system_learning --dead-code-report docs/reports/plans/system_learning_dead_code.md
```

**Acceptance**: Dead code identified with test coverage ensuring safe removal

### Phase 1.4 — File Reorganization
**Scope**: Move high-signal files to appropriate subfolders, eliminate root-level files, move low-signal files to subfolders

**Commands**:
```python
# Execute file reorganization
python tools/migrate/file_reorganizer.py --target system_learning --plan docs/reports/plans/system_learning_structure_analysis.md --dry-run false
```

**Acceptance**: Files reorganized according to plan, no root-level files remain

### Phase 1.5 — SSOT Updates for system_learning/
**Scope**: Update SSOT files to reflect system_learning/ structural changes

**Commands**:
```python
# Update SSOT files
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories --update-excluded-paths

# Validate SSOT consistency
python ops_scripts/ci/_analyse_ssot_violations.py
```

**Acceptance**: SSOT files updated and validated, no violations

### Phase 2.1 — ADG Signal Analysis for prompt_governance/ and runtime/
**Scope**: Query ADG snapshot for dead code signals in prompt_governance/ (130 nodes) and runtime/ (98 nodes)

**Commands**:
```python
# Parse ADG snapshot for specific layers
python -c "
import json
with open('artifacts/adg/adg_snapshot_04062026_0952.json') as f:
    snapshot = json.load(f)
print(f'L_PG nodes: {snapshot[\"by_layer\"][\"L_PG\"]}')
print(f'L_RUNTIME nodes: {snapshot[\"by_layer\"][\"L_RUNTIME\"]}')
"
```

**Acceptance**: Dead code signals extracted for both directories

### Phase 2.2 — File Structure Analysis for prompt_governance/ and runtime/
**Scope**: Analyze 9 subdirs in prompt_governance/ and 7 subdirs in runtime/ for organization issues

**Commands**:
```python
# Analyze directory structure
python tools/analysis/directory_structure_analyzer.py --target agentic_core/prompt_governance --output docs/reports/plans/prompt_governance_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target agentic_core/runtime --output docs/reports/plans/runtime_structure_analysis.md
```

**Acceptance**: Structure analysis reports generated

### Phase 2.3 — Dead Code Removal and File Reorganization
**Scope**: Remove dead code and reorganize files in both directories

**Commands**:
```python
# Identify and remove dead code
python tools/analysis/dead_code_detector.py --target agentic_core/prompt_governance --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/prompt_governance_dead_code.md
python tools/analysis/dead_code_detector.py --target agentic_core/runtime --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/runtime_dead_code.md

# Reorganize files
python tools/migrate/file_reorganizer.py --target agentic_core/prompt_governance --plan docs/reports/plans/prompt_governance_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target agentic_core/runtime --plan docs/reports/plans/runtime_structure_analysis.md --dry-run false
```

**Acceptance**: Dead code removed, files reorganized

### Phase 2.4 — SSOT Updates for prompt_governance/ and runtime/
**Scope**: Update SSOT files to reflect changes

**Commands**:
```python
# Update SSOT files
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories

# Validate SSOT consistency
python ops_scripts/ci/_analyse_ssot_violations.py
```

**Acceptance**: SSOT files updated and validated

### Phase 3.1 — ADG Signal Analysis for ops_scripts/
**Scope**: Query ADG snapshot for dead code signals in ops_scripts/ (673 nodes)

**Commands**:
```python
# Parse ADG snapshot
python -c "
import json
with open('artifacts/adg/adg_snapshot_04062026_0952.json') as f:
    snapshot = json.load(f)
print(f'L_OPS nodes: {snapshot[\"by_layer\"][\"L_OPS\"]}')
"
```

**Acceptance**: Dead code signals extracted for ops_scripts/

### Phase 3.2 — File Structure Analysis for ops_scripts/
**Scope**: Analyze 13 subdirectories in ops_scripts/ for organization issues

**Commands**:
```python
# Analyze directory structure
python tools/analysis/directory_structure_analyzer.py --target ops_scripts --output docs/reports/plans/ops_scripts_structure_analysis.md
```

**Acceptance**: Structure analysis report generated

### Phase 3.3 — Dead Code Identification in ops_scripts/
**Scope**: Identify dead code with focus on obsolete CI scripts and maintenance tools

**Commands**:
```python
# Identify dead code
python tools/analysis/dead_code_detector.py --target ops_scripts --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/ops_scripts_dead_code.md
```

**Acceptance**: Dead code identified with categorization (obsolete, deprecated, unused)

### Phase 3.4 — Archive Obsolete Scripts
**Scope**: Move obsolete scripts to tools/archive/ with preservation metadata

**Commands**:
```python
# Archive obsolete scripts
python tools/archive/script_archiver.py --target ops_scripts --dead-code-report docs/reports/plans/ops_scripts_dead_code.md --archive-dir tools/archive/ops_scripts_obsolete
```

**Acceptance**: Obsolete scripts archived with metadata

### Phase 3.5 — File Reorganization for ops_scripts/
**Scope**: Reorganize remaining files into appropriate subdirectories

**Commands**:
```python
# Reorganize files
python tools/migrate/file_reorganizer.py --target ops_scripts --plan docs/reports/plans/ops_scripts_structure_analysis.md --dry-run false
```

**Acceptance**: Files reorganized according to plan

### Phase 3.6 — SSOT Updates for ops_scripts/
**Scope**: Update SSOT files to reflect ops_scripts/ changes

**Commands**:
```python
# Update SSOT files
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories --update-excluded-paths

# Validate SSOT consistency
python ops_scripts/ci/_analyse_ssot_violations.py
```

**Acceptance**: SSOT files updated and validated

### Phase 4.1 — ADG Signal Analysis for data/, docs/, infrastructure/, tools/
**Scope**: Query ADG snapshot for dead code signals across all four directories

**Commands**:
```python
# Parse ADG snapshot
python -c "
import json
with open('artifacts/adg/adg_snapshot_04062026_0952.json') as f:
    snapshot = json.load(f)
print(f'L_TOOLS nodes: {snapshot[\"by_layer\"][\"L_TOOLS\"]}')
print(f'L_INFRA nodes: {snapshot[\"by_layer\"][\"L_INFRA\"]}')
"
```

**Acceptance**: Dead code signals extracted

### Phase 4.2 — File Structure Analysis for data/ and docs/
**Scope**: Analyze data/ (13 subdirs) and docs/ (17 subdirs) for organization

**Commands**:
```python
# Analyze directory structure
python tools/analysis/directory_structure_analyzer.py --target data --output docs/reports/plans/data_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target docs --output docs/reports/plans/docs_structure_analysis.md
```

**Acceptance**: Structure analysis reports generated

### Phase 4.3 — File Structure Analysis for infrastructure/ and tools/
**Scope**: Analyze infrastructure/ (6 subdirs) and tools/ (28 subdirs) for organization

**Commands**:
```python
# Analyze directory structure
python tools/analysis/directory_structure_analyzer.py --target infrastructure --output docs/reports/plans/infrastructure_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target tools --output docs/reports/plans/tools_structure_analysis.md
```

**Acceptance**: Structure analysis reports generated

### Phase 4.4 — Dead Code Removal and File Reorganization
**Scope**: Remove dead code and reorganize files across all four directories

**Commands**:
```python
# Identify dead code
python tools/analysis/dead_code_detector.py --target data --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/data_dead_code.md
python tools/analysis/dead_code_detector.py --target docs --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/docs_dead_code.md
python tools/analysis/dead_code_detector.py --target infrastructure --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/infrastructure_dead_code.md
python tools/analysis/dead_code_detector.py --target tools --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/tools_dead_code.md

# Reorganize files
python tools/migrate/file_reorganizer.py --target data --plan docs/reports/plans/data_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target docs --plan docs/reports/plans/docs_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target infrastructure --plan docs/reports/plans/infrastructure_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target tools --plan docs/reports/plans/tools_structure_analysis.md --dry-run false
```

**Acceptance**: Dead code removed, files reorganized

### Phase 4.5 — SSOT Updates for data/, docs/, infrastructure/, tools/
**Scope**: Update SSOT files to reflect all changes

**Commands**:
```python
# Update SSOT files
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories --update-excluded-paths --update-ast-signals

# Validate SSOT consistency
python ops_scripts/ci/_analyse_ssot_violations.py
```

**Acceptance**: SSOT files updated and validated

### Phase 5.1 — Test Mirroring Analysis
**Scope**: Analyze test coverage and ensure tests/ mirrors all file structure changes

**Commands**:
```python
# Analyze test coverage
python tools/testing/test_mirror_analyzer.py --target-all --output docs/reports/plans/test_mirror_analysis.md
```

**Acceptance**: Test mirror analysis report generated

### Phase 5.2 — Generate Missing Tests
**Scope**: Generate tests for newly created files and reorganized structures

**Commands**:
```python
# Generate missing tests
python tools/testing/test_generator.py --target-all --structure-reports docs/reports/plans/*_structure_analysis.md --output tests/
```

**Acceptance**: Missing tests generated

### Phase 5.3 — Full Test Suite Validation
**Scope**: Run full test suite to validate all changes

**Commands**:
```python
# Run full test suite
pytest tests/ -v --tb=short --maxfail=5

# Run ADG regeneration to validate structural changes
python tools/generate_full_adg.py

# Validate ADG integrity
python tools/adg/adg_rigorous_gap_closure_0617.py
```

**Acceptance**: All tests pass, ADG regenerates successfully, no violations

---

## Rules

- **Constitutional §0**: No PowerShell, use subprocess.run with shell=False
- **Constitutional §1**: No test skipping, all changes must have test coverage
- **Constitutional §2**: No editing while exploring — all 5 repair gates must pass
- **Constitutional §5**: ADG artifacts must be fully ingested before any query or refactoring
- **Constitutional §6**: Author-Gate discipline for decisions with multiple valid approaches
- **Constitutional §8**: Guardian exemption discipline — never add guardian comments without Author-Gate approval
- **Constitutional §10**: Zero-loss refactor discipline — check hollow file detector after removing boilerplate
- **Constitutional §11**: Terminal process lifecycle management — all processes must be terminated
- **Constitutional §12**: No imports from archives/ in production code
- **Graph-First Evidence**: ADG is primary evidence, text search is secondary confirmation only
- **Fail-Closed Rule**: If ADG cannot be built, STOP and record errors
- **Tier-Aware Analysis**: This is T3 — full AST dependency graph protocol required
- **Scope Validation**: Before any edit, declare exact file list with graph justification
- **Duplicate Prevention**: Before creating any new symbol, execute 4-step search

---

## Success Criteria

- [ ] All dead code removed (unused imports, dead imports, unreachable code, duplicate methods)
- [ ] All directories reorganized with no root-level files
- [ ] High-signal files moved to appropriate subfolders
- [ ] Low-signal files moved to newly created subfolders
- [ ] All SSOT files updated (excluded_paths.yaml, territories.yaml, layers.yaml, ast_signals.yaml)
- [ ] Test coverage mirrors all file structure changes
- [ ] Full test suite passes (pytest tests/)
- [ ] ADG regenerates successfully without errors
- [ ] No SSOT violations detected
- [ ] No guardian exemptions added without Author-Gate approval
- [ ] No imports from archives/ in production code
- [ ] All terminal processes terminated properly

---

## Implementation Commands

```bash
# Wave 1: system_learning/
python tools/analysis/directory_structure_analyzer.py --target system_learning --output docs/reports/plans/system_learning_structure_analysis.md
python tools/analysis/dead_code_detector.py --target system_learning --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/system_learning_dead_code.md
python tools/testing/test_generator.py --target system_learning --dead-code-report docs/reports/plans/system_learning_dead_code.md
python tools/migrate/file_reorganizer.py --target system_learning --plan docs/reports/plans/system_learning_structure_analysis.md --dry-run false
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories --update-excluded-paths
python ops_scripts/ci/_analyse_ssot_violations.py

# Wave 2: prompt_governance/ and runtime/
python tools/analysis/directory_structure_analyzer.py --target agentic_core/prompt_governance --output docs/reports/plans/prompt_governance_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target agentic_core/runtime --output docs/reports/plans/runtime_structure_analysis.md
python tools/analysis/dead_code_detector.py --target agentic_core/prompt_governance --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/prompt_governance_dead_code.md
python tools/analysis/dead_code_detector.py --target agentic_core/runtime --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/runtime_dead_code.md
python tools/migrate/file_reorganizer.py --target agentic_core/prompt_governance --plan docs/reports/plans/prompt_governance_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target agentic_core/runtime --plan docs/reports/plans/runtime_structure_analysis.md --dry-run false
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories
python ops_scripts/ci/_analyse_ssot_violations.py

# Wave 3: ops_scripts/
python tools/analysis/directory_structure_analyzer.py --target ops_scripts --output docs/reports/plans/ops_scripts_structure_analysis.md
python tools/analysis/dead_code_detector.py --target ops_scripts --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/ops_scripts_dead_code.md
python tools/archive/script_archiver.py --target ops_scripts --dead-code-report docs/reports/plans/ops_scripts_dead_code.md --archive-dir tools/archive/ops_scripts_obsolete
python tools/migrate/file_reorganizer.py --target ops_scripts --plan docs/reports/plans/ops_scripts_structure_analysis.md --dry-run false
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories --update-excluded-paths
python ops_scripts/ci/_analyse_ssot_violations.py

# Wave 4: data/, docs/, infrastructure/, tools/
python tools/analysis/directory_structure_analyzer.py --target data --output docs/reports/plans/data_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target docs --output docs/reports/plans/docs_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target infrastructure --output docs/reports/plans/infrastructure_structure_analysis.md
python tools/analysis/directory_structure_analyzer.py --target tools --output docs/reports/plans/tools_structure_analysis.md
python tools/analysis/dead_code_detector.py --target data --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/data_dead_code.md
python tools/analysis/dead_code_detector.py --target docs --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/docs_dead_code.md
python tools/analysis/dead_code_detector.py --target infrastructure --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/infrastructure_dead_code.md
python tools/analysis/dead_code_detector.py --target tools --adg-snapshot artifacts/adg/adg_snapshot_04062026_0952.json --output docs/reports/plans/tools_dead_code.md
python tools/migrate/file_reorganizer.py --target data --plan docs/reports/plans/data_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target docs --plan docs/reports/plans/docs_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target infrastructure --plan docs/reports/plans/infrastructure_structure_analysis.md --dry-run false
python tools/migrate/file_reorganizer.py --target tools --plan docs/reports/plans/tools_structure_analysis.md --dry-run false
python ops_scripts/dev_tools/L0_routing_scripts/ssot_adapters.py --update-layers --update-territories --update-excluded-paths --update-ast-signals
python ops_scripts/ci/_analyse_ssot_violations.py

# Wave 5: Test mirroring and validation
python tools/testing/test_mirror_analyzer.py --target-all --output docs/reports/plans/test_mirror_analysis.md
python tools/testing/test_generator.py --target-all --structure-reports docs/reports/plans/*_structure_analysis.md --output tests/
pytest tests/ -v --tb=short --maxfail=5
python tools/generate_full_adg.py
python tools/adg/adg_rigorous_gap_closure_0617.py
```

---

## Rollback Strategy

If things go wrong:
1. Git revert all changes: `git revert --no-commit HEAD`
2. Restore SSOT files from backup: `cp config/structure_blueprint/*.yaml.backup config/structure_blueprint/`
3. Restore archived files: `python tools/archive/script_restorer.py --archive-dir tools/archive/ops_scripts_obsolete --target ops_scripts`
4. Regenerate ADG: `python tools/generate_full_adg.py`
5. Validate system integrity: `pytest tests/ --maxfail=5`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Dead code removed | 100% of identified dead code | ADG snapshot comparison before/after |
| Root-level files | 0 in all target directories | Directory structure analyzer |
| File organization | 100% compliant with plan | Structure analysis validation |
| SSOT consistency | 0 violations | `_analyse_ssot_violations.py` |
| Test coverage | Mirrors all file changes | Test mirror analyzer |
| Test suite pass rate | 100% | `pytest tests/` |
| ADG regeneration | Success with 0 errors | `generate_full_adg.py` |
| Guardian exemptions | 0 new without Author-Gate | Guardian exemption gate |
| Archives imports | 0 in production code | `check_no_archives_imports.py` |
