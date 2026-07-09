# apps_rg Fast-Fail RCA: Why July 7 Did Not Fail Immediately

Date: 2026-07-09
Branch: `codex-apps-rg-fast-fail-rca`
Scope: RCA only. No runtime repair is included in this branch.

## Executive Finding

The July 7 Anthropic EY lane did not fast fail because the run selected the simple
grounded-read route (`R3_SIMPLE_GROUNDED_READ`) instead of the managed full-resume
route (`R3R4_MANAGED_WORKFLOW`).

That mattered because apps_research delegation is only executed for the managed
workflow route. Once the run landed on the simple route, the configured briefing
file was allowed to flow into lane generation and no mandatory apps_research
handoff gate stopped it first.

Plain English: the run took the wrong hallway. The hallway it took had a normal
briefing file in it, but not the apps_research-generated briefing. The system
should have stopped at the door and said "this is a fresh research run, but
apps_research did not produce the briefing." It did not.

## Artifact Evidence

Evidence was read from the primary checkout artifacts before this branch/worktree
was created. The artifact directories are gitignored and are not copied into this
worktree.

| Evidence point | July 6 pass | July 7 fail |
|---|---|---|
| Parent run root | `artifacts/rg_b_0706_r2` | `artifacts/apps_rg/runs/on_demand_anthropic_partnership_fresh_s2e` |
| EY proof root | `artifacts/apps_rg/runtime_proofs/full_resume_d192febb573a` | `artifacts/apps_rg/runtime_proofs/full_resume_2baf6e1b1bc2` |
| Spine route family | `R3R4_MANAGED_WORKFLOW` | `R3_SIMPLE_GROUNDED_READ` |
| Spine execution form | `MANAGED_WORKFLOW` | `SINGLE_STEP` |
| `research_delegation_executed` | `true` | `false` |
| Consumed briefing ref | `artifacts/rg_b_0706_r2/research/delegated_briefing.txt` | `apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_briefing.md` |
| Consumed briefing hash | `7cd45b22be5644398a37a5afabe359e9e9f62cec782f6961370b8675a25d6985` | `eff84e75119044243b3d231e38e61bd7fbe6519807513c7a22b9812c03202e52` |
| Briefing first line | `# Anthropic (private) - Manager of Applied AI Architecture, Partnerships briefing packet` | `Anthropic - Manager of Applied AI Architecture, Partnerships targeting brief` |
| Briefing length | `6562` chars | `4066` chars |
| apps_research envelope | present under `research/apps_research_briefing_envelope.json` | missing |
| Bridge files | fresh July 6 bridge request/response | stale July 4 bridge request/response, not the consumed briefing |
| Pre-dispatch apps_research receipt | not decisive for pass because delegation ran | absent under failed run/proof path |

The July 7 mandatory output also described the same failure condition:
`auto_research_internal=True; research_delegation_executed=False; source=RUN_SPECIFIC`.

## Primary Regression

Primary regression:

- Commit: `c5620d5a235da4802532bd78285dfed41f4971bf`
- Date: 2026-07-06 05:57:10 -0400
- Subject: `Checkpoint apps_rg L0 routing hardening`
- Local merge: `a4a215c9845541761200ac91e96eb1b65c54e54f`
- Merge subject: `Merge local branch codex-apps-rg-l0-routing-only into main`
- GitHub PR: none found via `gh pr` search for the branch/commit.

This change made `full_resume_managed` flag-gated while leaving
`default_single_step` as the production-enabled default.

Source evidence:

- `apps_rg/config/domain_contract/route_profiles.yaml`
  - `full_resume_managed::v1` requires `APPS_RG_ENABLE_MANAGED_WORKFLOW_L0`
  - `default_single_step::v1` has no activation flag and remains production-enabled
- `apps_rg/runtime/bindings/l0_binding.py`
  - `_profile_active` only activates flag-gated rows when the environment flag is truthy
  - `_select_profile` falls back to the one default row when no explicit active profile matches

Result: if the managed route flag is absent or not carried into the run process,
the same Anthropic resume request can route as `R3_SIMPLE_GROUNDED_READ`.

## Why Fast Fail Did Not Fire

The strict apps_research handoff gate exists, but it was not the universal e2e
gate for this path.

