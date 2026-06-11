---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\eq1-compiled-artifact-schema-d9a3e7.md'
original_relative_path: 'eq1-compiled-artifact-schema-d9a3e7.md'
source_sha256: fc1ad19a251d71b8e625552757599e50c3d049fa8789a3942f60eaf42d2a288d
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# EQ-1 — `CompiledPromptArtifact` Schema Extension

- **Plan slug**: `eq1-compiled-artifact-schema-d9a3e7`
- **Parent plan**: `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md`
- **Parent execution queue**: `docs/reports/plans/prompt-assembly-gap-b4e1c2/execution_queue.md`
- **ADRs**: `ADR-PROMPT-ASSEMBLY-001` (Q1 slot order, Q2 structured-slot handoff), `ADR-PROMPT-ASSEMBLY-002 §9` (idempotency nonce), §10 (cache-prefix stability)
- **Tier**: T2 (2–5 files, single layer — L2 contracts + shim in L_PG)
- **Status**: Approved 2026-04-23 (DECISION_CAPTURED: type=architecture_choice, confidence=0.90)
- **Author-Gate precedent**: ADR-PA-001 Q2 resolved at conf 0.93; ADR-PA-002 §9 at conf ~0.88

---

## 1. Goal

Extend `@c:/Git/Agentic-Workflow/agentic_core/L2_execution/reasoning/compiled_artifact.py`
`CompiledPromptArtifact` with:

1. `idempotency_nonce: str` — UUID4 hex, excluded from `manifest_hash`, included
   in HMAC inputs (ADR-PA-002 §9).
2. `structured_slots: dict[str, AuthoritySlot] | None` — optional per-slot map
   so provider adapters can render per-vendor without re-parsing the flat
   `final_system_string` (ADR-PA-001 Q2).
3. 90-day back-compat shim so pre-extension artifacts still verify.

Preserves determinism: `manifest_hash` stays over the **structured slot
payload**; the nonce is signature-only.

---

## 2. Scope (files)

| Path | Change type |
|------|-------------|
| `agentic_core/L2_execution/reasoning/compiled_artifact.py` | Add fields, update `_compute_signature`, add `manifest_hash` property, add shim |
| `agentic_core/L4_state/cache/replay_key.py` | Update replay-key derivation to exclude nonce but include structured slots |
| `agentic_core/prompt_governance/contracts/compiled_artifact_types.py` | Re-export alias already in place; just `__all__` refresh |
| `agentic_core/L2_execution/enforcement/provider_adapter.py` | Read `structured_slots` when present; fall back to flat strings |
| `tests/unit/L2_execution/reasoning/test_compiled_artifact_nonce.py` | New — nonce + signature + manifest_hash invariants |
| `tests/unit/L2_execution/reasoning/test_compiled_artifact_shim.py` | New — old artifacts still verify under shim |

---

## 3. Schema deltas

### 3.1 New fields on `CompiledPromptArtifact`

```python
idempotency_nonce: str = field(default_factory=lambda: uuid.uuid4().hex)
structured_slots: dict[str, AuthoritySlot] | None = None
schema_version: int = 2  # was implicit 1 pre-extension
```

### 3.2 `manifest_hash` property (new)

```python
@property
def manifest_hash(self) -> str:
    """SHA-256 over canonical slot payload. EXCLUDES idempotency_nonce."""
    payload = {
        "trace_id": self.trace_id,
        "system_version_hash": self.system_version_hash,
        "structured_slots": _canonicalize_slots(self.structured_slots)
            if self.structured_slots is not None
            else {"flat_system": self.final_system_string,
                  "flat_user": self.final_user_string},
        "allowed_tools_schema": self.allowed_tools_schema,
        "slots_used": self.slots_used,
        "schema_version": self.schema_version,
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
```

### 3.3 `_compute_signature` update

Include `idempotency_nonce` in signature inputs so forged retries are rejected:

```python
def _compute_signature(self, secret_key: bytes) -> str:
    payload = {
        "manifest_hash": self.manifest_hash,
        "idempotency_nonce": self.idempotency_nonce,
        "timestamp": self.timestamp,
    }
    return hmac.new(
        secret_key,
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
```

