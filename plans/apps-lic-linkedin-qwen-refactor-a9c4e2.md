---
plan_id: apps-lic-linkedin-qwen-refactor-a9c4e2
plan_type: refactor
touches_agentic_core: false
touches_governance_ci: false
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
created: 2026-06-08
owner: Codex
---

# apps_lic LinkedIn Qwen Refactor - Disable apps_research Delegation

Refactor the current `apps_lic` implementation into one live product path: drafting a LinkedIn recruiter outreach message from Amit through the existing canonical dispatch spine, with Qwen/vLLM as the primary provider and deprecated `apps_research` delegation blocked fail-closed.

> **plan_id discipline**: filename stem `apps-lic-linkedin-qwen-refactor-a9c4e2` == `plan_id`. Wave markers use `plan=apps-lic-linkedin-qwen-refactor-a9c4e2`.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: DONE
CURRENT_WAVE: COMPLETE
LAST_COMPLETED_WAVE: W6
LAST_UPDATED: 2026-06-08

---

## Context (SCQA)

- **Situation** - `apps_lic` already has a current implementation with a canonical product entrypoint, dispatch bindings, route profile, HOP pipeline, provider configuration, integration bridges, and tests.
- **Complication** - The current implementation is believed to still expose a deprecated R3R4 managed research path through `apps_research`, CLI auto-research behavior, generic/email defaults, and success-producing bridge/dispatcher shims. That conflicts with the intended live spine: `U0 -> L1 -> L0 -> C0 -> PA -> L3 -> L2 -> Exit`.
- **Question** - How do we refactor the current `apps_lic` code so the only live product path drafts LinkedIn recruiter outreach from Amit, while deprecated research requests become terminal R5 outcomes and no new runtime path is introduced?
- **Answer** - First review and receipt the current implementation, then remove live R3R4 research routing from canonical dispatch/L0/CLI, bound C0/PA/L3/L2 responsibilities, make Qwen/vLLM the primary generation provider, convert integration shims to fail-closed compatibility, and prove the behavior with focused tests, static checks, runtime receipts, and closeout evidence.

---

## Structured Reasoning Packet

SR_INTAKE:
- Objective: Refactor current `apps_lic` to one LinkedIn recruiter outreach draft path using the existing canonical dispatch spine.
- Constraints: no new app, no second runtime path, no bypass of `canonical_dispatch`, no live `apps_research`, no live R3R4 route, no L3 retrieval/execution/model/tool calls, no send/post/write side effects, no code edits before the review receipt exists.
- Assumptions: the listed files exist or have nearby current equivalents; Qwen/vLLM tests can use controlled stub behavior where configured; deprecated compatibility modules may remain importable but must not import or call `apps_research`.
- Tier: T3, because this crosses CLI, runtime dispatch, route contracts, bindings, config, provider behavior, integrations, proof artifacts, and tests.

SR_PLAN:
1. Establish read-only evidence and write `artifacts/apps_lic/current_apps_lic_refactor_review.md`.
2. Remove live deprecated research routing from canonical dispatch, route profile, L0, and CLI ingress.
3. Refactor bounded evidence, prompt assembly, provider defaults, L3 orchestration, and L2/HOP boundaries.
4. Convert bridge/dispatcher/quality-gate integrations into deprecated fail-closed shims.
5. Replace generic/email defaults with LinkedIn recruiter defaults and update output contracts.
6. Add and update tests for no live research imports, R3R4 blocking, manual R4 success, boundary discipline, provider settings, and LinkedIn output.
7. Run scoped pytest and static checks, then write `artifacts/apps_lic/current_apps_lic_refactor_closeout.md`.

