---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\prompt-taxonomy-implementation-7b2f9f.md'
original_relative_path: 'prompt-taxonomy-implementation-7b2f9f.md'
source_sha256: fbef9488e51dbbf2b4bfb9157f24850f456327e2faf4859f0363eb95dd28bd70
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-31'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Prompt Taxonomy Gap Analysis & Staged Implementation Plan

A phased implementation to close the 4-slot gap between the existing 5-slot system (S0/D0/I0/C0/U0) and the full 9-slot taxonomy, adding EXEMPLARS (E0), META-COGNITIVE (M0), SYNTHESIS (Y0), and HEALING PROPOSAL (H0) slots with proper authority levels and cross-layer governance.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 1 | Phase 1-2 | Core slot contracts + EXEMPLARS (E0) | 45K 🟢 | Slot contracts frozen, BOM types updated | Pending | E0 slot passes validation, GoldenContextMixin migrated |
| Wave 2 | Phase 3-4 | META-COGNITIVE (M0) + SYNTHESIS (Y0) | 55K 🟢 | L1 cognition integration, telemetry pipeline ready | Pending | M0/Y0 slots functional, reasoning chain templates updated |
| Wave 3 | Phase 5-6 | HEALING PROPOSAL (H0) + Full integration | 40K 🟢 | L2.3 Healer integration, re-entry validation ready | Pending | H0 slot validated, healing proposal flow end-to-end tested |
| Wave 4 | Phase 7 | Cross-apps propagation + Documentation | 25K 🟢 | apps_rg/lic/exec shared APIs stable | Pending | All apps_* layers use unified 9-slot taxonomy |

**Total: ~165K tokens across 4 waves, all GREEN**

---

## Gap Register

**GAP-1: EXEMPLARS (Golden Context/Few-Shot) — MISSING E0 Slot**
- Current: GoldenContextMixin exists but not formalized as assembly slot
- Impact: Few-shot examples cannot be systematically injected with proper authority ordering
- Taxonomy Authority: GUIDING (Performance) — Slot E0 should enforce ordering between I0 and C0

**GAP-2: META-COGNITIVE (Chain/Tree of Thought) — MISSING M0 Slot**
- Current: Reasoning chokepoints exist but no formal prompt slot for CoT/ToT directives
- Impact: Internal reasoning prompts cannot be cleanly separated from system directives or user context
- Taxonomy Authority: PRIVATE (Reasoning Only) — Slot M0 should sit between D0 and I0

**GAP-3: SYNTHESIS (Pattern Analysis/Telemetry→Proposals) — MISSING Y0 Slot**
- Current: L4 Historian/MetaLearning emits proposals but no formal slot for synthesis prompts
- Impact: Telemetry summarization prompts lack authority boundary and assembly ordering
- Taxonomy Authority: ANALYTIC (Improvement) — Slot Y0 should be background-injected

**GAP-4: HEALING PROPOSAL (Correction/Re-entry) — MISSING H0 Slot**
- Current: Healing proposal validation exists in prompt_assembler.py but not as formal slot
- Impact: L2.3→L5 healing loop prompts lack formal assembly channel with re-entry validation
- Taxonomy Authority: PROPOSED (Requires Re-Entry) — Slot H0 needs special validation gate

---

## Execution Plan

### Phase 1 — Slot Contract Foundation
**Scope**: Extend slot_contracts.py with 4 new frozen dataclass slots (E0, M0, Y0, H0) with proper authority levels and ordering constraints

**Files to Modify**:
- `agentic_core/prompt_governance/contracts/slot_contracts.py` — Add SlotE0, SlotM0, SlotY0, SlotH0
- Update SLOT_ORDER from ("S0", "D0", "I0", "C0", "U0") to ("S0", "D0", "M0", "I0", "E0", "C0", "Y0", "U0", "H0")
- Add slot-specific validation logic for H0 re-entry requirements

**Commands**:
```bash
# Phase 1 validation
python -c "from agentic_core.prompt_governance.contracts.slot_contracts import SLOT_ORDER; print('New slot order:', SLOT_ORDER)"
python -m pytest tests/unit/agentic_core/prompt_governance/contracts/test_slot_contracts.py -v -k "slot_order"
```

**Acceptance**: 
- All 9 slots defined as frozen dataclasses
- SLOT_ORDER tuple includes all 9 slots in authority-priority order
- validate_slot_order() passes with mixed old/new slot configurations

---

### Phase 2 — EXEMPLARS (E0) Implementation
**Scope**: Migrate GoldenContextMixin to formal E0 slot, update PromptAssembler to inject exemplars

