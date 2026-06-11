---
status: Archived
do_not_execute: true
memorialized: true
source_surface: docs_reports_plans
source_key: docs-reports
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\docs\\reports\\plans\\adg_evidence_contract.md'
original_relative_path: 'adg_evidence_contract.md'
source_sha256: fb4504d3f112f66786bf2e1808306b646a1f8399d6cf775d80e40fb0a042683f
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Evidence Contract — C0→PA Bridge Field Mapping
**Stage 1 Design — No code changes**
**Date:** 2026-04-11 | Scope: runtime bridge from `C0EvidenceContract` to `PromptEnvelope`

---

## 1. Executive Summary

The L3 C0 retrieval contract (`C0EvidenceContract`) and the tool-layer prompt assembly contracts (`EvidenceItem`, `EvidenceBundle`, `PromptEnvelope`, `PromptAssemblyStatus`) are architecturally aligned in intent but **have no shared field vocabulary or integration path**. The bridge is a **translation adapter** — a new module that sits at the L3/tool boundary, accepts a validated `C0EvidenceContract`, and emits a shaped `EvidenceBundle` that the existing `packets/builders.py` dispatcher can consume without modification. No new packet families are needed. No existing contract fields need to change. The adapter is the only missing piece.

**Architecture law preserved throughout:**
- C0 retrieves only → produces `C0EvidenceContract`
- Adapter translates only → no retrieval, no packet logic
- PA packages only → `build_packet()` unchanged

---

## 2. Confirmed Current Contracts

### 2.1 Runtime Side (L3 — C0 retrieval plane)

**`CitedSpan`** — `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py`

| Field | Type | Semantics |
|-------|------|-----------|
| `span_id` | `str` | Unique identifier for this retrieved span |
| `source_ref` | `str` | Reference to the source document/artifact |
| `text_snippet` | `str` | The actual retrieved text |
| `relevance_score` | `float` | Retrieval relevance [0.0–1.0] |
| `chunk_hash` | `str` | Hash of the chunk content (used in HMAC computation) |

**`C0EvidenceContract`** — same file

| Field | Type | Semantics |
|-------|------|-----------|
| `retrieval_id` | `str` | UUID of this retrieval pass |
| `request_id` | `str` | ID of the upstream request this evidence serves |
| `coverage_score` | `float` | Fraction of request covered by retrieved evidence [0.0–1.0] |
| `abstain_hint` | `bool` | If True, PA must emit ABSTAIN; auto-set when `coverage_score < 0.30` |
| `cited_spans` | `tuple[CitedSpan, ...]` | All retrieved evidence spans (frozen) |
| `evidence_hmac` | `str` | HMAC-SHA256 over `request_id + sorted(chunk_hashes)` |

**Abstain threshold constant:** `_ABSTAIN_COVERAGE_THRESHOLD = 0.30`

---

### 2.2 Tool-Layer PA Side (`tools/adg/prompt_assembly/contracts.py`)

**`EvidenceItem`**

| Field | Type | Default | Semantics |
|-------|------|---------|-----------|
| `source_artifact` | `str` | required | Artifact filename (e.g., `adg_indexed_04102026_1817.sqlite`) |
| `source_type` | `SourceType` | required | One of: `sqlite`, `json_report`, `graph_db`, `infra_view`, `ratchet`, `structural` |
| `snapshot_id` | `str` | required | Timestamp extracted from artifact filename |
| `commit_sha` | `str` | `""` | Git commit SHA of the ADG run |
| `scanner_digest` | `str` | `""` | Scanner digest from provenance report |
| `artifact_digest` | `str` | `""` | SHA-256 of the artifact file |
| `row_references` | `list[str]` | `[]` | Row-level references (e.g., `edges:violates:0`) |
| `cited_spans` | `list[str]` | `[]` | Span IDs for cross-reference |
| `support_score` | `float` | `1.0` | Per-item quality/confidence score |
| `coverage_score` | `float` | `1.0` | Per-item coverage fraction |
| `is_derived` | `bool` | `False` | True for GraphDB items |
| `freshness` | `str` | `""` | ISO-8601 timestamp of fetch |
| `data` | `dict[str, Any]` | `{}` | The actual evidence payload |

