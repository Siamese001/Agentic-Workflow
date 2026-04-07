# Narrows Possible Burndown — Micro-Wave Plan [DEFERRED]

**Status**: DEFERRED (2026-04-06)
**Reason**: SVP Engineering decision — requires AST-based exception inference tooling for safe automation

---

This plan breaks down the 2,420 `narrows_possible` broad_exception_catch entries into layer-prioritized micro-waves for systematic file-by-file narrowing from `except Exception` to specific exception types.

## Context

- **Remaining entries**: 2,420 `narrows_possible` from `broad_exception_catch` classification
- **Inventory location**: `@C:\Git\Agentic-Workflow\artifacts\adg_analysis\broad_exception_catch_subcategorized.json`
- **Classification criteria**: Entries that don't re-raise and aren't teardown context — these are candidates for narrowing to specific exception types
- **Action required**: File-by-file narrowing (e.g., `except Exception` → `except (ValueError, OSError)`) based on what the function actually does

## Deferral Rationale (SVP Engineering)

**Risk Profile**:
- 2,420 manual exception narrowings across ~270 unique functions
- Each narrowing requires context analysis to determine correct exception types
- High regression risk if wrong exceptions specified
- Time-intensive (estimated 10-20 hours for full burn-down)

**Operational Complexity**:
- 20-wave micro-batch strategy adds ceremony without proportional safety
- Function-grouped review still requires manual pattern specification per function
- No automated validation that narrowed exceptions are correct

**Decision**: Defer until AST-based exception inference tooling exists. The narrows_possible entries are lower severity than teardown/has_reraise (already handled). Better to invest in automated analysis before attempting bulk narrowing.

**Required Tooling**:
- AST-based raise analysis to infer which exceptions each function actually raises
- Automated narrowing suggestions with confidence scores
- Validation that narrowed exceptions don't miss actual raise sites

## Wave Strategy (Original Plan)

**Layer priority order** (SVP Engineering principle: ops/tools first, then apps, then core):
1. L_TOOLS (tools/, ops_scripts/) — lower risk, infrastructure code
2. L_OPS (infrastructure/) — operational glue code
3. L_APP (apps_*/) — application-specific code
4. agentic_core/ — core logic, highest risk

**Wave sizing**: ~50 files per wave (manageable per session, allows focused review)
**Single-entry files**: Batched together in waves 5-10 (efficiency)
**Large files (6+ entries)**: Dedicated waves for each (need focused attention)

## Wave Breakdown (Estimates)

| Wave | Layer | Focus | Est. Files | Est. Entries |
|------|-------|-------|-----------|--------------|
| W5c.1 | L_TOOLS | tools/ | ~50 | ~150 |
| W5c.2 | L_TOOLS | ops_scripts/ | ~50 | ~200 |
| W5c.3 | L_OPS | infrastructure/ | ~50 | ~150 |
| W5c.4 | L_APP | apps_eval/ | ~30 | ~100 |
| W5c.5 | L_APP | apps_exec/ | ~30 | ~100 |
| W5c.6 | L_APP | apps_lic/ | ~20 | ~80 |
| W5c.7 | L_APP | apps_research/ | ~20 | ~80 |
| W5c.8 | L_APP | apps_rfp/ | ~20 | ~80 |
| W5c.9 | L_APP | apps_rg/ | ~30 | ~120 |
| W5c.10 | L_APP | apps_underwriting_ai/ | ~20 | ~60 |
| W5c.11 | L_APP | apps_shared/ | ~30 | ~100 |
| W5c.12 | Singletons | Batch single-entry files | ~200 | ~200 |
| W5c.13 | agentic_core/L0_routing | L0_routing/ | ~20 | ~80 |
| W5c.14 | agentic_core/L1_cognition | L1_cognition/ | ~30 | ~120 |
| W5c.15 | agentic_core/L2_execution | L2_execution/ | ~40 | ~160 |
| W5c.16 | agentic_core/L3_orchestration | L3_orchestration/ | ~20 | ~80 |
| W5c.17 | agentic_core/L4_state | L4_state/ | ~20 | ~80 |
| W5c.18 | agentic_core/L5_safety | L5_safety/ | ~30 | ~120 |
| W5c.19 | agentic_core/L6_system | L6_system/ | ~10 | ~40 |
| W5c.20 | agentic_core/shared | agentic_core/ misc | ~50 | ~200 |

**Total waves**: 20
**Total entries**: 2,420

## Artifacts (Preserved)

- Wave manifests: `@C:\Git\Agentic-Workflow\artifacts\adg_analysis\waves\W5c.1_tools.json`
- Function grouping: `@C:\Git\Agentic-Workflow\artifacts\adg_analysis\waves\W5c.1_grouped_by_function.txt`
- Wave generation script: `@C:\Git\Agentic-Workflow\tools\evidence\_generate_wave_manifest.py`
- Function grouping script: `@C:\Git\Agentic-Workflow\tools\evidence\_group_by_function.py`

## Next Steps (When Revisiting)

1. Build AST-based exception inference tool:
   - Parse each function body to identify `raise` statements
   - Map raised exception types to containing function
   - Generate narrowing suggestions: `except Exception` → `except (Type1, Type2, ...)`

2. Validate suggestions:
   - Cross-reference with actual raise sites
   - Flag functions that raise exceptions not in suggested catch list
   - Require manual review for low-confidence suggestions

3. Apply automated narrowing:
   - Dry-run mode first
   - Scoped tests per file
   - Guardian gate verification
