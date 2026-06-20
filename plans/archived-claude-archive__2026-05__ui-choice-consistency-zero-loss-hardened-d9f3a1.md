---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\ui-choice-consistency-zero-loss-hardened-d9f3a1.md'
original_relative_path: '_archive\\2026-05\\ui-choice-consistency-zero-loss-hardened-d9f3a1.md'
source_sha256: 0a31dcc5d22d8ee6c7608aac7581314274299456de6aa179b706d6c037031394
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# UI Choice Consistency — Zero-Loss Refactor (Hardened)

**Plan ID:** `ui-choice-consistency-zero-loss-hardened-d9f3a1`  
**Status:** Draft  
**Tier:** T2  
**Created:** 2026-05-09  
**Classification:** Zero-Loss Refactor (per prompt directive)  
**Parent:** `ui-choice-consistency-zero-loss-d9e4f2` (superseded by this hardened revision)

---

## Revision Summary

This plan incorporates 8 hardening corrections from review:

1. **Fail policy aligned:** CI mode defaults to fail-closed; advisory only for local/manual
2. **Scanner separation:** New scanner `check_enriched_choice_ui_invariants.py` separate from AG audit
3. **Markdown discipline:** Instruction files get pattern updates, not Python imports
4. **antipattern-author-gate reclassified:** AUTHOR_GATE (governance exception decisions)
5. **Confidence fallback labeled:** `DEFAULT_HEURISTIC_CONFIDENCE = 0.72` with `confidence_source = heuristic_default`
6. **Responsibility split:** Unit tests prove formatting; scanner proves callsite discipline
7. **Concrete telemetry:** Builder returns telemetry packet; caller must emit
8. **Minimal scope preserved:** No docs-only, no CLI wizards, no AG changes, no broad framework

---

## 1. Discovery Callsite Inventory (HARDENED)

### 1.1 Canonical Author-Gate Path (AUTHOR_GATE — Keep As-Is)

| File | Line(s) | Current Pattern | Classification | Reason |
|------|---------|-----------------|----------------|--------|
| `.cursor/skills/author-gate-packet-builder/emit_packet.py` | 1-575 | AUTHOR_GATE_PACKET emitter | AUTHOR_GATE | Canonical emitter; emits 4-invariant options |
| `.cursor/skills/author-gate-ui-renderer/render_card.py` | 43-136 | OPTIONS_JSON builder | AUTHOR_GATE | Renders enriched options from packet |
| `.cursor/scripts/post_cursor_agent_author_gate_ui_audit.py` | 1-362 | UI invariant audit | AUTHOR_GATE | Validates AG 4 invariants only |

**Authority Boundary:** `post_cursor_agent_author_gate_ui_audit.py` stays AG-only. No extension for non-AG choices.

---

### 1.2 Standard Choice Surfaces (ENRICHED_CHOICE)

| File | Line(s) | Current Pattern | Classification | Reason | Planned Change |
|------|---------|-----------------|----------------|--------|----------------|
| `.cursor/skills/structured-reasoning/SKILL.md` | 144-151 | Plain ask_user_question example | ENRICHED_CHOICE | Instruction doc pattern; branch decisions | Update example pattern to show enriched payload (instruction, not executable import) |
| `.cursor/workflows/author-gate-decision-gate.md` | 45-48 | Minimal shape (label/description only) | ENRICHED_CHOICE | Decision-gate instructions | Update example to full enriched shape |

---

### 1.3 AUTHOR_GATE Reclassification (CORRECTED)

| File | Line(s) | Previous Classification | **Corrected Classification** | Reason |
|------|---------|------------------------|------------------------------|--------|
| `.cursor/workflows/antipattern-author-gate.md` | 38-45 | ENRICHED_CHOICE | **AUTHOR_GATE** | Anti-pattern remediation changes governance posture: allows exceptions via `# guardian: allow-<category>`, affects ratchet counts, modifies policy enforcement. These are governance decisions, not lightweight choices. |