SR_APPROVAL:
- This plan is ready for user approval before implementation. Execution must start with read-only review and receipt generation.

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| W0 | W0.1-W0.3 | Current implementation review and receipt | ~10K | Listed files are current or have nearby equivalents | TODO | Review receipt exists before refactor edits |
| W1 | W1.1-W1.4 | Remove live R3R4 research path from dispatch, routing, and CLI | ~18K | Deprecated route constants can remain for compatibility | TODO | Research requests terminal R5; no bridge dispatch occurs |
| W2 | W2.1-W2.5 | Bounded evidence, PA contract, Qwen/vLLM, L3/L2/HOP boundaries | ~22K | Existing HOP and provider seams can be reused | TODO | Manual brief R4 path reaches C0, PA, L3, L2, Exit only |
| W3 | W3.1-W3.4 | Integration shims, defaults, proof fields, env docs | ~14K | Shims can preserve import compatibility without success paths | TODO | No production runtime import or call to `apps_research` remains |
| W4 | W4.1-W4.4 | Tests, static checks, closeout receipt | ~18K | Existing tests can be updated rather than replaced wholesale | TODO | Required pytest/static commands pass or failures are documented |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W0.1 | Evidence preflight | ADG/graph health if available, git status, listed file inventory | Codex may lack some Claude MCPs | ~2K | TODO |
| W0.2 | Current code review | `apps_lic/__main__.py`, dispatch, bindings, configs, integrations, engines, validators, tests | Must verify known problems before changing | ~6K | TODO |
| W0.3 | Review receipt | `artifacts/apps_lic/current_apps_lic_refactor_review.md` | Receipt is a hard gate before refactor edits | ~2K | TODO |
| W1.1 | CLI ingress contract | `canonical_dispatch.build_cli_ingress_raw` | `allow_research=True` must be recorded but disabled | ~4K | TODO |
| W1.2 | Canonical dispatch removal | `canonical_dispatch.py`, proof/result helpers if needed | Block stale R3R4 without generating ungrounded draft | ~6K | TODO |
| W1.3 | Route profile and L0 | L0 route JSON, `l0_binding.py` | Preserve compatibility constants while preventing live selection | ~5K | TODO |
| W1.4 | CLI/wizard auto-research block | `apps_lic/__main__.py`, CLI tests | Must fail closed, not silently ignore | ~3K | TODO |
| W2.1 | C0 evidence boundary | `c0_binding.py`, validators/contracts as needed | No hidden retrieval or research rescue path | ~4K | TODO |
| W2.2 | PA output contract | PA binding, schema, exit rubric, prompt templates | JSON-only LinkedIn message contract; no subject required | ~5K | TODO |
| W2.3 | Qwen/vLLM provider defaults | provider config, HOP config, `.env.example`, tools/vLLM docs if needed | Healthcheck fail-closed only when required | ~5K | TODO |
| W2.4 | L3 boundary | `l3_binding.py`, L3 receipt/context types | L3 packages only; no execution/retrieval/provider calls | ~4K | TODO |
| W2.5 | L2/HOP boundary | `l2_binding.py`, `config/hop_pipeline.py`, HOP tests | HOP may run only inside L2 | ~4K | TODO |
| W3.1 | Deprecated integration shims | `apps_research_bridge.py`, `managed_workflow_dispatcher.py`, `briefing_quality_gate.py` | Preserve imports but never import `apps_research` or succeed | ~5K | TODO |
| W3.2 | LinkedIn recruiter defaults | CLI defaults, ingress payload, route/profile config, schemas | Remove Jane Smith/Acme/email renewal defaults | ~3K | TODO |
| W3.3 | Exit/proof manifests | stage receipts, runtime proof bundle, spine run result | Proof must pass for both success R4 and terminal R5 | ~4K | TODO |
| W3.4 | Env and docs alignment | `.env.example`, `tools/vllm/*` if needed | Avoid cross-app env dependencies | ~2K | TODO |
| W4.1 | Runtime behavior tests | `tests/apps_lic/*`, governance tests | Deprecated tests may assert old success behavior | ~6K | TODO |
| W4.2 | Boundary/static tests | no-import, L3/L2/HOP/provider/LinkedIn output tests | Need strong assertions without brittle implementation coupling | ~5K | TODO |
| W4.3 | Verification commands | scoped pytest and static checks | Some MCP runners may be unavailable in Codex | ~4K | TODO |
| W4.4 | Closeout receipt | `artifacts/apps_lic/current_apps_lic_refactor_closeout.md` | Must summarize proof and remaining risks | ~3K | TODO |

