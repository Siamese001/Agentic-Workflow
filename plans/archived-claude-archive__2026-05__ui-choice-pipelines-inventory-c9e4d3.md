---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\ui-choice-pipelines-inventory-c9e4d3.md'
original_relative_path: '_archive\\2026-05\\ui-choice-pipelines-inventory-c9e4d3.md'
source_sha256: 79227a6841b8b3d03a12485900b54f8ccfcadb6d4c0e1879afdf5c479f8ab9f7
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# UI Choice Presentation Pipelines — Complete Inventory

**Plan ID:** `ui-choice-pipelines-inventory-c9e4d3`  
**Status:** Draft  
**Tier:** T1 (Inventory/Analysis)  
**Created:** 2026-05-09

---

## 1. Executive Summary

This document inventories **all pipelines** in the Agentic-Workflow codebase that present choices to users. The goal is to identify inconsistencies in UI presentation (STAR ⭐, confidence prefix, trade-off segments) and provide a complete scope for harmonization.

---

## 2. Pipeline Taxonomy

### 2.1 Tier 1: Author-Gate Canonical Pipeline ✅ (Correct)

| Component | Path | UI Invariants | Telemetry |
|-----------|------|---------------|-----------|
| `emit_packet.py` | `.cursor/skills/author-gate-packet-builder/` | ✅ All 4 | `AUTHOR_GATE_PACKET:` |
| `render_card.py` | `.cursor/skills/author-gate-ui-renderer/` | ✅ All 4 | Pass-through |

**Invariants Enforced:**
1. `[confidence=X.XX]` prefix on all options
2. `⭐` star on recommended option (when dominance fires)
3. `· trade-off:` segment in every option
4. `AUTHOR_GATE_PACKET:` + `ROUTER_DECISION:` telemetry

**Coverage:** All Author-Gate decisions (architecture, refactoring, anti-patterns, deletions, etc.)

---

### 2.2 Tier 2: Native ask_user_question (Inconsistent) ⚠️

| Usage Pattern | Location | Invariants | Notes |
|---------------|----------|------------|-------|
| **Workflows** | `structured-reasoning/SKILL.md:144` | ❌ None | Plain label/description |
| **Plans** | `adg-chromadb-retrieval-assessment-8a3f2b.md` | ❌ None | No enrichment |
| **Apps** | `apps_rg/__main__.py` (interactive wizard) | ❌ None | TTY input, not ask_user_question |
| **Tests** | `test_hitl_validators.py` | ❌ None | Mock data only |

**Issue:** These use `ask_user_question` directly without the Author-Gate pipeline enrichment.

**Example (Current - Inconsistent):**
```python
ask_user_question(
    question="Step N has two valid approaches",
    options=[
        {"label": "Plan A", "description": "<what it does> — Pros: X — Cons: Y"},
        {"label": "Plan B", "description": "<what it does> — Pros: X — Cons: Y"}
    ]
)
```

**Should Be (Consistent):**
```python
ask_user_question(
    question="Step N has two valid approaches",
    options=[
        {
            "label": "⭐ A — [confidence=0.88] Plan A",
            "description": "[confidence=0.88] · trade-off: Gains X, loses Y · <what it does>"
        },
        {
            "label": "B — [confidence=0.74] Plan B",
            "description": "[confidence=0.74] · trade-off: Higher coverage but bigger blast radius · <what it does>"
        }
    ]
)
```

---

### 2.3 Tier 3: Workflow-Prose Choices (No Tool) ⚠️

| Workflow | Location | Pattern | Issue |
|----------|----------|---------|-------|
| **antipattern-author-gate** | `.cursor/workflows/antipattern-author-gate.md:38-45` | Markdown blockquote | ❌ No `ask_user_question` at all |

