# Codex ADG Enforcement Decoupling

PLAN_ID: codex-adg-enforcement-decoupling-4d7a1c
PLAN_TYPE: codex_governance_change
STATUS: APPROVED
APPROVED_BY: user
APPROVAL_EVIDENCE: conversation directive `approve`
BASELINE_COMMIT: badba07f7bb5c233c5adbbfb8badc626252157f3
FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W5
LAST_COMPLETED_WAVE: W5
LAST_UPDATED: 2026-07-19

## Objective

Remove ADG as a mandatory prerequisite from active Codex enforcement. Missing, stale, unhealthy, or
unreachable ADG state must not block ordinary prompts, dependency inspection, edits, tests, proof,
evaluation, publication, or default Codex readiness.

ADG remains an optional capability. Explicit ADG generation, audit, repair, and reporting workflows
retain their own integrity contracts when invoked; this plan does not delete ADG product code,
artifacts, MCP configuration, CI gates, or automations.

## Scope

1. Root Codex operating contract and primary-execution documentation.
2. Active Codex constitutional, plan, scope, and core-operating rules.
3. Active prompt, grep, and stop-hook registrations and dispatchers.
4. Default Codex readiness and minimum-enforcement-home verification.
5. Skills that currently require graph-backed scope, test selection, or fail-closed ADG health.
6. Focused governance, hook, readiness, verifier, and skill-contract tests.
7. The active `apps_rg_simple` plan, replacing its certified-ADG prerequisite with source hashes,
   exact source inspection, boundary checks, import inspection, and runtime tests.

## Non-Goals

- Delete or disable the optional `adg_sqlite` MCP server.
- Delete `tools/adg`, ADG data, reports, schemas, or CI implementation.
- Weaken app/core boundary, author-gate, test-integrity, runtime-proof, or publication controls.
- Change product/runtime uses of runtime ADG evidence.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | W1 | Policy and skills | ~6K | Approved scope unchanged | COMPLETE | Active rules and skills state ADG is optional |
| W2 | W2 | Active enforcement | ~4K | Hook registrations are authoritative | COMPLETE | No prompt, grep, or stop ADG dispatch remains |
| W3 | W3 | Readiness and verifiers | ~5K | Explicit ADG opt-in remains supported | COMPLETE | Default readiness and minimum verifier omit ADG |
| W4 | W4 | Active app plan | ~3K | Exact source evidence replaces graph prerequisite | COMPLETE | No ADG stop condition remains in the app plan |
| W5 | W5 | Verification | ~5K | Unrelated baselines are reported separately | COMPLETE | Focused tests and scoped governance gates pass |

## Execution

### W1 - Policy and skills

- Remove ordinary T2/T3 ADG mandates from `AGENTS.md`, `docs/codex-primary-execution.md`, and active
  `.codex/rules` files.
- Make `adg-sqlite` and `graph-analysis` explicitly opt-in.
- Replace graph-mandatory phase, scope, and test-selection language with exact-source, import-aware,
  test-entrypoint, runtime-evidence, and explicit-uncertainty requirements.

### W2 - Active enforcement

- Unregister the ADG-first Grep hook.
- Remove ADG SSOT and dependency-warning dispatch from the prompt hook.
- Remove ADG post-response compliance audits from the stop dispatcher.
- Retire the corresponding blocking scripts from active enforcement while retaining optional ADG
  tooling outside the ordinary Codex path.

### W3 - Readiness and verifiers

- Remove `adg_sqlite` from default required callable routes.
- Remove unconditional ADG health/transport checks from default readiness.
- Preserve explicit opt-in ADG checks for ADG-specific work.
- Stop treating ADG automations as mandatory files in the minimum Codex-primary enforcement home;
  validate their contracts only when present or explicitly invoked.

### W4 - Active app plan

- Remove every certified-ADG prerequisite from
  `plans/apps-rg-simple-end-to-end-spine-e6a41d.md`.
- Preserve the CoreAddition author receipt, exact-path binding, no-app-literal checks, source revision
  and digest inventory, boundary checks, focused tests, runtime receipts, and claim ceilings.

### W5 - Verification

- Prove a T3 prompt is accepted without an ADG snapshot or route.
- Prove Grep is not ADG-gated.
- Prove default readiness emits no critical ADG prerequisite.
- Prove stop dispatch runs no ADG compliance auditor.
- Run focused hook/readiness/verifier tests, Codex primary verification, enforcement-home verification,
  skill contract gates, structure policy, and diff-scope review.

## Acceptance Criteria

1. No active Codex rule says ADG is mandatory for ordinary T2/T3 work.
2. No active hook blocks or warns ordinary work because ADG was not used.
3. Default Codex readiness does not require ADG process, snapshot, transport, or callability proof.
4. No stop hook audits whether ADG preceded grep or implementation.
5. Optional ADG workflows remain callable and `adg_sqlite` stays `required=false` in MCP config.
6. `apps_rg_simple` is no longer blocked on ADG certification.
7. All focused regression and governance verification commands pass, or unrelated pre-existing failures
   are reported without weakening the requested controls.

## Rollback

Implementation occurs in named worktree `codex-adg-enforcement-decoupling` from the baseline commit.
Before commit, rollback is `git restore --staged --worktree -- <plan-owned files>` and removal of only
plan-owned untracked test fixtures. After commit, rollback is a normal `git revert <commit>`.

## Stop Conditions

- A proposed change removes a non-ADG safety control.
- Optional ADG product or audit code would need deletion rather than decoupling.
- Hook changes affect app/core author gates, write protection, runtime RCA, or publication authority.
- Verification shows an ordinary Codex path still blocks solely on ADG state.

## Definition of Done

- Active Codex hooks, default readiness, rules, and skills treat ADG as optional.
- Explicit ADG workflows and automations remain available and internally validated when invoked.
- The `apps_rg_simple` plan contains no ADG prerequisite or ADG-derived stop condition.
- Focused hook/readiness/verifier regression tests pass.
- Codex primary repo verification and skill-contract checks pass; unrelated baseline failures are
  recorded with comparison evidence.
