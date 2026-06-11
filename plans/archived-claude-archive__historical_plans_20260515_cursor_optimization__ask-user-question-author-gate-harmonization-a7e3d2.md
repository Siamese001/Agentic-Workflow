---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\ask-user-question-author-gate-harmonization-a7e3d2.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\ask-user-question-author-gate-harmonization-a7e3d2.md'
source_sha256: 01c6852695f8d8ef2ced61518010b4189a3acab2cbfff4b6e369c960cbc086ad
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ask_user_question ↔ Author-Gate Pipeline Harmonization

**Plan ID:** `ask-user-question-author-gate-harmonization-a7e3d2`  
**Status:** Draft  
**Tier:** T2  
**Created:** 2026-05-09

---

## 1. Problem Statement

### 1.1 Current State: Two Divergent Pipelines

| Pipeline | Entry Point | UI Invariants | Schema Validation | Telemetry |
|------------|-------------|---------------|-------------------|-----------|
| **Native ask_user_question** | Direct tool call | None | None | None |
| **Author-Gate** | `emit_packet.py` → `author-gate-ui-renderer` | 4 invariants (confidence, star, trade-off, packet) | `author_gate_packet.schema.json` | `AUTHOR_GATE_PACKET:`, `ROUTER_DECISION:` |

### 1.2 RCA Summary (from `author-gate-canonical-emitter-rca-c7f9d1`)

When Author-Gate decisions bypass the canonical emitter:
- ❌ No `[confidence=0.NN]` prefix
- ❌ No `⭐` dominance star on recommended option
- ❌ No `· trade-off: <text>` segment
- ❌ No `AUTHOR_GATE_PACKET:` block (ledger never updated)
- ❌ No `ROUTER_DECISION:` marker (closed-loop router family gap)

**Root Cause:** Hand-crafting `ask_user_question` option `label`/`description` strings without pipeline enrichment.

---

## 2. Why Two Pipelines Exist

| Pipeline | Purpose | Design Rationale |
|----------|---------|------------------|
| **ask_user_question** | Generic user choice (any domain) | Minimal API surface; caller controls all formatting |
| **Author-Gate** | Gated architectural decisions with precedent, confidence scoring, routing rules | Requires schema validation, precedent lookup, routing (dominance/low-conf/surface-top-N), telemetry, ledger writeback |

The Author-Gate pipeline adds **8 layers** not present in native `ask_user_question`:
1. Precedent consultation (`refactor_decision_ledger.sqlite`)
2. Signal vector calculation (5-signal weighted scoring)
3. Routing rule application (dominance, low-confidence, surface-top-N)
4. Schema validation (`author_gate_packet.schema.json`)
5. Didactic field enforcement (AG-10: thesis, principle, trade-offs, flip conditions)
6. UI invariant injection (confidence prefix, star, trade-off segment)
7. Telemetry emission (`AUTHOR_GATE_PACKET:`, `ROUTER_DECISION:`)
8. Ledger writeback (decision captured for future precedent)

---

## 3. Harmonization Strategy

### 3.1 Option A: Author-Gate as ask_user_question Preprocessor (Recommended ⭐)

**Design:** Create an `ask_user_question` wrapper/adapter that:
1. Detects Author-Gate context (keywords: "Author-Gate", "AG-", "decision", "options" with scores)
2. Routes through `emit_packet.py` if context detected
3. Falls back to native if no Author-Gate context

**Pros:**
- Single entry point for all decisions
- Backward compatible with non-gated choices
- Enforces invariants automatically
- No change to existing Author-Gate pipeline

**Cons:**
- Requires context detection (heuristic or explicit flag)
- Adds latency to non-gated decisions ( detection overhead)

**Files to Modify:**
- `.windsurf/scripts/pre_ask_user_question_gate.py` (new — detection + routing)
- `.windsurf/hooks.json` (add pre-hook for ask_user_question)

---

### 3.2 Option B: Unified Decision Surface (Emitter-First)

**Design:** Make `emit_packet.py` the single entry point for ALL decisions:
- Rename/reframe `emit_packet.py` → `decision_emitter.py`
- Add `decision_type: "simple_choice"` for non-gated decisions
- Strip Author-Gate-specific fields for simple choices
- Output compatible with `ask_user_question` options format

**Pros:**
- Single SSOT for decision presentation
- Consistent telemetry for all choices
- Simpler mental model: "all decisions go through emitter"

**Cons:**
- Heavyweight for simple choices (precedent lookup overhead)
- Breaking change to existing simple `ask_user_question` calls
- Requires refactoring all non-gated decisions

---

### 3.3 Option C: Explicit Opt-In (Flag-Based)

**Design:** Add explicit `author_gate: true` flag to `ask_user_question` calls:
- When `author_gate: true`, tool validates/enriches through pipeline
- When absent/false, native behavior unchanged

**Pros:**
- Explicit, no guessing
- Zero overhead for non-gated decisions
- Clear audit trail

**Cons:**
- Requires updating all Author-Gate call sites
- Human error: might forget flag

---

## 4. Recommended Approach: Option A with Context Detection

