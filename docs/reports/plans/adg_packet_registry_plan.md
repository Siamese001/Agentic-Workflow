# ADG Packet Registry Plan — Runtime-Readiness and Bridge Call Pattern
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: PacketRegistry, builder entrypoints, runtime call pattern, scatter, CI implications

---

## 1. Executive Summary

The `PacketRegistry` (`packets/registry.py`) and `build_packet()` dispatcher (`packets/builders.py`) are **runtime-ready for the C0→PA bridge without any registry or builder changes.** The `_assemble()` helper is the single integration point: it accepts pre-built `EvidenceItem` lists, applies shaping, budgeting, and constructs a `PromptEnvelope`. The bridge calls `_assemble()` directly (bypassing per-builder retrieval adapter calls), which is the correct and cleanest integration pattern. No new packet families are required — the existing 8 families are designed for ADG-analysis contexts, and the bridge selects among them based on request type.

**Firm decisions from this review:**
1. **No new packet families** — the 8 existing families cover the design space; bridge selects applicable type.
2. **No registry changes** — `TEMPLATES`, `get_template()`, `list_packet_types()` unchanged.
3. **No builder changes** — all 8 builder functions unchanged; bridge calls `_assemble()` directly.
4. **No `build_packet()` dispatcher changes** — bridge does not route through the CLI dispatcher.
5. **One deferred conditional change** — `"c0_span"` SourceType (not required for initial bridge).

---

## 2. Registry Surface Audit

### 2.1 `TEMPLATES` dict — 8 entries, fully registered

| Key | Builder | Must-use sources | Optional sources | Budget |
|-----|---------|-----------------|-----------------|--------|
| `determinism_rca` | `build_determinism_rca` | `provenance_report`, `closure_report`, `sqlite` | `graph_db` | 8,000 |
| `p0_failure` | `build_p0_failure` | `sqlite`, `closure_report`, `sc_ap_config` | `graph_db` | 6,000 |
| `ratchet_review` | `build_ratchet_review` | `ratchet`, `burndown`, `sqlite` | `structural` | 6,000 |
| `unknown_unresolved_triage` | `build_unknown_unresolved_triage` | `layer_coverage_report`, `sqlite` | `graph_db` | 6,000 |
| `hotspot_investigation` | `build_hotspot_investigation` | `sqlite`, `structural` | `graph_db` | 8,000 |
| `infrastructure_boundary` | `build_infrastructure_boundary` | `infra_view`, `sqlite` | `graph_db` | 6,000 |
| `graph_path_explanation` | `build_graph_path_explanation` | `graph_db`, `sqlite` | `structural` | 6,000 |
| `executive_summary` | `build_executive_summary` | `snapshot`, `burndown`, `closure_report`, `ratchet` | `structural`, `graph_db` | 4,000 |

**Registry integrity:** Every key in `TEMPLATES` has exactly one entry in the `dispatch` dict in `build_packet()`, and exactly one builder function. **No orphan templates. No orphan builders. No registry/builder mismatch.**

**Exception:** `build_packet()` hard-codes special-case handling for `graph_path_explanation` (requires `from_node`/`to_node`) and `hotspot_investigation` (accepts `top_n`). These are builder-parameter variances, not registry defects.

### 2.2 `VALID_PACKET_TYPES` — computed correctly

`VALID_PACKET_TYPES = frozenset(TEMPLATES.keys())` — computed from `TEMPLATES`. Adding a new template automatically updates `VALID_PACKET_TYPES` and `list_packet_types()`. No manual sync needed.

### 2.3 `get_template()` — clean

Raises `ValueError` for unknown packet type. Returns immutable `PacketTemplate` dataclass. No side effects. Thread-safe (read-only registry).

---

## 3. Builder Entrypoints — Structural Analysis

### 3.1 `_assemble()` — The Single Convergence Point

**Signature:**
```python
def _assemble(
    template: PacketTemplate,
    must_items: list[EvidenceItem],
    opt_items: list[EvidenceItem],
    task_block: str,
    replay_extras: dict[str, Any] | None = None,
) -> PromptEnvelope
```

**Internal sequence:**
1. `shape_evidence(all_items, must_use_sources=template.must_use_sources)` → `EvidenceBundle`
2. Split items into `must_dicts` / `opt_dicts` (by `must_items`/`opt_items` parameter, not by `is_derived` flag)
3. Estimate fixed token usage (`system_block + policy_block + task_block`)
4. `apply_budget(must_dicts, opt_dicts, fixed_tokens, template.token_budget)` → `BudgetResult`
5. Build `replay` dict from item `snapshot_id`, `commit_sha`, `artifact_digest`, `source_artifact`
6. Merge `replay_extras` into `replay` dict
7. Compute `evidence_status` and `assembly_result` from `bundle.coverage_score` and `budget_result.overflow_action`
8. Build `PromptAssemblyStatus`
9. Augment `abstain_instructions` if `coverage < 0.3`
10. Augment `refine_instructions` if `budget_result.summary_note` is non-empty
11. Return `PromptEnvelope`

