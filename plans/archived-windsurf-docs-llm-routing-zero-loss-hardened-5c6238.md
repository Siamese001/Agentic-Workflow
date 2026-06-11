---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\llm-routing-zero-loss-hardened-5c6238.md'
original_relative_path: 'llm-routing-zero-loss-hardened-5c6238.md'
source_sha256: ef9cb2da33d785baa4f716592888a3d7b69592583872de0c0812834f124b92aa
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# LLM Routing + Embedding-Augmented Zero-Loss Architecture: Hardened Plan

Implement hardened LLM routing with embedding augmentation that respects Zero-Loss invariants: embedding recall feeds confidence into the single choke point router, never bypasses it; generation and healing paths remain strictly separated; all cross-layer coupling eliminated.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Core Hardening Principles Applied

1. **Embedding recall never bypasses `route_healing_tier()`** — it only augments `HealingInput.context` with confidence scores
2. **Generation path (`route_generation()`) has NO embedding recall** — pure LLM generation only
3. **Router reads from L4 snapshots, not live Pinecone** — deterministic, no network dependencies at choke point
4. **All embedding operations consume `FailureSignal`, not raw dicts** — respects EscalationContext invariant
5. **Model version enforcement at startup** — seed pack must match production embedder
6. **Performance gating** — embedding only for semantic failures after first retry

---

## Phase 0 — Fix Dimension Mismatch + Model Version Enforcement (BLOCKER)

**File:** `agentic_core/L1_cognition/types/memory_types.py`

```python
# Before (ada-002)
EMBEDDING_DIMENSION: Final[int] = 1536

# After (text-embedding-3-large matching seed pack)
EMBEDDING_DIMENSION: Final[int] = 3072
EMBEDDING_MODEL: Final[str] = "text-embedding-3-large"
SEED_PACK_HASH: Final[str] = "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
```

**File:** `agentic_core/L2_execution/reasoning/EmbeddingSovereignAgent.py`

Add startup validation:
```python
def __init__(self, project_root: Path):
    # Verify model version matches seed pack
    if self.model != EMBEDDING_MODEL:
        raise EmbeddingModelMismatchError(
            f"Production model {self.model} != seed pack model {EMBEDDING_MODEL}"
        )
```

---

## Phase 1 — Seed Pack Loader with Frozen Hash

**New file:** `system_learning/engines/seed_pack_loader.py`

```python
SEED_PACK_PATH = Path(
    r"C:\AgenticEmbeddings\seed_packs\healing_contexts"
    r"\5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
)

def load_seed_pack_to_pinecone(pinecone_index, *, batch_size=100, dry_run=False):
    """Load ONLY if manifest.hash matches SEED_PACK_HASH constant."""
    manifest = json.loads(SEED_MANIFEST.read_text())
    if manifest["seed_index_version_hash"] != SEED_PACK_HASH:
        raise ValueError("Seed pack hash mismatch - frozen pack required")
    # Load with deterministic ordering, no dynamic discovery
```

---

## Phase 2 — Embedding Recall AS Confidence Augmentation (CRITICAL CHANGE)

**File:** `agentic_core/utils/decorators_util.py` (`@standard_heal`)

```python
# BEFORE LLM escalation decision:
if hasattr(_ml_mixin, "ml_recall_healing_pattern"):
    # Embedding recall produces confidence modifier, NOT bypass
    recall_result = _ml_mixin.ml_recall_healing_pattern(violation_dict)
    if recall_result:
        # Augment escalation context with embedding confidence
        escalation_inputs.embedding_recall_score = round(recall_result["similarity_score"], 6)
        escalation_inputs.embedding_content_hash = recall_result["content_hash"]
        escalation_inputs.embedding_replay_key = recall_result["replay_key"]
    # STILL call decide_heal_escalation() — single choke point preserved
```

**File:** `agentic_core/L5_safety/types/heal_policy_types.py`

Add to `HealEscalationInputs`:
```python
embedding_recall_score: float = 0.0
embedding_content_hash: str = ""
embedding_replay_key: str = ""
```

---

## Phase 3 — Router Consumes Embedding Confidence (No Bypass)

**File:** `agentic_core/L2_execution/healers/healing_tier_router.py`

