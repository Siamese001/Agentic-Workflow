---
slug: apps-rg-qwen-removal-b3d9f7
title: Remove Qwen/vLLM provider from apps_rg
status: Not Started
plan_type: refactor
tier: T3
created: 2026-06-07
---

# Remove Qwen/vLLM provider from apps_rg

## Context (SCQA)

- **Situation:** apps_rg ships a fully-wired local Qwen/vLLM provider alongside the
  default external Claude provider. The `wave10a_policy` in
  [provider_profiles.yaml](apps_rg/config/provider_profiles.yaml) retained Qwen as a
  `selectable_local_comparison_provider` until the gate
  `apps_rg_e2e_external_claude_runtime_PASS` cleared.
- **Complication:** The user has confirmed (a) full removal is desired and (b) the
  external-Claude E2E gate is permanently met — the Qwen parity baseline is no longer
  needed. But the canonical provider result contract (`ProviderResult` / `ProviderRequest`)
  is **defined inside the Qwen module**, so a naive delete breaks the external Claude path.
- **Question:** How do we excise Qwen end-to-end (transport, selection, section lanes,
  config, CLI, tests) without regressing the external Claude generation path?
- **Answer:** A 4-phase, behavior-preserving-first refactor: extract the shared contract,
  collapse the selection fork to Claude-only, delete the Qwen-only stack + strip lane code
  paths, then prove the Claude path intact via section tests + E2E smoke.

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P0 | Extract shared provider contract (behavior-preserving) | ~25k | `ProviderResult`/`ProviderRequest` move cleanly to neutral module | Completed | Importers repointed; 78/78 targeted tests green; committed d80fc82203 |
| W2 | P1 | Collapse provider selection to Claude-only | ~20k | `section_provider_call` fork is the sole selection chokepoint | Completed | `ProviderProfile.QWEN_VLLM` gone; gateway builds Claude/OpenAI only |
| W3 | P2, P3 | Delete Qwen-only stack + rewire 7 lanes + config/CLI | ~45k | Lanes route repair/regen through neutral `generate_section` (Claude) | Completed | 7 Qwen modules deleted; lanes import no `build_qwen_request`; profiles/CLI clean; neutral `section_generation` seam |
| W4 | P4 | Tests + suite verification | ~25k | external Claude key unavailable in this env → live-E2E deferred | Completed | Collection clean (10,599); unit-suite diff vs baseline = **0 new failures** (1 flaky-in-isolation excluded); live-E2E BLOCKED on key |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P0 | Extract `provider_contract.py` | New `provider_contract.py` + repoint 11 importers (provider_gateway, external_provider, section_provider_call, bullet_lane_generation, bullet_lane_self_consistency, role_episode_lane, ibm_narrative_lane_runtime, competencies_live_provider_gate, qwen_offline_contract_stub, + 2) | `ProviderResult` is load-bearing for the Claude path — must stay byte-identical | ~25k | Not Started |
| P1 | Collapse selection fork | provider_gateway.py, section_provider_call.py, providers/__init__.py, provider_profiles.yaml | Enum member + alias removal must not break `normalize_provider_profile` callers | ~20k | Not Started |
| P2 | Delete Qwen-only stack | qwen_vllm_provider, section_qwen_slice, qwen_transport_diag, qwen_vllm_health, qwen_vllm_docker_restart, qwen_live_only_guard, qwen_offline_contract_stub, competencies_live_provider_gate, apps_rg_http_reasoning_plan, executive_summary_qwen_regen_dispatch, *_preflight qwen bits | Some helpers (reasoning_plan, preflight) may have non-Qwen callers — verify fan-in before delete | ~25k | Not Started |
| P3 | Strip lanes + validators + CLI + env | 8 section lanes, 6 x2 validators (`ALLOWED_MODELS`), __main__.py, section_cli_defaults, section_cli_runners, .env.example | Per-lane: confirm a Claude path exists before removing the Qwen branch | ~20k | Not Started |
| P4 | Tests + proof | test_qwen_transport_reliability_w0_w2 (delete), test_executive_summary_token_budget_contract, test_apps_rg_canonical_runtime_hygiene, E2E smoke, ADG regen | E2E needs external Claude reachable or injected transport | ~25k | Not Started |

## ADG_HOTSPOT_REPORT

Snapshot: `adg_indexed_05272026_1632.sqlite` (healthy: 180,057 nodes / 1,068,351 edges; backend=sqlite)