**`ContradictionFlag`**

| Field | Type | Default |
|-------|------|---------|
| `field_name` | `str` | required |
| `source_a` | `str` | required |
| `value_a` | `Any` | required |
| `source_b` | `str` | required |
| `value_b` | `Any` | required |
| `severity` | `Literal["minor", "major"]` | `"minor"` |
| `description` | `str` | `""` |

**`EvidenceBundle`**

| Field | Type | Default |
|-------|------|---------|
| `items` | `list[EvidenceItem]` | `[]` |
| `coverage_score` | `float` | `0.0` |
| `contradiction_status` | `Literal["none","minor","major"]` | `"none"` |
| `contradictions` | `list[ContradictionFlag]` | `[]` |
| `gaps` | `list[str]` | `[]` |
| `freshness` | `str` | `""` |
| `weak_support` | `bool` | `False` |

**`PromptEnvelope`** (10-block ordered structure)

| Field | Type | Notes |
|-------|------|-------|
| `packet_type` | `str` | Required; must match a `TEMPLATES` key |
| `packet_id` | `str` | Auto-generated SHA-256[:16] from type+replay metadata |
| `schema_version` | `str` | `"1.0.0"` |
| `system_block` | `str` | From `PacketTemplate.system_block` |
| `policy_block` | `str` | Shared `_SHARED_POLICY` |
| `task_block` | `str` | Per-invocation task description |
| `must_use_evidence` | `list[dict]` | Serialized canonical `EvidenceItem` objects |
| `optional_evidence` | `list[dict]` | Serialized derived `EvidenceItem` objects |
| `contradiction_flags` | `list[dict]` | Serialized `ContradictionFlag` objects |
| `abstain_instructions` | `str` | From template |
| `refine_instructions` | `str` | From template |
| `output_schema` | `dict` | Per-type typed JSON schema |
| `replay_metadata` | `dict` | Provenance metadata for deterministic replay |
| `assembly_status` | `PromptAssemblyStatus \| None` | Assembly audit trail |

**`PromptAssemblyStatus`**

| Field | Type | Default |
|-------|------|---------|
| `packet_type` | `str` | required |
| `packet_id` | `str` | `""` |
| `input_artifacts` | `list[str]` | `[]` |
| `evidence_contract_status` | `Literal["complete","partial","empty"]` | `"empty"` |
| `contradiction_status` | `Literal["none","minor","major"]` | `"none"` |
| `token_budget_status` | `Literal["within_budget","trimmed","split"]` | `"within_budget"` |
| `overflow_action` | `Literal["none","summarized","narrowed","split","abstained"]` | `"none"` |
| `assembly_result` | `Literal["pass","fail","partial"]` | `"pass"` |
| `replay_metadata` | `dict` | `{}` |
| `assembly_timestamp` | `str` | Auto ISO-8601 UTC |

---

## 3. Field-by-Field Mapping Matrix

### 3.1 CitedSpan → EvidenceItem

| `CitedSpan` field | Mapping type | Target in `EvidenceItem` | Translation rule |
|-------------------|-------------|--------------------------|-----------------|
| `span_id` | **DIRECT** | `cited_spans: list[str]` | Append `span_id` to `cited_spans` list |
| `source_ref` | **DERIVED** | `source_artifact: str` | Map `source_ref` → `source_artifact`; derive `source_type` by inspecting `source_ref` extension/prefix |
| `text_snippet` | **DIRECT** | `data["text_snippet"]` | Place verbatim inside `data` dict |
| `relevance_score` | **DIRECT** | `support_score: float` | 1-to-1; both are [0.0–1.0] quality signals |
| `chunk_hash` | **DIRECT** | `row_references: list[str]` | Append `chunk_hash` as a row reference |
| *(no field)* | **MISSING in C0** | `source_type: SourceType` | Adapter must classify — inspect `source_ref` (e.g., `.sqlite` → `"sqlite"`, `.json` → `"json_report"`) |
| *(no field)* | **MISSING in C0** | `snapshot_id: str` | Derive from parent `C0EvidenceContract.retrieval_id` or from `source_ref` filename |
| *(no field)* | **MISSING in C0** | `commit_sha: str` | Carry forward from `PromptEnvelope.replay_metadata.commit_sha` if available |
| *(no field)* | **MISSING in C0** | `scanner_digest: str` | Leave `""` — runtime retrieval has no scanner digest |
| *(no field)* | **MISSING in C0** | `artifact_digest: str` | Leave `""` — C0 does not hash artifact files |
| *(no field)* | **MISSING in C0** | `coverage_score: float` | Set from parent `C0EvidenceContract.coverage_score` (same value for all spans) |
| *(no field)* | **MISSING in C0** | `is_derived: bool` | Always `False` — C0 spans are canonical retrieval, not graph-derived |
| *(no field)* | **MISSING in C0** | `freshness: str` | Set to ISO-8601 timestamp at translation time |