---

## Out Of Scope

- Designing a new `apps_lic` app or adding a second runtime path.
- Bypassing `apps_lic.runtime.dispatch.canonical_dispatch`.
- Re-enabling live web research or `apps_research` delegation under another name.
- Sending, posting, writing to LinkedIn, or committing durable L4 state from this workflow.
- Refactoring unrelated apps, shared governance rules, or `agentic_core` unless execution discovers a directly blocking contract mismatch.
- Inventing recruiter, company, role, referral, relationship, metric, application, salary, compensation, visa, or sensitive personal facts.

---

## Wave 0 - Current Implementation Review and Receipt

WAVE_ID: W0
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED - read-only review plus required artifact receipt.

**Phases**:
- **W0.1** - Evidence preflight | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.2** - Current code review | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W0.3** - Review receipt | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `artifacts/apps_lic/current_apps_lic_refactor_review.md` exists before any refactor edit.
- Receipt covers current live entrypoint, canonical dispatch flow, `apps_research` coupling, R3R4 behavior, CLI/wizard auto-research, defaults, Qwen/vLLM declarations, HOP usage, deprecated-behavior tests, files to modify, and tests to add/update.
- If ADG, memory, pytest, or GitKraken MCPs are unavailable in Codex, the receipt names the unavailable MCP and the local fallback used.

---

## Wave 1 - Remove Live R3R4 Research Path

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W1.1** - Refactor `build_cli_ingress_raw` | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** - Refactor `canonical_dispatch` | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** - Refactor L0 route profile and binding | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** - Disable CLI/wizard auto-research | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `build_cli_ingress_raw` has the requested signature and always sets `research_requirements.allow_research=false`.
- `allow_research=True` records `requested_but_disabled=true` and deprecation metadata.
- `canonical_dispatch` docstring and live flow are `U0 -> L1 -> L0 -> C0 -> PA -> L3 -> L2 -> Exit`.
- No live import remains from `apps_lic.integrations.apps_research_bridge`, `apps_lic.integrations.managed_workflow_dispatcher`, or `apps_research.*` in canonical dispatch.
- Stale `R3R4_MANAGED_RESEARCH_THEN_DRAFT` returns terminal R5 with `APPS_RESEARCH_DEPRECATED`, no C0/PA/L3/L2 execution, and no research invocation.
- Route profile allows only `R4_MANAGED_DRAFT` and `R5_FALLBACK`; R3R4 is deprecated/forbidden compatibility only.
- CLI `--auto-research` fails closed or returns terminal R5; wizard no longer offers auto-research.

---

## Wave 2 - Bound Evidence, Generation, and Runtime Stages

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W2.1** - C0 evidence boundary | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** - PA output contract and prompt lineage | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** - Qwen/vLLM provider resolution | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.4** - L3 orchestration boundary | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.5** - L2/HOP boundary | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- C0 consumes only approved inline/manual/preloaded evidence and emits weak/empty support when insufficient.
- PA requires JSON-only LinkedIn output with `message_text`, no subject requirement, max default 600 characters, no markdown links, no em dash, and no unsupported claims.
- Prompt slot lineage represents `S0 -> D0 -> I0 -> E0 -> C0 -> M0 -> U0 -> H0 -> R0`.
- M0 binds `target_provider=vllm`, `target_model=Qwen/Qwen2.5-32B-Instruct-AWQ`, JSON-only output, and no silent fallback.
- Provider resolution honors the requested environment-variable order for base URL, model, provider, and timeout.
- `APPS_LIC_REQUIRE_QWEN_VLLM=1` fails closed before generation if vLLM healthcheck fails, except controlled test stub mode.
- L3 only builds bounded receipts/contracts/context and hands the step to L2.
- L2 is the only runtime binding allowed to invoke `HopPipelineExecutor(REGISTRY)`.
- HOP research stage consumes C0/manual/preloaded evidence only and never calls `apps_research`.

