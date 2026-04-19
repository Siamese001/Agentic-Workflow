# H3 — Contract Authority Decision

wave: H3
adg_snapshot: artifacts/adg/adg_indexed_04182026_1558.sqlite
adg_snapshot_timestamp: "04182026_1558"

## Scope

- `B7-G6-01` (`L_CONTRACTS` dead/unwired status)
- `B7-G6-02` (duplicate execution-trace ownership)

## H1 closure tests applied

### B7-G6-01

1. L_CONTRACTS status explicitly decided
2. decision reflected in ownership and residual matrices
3. no contradictory authority claims remain

### B7-G6-02

1. single execution-trace contract owner designated
2. duplicate ownership removed or bounded
3. downstream references aligned to owner

## Direct evidence

- `docs/wave_g/G2_service_wiring/seam_usage_report.md` reports `agentic_core/L_CONTRACTS/` as runtime-dead/unwired (historically archived-only importer evidence).
- ADG H3 check (`04182026_1558`) returns no import fan-in for `agentic_core/L_CONTRACTS/execution_trace.py` module node.
- `docs/wave_g/G6_taxonomy_cleanup/normalization_matrix.md` classifies:
  - `G6-S001` (`agentic_core/L_CONTRACTS/`) as orphan/vestigial blocker-class input,
  - `G6-S006` (`L2_execution/types/execution_trace_types.py` + `L3_orchestration/types/execution_trace_types.py`) as duplicate_needing_resolution.
- `docs/wave_g/G7_integrated_runtime_map/*` carries both `B7-G6-01` and `B7-G6-02` as unresolved contract-surface blockers.

## Surface classification (required enum)

| surface | classification | evidence_note |
|---|---|---|
| `agentic_core/L_CONTRACTS/` (including `execution_trace.py`) | deprecated_non_authority | direct evidence shows non-runtime authority posture (dead/unwired) |
| `agentic_core/L2_execution/types/execution_trace_types.py` | unresolved | duplicate authority still present with L3 peer surface |
| `agentic_core/L3_orchestration/types/execution_trace_types.py` | unresolved | duplicate authority still present with L2 peer surface |

## H3 closure-test outcomes

### B7-G6-01 outcome

- Test 1: **pass** (explicit decision made in H3: `deprecated_non_authority`)
- Test 2: **partial** (reflected in H3 decision artifact; still open in prior-wave matrices)
- Test 3: **partial/fail** (contradictory authority signal remains because contract-like L_CONTRACTS surface still exists in tree)

Result: **narrowed, not closed**.

### B7-G6-02 outcome

- Test 1: **fail** (no evidence-strong single owner can be designated without contradictory live duplicate posture)
- Test 2: **partial** (duplicate set is bounded to two known surfaces)
- Test 3: **fail** (no evidence bundle shows downstream reference alignment to one owner)

Result: **still open with narrowed ambiguity boundary**.

## Net decision

- `L_CONTRACTS` is explicitly treated as **deprecated_non_authority** for runtime contract authority.
- Execution-trace contract authority between L2 and L3 remains **unresolved** in H3.
