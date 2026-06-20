---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\ui-choice-consistency-zero-loss-d9e4f2.md'
original_relative_path: '_archive\\2026-05\\ui-choice-consistency-zero-loss-d9e4f2.md'
source_sha256: bb056150e4556f840d57eb6342649f1e48390c122d4f648d860a9a3f3d0a4834
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# UI Choice Consistency — Zero-Loss Refactor

**Plan ID:** `ui-choice-consistency-zero-loss-d9e4f2`  
**Status:** Draft  
**Tier:** T2  
**Created:** 2026-05-09  
**Classification:** Zero-Loss Refactor (per prompt directive)

---

## 1. Discovery Callsite Inventory (COMPLETE)

### 1.1 Canonical Author-Gate Path (AUTHOR_GATE — Keep As-Is)

| File | Line(s) | Current Pattern | Classification | Reason |
|------|---------|-----------------|----------------|--------|
| `.cursor/skills/author-gate-packet-builder/emit_packet.py` | 1-575 | AUTHOR_GATE_PACKET emitter | AUTHOR_GATE | Canonical emitter; emits 4-invariant options with confidence prefix, star, trade-off |
| `.cursor/skills/author-gate-ui-renderer/render_card.py` | 43-136 | OPTIONS_JSON builder | AUTHOR_GATE | Renders enriched options from packet; 4-invariants enforced |
| `.cursor/scripts/post_cursor_agent_author_gate_ui_audit.py` | 1-362 | UI invariant audit | AUTHOR_GATE | Validates confidence prefix, star count, trade-off segment |

**Audit:** These already emit and enforce all 4 invariants. No changes required.

---

### 1.2 Standard Choice Surfaces Needing Enrichment (ENRICHED_CHOICE)

| File | Line(s) | Current Pattern | Classification | Reason | Planned Change |
|------|---------|-----------------|----------------|--------|----------------|
| `.cursor/skills/structured-reasoning/SKILL.md` | 144-151 | Plain `ask_user_question` with pros/cons in description | ENRICHED_CHOICE | Branch resolution decisions; not architecture-scale | Convert to `build_enriched_choice_question()` with confidence/trade-off |
| `.cursor/workflows/antipattern-author-gate.md` | 38-45 | Markdown blockquote prose options | ENRICHED_CHOICE | Anti-pattern remediation choices; governance scope but lightweight | Convert to `ask_user_question` + `build_enriched_choice_question()` |
| `.cursor/workflows/author-gate-decision-gate.md` | 45-48 | Minimal shape (label/description only) | ENRICHED_CHOICE | Decision-gate instructions; needs confidence/trade-off upgrade | Update example to full enriched shape |

---

### 1.3 Exempt Surfaces (EXEMPT)

| File | Line(s) | Current Pattern | Classification | Reason |
|------|---------|-----------------|----------------|--------|
| `apps_shared/cli/interactive_wizard.py` | 22-32 | Data collection prompts (company, description, briefing) | EXEMPT | Data collection, not decision presentation |
| `tests/governance/test_hitl_validators.py` | Various | Mock options for validation | EXEMPT | Test fixtures |
| `tests/unit/author_gate/test_author_gate_ui_audit.py` | 37-44 | Synthetic response builder `_make_response` | EXEMPT | Test helper |
| Plan markdown files | Various | Documentation examples | EXEMPT | Docs-only, not executable |

---

### 1.4 Existing Scanner/Audit Hooks (Reusable)

| File | Purpose | Coverage Gap |
|------|---------|--------------|
| `post_cursor_agent_author_gate_ui_audit.py` | Validates 4 invariants for AG decisions | Does NOT audit native ask_user_question |
| `post_cursor_agent_ask_user_question_packet_audit.py` | Detects missing AUTHOR_GATE_PACKET | Does NOT enforce UI invariants |
| `check_ask_user_question_packet_freshness.py` | CI freshness check for packet violations | Does NOT check UI conformance |

**Gap:** No scanner enforces UI invariants on non-AG ask_user_question calls.

---

## 2. Implementation Plan

### 2.1 Helper: `build_enriched_choice_question()`

**Location:** `tools/decisions/enriched_choice_builder.py`

**Rationale:** Per SSOT folder enforcement (`ssot-folder-enforcement.md`), general utilities go to `tools/<domain>/`. Decision presentation is a new domain.

**Interface:**
```python
def build_enriched_choice_question(
    question: str,
    options: list[dict[str, Any]],  # Each needs: id, label, description, tradeoff, optional confidence
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> dict[str, Any]:
    """
    Build an enriched ask_user_question payload with UI invariants.
    
    Returns dict with:
    - question: str (enriched header)
    - options: list[dict] (formatted label/description with confidence, star, trade-off)
    - telemetry_marker: str (ASK_USER_QUESTION_PACKET ready)
    """
```

