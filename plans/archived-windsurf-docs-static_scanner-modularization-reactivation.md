---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\static_scanner-modularization-reactivation.md'
original_relative_path: 'static_scanner-modularization-reactivation.md'
source_sha256: b80fba7c244dd003c5ba433fea56c8313434895ed71a0dc7aa15ca19238cc3d5
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-02'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# static_scanner.py Modularization Reactivation Plan

## Reactivation Trigger
File size at 417KB (93% of 450KB threshold); visitor count at 24 (96% of 25 threshold).

---

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|---------------|--------|------------------|
| P0 | P0-SSOT, P0-SYNTH | Symbol SSOT cleanup, bootstrap isolation | 6,200 | schema_util.py exports complete | 🟡 IN PROGRESS | Duplicate frozensets removed, module-load synthetic edges isolated |
| P1 | P1-ORCH, P1-REG, P1-POL | Orchestration/extraction separation | 8,500 | P0 complete, scan_mode logic stable | 🟢 PENDING | scanner.py orchestration only, registry.py declarative, policy.py mode selection |
| P2 | P2-BASE, P2-VIS | Visitor base contract + category decomposition | 9,800 | P1 complete, visitor signatures stable | 🟢 PENDING | visitors/base.py contract, visitors/structural/, visitors/governance/, visitors/l4_waves/ |
| P3 | P3-HELP, P3-FILT | Shared helpers consolidation, filters extraction | 5,400 | P2 complete, helper patterns identified | 🟢 PENDING | Symbol parsing helpers unified, runtime filters extracted |
| P4 | P4-TEST, P4-VAL | Test reconstruction + validation harness | 7,100 | P3 complete, visitor contracts stable | 🟢 PENDING | Contract tests per visitor, determinism digest regression, no-bootstrap-leakage test |
| P5 | P5-OPT | Scan-mode optimization post-architecture | 4,200 | P4 complete, architecture stable | 🟢 PENDING | Cache-aware mode optimized, selective visitor dispatch benchmarked |

**Total: 41,200 tokens across 6 phases, YELLOW** (architectural refactoring with behavior preservation)

---

## Phase 0: Symbol SSOT + Synthetic Edge Control (P0)

### P0-SSOT: Remove Duplicate Symbol Definitions

**Current issue:** Lines 2747-2789 in `static_scanner.py` contain local frozensets shadowing imports from `schema_util.py`.

**Files:**
- `agentic_core/adg/extraction/static_scanner.py` — Delete duplicate frozensets
- `agentic_core/adg/schema_util.py` — Verify exports cover all required symbol families

**Actions:**
1. Identify all `_UWG_*_SYMBOLS` local frozensets at lines 2747-2789
2. Verify each exists in `schema_util.py` imports (lines 135-138)
3. Delete local definitions
4. Update references to use imported names (remove underscore prefix where applicable)

**Acceptance:**
- [ ] 0 local frozensets shadowing `schema_util.py` exports
- [ ] Import-time assertion validates all required symbol sets non-empty
- [ ] 19/19 scanner tests pass

### P0-SYNTH: Isolate Bootstrap/Instrumentation Edges

**Current issue:** Module-load `_emit_*` calls pollute scanner output with synthetic edges.

**Files:**
- `agentic_core/adg/extraction/static_scanner.py` — Gate bootstrap calls behind flag
- `agentic_core/adg/extraction/scanner.py` (new) — Create orchestrator without bootstrap pollution

**Actions:**
1. Add `ADG_SCANNER_SELF_TEST` environment flag
2. Gate all module-level `_emit_*` calls: `if os.environ.get("ADG_SCANNER_SELF_TEST"):`
3. Default scan mode excludes synthetic bootstrap edges

**Acceptance:**
- [ ] 0 synthetic edges in production scan output by default
- [ ] Self-test mode produces same edges as before (backward compatible)
- [ ] New "no-bootstrap-leakage" test passes

---

## Phase 1: Orchestration/Extraction Separation (P1)

### P1-ORCH: Extract Scanner Orchestrator

**Files:**
- `agentic_core/adg/extraction/scanner.py` (new) — `ADGStaticScanner` orchestrator
- `agentic_core/adg/extraction/static_scanner.py` — Remove orchestration, keep visitors temporarily

**Actions:**
1. Move `scan()`, `_get_cache_aware_scan_mode()`, `_get_selective_visitors()` to `scanner.py`
2. Extract `ScanResult`, `ScanManifest` to `models.py` (or keep in scanner.py)
3. `scanner.py` imports visitors from temporary location

**Structure:**
```python
# scanner.py
class ADGStaticScanner:
    def __init__(self, config: ScannerConfig): ...
    def scan(self, file_path: Path, rel_path: str) -> ScanResult: ...
    def _get_visitors_for_mode(self, mode: ScanMode) -> list[type[_BaseVisitor]]: ...
```

### P1-REG: Declarative Visitor Registry

**Files:**
- `agentic_core/adg/extraction/registry.py` (new) — `VisitorSpec` dataclass + registry

**Structure:**
```python
@dataclass(frozen=True)
class VisitorSpec:
    cls: type[_BaseVisitor]
    modes: frozenset[str]  # "full", "structural_only", "selective"
    category: str  # "structural", "governance", "runtime_semantic", "l4_waves"
    emits_relations: frozenset[str]
    order: int

_VISITOR_REGISTRY: list[VisitorSpec] = [...]
```