**Files to Modify**:
- `agentic_core/prompt_governance/core/prompt_assembler.py` — Add E0 slot injection logic
- `agentic_core/mixins/golden_context_mixin.py` — Deprecate in favor of E0 slot
- `agentic_core/prompt_governance/contracts/prompt_bom_types.py` — Add exemplars_required field

**Commands**:
```bash
# Phase 2 validation
python -m pytest tests/unit/agentic_core/prompt_governance/test_prompt_assembler.py -v -k "exemplar"
python -c "from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler; p = PromptAssembler(); print('E0 slot support:', hasattr(p, '_format_exemplars'))"
```

**Acceptance**:
- GoldenContextMixin functionality migrated to E0 slot
- PromptAssembler.assemble() accepts exemplars parameter
- BOM types support exemplars_required field
- 19/19 scanner tests still pass (non-regression)

---

### Phase 3 — META-COGNITIVE (M0) Implementation
**Scope**: Add CoT/ToT prompt slot between D0 and I0 for internal reasoning directives

**Files to Modify**:
- `agentic_core/prompt_governance/core/prompt_assembler.py` — Add M0 slot injection
- `agentic_core/L1_cognition/enforcement/reasoning_chokepoint.py` — Wire M0 slot
- `agentic_core/prompt_governance/templates/reasoning_chain.jinja` — Update for M0 slot

**Commands**:
```bash
# Phase 3 validation
python -m pytest tests/unit/agentic_core/L1_cognition/enforcement/test_reasoning_chokepoint.py -v
python -c "from agentic_core.prompt_governance.contracts.slot_contracts import SlotM0; m = SlotM0(content='Think step by step'); print('M0 created:', m)"
```

**Acceptance**:
- M0 slot accepts content with reasoning directives
- Reasoning chokepoint can inject M0 slot content
- Chain-of-thought templates use M0 slot structure

---

### Phase 4 — SYNTHESIS (Y0) Implementation
**Scope**: Add background synthesis slot for telemetry→proposal prompts

**Files to Modify**:
- `agentic_core/prompt_governance/core/prompt_assembler.py` — Add Y0 slot (background-injected)
- `agentic_core/L4_state/enforcement/telemetry_recorder.py` — Wire synthesis slot emission
- `agentic_core/prompt_governance/meta_prompts/` — Add synthesis templates

**Commands**:
```bash
# Phase 4 validation
python -m pytest tests/unit/agentic_core/L4_state/enforcement/test_telemetry_recorder.py -v -k "synthesis"
python -c "from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler; p = PromptAssembler(); print('Y0 slot background injection:', 'SLOT_Y0' in p.DEFAULT_TEMPLATE)"
```

**Acceptance**:
- Y0 slot supports background synthesis prompts
- Telemetry recorder can emit synthesis proposals via Y0
- Meta-learning pipeline uses Y0 for pattern analysis

---

### Phase 5 — HEALING PROPOSAL (H0) Implementation
**Scope**: Formalize healing proposal slot with re-entry validation gates

**Files to Modify**:
- `agentic_core/prompt_governance/core/prompt_assembler.py` — Add H0 slot with validation
- `agentic_core/prompt_governance/security/validators/output_schema_validator.py` — Wire healing validation
- `agentic_core/L5_safety/enforcement/sovereign_healing_engine_enforcer.py` — Wire H0 slot

**Commands**:
```bash
# Phase 5 validation
python -m pytest tests/unit/agentic_core/L5_safety/enforcement/test_sovereign_healing_engine.py -v -k "proposal"
python -c "from agentic_core.prompt_governance.core.prompt_assembler import PromptAssembler; p = PromptAssembler(); print('H0 validation:', p.validate_healing_proposal is not None)"
```

**Acceptance**:
- H0 slot enforces re-entry validation before acceptance
- Healing proposal validation passes/fails appropriately
- L2.3→L5 healing loop uses H0 slot for corrections

---

### Phase 6 — Cross-Layer Integration
**Scope**: Update all layer-specific prompt assembly to use new slots

**Files to Modify**:
- `agentic_core/L0_routing/engines/prompt_bom_builder.py` — Support all 9 slots
- `agentic_core/L1_cognition/engines/prompt_template_manager.py` — Wire M0 slot
- `agentic_core/L2_execution/` — Wire H0 for healing
- `agentic_core/L3_orchestration/` — Wire Y0 for synthesis
- `agentic_core/L4_state/` — Wire E0 for golden context
- `agentic_core/L5_safety/` — Wire all slots for validation