**Bridge integration point:** The bridge calls `_assemble()` with pre-built `must_items` (C0 spans) instead of invoking retrieval adapters. This bypasses steps 1–N of individual builder functions. `_assemble()` itself requires no change.

**Important design note — must/opt split:** `_assemble()` separates `must_dicts` from `opt_dicts` based on the **input parameter lists** (`must_items` vs `opt_items`), not on `EvidenceItem.is_derived`. Error-flagged items are excluded from both (`if not item.data.get("error")`). For the C0 bridge: all C0 spans go into `must_items` (canonical retrieval = must-use). `opt_items=[]`. This is correct.

### 3.2 Per-Builder Functions — Roles and Boundaries

Each builder function has exactly one responsibility: fetch evidence via retrieval adapters, split into `must_items`/`opt_items`, define the `task_block`, and call `_assemble()`. They do not perform:
- Direct SQL queries (all via adapters)
- Prompt string construction (all via `_assemble()`)
- Token counting (all via `token_budgeter.py`)
- Coverage computation (all via `evidence_shaper.py`)

**No builder duplicates logic from another builder.** All shared logic is in `_assemble()`. This is clean.

### 3.3 `build_packet()` Dispatcher — Entry Points

The `build_packet()` dispatcher is the public API for CLI and external callers. For the C0 bridge, it is **not the right entry point** because:
- `build_packet()` always invokes per-builder retrieval adapters (reads from disk)
- The bridge has already fetched evidence via C0
- The bridge needs to inject pre-built `EvidenceItem` objects, not trigger new retrieval

**Bridge call pattern:** The adapter calls `_assemble()` directly, importing it from `builders.py`. This is an internal import from the same package — fully permitted. The bridge is not a CLI caller.

---

## 4. Prompt Scatter Findings — Inside PA Package

### 4.1 Shared Block Duplication — NONE

`_SHARED_POLICY`, `_SHARED_ABSTAIN`, `_SHARED_REFINE` defined once each. Used by reference in all 8 `PacketTemplate` constructors. No inline copies. **Clean.**

### 4.2 Task Block Duplication — NONE

Task blocks are per-builder string literals defined inside each builder function. They are semantically distinct. No cross-builder duplication. **Clean.**

### 4.3 Builder Logic Duplication — NONE

Evidence fetching patterns are similar across builders (fetch → split must/opt → call `_assemble()`), but there is no copy-paste of assembly logic — all assembly routes through `_assemble()`. **Clean.**

### 4.4 Registry/Builder Mismatch — ONE PRE-EXISTING

| Location | Mismatch | Effect |
|----------|---------|--------|
| `infrastructure_boundary` | `PacketTemplate.must_use_sources = ["infra_view", "sqlite"]` but `build_infrastructure_boundary()` fetches `sq.fetch_infra_wiring_views()` with `source_type="sqlite"` — not `"infra_view"` | `_compute_coverage()` will not find `"infra_view"` in present sources → `coverage_score` computed as `0.5` (1 of 2 must-use sources present) → `weak_support=True` → `evidence_contract_status="partial"` |
| | | **This is pre-existing and low-severity. The infra data is present — it just has the wrong source_type label.** Not introduced by bridge design. |

**Recommended future fix (not in scope for this stage):** Either update `PacketTemplate.must_use_sources` to `["sqlite"]` for `infrastructure_boundary`, or have `fetch_infra_wiring_views()` set `source_type="infra_view"`. The second is cleaner.

### 4.5 System Block Wording Drift — NONE

All 8 system blocks follow the `"You are an ADG <role>."` pattern. Consistent grammar, consistent scope declaration. No drift.

### 4.6 `cli.py` Scatter — NONE

`cli.py` has zero prompt construction logic. It dispatches exclusively to `build_packet()`. The guardian-annotated `except Exception` at line 153 is correctly annotated: `# guardian: allow-broad-exception -- CLI top-level catch for user-facing error messages`. **Clean.**

---

## 5. No New Packet Families Required

**Default answer: No new packet families.**