**Current (Non-Standard):**
```markdown
> This change will introduce N new `<category>` instance(s) in `<file>`.
> **Options:**
> A) Narrow the exception type...
> B) Add `# guardian: allow-<category>`...
> C) Restructure...
> D) Proceed as-is...
>
> Which approach?
```

**Should Be:** Use `ask_user_question` with enriched options (or full Author-Gate if architectural).

---

### 2.4 Tier 4: CLI Interactive Wizards (Different Surface)

| Component | Path | Pattern | Notes |
|-----------|------|---------|-------|
| **interactive_wizard.py** | `apps_shared/cli/interactive_wizard.py` | `input()` prompts | TTY only, no ask_user_question |

**Pattern:**
```python
WizardField("company", "Target company", kind="string")
WizardField("description", "Job description", kind="multiline_or_file")
```

**Assessment:** These are **data collection** (gathering inputs), not **decision presentation** (choosing between approaches). UI enrichment not applicable.

---

### 2.5 Tier 5: HITL / L5 Safety (Partial Overlap)

| Component | Path | Relationship to Author-Gate |
|-----------|------|----------------------------|
| `exit_control_hitl.py` | `agentic_core/L5_safety/enforcement/` | Uses Author-Gate for escalation decisions |
| `hitl_gate.py` | `agentic_core/L5_safety/enforcement/` | Wraps Author-Gate for L5 context |
| `escalation_packet.py` | `agentic_core/L5_safety/eval_spine/` | Emits HITL packets (distinct from AG packets) |

**Note:** HITL (Human-In-The-Loop) at L5 uses the Author-Gate pipeline when escalation involves architectural choices. For simple safety overrides, it uses direct `ask_user_question` without enrichment.

---

## 3. Inconsistency Matrix

| Pipeline | Confidence Prefix | Star Indicator | Trade-off Segment | Telemetry | Schema Validated |
|----------|-------------------|----------------|-------------------|-----------|------------------|
| **Author-Gate (canonical)** | ✅ | ✅ | ✅ | ✅ AG packet | ✅ |
| **Native ask_user_question** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Workflow prose (blockquote)** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Structured reasoning skill** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **HITL simple overrides** | ❌ | ❌ | ❌ | ⚠️ HITL packet | ❌ |
| **CLI wizards** | N/A | N/A | N/A | N/A | N/A |

---

## 4. Files Requiring Harmonization

### 4.1 Skills (High Priority)

| File | Line(s) | Current Pattern | Needed Change |
|------|---------|---------------|---------------|
| `.cursor/skills/structured-reasoning/SKILL.md` | 144-149 | Plain ask_user_question | Route through universal enricher |

### 4.2 Workflows (High Priority)

| File | Line(s) | Current Pattern | Needed Change |
|------|---------|---------------|---------------|
| `.cursor/workflows/antipattern-author-gate.md` | 38-45 | Markdown blockquote | Convert to ask_user_question + enricher |
| `.cursor/workflows/author-gate-decision-gate.md` | 45-48 | Minimal shape (no confidence) | Update to full AG-10 shape |

### 4.3 Plans (Documentation Only)

| File | Context |
|------|---------|
| `.cursor/plans/adg-chromadb-retrieval-assessment-8a3f2b.md` | Example in plan doc |

### 4.4 Tests (Reference Implementations)

| File | Line(s) | Purpose |
|------|---------|---------|
| `tests/governance/test_hitl_validators.py` | Various | Mock options for validation |
| `tests/unit/author_gate/test_author_gate_ui_audit.py` | Various | Enriched options (reference) |

---

## 5. Root Cause Analysis

### 5.1 Why Inconsistencies Exist

| Factor | Explanation |
|--------|-------------|
| **Pipeline Age** | Native `ask_user_question` predates Author-Gate enrichment (2026-04 vs 2026-05) |
| **Documentation Drift** | Workflows documented before UI invariants were codified |
| **Tool API Stability** | `ask_user_question` is external tool; can't modify its internals |
| **Skill Boundaries** | `structured-reasoning` skill predates `author-gate-packet-builder` |
| **HITL vs AG Distinction** | Historical separation: safety (L5) vs governance (Author-Gate) |

### 5.2 Enforcement Gaps

| Hook | Coverage | Gap |
|------|----------|-----|
| `post_cursor_agent_author_gate_ui_audit.py` | Author-Gate decisions only | ❌ Does not audit native ask_user_question |
| `post_cursor_agent_ask_user_question_packet_audit.py` | Packet presence | ❌ Does not enforce UI invariants |
| `pre_user_prompt_author_gate_reminder.py` | Pre-prompt reminder | ❌ Does not intercept tool calls |

---

## 6. Harmonization Options

### Option A: Universal Enrichment (Recommended ⭐)

**Approach:** Create a wrapper that enriches ALL `ask_user_question` calls with confidence/star/trade-off.

**Pros:**
- Single point of enforcement
- Backward compatible (adds info, doesn't remove)
- Works with existing Author-Gate pipeline

**Cons:**
- Requires confidence scoring for all decisions (heuristic fallback needed)

**Implementation:** See `ask-user-question-interactive-enrichment-b8c3e1.md`

### Option B: Tiered Presentation

**Approach:** Different enrichment levels based on decision criticality.

| Tier | Invariants | Use Case |
|------|------------|----------|
| Tier 1 (Critical) | Full Author-Gate | Architecture, refactoring, deletion |
| Tier 2 (Standard) | Confidence + trade-off | Simple choices in workflows |
| Tier 3 (Minimal) | Plain | Data collection wizards |

### Option C: Documentation-Only Fix

**Approach:** Update workflow docs to recommend Author-Gate pipeline.

**Cons:** No enforcement; inconsistencies persist.

---

## 7. Recommended Action

1. **Immediate:** Update `structured-reasoning/SKILL.md` to use Author-Gate pipeline for branch decisions
2. **Short-term:** Convert `antipattern-author-gate.md` from prose to `ask_user_question` + enricher
3. **Medium-term:** Implement `ask-user-question-interactive-enrichment-b8c3e1.md` (universal enricher)
4. **Long-term:** Add CI gate `check_ask_user_question_ui_invariants.py` to enforce at commit time

---

## 8. Success Criteria

| # | Criterion | Metric |
|---|-----------|--------|
| 1 | All user choices have confidence visibility | 100% of `ask_user_question` calls |
| 2 | Top option has visual indicator | 100% of multi-option decisions |
| 3 | Trade-off transparency | ≥1 trade-off per option |
| 4 | Telemetry completeness | `ASK_USER_QUESTION_PACKET:` for all choices |
| 5 | Zero plain-prose options | 0 markdown blockquote choices |

---

## 9. References

- **Enrichment Plan:** `ask-user-question-interactive-enrichment-b8c3e1.md`
- **Harmonization Plan:** `ask-user-question-author-gate-harmonization-a7e3d2.md`
- **RCA:** `author-gate-canonical-emitter-rca-c7f9d1.md`
- **Rule:** `author-gate-enforcement.md` §"Canonical-emitter invariant"
- **Schema:** `.cursor/schemas/author_gate_packet.schema.json`

---

*Inventory completed 2026-05-09. 5 tiers identified, 6+ files flagged for harmonization.*