### P1-POL: Scan Policy Extraction

**Files:**
- `agentic_core/adg/extraction/policy.py` (new) — Mode selection, file-path applicability

**Actions:**
1. Move `_get_cache_aware_scan_mode()`, `_get_selective_visitors()` logic to `policy.py`
2. Define `ScanModePolicy` with predicates for file-path matching

**Acceptance:**
- [ ] `scanner.py` contains no visitor class definitions
- [ ] `scanner.py` delegates visitor selection to `registry.py` + `policy.py`
- [ ] Behavior unchanged: same edges for same inputs

---

## Phase 2: Visitor Contract + Category Decomposition (P2)

### P2-BASE: Visitor Base Contract

**Files:**
- `agentic_core/adg/extraction/visitors/base.py` (new)

**Structure:**
```python
class _BaseVisitor(ast.NodeVisitor):
    @property
    def visitor_name(self) -> str: ...
    @property
    def emits_relations(self) -> frozenset[str]: ...
    @property
    def supports_modes(self) -> frozenset[str]: ...
    def applies_to(self, rel_path: str) -> bool: ...
    def run(self, tree: ast.AST, context: ScanContext) -> list[Edge]: ...
```

### P2-VIS: Visitor Category Decomposition

**Files (new):**
- `visitors/__init__.py` — public exports
- `visitors/structural/` — `_ImportVisitor`, `_ClassVisitor`, `_FunctionVisitor`
- `visitors/governance/` — `_GovernancePlaneVisitor`, `_L5ValidationProofVisitor`
- `visitors/l4_waves/` — `_UWGIngressGateVisitor`, `_MutationRecordAssemblyVisitor`, etc.

**Actions:**
1. Move each visitor class to appropriate category directory
2. Update imports in `static_scanner.py` to import from visitors/
3. Maintain backward compatibility during transition

**Final structure:**
```
agentic_core/adg/extraction/
├── scanner.py              # orchestration
├── registry.py             # declarative registration
├── policy.py               # mode selection
├── models.py               # ScanResult, Edge, ScanManifest
├── filters.py              # runtime edge filtering
├── visitors/
│   ├── __init__.py
│   ├── base.py             # _BaseVisitor contract
│   ├── structural/         # AST structure visitors
│   ├── governance/         # GG, G26, etc.
│   ├── runtime_semantic/   # G9, G19, G27, etc.
│   └── l4_waves/           # G34-G37 UWG visitors
└── utils.py                # shared helpers
```

---

## Phase 3: Helpers Consolidation + Filters (P3)

### P3-HELP: Symbol Parsing Helpers

**Files:**
- `visitors/base.py` — Move `_sym()`, `_extract_symbol()`, `_extract_name()`
- `utils.py` — Dotted-attribute extraction, call symbol parsing

**Actions:**
1. Extract all symbol resolution helpers to base class or utils
2. Ensure consistent tail/base comparison patterns
3. Add unit tests for helper functions

### P3-FILT: Runtime Filters Extraction

**Files:**
- `filters.py` — Runtime edge filtering logic currently embedded in scanner

---

## Phase 4: Test Reconstruction (P4)

### P4-TEST: Test Directory Restructure

**New structure:**
```
tests/adg/scanner_contracts/    # scan mode matrix, determinism
tests/adg/visitors/              # per-visitor golden tests
tests/adg/postpasses/            # violation propagation, cycles
tests/adg/fixtures/              # shared AST fixtures
```

### P4-VAL: Validation Harness

**Tests to add:**
- [ ] One golden test per visitor category
- [ ] One scan-mode matrix test (full, structural_only, selective)
- [ ] One determinism digest regression test
- [ ] One "no synthetic bootstrap leakage" test
- [ ] One "schema_util SSOT completeness" test

---

## Phase 5: Optimization (P5)

### P5-OPT: Scan-Mode Performance

**Actions:**
1. Benchmark cache-aware mode after architecture stable
2. Optimize selective visitor dispatch via registry metadata
3. Compare performance pre/post decomposition

---

## Success Criteria

| Metric | Target | Verification |
|--------|--------|------------|
| File size | `static_scanner.py` < 100KB (visitors extracted) | `wc -c` |
| Visitor count in monolith | 0 | grep -c "class.*Visitor" |
| Scanner tests | 19/19 pass | `pytest tests/adg/test_static_scanner.py` |
| Contract tests | 5/5 pass (one per category) | `pytest tests/adg/visitors/` |
| Determinism | Digest stable across 3 runs | `test_adg_digest_stable.py` |
| No-bootstrap-leakage | 0 synthetic edges in prod mode | custom test |

---

## Rollback Strategy

1. **Per-phase revert:** Git revert individual phase commits
2. **Full rollback:** Use `adg_rollback.py` to last known good ADG
3. **Behavioral checkpoint:** Golden digest frozen before P0; must match after P5

---

*Plan generated: 2026-04-02*  
*Reactivation trigger: File size 417KB (93% threshold)*  
*RCA reference: RCA_static_scanner_modularization_abandonment.md*
