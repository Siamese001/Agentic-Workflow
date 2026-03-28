# Prompt Template E2E Wiring: All Apps Implementation Plan

**Objective:** Wire prompt templates end-to-end across all apps_* following windsurf revalidation rules.

**Current State:**
- ✅ apps_rg: Fully wired (FROZEN_SNAPSHOT, get_prompt())
- ❌ apps_exec: No wiring
- ❌ apps_research: No wiring
- ❌ apps_rfp: No wiring
- ❌ apps_lic: No wiring

**Target:** All 5 apps have working get_prompt() methods with E2E tests.

---

## WAVE 1: apps_exec PromptTemplate Types

**In-scope files:**
- `apps_exec/types/PromptTemplate.py` (NEW)
- `apps_exec/config/knowledge_base.py` (NEW)
- `apps_exec/engines/base_exec_engine.py` (MODIFY)

**Gaps to fix:**
- G1: No PromptTemplate types module in apps_exec
- G2: No knowledge_base.py to expose FROZEN_SNAPSHOT
- G3: No get_prompt() method in BaseExecEngine

**Validation:**
- Command: `python -c "from apps_exec.config.knowledge_base import FROZEN_SNAPSHOT, get_prompt; print('ok')"`
- Command: `python -m pytest tests/unit/apps_exec/engines/test_base_exec_engine.py -v`

---

## WAVE 2: apps_research PromptTemplate Types

**In-scope files:**
- `apps_research/types/PromptTemplate.py` (NEW)
- `apps_research/config/knowledge_base.py` (NEW)
- `apps_research/engines/base_research_engine.py` (MODIFY)

**Gaps to fix:**
- G1: No PromptTemplate types module in apps_research
- G2: No knowledge_base.py to expose FROZEN_SNAPSHOT
- G3: No get_prompt() method in BaseResearchEngine

**Validation:**
- Command: `python -c "from apps_research.config.knowledge_base import FROZEN_SNAPSHOT, get_prompt; print('ok')"`
- Command: `python -m pytest tests/unit/apps_research/engines/test_base_research_engine.py -v`

---

## WAVE 3: apps_rfp PromptTemplate Types

**In-scope files:**
- `apps_rfp/types/PromptTemplate.py` (NEW)
- `apps_rfp/config/knowledge_base.py` (NEW)
- `apps_rfp/engines/base_rfp_engine.py` (MODIFY)

**Gaps to fix:**
- G1: No PromptTemplate types module in apps_rfp
- G2: No knowledge_base.py to expose FROZEN_SNAPSHOT
- G3: No get_prompt() method in BaseRfpEngine

**Validation:**
- Command: `python -c "from apps_rfp.config.knowledge_base import FROZEN_SNAPSHOT, get_prompt; print('ok')"`
- Command: `python -m pytest tests/unit/apps_rfp/engines/test_base_rfp_engine.py -v`

---

## WAVE 4: apps_lic PromptTemplate Types

**In-scope files:**
- `apps_lic/types/PromptTemplate.py` (NEW)
- `apps_lic/config/knowledge_base.py` (NEW)
- `apps_lic/engines/control_plane.py` (MODIFY - add get_prompt to existing)

**Gaps to fix:**
- G1: No PromptTemplate types module in apps_lic
- G2: No knowledge_base.py to expose FROZEN_SNAPSHOT
- G3: No get_prompt() method (control_plane doesn't extend base engine pattern)

**Validation:**
- Command: `python -c "from apps_lic.config.knowledge_base import FROZEN_SNAPSHOT, get_prompt; print('ok')"`
- Command: `python -m pytest tests/unit/apps_lic/engines/test_control_plane.py -v`

---

## WAVE 5: Cross-App Integration Test

**In-scope files:**
- `tests/integration/test_prompt_template_cross_app.py` (NEW)

**Test coverage:**
- Import from all 5 apps
- Render from each app's knowledge base
- Verify get_prompt() returns non-empty for known prompt IDs
- Verify KeyError for unknown prompt IDs
- Verify empty string when knowledge disabled

**Validation:**
- Command: `python -m pytest tests/integration/test_prompt_template_cross_app.py -v`

---

## WAVE 6: ADG Re-index and Final Validation

**Steps:**
1. Regenerate ADG: `python tools/generate_full_adg.py`
2. Verify new edges for prompt/knowledge wiring
3. Run full E2E test suite: `python -m pytest tests/unit/prompt_governance/ tests/unit/apps_*/engines/ -v`

**Success criteria:**
- All new nodes appear in ADG
- All new edges recorded
- 0 test failures
- ADG digest updated

---

## Execution Rules (Per Windsurf Standards)

1. **One gap → one fix** (no batching)
2. **Must show unified diff** for every change
3. **Must verify callable signature** before modifying calls
4. **Must run targeted validation** after every fix
5. **Must pass full-file pytest gate** for any modified test file
6. **No summaries** until final reconciliation
7. **Anti-replay:** Do not re-implement already-fixed work
8. **Reconciliation check:** gaps_listed = diffs_shown = validations_passed

---

## Progress Tracking

| Wave | Status | Gaps | Diffs | Validations |
|------|--------|------|-------|-------------|
| W1 | PENDING | 3 | 0 | 0 |
| W2 | PENDING | 3 | 0 | 0 |
| W3 | PENDING | 3 | 0 | 0 |
| W4 | PENDING | 3 | 0 | 0 |
| W5 | PENDING | 0 | 0 | 0 |
| W6 | PENDING | 0 | 0 | 0 |