**Conflict:** `CitedSpan` carries `text_snippet` (raw text), while `EvidenceItem.data` is typed `dict[str, Any]`. The adapter wraps it: `data={"text_snippet": span.text_snippet, "source_ref": span.source_ref}`.

---

### 3.2 C0EvidenceContract → EvidenceBundle

| `C0EvidenceContract` field | Mapping type | Target in `EvidenceBundle` | Translation rule |
|---------------------------|-------------|--------------------------|-----------------|
| `coverage_score` | **DIRECT** | `coverage_score: float` | 1-to-1 |
| `abstain_hint=True` | **DERIVED** | `weak_support=True` + `gaps` | When `abstain_hint=True`, set `weak_support=True` and append `"abstain_hint:c0_coverage_below_threshold"` to `gaps` |
| `cited_spans` | **DERIVED** | `items: list[EvidenceItem]` | Each `CitedSpan` becomes one `EvidenceItem` via §3.1 mapping |
| `evidence_hmac` | **RUNTIME-ONLY** | `replay_metadata` only | Do not map to `EvidenceBundle`; forward to `PromptEnvelope.replay_metadata.evidence_hmac` |
| `retrieval_id` | **RUNTIME-ONLY** | `replay_metadata` only | Forward to `PromptEnvelope.replay_metadata.retrieval_id` |
| `request_id` | **RUNTIME-ONLY** | `replay_metadata` only | Forward to `PromptEnvelope.replay_metadata.request_id` |
| *(no field)* | **MISSING in C0** | `contradictions: list[ContradictionFlag]` | Cannot be derived from a single `C0EvidenceContract`; shaper runs contradiction detection across `EvidenceItems` |
| *(no field)* | **MISSING in C0** | `contradiction_status` | Computed by `shape_evidence()` post-mapping |
| *(no field)* | **MISSING in C0** | `freshness: str` | Derived: max of all `EvidenceItem.freshness` values |

---

### 3.3 Runtime Metadata → PromptAssemblyStatus

| Runtime concept | Source | Target in `PromptAssemblyStatus` | Translation rule |
|----------------|--------|--------------------------------|-----------------|
| `retrieval_id` | `C0EvidenceContract` | `replay_metadata["retrieval_id"]` | Forward verbatim |
| `request_id` | `C0EvidenceContract` | `replay_metadata["request_id"]` | Forward verbatim |
| `evidence_hmac` | `C0EvidenceContract` | `replay_metadata["evidence_hmac"]` | Forward verbatim — never recomputed |
| `coverage_score` | `EvidenceBundle.coverage_score` | `evidence_contract_status` | If `≥0.9` → `"complete"`, `≥0.3` → `"partial"`, `<0.3` → `"empty"` |
| `abstain_hint=True` | `C0EvidenceContract` | `assembly_result="fail"` + `overflow_action="abstained"` | Hard gate: if `abstain_hint=True`, PA must not continue assembly |
| `contradiction_status` | `EvidenceBundle.contradiction_status` | `contradiction_status` | 1-to-1 |
| `overflow_action` | `BudgetResult.overflow_action` | `overflow_action` | 1-to-1 from token budgeter |
| `budget_status` | `BudgetResult.budget_status` | `token_budget_status` | 1-to-1 |
| *(new)* | adapter translation time | `input_artifacts` | List of `source_ref` values from all `CitedSpan` objects |

