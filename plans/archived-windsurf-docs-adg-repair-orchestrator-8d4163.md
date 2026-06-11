---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg-repair-orchestrator-8d4163.md'
original_relative_path: 'adg-repair-orchestrator-8d4163.md'
source_sha256: 960f6a70f34baffa2f0c8d153d904f445f6f37c328f7f1d34fb34750b10d2bd5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Repair Orchestrator Implementation Plan

Implements a comprehensive post-ADG repair orchestrator that analyzes ADG reports, categorizes deficiencies by fixability, and automatically applies safe fixes with full deterministic logging.

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| 1 | W1-P1, W1-P2 | Core Framework + Rule Engine Architecture | 18,000 | Token estimator available, ADG reports in JSON format | PENDING | Framework loads, rules register, categories work |
| 2 | W2-P1, W2-P2 | Report Integration + Deficiency Detection | 22,000 | Closure reports generated, SQLite accessible | PENDING | All 7 report types parsed, deficiencies extracted |
| 3 | W3-P1, W3-P2 | AUTO_FIX Rule Implementations | 28,000 | AST parsing available, existing fixers as reference | PENDING | 8+ fix categories implemented, tests pass |
| 4 | W4-P1, W4-P2 | Execution Engine + Integration | 20,000 | Dry-run mode supported, git available | PENDING | Fixes apply, rollbacks work, integrated with ADG gen |

**Total: ~88,000 tokens across 4 waves, all GREEN** 🟢

---

## Gap Register

**GAP-1: No Post-ADG Automated Repair**
- Current ADG generation produces reports but requires manual review
- Deficiencies like missing `__all__`, wrong guardian formats, missing constants require human intervention
- Impact: Wasted engineering cycles on repetitive fixes

**GAP-2: Inconsistent Fix Application**
- Existing fixers (`adg_antipattern_fixer.py`) operate independently
- No centralized orchestration or rollback capability
- Impact: Risk of partial fixes, no atomicity guarantees

**GAP-3: No Deficiency Categorization**
- No distinction between AUTO_FIX (safe), SUGGEST_FIX (needs HITL), and BLOCK_FIX (requires human)
- Impact: Either over-cautious (manual everything) or over-aggressive (auto-break things)

**GAP-4: Limited Observability**
- Current ADG output doesn't clearly show what can vs. cannot be auto-fixed
- Impact: Engineers waste time investigating fixable issues

---

## Execution Plan

### Phase W1-P1 — Core Framework Architecture
**Scope**: Build the `ADGRepairOrchestrator` class with pluggable rule engine, deficiency categorization, and deterministic logging.

**Files to Create**:
- `tools/adg/repair/orchestrator.py` - Main orchestrator class
- `tools/adg/repair/__init__.py` - Package exports
- `tools/adg/repair/types.py` - Deficiency dataclasses, FixCategory enum

**Key Components**:
```python
class FixCategory(enum.Enum):
    AUTO_FIX = "auto_fix"      # Safe to apply automatically
    SUGGEST_FIX = "suggest_fix"  # Needs HITL approval
    BLOCK_FIX = "block_fix"     # Requires human engineering

@dataclass
class Deficiency:
    id: str
    category: FixCategory
    file_path: str
    line_no: int | None
    issue_type: str
    description: str
    suggested_fix: str | None
    confidence: float
```

**Acceptance**:
- [ ] Framework loads without errors
- [ ] Rule registration works
- [ ] Categories properly assign
- [ ] Logging captures all decisions

### Phase W1-P2 — Rule Engine Implementation
**Scope**: Implement the rule registration and matching system that connects deficiency patterns to fix functions.

**Files to Create**:
- `tools/adg/repair/rule_engine.py` - Rule registration and matching
- `tools/adg/repair/base_rule.py` - Abstract base class for repair rules

**Key Components**:
- Decorator-based rule registration (`@repair_rule`)
- Pattern matching against deficiency types
- Priority-based rule ordering
- Conflict detection when multiple rules match

**Acceptance**:
- [ ] Rules register via decorator
- [ ] Pattern matching works
- [ ] Conflicts detected and logged
- [ ] Priority ordering respected

### Phase W2-P1 — Report Integration Layer
**Scope**: Build parsers for all 7 ADG report types to extract deficiencies.

**Files to Create**:
- `tools/adg/report_parsers/closure_parser.py` - closure_validation_report_*.json
- `tools/adg/report_parsers/layer_parser.py` - layer_coverage_report_*.json
- `tools/adg/report_parsers/edge_parser.py` - edge_density_report_*.json
- `tools/adg/report_parsers/provenance_parser.py` - provenance_report_*.json
- `tools/adg/report_parsers/determinism_parser.py` - replay_determinism_report_*.json
- `tools/adg/report_parsers/boundary_parser.py` - boundary_report_*.json
- `tools/adg/report_parsers/mutation_parser.py` - mutation_integrity_report_*.json