---

## Wave 3 - Compatibility Shims, Defaults, and Proof

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Phases**:
- **W3.1** - Convert integration modules to fail-closed shims | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** - Replace generic/email defaults | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** - Align stage receipts and runtime proof bundle | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.4** - Update `.env.example` and vLLM docs if required | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- `apps_lic/integrations/apps_research_bridge.py`, `managed_workflow_dispatcher.py`, and `briefing_quality_gate.py` have no live `apps_research` imports and cannot return success-producing managed research results.
- Deprecated execution returns terminal/fail-closed `APPS_RESEARCH_DEPRECATED` results.
- Default use case is `linkedin_recruiter_outreach_draft`; sender is Amit Ayer, Senior Agentic AI / AI Engineering Leader; default lead is Recruiter/Unknown with consent attested.
- Old email/enterprise renewal/Jane Smith/Acme defaults are removed from the live path.
- Successful live run proof includes `apps_research_invoked=false`, `r3r4_research_invoked=false`, `l3_participated=true`, `c0_invoked=true`, `pa_invoked=true`, `l2_executed=true`, and no send/L4/connector assertions.
- Deprecated research request proof includes terminal R5, `APPS_RESEARCH_DEPRECATED`, no C0/PA/L3/L2 execution, and `x3_disposition=DENY` or `SAFE_ABSTAIN`.

---

## Wave 4 - Tests, Static Checks, and Closeout

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W4.1** - Runtime behavior tests | ~6K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** - Boundary, provider, and LinkedIn output tests | ~5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** - Verification commands and static checks | ~4K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.4** - Closeout receipt | ~3K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- Tests cover no live `apps_research` imports, L0 never emitting R3R4, CLI auto-research blocking, canonical dispatch blocking stale R3R4, manual brief R4 success, L3 boundary, L2/HOP boundary, HOP research stage, provider config, and LinkedIn output contract.
- Required pytest selectors pass or any failure is triaged with exact failing tests and next action.
- Static import/call scans show no live research path, no direct HOP outside L2, and no send/post execution path.
- `artifacts/apps_lic/current_apps_lic_refactor_closeout.md` includes changed files, before/after behavior, removed/converted coupling, proofs, commands run, results, and remaining risks.

---

## Execution Details

### W0.1 - Evidence Preflight
**Scope**: Establish state and available governance tooling before touching implementation.

**Commands**:
```bash
git status --short --branch
git worktree list
python scripts/governance/verify_codex_backup.py
```

If available in the active surface, use ADG/Memory/GitKraken/Pytest MCP equivalents first. If unavailable in Codex, record the unavailable MCP and use the closest local script or CLI fallback.

### W0.2 - Current Code Review
**Scope**: Read the files named in the prompt and nearby current equivalents, with emphasis on actual live control flow rather than desired architecture.

**Required review topics**:
- Current live entrypoint and canonical dispatch flow.
- Current `apps_research` coupling points.
- Current R3R4 route behavior.
- Current CLI/wizard auto-research behavior.
- Current LinkedIn/email defaults.
- Current Qwen/vLLM model/provider declarations.
- Current HOP pipeline usage.
- Tests preserving deprecated behavior.
- Files to modify and tests to add/update.

### W0.3 - Review Receipt
**Scope**: Write `artifacts/apps_lic/current_apps_lic_refactor_review.md` before refactor edits.

**Required result**:
```text
artifacts/apps_lic/current_apps_lic_refactor_review.md
```

### W1-W3 - Refactor Execution
**Scope**: Make focused code/config/test edits in the current implementation only, preserving `canonical_dispatch` as the product entrypoint.