**Formatting Rules:**
- Label: `"⭐ A [confidence=0.88] <label_text>"` (if recommended) or `"B [confidence=0.72] <label_text>"`
- Description: `"[confidence=0.88] · trade-off: <text> · <description>"`
- Star rules: Exactly one ⭐ when recommendation exists; zero when none
- Confidence fallback: `0.72` (surface threshold) when not provided
- Trade-off: Required; raises if missing

**Telemetry:**
- Emits `ASK_USER_QUESTION_PACKET:` with context id, timestamp, option count, recommended index
- **NEVER** emits `AUTHOR_GATE_PACKET:`

---

### 2.2 Scanner: Extend `post_cursor_agent_author_gate_ui_audit.py`

**Change:** Add new invariants 6-10 for standard enriched choices:

| Invariant | Rule | Severity |
|-----------|------|----------|
| 6 | All ask_user_question calls in decision context must have enriched format (confidence prefix) | high |
| 7 | Raw/plain ask_user_question for decision prompts fails scanner | high |
| 8 | Markdown prose option blocks in active workflows fail scanner | high |
| 9 | ASK_USER_QUESTION_PACKET must be present for enriched choices | medium |
| 10 | AUTHOR_GATE_PACKET must NOT appear outside canonical AG path | critical |

**Allowlist mechanism:**
```python
_EXEMPT_PATHS = {
    "apps_shared/cli/interactive_wizard.py": "data_collection",
    "tests/": "test_fixture",
    "docs/": "docs_example",
    ".cursor/plans/": "docs_example",
}
```

---

### 2.3 Migration of Active Surfaces

#### A. structured-reasoning/SKILL.md (Lines 144-151)

**Before:**
```python
ask_user_question(
  question="Step N has two valid approaches — which should I use?",
  options=[
    {"label": "Plan A", "description": "<what it does> — Pros: X — Cons: Y"},
    {"label": "Plan B", "description": "<what it does> — Pros: X — Cons: Y"}
  ],
  allowMultiple=False
)
```

**After:**
```python
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

payload = build_enriched_choice_question(
    question="Step N has two valid approaches — which should I use?",
    options=[
        {
            "id": "A",
            "label": "Plan A: Evidence-first retrieval",
            "description": "Pulls ADG/materialized views before editing",
            "tradeoff": "Slower start but zero false-positive edits",
            "confidence": 0.88,
        },
        {
            "id": "B", 
            "label": "Plan B: Direct edit",
            "description": "Edits immediately based on grep/code_search",
            "tradeoff": "Faster but risks edits without structural context",
            "confidence": 0.72,
        },
    ],
    recommended_id="A",
    telemetry_context="structured-reasoning-branch",
)
ask_user_question(
    question=payload["question"],
    options=payload["options"],
    allowMultiple=False,
)
# Telemetry emitted via build_enriched_choice_question:
# ASK_USER_QUESTION_PACKET: {...}
```

#### B. antipattern-author-gate.md (Lines 38-45)

**Before:** Markdown blockquote prose options.

**After:** Convert to enriched ask_user_question:
```python
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

payload = build_enriched_choice_question(
    question=f"Anti-pattern remediation: {category} in {file}",
    options=[
        {
            "id": "A",
            "label": "Narrow exception types",
            "description": "Use (ImportError, AttributeError, OSError) — no guardian comment",
            "tradeoff": "Cleanest code, no ratchet increase, but requires specific exception knowledge",
            "confidence": 0.92,
        },
        {
            "id": "B",
            "label": "Add guardian exemption",
            "description": "Add # guardian: allow-<category> on preceding line",
            "tradeoff": "Counted in ratchet but exempt from blocking; audit trail preserved",
            "confidence": 0.78,
        },
        # ... C and D
    ],
    recommended_id="A",
    telemetry_context="antipattern-remediation",
)
ask_user_question(...)
```

#### C. author-gate-decision-gate.md (Lines 45-48)

**Update the minimal shape example to full enriched shape.**

---

### 2.4 CI Scanner: `check_enriched_choice_ui_invariants.py`

**Location:** `ops_scripts/ci/check_enriched_choice_ui_invariants.py`

**Checks:**
1. No raw ask_user_question in decision context (outside AG pipeline)
2. No markdown prose option blocks in workflows
3. Confidence prefix present on all enriched options
4. Trade-off segment present on all enriched options
5. Star count = 1 when recommendation exists; 0 when none
6. ASK_USER_QUESTION_PACKET present for enriched choices
7. AUTHOR_GATE_PACKET never appears outside canonical AG path

**Fail policy:** OPEN (advisory) by default; `ENRICHED_CHOICE_UI_FAIL_CLOSED=1` for strict.

---

## 3. Tests

### 3.1 Unit Tests: `tests/unit/tools/decisions/test_enriched_choice_builder.py`

| Test | Scenario |
|------|----------|
| 1 | Standard two-option enriched question passes |
| 2 | Three-option enriched question passes |
| 3 | Recommended option has exactly one star |
| 4 | No recommendation allows zero stars |
| 5 | Multiple stars fail validation |
| 6 | Missing confidence uses fallback (0.72) |
| 7 | Missing trade-off raises ValueError |
| 8 | ASK_USER_QUESTION_PACKET emitted with correct shape |
| 9 | AUTHOR_GATE_PACKET never emitted |
| 10 | Telemetry context preserved in packet |

