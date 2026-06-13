# Embedding Structural Hardening Supplement

Seven structural hardening measures to eliminate all bypass debt, enforce non-mutation at the code level, bind embedder identity into replay keys, and make the AST scanner blocking.

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


## H-1: Eliminate All Bypass Debt (Found == 0)

**Current:** `EMBEDDING-BYPASS-DEBT: found=1` (tiktoken import at `hardening_mixin.py:187`)

**Action:**
- Create `agentic_core/embeddings/tokenization_adapter.py` — wraps `tiktoken` as single import point
- `hardening_mixin.py` calls `TokenCountAdapter.count_tokens()` — removes direct `tiktoken` import
- Update scanner: `KNOWN_EMBEDDING_BYPASS_DEBT = {}`, `KNOWN_EMBEDDING_BYPASS_DEBT_CEILING = 0`
- Test assertion: `assert found == 0` (hard zero)

**Target Output:**
```
EMBEDDING-BYPASS-DEBT: found=0, ceiling=0, delta=0
```

---

## H-2: Structural Non-Mutation Guard (Code-Level)

**Current:** Tests prove embeddings don't affect routing, but nothing prevents routing modules from importing embedding modules.

**New AST Rules:**
- **Router modules** (`agentic_core/L0_routing/**`) cannot import any embedding modules
- **Tier router** (`agentic_core/L0_routing/engines/*`) cannot read embedding fields
- **Safety policy** (`agentic_core/L5_safety/**`) cannot read embedding context
- **ExecutionMode decisions** must be sealed before any embedding injection

**New Tests:**
```python
def test_no_embedding_imports_in_routing_modules():
    """AST scan: L0_routing modules cannot import embedding modules."""

def test_no_embedding_usage_in_tier_router():
    """AST scan: Tier router code cannot reference embedding fields."""

def test_execution_mode_sealed_before_embedding():
    """Verify ExecutionMode is computed before any HS injection."""
```

**Effect:** Converts "verified by test" → "impossible by structure".

---

## H-3: Bind Full Embedder Identity into Replay Key

**Current:** `get_replay_metadata()` includes basic fields but not all identity dimensions.

**Extended Replay Key Material:**
- `provider: "openai"`
- `model: "text-embedding-3-large"`
- `embedding_dimension: 1536` (observed from first API response)
- `tokenization_policy_version: "cl100k_base_v1"`
- `normalization_policy: "l2"`
- `hs_injection_surface_version: "1.0"` (bump if HS interfaces change)

**Invariant:** If any embedder config changes → W10 digest changes.

**Files:** `agentic_core/embeddings/embedding_factory.py`, `system_learning/engines/embedding_service_factory.py`

---

## H-4: Deterministic Cache Canonicalization

**Canonical Text Normalization:**
- Strip BOM (`\ufeff`)
- Normalize all newlines to `\n` (CRLF → LF, CR → LF)
- Enforce UTF-8 encoding with errors="replace"
- Trim trailing whitespace

**Cache Key Formula:**
```
SHA-256(
    normalized_text_bytes + "|" +
    provider + "|" +
    model + "|" +
    str(dimensions) + "|" +
    tokenization_policy_version
)
```

**Float Handling:**
- Explicit `query_vector.astype(np.float32)` before any similarity computation
- `np.round(scores, 6)` for deterministic tie-breaking
- Stable ordering: `(score_round6 DESC, content_hash ASC)`

**New Test:**
```python
def test_embedding_cache_key_canonicalization():
    """Verify identical text produces identical cache key across platforms."""
```

---

## H-5: Kill-Switch Surface Hardening

**Current:** Kill-switch checked only at factory init.

**Hardening:**
- Add `EmbeddingFactory.is_enabled()` class method (reads `EMBEDDING_ENABLED` each call)
- Every HS injection point wraps with:
  ```python
  if not EmbeddingFactory.is_enabled():
      logger.warning("EMBEDDING_DISABLED: site=%s component=%s", hs_id, cls.__name__)
      return <neutral_value>
  ```
- Assert no fallback similarity logic exists (search for "fallback" in embedding code paths)
- Exactly one structured audit log per seam when disabled

**New Test:**
```python
def test_kill_switch_enforced_at_all_hs_seams():
    """Verify EMBEDDING_DISABLED blocks all HS injection points."""
```

---

## H-6: Data Boundary Controls

**Field Allowlist:**
Only these fields may be embedded:
- `u0_user_prompt`
- `failure_signal.error_message`
- `pattern_text`
- `rag_query`

**Redaction Enforcement:**
- Strip API keys: `sk-...`, `Bearer ...`
- Strip UUIDs in sensitive positions
- Strip sovereign config secret patterns
- Must happen before any `embed_batch()` call

**Logging Contract:**
- FORBIDDEN: `logger.info(f"Embedding: {text}")` — raw text
- ALLOWED: `logger.info("Embedding: hash=%s size=%d model=%s", sha256[:16], len(text), model)`
- AST scanner rule: detect `logger.*` calls containing embedding variables with raw text

**Negative Control:**
```python
def test_w10_data_leak_tamper_xfail():
    """W10_DATA_LEAK_TAMPER=1 should XFAIL on forbidden field embedding."""
    os.environ["W10_DATA_LEAK_TAMPER"] = "1"
    with pytest.raises(EmbeddingInputViolation):
        guard_and_embed("sk-12345secret")  # Should be redacted before embedding
```

---

## H-7: Make AST Scanner Blocking (Found == 0)

**Current:** `assert found <= ceiling` (soft check with KNOWN exceptions)

**After Debt Clearance:**
```python
def test_no_new_embedding_bypass_violations():
    """Hard zero tolerance: no direct embedding SDK imports allowed."""
    # After H-1, KNOWN_EMBEDDING_BYPASS_DEBT is empty
    assert found == 0, f"found={found}, expected=0 — direct embedding SDK import detected"
```

**Extended Scanner Rules:**
- `tiktoken` allowed only in `tokenization_adapter.py`
- `faiss` allowed only in `local_faiss_store.py`
- `openai.Embedding` / `openai.embeddings` call-sites forbidden outside factory
- Allowlist entries cryptographically bound: `{"path": "...", "sha256": "<file_hash>"}`

---

## Implementation Sequence

| # | Hardening | Dependencies | Risk |
|---|---|---|---|
| 1 | H-1: TokenCountAdapter + zero debt | None | Low |
| 2 | H-7: Scanner blocking | H-1 complete | Low |
| 3 | H-3: Full embedder identity in replay key | None | Low |
| 4 | H-4: Cache canonicalization | H-3 (for key material) | Low |
| 5 | H-5: Kill-switch at seams | None | Low |
| 6 | H-6: Data boundary controls | H-5 (for audit logging) | Medium |
| 7 | H-2: Structural non-mutation guard | All others | Medium |

---

## Acceptance Criteria

- `EMBEDDING-BYPASS-DEBT: found=0, ceiling=0, delta=0` (hard zero)
- AST scanner passes with `assert found == 0` (no soft ceiling)
- Router/tier/safety modules have no embedding imports (AST-verified)
- `EmbeddingFactory.replay_key()` includes all 6 identity fields
- Cache key identical across platforms for same normalized text
- `EMBEDDING_DISABLED` blocks all HS seams with audit log
- `EmbeddingInputGuard` redacts secrets; logger never contains raw text
- `W10_DATA_LEAK_TAMPER=1` XFAILs on forbidden field
- All existing Phase 10 tests pass (12 passed, 1 skipped)

**Result:** Phase 10 reaches 100% structural closure — no residual bypass lanes, no test-only invariants, full embedder identity binding, and blocking CI enforcement.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

