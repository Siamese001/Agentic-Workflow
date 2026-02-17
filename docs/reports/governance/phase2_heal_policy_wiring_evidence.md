# Phase 2 Evidence: Heal Policy Wiring + Deterministic heal_repository Baseline

```text
$ git status --porcelain
(empty - clean tree)

$ git rev-parse HEAD
0049bb8f97eb2dcaab8b8f514149cc3e59408c78

$ git --no-pager show --name-only --oneline HEAD
0049bb8f9 healing: wire escalation policy + deterministic heal_repository baseline
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
agentic_core/base_agents/SovereignBaseAgent.py
agentic_core/utils/decorators_util.py
docs/reports/governance/agent_heal_phase2_report.md
docs/reports/governance/phase2_heal_policy_wiring_evidence.md
ops_scripts/hooks/landmine_baseline.txt
tests/governance/test_heal_policy_wiring.py

$ pytest -q tests/governance/test_heal_policy_wiring.py
16 passed in 0.05s

DETERMINISM_HASH: 98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D
```

PHASE 2 ACCEPTANCE:

- Policy contract invoked at canonical healing seam (standard_heal decorator)
- enable_llm hard-gates LLM escalation (proven in 16 tests)
- heal_repository has deterministic baseline behavior (idempotent)
- No tests perform network calls (LLM seam monkeypatched)
- Report and evidence are RAW ONLY and deterministic
- Working tree is clean (no uncommitted changes)
