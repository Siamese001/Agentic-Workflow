# AST + Fuzzy SSOT Consolidation Phase 1 Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Objective
Eliminate duplicated/divergent AST + fuzzy/similarity matching implementations by discovering, inventorying, and designing a consolidated SSOT utility.

## Wave 1.1: SSOT Folder Discovery (COMPLETED)
**Governance Sources Found:**
- `agentic_core/L5_safety/config/structure_blueprint/` - Core structural SSOT
- `ops_scripts/hooks/validate_folder_purity.py` - Defines project dirs: `["agentic_core", "apps_lic", "apps_rg", "apps_shared"]`
- `tests/_contracts/` - Contract enforcement boundaries
- Legacy allowlists and quarantine manifests for excluded areas

**Derived SSOT-Approved Folders:**
- `agentic_core/` - Core framework (L0-L7 layers)
- `tools/` - Architectural and governance tools
- `ops_scripts/` - Operational scripts and maintenance
- `docs/reports/` - Documentation (report storage per constitutional rule)

**Explicit Exclusions:**
- `tests/` - Test code (quarantine-managed)
- `apps_lic/`, `apps_rg/`, `apps_shared/` - Application layers (untrusted per governance)
- `archives/` - Deprecated code
- `.backup/` - Backup files

## Wave 1.2: Inventory AST + Fuzzy Logic (IN PROGRESS)
**Discovery Targets:**
- AST libraries: `ast`, `libcst`, `parso`, `tree_sitter`, `typed_ast`, `astroid`, `inspect`, `tokenize`, `symtable`, `compile`
- Fuzzy libraries: `rapidfuzz`, `fuzzywuzzy`, `difflib`, `Levenshtein`, `jaro`, `jaccard`
- Definition patterns: functions/classes containing keywords like `parse`, `fuzzy`, `similar`, `match`, `compare`, `normalize`

**Preliminary Findings:**
- **agentic_core/**: 40+ files with AST usage (validators, mixins, runtime engines)
- **tools/**: Minimal AST usage (security guards)
- **ops_scripts/**: 30+ files with AST usage (maintenance, governance, analysis)
- **Fuzzy usage**: Primarily `difflib.SequenceMatcher` for similarity scoring
- **Hot spots**: `L5_safety/validators/`, `mixins/`, `L0_routing/scripts/`

## Wave 1.3: Near-Duplicate Clustering (PENDING)
**Methodology:**
- AST structural hash via `ast.dump(node, include_attributes=False)` → SHA256
- Token-based fingerprinting for similarity detection
- Cluster by: identical structural hash (exact dupes) + high token similarity
- Use stdlib `difflib.SequenceMatcher` for deterministic similarity scoring

## Wave 1.4: Call-Site Mapping (PENDING)
**Approach:**
- Lightweight ripgrep for symbol names (word boundaries)
- AST call extraction for same-module references
- Map definition → call-sites with file:line references
- Identify "most central" definitions by inbound reference count

## Wave 1.5: Consolidation Design (PENDING)
**Proposed SSOT Location:** `agentic_core/utils/ast_fuzzy.py`
**Rationale:**
- Inside `agentic_core/` (proven SSOT-approved)
- Co-located with other utilities in `utils/`
- Accessible to all layers without layer inversion

**Proposed API (stdlib-first):**
```python
# Core AST utilities
parse_source_to_ast(source: str, *, mode="exec") -> ast.AST
stable_ast_dump(node: ast.AST) -> str
ast_structural_hash(node: ast.AST) -> str

# Similarity utilities (stdlib difflib)
normalize_tokens(source: str) -> list[str]
similarity(a: str|list[str], b: str|list[str], *, method="sequence", threshold=None) -> float
best_match(query, candidates, *, threshold, return_score=True) -> ...
```

**Migration Strategy:**
- Replace duplicate implementations with SSOT imports
- Deprecate old functions with clear shims pointing to SSOT
- Preserve existing behavior via configurable normalization rules

## Deliverables
1. **Discovery script**: `tools/tmp_ok/scan_ast_fuzzy_defs.py`
2. **Evidence report**: `docs/reports/sub/ast_fuzzy_ssot_consolidation_phase1.md`
3. **Inventory JSON**: Deterministic file/definition/call-site mapping
4. **Cluster analysis**: Near-duplicate groups with similarity metrics

## Acceptance Criteria
- Single evidence markdown file with all findings
- Deterministic outputs (re-runnable → byte-identical)
- No functional code changes in Phase 1 (discovery + design only)
- Clear migration path with risk assessment

## Next Steps
1. Create discovery script in approved tools location
2. Run comprehensive scan of SSOT folders
3. Perform clustering analysis
4. Generate evidence report with design recommendations
5. Present findings for Phase 2 implementation approval

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

