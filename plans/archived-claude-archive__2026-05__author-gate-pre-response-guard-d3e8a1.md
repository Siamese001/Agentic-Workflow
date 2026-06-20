---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\author-gate-pre-response-guard-d3e8a1.md'
original_relative_path: '_archive\\2026-05\\author-gate-pre-response-guard-d3e8a1.md'
source_sha256: 7fc35683a6620bb4d2e4a0d7848f5340ba170b00232cd27b5cf56ef51c356f6e
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: author-gate-pre-response-guard-d3e8a1
plan_type: infra
---

# Author-Gate Pre-Response Guard for Missing AUTHOR_GATE_PACKET

> Deferred from `author-gate-canonical-emitter-rca-c7f9d1.md` §3.3 (P3 priority)
> Build a detection mechanism that warns when `ask_user_question` is called in Author-Gate context without canonical packet emission.

---

## Context (SCQA)

- **Situation** — The Author-Gate canonical emitter pipeline requires three steps: `refactor-decision-memory` → `author-gate-packet-builder` → `author-gate-ui-renderer`. Post-cascade audit (`post_cascade_author_gate_ui_audit.py`) detects violations but only after the user has already seen the degraded UI.

- **Complication** — Pre-response hooks cannot intercept `ask_user_question` tool arguments, so there's no mechanism to block or warn at call time. The violation is discovered post-hoc.

- **Question** — How do we detect and warn about hand-crafted Author-Gate invocations BEFORE the user sees the degraded UI?

- **Answer** — Extend `post_cascade_author_gate_ui_audit.py` with a post-cascade pattern matcher that looks for `ask_user_question` calls combined with Author-Gate context words ("Author-Gate", "P3.", "AG:") but missing `AUTHOR_GATE_PACKET:` blocks.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `author-gate-canonical-emitter-rca-c7f9d1.md` | Parent RCA with deferred scope | ✅ |
| `post_cascade_author_gate_ui_audit.py` | Extension target for detection | 🔲 |
| `author-gate-enforcement.md` | Policy SSOT for canonical pipeline | ✅ |

---

## Wave Structure

| Wave | Focus | Status |
|------|-------|--------|
| W1 | Design pattern-matcher heuristics | Not Started |
| W2 | Implement audit extension | Not Started |
| W3 | Test with historical violations | Not Started |

---

## Out Of Scope

- Pre-response blocking (impossible — hooks cannot see tool arguments)
- Modifying `ask_user_question` tool behavior
- Changes to the canonical emitter pipeline itself

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.P1 | Pattern design | Design doc | Guard word selection | ~0.5k | 🔲 TODO |
| W2.P1 | Audit extension | post_cascade_author_gate_ui_audit.py | Regex performance, false-positive rate | ~1k | 🔲 TODO |
| W2.P2 | Scorer integration | Priority assignment (P3 default) | Integration with deferred_scope_capture | ~0.5k | 🔲 TODO |
| W3.P1 | Regression test | Historical violation corpus | Validate detection accuracy | ~0.5k | 🔲 TODO |

---

## Gap Register

**GAP-1: Guard word selection**
- Need high-precision context words that indicate Author-Gate intent without false positives
- Candidates: "Author-Gate", "P3.", "AG:", "decision point", "options"

**GAP-2: Pattern matching accuracy**
- Must detect `ask_user_question` tool use in response text
- Must correlate with absence of `AUTHOR_GATE_PACKET:` block
- Must avoid false positives on legitimate non-Author-Gate `ask_user_question` calls

---

## Execution Plan

### W1.P1 — Pattern Design
**Scope**: Document guard word selection and pattern matching strategy

**Acceptance**: 
- Guard word list defined with rationale
- False-positive analysis documented
- Pattern matching approach specified

### W2.P1 — Audit Extension
**Scope**: Extend `post_cascade_author_gate_ui_audit.py` with pattern matcher

**Implementation sketch**:
```python
# In post_cascade response handler
AG_CONTEXT_WORDS = ["Author-Gate", "P3.", "AG:", "Author Gate"]

def detect_handcrafted_author_gate(response_text: str) -> List[Violation]:
    # Check for ask_user_question presence
    # Check for AG context words
    # Check for absence of AUTHOR_GATE_PACKET
    # Return violation if all three conditions met
```

**Acceptance**: 
- Extension logs violations to `author_gate_ui_violations.jsonl`
- New invariant: `handcrafted_author_gate_detected`
- Severity: WARN (not ERROR — this is advisory detection)

### W2.P2 — Scorer Integration
**Scope**: Wire detection into deferred scope capture with P3 priority

**Acceptance**:
- Violations auto-post to Backlog Items with P-Band=P3
- Plan relation links back to this plan

### W3.P1 — Regression Test
**Scope**: Validate against W3 P3.1/P3.2 violations from parent RCA

**Acceptance**:
- Detection catches the historical violations
- No false positives on legitimate canonical pipeline uses

---

## Rules

- Extension must be fail-soft — never block or error
- Pattern matching is advisory only (post-hoc detection)
- All detections logged with full context for manual review
- P-Band P3 (not blocking, schedule opportunistically)

---

## Success Criteria

- [ ] Pattern matcher detects hand-crafted Author-Gate invocations
- [ ] Violations logged with context for manual review
- [ ] Integration with deferred scope capture (auto-Notion post)
- [ ] Zero false positives on canonical pipeline uses

---

## Parent Reference

Deferred from: `author-gate-canonical-emitter-rca-c7f9d1.md` §3.3
Original DEFERRED_SCOPE marker:
```
DEFERRED_SCOPE: Pre-response guard that warns when `ask_user_question` is called
in the same response as an Author-Gate context word (e.g. "Author-Gate", "P3.", 
"AG:") but no `AUTHOR_GATE_PACKET:` block is present. Difficulty: pre-response 
hooks cannot see tool arguments. Alternative: post-cascade hook pattern match 
`ask_user_question` + guard word + missing packet. P-band: P3. Assign to: 
post_cascade_author_gate_ui_audit.py extension.
```

---

## Cascade Alignment Checks

- Plan is T1/T2 scope (single file extension, no cross-layer changes)
- No ADG graph-layer evidence required (plan_type: infra)
- Non-goals explicitly guard against scope expansion
