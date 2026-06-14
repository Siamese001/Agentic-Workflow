---
plan_id: github-actions-ci-rationalization-b8a4c2
plan_format: v2
plan_type: infra
touches_agentic_core: false
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
supersedes: []
---

# GitHub Actions CI Rationalization

Refactor GitHub Actions so PR checks validate only changed, GitHub-checkable surfaces while full-repo evidence remains manual or scheduled.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-06-14

---

## Context (SCQA)

- **Situation** — The repo has many GitHub workflows, including broad PR checks, manual evidence workflows, three duplicated runtime smoke workflows, and a heavy `common-setup` composite action.
- **Complication** — Normal PR CI can still run whole-repo gates or stale historical checks, which makes a small PR prove unrelated repository state.
- **Question** — How do we make GitHub PR CI answer only whether the PR diff broke the surface it touched?
- **Answer** — Split PR CI into stable summary workflows with changed-file routing, move whole-repo proof to manual evidence workflows, replace common setup, and add a workflow reference self-check.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1, W1.2 | CI setup primitives and runtime smoke consolidation | ~8K | Existing smoke commands remain representative | ✅ DONE | `python-setup` and `runtime-smokes` landed; replaced smoke files removed |
| W2 | W2.1, W2.2 | Contract gates and workflow self-check | ~10K | Whole-repo-only scripts may be moved out of PR blocking instead of rewritten | ✅ DONE | PR blocking checks have changed-file routing and stable summary jobs |
| W3 | W3.1, W3.2 | Manual workflow cleanup and deletion pass | ~9K | Manual evidence workflows stay runnable but not PR required | ✅ DONE | Stale PR/nightly logic removed or matched to real triggers; `common-setup` deleted |
| W4 | W4.1, W4.2 | Verification and branch-protection handoff | ~6K | Branch protection settings are outside local files | ✅ DONE | Local validation passes and required-check reset is documented |

### Phase Progress

| Phase | Title | Status |
|-------|-------|--------|
| W1.1 | Add `python-setup` composite action | ✅ DONE |
| W1.2 | Create consolidated `runtime-smokes` workflow | ✅ DONE |
| W2.1 | Refactor `contract-gates` to diff-scoped summary flow | ✅ DONE |
| W2.2 | Add workflow reference checker and `ci-self-check` | ✅ DONE |
| W3.1 | Clean manual/full-repo evidence workflow trigger truthfulness | ✅ DONE |
| W3.2 | Remove replaced/stale workflows and `common-setup` | ✅ DONE |
| W4.1 | Run scoped validation | ✅ DONE |
| W4.2 | Review diff and document branch-protection reset | ✅ DONE |

---

## Out Of Scope

- Local AI agent behavior, local merge-to-main behavior, branch workflow, or local governance hooks unless directly invoked by GitHub Actions.
- Application/runtime code, except minimal changed-file support for CI scripts that are directly used by GitHub workflows.
- Applying GitHub branch-protection settings, pushing, or creating validation PRs without separate explicit approval.

---

## Wave 1 — Setup And Runtime Smokes

WAVE_ID: W1
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER
CHECKPOINT: A

**Authorization**: APPROVED_BY_USER — User approved the plan and requested a new worktree branch.

**Phases**:
- **W1.1** — Add `python-setup` composite action | ~3K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W1.2** — Create consolidated `runtime-smokes` workflow | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `.github/actions/python-setup/action.yml` has no checkout and supports install modes.
- `.github/workflows/runtime-smokes.yml` has a `changes` job, conditional smoke lanes, and always-running `smoke-summary`.
- The three replaced runtime smoke workflows are deleted.

---

## Wave 2 — Diff-Scoped PR Gates

WAVE_ID: W2
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER
CHECKPOINT: B

**Phases**:
- **W2.1** — Refactor contract gates | ~6K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W2.2** — Add workflow reference checker and CI self-check | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- `contract-gates` computes changed files first and exposes `contract-summary` as the stable required job.
- Whole-repo-only checks are not normal PR blockers.
- `ci-self-check` runs only when GitHub workflow/action or checker files change.
- `check_workflow_references.py` supports changed-file mode and catches missing paths, absent `requirements.txt`, stale event logic, deleted workflow names, and old action references.

---

## Wave 3 — Manual Evidence Workflow Cleanup

WAVE_ID: W3
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER
CHECKPOINT: C

**Phases**:
- **W3.1** — Clean workflow trigger truthfulness | ~5K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W3.2** — Delete replaced/stale workflow/action files | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- Manual-only workflows do not claim nightly or PR behavior unless they have those triggers.
- Workflows without PR triggers do not request PR comment permissions or run PR comment steps.
- `common-setup` is removed after all callers migrate.
- Present historical workflows are either made manual/advisory/diff-scoped or removed according to the accepted final inventory.

---

## Wave 4 — Verification And Handoff

WAVE_ID: W4
WAVE_STATUS: DONE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: APPROVED_BY_USER
CHECKPOINT: D

**Phases**:
- **W4.1** — Run scoped validation | ~4K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES
- **W4.2** — Review diff and document required checks | ~2K tokens | PHASE_STATUS: DONE | PHASE_COMPLETE: YES