`tests/unit/apps_rg/test_pre_dispatch_preflight.py` proves that a configured
brief can be blocked when callers explicitly pass:

- `require_apps_research_handoff=True`
- `require_apps_research_x1_x3=True`

But the section CLI path in `apps_rg/__main__.py` calls the pre-dispatch gate
without those strict arguments. The defaults are false. That means ordinary lane
dispatch can validate that a briefing exists without also requiring that the
briefing was produced by apps_research.

There is a second route-specific gap in `apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`:
`should_delegate_apps_research` returns false unless the route family is
`R3R4_MANAGED_WORKFLOW`. Once July 7 routed as `R3_SIMPLE_GROUNDED_READ`, the
apps_research hop was skipped by design.

So the failure chain was:

1. Managed route flag was not effective for the July 7 run.
2. L0 selected `R3_SIMPLE_GROUNDED_READ`.
3. apps_research delegation did not execute because delegation is tied to the managed route.
4. The section preflight did not require a strict apps_research handoff.
5. The configured briefing file was accepted as lane input.
6. EY lane generation ran and later surfaced the two-unique-bullets defect.

## Later Compounding Regression

A later change codified a related non-fast-fail behavior, but it happened after
the observed July 7 morning EY failure.

- Commit: `ca21b3e29753261356a51afba2c22e548900762a`
- Date: 2026-07-07 22:45:12 -0400
- Subject: `fix apps_rg fresh e2e post-runtime`
- Local merge: `2acff50883eb631c66d7b4d88c6c58ac0b6d000a`
- GitHub PR mapping observed: PR #510, `Fix apps_rg section aggregation convergence`

This change added `research_failure_nonterminal` and
`research_fallback_to_manual_brief` in
`apps_rg/runtime/orchestration/r3r4_whole_run_orchestration.py`. In plain terms,
if apps_research failed but a configured brief was present, the run could keep
going instead of failing.

That did not cause the July 7 morning artifact, but it is the same class of bug:
configured briefing input can become a survival path when fresh apps_research
should be mandatory.

## Adjacent Risk

Commit `fc5edb1f4a367963cdac58a396db59f63cd8cdb9`
(`Fix apps_rg section aggregation convergence`) added patch-run behavior that
preserves a majority briefing already used by accepted lanes. That can be useful
for run coherence, but it is risky unless the preserved briefing is proven to be
an apps_research handoff when fresh research is required.

This is adjacent, not the primary cause of the July 7 EY lane failure.

## Correct Contract

For this Anthropic fresh source-to-end run:

1. If `auto_research_internal=True`, apps_research must generate the briefing
   consumed by apps_rg, unless there is an explicit operator skip/waiver.
2. If the run selects anything other than `R3R4_MANAGED_WORKFLOW`, it must fail
   before section lanes start.
3. If no valid apps_research envelope is observed, the run must fail before
   section lanes start.
4. A configured briefing file may be a bootstrap input to apps_research, but it
   must not be treated as the consumed final briefing for a fresh e2e proof.

## Recurrence Guards

Recommended repair scope:

1. Add a root fresh-e2e route assertion:
   fail before U0/lane dispatch unless route family is `R3R4_MANAGED_WORKFLOW`
   when `--fresh-e2e` or equivalent fresh-source-to-end mode is active.

2. Make strict apps_research handoff mandatory when `auto_research_internal=True`:
   pass `require_apps_research_handoff=True` and
   `require_apps_research_x1_x3=True`, or enforce the same invariant at the
   whole-run root before section lanes can start.

3. Remove or fence `research_fallback_to_manual_brief`:
   fallback may only be legal under an explicit operator skip/waiver that is
   visible in the final mandatory output.

4. Add a regression test using the exact Anthropic fixtures:
   with `auto_research_internal=True`, configured briefing present, and no valid
   apps_research envelope, the run must exit before `ey_bullets` dispatch.

5. Add mandatory output enforcement:
   any final report with `auto_research_internal=True` and
   `research_delegation_executed=False` must be terminal failure, not a completed
   or partially completed e2e proof.

## Bottom Line

The July 7 run did not fast fail because routing changed the run out of the
managed apps_research path, and the remaining e2e/lane gates treated the existing
configured briefing as enough to continue. The fast-fail rule existed in pieces,
but it was not wired as a mandatory root invariant for the source-to-end run.
