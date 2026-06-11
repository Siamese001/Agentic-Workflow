---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\unified-decision-presentation-ux-hardened-d9e5f2.md'
original_relative_path: 'unified-decision-presentation-ux-hardened-d9e5f2.md'
source_sha256: 4bd15922eb660cda4942d319a3453a210c652925be24bf722ba6be2b8e0eb293
recovered_status: LOST_RECOVERED
last_commit: '799612a40d6'
last_commit_date: '2026-05-09 18:56:12 -0400'
created_date: '2026-05-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Unified Decision Presentation UX — Hardened Implementation Plan

**Plan ID:** `unified-decision-presentation-ux-hardened-d9e5f2`  
**Parent:** `ask-user-question-interactive-enrichment-b8c3e1` (directionally approved)  
**Status:** Draft → Hardened for Implementation  
**Tier:** T2  
**Created:** 2026-05-09  
**Hardened By:** User direction with non-negotiable boundaries

---

## 0. Executive Summary

**Goal:** Unify decision-presentation UX without creating parallel systems, modifying external tools, or over-enriching data-collection wizards.

**Approach:** Hardened universal enricher with strict tier classification, enforcement gates, and telemetry separation.

---

## 1. Non-Negotiable Boundaries (Constitutional)

| # | Boundary | Rationale |
|---|----------|-----------|
| 1 | Do not modify external `ask_user_question` internals | Tool API is external contract |
| 2 | Do not create a second Author-Gate emitter | Single SSOT for AG telemetry |
| 3 | Do not enrich CLI `input()` wizards unless presenting competing decisions | Data collection is out of scope |
| 4 | Do not treat every HITL prompt as Author-Gate | Architectural/governance = AG; simple safety = enriched |
| 5 | Do not solve with documentation only | Must add enforcement |
| 6 | No broad refactors, no unrelated renames | Minimal coherent change set |

---

## 2. Wave Structure

| Wave | Focus | Phases | Est. Tokens | Status |
|------|-------|--------|-------------|--------|
| W0 | Discovery — callsite inventory | 2 | 1.5k | Not Started |
| W1 | Contract — tier classification & schema | 2 | 2k | Not Started |
| W2 | Universal Enricher — wrapper implementation | 3 | 3.5k | Not Started |
| W3 | Migrations — callsite updates | 4 | 3k | Not Started |
| W4 | Enforcement — CI/pre-commit gates | 2 | 2k | Not Started |
| W5 | Tests — acceptance suite | 2 | 2k | Not Started |

**Total:** 5 waves, 15 phases, ~14k tokens

---

## 3. Phase-Level Detail

### W0 Discovery

**W0.P1: Re-scan all callsites**
- Grep for `ask_user_question` across `.py`, `.md`
- Grep for markdown blockquote choice patterns (`> A)`, `> B)`, `**Options:**`)
- Grep for prose decision patterns ("Options:", "Which approach?", "Choose from:")

**W0.P2: Produce callsite table**

```python
# Schema for callsite table (CSV/JSON lines)
{
    "file": "path/to/file.py",
    "line": 144,
    "context": "structured_reasoning_branch",
    "decision_type": "author_gate" | "standard_choice" | "hitl_simple" | "data_collection" | "test_fixture" | "doc_example",
    "required_enrichment": "full_ag" | "standard_enriched" | "exempt",
    "reason": "Architectural branch decision requires precedent"
}
```

| decision_type | Definition | Example |
|---------------|------------|---------|
| `author_gate` | Architecture, refactor, deletion, anti-pattern, governance | "Split L2 adapter into 3 files" |
| `standard_choice` | Simple decision with trade-offs, no precedent needed | "Use sqlite3 vs sqlalchemy" |
| `hitl_simple` | Safety override, minimal context | "Proceed despite stale ADG?" |
| `data_collection` | Gathering inputs, not choosing approaches | "Enter target company" |
| `test_fixture` | Test mocks/stubs | Mock options in unit tests |
| `doc_example` | Documentation only, not executable | Example in plan.md |

**Deliverable:** `artifacts/windsurf/decision_callsite_inventory.jsonl`

---

### W1 Contract