In `compute_heal_confidence()`:
```python
def compute_heal_confidence(healing_input: HealingInput) -> tuple[float, list[str]]:
    """Embedding recall boosts confidence but never bypasses routing."""
    base_score = FAILURE_CLASS_PRIORS.get(healing_input.failure_type, _NEUTRAL_PRIOR)

    # Embedding confidence augmentation
    if hasattr(healing_input, "embedding_recall_score") and healing_input.embedding_recall_score > 0:
        # Boost confidence proportionally, but cap at 0.1 increase
        boost = min(healing_input.embedding_recall_score * 0.1, 0.1)
        base_score = min(base_score + boost, 1.0)
        reason_codes.append("embedding_boost")

    # Continue with normal blast radius, retry decay, etc.
    # NO early return — always proceed to tier selection
```

---

## Phase 4 — Deterministic Replay Keys for Embedding

**File:** `agentic_core/L1_cognition/engines/memory_embedder.py`

Add to `HealingMemoryEmbedder`:
```python
def get_replay_key(self, violation: dict[str, Any]) -> str:
    """Deterministic replay key for embedding recall."""
    import hashlib
    key_data = {
        "model": EMBEDDING_MODEL,
        "pack_hash": SEED_PACK_HASH,
        "top_k": 1,
        "cutoff": 0.85,
        "blas_impl": "numpy",  # Fixed implementation
    }
    return hashlib.sha256(
        json.dumps(key_data, sort_keys=True).encode()
    ).hexdigest()
```

**File:** `agentic_core/L2_execution/healers/healing_tier_types.py`

Add to `InvocationRecord`:
```python
embedding_replay_key: str = ""
embedding_content_hash: str = ""
```

---

## Phase 5 — L4 Materialized Success Rates (No Live Pinecone in Router)

**File:** `agentic_core/L2_execution/healers/healing_tier_router.py`

Replace live lookup with snapshot:
```python
def get_historical_success_rate(error_signature: str, config_snapshot: dict) -> float:
    """Read from L4 config snapshot, not live Pinecone."""
    # config_snapshot passed from L2.2 materialized state
    return config_snapshot.get("historical_success_rates", {}).get(
        error_signature, _NEUTRAL_PRIOR
    )
```

**New materializer:** `system_learning/engines/success_rate_materializer.py`

Periodic job that:
1. Queries Pinecone for success patterns
2. Aggregates by error_signature
3. Writes JSON snapshot to L4 state
4. Updates `ReplayBundle.active_config_hashes`

---

## Phase 6 — Remove Embedding from Generation Path

**File:** `agentic_core/mixins/mcp_operation_mixin.py`

```python
async def call_llm(
    self, prompt: str, *,
    reasoning_class=None, trace_id: str | None = None,
) -> str:
    """PURE generation path — NO embedding recall."""
    from agentic_core.config.reasoning_class import ReasoningClass
    from agentic_core.L2_execution.enforcement.SovereignLLMGateway import get_llm_gateway

    # REMOVED: embedding recall — generation must be pure
    cls = reasoning_class or getattr(self, "AGENT_REASONING_CLASS", ReasoningClass.LIGHT)
    result = await get_llm_gateway().route_generation(
        prompt, cls, trace_id or generate_trace_id()
    )
    return result.get("content", "")
```

---

## Phase 7 — Keep Apps_* Clean of Embedding Dependencies

**DO NOT add MetaLearningClientMixin to BaseRGEngine**

Instead, ensure apps_rg emits proper `FailureSignal`:
```python
# In BaseRGEngine error handling:
failure_signal = FailureSignal.from_exception(
    e,
    failure_type="RUNTIME",  # Semantic failure type
    domain="apps_rg"
)
# L2.3 will handle embedding recall
```

**File:** `apps_lic/engines/lic_spine_adapter.py`

**REMOVE** the recalled_path shortcut entirely. No execution path recall.

---

## Phase 8 — Performance Gating for Embedding Calls

**File:** `agentic_core/L1_cognition/engines/memory_embedder.py`

Add semantic gating:
```python
def should_embed(self, failure_type: str, retry_count: int) -> bool:
    """Only embed semantic failures after first retry."""
    NON_SEMANTIC_FAILURES = {
        "test_failure", "permission_denied", "network_timeout"
    }
    return (
        retry_count >= 1 and
        failure_type not in NON_SEMANTIC_FAILURES
    )
```

Apply in all embedding recall points.

---

## Phase 9 — Wire Real Provider Calls (Unchanged)

