# Reviewer Guide — Governed Architecture

> **Start here.** This is the technical entry point for reviewing the governed architecture.  
> Read time: about five minutes.  
> One-command proof: `python ops_scripts/ci/run_architecture_proof.py`

## What was built

Agentic Workflow provides a shared control-plane substrate for app packages that have adopted the governed runtime path. Governed entries use shared planning, routing, context, execution, exit, write-control, replay, and observation surfaces rather than rebuilding those responsibilities inside each app.

```text
U0 -> L1 -> L0 -> C0/Prompt Assembly -> L2 or L3/L2 -> Exit -> UWG -> L4
                                                               |
                                                               `-> L6 after run boundary
```

Apps that cannot use the generic runner or entrypoint are recorded as formal exceptions with reason codes, safe/blocked surfaces, compensating controls, owners, and review cadence.

## Reading order

| Step | Read or run | Purpose |
|---|---|---|
| 1 | This file | Reviewer orientation |
| 2 | [`../RUNTIME_CONTROL_PLANE.md`](../RUNTIME_CONTROL_PLANE.md) | Authority and runtime model |
| 3 | [`architecture-proof-pack.md`](architecture-proof-pack.md) | Proof command map and current registry shape |
| 4 | `python ops_scripts/ci/run_architecture_proof.py` | Current executable status |
| 5 | [`governed-app-contract.md`](governed-app-contract.md) | Governed and formal-exception contracts |
| 6 | [`ROLLOUT_CLOSEOUT.md`](ROLLOUT_CLOSEOUT.md) | Current closeout and tracked gaps |

## Executive walkthrough

**Problem:** application packages can drift into separate routing, retrieval, execution, and governance implementations. Static architecture prose does not prevent that drift.

**Control model:**

1. `APP_REGISTRY` classifies governed entries and formal exceptions.
2. Governed entrypoints bind apps to the shared runtime controls.
3. Formal exceptions expose compensating controls instead of hiding bypasses.
4. The conformance gate checks registry shape, imports, capability tokens, exception metadata, and control hooks.
5. The behavioral proof exercises governed behavior and exception controls.
6. The release runner composes the structural, behavioral, and regression suites.
7. Reviewer-facing counts are derived from the registry at runtime rather than copied into the runner.

**Current registry snapshot:**

- **3 governed entries:** `apps_exec`, `apps_research`, `apps_rg`;
- **5 formal exceptions:** `apps_architect`, `apps_eval`, `apps_lic`, `apps_qna`, `apps_underwriting_ai`;
- **0 ad hoc statuses.**

The registry and current command output outrank dated prose when status changes.

## Engineer quickstart

```bash
# Codex governance contract
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json

# Structural registry and exception checks
python ops_scripts/ci/run_architecture_proof.py --suite S1

# Structural plus behavioral proof
python ops_scripts/ci/run_architecture_proof.py --skip-regression

# Full architecture proof
python ops_scripts/ci/run_architecture_proof.py
```

Targeted behavioral commands remain available through `tools/eval/retrieval_benchmark.py`. Prefer `--exception-framework-proof` for the current registry model; older grouped proof names may remain as compatibility surfaces.

Inspect the registry directly:

```bash
python -c "from apps_shared.integrations.app_registry import APP_REGISTRY; [print(k, v.status) for k, v in APP_REGISTRY.items()]"
```

## What to inspect

### Structural correctness

- App packages appear in the registry.
- Governed entries expose an importable governed runner or canonical callable.
- Capability tokens are versioned.
- Formal exceptions use canonical reason codes.
- Blocked and safe surfaces are declared.
- Compensating controls and review cadence are present.
- Partial-adoption handlers import and report control state.
- Ad hoc status values are rejected.

### Behavioral correctness

- Governed entries exercise happy and degraded behavior.
- Degraded evidence paths abstain or fail safely rather than inflating support.
- Exception handlers emit the required telemetry and conformance evidence.
- Exit and disposition evidence is recorded.
- Current results align with the registry rather than a retired app grouping.

### Governance correctness

- `.codex` remains the repo governance home.
- The weekly SVP documentation automation is audit-only.
- Approved documentation edits use the separate manual refresh.
- `ALLOW_TO_PR` is a handoff to the PR-only main publisher, not merge authority.
- X1D judgment does not override X2 deterministic failures.
- X3 emits one bounded disposition.

## Current validation posture

The proof runner now derives its registry summary from `apps_shared/integrations/app_registry.py`. It does not maintain a second app-count constant.

Use current output as the authority:

```bash
python ops_scripts/ci/check_governed_app_conformance.py
python ops_scripts/ci/run_architecture_proof.py
```

A static document may describe the expected proof shape, but it must not claim current green status without command or receipt evidence.

## Known non-blocking environment gaps

| Gap | Expected treatment |
|---|---|
| No live vector collection in a proof environment | Validate the governed abstain/degraded path |
| Clock or provider test-harness mismatch | Record the bounded fallback and keep disposition evidence |
| Provider prompt-context mismatch in a test harness | Preserve failure classification and sealed output evidence |

The tracked register is [`RELEASE_READINESS.md`](RELEASE_READINESS.md). Current executable results outrank its dated history sections.

## Key files

| File | Role |
|---|---|
| `apps_shared/integrations/app_registry.py` | App classification source of truth |
| `apps_shared/integrations/governed_app_runner.py` | Shared governed runner |
| `ops_scripts/ci/check_governed_app_conformance.py` | Structural conformance gate |
| `ops_scripts/ci/run_architecture_proof.py` | Registry-driven release runner |
| `tools/eval/retrieval_benchmark.py` | Behavioral and regression proof suites |
| `scripts/governance/svp_docs_review.py` | Deterministic SVP documentation X2/X3 engine |
| `.codex/automations/svp-readme-documentation-refresh/automation.toml` | Weekly read-only audit contract |
| `.codex/automations/on-demand-svp-documentation-refresh/automation.toml` | Approval-bound edit contract |
| `architecture-proof-pack.md` | Proof map and registry snapshot |
| `governed-app-contract.md` | Governed and exception schema |

## Reviewer takeaway

The leadership signal is not the number of gates. It is the operating model: architecture claims have an authority source, a deterministic check, a behavioral proof path, a bounded exception model, and a publication control surface.