**Deficiency Extraction Mapping**:
| Report | Deficiency Type | Category | Fixable |
|--------|----------------|----------|---------|
| closure | STRUCTURAL_COVERAGE_LOW | SUGGEST | Partial |
| closure | EDGE_SEMANTIC_PRECISION_FAIL | AUTO | Yes |
| layer | UNKNOWN_LAYER_MODULE | AUTO | Yes |
| layer | L_UNKNOWN_HIGH_COUNT | SUGGEST | Partial |
| edge | CRITICAL_EDGE_MISSING | BLOCK | No |
| determinism | DIGEST_MISMATCH | BLOCK | No |
| boundary | UNRESOLVED_IMPORTS | AUTO | Yes |
| mutation | MISSING_SIGNATURE | AUTO | Yes |

**Acceptance**:
- [ ] All 7 report parsers implemented
- [ ] Deficiencies extracted with correct categorization
- [ ] SQLite fallback for missing report fields
- [ ] Parser tests pass

### Phase W2-P2 — SQLite Integration for Deep Analysis
**Scope**: Direct SQLite queries for edge-level deficiency detection when reports are insufficient.

**Files to Create**:
- `tools/adg/repair/sqlite_analyzer.py` - Direct ADG SQLite analysis

**Query Patterns**:
- Missing governance edges by module
- Unresolved imports analysis
- Layer violation propagation paths
- Semantic precision gaps

**Acceptance**:
- [ ] SQLite connection and query layer works
- [ ] Edge-level deficiencies detected
- [ ] Module-level aggregations accurate
- [ ] Performance acceptable (<5s for large graphs)

### Phase W3-P1 — AUTO_FIX Rule Implementations (Part 1)
**Scope**: Implement 4 high-value AUTO_FIX rules.

**Files to Create**:
- `tools/adg/repair/rules/fix_missing_all.py` - Add missing `__all__` exports
- `tools/adg/repair/rules/fix_guardian_format.py` - Correct guardian comment format
- `tools/adg/repair/rules/fix_missing_constants.py` - Add missing config constants
- `tools/adg/repair/rules/fix_layer_assignment.py` - Auto-assign L_UNKNOWN layers

**Rule: Missing __all__**
- Detect: Module has exports but no `__all__`
- Fix: Generate `__all__` from detected exports
- Safety: High (adds explicit contract)

**Rule: Guardian Format**
- Detect: Non-canonical guardian comments
- Fix: Apply `adg_antipattern_fixer.py` logic
- Safety: High (format only, no semantic change)

**Rule: Missing Constants**
- Detect: ADG schema expects constants that are missing
- Fix: Add default constants to module
- Safety: Medium (uses sensible defaults)

**Rule: Layer Assignment**
- Detect: L_UNKNOWN modules with inferrable layer
- Fix: Add layer marker comment or move file
- Safety: Medium (path-based inference)

**Acceptance**:
- [ ] Each rule has unit tests
- [ ] Dry-run mode shows intended changes
- [ ] Actual fixes apply correctly
- [ ] Rollback works for each rule

### Phase W3-P2 — AUTO_FIX Rule Implementations (Part 2)
**Scope**: Implement 4 additional AUTO_FIX rules.

**Files to Create**:
- `tools/adg/repair/rules/fix_import_order.py` - Sort imports per policy
- `tools/adg/repair/rules/fix_missing_typing.py` - Add basic type annotations
- `tools/adg/repair/rules/fix_docstring_placeholder.py` - Add placeholder docstrings
- `tools/adg/repair/rules/fix_unused_imports.py` - Remove confirmed unused imports

**Acceptance**:
- [ ] All 8 rules implemented
- [ ] Test coverage >80%
- [ ] No false positives in safe mode

### Phase W4-P1 — Fix Execution Engine
**Scope**: Build the execution engine that applies fixes atomically with rollback support.

**Files to Create**:
- `tools/adg/repair/execution_engine.py` - Fix application with rollback
- `tools/adg/repair/git_integration.py` - Git checkpoint and rollback

**Features**:
- Atomic fix batches (per-file or per-rule)
- Pre-fix git checkpoint
- Post-fix verification
- Automatic rollback on verification failure
- Change summary generation

**Acceptance**:
- [ ] Fixes apply atomically
- [ ] Git checkpoint created before fixes
- [ ] Verification runs post-fix
- [ ] Rollback restores original state
- [ ] Change summary accurate

### Phase W4-P2 — Integration with generate_full_adg.py
**Scope**: Add post-run hook to `generate_full_adg.py` and create standalone entry point.

**Files to Modify**:
- `tools/generate_full_adg.py` - Add `--repair` flag and post-run hook

**Files to Create**:
- `tools/adg_repair.py` - Standalone CLI entry point
- `tools/adg/repair_cli.py` - CLI argument parsing and main flow

