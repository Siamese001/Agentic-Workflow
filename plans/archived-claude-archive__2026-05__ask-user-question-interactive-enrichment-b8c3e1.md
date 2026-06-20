---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\ask-user-question-interactive-enrichment-b8c3e1.md'
original_relative_path: '_archive\\2026-05\\ask-user-question-interactive-enrichment-b8c3e1.md'
source_sha256: f33cdaa22c1df660a7b111781609512eb9834b4b98ca1b7f45cead38db0c30a7
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ask_user_question Interactive Enrichment — Author-Gate UX for All Decisions

**Plan ID:** `ask-user-question-interactive-enrichment-b8c3e1`  
**Status:** Draft  
**Tier:** T2  
**Parent:** None (parallel to `author-gate-enforcement-fix-c9d4e2`)  
**Created:** 2026-05-09

---

## 1. Problem Statement

### 1.1 Current Asymmetry

| Feature | Author-Gate Decisions | Native ask_user_question |
|---------|----------------------|--------------------------|
| Confidence prefix | `[confidence=0.88]` | ❌ None |
| Dominance star | `⭐` on recommended | ❌ None |
| Trade-off segment | `· trade-off: <text>` | ❌ None |
| Structured rationale | thesis, principle, flip | ❌ Plain text only |
| Telemetry | `AUTHOR_GATE_PACKET:` | ❌ None |
| Precedent consultation | ✅ Ledger lookup | ❌ None |
| Schema validation | ✅ `author_gate_packet.schema.json` | ❌ None |

### 1.2 User Impact

- **Inconsistent UX:** Same "choose an option" interaction looks different depending on internal pipeline
- **Missing context:** Users can't see confidence scores or trade-offs for non-gated decisions
- **No audit trail:** Simple decisions lack telemetry and ledger writeback
- **Cognitive load:** Users must parse plain text vs. structured enriched options

---

## 2. Vision: Equalized Interactive Requirements

**Goal:** Every `ask_user_question` invocation — whether Author-Gate gated or not — presents options with:
1. **Confidence visibility** — Score-based ranking (even if heuristic)
2. **Visual hierarchy** — Star/recommendation indicator for top option
3. **Trade-off transparency** — One-line consequence summary per option
4. **Consistent formatting** — Same bracketed prefix pattern
5. **Telemetry emission** — `ASK_USER_QUESTION_PACKET:` for auditability

---

## 3. Design: Universal Option Enrichment

### 3.1 Core Principle

**Enrich all options, not just gated ones.** The Author-Gate pipeline becomes the **universal decorator** for user choices.

```
Before (Native):
  Option A — Use sqlite3
  Option B — Use sqlalchemy

After (Enriched):
  ⭐ A — [confidence=0.92] Use sqlite3 · trade-off: zero deps, manual schema
  B — [confidence=0.74] Use sqlalchemy · trade-off: ORM overhead, migration complexity
```

### 3.2 Scoring for Non-Gated Decisions

Since non-gated decisions lack Author-Gate's signal vectors, use **heuristic scoring**:

| Heuristic | Weight | Source |
|-----------|--------|--------|
| Blast radius (files touched) | 0.25 | ADG lookup |
| Layer criticality | 0.20 | Path-based (L0/L5 ×2, L3/L4 ×1.75) |
| Reversibility | 0.20 | File type (config > code > schema) |
| Test surface delta | 0.20 | Test file count in scope |
| Precedent match | 0.15 | Decision ledger (if any) |

**Fallback:** When no heuristics available, default to `confidence=0.72` (surface threshold) for all options.

### 3.3 Option Shape Contract (Universal)

All options — gated or not — MUST include:

```python
{
    "id": "A",
    "label": "Short title",
    "confidence_score": 0.88,           # NEW — required
    "thesis": "One-sentence rationale", # NEW — required
    "key_tradeoffs": ["consequence 1", "consequence 2"],  # NEW — required
    "what_would_flip": "Evidence that changes choice",   # NEW — required
    "surface_description": "[confidence=0.88] ...",      # NEW — auto-generated
}
```

---

## 4. Architecture

### 4.1 New Component: Universal Option Enricher

```
ask_user_question tool call
         ↓
universal_option_enricher.py (NEW)
         ↓
    ┌────┴────────────────────────────┐
    ↓                                   ↓
Author-Gate context?                 Simple choice?
    ↓                                   ↓
Full signal vectors (5)              Heuristic scoring (5)
Precedent lookup                   Default trade-offs
Routing rules (dominance/etc)      Simple ranking
    ↓                                   ↓
    └────┬──────────────────────────────┘
         ↓
ask_user_question_ui_renderer.py (NEW — shared)
         ↓
Consistent enriched output:
  - [confidence=X.XX] prefix
  - ⭐ on top option
  - · trade-off: segment
         ↓
ask_user_question (enriched)
         ↓
ASK_USER_QUESTION_PACKET: emission (NEW telemetry)
```

### 4.2 Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `tools/decisions/universal_option_enricher.py` | Create | Core enrichment logic |
| `tools/decisions/ask_user_question_ui_renderer.py` | Create | Shared UI formatting |
| `tools/decisions/heuristic_scorer.py` | Create | Non-gated confidence calculation |
| `.cursor/schemas/ask_user_question_packet.schema.json` | Create | Telemetry schema |
| `.cursor/scripts/post_cursor_agent_ask_user_question_capture.py` | Modify | Add packet emission |
| `.cursor/skills/author-gate-packet-builder/emit_packet.py` | Modify | Delegate to shared renderer |

---

## 5. Wave Structure

