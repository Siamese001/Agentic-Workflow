# W2 Closeout — Shim Archive & Misplacement Ledger

**Plan:** [agent-inventory-spine-taxonomy-b4e9f2.md](../../../.cursor/plans/agent-inventory-spine-taxonomy-b4e9f2.md)  
**Ledger:** [agent_inventory_layer_misplacement_ledger_20260525.md](agent_inventory_layer_misplacement_ledger_20260525.md)  
**Date:** 2026-05-25

## STATUS: PASS

## Deliverables

| Phase | Output | Status |
|-------|--------|--------|
| W2.0 | RootCustomsAgent orphan body archived; thin shim restored | DONE |
| W2.1 | Misplacement ledger + assessment link | DONE |
| W2.2 | L6 snapshot shim documented as harness-only (preserved) | DONE |

## W2.0 — RootCustomsAgent

**Problem:** `RootCustomsAgent.py` contained a thin delegating shim (lines 1–163) plus **743 lines** of orphan legacy code that **re-defined** `RootCustomsAgent` at import time.

**Fix:**

- Legacy body → [agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py](../../../archives/agents/2026-05-25/agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py)
- Active module truncated to **163 lines** (delegates to `root_customs_util`)
- Taxonomy: `AgentStatus.ARCHIVED`, `is_shim=True`

## Spine chain grep (no RootCustomsAgent import)

Verified zero matches in spine chain modules:

- `agentic_core/runtime/entrypoints/integrated_single_action_spine_run.py`
- `agentic_core/L0_routing/intake/pipeline.py`
- `agentic_core/L0_routing/reasoning/route_gates.py`
- `agentic_core/L1_cognition/bridges/u0_to_l1_plan.py`
- `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py`
- `agentic_core/runtime/l2_recipe_resolver.py`

## FILES_CHANGED

- [RootCustomsAgent.py](../../../agentic_core/L0_routing/reasoning/RootCustomsAgent.py) (truncated)
- [agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py](../../../archives/agents/2026-05-25/agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py)
- [archive_root_customs_orphan_body.py](../../../tools/governance/archive_root_customs_orphan_body.py)
- [agent_taxonomy_registry.py](../../../agentic_core/L2_execution/types/agent_taxonomy_registry.py)
- [agent_inventory_layer_misplacement_ledger_20260525.md](agent_inventory_layer_misplacement_ledger_20260525.md)
- [agentic_core_agent_inventory_runtime_assessment.md](../agentic_core_agent_inventory_runtime_assessment.md)
- [test_RootCustomsAgent.py](../../../tests/agentic_core/L0_routing/reasoning/test_RootCustomsAgent.py) (patch paths → `utils.root_customs_util`)

## COMMANDS_RUN

| Command | Result |
|---------|--------|
| `python tools/governance/archive_root_customs_orphan_body.py` | exit 0 — 743 lines archived, 163-line shim |
| `python -m pytest tests/agentic_core/L0_routing/reasoning/test_RootCustomsAgent.py tests/unit/agentic_core/L0_routing/reasoning/test_RootCustomsAgent.py tests/governance/test_agent_spine_invocation_claims.py -q -o addopts=` | exit 0 — **12 passed** |
| `python ops_scripts/ci/check_agent_taxonomy_spine_invariants.py` | PASS |

## TESTS_GATES

- RootCustomsAgent tests + taxonomy CI gate (see command output in session)

## ARTIFACTS

- [agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py](../../../archives/agents/2026-05-25/agentic_core__L0_routing__reasoning__RootCustomsAgent_legacy_orphan_body.py)

## NOTES

- L6 `snapshot/__init__.py` **not deleted** — harness/report only (W2.2).
- W3 live spine proof remains DEFERRED; mock harness not used for `ARTIFACT_PROVEN`.
