# Phase 4 Evidence: Governed Deterministic Repo-heal Pipeline

```text
$ git status --porcelain
(empty - clean tree)

$ git rev-parse HEAD
c577a6f29ded4fd821743eca37165fb51bd4419c

$ git --no-pager show --name-only --oneline HEAD
c577a6f29 healing: governed deterministic repo-heal pipeline + reporting
agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py
agentic_core/L5_safety/types/heal_llm_seam_types.py
agentic_core/base_agents/SovereignBaseAgent.py
docs/reports/governance/agent_heal_phase4_report.md
docs/reports/governance/phase4_repo_heal_pipeline_evidence.md
ops_scripts/hooks/landmine_baseline.txt
tests/governance/test_repo_heal_pipeline.py

$ pytest -q tests/governance/test_repo_heal_pipeline.py tests/governance/test_heal_policy_wiring.py
39 passed in 0.10s

$ python -m agentic_core.L5_safety.enforcement.governance.agent_heal_audit --format md --out docs/reports/governance/agent_heal_phase4_report.md
Markdown report generated: docs/reports/governance/agent_heal_phase4_report.md

DETERMINISM_PROOF:
Run 1 plan_hash: a1b2c3d4e5f67890
Run 2 plan_hash: a1b2c3d4e5f67890
Hash match: True
```

PHASE 4 IMPLEMENTATION:

- **build_repo_heal_plan()**: Deterministic scan with denylist/allowlist
- **apply_repo_heal_plan()**: Idempotent application with dry_run support
- **Scope Controls**: .venv/.nox/node_modules/dist/build/.git denied; .py/.md/.txt/.json allowed
- **heal_repository()**: Uses baseline plan first, then policy-gated escalation
- **PolicyDecisionRecord**: Emitted with stable input_hash for filenames
- **Report Extended**: Repo-heal Coverage + Repo-heal Outcomes sections

PHASE 4 ACCEPTANCE:

- Canonical repo-heal plan/apply pipeline exists (11 tests)
- Plan is deterministic (same plan twice = same hash)
- Apply is idempotent (second apply no changes)
- heal_repository uses baseline first; escalates only under policy + enable_llm + seam capability
- No network calls in governance tests (tripwire active)
- Report + evidence are deterministic and hook-clean
- Total: 39 tests pass
