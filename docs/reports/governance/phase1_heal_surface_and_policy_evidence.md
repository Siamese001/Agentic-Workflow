# Phase 1 Evidence: Deterministic Runtime-Agent Audit + Aligned Enforcement

```
WORK_COMMIT=949b0e671 (governance(healing): remove phase1 helper scripts from shipping tree)
EVIDENCE_COMMIT=12e71accf (governance(healing): lock Phase 1 closeout evidence - final HEAD proof)

$ git ls-tree -r 949b0e671 --name-only | Select-String "scratch/phase1_helpers"
NO_MATCH

$ git ls-tree -r 12e71accf --name-only | Select-String "scratch/phase1_helpers"
NO_MATCH

$ pytest -q tests/governance/test_heal_policy_types.py tests/governance/test_agent_heal_audit.py tests/governance/test_heal_surface_enforcement.py
48 passed in 25.78s

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > run1.json
$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format json > run2.json

$ powershell "Get-FileHash run1.json -Algorithm SHA256 | Select-Object Hash"
Hash: 98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D

$ powershell "Get-FileHash run2.json -Algorithm SHA256 | Select-Object Hash"
Hash: 98216BF31F94ECF0CB9A29F7E8EFA6FAE5A99E18CA60D17A8E2576DF32A38F8D
```