| Wave | Focus | Phases | Est. Tokens | Status |
|------|-------|--------|-------------|--------|
| W1 | Heuristic Scorer + ADG Integration | 2 | 2.5k | Not Started |
| W2 | Universal Enricher Core | 2 | 3k | Not Started |
| W3 | Shared UI Renderer | 2 | 2.5k | Not Started |
| W4 | Telemetry + Ledger Integration | 2 | 2k | Not Started |
| W5 | Migration + Backward Compatibility | 2 | 2k | Not Started |
| W6 | CI Gate + Rollout | 2 | 1.5k | Not Started |

**Total:** 6 waves, 12 phases, ~13.5k tokens

---

## 6. Phase-Level Summary

| Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|-------|-------|-------|-------------|-------------|--------|
| W1.P1 | Heuristic scoring framework | `heuristic_scorer.py` — 5 signal implementation | ADG lookup reliability | 1.5k | Not Started |
| W1.P2 | ADG integration for non-gated | Blast radius, layer criticality queries | Stale ADG handling | 1k | Not Started |
| W2.P1 | Universal enricher scaffold | `universal_option_enricher.py` core | Context detection accuracy | 1.5k | Not Started |
| W2.P2 | Author-Gate delegation | Route gated decisions to existing pipeline | Pipeline compatibility | 1.5k | Not Started |
| W3.P1 | Shared UI renderer | `ask_user_question_ui_renderer.py` — bracketed prefixes, stars, trade-offs | Unicode rendering (⭐) | 1.5k | Not Started |
| W3.P2 | Option shape validation | AG-10 enforcement for all options | Legacy option backward compat | 1k | Not Started |
| W4.P1 | Telemetry schema + emission | `ASK_USER_QUESTION_PACKET:` marker, schema validation | Overhead budget (<50ms) | 1k | Not Started |
| W4.P2 | Ledger writeback for non-gated | Extend `refactor_decision_ledger.sqlite` | Schema migration | 1k | Not Started |
| W5.P1 | Backward compatibility shim | Graceful degradation for legacy callers | No breaking changes | 1k | Not Started |
| W5.P2 | Migration examples + docs | Update 10+ example call sites | Human adoption | 1k | Not Started |
| W6.P1 | CI gate for invariant violations | `check_ask_user_question_invariants.py` | False positive rate | 0.75k | Not Started |
| W6.P2 | Gradual rollout | Feature flag, 25% → 50% → 100% | Rollback plan | 0.75k | Not Started |

---

## 7. Gap Register (Deferred Scope)

| Gap | Description | P-Band | Deferred To |
|-----|-------------|--------|-------------|
| G1 | Real-time user feedback on option quality | P3 | Post-rollout enhancement |
| G2 | A/B testing framework for option presentation | P4 | Analytics phase 2 |
| G3 | Multi-language trade-off localization | P4 | Internationalization plan |
| G4 | Voice/narrative option reading | P5 | Accessibility roadmap |

---

## 8. Success Criteria

| # | Criterion | Metric | Target |
|---|-----------|--------|--------|
| 1 | All options have confidence prefix | `[confidence=X.XX]` present | 100% of enriched calls |
| 2 | Top option has visual indicator | `⭐` or `[RECOMMENDED]` | 100% of enriched calls |
| 3 | All options have trade-off segment | `· trade-off:` present | 100% of enriched calls |
| 4 | Telemetry completeness | `ASK_USER_QUESTION_PACKET:` emitted | 100% of calls |
| 5 | Backward compatibility | Legacy callers unbroken | Zero regressions |
| 6 | Latency budget | Enrichment overhead | ≤50ms per call |
| 7 | User satisfaction | Perceived decision quality | ≥4.0/5.0 (survey) |

---

## 9. Non-Goals

- No changes to Author-Gate scoring logic (preserved as-is)
- No changes to `ask_user_question` tool API (native tool unchanged)
- No mandatory migration of existing gated decisions (backward compatible)
- No changes to precedent ledger schema (extended, not modified)
- No real-time LLM-based option generation (out of scope)

---

## 10. Differentiation from Harmonization Plan

| Aspect | Harmonization (`a7e3d2`) | This Plan (`b8c3e1`) |
|--------|--------------------------|----------------------|
| **Goal** | Route decisions to correct pipeline | Enrich ALL decisions with Author-Gate UX |
| **Scope** | Detection + routing logic | Universal option enrichment |
| **UX Change** | Preserves asymmetry (simple vs. gated) | Equalizes all decisions |
| **Telemetry** | Fixes Author-Gate only | All decisions get telemetry |
| **Scoring** | Gated = signals, Simple = native | All decisions = scored (heuristic or signal) |
| **Implementation** | Pre-hook router | Universal enricher + shared renderer |

**Relationship:** These plans are **complementary**. Harmonization ensures routing is correct; Enrichment ensures presentation is consistent.

---

## 11. References

- **Parent RCA:** `author-gate-canonical-emitter-rca-c7f9d1.md`
- **Harmonization Plan:** `ask-user-question-author-gate-harmonization-a7e3d2.md`
- **Rule:** `author-gate-enforcement.md` §"Canonical-emitter invariant"
- **Skill:** `author-gate-packet-builder/emit_packet.py`
- **Skill:** `author-gate-ui-renderer/render_card.py`
- **Schema:** `.cursor/schemas/author_gate_packet.schema.json`
- **Hook:** `post_cursor_agent_ask_user_question_packet_audit.py`

---

*Plan created 2026-05-09. Scope: Equalize ask_user_question UX with Author-Gate interactive requirements for ALL user decisions.*