**Evidence:**
- The 8 existing families cover all ADG analysis contexts (provenance, violations, ratchet, unknown, hotspot, infra, path, summary)
- The bridge does not introduce a new analysis context — it introduces a new *evidence source* (C0 spans)
- The existing packet families handle the bridge evidence via the correct abstain path when C0 spans do not match the packet's must-use source types
- For packets where C0 evidence is contextually appropriate (`graph_path_explanation`, `executive_summary`), the existing templates accept it without modification
- A "c0_retrieval" packet type would be redundant with the existing executive_summary or graph_path_explanation packets for most use cases

**When a new packet family would be warranted:** Only if a C0 retrieval scenario produces evidence that requires a fundamentally different output schema, task framing, and source mix that cannot be served by any existing family. No such scenario exists in the current design.

---

## 6. Future Runtime Call Pattern — Design (Not Code)

### 6.1 Full Sequence

```
[L3 Orchestration Dispatcher]
    │
    ├─ 1. Receive request (task context + packet_type selection)
    ├─ 2. Call C0 retrieval engine
    │      → C0EvidenceContract (validated, HMAC-sealed)
    │
    ├─ 3. Call c0_to_pa_adapter.translate(contract, packet_type)
    │      ├─ abstain gate (if abstain_hint → return empty bundle immediately)
    │      ├─ CitedSpan → EvidenceItem translation
    │      ├─ contradiction pre-population
    │      ├─ shape_evidence(items, must_use_sources=[])
    │      ├─ bridge merger (coverage override, gap merge, confidence_band)
    │      └─ return (EvidenceBundle, replay_extras dict)
    │
    ├─ 4. Select template: get_template(packet_type)
    │
    ├─ 5. If abstain_hint=True:
    │      → build stub PromptEnvelope with abstain_instructions only
    │      → set assembly_result="fail"
    │      → STOP, return to caller
    │
    ├─ 6. Call _assemble(
    │         template=template,
    │         must_items=bundle.items,
    │         opt_items=[],
    │         task_block=<request-specific task description>,
    │         replay_extras=replay_extras
    │     )
    │      → PromptEnvelope (sealed)
    │
    ├─ 7. Return PromptEnvelope to L2 dispatcher
    │
    └─ 8. (Optional audit) Write envelope.to_json() to
           artifacts/adg/packets/<packet_type>_<packet_id>.json
```

### 6.2 Adapter Output → Builder Input Mapping

| Adapter output | Builder input |
|---------------|--------------|
| `bundle.items` (list[EvidenceItem]) | `must_items` parameter of `_assemble()` |
| `[]` (no derived evidence from C0) | `opt_items` parameter of `_assemble()` |
| `<request-specific task description>` | `task_block` parameter of `_assemble()` |
| `{"retrieval_id": ..., "request_id": ..., "evidence_hmac": ..., "coverage_score": ..., "abstain_hint": ..., "confidence_band": ...}` | `replay_extras` parameter of `_assemble()` |
| `get_template(packet_type)` | `template` parameter of `_assemble()` |

### 6.3 Registry Selection — Design Rules

The L3 dispatcher selects `packet_type` based on the current request context. Selection rules (design, not code):

| Request context | Recommended packet type |
|----------------|------------------------|
| Request concerns a specific violating path | `graph_path_explanation` |
| Request concerns overall run status | `executive_summary` |
| Request concerns P0 hard failures | `p0_failure` |
| Request concerns ratchet/anti-pattern trends | `ratchet_review` |
| Request concerns hotspots or structural risk | `hotspot_investigation` |
| Request concerns infra wiring | `infrastructure_boundary` |
| Request concerns unknown/unresolved modules | `unknown_unresolved_triage` |
| Request concerns digest mismatches | `determinism_rca` |
| No clear match | `executive_summary` as default fallback |

**Important:** When C0 evidence does not match a packet's `must_use_sources`, the shaper will compute low coverage → abstain path fires → `assembly_result="fail"`. L3 dispatcher should select packet type carefully to maximize evidence/template alignment. For initial bridge implementation, `executive_summary` is the safest default because its must-use sources are the most broadly available and its output schema is the most generic.

### 6.4 Envelope Return Shape — Confirmed Stable

`PromptEnvelope.to_dict()` is the canonical return shape. No new serialization format needed. `replay_metadata` carries all C0 identity fields. `assembly_status` carries the audit trail. Both are already included in `to_dict()`.

### 6.5 Artifact Materialization Point

**Location:** `artifacts/adg/packets/<packet_type>_<packet_id>.json`

**Writer:** L3 orchestration dispatcher (not PA)  
**Format:** `envelope.to_json(indent=2)` — already implemented  
**When:** After `_assemble()` returns, before returning to L2  
**Condition:** Only when `assembly_result != "fail"` (no failed packets on disk)