**Primary files in scope**:
```text
apps_lic/__main__.py
apps_lic/runtime/dispatch/canonical_dispatch.py
apps_lic/runtime/dispatch/stage_receipts.py
apps_lic/runtime/dispatch/runtime_proof_bundle.py
apps_lic/runtime/dispatch/spine_run_result.py
apps_lic/runtime/bindings/l0_binding.py
apps_lic/runtime/bindings/l1_binding.py
apps_lic/runtime/bindings/c0_binding.py
apps_lic/runtime/bindings/pa_binding.py
apps_lic/runtime/bindings/l3_binding.py
apps_lic/runtime/bindings/l2_binding.py
apps_lic/runtime/bindings/exit_binding.py
apps_lic/config/domain_contract/l0_route_profile.outreach_message.v1.json
apps_lic/config/hop_pipeline.py
apps_lic/config/outreach_schema.json
apps_lic/config/exit_rubric.yaml
apps_lic/prompt_assembly/templates/compact_recruiter_arc.yaml
apps_lic/integrations/apps_research_bridge.py
apps_lic/integrations/managed_workflow_dispatcher.py
apps_lic/integrations/briefing_quality_gate.py
apps_lic/engines/*
apps_lic/validators/*
.env.example
tools/vllm/README.md
tools/vllm/check_vllm.sh
tools/vllm/start_vllm_server_32b.sh
```

### W4.3 - Verification Commands
**Scope**: Run the prompt-requested tests and static checks.

**Pytest**:
```bash
pytest tests/apps_lic -q
pytest tests/governance -q
pytest tests/_apps_contract -q
```

**Static checks requested by prompt**:
```bash
grep -R "from apps_research\|import apps_research" apps_lic/runtime apps_lic/engines apps_lic/reasoning -n
grep -R "GovernedResearchRun" apps_lic -n
grep -R "ResearchRequest" apps_lic -n
grep -R "dispatch_managed_briefing" apps_lic/runtime apps_lic/engines apps_lic/reasoning -n
grep -R "AppsResearchBridge" apps_lic/runtime apps_lic/engines apps_lic/reasoning -n
grep -R "auto delegates to apps_research" apps_lic -n
grep -R "L3 apps_research support" apps_lic -n
grep -R "HopPipelineExecutor" apps_lic/__main__.py apps_lic/runtime/bindings/l3_binding.py -n
grep -R "linkedin_send\|connector_send\|external_http_post" apps_lic -n
```

On Windows/Codex, equivalent `rg` commands are acceptable if the exact grep command is unavailable, but the closeout must state the substitution.

---

## Gap Register

**GAP-1: Current code may differ from prompt assumptions**
- Verify every named issue in W0 before editing.
- If a named file moved or a behavior was already removed, record the current equivalent in the review receipt.

**GAP-2: Deprecated tests may encode desired backward compatibility**
- Some tests may intentionally protect import compatibility for old integration names.
- Preserve import compatibility where needed, but change success-producing behavior to fail-closed.

**GAP-3: Provider healthcheck may not be available in CI**
- Tests should distinguish production fail-closed behavior from configured test stub mode.
- Do not introduce external fallback generation.

**GAP-4: Static scans can produce false positives from deprecation prose**
- The hard no-import scans apply to live runtime/engines/reasoning imports.
- Compatibility shims may mention names in deprecation text only; closeout must explain allowed textual hits.

**GAP-5: HOP pipeline may currently mix stage intent and execution**
- Keep HOP execution in L2 only.
- If existing helper structure requires movement, document the boundary decision and test it.

---

## Definition of Done

DoD-1: Review receipt exists before refactor edits.
- Evidence: `artifacts/apps_lic/current_apps_lic_refactor_review.md` includes all required review bullets.
- Status: TODO

DoD-2: Live R3R4 research path is removed from canonical dispatch.
- Evidence: stale R3R4 route returns terminal R5 with `APPS_RESEARCH_DEPRECATED`, no C0/PA/L3/L2 execution, and no research invocation.
- Status: TODO