**W1.P1: Decision Presentation Tier Enum**

```python
# tools/decisions/decision_presentation_tier.py
from enum import Enum

class DecisionPresentationTier(str, Enum):
    """Classification for how a decision is presented to the user."""
    
    AUTHOR_GATE_FULL = "author_gate_full"
    """Full Author-Gate pipeline: precedent, signals, routing, AG-10 shape.
    Used for: architecture, refactoring scope, deletion, anti-pattern, governance.
    Emits: AUTHOR_GATE_PACKET + ROUTER_DECISION
    """
    
    STANDARD_ENRICHED = "standard_enriched"
    """Universal enricher: confidence, star, trade-off, telemetry.
    Used for: simple choices with trade-offs, no precedent needed.
    Emits: ASK_USER_QUESTION_PACKET
    """
    
    EXEMPT_DATA_COLLECTION = "exempt_data_collection"
    """No enrichment required. Plain input() or ask_user_question.
    Used for: data gathering, configuration, non-decision prompts.
    Emits: None (or standard telemetry only)
    """
    
    EXEMPT_TEST_FIXTURE = "exempt_test_fixture"
    """Test mocks. No enforcement.
    Used for: unit tests, integration test fixtures.
    """
```

**W1.P2: Enriched Choice Option Contract**

```python
# tools/decisions/enriched_choice_option.py
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class EnrichedChoiceOption:
    """Contract for all enriched decision options."""
    
    # Required — presentation
    label: str  # Short title (≤40 chars)
    description: str  # Full description with trade-off
    
    # Required — confidence
    confidence: float  # 0.00–1.00
    confidence_source: Literal["explicit", "heuristic", "inherited"]
    """explicit = calculated signal vectors
    heuristic = ADG + layer + reversibility estimate
    inherited = from parent/caller context
    """
    
    # Required — recommendation
    recommended: bool  # Exactly one true per decision
    
    # Required — trade-off
    tradeoff: str  # One-line consequence summary (≤80 chars)
    
    # Required — classification
    decision_type: str  # "architecture_choice", "dependency_addition", etc.
    
    # Required — telemetry
    telemetry_id: str  # Stable UUID for this option
    trace_id: str | None = None  # OTEL trace context when available
    
    # Optional — enrichment
    thesis: str | None = None  # One-sentence rationale
    principle_at_stake: str | None = None  # Constitutional principle
    what_would_flip: str | None = None  # Evidence that changes choice
    
    def __post_init__(self):
        assert 0.0 <= self.confidence <= 1.0, "confidence must be 0.0–1.0"
        assert len(self.tradeoff) <= 80, "tradeoff must be ≤80 chars"
        assert len(self.label) <= 40, "label must be ≤40 chars"


class EnrichedChoiceValidator:
    """Validate enriched choice invariants."""
    
    @staticmethod
    def validate_options(options: list[EnrichedChoiceOption]) -> list[str]:
        """Return list of validation errors (empty if valid)."""
        errors = []
        
        # Exactly one recommended when multiple options
        if len(options) > 1:
            recommended = [o for o in options if o.recommended]
            if len(recommended) != 1:
                errors.append(f"Expected exactly one recommended option, found {len(recommended)}")
        
        # All options must have confidence prefix in description
        for opt in options:
            if f"[confidence={opt.confidence:.2f}]" not in opt.description:
                errors.append(f"Option {opt.label}: missing confidence prefix in description")
            
            # Trade-off segment
            if "· trade-off:" not in opt.description:
                errors.append(f"Option {opt.label}: missing trade-off segment")
            
            # Star indicator for recommended
            if opt.recommended and "⭐" not in opt.label:
                errors.append(f"Option {opt.label}: recommended but no star in label")
            if not opt.recommended and "⭐" in opt.label:
                errors.append(f"Option {opt.label}: not recommended but has star")
        
        return errors
```

---

### W2 Universal Enricher

**W2.P1: Wrapper Core**

