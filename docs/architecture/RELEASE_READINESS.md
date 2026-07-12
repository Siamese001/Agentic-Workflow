# Architecture Release Readiness Register

> **Status source:** current command output and receipts  
> **Registry source:** `apps_shared/integrations/app_registry.py`  
> **Proof command:** `python ops_scripts/ci/run_architecture_proof.py`

This register tracks the reviewer-facing architecture posture. It is not a substitute for current proof execution.

## Current registry shape

The committed registry currently records:

- **3 governed entries:** `apps_exec`, `apps_research`, `apps_rg`;
- **5 formal exceptions:** `apps_architect`, `apps_eval`, `apps_lic`, `apps_qna`, `apps_underwriting_ai`;
- **0 ad hoc statuses.**

The release runner derives these counts from `APP_REGISTRY` and prints them with the suite result.

## Current proof matrix

| Surface | Command | Authority |
|---|---|---|
| Codex primary contract | `python scripts/governance/verify_codex_primary.py` | Repo governance structure and required anchors |
| Codex enforcement home | `python scripts/governance/verify_codex_enforcement_home.py --json` | Repo-owned automation and skill placement |
| App conformance | `python ops_scripts/ci/check_governed_app_conformance.py` | Registry, governed entrypoints, formal exceptions, compensating controls |
| Architecture proof | `python ops_scripts/ci/run_architecture_proof.py` | Structural, behavioral, and regression composition |
| SVP documentation review | `python scripts/governance/svp_docs_review.py --mode audit --phase pre --json` | X2 deterministic review and one X3 disposition |

A green claim requires current command evidence. Dated counts or historical release notes do not certify the current branch.

## SVP documentation publication posture

| Control | Current design |
|---|---|
| Weekly cadence | Read-only audit |
| Edit authority | Separate manual automation with approval receipt |
| Deterministic review | X2 pre and post receipts |
| Senior-reader judgment | X1D receipt; unavailable transport degrades to WARN |
| Final decision | One X3 receipt |
| Publication | `ALLOW_TO_PR` handoff to `on-demand-pr-main-publisher` |
| Direct main push | Forbidden |

## Tracked gaps

### GAP-01 — Live retrieval dependency may be absent in proof environments

- **Severity:** low
- **Behavior:** C0 may return no shaped evidence and drive a governed abstain/degraded result.
- **Required proof:** disposition, evidence-status, and telemetry remain present.
- **Owner:** deployment/platform.
- **Release impact:** non-blocking when the degraded path is the expected test posture.

### GAP-02 — Test-harness clock/provider interface drift

- **Severity:** low
- **Behavior:** a bounded fallback may be exercised when test doubles lag the current interface.
- **Required proof:** route and disposition remain deterministic and the fallback is visible.
- **Owner:** platform.
- **Release impact:** non-blocking only when the selected proof explicitly expects that path.

### GAP-03 — Prompt/provider context mismatch in isolated proof paths

- **Severity:** low
- **Behavior:** provider invocation may reject a malformed or outdated context shape.
- **Required proof:** failure classification, sealed output, and Exit evidence remain available.
- **Owner:** platform/provider integration.
- **Release impact:** evaluated by the current suite, not pre-declared green.

### GAP-04 — Historical architecture documents can outlive registry changes

- **Severity:** medium
- **Behavior:** dated rollout notes may retain retired app groupings or check counts.
- **Control:** active reviewer packet, registry consistency gate, link/command checks, and explicit historical labeling.
- **Owner:** platform documentation.
- **Release impact:** blocks public reviewer claims when active documents disagree with `APP_REGISTRY`.

### GAP-05 — Judge quality requires periodic calibration

- **Severity:** medium
- **Behavior:** X1D may drift toward persuasive prose rather than evidence-backed senior-reader judgment.
- **Control:** frozen rubric version, judge identity, prompt hash, packet digest, and periodic human-labeled replay.
- **Owner:** evaluation platform.
- **Release impact:** X1D does not override deterministic X2 failures.

## Historical note

The initial governed-app rollout was documented in April 2026. Those records are useful history, but app classifications, proof counts, and handler names have changed since that snapshot. Active reviewer documents and current command output are the operational sources.

## Release decision rule

A reviewer-facing architecture update is ready for PR handoff when:

1. app classifications agree with `APP_REGISTRY`;
2. required links and proof commands resolve;
3. Codex primary and enforcement-home verifiers pass;
4. architecture conformance and selected behavioral proofs pass;
5. X2 post is `ALLOW` or bounded `WARN`;
6. X1D is `ALLOW` or bounded `WARN` with no high-severity finding;
7. X3 is `ALLOW_TO_PR`;
8. the branch is handed to the PR-only main publisher.

## Current reviewer statement

> The repository has a registry-backed governed-entry and formal-exception model, executable architecture proofs, and a separated documentation audit/edit/publication workflow. Current green status must be established from commands and receipts on the reviewed commit.