DoD-3: L0 and route profile allow only live R4/R5 behavior.
- Evidence: tests show `allow_research=True` and stale R3R4 convert to R5 fallback with deprecation reason codes.
- Status: TODO

DoD-4: CLI/wizard auto-research is disabled fail-closed.
- Evidence: CLI test for `--auto-research` exits 2 or terminal R5 and includes `APPS_RESEARCH_DEPRECATED`.
- Status: TODO

DoD-5: Manual brief R4 path works through the canonical spine.
- Evidence: manual brief test proves C0, PA, L3, L2, and Exit participate; `apps_research_invoked=false`.
- Status: TODO

DoD-6: L3 and L2 boundaries are enforced.
- Evidence: tests/static checks prove L3 has no research/provider/HOP/tool execution and L2 is the only runtime binding that calls `HopPipelineExecutor`.
- Status: TODO

DoD-7: Qwen/vLLM is the primary provider.
- Evidence: provider tests and `.env.example` show Qwen/vLLM defaults and required resolution order.
- Status: TODO

DoD-8: LinkedIn recruiter output contract is enforced.
- Evidence: tests validate `channel=linkedin`, `recipient_class=recruiter`, `message_text`, no subject requirement, length limit, low-friction ask, no em dash, no markdown links, and no unsupported claims.
- Status: TODO

DoD-9: Required tests and static checks are run.
- Evidence: closeout records `pytest tests/apps_lic -q`, `pytest tests/governance -q`, `pytest tests/_apps_contract -q`, and static scan results.
- Status: TODO

DoD-10: Closeout receipt exists.
- Evidence: `artifacts/apps_lic/current_apps_lic_refactor_closeout.md` covers files changed, before/after behavior, coupling removed/converted, proofs, test commands/results, and risks.
- Status: TODO

### Verification vs Deferral

| Item | Must Verify Before Completion | May Defer? | Deferral Condition |
|---|---|---|---|
| Review receipt | Yes | No | None |
| No live `apps_research` imports/calls | Yes | No | None |
| R3R4 terminal R5 behavior | Yes | No | None |
| Manual brief R4 success | Yes | No | None |
| Qwen/vLLM provider defaults | Yes | No | None |
| Full governance test suite outside requested selectors | No | Yes | Defer only if requested selectors pass and unrelated failures are documented |
| Live vLLM server generation | No | Yes | Defer if no local vLLM is running; stub mode must be explicit |

---

## Scope Expansion Authorization

When scope is discovered during execution, emit markers in order:

```text
DISCOVERED_SCOPE: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 wave=<N> phase=<M> gap="<what>" impact="<severity>"
AUTHORIZATION_DECISION: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 decision=<ACCEPTED|DEFERRED|SPLIT_TO_NEW_PLAN|REJECTED> authorized_by=<user|author_gate|self> decisive_reason="<why>"
SCOPE_EXPANSION: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 reason="<summary>" added="<waves/phases>" authorized="yes"
```

| Decision | When | Continues? |
|---|---|---|
| ACCEPTED | In-charter and necessary for the requested refactor | Yes, expanded scope |
| DEFERRED | Valid but not needed for the requested live path | Yes, original scope |
| SPLIT_TO_NEW_PLAN | Too large or outside `apps_lic` | Yes, original scope |
| REJECTED | New app design, alternate runtime path, or unrelated cleanup | Yes, original scope |

---

## Marker Quick Reference

Wave lifecycle markers must be at start of line and use the exact plan_id:

```text
PLAN_CREATED: slug=apps-lic-linkedin-qwen-refactor-a9c4e2 path=plans/apps-lic-linkedin-qwen-refactor-a9c4e2.md status=Not Started
WAVE_START: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 wave=<N>
WAVE_COMPLETE: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 wave=<N> note="+N tests, N files, scope=<summary>"
PHASE_COMPLETE: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 phase=<W1.1>
PLAN_COMPLETE: plan=apps-lic-linkedin-qwen-refactor-a9c4e2 note="<final outcome>"
```