**Integration Points**:
```python
# In generate_full_adg.py after report generation:
if args.repair:
    from tools.adg.repair.orchestrator import ADGRepairOrchestrator
    orchestrator = ADGRepairOrchestrator(adg_dir, ts)
    result = orchestrator.run(dry_run=args.repair_dry_run)
    if result.fixes_applied:
        print(f"[ADG] Repair: {result.fixes_applied} fixes applied")
        print(f"[ADG] Repair: {result.fixes_suggested} fixes suggested")
        print(f"[ADG] Repair: {result.fixes_blocked} fixes require human attention")
```

**Acceptance**:
- [ ] `--repair` flag works in generate_full_adg.py
- [ ] Standalone `tools/adg_repair.py` works
- [ ] Dry-run mode shows what would change
- [ ] Full mode applies fixes
- [ ] Integration tested end-to-end

---

## Rules

1. **Never break the build**: All fixes must be reversible; if verification fails, rollback
2. **Category discipline**: Only AUTO_FIX rules apply automatically; SUGGEST_FIX and BLOCK_FIX require explicit override
3. **Audit everything**: Every deficiency, decision, and fix is logged with deterministic IDs
4. **Fail closed on uncertainty**: When confidence < 0.8, escalate to SUGGEST_FIX or BLOCK_FIX
5. **Reuse existing fixers**: Leverage `adg_antipattern_fixer.py` and other proven fixers rather than reimplementing
6. **Test before apply**: Every fix rule must have passing tests before being marked AUTO_FIX
7. **No PowerShell**: Use Python subprocess only, per user preference

---

## Success Criteria

- [ ] All 7 ADG report types parsed and analyzed
- [ ] 8+ AUTO_FIX rules implemented and tested
- [ ] Deficiency categorization accuracy >95%
- [ ] Fix application with atomic rollback capability
- [ ] Integration with `generate_full_adg.py` via `--repair` flag
- [ ] Standalone `tools/adg_repair.py` CLI works
- [ ] Dry-run mode shows all intended changes
- [ ] Full execution applies safe fixes automatically
- [ ] No regressions in existing ADG functionality

---

## Implementation Commands

```bash
# Wave 1: Core framework
python -c "from tools.adg.repair.orchestrator import ADGRepairOrchestrator; print('OK')"
python -c "from tools.adg.repair.rule_engine import RuleEngine; print('OK')"

# Wave 2: Report integration
python tools/adg/repair/test_report_parsers.py
python tools/adg/repair/test_sqlite_analyzer.py

# Wave 3: Fix rules
pytest tools/adg/repair/rules/test_*.py -v

# Wave 4: Integration
python tools/generate_full_adg.py --repair --repair-dry-run
python tools/adg_repair.py --latest --dry-run
python tools/adg_repair.py --latest --apply
```

---

## Rollback Strategy

If things go wrong:
1. **Immediate**: Git checkpoint created pre-repair can be restored via `git checkout <checkpoint-branch>`
2. **Per-file**: Each file modification is backed up to `.adg_repair_backup/<timestamp>/<file>`
3. **Per-rule**: Rules can be disabled via `--skip-rule <rule_id>`
4. **Full reset**: `python tools/adg_repair.py --rollback --to-checkpoint <ts>`
5. **Validation**: Run `pytest tests/adg/ -v` to verify no regressions

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Report parser coverage | 7/7 types | `test_report_parsers.py` passes |
| AUTO_FIX rules implemented | 8+ | `ls tools/adg/repair/rules/fix_*.py` |
| Deficiency categorization accuracy | >95% | Manual review of 50 samples |
| Fix success rate | >90% | Run on test repo, measure success |
| Rollback success rate | 100% | Test rollback after each fix |
| Integration test pass | 100% | `test_adg_repair_integration.py` |
| No ADG regressions | 0 failures | `pytest tests/adg/ -v` |

---

## Design Comparison (Before Selection)

| Design | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A: Post-ADG Script** | Minimal change to existing code, simple, focused | No integration, separate step, easy to forget | ❌ Too decoupled |
| **B: Integrated in Generator** | Single command, tight integration | Complicates generator, mixes concerns, harder to test independently | ❌ Violates SRP |
| **C: Full Orchestrator** | Clean separation, comprehensive, extensible, proper categorization | More initial code, needs careful design | ✅ Selected - best balance of power and maintainability |

---

## Evidence of User Preference Alignment

The user selected:
- **Option C (Full Repair Orchestrator)**: Comprehensive post-ADG system with categorization
- **Max automation**: Fix everything possible, error on unfixable

This plan delivers on both preferences while maintaining safety through:
1. AUTO_FIX category for truly safe automatic fixes
2. SUGGEST_FIX/BLOCK_FIX for items requiring judgment
3. Full deterministic logging for auditability
4. Git-based rollback for recovery