### 4.1 Detection Heuristics

```python
# pre_ask_user_question_gate.py
AUTHOR_GATE_KEYWORDS = [
    "author-gate", "author_gate", "AG-", "decision", "confidence",
    "recommend", "option A", "blast radius", "precedent"
]

def is_author_gate_context(question: str, options: list) -> bool:
    """Detect if this ask_user_question should route through Author-Gate pipeline."""
    # Keyword match in question
    if any(kw in question.lower() for kw in AUTHOR_GATE_KEYWORDS):
        return True
    
    # Options have score-like fields (confidence, score, rank)
    for opt in options:
        if any(field in opt for field in ["confidence", "score", "rank", "thesis"]):
            return True
    
    # Options have structured description with bracketed prefix
    for opt in options:
        desc = opt.get("description", "")
        if re.search(r"\[confidence=\d+\.\d+\]", desc):
            return True  # Already formatted — skip re-processing
    
    return False
```

### 4.2 Pipeline Flow

```
ask_user_question tool call
         ↓
pre_ask_user_question_gate.py (NEW)
         ↓
    ┌────┴────┐
    ↓         ↓
Author-Gate?   Simple choice?
    ↓              ↓
emit_packet.py   Native tool
    ↓              ↓
author-gate-ui-renderer   (pass-through)
    ↓              ↓
ask_user_question (enriched)   ask_user_question (native)
```

---

## 5. Wave Structure

| Wave | Focus | Phases | Est. Tokens | Status |
|------|-------|--------|-------------|--------|
| W1 | Detection Logic + Pre-Hook Scaffold | 2 | 2k | Not Started |
| W2 | emit_packet.py Integration | 2 | 3k | Not Started |
| W3 | Backward Compatibility + Tests | 2 | 2k | Not Started |
| W4 | CI Gate + Rollout | 2 | 1k | Not Started |

---

## 6. Phase-Level Summary

| Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|-------|-------|-------|-------------|-------------|--------|
| W1.P1 | Context detection heuristics | `pre_ask_user_question_gate.py` core | False positive/negative tuning | 1k | Not Started |
| W1.P2 | Pre-hook registration | `.windsurf/hooks.json` + `pre_ask_user_question_gate.py` | Hook ordering with other pre-hooks | 1k | Not Started |
| W2.P1 | emit_packet.py adapter | Bridge from detection to pipeline | Latency budget (≤100ms overhead) | 1.5k | Not Started |
| W2.P2 | author-gate-ui-renderer integration | Ensure renderer output compatible with ask_user_question | UI invariant enforcement | 1.5k | Not Started |
| W3.P1 | Backward compatibility tests | Non-gated decisions unchanged | Test matrix (simple, complex, Author-Gate) | 1k | Not Started |
| W3.P2 | Migration guide + examples | Update docs with new pattern | Human adoption | 1k | Not Started |
| W4.P1 | CI gate for invariant violations | `check_ask_user_question_author_gate_invariants.py` | Detection accuracy | 0.5k | Not Started |
| W4.P2 | Gradual rollout + monitoring | Enable for 10% → 50% → 100% | Rollback plan if FP rate high | 0.5k | Not Started |

---

## 7. Gap Register (Deferred Scope)

| Gap | Description | P-Band | Deferred To |
|-----|-------------|--------|-------------|
| G1 | Real-time LLM-based context classification (vs. heuristics) | P3 | Future plan — ML-based detection |
| G2 | User override to force native/simple presentation | P3 | W4.P2 — add bypass flag |
| G3 | Cross-session decision pattern learning | P4 | Future — precedent system extension |
| G4 | Multi-modal decision surfaces (voice, visual) | P5 | Future — not in scope |

---

## 8. Success Criteria

| # | Criterion | Metric | Target |
|---|-----------|--------|--------|
| 1 | Author-Gate invariants enforced | Violations in `author_gate_ui_violations.jsonl` | Zero new violations |
| 2 | Simple choices unaffected | Non-gated decision latency | ≤100ms overhead |
| 3 | Detection accuracy | True positive rate | ≥95% |
| 4 | False positive rate | Simple choices incorrectly routed | ≤5% |
| 5 | Telemetry completeness | `AUTHOR_GATE_PACKET:` + `ROUTER_DECISION:` present | 100% of Author-Gate contexts |

---

## 9. Non-Goals

- No changes to Author-Gate scoring/routing logic (preserved)
- No changes to `ask_user_question` tool API (native tool unchanged)
- No changes to precedent ledger schema (preserved)
- No migration of existing non-gated decisions (backward compatible)

---

## 10. References

- **RCA:** `author-gate-canonical-emitter-rca-c7f9d1.md`
- **Rule:** `author-gate-enforcement.md` §"Canonical-emitter invariant"
- **Skill:** `author-gate-packet-builder/emit_packet.py`
- **Skill:** `author-gate-ui-renderer/render_card.py`
- **Schema:** `.windsurf/schemas/author_gate_packet.schema.json`
- **Hook:** `post_cascade_author_gate_ui_audit.py`

---

*Plan created 2026-05-09. Implementation pending prioritization.*