---

### 3.4 Runtime Handoff Metadata → PromptEnvelope.replay_metadata

The `replay_metadata` dict on `PromptEnvelope` is the provenance carrier across the bridge. All runtime integrity fields must survive here.

| Field | Source | Required for replay? | Notes |
|-------|--------|---------------------|-------|
| `retrieval_id` | `C0EvidenceContract` | **YES** | Identifies the exact retrieval pass |
| `request_id` | `C0EvidenceContract` | **YES** | Ties packet to upstream request |
| `evidence_hmac` | `C0EvidenceContract` | **YES** | Integrity seal from C0; PA must not recompute |
| `coverage_score` | `C0EvidenceContract` | YES | Lets downstream verify evidence quality |
| `abstain_hint` | `C0EvidenceContract` | YES | Lets downstream verify assembly decision |
| `packet_type` | `PacketTemplate` | YES | Required for deterministic re-assembly |
| `snapshot_id` | derived from `source_ref` | YES | ADG snapshot identity |
| `commit_sha` | from ADG provenance report (if available) | conditional | Only if PA receives it from context |
| `assembly_timestamp` | `PromptAssemblyStatus` | YES | When the packet was built |

---

## 4. Ownership Boundaries

### 4.1 What C0 MUST produce before Prompt Assembly starts

- A fully validated `C0EvidenceContract` — `validate()` must pass without `C0ContractViolation`
- `evidence_hmac` computed over `request_id + sorted(chunk_hashes)` — sealed and immutable
- `coverage_score` set accurately — PA will use it to decide `evidence_contract_status`
- `abstain_hint` set correctly — PA treats this as a hard gate, not a suggestion
- `cited_spans` non-empty when `abstain_hint=False`
- Each `CitedSpan` carrying a non-empty `chunk_hash` (required for HMAC)

### 4.2 What Prompt Assembly MAY derive

- `source_type` classification from `source_ref` pattern
- `snapshot_id` from `source_ref` filename or `retrieval_id`
- `freshness` timestamp at translation time
- `ContradictionFlag` objects from cross-span reconciliation
- `weak_support` flag from `coverage_score < 0.5`
- `gaps` list from missing must-use sources
- `packet_id` via `PromptEnvelope._generate_packet_id()`
- `assembly_timestamp` from clock at assembly time
- Token budget trimming decisions (narrowed, summarized, split, abstained)

### 4.3 What Prompt Assembly MUST NEVER retrieve or invent

- **Never re-query ADG SQLite or JSON reports** during a runtime bridge invocation — that is C0's job
- **Never recompute `evidence_hmac`** — the C0 seal is inviolable; PA carries it forward but does not verify or regenerate it
- **Never override `abstain_hint=True`** — if C0 flags abstain, PA must emit ABSTAIN regardless of other evidence quality signals
- **Never fabricate `CitedSpan` data** — only `source_ref` classification and wrapping are permitted
- **Never modify `text_snippet`** content — shaper normalizes field names inside `data`, not snippet text
- **Never invent a `commit_sha` or `scanner_digest`** if not available — leave `""` rather than guessing
- **Never call `C0EvidenceContract.build()` or `compute_hmac()`** from within the PA package — those are C0-layer methods

---

## 5. Runtime Packet Handoff Design

### 5.1 Where PromptEnvelope should be materialized

**Option A (preferred for current architecture):** In-memory handoff within the same process.
- The adapter produces a `PromptEnvelope` object
- PA returns it directly to the L3 orchestration dispatcher
- No file I/O required for the hot path
- Replay/audit copy optionally written to `artifacts/adg/packets/<packet_id>.json`

**Option B (async/out-of-process):** Write to `artifacts/adg/packets/<packet_type>_<packet_id>.json`
- L2 polls or subscribes to the `packets/` directory
- Requires a file-watch or channel mechanism not currently present
- `PromptEnvelope.to_json()` already supports this format

**Recommended:** Option A for runtime; Option B for audit trail (write after handoff, not before).

### 5.2 How L2 should receive it

