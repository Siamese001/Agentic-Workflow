# Governed Architecture and SVP Documentation — Closeout

> **Status:** implementation complete; current green status requires command evidence  
> **Registry:** `apps_shared/integrations/app_registry.py`  
> **Architecture proof:** `python ops_scripts/ci/run_architecture_proof.py`  
> **SVP docs proof:** `python scripts/governance/svp_docs_review.py --mode audit --phase pre --json`

## What is in place

### Governed runtime and exception model

The app portfolio is classified through one registry:

- **3 governed entries:** `apps_exec`, `apps_research`, `apps_rg`;
- **5 formal exceptions:** `apps_architect`, `apps_eval`, `apps_lic`, `apps_qna`, `apps_underwriting_ai`;
- **0 ad hoc statuses.**

Governed entries expose a shared runner or canonical governed callable. Formal exceptions declare reason codes, blocked and safe surfaces, compensating controls, handlers, ownership, and review cadence.

### Registry-driven proof runner

`ops_scripts/ci/run_architecture_proof.py` composes:

| Suite | Purpose |
|---|---|
| S1 | Registry, governed-entry, and formal-exception conformance |
| S2 | Governed behavior and formal-exception controls |
| S3 | Evidence-governance regression baseline |

The runner derives its registry summary from `APP_REGISTRY`. It does not maintain a separate app-count constant or retired app grouping.

### SVP documentation control path

The documentation workflow is separated into three authorities:

```text
weekly read-only audit
  -> X2 pre
  -> X1D judgment
  -> X3 NOOP / PLAN_ONLY / BLOCK / ESCALATE_HUMAN

approved manual refresh
  -> X2 pre
  -> bounded docs edit
  -> X2 post
  -> X1D final review
  -> X3 ALLOW_TO_PR / BLOCK / ESCALATE_HUMAN

ALLOW_TO_PR
  -> on-demand-pr-main-publisher
  -> GitHub PR, CI, merge, closeout
```

The weekly job cannot edit or publish. The manual refresh requires a machine-readable approval receipt. Neither automation pushes or merges directly to `main`.

## Evidence artifacts

| Artifact | Role |
|---|---|
| `.codex/automations/svp-readme-documentation-refresh/automation.toml` | Weekly read-only audit contract |
| `.codex/automations/on-demand-svp-documentation-refresh/automation.toml` | Approval-bound edit contract |
| `.codex/automations/svp-readme-documentation-refresh/reviewer_packet.v1.json` | Active reviewer packet and claim-evidence map |
| `.codex/schemas/svp_docs_x1d_v1.schema.json` | Senior-reader judgment receipt |
| `.codex/schemas/svp_docs_x2_v1.schema.json` | Deterministic gate receipt |
| `.codex/schemas/svp_docs_x3_v1.schema.json` | Final disposition receipt |
| `.codex/schemas/svp_docs_run_v1.schema.json` | Run-level replay receipt |
| `.codex/schemas/svp_docs_approval_v1.schema.json` | Manual edit approval receipt |
| `scripts/governance/svp_docs_review.py` | X2 gate execution and X3 aggregation |
| `python scripts/governance/svp_docs_review.py --mode audit --phase pre --json` | Operator-run review outside GitHub Actions |

## X2 deterministic gate set

The implementation runs these gates in a fixed order:

1. automation TOML parsing;
2. launcher and publication SSOT;
3. stale active terms;
4. relative links;
5. unsupported customer/compliance/ROI/SLA/roadmap claims;
6. docs-only scope;
7. reviewer packet presence;
8. root README sections;
9. Codex primary verification;
10. enforcement-home verification;
11. diff hygiene;
12. branch and publication isolation;
13. architecture status consistency;
14. claim-evidence mapping;
15. proof-command target resolution;
16. receipt schema validation;
17. explicit approval mode;
18. unanchored absolute-language detection.

X1D can recommend or block on evidence-backed high-severity findings. It cannot waive a failed X2 gate.

## Verification matrix

```bash
python -m py_compile scripts/governance/svp_docs_review.py
pytest -q tests/unit/scripts/governance/test_svp_docs_review.py
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json
python scripts/governance/svp_docs_review.py --mode audit --phase pre --base-ref origin/main --json
python ops_scripts/ci/run_architecture_proof.py --suite S1
git diff --check
```

Full behavioral and regression proof remains:

```bash
python ops_scripts/ci/run_architecture_proof.py
```

## Remaining operational work

| Item | Treatment |
|---|---|
| Independent X1D transport | Configure the weekly/manual runtime to emit the schema-valid judge receipt; missing transport remains WARN |
| Judge calibration | Periodically replay frozen packets against human labels |
| Historical document cleanup | Keep dated snapshots labeled historical and outside active status authority |
| Live retrieval dependencies | Validate environment-specific happy paths separately from governed degraded paths |

## Closeout decision

The implementation is ready for PR review when CI confirms the focused tests, Codex verifiers, deterministic SVP review, and S1 architecture proof on the branch head. Merge authority remains with the existing PR-only publisher and normal GitHub review controls.