### 3.4 Back-compat shim

```python
def verify_signature(self, secret_key: bytes) -> bool:
    """Verify HMAC-SHA256. Accepts legacy (v1, no-nonce) signatures during shim window."""
    v2 = self._compute_signature(secret_key)
    if hmac.compare_digest(v2, self.signature):
        return True
    # Legacy path — only for artifacts minted before 2026-04-23
    v1 = self._compute_signature_v1(secret_key)
    return hmac.compare_digest(v1, self.signature)
```

`_compute_signature_v1` is the pre-EQ1 code (current `_compute_signature`),
retained verbatim for 90 days and deleted on 2026-07-23.

---

## 4. Invariants preserved

1. `manifest_hash` is deterministic given identical structured slots → replay stable.
2. Same `(bom, secret_key)` + different session → same `manifest_hash`, different `idempotency_nonce`, different `signature` — detectable as legitimate retry.
3. Cache prefix (`S0 + D0 + I0`) stays byte-identical across renders (ADR-PA-002 §10).
4. Legacy callers that don't pass `structured_slots` still work — manifest_hash falls back to hashing flat strings.

---

## 5. Execution Waves

| Wave | Focus | Est. tokens | Status |
|------|-------|-------------|--------|
| W1 | Field + property + signature extensions in `compiled_artifact.py` | 4 000 🟢 | Todo |
| W2 | `replay_key.py` — exclude nonce, include structured slots | 2 500 🟢 | Todo |
| W3 | `provider_adapter.py` — consume `structured_slots` when present | 3 000 🟢 | Todo |
| W4 | Back-compat shim (`_compute_signature_v1`) + TTL sunset comment | 1 500 🟢 | Todo |
| W5 | Unit tests — nonce determinism, manifest_hash stability, shim path | 4 000 🟢 | Todo |
| W6 | Full test suite + ADG regen + burndown check | 2 000 🟢 | Todo |

Total: ~17 000 tokens (well under phase ceiling).

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Add fields to CompiledPromptArtifact | `compiled_artifact.py` | Must stay frozen dataclass; use `field(default_factory=...)` correctly | 2 000 | Todo |
| 1.2 | Add `manifest_hash` property + canonicalizer helper | `compiled_artifact.py` | Ensure `AuthoritySlot` serializes deterministically (metadata dict sort) | 2 000 | Todo |
| 2.1 | Replay-key derivation update | `replay_key.py` | 5 existing call sites; must return byte-identical key for same structured slots | 2 500 | Todo |
| 3.1 | provider_adapter fallback logic | `provider_adapter.py` + 3 adapter files | Anthropic/OpenAI/Gemini adapter files each have 1 match — thread through uniformly | 3 000 | Todo |
| 4.1 | `_compute_signature_v1` shim + sunset note | `compiled_artifact.py` | Delete date 2026-07-23; mark with `# TODO(2026-07-23): remove EQ-1 shim` | 1 500 | Todo |
| 5.1 | New unit tests — `test_compiled_artifact_nonce.py` | `tests/unit/L2_execution/reasoning/` | Nonce ≠ across renders; `manifest_hash` stable | 2 500 | Todo |
| 5.2 | New unit tests — `test_compiled_artifact_shim.py` | same | Hand-crafted v1 artifact verifies under shim | 1 500 | Todo |
| 6.1 | Full test suite + ADG regen | repo | ADG regen can take 2–5 min | 2 000 | Todo |

---

## 6. ADG_GRAPH_LAYER_EVIDENCE

- **Fan-in via grep** (MCP-serialization-safe): `CompiledPromptArtifact` used in 17 files, 108 matches. Highest concentration:
  - `agentic_core/prompt_governance/contracts/compiled_artifact_types.py` (47 — the alias/shim hub)
  - `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` (16 — primary consumer)
  - `agentic_core/L2_execution/reasoning/slot_assembly_engine.py` (9 — producer)
  - `agentic_core/L0_routing/reasoning/assembly_stage.py` (7 — assembler)
  - `agentic_core/L2_execution/enforcement/provider_adapter.py` (5)
  - `agentic_core/L2_execution/reasoning/prompt_messages.py` (5 — IR)
  - `agentic_core/L4_state/cache/replay_key.py` (5 — replay derivation)
  - `agentic_core/L2_execution/enforcement/_adapter_{anthropic,openai,gemini}.py` (1 each)