**File naming convention (design):**
```
artifacts/adg/packets/
    executive_summary_abc123def456.json
    graph_path_explanation_7b8c9d0e1f2a.json
```
`<packet_id>` is the first 16 chars of SHA-256 over `(packet_type, replay_metadata)` — already computed by `PromptEnvelope.__post_init__()`.

---

## 7. Minimal Additive Changes — Summary

| Change | File | Type | Blocking? | When |
|--------|------|------|-----------|------|
| New `c0_to_pa_adapter.py` | `agentic_core/L3_orchestration/adapters/` | New module | **YES — bridge requires this** | Initial implementation |
| Add `"c0_span"` to `SourceType` Literal | `tools/adg/prompt_assembly/contracts.py` | Additive type change (1 line) | No | After first iteration |
| `fetch_infra_wiring_views()` source_type fix | `tools/adg/prompt_assembly/retrieval/adapters.py` | Bug fix (1 line) | No | Pre-existing bug, separate PR |
| E21 violation count → CI hard-block | `ops_scripts/ci/adg_gates/gate_p0_authority.py` | Gate logic addition | No | Future CI phase |
| `evidence_hmac` presence gate on `packets/` dir | `ops_scripts/ci/adg_gates/` | New gate module | No | Future CI phase |

**Zero changes to:**
- `packets/registry.py` ← no new templates, no template modifications
- `packets/builders.py` ← no new builders, no `_assemble()` changes
- `contracts.py` (except optional `SourceType`) ← no field additions
- `budgeting/token_budgeter.py` ← no changes
- `shaping/evidence_shaper.py` ← no changes
- `cli.py` ← no changes
- `c0_evidence_contract_types.py` ← no changes

---

## 8. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|---------|-----------|
| Bridge dispatcher calls `build_packet()` instead of `_assemble()` directly, triggering retrieval adapters that read disk | HIGH — double-fetch, incorrect evidence mix | Explicitly document: bridge calls `_assemble()`, not `build_packet()`. `build_packet()` is CLI-only. |
| `replay_extras` keys collide with existing `replay` dict keys | MEDIUM — silent overwrite via `dict.update()` | Existing `replay` keys: `snapshot_ids`, `commit_shas`, `artifact_digests`, `source_artifacts`. C0 extras: `retrieval_id`, `request_id`, `evidence_hmac`, `coverage_score`, `abstain_hint`, `confidence_band`. **No collision confirmed.** |
| New packet type accidentally added to `TEMPLATES` without corresponding builder | LOW — `build_packet()` dispatch dict would miss it → `KeyError` at runtime | The dispatch dict in `build_packet()` must be kept in sync with `TEMPLATES`. Enforce via test: `assert set(dispatch.keys()) == set(TEMPLATES.keys())`. |
| `graph_path_explanation` called by bridge without `from_node`/`to_node` | MEDIUM — task block includes empty node references, replay_metadata has empty node fields | Bridge dispatcher must supply `from_node`/`to_node` via `replay_extras` when selecting this packet type. |
| C0 spans with very large `text_snippet` exhaust the token budget silently | MEDIUM — `abstained` overflow without clear explanation | Adapter truncates `text_snippet` to ≤512 chars; logs truncation as gap string in `EvidenceBundle.gaps`. |
| L3 dispatcher writes failed packets (`assembly_result="fail"`) to disk | LOW — misleading audit trail | Only write to `artifacts/adg/packets/` when `assembly_result != "fail"`. |
| `packets/` directory grows unbounded with runtime-written envelopes | LOW — disk usage | Future gate: rotate `packets/` files older than N days. Out of scope for initial bridge. |

---

## 9. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `_assemble()` is importable directly by the bridge adapter (not restricted to builders.py internal use) | **Confirmed** — it is a module-level function, not private (`_` prefix by convention but not by Python import restriction) |
| `get_template()` is importable by the bridge adapter from `packets/registry.py` | **Confirmed** — public API |
| No test enforces that only `build_packet()` may call `_assemble()` (i.e., no private-method enforcement) | **Confirmed** — Python has no private enforcement for functions starting with `_`; convention only |
| `infrastructure_boundary` source_type mismatch is pre-existing and known to team | **Confirmed from code** — not a bridge concern |
| The L3 orchestration dispatcher module exists but is not in scope for this design | **Assumed** — dispatcher lifecycle is out of scope |
| `artifacts/adg/packets/` directory exists (created by infrastructure) | **Confirmed** — directory present, currently empty |
| No existing test asserts `set(TEMPLATES.keys()) == set(dispatch.keys())` in `build_packet()` | **Inferred** — no test files were in scope for this review; recommended as a future test |