**Acceptance**:
- YAML files parse.
- New checker passes on changed CI files.
- Focused pytest or direct script tests pass for the checker.
- Final report names the desired branch-protection checks and calls out GitHub settings that require manual or GitHub API follow-up.

---

## Execution Details

### W1.1 — Add `python-setup`
**Scope**: Replace the heavy checkout/install composite action with a parameterized Python setup action.

**Commands**:
```bash
python -m pytest <new-checker-tests> -q
```

### W1.2 — Consolidate Runtime Smokes
**Scope**: Move R1B, runtime spine, and UWG smoke lanes into one workflow with a stable summary job.

**Commands**:
```bash
python ops_scripts/ci/check_workflow_references.py --changed-files .github/workflows/runtime-smokes.yml
```

### W2.1 — Refactor Contract Gates
**Scope**: Add changed-file routing and make summary jobs the PR-required surface.

**Commands**:
```bash
python ops_scripts/ci/check_workflow_references.py --changed-files .github/workflows/contract-gates.yml
```

### W2.2 — Add CI Self-Check
**Scope**: Implement changed-file-aware workflow reference validation and wire it to GitHub Actions.

**Commands**:
```bash
python ops_scripts/ci/check_workflow_references.py --changed-only --base-ref main
```

### W3.1 — Clean Manual Workflows
**Scope**: Align workflow comments, names, permissions, and event conditions with actual triggers.

**Commands**:
```bash
python ops_scripts/ci/check_workflow_references.py --changed-only --base-ref main
```

### W3.2 — Delete Replaced Files
**Scope**: Remove `common-setup` and replaced smoke workflows after replacements exist.

**Commands**:
```bash
git status --short
```

### W4.1 — Validate
**Scope**: Run parser checks, the new checker, and focused tests.

**Commands**:
```bash
python -m pytest tests/unit/ops_scripts/ci/test_check_workflow_references.py -q
python ops_scripts/ci/check_workflow_references.py --changed-only --base-ref main
```

### W4.2 — Handoff
**Scope**: Review diff and produce the branch-protection reset list.

**Commands**:
```bash
git diff --stat
git diff -- .github ops_scripts/ci/check_workflow_references.py
```

---

## Gap Register

**GAP-1: ADG MCP unavailable in Codex**
- Structural ADG MCP queries are not exposed in this Codex session.
- Fallback: use repo scripts and direct Git evidence for this GitHub-only CI refactor.

**GAP-2: Branch protection is outside local file state**
- Required checks may need GitHub repository settings updates after workflow names change.
- Impact: code can prepare the stable summary checks, but the actual protection reset is a separate GitHub operation.

**GAP-3: Current checkout has unrelated dirty work**
- Primary checkout has staged and unstaged unrelated changes.
- Fallback: implementation happens in `C:\Git\.chat-worktrees\codex-github-actions-ci-rationalization` on `codex/github-actions-ci-rationalization`.

---

## Definition of Done

DoD-1: PR CI is diff-scoped
- Evidence: `contract-gates`, `runtime-smokes`, and `ci-self-check` compute changed files and expose stable summary jobs.
- Status: DONE

DoD-2: Runtime smoke consolidation is complete
- Evidence: `.github/workflows/runtime-smokes.yml` exists and the three replaced smoke workflows are deleted.
- Status: DONE

DoD-3: Workflow reference checker works
- Evidence: `python -m pytest tests/unit/ops_scripts/ci/test_check_workflow_references.py -q` passes with 6 tests.
- Status: DONE

DoD-4: Workflow/action references are internally consistent
- Evidence: `python ops_scripts/ci/check_workflow_references.py --all` and `--changed-only` exit 0.
- Status: DONE

DoD-5: Manual evidence workflows remain available but non-blocking
- Evidence: manual/full-repo workflows keep `workflow_dispatch` and no normal PR required-check dependency is introduced.
- Status: DONE

DoD-6: Branch-protection reset is documented
- Evidence: final handoff names target required checks: `ci-self-check / workflow-reference-check`, `contract-gates / contract-summary`, and `runtime-smokes / smoke-summary`.
- Status: DONE

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```
DISCOVERED_SCOPE: plan=github-actions-ci-rationalization-b8a4c2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=github-actions-ci-rationalization-b8a4c2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=github-actions-ci-rationalization-b8a4c2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter, absorbable | Yes, expanded scope |
| DEFERRED | Valid but time-gated | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large | Yes, original scope |
| REJECTED | Gold-plating | Yes, original scope |

---

## Supersedes

| Predecessor slug | Reason |
|---|---|
| _None_ | Net-new GitHub Actions rationalization plan. |

_None — net-new plan._

---

## Marker Quick Reference

Wave lifecycle markers:
```
WAVE_START: plan=github-actions-ci-rationalization-b8a4c2 wave=<N>
WAVE_COMPLETE: plan=github-actions-ci-rationalization-b8a4c2 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=github-actions-ci-rationalization-b8a4c2 phase=<W1.1>
PLAN_COMPLETE: plan=github-actions-ci-rationalization-b8a4c2 note="<final outcome>"
```
