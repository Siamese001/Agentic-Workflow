# Waves 5 & 6: Coverage Expansion Analysis

**Date**: 2026-03-14
**Status**: 🔍 ANALYSIS COMPLETE
**Conclusion**: Different approach needed than Wave 4

---

## Current State

### Wave 5: `records_execution_trace`
- **Current**: 64 edges across 15 files
- **Distribution**: 56 in tests, 8 in production code
- **Coverage**: ~1% of modules

**Top Files**:
- `tests/adg/test_adg_gap_g7_g16.py`: 13 sites
- `tests/adg/test_adg_g7_g16_completeness_accuracy.py`: 12 sites
- `agentic_core/runtime/execution_trace.py`: 2 sites (infrastructure)

### Wave 6: `writes_through`
- **Current**: 98 edges across 13 files
- **Distribution**: 96 in tests, 2 in production code
- **Coverage**: ~1.5% of modules
- **Ratio**: Cannot calculate (no `mutates_state` edges in ADG)

**Top Files**:
- `tests/governance/test_stabilization_hardening_s1_s5.py`: 23 sites
- `tests/unit/agentic_core/L2_execution/enforcement/test_write_governor_mixin.py`: 18 sites
- `agentic_core/L2_execution/UniversalWriteGateway.py`: 1 site (infrastructure)

---

## Key Insight

**These are NOT guardrail edges** - they are infrastructure-emitted edges:

| Edge Type | How It's Created | Migration Approach |
|-----------|------------------|-------------------|
| `applies_guardrail` (Wave 4) | Guard check calls | ✅ Bulk AST injection |
| `records_execution_trace` (Wave 5) | Execution trace infrastructure | ❌ Requires trace instrumentation |
| `writes_through` (Wave 6) | Write-through gateway usage | ❌ Requires gateway adoption |

---

## Why Bulk Migration Won't Work

### Wave 5 Problem
`records_execution_trace` edges are emitted by:
- `ExecutionTrace.record()` calls in runtime infrastructure
- Trace context managers wrapping agent execution
- Not something we can inject via AST rewriting

**Example**:
```python
# This emits records_execution_trace edge:
with ExecutionTrace(trace_id=...) as trace:
    trace.record("agent_start", metadata={...})
    result = agent.execute()
    trace.record("agent_complete", result=result)
```

### Wave 6 Problem
`writes_through` edges are emitted by:
- UniversalWriteGateway (UWG) usage for state mutations
- Write-through pattern enforcement
- Requires refactoring state mutations to use UWG

**Example**:
```python
# This emits writes_through edge:
uwg = UniversalWriteGateway()
uwg.write(target="redis", key="foo", value="bar")  # Emits edge
```

---

## Recommended Approach

### Option 1: Infrastructure Expansion (High Effort)
**Wave 5**: Instrument more agent execution paths with `ExecutionTrace`
- Add trace context managers to uncovered agents
- Expand trace recording in L2/L3 orchestration layers
- **Effort**: 3-, requires careful integration

**Wave 6**: Refactor state mutations to use UniversalWriteGateway
- Identify direct Redis/DB writes
- Wrap with UWG write-through pattern
- **Effort**: 4-, high risk of breaking changes

### Option 2: Document Current State (Low Effort) ⭐ RECOMMENDED
- Accept current coverage levels (64 and 98 edges)
- Document that these edges require infrastructure adoption, not migration
- Create roadmap for future infrastructure expansion
- **Effort**: 

### Option 3: Targeted Expansion (Medium Effort)
**Wave 5**: Add execution trace to top 10-20 uncovered agents
- Focus on high-criticality agents (L5 safety, L3 orchestration)
- Manual instrumentation with ExecutionTrace context managers
- **Effort**: 2-

**Wave 6**: Convert top 10-20 state mutation sites to UWG
- Focus on critical state operations (config writes, cache updates)
- Manual refactoring to write-through pattern
- **Effort**: 2-

---

## Comparison to Wave 4

| Aspect | Wave 4 (Guardrails) | Waves 5 & 6 (Infrastructure) |
|--------|---------------------|------------------------------|
| Edge emission | Guard check calls | Infrastructure method calls |
| Migration method | AST injection | Manual instrumentation |
| Automation | 100% automated | Requires manual integration |
| Risk | Low (additive only) | Medium-High (refactoring) |
| Validation | ADG edge count | Runtime behavior + ADG |
| Effort per file | ~ | ~15- |

---

## Recommendation

**Accept current state and document** (Option 2):

1. Waves 5 & 6 target infrastructure-emitted edges, not injectable patterns
2. Current coverage (64 and 98 edges) represents existing infrastructure usage
3. Expansion requires manual instrumentation/refactoring, not bulk migration
4. ROI is lower than Wave 4 (guardrails protect against security risks)
5. Infrastructure expansion should be driven by feature needs, not coverage metrics

**If user wants to proceed**: Use Option 3 (targeted expansion) with explicit file selection and manual review per change.

---

## Next Steps (if proceeding with Option 3)

### Wave 5 Targeted Expansion
1. Identify top 10 high-criticality agents without execution trace
2. Add `ExecutionTrace` context managers manually
3. Validate trace emission in test runs
4. Regenerate ADG and verify edge increase

### Wave 6 Targeted Expansion
1. Identify top 10 direct state mutation sites
2. Refactor to use UniversalWriteGateway
3. Validate write-through behavior in tests
4. Regenerate ADG and verify edge increase

**Estimated Total Effort**: 4- (vs. Wave 4's 2- for 490 edges)

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