The `PromptEnvelope` should be passed as an argument to the L2 execution dispatcher — **not** fetched from disk. The envelope is the "signed packet" referenced in `04_Live_Task_Dispatch_Execution.md`. L2 must:

1. Verify `assembly_status.assembly_result != "fail"` before processing
2. Verify `abstain_instructions` is empty (or handle abstain path)
3. Consume `must_use_evidence` and `optional_evidence` blocks in order
4. Respect `contradiction_flags` — never collapse contradictions
5. Write results only via UWG — `policy_block` rule §6 already states this

L2 must **not** modify `replay_metadata` — it is read-only provenance.

### 5.3 What replay/HMAC/digest metadata must survive the bridge

| Metadata field | Survival requirement |
|---------------|---------------------|
| `evidence_hmac` | Must be in `replay_metadata` unchanged from C0 |
| `retrieval_id` | Must be in `replay_metadata` |
| `request_id` | Must be in `replay_metadata` |
| `packet_id` | Generated by `PromptEnvelope.__post_init__`; must not change after generation |
| `assembly_timestamp` | Set once at assembly; must not be modified by L2 |
| `coverage_score` | Must be in `replay_metadata` for audit |
| `abstain_hint` | Must be in `replay_metadata` for audit |

### 5.4 Artifact/channel shape for future implementation

The minimal channel shape for `artifacts/adg/packets/` audit files:

```json
{
  "packet_type": "executive_summary",
  "packet_id": "abc123def456abcd",
  "schema_version": "1.0.0",
  "replay_metadata": {
    "retrieval_id": "...",
    "request_id": "...",
    "evidence_hmac": "...",
    "coverage_score": 0.87,
    "abstain_hint": false,
    "snapshot_id": "04102026_1817",
    "assembly_timestamp": "2026-04-11T12:00:00+00:00"
  },
  "assembly_status": { ... },
  "must_use_evidence": [ ... ],
  "optional_evidence": [ ... ],
  "contradiction_flags": [ ... ],
  "system_block": "...",
  "policy_block": "...",
  "task_block": "...",
  "abstain_instructions": "...",
  "refine_instructions": "...",
  "output_schema": { ... }
}
```

This is exactly `PromptEnvelope.to_dict()` — no new format needed.

---

## 6. Minimum Future Implementation Targets

### 6.1 The Adapter/Translator Layer (one new module — not coded here)

**Proposed location:** `agentic_core/L3_orchestration/adapters/c0_to_pa_adapter.py`

**Why this location:**
- It sits at the L3/tool boundary — importing both `C0EvidenceContract` (L3) and `EvidenceItem` (L_TOOLS)
- C0 must never import from PA (stated in `c0_evidence_contract_types.py` docstring)
- PA adapters (`tools/adg/prompt_assembly/retrieval/`) must not import from L3 runtime
- An L3-layer adapter that imports from L_TOOLS is the only compliant placement

**Responsibility:** Translate exactly — no retrieval, no packet building, no policy logic.

**Interface (design only):**
```
translate_c0_to_evidence_bundle(
    contract: C0EvidenceContract,
    packet_type: str,
) -> EvidenceBundle
```

The returned `EvidenceBundle` is then passed to `shape_evidence()` (existing) and then to `build_packet()` (existing). Zero changes to `adapters.py`, `evidence_shaper.py`, or `builders.py`.

### 6.2 Contract Extensions (minimum — potentially none)

| Extension | Necessity | Risk |
|-----------|-----------|------|
| Add `"c0_span"` to `SourceType` Literal | **Conditional** — only if PA needs to distinguish live spans from ADG-file evidence in the shaping step | Low — additive change to `contracts.py` only |
| Add `retrieval_id` field to `EvidenceBundle` | **Not required** — forward via `PromptEnvelope.replay_metadata` | N/A |
| Add `evidence_hmac` field to `EvidenceBundle` | **Not required** — forward via `replay_metadata` | N/A |
| Extend `abstain_hint` into `PromptAssemblyStatus` | **Not required** — already captured via `assembly_result="fail"` path | N/A |

**Preferred:** No contract extensions until `"c0_span"` differentiation proves necessary in shaping.

### 6.3 Packet Emission Point