**File:** `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

Replace stubs with real `SovereignLLMGateway` calls (same as original plan).

---

## Phase 10 — Add ReasoningClass Enum (Unchanged)

**File:** `agentic_core/config/reasoning_class.py`

Create enum with deterministic temperature=0.0 for all classes.

---

## Phase 11 — Add `route_generation()` to Gateway (Unchanged)

**File:** `agentic_core/L2_execution/enforcement/SovereignLLMGateway.py`

Add method that enforces temperature=0.0 and policy-based model selection.

---

## Phase 12 — Migrate 3 Direct Callers (Unchanged)

Migrate `FissionManagerAgent`, `CognitiveDispositionAgent`, `StructuredEngineAgent` to `route_generation()`.

---

## Phase 13 — Expanded AST CI Guard

**New file:** `ops_scripts/ci/check_llm_routing_compliance.py`

Add checks:
```python
CHECKS = [
    check_agent_has_reasoning_class,
    check_no_model_string_literals,
    check_no_direct_llm_generate_in_agents,
    check_no_temperature_kwarg_outside_gateway,
    check_no_model_env_lookup_in_agents,
    check_no_raw_http_in_agents,
    # NEW:
    check_no_embedding_client_import_outside_allowed,
    check_no_pinecone_usage_outside_l1_l2,
    check_temperature_zero_in_generation_path,
]
```

Allowed modules for embedding:
- `agentic_core/L1_cognition/engines/memory_embedder.py`
- `agentic_core/L1_cognition/engines/meta_client.py`
- `agentic_core/L2_execution/healers/healing_tier_dispatcher.py`

---

## Critical Structural Corrections Summary

| Original Issue | Hardening Applied |
|----------------|------------------|
| Embedding bypassed router | Now augments `HealingInput.context` only |
| Generation had embedding | Removed entirely from `call_llm()` |
| Router queried Pinecone live | Now reads L4 snapshots only |
| apps_lic path substitution | Removed — no execution recall |
| Raw violation_dict used | Now consumes `FailureSignal` only |
| Floating point instability | Scores rounded to 6 decimals |
| Model version mismatch | Startup validation enforced |
| Performance risk | Semantic gating added |
| Cross-layer coupling | Apps_* remain clean of embedding deps |

---

## Files Changed (Reduced Scope)

| Phase | File | Change |
|-------|------|--------|
| 0 | `memory_types.py` | Add EMBEDDING_MODEL, SEED_PACK_HASH |
| 0 | `EmbeddingSovereignAgent.py` | Add model version validation |
| 1 | `seed_pack_loader.py` | NEW with hash verification |
| 2 | `decorators_util.py` | Embedding as confidence augment |
| 2 | `heal_policy_types.py` | Add embedding fields to inputs |
| 3 | `healing_tier_router.py` | Consume embedding confidence |
| 4 | `memory_embedder.py` | Add replay_key method |
| 4 | `healing_tier_types.py` | Add embedding fields to record |
| 5 | `healing_tier_router.py` | Read from L4 snapshot |
| 5 | `success_rate_materializer.py` | NEW periodic job |
| 6 | `mcp_operation_mixin.py` | Remove embedding recall |
| 7 | Various apps_* files | Ensure FailureSignal emission |
| 8 | `memory_embedder.py` | Add semantic gating |
| 9 | `healing_tier_dispatcher.py` | Wire real providers |
| 10 | `reasoning_class.py` | NEW enum |
| 11 | `SovereignLLMGateway.py` | Add route_generation |
| 12 | 3 agent files | Migrate to route_generation |
| 13 | `check_llm_routing_compliance.py` | Expanded CI guard |
| **Total** | | **18 files** |

---

## Success Criteria (Zero-Loss Compliant)

1. Seed pack loaded with hash verification
2. Embedding recall never bypasses `route_healing_tier()`
3. Generation path has zero embedding operations
4. Router reads deterministic L4 snapshots only
5. All embedding operations consume `FailureSignal`
6. Similarity scores rounded and replay-keyed
7. Production model matches seed pack model
8. Embedding only for semantic failures after retry 1
9. CI enforces embedding boundary rules
10. Apps_* emit FailureSignal, never query embeddings directly

---

## Zero-Loss Architecture Compliance

✅ **Single choke point preserved** — `route_healing_tier()` remains sole decision maker
✅ **Deterministic replay** — embedding keys stored, scores rounded
✅ **Authority separation** — L1/L2.3 own embeddings, Apps_* clean
✅ **No cross-layer coupling** — generation path pure, healing augmented
✅ **Frozen dependencies** — seed pack hash pinned, model verified
✅ **Performance bounded** — semantic gating, no generation embedding

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

