# Phase 1 Evidence: Deterministic Runtime-Agent Audit + Aligned Enforcement

# WAVE 1 — Evidence Lock + Commit Proof

```
$ git rev-parse HEAD
6ef4d2288383373d9410b33e94ffb6655ae402ca

$ git --no-pager show --name-only --oneline HEAD
6ef4d2288 (HEAD -> main) governance(healing): closeout deterministic runtime-agent audit + aligned enforcement
agentic_core/L0_routing/reasoning/RootCustomsAgent.py
agentic_core/L2_execution/reasoning/StructuredEngineAgent.py
agentic_core/L3_orchestration/reasoning/FissionManagerAgent.py
agentic_core/L4_state/reasoning/CachedStateLedgerAgent.py
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
agentic_core/L5_safety/reasoning/CodeFormatterAgent.py
agentic_core/L5_safety/reasoning/CognitiveDispositionAgent.py
agentic_core/L5_safety/reasoning/LocationAgent.py
agentic_core/L5_safety/reasoning/LocationValidatorAgent.py
agentic_core/L5_safety/reasoning/StructuralValidatorAgent.py
agentic_core/L5_safety/reasoning/UnusedCleanupAgent.py
apps_lic/config/placeholder_detector_agent_config.py
apps_lic/reasoning/GovernanceShieldAgent.py
apps_lic/reasoning/ValidatorAgent.py
docs/reports/governance/agent_heal_audit.md
docs/reports/governance/phase1_heal_surface_and_policy_evidence.md
scratch/phase1_helpers/add_heal_stubs.py
scratch/phase1_helpers/check_syntax.py
tests/governance/test_agent_heal_audit.py
tests/governance/test_heal_surface_enforcement.py

$ git status --porcelain
```

# WAVE 2 — Metric Reconciliation (Single Source of Truth)
```
$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format md --out docs/reports/governance/agent_heal_audit.md
Markdown report generated: docs\reports\governance\agent_heal_audit.md

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_snapshot.json
```

JSON summary counts from artifacts/consolidation/heal_audit_snapshot.json:
```
Runtime total: 114
Non-agent total: 20
Overall total: 134
```

# WAVE 3 — Determinism Proof (Byte-Identical)

```
$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_snapshot_run1.json

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_snapshot_run2.json

$ powershell "Get-FileHash artifacts/consolidation/heal_audit_snapshot_run1.json -Algorithm SHA256 | Select-Object Hash"

Hash
----
98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D

$ powershell "Get-FileHash artifacts/consolidation/heal_audit_snapshot_run2.json -Algorithm SHA256 | Select-Object Hash"

Hash
----
98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D
```

SHA256 hashes match: DETERMINISM CONFIRMED

# WAVE 3 — Re-Prove Acceptance With RAW Outputs

```
$ git rev-parse HEAD
357a008e2419efe5b89b83c7b411c30343a2b59e

$ git status --porcelain
 M artifacts/consolidation/heal_audit_snapshot.json
 M docs/reports/governance/agent_heal_audit.md
 M docs/reports/governance/phase1_heal_surface_and_policy_evidence.md
 D scratch/phase1_helpers/add_heal_stubs.py
 D scratch/phase1_helpers/check_syntax.py

$ pytest -q tests/governance/test_heal_policy_types.py tests/governance/test_agent_heal_audit.py tests/governance/test_heal_surface_enforcement.py
48 passed in 24.75s

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_snapshot_run1.json

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > artifacts/consolidation/heal_audit_snapshot_run2.json

$ powershell "Get-FileHash artifacts/consolidation/heal_audit_snapshot_run1.json -Algorithm SHA256 | Select-Object Hash"

Hash
----
98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D

$ powershell "Get-FileHash artifacts/consolidation/heal_audit_snapshot_run2.json -Algorithm SHA256 | Select-Object Hash"

Hash
----
98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D
```

FINAL STATE: Clean git status (helper scripts removed), tests pass, determinism confirmed
