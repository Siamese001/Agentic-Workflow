# Phase 5 Evidence: Deterministic Telemetry + Budget Caps

```text
$ git status --porcelain
(empty - clean tree)

$ git rev-parse HEAD
6b1c20b3327f1dcee096741846f6910fbde0ce44

$ git --no-pager show --name-only --oneline HEAD
6b1c20b33 healing: lock Phase 5 closeout evidence (telemetry+budgets)
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
agentic_core/L5_safety/types/heal_llm_seam.py
artifacts/consolidation/heal_telemetry/determinism_proof_fixed.json
docs/reports/governance/agent_heal_phase5_report.md
docs/reports/governance/phase5_telemetry_and_budgets_evidence.md
tests/governance/test_heal_telemetry_and_budgets.py

$ pytest -q tests/governance/test_heal_policy_wiring.py tests/governance/test_repo_heal_pipeline.py tests/governance/test_heal_telemetry_and_budgets.py
53 passed in 0.14s

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format md --out docs/reports/governance/agent_heal_phase5_report.md
Markdown report generated: docs/reports/governance/agent_heal_phase5_report.md

$ Get-FileHash artifacts/consolidation/heal_telemetry/determinism_proof_fixed.json -Algorithm SHA256 | Select-Object Hash
Hash
----
11280CA442526B6C365349CE8A29F2DCD2B103511609AC8566E499E5201BB00C

$ Get-FileHash artifacts/consolidation/heal_telemetry/determinism_proof_fixed.json -Algorithm SHA256 | Select-Object Hash
Hash
----
11280CA442526B6C365349CE8A29F2DCD2B103511609AC8566E499E5201BB00C
```
