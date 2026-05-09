# Enriched Choice Builder API

**Module:** `tools.decisions.enriched_choice_builder`  
**Classification:** ENRICHED_CHOICE (non-governance decisions)  
**Authority:** Emits `ASK_USER_QUESTION_PACKET` (never `AUTHOR_GATE_PACKET`)

---

## Overview

The enriched choice builder provides UI invariants for non-governance decisions:
- Confidence prefix `[confidence=X.XX]` in question text
- ⭐ indicator on recommended option
- Trade-off segment in every option description
- Telemetry packet emission for analytics

---

## Functions

### `build_enriched_choice_question()`

```python
def build_enriched_choice_question(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: dict[str, Any] | None = None,
) -> dict[str, Any]
```

Builds an enriched choice question with UI invariants enforced.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | `str` | Yes | Base question text (confidence prefix added automatically) |
| `options` | `list[dict]` | Yes | List of option dicts (2-4 options) |
| `recommended_id` | `str \| None` | No | ID of recommended option (⭐ added) |
| `telemetry_context` | `dict \| None` | No | Additional context for telemetry |

**Option Dictionary Shape:**

```python
{
    "id": str,                 # Unique identifier (A, B, C...)
    "label": str,              # Short label (≤120 chars)
    "description": str,        # Detailed description (≤240 chars)
    "tradeoff": str,           # Trade-off statement (required)
    "confidence": float,       # 0.0-1.0 (auto-set if missing)
}
```

**Returns:**

```python
{
    "question": str,           # With confidence prefix
    "options": list[dict],     # With ⭐ and trade-off segments
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
            "tradeoff": "Higher technical debt, may need refactoring later",
        },
        {
            "id": "B",
            "label": "Thorough approach — comprehensive solution",
            "description": "Full implementation with tests and docs",
            "tradeoff": "Takes longer, more upfront complexity",
        },
    ],
    recommended_id="A",
    telemetry_context={"decision": "implementation_approach"},
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
            "tradeoff": "Higher impact but more complex blast radius",
        },
        {
            "id": "B",
            "label": f"{node_b['name']} — safer target",
            "description": f"Centrality: {node_b['centrality']:.2f}",
            "tradeoff": "Lower risk but less structural impact",
        },
    ],
    recommended_id="A" if node_a["centrality"] > node_b["centrality"] else None,
    telemetry_context={"adg_analysis": "hotspot_selection"},
)
```

---

## UI Invariants

| Invariant | Enforcement |
|-----------|-------------|
| Confidence prefix | `[confidence=X.XX]` prepended to question |
| ⭐ indicator | Added to recommended option label only |
| Trade-off segment | `· trade-off: <text>` in every description |
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
    "question_hash": str,                       # SHA-256 of question
    "options_count": int,
    "has_recommended": bool,
    "confidence_values": list[float],
    "confidence_source": "explicit" | "heuristic_default",
    "context": dict,                            # Caller-provided context
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
- Emits: `AUTHOR_GATE_PACKET`

Use `.windsurf/skills/author-gate-packet-builder/emit_packet.py` for governance decisions.

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
- `AUTHOR_GATE_PACKET` outside AG pipeline (FAIL)

---

## References

- **Plan:** `ui-choice-consistency-zero-loss-hardened-d9f3a1.md`
- **Scanner:** `ops_scripts/ci/check_enriched_choice_ui_invariants.py`
- **Tests:** `tests/unit/tools/decisions/test_enriched_choice_builder.py`
- **Integration:** `tests/integration/test_ui_choice_integration.py`