- **Runtime hot path:** `translate_c0_to_evidence_bundle()` → `shape_evidence()` → `build_packet()` → return `PromptEnvelope` to L3 dispatcher
- **Audit path:** After return, L3 dispatcher (or a thin wrapper) calls `envelope.to_json()` and writes to `artifacts/adg/packets/<type>_<id>.json`
- **Emission point is not in PA** — it is in the L3 dispatcher that owns the lifecycle. PA returns the envelope; it does not write it.

### 6.4 Future CI / E21 Implications

| Implication | Current State | Future State |
|-------------|--------------|-------------|
| E21 `PromptAuthorityReport` is advisory only | Confirmed — report produced, not CI-gated | Upgrade E21 output to feed `gate_p0_authority.py` — fail CI if `violation_count > 0` |
| `generates_prompt` edges from adapter | No adapter exists yet | Once adapter emits `consumes_prompt` edges (via lifecycle trace contract), E20 visitor will pick them up automatically |
| `evidence_hmac` replay integrity check | Not CI-gated | Add a gate that verifies `evidence_hmac` in `replay_metadata` is present on all packets in `artifacts/adg/packets/` |
| `abstain_hint` audit | Not tracked | Gate on: no packet in `packets/` has `assembly_result="fail"` without a corresponding `abstain_instructions` field populated |

---

## 7. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|---------|-----------|
| Adapter placed in wrong layer (e.g., inside `tools/adg/prompt_assembly/retrieval/`) | HIGH — violates C0-never-imports-PA rule | Enforce placement at `agentic_core/L3_orchestration/adapters/` via E6 layer boundary gate |
| `evidence_hmac` recomputed or discarded by PA | HIGH — breaks replay integrity | The adapter must carry it to `replay_metadata` only; PA contracts have no HMAC field so accidental overwrite is structurally impossible |
| `abstain_hint=True` overridden by high `support_score` on a span | HIGH — false confidence | The `abstain_hint` check must be the first gate in the adapter, before any shaping |
| `source_type` misclassified (e.g., a `.json` `source_ref` classified as `json_report` when it is a ratchet) | MEDIUM — affects shaper coverage computation | Implement explicit classification map: `source_ref` pattern → `SourceType`; default to `json_report` and log warning |
| `text_snippet` size inflates token budget unexpectedly | MEDIUM — runtime spans may be much larger than ADG report rows | The token budgeter already handles this via `apply_budget()`; no special case needed |
| `SourceType` Literal does not include `"c0_span"` | LOW — shaper will accept any `SourceType` value; TypeErrors only at type-check time | Add `"c0_span"` if differentiation is needed; otherwise map spans to `"json_report"` with `source_artifact="c0_retrieval"` |
| L2 modifying `replay_metadata` | LOW — L2 has no contract requiring it to be read-only | Document in `PromptEnvelope` docstring; enforce via E21 audit |

---

## 8. Assumptions and Uncertainties

| Item | Status |
|------|--------|
| `C0EvidenceContract` is the only typed output from C0 (no other contract types in L3) | **Confirmed** — only `CitedSpan` and `C0EvidenceContract` found in `c0_evidence_contract_types.py` |
| The `hmac.new()` call in `C0EvidenceContract.compute_hmac()` is intentional (Python `hmac.new` is `hmac.HMAC`) | **Confirmed syntax** — standard library usage |
| `PacketRegistry` will not be modified to accept a `C0EvidenceBundle` path | **Confirmed** — no packet family change needed |
| `EvidenceItem.cited_spans: list[str]` is an existing but unused field in current ADG adapters | **Confirmed** — all current adapters set `cited_spans=[]` (default); designed for exactly this bridge use |
| The L3 orchestration dispatcher (who calls C0 and PA) is not in scope | **Confirmed** — this doc covers the contract boundary only |
| `"c0_span"` is not currently a valid `SourceType` | **Confirmed** — Literal has 6 members; `"c0_span"` is absent |
| E20 `_PromptSlotVisitor` will automatically pick up new `generates_prompt` / `consumes_prompt` edges from the adapter module | **Inferred** — depends on the adapter calling `lifecycle_trace_contract` emit functions |