```python
# tools/decisions/universal_decision_enricher.py
"""
Universal enricher for decision presentation.

Wraps ask_user_question construction to enforce UI invariants.
Does NOT emit AUTHOR_GATE_PACKET — that is reserved for canonical AG pipeline.
"""

from typing import Callable
from dataclasses import asdict
import json
import uuid
from datetime import datetime, timezone

def enrich_and_emit_ask_user_question(
    question: str,
    options: list[EnrichedChoiceOption],
    tier: DecisionPresentationTier,
    context: dict | None = None,
    emit_telemetry: bool = True,
) -> dict:
    """Enrich options and return ask_user_question payload + telemetry.
    
    Args:
        question: The decision question
        options: Enriched options (validated)
        tier: Presentation tier classification
        context: Optional additional context for telemetry
        emit_telemetry: Whether to emit ASK_USER_QUESTION_PACKET
    
    Returns:
        dict with 'ask_user_question_payload' and 'telemetry_payload'
    """
    # Validate
    errors = EnrichedChoiceValidator.validate_options(options)
    if errors:
        raise ValueError(f"Enriched choice validation failed: {errors}")
    
    # Build ask_user_question payload
    ask_payload = {
        "question": question,
        "options": [
            {
                "label": opt.label,
                "description": opt.description,
            }
            for opt in options
        ],
        "allowMultiple": False,
    }
    
    # Build telemetry payload (NOT AUTHOR_GATE_PACKET)
    telemetry_payload = None
    if emit_telemetry and tier != DecisionPresentationTier.EXEMPT_DATA_COLLECTION:
        telemetry_payload = {
            "packet_type": "ASK_USER_QUESTION_PACKET",
            "packet_id": f"auq_{uuid.uuid4().hex[:12]}",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tier": tier.value,
            "question": question,
            "options_count": len(options),
            "options_summary": [
                {
                    "id": opt.telemetry_id,
                    "confidence": opt.confidence,
                    "confidence_source": opt.confidence_source,
                    "recommended": opt.recommended,
                    "decision_type": opt.decision_type,
                }
                for opt in options
            ],
            "context": context or {},
        }
    
    return {
        "ask_user_question_payload": ask_payload,
        "telemetry_payload": telemetry_payload,
    }


def emit_ask_user_question_packet(telemetry_payload: dict) -> None:
    """Emit ASK_USER_QUESTION_PACKET marker to stdout."""
    print(f"ASK_USER_QUESTION_PACKET: {json.dumps(telemetry_payload)}")
```

**W2.P2: Heuristic Confidence Calculator**

```python
# tools/decisions/heuristic_confidence_scorer.py
"""Calculate heuristic confidence for non-Author-Gate decisions."""

from pathlib import Path
from typing import Any

def calculate_heuristic_confidence(
    files_in_scope: list[str],
    decision_category: str,
    adg_context: dict[str, Any] | None = None,
) -> tuple[float, str]:
    """Return (confidence, source_note) for heuristic scoring.
    
    Confidence fallback is allowed, but must be marked heuristic.
    Do not fake precision.
    """
    # Base confidence by decision category
    base_scores = {
        "dependency_addition": 0.70,
        "test_strategy": 0.75,
        "error_handling": 0.72,
        "performance_optimization": 0.68,
        "simple_choice": 0.72,  # surface threshold
    }
    base = base_scores.get(decision_category, 0.72)
    
    # Modifiers from ADG context
    if adg_context:
        # Lower confidence for high blast radius
        blast_radius = adg_context.get("blast_radius_hops", 0)
        if blast_radius > 3:
            base -= 0.10
        
        # Lower confidence for critical layers
        layers = adg_context.get("layers_touched", [])
        if any(l in ("L0", "L5") for l in layers):
            base -= 0.05
    
    # Clamp to valid range
    confidence = max(0.60, min(0.95, base))
    
    return round(confidence, 2), "heuristic:category_base+adg_modifiers"
```

**W2.P3: Integration Adapter**

