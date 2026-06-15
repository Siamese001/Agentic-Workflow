# Enriched Choice Builder API

**Module:** `tools.decisions.enriched_choice_builder`  
**Classification:** ENRICHED_CHOICE (non-governance decisions)  
**Authority:** Emits `ASK_USER_QUESTION_PACKET` (never `AUTHOR_GATE_PACKET`)

---

## Overview

The enriched choice builder provides UI invariants for non-governance decisions:
- Recommended option appears first and its label ends `(Recommended)`
- Confidence prefix in every option description
- `[RECOMMENDED ⭐ confidence=X.XX]` prefix on the recommended description
- Pros and Cons segments in every option description
- Telemetry packet emission for analytics

---

## Functions

### `build_enriched_choice_question()`

```python
def build_enriched_choice_question(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> dict[str, Any]
```

Builds an enriched choice question with UI invariants enforced.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | `str` | Yes | Base question text (confidence prefix added automatically) |
| `options` | `list[dict]` | Yes | List of option dicts (2-4 options) |
| `recommended_id` | `str \| None` | No | ID of recommended option (⭐ added) |
| `telemetry_context` | `str \| None` | No | Context slug for telemetry |

**Option Dictionary Shape:**

```python
{
    "id": str,                 # Unique identifier (A, B, C...)
    "label": str,              # Short label (≤120 chars)
    "description": str,        # Detailed description (≤240 chars)
    "tradeoff": str,           # Trade-off statement (required)
    "pros": str,               # Optional; derived from description/tradeoff if omitted
    "cons": str,               # Optional; derived from tradeoff if omitted
    "flip_condition": str,     # Optional; recommended option only
    "confidence": float,       # 0.0-1.0 (auto-set if missing)
}
```

**Returns:**

```python
{
    "question": str,
    "options": list[dict],     # With confidence, pros/cons, and recommendation marker
    "telemetry_packet": dict,  # For ASK_USER_QUESTION_PACKET emission
}
```

---

## Usage Examples

### Basic Two-Option Decision

```python
from tools.decisions.enriched_choice_builder import build_enriched_choice_question

payload = build_enriched_choice_question(
    question="Which approach should I use?",
    options=[
        {
            "id": "A",
            "label": "Fast approach — quick implementation",
            "description": "Implements quickly with minimal scaffolding",
            "pros": "Fastest path to a working implementation",
            "cons": "May need refactoring later",
            "tradeoff": "Faster delivery but higher technical debt",
        },
        {
            "id": "B",
            "label": "Thorough approach — comprehensive solution",
            "description": "Full implementation with tests and docs",
            "pros": "Tests and docs land with the change",
            "cons": "Takes longer and adds upfront complexity",
            "tradeoff": "Takes longer but validates the behavior",
            "flip_condition": "the change is isolated to one low-risk file",
        },
    ],
    recommended_id="A",
    telemetry_context="implementation-approach",
)

# Emit telemetry (REQUIRED)
print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))

# Present to user
ask_user_question(
    question=payload["question"],
    options=payload["options"],
    allowMultiple=False,
)
```

### ADG-Driven Branch Resolution

```python
# When ADG shows multiple hotspot candidates
payload = build_enriched_choice_question(
    question="ADG shows multiple hotspots. Which should I refactor first?",
    options=[
        {
            "id": "A",
            "label": f"{node_a['name']} — higher fan-in",
            "description": f"Centrality: {node_a['centrality']:.2f}",
            "pros": "Higher structural impact",
            "cons": "More complex blast radius",
            "tradeoff": "Higher impact but more complex blast radius",
        },
        {
            "id": "B",
            "label": f"{node_b['name']} — safer target",
            "description": f"Centrality: {node_b['centrality']:.2f}",
            "pros": "Lower implementation risk",
            "cons": "Less structural impact",
            "tradeoff": "Lower risk but less structural impact",
        },
    ],
    recommended_id="A" if node_a["centrality"] > node_b["centrality"] else None,
    telemetry_context="hotspot-selection",
)
```

---

## UI Invariants

| Invariant | Enforcement |
|-----------|-------------|
| Recommendation marker | Recommended option label ends `(Recommended)` and is first |
| Confidence prefix | `[confidence=X.XX]` in every description; recommended uses `[RECOMMENDED ⭐ confidence=X.XX]` |
| Pros/Cons segment | `Pros: <text>. Cons: <text>.` in every description |
| Label length | Capped at 120 characters |
| Description length | Capped at 240 characters |
| Confidence clamping | 0.0-1.0 range enforced |
| Single recommendation | Exactly one ⭐ if `recommended_id` set |

---

## Telemetry Packet

The `telemetry_packet` field contains:

```python
{
    "packet_type": "ASK_USER_QUESTION_PACKET",  # Never AUTHOR_GATE_PACKET
    "timestamp": str,                           # ISO format
    "question": str,
    "option_count": int,
    "recommended_index": int | null,
    "confidence_score": float | null,
    "options": list[dict],
    "confidence_source": "explicit" | "heuristic_default",
    "context": str,
}
```

---

## Authority Boundary

**ENRICHED_CHOICE** (this builder):
- Branch resolution when evidence inconclusive
- ADG-driven hotspot selection
- Non-governance implementation choices
- Emits: `ASK_USER_QUESTION_PACKET`

**AUTHOR_GATE** (governance decisions):
- Refactoring scope decisions
- Architecture choices
- Anti-pattern introduction
- Dependency additions
- Uses native `AskUserQuestion` with the `.claude/skills/ask-user-question-recommendation`
  option-shape convention

Use `.claude/skills/ask-user-question-recommendation/SKILL.md` for governance decisions.

---

## Scanner Validation

Files using this builder are validated by:

```bash
python ops_scripts/ci/check_enriched_choice_ui_invariants.py <file> --advisory
```

The scanner checks:
- Raw `ask_user_question` without wrapper (FAIL)
- Missing `ASK_USER_QUESTION_PACKET` emission (FAIL)
- Markdown prose options in active surfaces (FAIL)
- Retired packet markers outside archived docs (FAIL)

---

## References

- **Plan:** `ui-choice-consistency-zero-loss-hardened-d9f3a1.md`
- **Scanner:** `ops_scripts/ci/check_enriched_choice_ui_invariants.py`
- **Tests:** `tests/unit/tools/decisions/test_enriched_choice_builder.py`
- **Integration:** `tests/integration/test_ui_choice_integration.py`