**Commands**:
```bash
# Phase 6 integration test
python -m pytest tests/integration/test_prompt_assembly_full.py -v --tb=short
python tools/adg/adg_redis_ingest.py --force  # Regenerate ADG with new slot edges
```

**Acceptance**:
- All L0-L5 layers can emit all 9 slot types
- Integration tests pass with full slot coverage
- ADG shows edges for slot emissions

---

### Phase 7 — Apps Layer Propagation
**Scope**: Migrate apps_rg, apps_lic, apps_exec to unified 9-slot taxonomy

**Files to Modify**:
- `apps_rg/types/PromptTemplate.py` — Add slot-aware prompt types
- `apps_lic/types/PromptTemplate.py` — Add slot-aware prompt types
- `apps_exec/reasoning/` — Wire appropriate slots for execution

**Commands**:
```bash
# Phase 7 apps validation
python -m pytest tests/apps_rg/ -v -k "prompt" --ignore-glob="*_adg.py"
python -m pytest tests/apps_lic/ -v -k "prompt" --ignore-glob="*_adg.py"
python -m pytest tests/apps_exec/ -v -k "prompt" --ignore-glob="*_adg.py"
```

**Acceptance**:
- All apps_* tests pass with new slot system
- No collection errors from slot contract changes
- apps_* layers use shared slot taxonomy consistently

---

## Rules

- **Slot Order Immutable**: Once SLOT_ORDER is updated in Phase 1, it becomes frozen — no mid-phase reordering
- **Authority Level Enforcement**: Each slot MUST reject content that violates its authority level (e.g., H0 cannot be injected without re-entry validation)
- **Backward Compatibility**: Existing 5-slot prompts must continue to work during all phases
- **ADG Edge Emission**: Every slot injection MUST emit corresponding ADG edge for traceability
- **Non-Regression**: 19/19 scanner tests must pass at end of each wave

---

## Success Criteria

- [ ] All 9 slots (S0, D0, M0, I0, E0, C0, Y0, U0, H0) implemented as frozen dataclasses
- [ ] SLOT_ORDER enforces authority priority: S0 > D0 > M0 > I0 > E0 > C0 > Y0 > U0 > H0
- [ ] PromptAssembler.assemble() accepts all 9 slot content types
- [ ] GoldenContextMixin functionality migrated to E0 (exemplars) slot
- [ ] Reasoning chokepoints use M0 (meta-cognitive) slot
- [ ] Telemetry synthesis uses Y0 (synthesis) slot
- [ ] Healing proposals use H0 slot with re-entry validation
- [ ] All apps_* layers migrated to unified taxonomy
- [ ] 19/19 scanner tests pass (non-regression)
- [ ] ADG shows slot emission edges for all 9 types

---

## Implementation Commands

```bash
# Wave 1: Foundation + E0
python -m pytest tests/unit/agentic_core/prompt_governance/contracts/ -v
python -m pytest tests/unit/agentic_core/prompt_governance/core/ -v -k "slot"

# Wave 2: M0 + Y0
python -m pytest tests/unit/agentic_core/L1_cognition/ -v -k "reasoning"
python -m pytest tests/unit/agentic_core/L4_state/ -v -k "synthesis"

# Wave 3: H0 + Integration
python -m pytest tests/unit/agentic_core/L5_safety/ -v -k "healing"
python -m pytest tests/integration/test_prompt_assembly_full.py -v

# Wave 4: Apps + Final validation
python -m pytest tests/apps_rg/ tests/apps_lic/ tests/apps_exec/ -v --ignore-glob="*_adg.py"
python tools/adg/generate_full_adg.py  # Final ADG with all slot edges
```

---

## Rollback Strategy

If things go wrong:
1. Revert slot_contracts.py to original 5-slot SLOT_ORDER
2. Revert prompt_assembler.py to legacy_mode default=True
3. Restore GoldenContextMixin as primary exemplar mechanism
4. Regenerate ADG without new slot edges: `python tools/adg/generate_full_adg.py --baseline`

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| Slot Coverage | 9/9 implemented | `len(SLOT_ORDER) == 9` |
| Assembler Support | All slots | `PromptAssembler` accepts all slot params |
| Apps Migration | 100% | All apps_* PromptTemplate types use slots |
| Test Pass Rate | 100% | `pytest --collect-only` shows 0 errors |
| ADG Slot Edges | >1000 | Query shows edges for all 9 slot types |

---

*Plan generated: 2026-03-31*  
*Target completion: 4 waves (~2 weeks)*  
*Risk level: Medium (cross-layer changes)*