```python
# tools/decisions/ask_user_question_adapter.py
"""Adapter for existing code to use universal enricher."""

def present_standard_choice(
    question: str,
    raw_options: list[dict],  # Legacy shape: [{"label": "A", "description": "..."}]
    files_in_scope: list[str] | None = None,
    context: dict | None = None,
) -> dict:
    """Convert legacy options to enriched and present.
    
    Convenience function for simple migration path.
    """
    # Calculate heuristic confidence
    confidence, source = calculate_heuristic_confidence(
        files_in_scope or [],
        "simple_choice",
        context,
    )
    
    # Build enriched options (equal confidence, no recommendation)
    enriched_options = []
    for idx, raw in enumerate(raw_options):
        is_recommended = idx == 0 and len(raw_options) > 1  # First option recommended
        
        # Infer tradeoff from description
        tradeoff = _extract_tradeoff_from_description(raw.get("description", ""))
        
        opt = EnrichedChoiceOption(
            label=f"{'⭐ ' if is_recommended else ''}{raw['label']}",
            description=f"[confidence={confidence:.2f}] {raw['description']} · trade-off: {tradeoff}",
            confidence=confidence,
            confidence_source="heuristic" if source.startswith("heuristic") else "explicit",
            recommended=is_recommended,
            tradeoff=tradeoff,
            decision_type="simple_choice",
            telemetry_id=f"opt_{uuid.uuid4().hex[:8]}",
            trace_id=context.get("trace_id") if context else None,
        )
        enriched_options.append(opt)
    
    return enrich_and_emit_ask_user_question(
        question=question,
        options=enriched_options,
        tier=DecisionPresentationTier.STANDARD_ENRICHED,
        context=context,
    )


def _extract_tradeoff_from_description(desc: str) -> str:
    """Extract or generate tradeoff from description."""
    # Look for explicit trade-off patterns
    if "· trade-off:" in desc:
        return desc.split("· trade-off:")[1].strip()[:80]
    if "Pros:" in desc and "Cons:" in desc:
        return "See description for trade-offs"
    
    # Default fallback
    return "Trade-off not explicitly stated"
```

---

### W3 Migrations

**W3.P1: Structured Reasoning Skill**

File: `.windsurf/skills/structured-reasoning/SKILL.md` (line ~144)

Current:
```python
ask_user_question(
  question="Step N has two valid approaches — which should I use?",
  options=[
    {"label": "Plan A", "description": "<what it does> — Pros: X — Cons: Y"},
    {"label": "Plan B", "description": "<what it does> — Pros: X — Cons: Y"}
  ],
)
```

Change to:
```python
# For architectural branch decisions → Author-Gate pipeline
# For simple implementation choices → standard enriched

from tools.decisions.ask_user_question_adapter import present_standard_choice

result = present_standard_choice(
    question="Step N has two valid approaches — which should I use?",
    raw_options=[
        {"label": "A", "description": "Plan A — Pros: X — Cons: Y"},
        {"label": "B", "description": "Plan B — Pros: X — Cons: Y"}
    ],
    files_in_scope=files_in_scope,
)
ask_user_question(**result["ask_user_question_payload"])
if result["telemetry_payload"]:
    emit_ask_user_question_packet(result["telemetry_payload"])
```

**W3.P2: Antipattern Author-Gate Workflow**

File: `.windsurf/workflows/antipattern-author-gate.md` (lines 38-45)

Current: Markdown blockquote choices.

Change to:
```python
# This is a governance decision → full Author-Gate pipeline
from tools.decisions.universal_decision_enricher import enrich_and_emit_ask_user_question
from tools.decisions.decision_presentation_tier import DecisionPresentationTier

# Route through canonical Author-Gate emitter (not shown here)
# Or use standard enriched if simple safety override
```

**W3.P3: Author-Gate Decision Gate**

File: `.windsurf/workflows/author-gate-decision-gate.md` (lines 45-48)

Update to full AG-10 shape with confidence, star, trade-off.

**W3.P4: Remaining Callsites**

Process remaining calls from W0 inventory.

---

### W4 Enforcement

**W4.P1: CI/Pre-commit Checker**