**Migration:** `antipattern-author-gate.md` must use canonical Author-Gate pipeline (emit_packet.py), not lightweight enriched wrapper.

---

### 1.4 Exempt Surfaces (UNCHANGED)

| File | Line(s) | Current Pattern | Classification | Reason |
|------|---------|-----------------|----------------|--------|
| `apps_shared/cli/interactive_wizard.py` | 22-32 | Data collection prompts | EXEMPT | Data collection, not decision presentation |
| `tests/governance/test_hitl_validators.py` | Various | Mock options | EXEMPT | Test fixtures |
| `tests/unit/author_gate/test_author_gate_ui_audit.py` | 37-44 | Synthetic response builder | EXEMPT | Test helper |
| Plan markdown files | Various | Documentation examples | EXEMPT | Docs-only, not executable |

---

## 2. Implementation (HARDENED)

### 2.1 Helper: `tools/decisions/enriched_choice_builder.py`

**Interface:**
```python
DEFAULT_HEURISTIC_CONFIDENCE: float = 0.72

def build_enriched_choice_question(
    question: str,
    options: list[dict[str, Any]],  # Each needs: id, label, description, tradeoff, optional: confidence
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> dict[str, Any]:
    """
    Build enriched ask_user_question payload with UI invariants.
    
    Returns dict with keys:
    - question: str (enriched header)
    - options: list[dict] (formatted label/description)
    - telemetry_packet: dict (ASK_USER_QUESTION_PACKET shape)
    
    Caller MUST emit telemetry_packet via print/log.
    Builder does NOT emit telemetry directly.
    """
```

**Formatting Rules:**
- Label: `"⭐ A [confidence=0.88] <label_text>"` (if recommended) or `"B [confidence=0.72] <label_text>"`
- Description: `"[confidence=0.88] · trade-off: <text> · <description>"`
- Star rules: Exactly one ⭐ when recommendation exists; zero when none
- Confidence handling:
  - If explicit confidence provided: use it, set `confidence_source = "explicit"`
  - If no confidence: use `DEFAULT_HEURISTIC_CONFIDENCE`, set `confidence_source = "heuristic_default"`
- Trade-off: Required; raises `ValueError` if missing

**Telemetry Packet Shape:**
```python
{
    "packet_type": "ASK_USER_QUESTION_PACKET",
    "context": telemetry_context or "enriched_choice",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "option_count": len(options),
    "recommended_index": recommended_index,  # or None
    "confidence_source": "explicit" | "heuristic_default",
    "invariants": ["confidence_prefix", "tradeoff_segment", "star_marker"],
}
```

---

### 2.2 Scanner: `ops_scripts/ci/check_enriched_choice_ui_invariants.py` (NEW)

**Design Principle:** Scanner enforces callsite discipline, not runtime formatting.

**Checks (Callsite-Level):**

| Check | Rule | Severity |
|-------|------|----------|
| 1 | Active decision prompts must use either Author-Gate pipeline OR `build_enriched_choice_question()` | critical |
| 2 | Raw `ask_user_question` in decision context without wrapper is a violation | critical |
| 3 | Markdown prose option blocks in active workflow files are violations | high |
| 4 | `AUTHOR_GATE_PACKET` appearing outside canonical AG path is a violation | critical |
| 5 | Files without exemption reason must not use plain ask_user_question for decisions | high |

**Exemption Allowlist (Narrow, Path-Scoped, Auditable):**

```python
_EXEMPTIONS: dict[str, str] = {
    "apps_shared/cli/interactive_wizard.py": "data_collection_field_input",
    "tests/": "test_fixture",
    "docs/": "documentation_example",
    ".cursor/plans/": "plan_documentation",
    # Any addition requires explicit reason and narrow path scope
}
```

