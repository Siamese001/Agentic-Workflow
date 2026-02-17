# Phase 2 Evidence: Heal Policy Wiring + Deterministic heal_repository Baseline

```text
$ git rev-parse HEAD
e73d305b3

$ git status --porcelain
 M agentic_core/base_agents/SovereignBaseAgent.py
 M agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
 M agentic_core/utils/decorators_util.py
 A docs/reports/governance/agent_heal_phase2_report.md
 A tests/governance/test_heal_policy_wiring.py

$ pytest -q tests/governance/test_heal_policy_types.py tests/governance/test_agent_heal_audit.py tests/governance/test_heal_surface_enforcement.py tests/governance/test_heal_policy_wiring.py
64 passed in 25.58s

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format md --out docs/reports/governance/agent_heal_phase2_report.md
Markdown report generated: docs\reports\governance\agent_heal_phase2_report.md

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_phase2_run1.json
$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_phase2_run2.json

$ powershell "Get-FileHash artifacts/consolidation/heal_audit_phase2_run1.json -Algorithm SHA256 | Select-Object Hash"
Hash: 98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D

$ powershell "Get-FileHash artifacts/consolidation/heal_audit_phase2_run2.json -Algorithm SHA256 | Select-Object Hash"
Hash: 98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D
```

PHASE 2 ACCEPTANCE:

- Policy contract invoked at canonical healing seam (standard_heal decorator)
- enable_llm hard-gates LLM escalation (proven in 16 tests)
- heal_repository has deterministic baseline behavior (idempotent)
- No tests perform network calls (LLM seam monkeypatched)
- Report and evidence are RAW ONLY and deterministic