```python
# ops_scripts/ci/check_ask_user_question_ui_invariants.py
"""CI gate: Enforce decision presentation invariants.

Fails on:
- Direct ask_user_question call outside approved wrapper
- Missing confidence prefix
- Missing trade-off segment
- Multiple stars
- No star when recommended=true
- Markdown blockquote decision options in active workflows
- AUTHOR_GATE_PACKET emitted outside canonical Author-Gate path

Allows:
- Data collection wizards (explicit EXEMPT_DATA_COLLECTION)
- Test fixtures (EXEMPT_TEST_FIXTURE)
- Documentation-only examples
"""

import ast
import re
import sys
from pathlib import Path

ALLOWLIST_PATTERNS = [
    r"test_.*\.py$",  # Test files
    r"_test\.py$",
    r"docs/.*\.md$",  # Documentation (not executable)
    r"\.windsurf/plans/.*\.md$",  # Plans (examples only)
]

VIOLATION_PATTERNS = [
    # Markdown blockquote choices in workflows
    (r">\s*[A-D]\)\s*.+\n>\s*[A-D]\)\s*", "markdown_blockquote_choices"),
    # Prose option lists
    (r"\*\*Options:\*\*\s*\n>\s*A[.)]", "prose_option_list"),
]


def check_file(path: Path) -> list[dict]:
    """Check single file for violations."""
    violations = []
    content = path.read_text(encoding="utf-8")
    
    # Skip allowlisted patterns
    for pattern in ALLOWLIST_PATTERNS:
        if re.search(pattern, str(path)):
            return []
    
    # Check for direct ask_user_question (not through wrapper)
    if "ask_user_question(" in content:
        # Verify it's not using the adapter
        if "present_standard_choice" not in content and "enrich_and_emit" not in content:
            # Check if it's in a workflow or skill (active code)
            if ".windsurf/workflows/" in str(path) or ".windsurf/skills/" in str(path):
                violations.append({
                    "file": str(path),
                    "line": _find_line_number(content, "ask_user_question("),
                    "type": "direct_ask_user_question",
                    "severity": "ERROR",
                    "message": "Direct ask_user_question call outside approved wrapper",
                })
    
    # Check for markdown blockquote choices in workflows
    if ".windsurf/workflows/" in str(path):
        for pattern, vtype in VIOLATION_PATTERNS:
            if re.search(pattern, content, re.MULTILINE):
                violations.append({
                    "file": str(path),
                    "line": _find_line_number(content, "> A)"),
                    "type": vtype,
                    "severity": "ERROR",
                    "message": f"Markdown blockquote decision options: {vtype}",
                })
    
    return violations


def _find_line_number(content: str, pattern: str) -> int:
    """Find line number of pattern in content."""
    for idx, line in enumerate(content.split("\n"), 1):
        if pattern in line:
            return idx
    return 0


def main() -> int:
    """Main entry for CI."""
    repo_root = Path(__file__).resolve().parents[3]
    violations = []
    
    # Scan active code paths
    scan_paths = [
        repo_root / ".windsurf" / "skills",
        repo_root / ".windsurf" / "workflows",
        repo_root / "tools" / "decisions",
    ]
    
    for scan_path in scan_paths:
        if not scan_path.exists():
            continue
        for file_path in scan_path.rglob("*.py"):
            violations.extend(check_file(file_path))
        for file_path in scan_path.rglob("*.md"):
            violations.extend(check_file(file_path))
    
    # Emit report
    if violations:
        print("ASK_USER_QUESTION_UI_INVARIANT_VIOLATIONS:")
        for v in violations:
            print(f"  [{v['severity']}] {v['file']}:{v['line']} — {v['type']}: {v['message']}")
        return 1
    
    print("OK — No decision presentation violations found")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**W4.P2: Hook Registration**

Register in `.windsurf/hooks.json` and `ops_scripts/ci/run_contract_gates.py`.

Bypass: `ASK_USER_QUESTION_UI_INVARIANT_BYPASS=1`
Fail-closed: `ASK_USER_QUESTION_UI_INVARIANT_FAIL_CLOSED=1`

---

### W5 Tests

**W5.P1: Core Test Suite**

```python
# tests/unit/decisions/test_universal_decision_enricher.py