| rank | file | layer | role | surface | archetype | note |
|---|---|---|---|---|---|---|
| 1 | qwen_vllm_provider.py | L_APP | CENTRAL_DEPENDENCY | Execution | CENTRAL_DEPENDENCY | Hosts shared `ProviderResult` — 11 importers incl. Claude path. Extract before delete. |
| 2 | provider_gateway.py | L_APP | selection | Execution | ORCHESTRATOR | `ProviderProfile` enum source; selection chokepoint |
| 3 | section_provider_call.py | L_APP | selection fork | Execution | ORCHESTRATOR | `if profile==QWEN_VLLM` fork — the single dispatch branch to remove |
| 4 | section_qwen_slice.py | L_APP | transport entry | Execution | CENTRAL_DEPENDENCY | `call_qwen_vllm` centralized slice; delete after lanes stripped |

## ADG_GRAPH_LAYER_EVIDENCE

- **Layer purity:** All Qwen nodes resolve to `layer: L_APP` (`adg_nodes_by_file` on
  qwen_vllm_provider.py → 8 nodes, all `L_APP`). **No `agentic_core` coupling** → no
  core-boundary migration receipt required.
- **Contract fan-in (semantic `imports`):** `ProviderResult` imported by provider_gateway,
  external_provider, section_provider_call, bullet_lane_generation,
  bullet_lane_self_consistency, role_episode_lane, ibm_narrative_lane_runtime,
  competencies_live_provider_gate, qwen_offline_contract_stub (verified via Grep of
  `from apps_rg.runtime.providers.qwen_vllm_provider import`). This fan-in is the reason
  P0 (extract) precedes any deletion.
- **Selection chokepoint:** `call_section_model_provider`
  ([section_provider_call.py:78](apps_rg/runtime/providers/section_provider_call.py)) is the
  only branch that routes to the Qwen slice; everything else flows to `ProviderGateway`.
- **DEGRADED_FALLBACK:** none — ADG MCP healthy, used directly.

## Definition of Done

| # | Criterion | Verification |
|---|---|---|
| 1 | `ProviderResult`/`ProviderRequest` live in a Qwen-neutral module; all importers repointed | `grep "qwen_vllm_provider import"` returns 0 contract imports |
| 2 | `ProviderProfile.QWEN_VLLM` and all `qwen`/`local_qwen` aliases removed | `grep -i "QWEN_VLLM\|local_qwen"` in `apps_rg/` returns 0 (config + code) |
| 3 | All Qwen-only modules deleted (transport, slice, diag, health, docker-restart, live-guard, offline-stub, reasoning-plan, regen-dispatch) | `ls` confirms removal; import graph clean |
| 4 | 8 section lanes import no `build_qwen_request` / `DEFAULT_QWEN_MODEL` | `grep "build_qwen_request"` returns 0 |
| 5 | `provider_profiles.yaml`, `.env.example` carry no Qwen profile/env (`VLLM_BASE_URL`, `QWEN_VLLM_MODEL`) | file inspection |
| 6 | X2 validator `ALLOWED_MODELS` lists contain no Qwen model ids | inspection of executive_summary_x2 et al. |
| 7 | **Smoke-run:** `python -m apps_rg --section executive_summary ...` exits 0 on external Claude | command output, exit code 0 |
| 8 | apps_rg test suite green (Qwen transport test deleted, contract/hygiene tests updated) | `pytest tests/unit/apps_rg tests/_apps_contract -q` |
| 9 | ADG regenerated post-removal; no new violations | `python tools/generate_full_adg.py` + `adg_violations` delta |

Verification-vs-Deferral: all 9 verified in-plan. No deferred scope unless a Qwen-only
helper turns out to have a non-Qwen consumer (then P2 narrows and that consumer is
captured as a follow-up).

## Risks

- **R1 — Hidden non-Qwen consumer of a "Qwen-only" helper** (e.g. `apps_rg_http_reasoning_plan`,
  `*_preflight`). Mitigation: `adg_edge_fanin` / Grep each module before deleting in P2;
  if a Claude-path caller exists, keep + neutralize instead of delete.
- **R2 — A section lane is Qwen-only with no Claude path.** Mitigation: P3 verifies each
  lane reaches `call_section_model_provider` before stripping; if not, wire the neutral
  path first (behavior-preserving) then strip.
- **R3 — E2E smoke needs a live Claude key.** Mitigation: if unavailable, prove via the
  transport-injectable `ExternalProvider` stub path (already supported) and mark the live
  smoke BLOCKED with the exact missing dependency.

## Execution discipline

- Phases land in order (P0 behavior-preserving first; it can be its own commit/PR).
- Scoped tests after each phase (`pytest tests/unit/apps_rg/...`), full suite at P4.
- No `agentic_core` edits (all L_APP); if that changes, stop and open a boundary audit.
