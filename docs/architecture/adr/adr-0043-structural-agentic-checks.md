# ADR-0043: Structural Conformance & Agentic Anti-Pattern Checks

**Status**: Accepted  
**Date**: 2026-04-08  
**Deciders**: @Siamese001  
**Context**: ADG P0-P3 Structural Conformance & Agentic Anti-Pattern Expansion (Waves 1-6)

---

## Context

The ADG (AST Dependency Graph) generation pipeline had existing violation detection for:
- **P0**: Layer violations, circular imports, dynamic execution
- **P1**: HIGH-severity antipatterns (broad exception catch, silent swallow, etc.)
- **P2**: MEDIUM-severity antipatterns
- **P3**: LOW-severity style/warnings

However, these were limited to AST-level pattern matching. The architecture lacked:
1. **Structural conformance checks** — verifying that the codebase conforms to architectural contracts (layer gravity, lifecycle phases, write isolation, choke-points)
2. **Agentic anti-pattern checks** — detecting emergent patterns in agentic systems (text-to-action paths, phase bypasses, provider leaks, sprawl, dormancy)

## Decision

Implement 25 graph-query-based checks split across two violation classes:

### Structural Conformance (SC-1 through SC-8)

| Check | Severity | Description |
|-------|----------|-------------|
| SC-1 | P0 | Gravity import / illegal layer reach |
| SC-2 | P0 | L2 execution lifecycle conformance |
| SC-3 | P0 | UWG-only durable write conformance |
| SC-4 | P0 | Capability/tool/provider choke-point |
| SC-5 | P1 | Agentic spine completeness |
| SC-6 | P1 | L0/L1/L6 role purity |
| SC-7 | P1 | Grounding contract / C0-PA separation |
| SC-8 | P1 | Trace/replay/eval surface coverage |

### Agentic Anti-Patterns (AP-1 through AP-17)

| Check | Severity | Description |
|-------|----------|-------------|
| AP-1 | P0 | Unsafe text-to-action path |
| AP-2 | P0 | L2 phase bypass |
| AP-3 | P0 | Provider/tool bypass |
| AP-4 | P0 | Direct durable write breach |
| AP-5 | P1 | Tool overlap / ambiguous surfaces |
| AP-6 | P1 | Premature multi-agent sprawl |
| AP-7 | P1 | Duplicate specialization |
| AP-8 | P1 | Missing trace/eval on action paths |
| AP-9 | P1 | Infrastructure spread / service locator drift |
| AP-10 | P1 | Live/future mutation confusion |
| AP-11 | P2 | Poorly scoped work contracts |
| AP-12 | P2 | Prompt scatter |
| AP-13 | P2 | Retry/heal without exit criteria |
| AP-14 | P2 | Retrieval without evidence contract |
| AP-15 | P3 | Agent count outrunning tool surfaces |
| AP-16 | P3 | Dormant infrastructure |
| AP-17 | P3 | Agentic semantic precision gaps |

### Key Design Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| All new checks start **disabled** | `enabled: false` | Prevents ADG breakage during rollout |
| When enabled, checks start in **audit mode** | `audit_mode: true` | Logs violations without blocking |
| Graph queries on **existing edges** | No scanner changes | Graph-first, minimal blast radius |
| `violation_class` added at **gate time** | Not scanner-time | SC/AP checks are post-scan graph queries |
| Separate gate functions | `_check_structural_conformance` + `_check_agentic_antipatterns` | Clean separation from existing P0/P1/P2 gates |
| Config-driven per-check toggle | `artifacts/adg/sc_ap_config.json` | Incremental rollout and per-check promotion |
| Auto-migration for `violation_class` column | `_ensure_violation_class_column()` | Backward-compatible with older DBs |

## Architecture

```
generate_full_adg.py
  ├── Tier-2b: _check_structural_conformance(sqlite_path, config_path)
  │     ├── _SC_CHECK_DISPATCH: SC-1..SC-8 → query functions
  │     └── Inserts violations with violation_class='structural_conformance'
  ├── Tier-2b: _check_agentic_antipatterns(sqlite_path, config_path)
  │     ├── _AP_CHECK_DISPATCH: AP-1..AP-17 → query functions
  │     └── Inserts violations with violation_class='agentic_antipattern'
  └── reports.py: _print_defect_table
        ├── SC~/AP~ audit rows in defect table
        └── by_class burndown breakdown
```

### Promotion Workflow

```
1. Enable check: set enabled=true in sc_ap_config.json
2. Observe in audit mode (logs violations, no blocking)
3. When violations reach 0 or all exempted:
   - Set audit_mode=false, promoted_date=<date>
   - Check now blocks ADG generation on violation
```

## Consequences

### Positive
- **25 architectural checks** covering structural contracts and agentic anti-patterns
- **Zero impact on existing pipeline** — all checks disabled by default
- **Incremental promotion** — each check can be independently enabled/promoted
- **Burndown visibility** — `by_class` breakdown in burndown JSON
- **175 tests** covering all checks, edge cases, and integration with live DB
- **Schema migration** — `_ensure_violation_class_column` handles older DBs

### Negative
- **4 new P2 antipattern detections** in gate code (ratchet ceiling updated 1364→1368)
- **Integration tests take ~5 min** due to live DB queries (all 25 checks × full graph)

### Risks
- Checks are disabled by default — value only realized when progressively enabled
- Some checks (SC-5 spine, AP-15 ratio) may need threshold tuning for the specific codebase

## Files

| File | Role |
|------|------|
| `tools/generate/validation/gates.py` | 25 query functions, dispatch tables, gate orchestration |
| `tools/generate/validation/__init__.py` | Public exports |
| `tools/generate/reporting/reports.py` | Defect table SC/AP rows, burndown by_class fix |
| `tools/generate/test_generate_full_adg_failfast.py` | 166 unit tests |
| `tools/generate/test_sc_ap_integration.py` | 9 integration tests (live DB) |
| `artifacts/adg/sc_ap_config.json` | Per-check enable/audit/promote config |
| `docs/architecture/adr/adr-0043-structural-agentic-checks.md` | This ADR |
| `docs/reference/sc_ap_check_definitions.md` | Check definitions reference |
