# SVP Engineering Reviewer Hub

Status: **Active reviewer navigation and proof hub**.

Agentic Workflow is presented as a deterministic control plane for governed enterprise agents. Use this page to choose the shortest credible review path for CTO, SVP Engineering, platform, governance, hiring, and contributor audiences.

SVP documentation review is intentionally operator-run outside GitHub Actions.
Use the local command below when a review is required; no repository workflow
registers it as pull-request CI.

## Start Here

| Audience | Read first | Why |
|---|---|---|
| Hiring manager / recruiter | [`../RECRUITER_GUIDE.md`](../RECRUITER_GUIDE.md) | Plain-English leadership and role signal |
| CTO / SVP Engineering | [`../EXECUTIVE_OVERVIEW.md`](../EXECUTIVE_OVERVIEW.md) | Platform thesis and executive implications |
| Engineering reviewer | [`../RUNTIME_CONTROL_PLANE.md`](../RUNTIME_CONTROL_PLANE.md) | Runtime authority, evidence, execution, exit, write control, and learning |
| Governance reviewer | [`../SVP_ENGINEERING_GOVERNANCE_README.md`](../SVP_ENGINEERING_GOVERNANCE_README.md) | Codex-primary, ADG, commit-time, and runtime evidence layers |
| Deep technical reviewer | [`../architecture/REVIEWER_GUIDE.md`](../architecture/REVIEWER_GUIDE.md) | Registry, proof commands, and inspection path |
| Documentation governance reviewer | [`../../scripts/governance/svp_docs_review.py`](../../scripts/governance/svp_docs_review.py) | Deterministic X2 checks and one X3 disposition |

## What This Repository Demonstrates

- **Platform strategy:** the governed runtime around the agent is the product boundary.
- **System design:** planning, route authority, evidence, prompt compilation, bounded execution, exit disposition, durable writes, replay, and learning are separated.
- **Governance maturity:** Codex execution discipline, commit-time controls, architecture-graph checks, runtime evidence, and documentation publication authority are distinct surfaces.
- **Exception discipline:** app deviations are formal registry state with compensating controls rather than silent bypasses.
- **Reviewer proof:** material claims point to source, commands, or receipts.

## Current Registry Snapshot

`apps_shared/integrations/app_registry.py` currently records:

- **3 governed entries:** `apps_exec`, `apps_research`, `apps_rg`;
- **5 formal exceptions:** `apps_architect`, `apps_eval`, `apps_lic`, `apps_qna`, `apps_underwriting_ai`;
- **0 ad hoc statuses.**

Run the proof commands for current branch status rather than relying on this static snapshot.

## Proof Commands

Run from the repository root:

```bash
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json
python scripts/governance/svp_docs_review.py --mode audit --phase pre --json
python ops_scripts/ci/check_governed_app_conformance.py
python ops_scripts/ci/run_architecture_proof.py
```

## Documentation Governance

The weekly SVP documentation automation is read-only. It may emit `NOOP`, `PLAN_ONLY`, `BLOCK`, or `ESCALATE_HUMAN`.

Approved edits use the separate manual automation and require:

1. a schema-valid approval receipt;
2. an isolated non-main branch;
3. X2 pre and post receipts;
4. an X1D receipt over the final packet and diff;
5. one X3 disposition;
6. `ALLOW_TO_PR` handoff to the existing PR-only main publisher.

The documentation automation does not merge or push directly to `main`.

For the complete GitHub landing page and portfolio navigation, start at [`../../README.md`](../../README.md).

## Historical Retrieval SVP Packet

The files below are retained as historical retrieval-system notes. They are not the current source of truth for repository-wide SVP positioning and should not be treated as current ROI, roadmap, or support commitments:

- [`Retrieval_System_SVP.md`](./Retrieval_System_SVP.md)
- [`Technical_Implementation_Guide.md`](./Technical_Implementation_Guide.md)
- [`demo_script.py`](./demo_script.py)

Prefer the active documents in [Start Here](#start-here) for current public positioning.

---

Last updated: July 2026.