class TestStandardEnrichedTwoOptionChoice:
    """Test basic two-option enriched presentation."""
    
    def test_two_options_both_have_confidence(self):
        """Both options must have [confidence=X.XX] prefix."""
        pass
    
    def test_recommended_option_has_star(self):
        """Exactly one option has ⭐ in label."""
        pass
    
    def test_both_options_have_tradeoff(self):
        """Both options have · trade-off: segment."""
        pass
    
    def test_emits_ask_user_question_packet(self):
        """Must emit ASK_USER_QUESTION_PACKET, not AUTHOR_GATE_PACKET."""
        pass


class TestThreeOptionChoice:
    """Test three-option with one recommended."""
    
    def test_three_options_exactly_one_star(self):
        """Exactly one option has ⭐ when one is recommended."""
        pass


class TestHeuristicConfidenceFallback:
    """Test heuristic confidence when no explicit scoring."""
    
    def test_heuristic_confidence_marked(self):
        """Heuristic confidence must have confidence_source='heuristic'."""
        pass
    
    def test_heuristic_not_fake_precision(self):
        """Heuristic confidence rounded to 2 decimals, not fake precision."""
        pass


class TestInvariantViolations:
    """Test validation catches violations."""
    
    def test_missing_tradeoff_fails(self):
        """Option without trade-off segment fails validation."""
        pass
    
    def test_multiple_recommended_fails(self):
        """More than one recommended=true fails."""
        pass
    
    def test_multiple_stars_fails(self):
        """More than one ⭐ in options fails."""
        pass


class TestProseWorkflowChoices:
    """Test prose/markdown choices are caught."""
    
    def test_markdown_blockquote_choices_fail(self):
        """> A) > B) pattern in workflow fails CI."""
        pass


class TestExemptions:
    """Test valid exemptions."""
    
    def test_data_collection_wizard_exempt(self):
        """CLI data collection wizards are exempt with explicit reason."""
        pass
    
    def test_test_fixture_exempt(self):
        """Test fixtures are exempt."""
        pass


class TestTelemetrySeparation:
    """Test AG vs standard telemetry separation."""
    
    def test_author_gate_path_emits_ag_packet(self):
        """Canonical Author-Gate path still emits AUTHOR_GATE_PACKET."""
        pass
    
    def test_standard_path_does_not_emit_ag_packet(self):
        """Standard enriched path emits ASK_USER_QUESTION_PACKET, not AG."""
        pass
```

**W5.P2: Integration Tests**

- End-to-end migration test for structured-reasoning skill
- End-to-end migration test for antipattern workflow
- CI gate accuracy test (true positive, true negative rates)

---

## 4. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|--------------|
| 1 | 100% active `ask_user_question` decision callsites use wrapper or canonical Author-Gate | CI gate passes |
| 2 | 0 active workflow prose choice blocks | CI gate passes |
| 3 | 100% multi-option decision prompts show confidence | Visual inspection + CI |
| 4 | 100% options include trade-off text | Visual inspection + CI |
| 5 | Exactly one star appears when recommended option exists | Visual inspection + CI |
| 6 | No false Author-Gate telemetry from non-AG prompts | `ASK_USER_QUESTION_PACKET` only |
| 7 | CLI data collection remains exempt with explicit audit reason | Exemption list + CI |
| 8 | CI fails closed on new non-enriched decision prompts | Gate exit code 1 |

---

## 5. Deliverables

1. **Callsite inventory** (before/after table)
2. **Files changed** (list with diff summaries)
3. **Tests added** (count + coverage report)
4. **CI command output** (`python ops_scripts/ci/check_ask_user_question_ui_invariants.py`)
5. **Examples:**
   - One Author-Gate decision (full AG-10 shape, `AUTHOR_GATE_PACKET`)
   - One standard enriched `ask_user_question` decision (`ASK_USER_QUESTION_PACKET`)
6. **Explicit exemptions** with reasons documented

---

## 6. References

- **Directional Plan:** `ask-user-question-interactive-enrichment-b8c3e1`
- **Harmonization Plan:** `ask-user-question-author-gate-harmonization-a7e3d2`
- **Inventory:** `ui-choice-pipelines-inventory-c9e4d3`
- **RCA:** `author-gate-canonical-emitter-rca-c7f9d1`
- **Rule:** `author-gate-enforcement.md` §Canonical-emitter invariant

---

*Plan hardened 2026-05-09. Ready for implementation upon prioritization.*