### 3.2 Scanner Tests: `tests/unit/ops_scripts/ci/test_check_enriched_choice_ui_invariants.py`

| Test | Scenario |
|------|----------|
| 11 | Raw ask_user_question in decision context fails scanner |
| 12 | Markdown prose options in workflow fails scanner |
| 13 | Missing confidence prefix fails scanner |
| 14 | Missing trade-off fails scanner |
| 15 | CLI data-collection wizard exemption passes |
| 16 | Docs-only example exemption passes |
| 17 | Author-Gate path still emits AUTHOR_GATE_PACKET (allowed) |
| 18 | Enriched choice emits ASK_USER_QUESTION_PACKET only |

---

## 4. Wave Structure

| Wave | Focus | Phases | Est. Tokens | Status |
|------|-------|--------|-------------|--------|
| W1 | Helper implementation | 2 | 2k | Not Started |
| W2 | Scanner extension + CI gate | 2 | 2.5k | Not Started |
| W3 | Migration of 3 active surfaces | 2 | 1.5k | Not Started |
| W4 | Tests + verification | 2 | 2k | Not Started |

---

## 5. Before/After Examples

### 5.1 Author-Gate Decision (UNCHANGED — Canonical Path)

**Before & After (Same):**
```python
# Author-Gate pipeline (existing, unchanged)
# emit_packet.py → render_card.py → ask_user_question

AUTHOR_GATE_PACKET: {
  "decision_id": "dec_abc123",
  "candidates": [
    {
      "id": "A",
      "surface_description": "[RECOMMENDED ⭐ confidence=0.90] · trade-off: Gains X, loses Y · ...",
      ...
    }
  ]
}
```

**Telemetry:** `AUTHOR_GATE_PACKET:` + `ROUTER_DECISION:`

---

### 5.2 Standard Enriched Choice (NEW — Lightweight Path)

**Before:**
```python
ask_user_question(
    question="Which approach?",
    options=[
        {"label": "Plan A", "description": "Pros: fast — Cons: risky"},
        {"label": "Plan B", "description": "Pros: safe — Cons: slow"},
    ]
)
```

**After:**
```python
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

payload = build_enriched_choice_question(
    question="Which approach?",
    options=[
        {
            "id": "A",
            "label": "Fast approach",
            "description": "Quick implementation",
            "tradeoff": "Fast execution but higher risk of edge-case misses",
            "confidence": 0.74,
        },
        {
            "id": "B",
            "label": "Safe approach", 
            "description": "Conservative implementation",
            "tradeoff": "Slower but validates all assumptions",
            "confidence": 0.88,
        },
    ],
    recommended_id="B",
)
ask_user_question(
    question=payload["question"],
    options=payload["options"],
)
# Emits: ASK_USER_QUESTION_PACKET: {...}
```

---

## 6. Non-Goals (Explicitly Excluded)

| Exclusion | Reason |
|-----------|--------|
| No broad DecisionPresentation framework | Per prompt: "Do not implement a broad DecisionPresentation framework unless discovery proves it already exists" |
| No changes to external ask_user_question tool | API is external; we wrap, not modify |
| No enrichment of data-collection wizards | `interactive_wizard.py` is field collection, not decision presentation |
| No changes to Author-Gate scoring logic | AG pipeline remains unchanged |
| No migration of test fixtures | Tests are fixtures, not active surfaces |
| No docs-only fixes | Executable workflows only |

---

## 7. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | Existing canonical Author-Gate remains only AG packet path | `test_author_gate_ui_audit.py` passes |
| 2 | Standard ask_user_question uses one lightweight enrichment wrapper | `test_enriched_choice_builder.py` passes |
| 3 | Active multi-option prompts show confidence | Scanner invariant 6 |
| 4 | Active prompts include trade-off text | Scanner invariant 7 |
| 5 | Recommended decisions show exactly one ⭐ | Scanner invariant 8 |
| 6 | Workflow prose option blocks gone | Scanner invariant 9 |
| 7 | CLI data collection remains exempt | Allowlist test passes |
| 8 | No false AG telemetry introduced | Scanner invariant 10 |
| 9 | CI scanner fails closed on raw prompts | `ENRICHED_CHOICE_UI_FAIL_CLOSED=1` test passes |

---

## 8. References

- **Prompt Source:** Zero-loss refactor prompt (this document)
- **Inventory:** `ui-choice-pipelines-inventory-c9e4d3.md`
- **Enrichment Plan:** `ask-user-question-interactive-enrichment-b8c3e1.md`
- **SSOT Folders:** `ssot-folder-enforcement.md`
- **Canonical AG:** `author-gate-enforcement.md` §"Canonical-emitter invariant"

---

*Plan created 2026-05-09. Status: Discovery complete. Implementation pending.*
