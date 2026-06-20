---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\author-gate-ask-ui-consolidated-a1e3f7.md'
original_relative_path: '_archive\\2026-05\\author-gate-ask-ui-consolidated-a1e3f7.md'
source_sha256: 4aa8467198d45120c9cb04ed4bd8d74b86d63be3679d24e712b47b6de396c507
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Author-Gate / ask_user_question UI Pipeline — Consolidated Completion Plan

**Plan ID:** `author-gate-ask-ui-consolidated-a1e3f7`  
**Status:** Live  
**Tier:** T2  
**Consolidates:** d9e4f2, d9e5f2 (Notion-only), b8c3e1, a7e3d2  
**Created:** 2026-05-10  
**Rebaseline Date:** 2026-05-10

---

## 1. Rebaseline: Current Implementation State

### 1.1 ✅ COMPLETE (Already Landed)

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **Enriched Choice Builder** | `tools/decisions/enriched_choice_builder.py` | ✅ Complete | All UI invariants: confidence prefix, ⭐ star, trade-off segment |
| **ASK_USER_QUESTION_PACKET Schema** | `tools/decisions/enriched_choice_builder.TelemetryPacket` | ✅ Complete | Returns packet; caller emits |
| **Post-Cursor-Agent Audit** | `post_cursor_agent_ask_user_question_packet_audit.py` | ✅ Complete | Vacuum-closure audit for ask_user_question without packet |
| **CI Gate** | `ops_scripts/ci/check_enriched_choice_ui_invariants.py` | ✅ Complete | AST-based scanner for UI invariant violations |
| **CI Gate (AST)** | `ops_scripts/ci/check_enriched_choice_ui_invariants_ast.py` | ✅ Complete | Alternative AST-based implementation |
| **Author-Gate Pipeline** | `emit_packet.py` → `render_card.py` | ✅ Complete | AUTHOR_GATE_PACKET + ROUTER_DECISION emission |
| **Workflow: antipattern-author-gate** | `.cursor/workflows/antipattern-author-gate.md` | ✅ Migrated | Uses canonical AUTHOR_GATE_PACKET path |
| **Workflow: author-gate-decision-gate** | `.cursor/workflows/author-gate-decision-gate.md` | ✅ Migrated | Uses canonical AUTHOR_GATE_PACKET path |

### 1.2 ⏳ PENDING (Remaining Work)

| Component | Location | Gap | Effort |
|-----------|----------|-----|--------|
| **Structured-Reasoning Migration** | `.cursor/skills/structured-reasoning/SKILL.md` | Lines 144-151 still use plain `ask_user_question` | 0.5k tokens |
| **Pre-Hook Harmonization** | `pre_ask_user_question_gate.py` (new) | Context detection + routing between AG and enriched paths | 2k tokens |
| **Ledger Writeback for Non-Gated** | `refactor_decision_ledger.sqlite` extension | ASK_USER_QUESTION_PACKET decisions → ledger | 1k tokens |
| **Universal Enricher Heuristics** | `heuristic_scorer.py` (new) | ADG blast radius, layer criticality scoring | 1.5k tokens |
| **CI Gate Registration** | `run_contract_gates.py` | Register enriched_choice gate in assurance_gates | 0.2k tokens |

### 1.3 ❌ ARCHIVED (Superseded)

| Original Plan | Reason |
|---------------|--------|
| `unified-decision-presentation-ux-hardened-d9e5f2` | Notion-only, never materialized; concepts merged here |
| `ui-choice-consistency-zero-loss-d9e4f2` | Core delivered; remaining scope consolidated here |
| `ask-user-question-interactive-enrichment-b8c3e1` | Partially complete; gaps covered here |
| `ask-user-question-author-gate-harmonization-a7e3d2` | Core concept (pre-hook routing) still pending |

---

## 2. Consolidated Scope: Remaining Waves

### Wave 1: Structured-Reasoning Skill Migration (W1)

**Files:** `.cursor/skills/structured-reasoning/SKILL.md`

**Current State:** Lines 144-151 show plain `ask_user_question`:
```markdown
ask_user_question(
  question="Step N has two valid approaches — which should I use?",
  options=[
    {"label": "Plan A", "description": "<what it does> — Pros: X — Cons: Y"},
    {"label": "Plan B", "description": "<what it does> — Pros: X — Cons: Y"}
  ],
  allowMultiple=False
)
```

**Target State:** Convert to enriched_choice_builder with:
- `[confidence=X.XX]` prefix
- `· trade-off:` segment
- `ASK_USER_QUESTION_PACKET` telemetry
- ⭐ on recommended option

**Acceptance:** Scanner passes on SKILL.md after migration.

---

### Wave 2: Pre-Hook Harmonization (W2)

**Purpose:** Route decisions through correct pipeline automatically.