- **Semantic edges**:
  - `flows_to`: `slot_assembly_engine.SlotAssemblyEngine` → `CompiledPromptArtifact` → `SovereignLLMGateway` → provider adapter → vendor API
  - `reads_from`: `replay_key` reads artifact bytes; cache key builders read `manifest_hash`
  - `writes_to`: `L6 observability` logs `(trace_id, manifest_hash, idempotency_nonce)`
  - `emits_side_effect`: HMAC-SHA256 signing; telemetry

- **P-view classification**:
  - `v_p0_*`: none — all touched code is L2 governance infra.
  - `v_p1_*`: `assembly_stage.py` uses lazy imports (must preserve).
  - `v_p2_*`: prior merge RH2B.2 collapsed narrow+rich SSOT — avoid reintroducing drift.

- **Provenance**: `backend=grep+on-disk-read, snapshot=working-tree 2026-04-23`.

---

## 7. ADG_HOTSPOT_REPORT

| File | Archetype | Surfaces | Fan-in | Layer | Impact | Notes |
|------|-----------|----------|--------|-------|--------|-------|
| `agentic_core/L2_execution/reasoning/compiled_artifact.py` | **CENTRAL_DEPENDENCY** | Execution, Write, Security, State | ~17 files | L2 | **high** | Schema change SSOT — any field addition must preserve frozen-dataclass semantics. |
| `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py` | **SAFETY_GATEKEEPER** | Execution, Security, Observability | high | L2 | **high** | Must correctly handle both v1 and v2 artifacts during shim window. |
| `agentic_core/L4_state/cache/replay_key.py` | **STATE_NODE** | State, Execution | 5 callers | L4 | medium | Replay-key stability is the primary determinism surface; bugs silently break audit trails. |
| `agentic_core/L2_execution/enforcement/_adapter_{anthropic,openai,gemini}.py` | **ORCHESTRATOR** | Execution | 1 each | L2 | medium | Each adapter threads structured_slots with identical fallback logic. |

Layer multipliers: L2 ×1.0, L4 ×1.75. All primary hotspots ride Execution + Security surfaces; Author-Gate pre-approved at ADR drafting.

---

## 8. Rollback & Risk

1. **Tag pre-EQ1**: `git tag pre-EQ1-2026-04-23` before merge.
2. **Feature flag**: `USE_V2_ARTIFACT_SCHEMA=1` (default on in dev, staged rollout in prod). Flip off → artifacts minted as v1 shape (legacy path).
3. **Revert criterion**: any replay-key mismatch on historical traces within 24 hr of merge → revert to tag.
4. **Known risk**: `structured_slots` dict mutation after construction would break hash stability. Mitigated by `frozen=True` on `AuthoritySlot` + top-level dataclass already frozen.

---

## 9. Success Criteria

1. `CompiledPromptArtifact` has `idempotency_nonce`, `structured_slots`, `schema_version=2`, `manifest_hash` property.
2. `verify_signature` accepts both v1 and v2 during shim window.
3. All existing tests still pass (≥ 99% retained).
4. New nonce + shim tests land green.
5. ADG regen shows no new P0/P1 violations.
6. Cache-prefix stability gate (`check_cache_prefix_stability.py`, to be added in EQ-9) runs green once it exists.
7. 90-day sunset calendar entry created for 2026-07-23.

---

## 10. Related Plans

- `.windsurf/plans/prompt-assembly-best-practices-gap-b4e1c2.md` — gap parent
- `.windsurf/plans/prompt-assembly-reception-hardening-9c4e2b.md` — ADR-PA-001 execution (prior)
- `docs/reports/plans/prompt-assembly-gap-b4e1c2/execution_queue.md` — upstream queue