**Fail Policy (CORRECTED per Review):**
- **CI/Pre-commit mode:** `ENRICHED_CHOICE_UI_FAIL_CLOSED=1` is **default** (exit 1 on violation)
- **Local/Manual mode:** Advisory (exit 0, log only) only when explicitly requested
- No ambiguous advisory-by-default in CI

---

### 2.3 Responsibility Split (NEW)

| Layer | Responsibility | How Verified |
|-------|----------------|------------|
| **Unit tests** | Builder formatting invariants (confidence prefix, star count, trade-off) | `tests/unit/tools/decisions/test_enriched_choice_builder.py` |
| **Scanner** | Callsite discipline (AG pipeline or wrapper used) | `check_enriched_choice_ui_invariants.py` source scan |
| **Runtime audit** | Emitted packet validation (if telemetry available) | `post_cursor_agent_ask_user_question_packet_audit.py` (existing, extended) |

---

### 2.4 Migration of Active Surfaces

#### A. structured-reasoning/SKILL.md (Lines 144-151) — INSTRUCTION UPDATE

**Before:**
```markdown
ask_user_question(
  question="Step N has two valid approaches — which should I use?",
  options=[
    {"label": "Plan A", "description": "<what it does> — Pros: X — Cons: Y"},
    {"label": "Plan B", "description": "<what it does> — Pros: X — Cons: Y"}
  ],
)
```

**After:**
```markdown
Use `build_enriched_choice_question()` from `tools/decisions/enriched_choice_builder.py`:

```python
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
            # confidence omitted → uses DEFAULT_HEURISTIC_CONFIDENCE
        },
    ],
    recommended_id="A",
    telemetry_context="structured-reasoning-branch",
)
ask_user_question(
    question=payload["question"],
    options=payload["options"],
)
print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))
```

**Format:**
- Label: `"⭐ A [confidence=0.88] Plan A: Evidence-first retrieval"`
- Description: `"[confidence=0.88] · trade-off: Slower start but zero false-positive edits · Pulls ADG..."`
- Telemetry: Caller emits `ASK_USER_QUESTION_PACKET` with returned packet
```

---

#### B. author-gate-decision-gate.md (Lines 45-48) — INSTRUCTION UPDATE

**Update minimal shape example to show enriched payload pattern.**

---

#### C. antipattern-author-gate.md (CORRECTED — Use Author-Gate)

**Classification Change:** This is AUTHOR_GATE, not ENRICHED_CHOICE.

**Reason:** Anti-pattern remediation involves governance exceptions (`# guardian: allow-<category>`), ratchet count changes, and policy enforcement modifications. These are high-stakes governance decisions.

**Implementation:**
```markdown
### Step 2 — STOP and invoke Author-Gate

**Before proceeding**, build an Author-Gate packet via `emit_packet.py`:

```bash
# Build spec JSON with candidates A-D
cat << 'EOF' | python .cursor/skills/author-gate-packet-builder/emit_packet.py
{
  "decision_type": "anti_pattern",
  "normalized_intent": "anti-pattern remediation",
  "candidates": [
    {"id": "A", "thesis": "Narrow exception types", "confidence_score": 0.92, ...},
    {"id": "B", "thesis": "Add guardian exemption", "confidence_score": 0.78, ...},
    ...
  ]
}
EOF
```

Use the emitted `OPTIONS_JSON` with `ask_user_question`.
```

---

## 3. Tests (HARDENED)

### 3.1 Unit Tests: `tests/unit/tools/decisions/test_enriched_choice_builder.py`