**New File:** `.cursor/scripts/pre_ask_user_question_gate.py`

**Responsibility:**
1. Detect if ask_user_question context is Author-Gate-class (governance decisions)
2. Route AG-class → canonical `emit_packet.py` pipeline
3. Route non-AG → `enriched_choice_builder` pipeline
4. Ensure exactly one of AUTHOR_GATE_PACKET or ASK_USER_QUESTION_PACKET is emitted

**Detection Heuristics (from a7e3d2):**
```python
AUTHOR_GATE_KEYWORDS = [
    "author-gate", "author_gate", "AG-", "decision", "confidence",
    "recommend", "option A", "blast radius", "precedent", "refactor",
    "delete", "cross-layer", "migration", "breaking change"
]
```

**Integration:** Register in `.cursor/hooks.json` as pre-hook.

---

### Wave 3: Heuristic Scorer + Ledger (W3)

**3.1 Heuristic Scorer** (`tools/decisions/heuristic_scorer.py`)

Purpose: Compute confidence for non-gated decisions using:
- ADG blast radius (files touched)
- Layer criticality (L0/L5 ×2.0, L3/L4 ×1.75)
- Reversibility (file type)
- Test surface delta
- Precedent match (if any)

**3.2 Ledger Writeback Extension**

Extend `refactor_decision_ledger.sqlite` schema to accept ASK_USER_QUESTION_PACKET rows:
- `packet_type: "ASK_USER_QUESTION_PACKET"`
- `context: str` (telemetry context)
- `confidence_source: "explicit" | "heuristic_default"`
- Standard fields: decision_id, timestamp, outcome

---

### Wave 4: CI Integration + Tests (W4)

**4.1 Gate Registration**

Register `check_enriched_choice_ui_invariants.py` in `run_contract_gates.py` assurance_gates list.

**4.2 Tests**

| Test | File |
|------|------|
| Pre-hook detection accuracy | `tests/unit/windsurf_scripts/test_pre_ask_user_question_gate.py` |
| Heuristic scorer accuracy | `tests/unit/tools/decisions/test_heuristic_scorer.py` |
| Ledger writeback | `tests/unit/ledgers/test_ask_user_question_ledger.py` |
| End-to-end harmonization | `tests/integration/test_author_gate_ask_harmonization.py` |

---

## 3. Decision Presentation Taxonomy (Final)

| Tier | Pipeline | Use Case | Telemetry | Example |
|------|----------|----------|-----------|---------|
| **AUTHOR_GATE_FULL** | `emit_packet.py` → `render_card.py` | Governance-class: refactor, delete, anti-pattern, cross-layer | AUTHOR_GATE_PACKET + ROUTER_DECISION | Anti-pattern remediation |
| **ENRICHED_CHOICE** | `enriched_choice_builder.py` | Standard multi-option decisions with confidence/trade-offs | ASK_USER_QUESTION_PACKET | Branch resolution in structured reasoning |
| **EXEMPT_DATA_COLLECTION** | Native `ask_user_question` | CLI wizards, field collection | None | `interactive_wizard.py` |
| **EXEMPT_TEST_FIXTURE** | Native `ask_user_question` | Test mocks, synthetic data | None | Unit test helpers |

---

## 4. Definition of Done

| # | Criterion | Verification |
|---|-----------|------------|
| DoD-1 | structured-reasoning/SKILL.md uses enriched_choice_builder | Scanner passes on file |
| DoD-2 | pre_ask_user_question_gate.py routes correctly | Unit tests: TP≥95%, FP≤5% |
| DoD-3 | Heuristic scorer integrated with ADG | ADG lookup test passes |
| DoD-4 | Ledger accepts ASK_USER_QUESTION_PACKET | SQLite schema test passes |
| DoD-5 | CI gate registered and passing | run_contract_gates.py green |
| DoD-6 | No regression in Author-Gate pipeline | Existing AG tests pass |
| DoD-7 | Telemetry completeness | 100% of enriched calls emit packet |

---

## 5. Non-Goals

- No changes to external `ask_user_question` tool API
- No changes to Author-Gate scoring/routing logic
- No changes to precedent ledger schema (extended only)
- No migration of existing test fixtures
- No docs-only example updates outside SKILL.md

---

## 6. References

- **Superseded Plans:** d9e4f2, d9e5f2 (Notion), b8c3e1, a7e3d2
- **Existing Implementation:** `tools/decisions/enriched_choice_builder.py`
- **Post-Cursor-Agent Audit:** `.cursor/scripts/post_cursor_agent_ask_user_question_packet_audit.py`
- **CI Gate:** `ops_scripts/ci/check_enriched_choice_ui_invariants.py`
- **Rule:** `.cursor/rules/author-gate-enforcement.md`

---

*Consolidated 2026-05-10. Core infrastructure complete; 4 waves remaining for full harmonization.*
