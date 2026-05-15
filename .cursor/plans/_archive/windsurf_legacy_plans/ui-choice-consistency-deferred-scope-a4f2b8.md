# UI Choice Consistency — Deferred Scope

**Plan ID:** `ui-choice-consistency-deferred-scope-a4f2b8`  
**Status:** Draft  
**Tier:** T2  
**Created:** 2026-05-09  
**Parent:** `ui-choice-consistency-zero-loss-hardened-d9f3a1` (completed)

---

## 1. Deferred Scope Summary

This plan captures all work intentionally descoped from the hardened zero-loss refactor. These items were identified as **not required** for the immediate deliverable but represent **valid future work** for UI choice consistency expansion.

---

## 2. Deferred Items

### 2.1 Active Surface Migration (P2 — Valid but Deferred)

| File | Classification | Why Deferred | Future Trigger |
|------|----------------|--------------|----------------|
| `.windsurf/workflows/antipattern-author-gate.md` | AUTHOR_GATE | Already references AG pipeline; needs canonical path example update | When antipattern workflow is next edited |
| `.windsurf/skills/adg-sqlite/SKILL.md` | ENRICHED_CHOICE | Not in original active surface list; instructional only | When skill is updated for ADG query examples |
| `.windsurf/skills/author-gate-ui-renderer/SKILL.md` | AUTHOR_GATE | Render-only skill; no decision prompts | If renderer adds configuration choices |

**Rationale:** These surfaces are either already compliant (AUTHOR_GATE paths) or are instructional-only markdown not in the active decision path.

---

### 2.2 Test Fixture Migration (P3 — Never Required)

| Location | Status | Why Exempt | Future Action |
|----------|--------|------------|---------------|
| `tests/` | EXEMPT | Test fixtures explicitly exempt per hardened review #8 | None — maintain exemption |
| `tests/governance/` | EXEMPT | Test fixtures | None |
| `tests/unit/` | EXEMPT | Test fixtures | None |

**Rationale:** Test code is explicitly out of scope per the hardened plan's "Minimal scope preserved" requirement.

---

### 2.3 Framework Extension (P3 — Explicitly Excluded)

| Feature | Why Excluded | Future Consideration |
|---------|--------------|-------------------|
| Broad DecisionPresentation framework | Per prompt: "minimal implementation only" | If decision consistency becomes organization-wide concern |
| External ask_user_question tool changes | Tool API is external; we wrap only | If tool adds native enrichment support |
| CLI wizard enrichment | `interactive_wizard.py` explicitly exempt (data collection, not decisions) | If wizards add branching decisions |
| Author-Gate scoring changes | AG pipeline unchanged by design | If AG scoring algorithm changes |

**Rationale:** These were explicitly listed as non-goals in the hardened plan §5.

---

### 2.4 Scanner Enhancement (P2 — Valid but Deferred)

| Enhancement | Priority | Future Trigger |
|-------------|----------|----------------|
| AST-based detection (vs regex) | P2 | When regex false positive rate > 5% |
| Multi-file context analysis | P2 | When cross-file builder imports common |
| Automatic fix suggestions | P3 | When scanner runs in IDE pre-commit hook |
| Severity-based filtering | P3 | When violation volume becomes unmanageable |

**Rationale:** Current regex-based scanner is sufficient for the 2 active surfaces. AST upgrade justified only if surface count grows >10.

---

### 2.5 Documentation Expansion (P3 — Explicitly Excluded)

| Doc | Why Excluded | Future Action |
|-----|--------------|---------------|
| Comprehensive API documentation | Minimal scope | If external teams adopt helper |
| Video walkthrough | Docs-only | If onboarding friction detected |
| Migration cookbook for other repos | Not needed | If pattern adopted elsewhere |

**Rationale:** Code is self-documenting; examples in migrated surfaces sufficient.

---

## 3. Reactivation Conditions

This deferred scope becomes active if ANY of the following trigger:

| Trigger | Deferred Item | Activation Condition |
|---------|---------------|---------------------|
| T1 | Scanner regex → AST | False positive rate > 5% in CI |
| T2 | antipattern-author-gate.md update | File modified for content reasons |
| T3 | New active surfaces | >3 new decision surfaces added |
| T4 | External adoption | Another repo requests helper |
| T5 | Tool API change | ask_user_question adds native enrichment |

---

## 4. Success Criteria (If Activated)

| Criterion | Measurement |
|-----------|-------------|
| Scanner accuracy | ≥95% true positive rate |
| Migration coverage | 100% of active surfaces pass |
| Test coverage | Unit + scanner + integration ≥50 tests |
| CI integration | Zero additional CI time overhead |

---

## 5. References

- **Completed Parent:** `ui-choice-consistency-zero-loss-hardened-d9f3a1.md`
- **Hardening Review:** 8 corrections incorporated in parent
- **Non-Goals Source:** Parent plan §5
- **Scanner:** `ops_scripts/ci/check_enriched_choice_ui_invariants.py`
- **Helper:** `tools/decisions/enriched_choice_builder.py`

---

*Deferred scope captured 2026-05-09. Reactivation requires explicit user request or trigger condition met.*