| Test | Scenario | Invariant |
|------|----------|-----------|
| 1 | Two-option enriched question | Options have correct label format |
| 2 | Three-option enriched question | All options have trade-off segment |
| 3 | Recommended option has exactly one star | Star count = 1 |
| 4 | No recommendation allows zero stars | Star count = 0 |
| 5 | Multiple stars fails validation | Raises ValueError |
| 6 | Explicit confidence preserved | confidence_source = "explicit" |
| 7 | Missing confidence uses DEFAULT_HEURISTIC_CONFIDENCE | confidence_source = "heuristic_default" |
| 8 | Missing trade-off raises ValueError | Required field validation |
| 9 | Telemetry packet returned with correct shape | packet_type = ASK_USER_QUESTION_PACKET |
| 10 | AUTHOR_GATE_PACKET never in telemetry | Packet type invariant |
| 11 | Telemetry context preserved | context field matches input |

### 3.2 Scanner Tests: `tests/unit/ops_scripts/ci/test_check_enriched_choice_ui_invariants.py`

| Test | Scenario | Scanner Check |
|------|----------|---------------|
| 12 | Raw ask_user_question in decision context | Fails (critical) |
| 13 | Markdown prose options in workflow | Fails (high) |
| 14 | Exemption allowlist entry passes | data_collection exemption |
| 15 | AUTHOR_GATE_PACKET outside AG path | Fails (critical) |
| 16 | Author-Gate canonical path passes | AG pipeline allowed |
| 17 | Enriched wrapper usage passes | build_enriched_choice_question allowed |
| 18 | CI mode fail-closed by default | Exit 1 on violation |
| 19 | Manual mode advisory allowed | Exit 0 when explicitly requested |

---

## 4. Revised Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | AG audit remains green | `post_cursor_agent_author_gate_ui_audit.py` passes |
| 2 | New scanner is fail-closed in CI | `ENRICHED_CHOICE_UI_FAIL_CLOSED=1` default; exit 1 on violation |
| 3 | Active decision prompts are AUTHOR_GATE or ENRICHED_CHOICE | Scanner passes on all active surfaces |
| 4 | Exemptions narrow and reasoned | `_EXEMPTIONS` dict auditable |
| 5 | Standard choices emit ASK_USER_QUESTION_PACKET only | Tests assert telemetry packet type |
| 6 | Author-Gate remains only AUTHOR_GATE_PACKET path | Scanner check 4 + AG audit separation |
| 7 | Confidence fallback labeled | `confidence_source = heuristic_default` in telemetry |
| 8 | Telemetry concrete, not comment | Tests assert returned telemetry packet |
| 9 | Markdown files get pattern updates | Instruction examples updated, no fake imports |
| 10 | antipattern-author-gate uses AG | Classification corrected, uses canonical pipeline |

---

## 5. Non-Goals (Reaffirmed)

| Exclusion | Reason |
|-----------|--------|
| No broad DecisionPresentation framework | Per prompt: minimal implementation only |
| No changes to external ask_user_question tool | Tool API is external; we wrap |
| No enrichment of data-collection wizards | `interactive_wizard.py` exempt |
| No changes to Author-Gate scoring | AG pipeline unchanged |
| No migration of test fixtures | Tests exempt |
| No docs-only fixes | Executable workflows only |
| No scanner merger | AG and non-AG stay separate |

---

## 6. Wave Structure

| Wave | Focus | Phases | Est. Tokens | Status |
|------|-------|--------|-------------|--------|
| W1 | Helper + Unit Tests | 2 | 2.5k | Not Started |
| W2 | Scanner + CI Gate + Scanner Tests | 2 | 3k | Not Started |
| W3 | Migration (SKILL.md, decision-gate, antipattern-AG) | 2 | 1.5k | Not Started |
| W4 | Integration + Verification | 2 | 1k | Not Started |

---

## 7. References

- **Original Plan:** `ui-choice-consistency-zero-loss-d9e4f2.md` (superseded)
- **Hardening Prompt:** User review corrections (8 items)
- **Inventory:** `ui-choice-pipelines-inventory-c9e4d3.md`
- **SSOT Folders:** `ssot-folder-enforcement.md`
- **AG Authority:** `author-gate-enforcement.md`

---

*Hardened plan created 2026-05-09. Incorporates all 8 review corrections. Implementation pending.*
