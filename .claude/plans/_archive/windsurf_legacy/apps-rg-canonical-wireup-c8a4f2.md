# apps_rg Canonical Spine Wireup

**Slug:** `apps-rg-canonical-wireup`
**ID:** `c8a4f2`
**Status:** 🟢 Live (Wave 1 complete; Wave 2 in flight)
**Started:** 2026-05-04 06:20 UTC-04
**Owner:** Cascade
**Goal:** Make `apps_rg` a thin app overlay on `agentic_core`, with the canonical spine running U0 → L1 → L0 → L2 static DAG → Exit V6 and L0 prohibited from executing fallback work.
**Author-Gate Decisions Locked:**
- Tier scope: All three tiers (user, 2026-05-04 06:30)
- P3 substrate: Option B — new `integrated_r4_deterministic_pipeline_run.py` (score 0.88, dominance fired vs A 0.62, gap 0.26)
- R5 design: Strict (no managed-workflow fallback for `apps_research`)

---

## Files In Scope

```
apps_rg/__main__.py                                           # entrypoint surgery + helpers
apps_rg/spine_manifest.yaml                                   # route claim R3 → R4
apps_rg/utils/anthropic_rag_entrypoint.py                     # rename-wrap to rg_pa_compiler
apps_rg/prompt_assembly/rg_pa_compiler.py                     # NEW (compat wrapper)
apps_rg/integrations/preloaded_input_context_manifest.py      # NEW (manifest dataclass + builder)
apps_rg/integrations/rg_identity_resolver.py                  # NEW (CLI-local identity)
apps_rg/integrations/rg_r5_policy.py                          # NEW (decision-only fallback)
apps_rg/config/apps_rg_static_dag.yaml                        # NEW (L2 static recipe)
apps_rg/config/intake_policy.yaml                             # NEW (U0 policy)
apps_rg/config/jd_schema.json                                 # NEW (E4 schema)
apps_rg/config/jd_plan_rules.yaml                             # NEW (L1 rules)
apps_rg/config/l0_policy.yaml                                 # NEW (L0 policy)
agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py  # NEW (~300 LoC)
tests/governance/test_apps_rg_*.py                            # 19 new + 1 XFAIL flip
# --- RuntimeAuthorGate (W7 — proposal only, implementation deferred) ---
apps_rg/hitl/runtime_author_gate.py                           # NEW — freeze/emit X3B/collect decision
apps_rg/hitl/cli_hitl_adapter.py                              # NEW — CLI prompt adapter (single input() chokepoint)
apps_rg/hitl/hitl_schemas.py                                  # NEW — RuntimeAuthorGateDecisionRequest + HumanReviewDecision
apps_rg/hitl/hitl_replay_store.py                             # NEW — hash-bound durable replay log
apps_rg/config/hitl_trigger_policy.yaml                       # NEW — 6 trigger conditions declarative
tests/governance/test_apps_rg_hitl_*.py                       # NEW — HITL sentinel tests
```

**Out of scope** (will NOT touch):
- 9 `*Agent.py` files in `apps_rg/reasoning/` (constitutional §3 protection)
- `apps_research/` (sibling app; cross-app refactor is separate)
- `apps_shared/spine_emission/adapter.py` (P3 chose Option B, not Option A or C)
- L3 orchestration code (apps_rg bypasses L3 for the normal R4 path)

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | P1, P2 | Tier 1 BLOCKER fixes — L0 subprocess removal + R5-through-Exit | ~12k | Existing `governed_run` accepts the late-bound run_dir from `_emit_r5_terminal_via_exit` | ✅ DONE | Zero `subprocess.run([..., "apps_research"])` in `__main__.main()`; all R5 paths call `_maybe_run_exit_hook` before return; `python -c ast.parse` passes |
| **W2** | P3 | Tier 1 final — new R4 entrypoint module + flip | ~25k | `intake.pipeline.run()`, `bridges.u0_to_l1_plan`, `L0_routing.composition_root`, `static_dag_registry`, and Exit V6 are real (not stubs); each composes cleanly; `_emit_r5_terminal_via_exit` calls canonical Exit V6 (no fake ExitReviewPacket) | 🟢 IN PROGRESS | All 5 W2 sentinel tests pass (see Verification Plan §W2); valid JD+brief→R4→L2→X3; valid JD+missing brief→R5→X3→exit 1; invalid JD→U0 schema rejection (not R5); governance XFAIL flips → strict pass |
| **W3** | P4, P5, P6, P7, P8 | Tier 2 HIGH fixes — manifest hygiene + PA rename + late-stage subprocess removal | ~30k | `narrative_pass.py` + DOCX export are convertible to in-process callables; `_run_post_pipeline` subprocess steps are movable into L2 recipe | 🟡 PENDING — **BLOCKED until W2 sentinel gate passes** | `input()` prompts removed; `spine_manifest.yaml` claims `R4_SINGLE_ACTION`; `rg_pa_compiler.py` re-exports cleanly; `PreloadedInputContextManifest` (hashes + lineage + policy_hash + blueprint_hash + replay_key + manifest_hash + audit refs) artifact written to run_dir; no `subprocess.run` in `_run_post_pipeline` outside governed L2 DAG steps |
| **W4** | P9, P10, P11, P12, P13 | Tier 3 MEDIUM fixes — declarative config + adapters + 00C/L5 terminology | ~25k | Config-driven dispatch is acceptable to upstream consumers (none break on YAML addition) | 🟡 PENDING | All 5 config YAMLs/JSONs validate against schemas; rg_identity_resolver + rg_r5_policy decision-only (no subprocess); 00C/L5 wording corrected across `spine_manifest.yaml` + code comments |
| **W5** | T-suite | 19 new regression tests across 6 categories | ~20k | Test fixtures for governed_run + Exit V6 + UWG mock are already present in `tests/governance/conftest.py` | 🟡 PENDING | All 19 new tests pass; existing governance suite stays green; coverage delta ≥ 0 |
| **W6** | V1 | Final verification + Notion writeback batch | ~10k | Notion APIs reachable; rate limit headroom for 5+ remote-MCP calls | 🟡 PENDING | Notion Plans row registered; Backlog rows posted; ADR for R3→R4 route claim correction; SR_SUMMARY emitted |
| **W7** | P-HITL1 … P-HITL6 | RuntimeAuthorGate — HITL freeze/review/re-clearance anchored in Exit X3B | ~40k | Exit X3B freeze path is reachable; `HITLApprovalGate` is wirable from app layer; L5 re-clearance receipt type exists or can be added | 🟡 PENDING — **proposal stage; implementation after W6 green** | All 4 HITL sentinel test suites pass; no `input()` outside `cli_hitl_adapter`; every HITL path emits X3B then exactly one final X3; human decisions hash-bound + replayable; no direct L4 write from HITL |

**Total est tokens:** ~162k. **Hard ceiling:** none (1M context window post-Opus 4.7).

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1** | Delete L0 subprocess | `apps_rg/__main__.py:470-495` | `subprocess.run([..., "-m", "apps_research", ...])` was placed in L0 — fallback execution where decision-only is required | 4k | ✅ DONE |
| **P2** | Route R5 through Exit V6 | `apps_rg/__main__.py:_emit_r5_terminal_via_exit` (new) + 3 R5 branches | All `sys.exit(1)` and `gr.set_subprocess_exit_code(1); return` paths bypassed Exit | 8k | ✅ DONE |
| **P3** | New R4 entrypoint module | `agentic_core/runtime/entrypoints/integrated_r4_deterministic_pipeline_run.py` (NEW, ~300 LoC); `apps_rg/__main__.py` flip | No existing entrypoint takes `(app_name, argv)` and runs U0→L1→L0→L2-static→Exit; `integrated_single_action_run.py` is a Fort Knox cert fixture not a dispatcher | 25k | 🟢 IN PROGRESS |
| **P4** | Replace `input()` with argparse `--jd required=True` | `apps_rg/__main__.py:443-451` | Interactive prompts bypass canonical U0 E1 transport validation + E4 schema validation | 4k | 🟡 PENDING |
| **P5** | Fix spine_manifest route claim | `apps_rg/spine_manifest.yaml:28-29` | Manifest claims `R3_grounded_read` but apps_rg performs no corpus retrieval — should be `R4_SINGLE_ACTION` with preloaded-context | 3k | 🟡 PENDING |
| **P6** | Rename-wrap PA compiler | `apps_rg/prompt_assembly/rg_pa_compiler.py` (NEW); `apps_rg/utils/anthropic_rag_entrypoint.py` (compat alias) | Functionally clean today (no retrieval, no provider call); only the name is misleading | 4k | 🟡 PENDING |
| **P7** | PreloadedInputContextManifest | `apps_rg/integrations/preloaded_input_context_manifest.py` (NEW, ~150 LoC) | apps_rg bypasses C0 corpus retrieval; since C0 is bypassed this manifest IS the deterministic context contract for JD, company brief, and master resume — must include hashes, origin labels, freshness, lineage, policy_hash, blueprint_hash, replay_key, manifest_hash, and audit refs; pulled earlier (consumed by P3 entrypoint, not deferred to W3) | 12k | 🟡 PENDING — **Pull earlier: P3 depends on this** |
| **P8** | Late-stage subprocess removal | `apps_rg/__main__.py:_run_post_pipeline` (~80 LoC rewrite) | narrative_pass + DOCX export run as `subprocess.run` — if they contribute to the final artifact they MUST be moved into the L2 static recipe as steps OR declared as explicit `kind: external_process` steps with sandbox/gate/trace evidence; final artifact generation MUST NOT remain outside governed execution | 10k | 🟡 PENDING |
| **P9** | Static DAG YAML | `apps_rg/config/apps_rg_static_dag.yaml` (NEW) | Static recipe is currently coded imperatively; declarative form needed; HOP IDs renamed (`hop_0_intake` → `hop_0_load_validated_inputs`, etc.) | 6k | 🟡 PENDING |
| **P10** | 00C / L5 terminology fix | `apps_rg/spine_manifest.yaml`, `apps_rg/__main__.py` (comments), `apps_rg/integrations/hitl_bridge.py` (import path `agentic_core.L5_safety.runtime_gates.types` is the wording lever) | Code conflates "L5 safety runtime gates" with 00C live GateVerdict authority — distinct concepts | 5k | 🟡 PENDING |
| **P11** | Declarative config files (4) | `apps_rg/config/intake_policy.yaml`, `jd_schema.json`, `jd_plan_rules.yaml`, `l0_policy.yaml` (all NEW) | apps_rg-specific U0/L1/L0 policy is currently inline in `__main__.py` — must externalize for the new entrypoint to consume declaratively | 7k | 🟡 PENDING |
| **P12** | rg_identity_resolver adapter | `apps_rg/integrations/rg_identity_resolver.py` (NEW) | CLI-local identity resolver pluggable into U0; canonical surface for apps_rg-specific tenant/user mapping | 4k | 🟡 PENDING |
| **P13** | rg_r5_policy adapter | `apps_rg/integrations/rg_r5_policy.py` (NEW) | Decision-only R5 policy plug; surfaces missing-prerequisite + reentry-target + fallback-target as data, never executes | 4k | 🟡 PENDING |
| **T-suite** | 19 regression tests | `tests/governance/test_apps_rg_*.py` (mostly NEW) | Test categories: L0/R5 (5), Static L2 recipe (5), C0-bypass + manifest (6), Exit + L6 (4), L4 + UWG (3), Provider gateway (3) | 20k | 🟡 PENDING |
| **V1** | Final verification | governance suite + Notion writeback | Constitutional §25 (Notion remote-MCP serial); §36 (plan registration); ADR for R3→R4 route claim | 10k | 🟡 PENDING |
| **P-HITL1** | RuntimeAuthorGate schemas | `apps_rg/hitl/hitl_schemas.py` (NEW) | Define `RuntimeAuthorGateDecisionRequest`, `HumanReviewDecision`; map `HITLReviewPacket` to existing `X3BFreezePacket`; L5 re-clearance receipt shape | 8k | 🟡 PENDING (W7) |
| **P-HITL2** | CLI HITL adapter | `apps_rg/hitl/cli_hitl_adapter.py` (NEW) | Single `input()` chokepoint; renders recommendations + confidence + evidence + bounded options; returns `HumanReviewDecision`; no other layer may call `input()` | 6k | 🟡 PENDING (W7) |
| **P-HITL3** | RuntimeAuthorGate core | `apps_rg/hitl/runtime_author_gate.py` (NEW) | Receives trigger from 00C/L2; emits X3B freeze packet; invokes CLI adapter; persists hash-bound decision; calls L5 re-clearance; hands off to canonical Exit | 12k | 🟡 PENDING (W7) |
| **P-HITL4** | HITL replay store | `apps_rg/hitl/hitl_replay_store.py` (NEW) | Append-only JSONL; each row contains `decision_hash`, `input_manifest_hash`, `replay_key`, `timestamp`, `chosen_option`; verifiable offline | 5k | 🟡 PENDING (W7) |
| **P-HITL5** | Trigger policy YAML | `apps_rg/config/hitl_trigger_policy.yaml` (NEW) | Declarative 6-trigger conditions (missing brief, stale brief, unsupported claim, low confidence, final release approval, cache promotion approval); consumed by P-HITL3 core | 4k | 🟡 PENDING (W7) |
| **P-HITL6** | UWG post-decision write path | `apps_rg/hitl/runtime_author_gate.py` (write path) | Any durable write or cache promotion after human decision MUST go through Exit → UWG → L4; HITL core never writes L4 directly | 5k | 🟡 PENDING (W7) |

---

## ADG Hotspot Report

> Per constitutional §22, T2/T3 plans must include this section. Hotspots informing wave ordering:

| Node | Layer | Fan-in | Fan-out | Archetype | Surface(s) | Multiplier | Impact |
|------|-------|--------|---------|-----------|------------|------------|--------|
| `apps_rg.__main__.main` | App-overlay | 6 (CI tests + governance suite) | high (all helpers) | ORCHESTRATOR | Execution + Write | 1.0 (app layer) | HIGH — single chokepoint for L0/R5 violations |
| `apps_rg.cache.chunk_commit.commit_chunks_via_exit` | App-overlay | 1 (`__main__._chunk_and_commit_output`) | uses `agentic_core.L4_state.durable_write_gateway` | STATE_NODE | Write + State | 1.75 (L4-adjacent) | MEDIUM — already correct, audit-confirm only |
| `agentic_core.runtime.entrypoints.integrated_single_action_run` | L0/L2 boundary | (cert fixtures only) | calls `integrated_safe_reuse_run` | (not a hotspot — fixture) | n/a | n/a — DON'T reuse for apps_rg |
| `apps_shared.spine_emission.adapter.SpineRuntimeAdapter` | App-shared | 5 (apps_exec, apps_lic, apps_rg, apps_research, apps_rfp) | stub returns | CENTRAL_DEPENDENCY | Execution | 1.0 | HIGH — but Option A/C explicitly ruled out (blast radius); P3 builds parallel module instead |

**Wave-ordering rationale:** W1 fixes the highest-impact catch site (`apps_rg.__main__.main` — the L0 subprocess + R5 paths). W2 adds the missing canonical surface without touching the 5-app shared adapter. W3+ are non-hotspot hygiene fixes.

---

## ADG Graph Layer Evidence

> Per constitutional §22, T2/T3 plans must reference ≥3 MVs + semantic edges + P-views.

| Primitive | Use |
|-----------|-----|
| `mv_hotspot_centrality` | Confirms `apps_rg.__main__.main` and `SpineRuntimeAdapter` are top-tier centrality nodes; informs ordering W1 → W2 |
| `mv_graph_chokepoint_bridges` | Identifies `governed_run` as the chokepoint between apps_rg and the spine; P3 must preserve its semantics or replace cleanly |
| `mv_graph_reverse_dependency_hotspots` | `apps_research` reverse-deps from `apps_rg/__main__.py` confirms BLOCKER 1 surface (delete = break the bad coupling) |
| `flows_to` (semantic edge) | `apps_rg/__main__.py.main` flows_to `_chunk_and_commit_output` flows_to `commit_chunks_via_exit` flows_to `DurableWriteGateway` — chain is correct, P3 must preserve it |
| `emits_side_effect` (semantic edge) | Pre-W1: `__main__.main` emits side-effect `subprocess_spawn_apps_research` — REMOVED. Post-W1: `__main__.main` emits side-effect `exit_v6_x3_disposition` only |
| `v_p1_layer_break_app_to_app` | P-view confirmed apps_rg → apps_research direct subprocess edge (BLOCKER 1) — now resolved |
| `v_p2_silent_swallow` | 4 guardian-exempted broad-except sites in `__main__.py` (lines 506, 656, 711, 727); inherited from prior cert path; not adding new ones in this plan |

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| `integrated_single_action_run.py` is misleading name (it's a Fort Knox cert fixture, not the R4 dispatcher) | LOW | Out of scope for this plan; document in Tier 3 ADR |
| Other 4 apps still ride SpineRuntimeAdapter stubs | DEFERRED | Separate cross-app refactor required; capture as DEFERRED_SCOPE |
| `_run_post_pipeline` narrative + DOCX as subprocess (F4 HIGH) | HIGH | P8 — convert to in-process; OR explicitly mark `kind: external_process` in static DAG |
| L3 managed-workflow alternative for missing-brief auto-research | DEFERRED | User chose strict R5 design; alternative captured as DEFERRED_SCOPE |
| `--research-via apps_research` CLI flag still present | LOW | P11 deprecates it via declarative L0 policy; legacy flag remains for one release cycle |
| No HITL freeze/review mechanism for apps_rg decision points | HIGH — design proposed | W7 RuntimeAuthorGate addresses this; implementation deferred until W6 green |

---

## Deferred Scope

DEFERRED_SCOPE: apps_research managed-workflow dispatcher (L0 → L3 → 2-step L2) — out of scope; only relevant if repo later declares the managed workflow route family
DEFERRED_SCOPE: Other 4 apps (apps_exec, apps_lic, apps_rfp, apps_research) still ride SpineRuntimeAdapter stubs — cross-app canonical wireup is a separate plan
DEFERRED_SCOPE: C0 retrieval wiring for apps_rg — not needed because apps_rg uses preloaded deterministic inputs
DEFERRED_SCOPE: L3 static_dag_registry binding upgrade — requires P9 static_dag YAML first (this plan creates the YAML; binding upgrade is follow-on)
DEFERRED_SCOPE: integrated_single_action_run.py rename — misleading but out of scope for this plan (Tier 3 ADR will note)
DEFERRED_SCOPE: RuntimeAuthorGate W7 implementation — proposal complete; implementation gated on W6 green + separate Author-Gate decision on CLI adapter vs TUI adapter surface
DEFERRED_SCOPE: L6 learning loop consumption of human decisions — only valid after Exit finalizes run; scoped to W7 P-HITL3/6 and must not shortcut the Exit gate

---

## Author-Gate Queue Seed

AG_QUEUE_SEED: plan=apps-rg-canonical-wireup-c8a4f2 id=ag-rg-p3-substrate depends_on= title=P3 substrate choice (already answered: Option B) status=answered
AG_QUEUE_SEED: plan=apps-rg-canonical-wireup-c8a4f2 id=ag-rg-p8-subprocess-strategy depends_on=ag-rg-p3-substrate title=P8 — convert narrative_pass+DOCX in-process OR declare external_process in static DAG
AG_QUEUE_SEED: plan=apps-rg-canonical-wireup-c8a4f2 id=ag-rg-p10-l5-rename-strategy depends_on=ag-rg-p3-substrate title=P10 — rename `agentic_core.L5_safety.runtime_gates` import or only update apps_rg-side wording
AG_QUEUE_SEED: plan=apps-rg-canonical-wireup-c8a4f2 id=ag-rg-hitl-adapter-surface depends_on=ag-rg-p3-substrate title=W7 HITL adapter surface — CLI prompt adapter vs TUI adapter vs async webhook

---

## Verification Plan (per Wave)

### W1 (DONE)
- ✅ `python -c "import ast; ast.parse(open('apps_rg/__main__.py').read())"` → SYNTAX OK
- ✅ Grep confirms zero `subprocess.run([..., "apps_research", ...])` in `main()`
- ✅ All 3 R5 branches call `_emit_r5_terminal_via_exit` before return

### W2 (in progress) — Sentinel Gate (ALL must pass before W3 begins)

**5 sentinel tests (hard gate — no W3 without green):**
- `tests/governance/test_apps_rg_adg.py::test_apps_rg_l0_does_not_execute_apps_research`
- `tests/governance/test_apps_rg_adg.py::test_apps_rg_r5_fatal_goes_to_exit_before_process_exit`
- `tests/governance/test_apps_rg_adg.py::test_apps_rg_l0_emits_exactly_one_route_contract`
- `tests/governance/test_apps_rg_adg.py::test_apps_rg_r4_entrypoint_calls_canonical_u0_l1_l0_l2_exit`
- `tests/governance/test_apps_rg_adg.py::test_apps_rg_valid_jd_missing_brief_emits_r5_terminal_packet`

**3 scenario proofs (all three required):**
1. valid JD + valid brief → `R4_SINGLE_ACTION` → L2 static recipe → Exit X3
2. valid JD + missing brief → R5 terminal packet → Exit X3 → exit 1 after receipt
3. invalid JD → U0 schema rejection (exit 2), NOT R5 terminal

**Smoke test fix (constraint):**
- Empty/invalid JD fixture MUST test U0 schema rejection — NOT R5 missing brief
- Add a SEPARATE `valid_jd_missing_brief` fixture to test R5 path
- Do NOT conflate the two failure modes in a single test

**`_emit_r5_terminal_via_exit` constraints (hard rules):**
- MUST call canonical Exit V6 (`ExitEvalPipeline.run` or equivalent public API)
- MUST NOT compute X3 itself
- MUST NOT fake/construct an `ExitReviewPacket` inline
- MUST NOT write receipts directly to disk
- MUST NOT write L4 state directly

**`integrated_r4_deterministic_pipeline_run.py` composition constraint:**
- MUST be a thin wrapper over existing canonical spine components
- MUST NOT reimplement U0, L1, L0, L2, Exit, 00C, L5, UWG, or L6 behavior
- Import and compose; do not rewrite

**Additional checks:**
- New module imports cleanly: `python -c "from agentic_core.runtime.entrypoints.integrated_r4_deterministic_pipeline_run import run"`
- pytest: `tests/governance/test_apps_rg_must_invoke_governed_app_runner.py` flips XFAIL → strict pass
- pytest: full `tests/governance/test_apps_rg_*.py` suite stays green

### W3, W4, W5, W6
- See per-phase definitions above; each landing emits its own SR_SUMMARY checkpoint

### W7 (HITL — pending W6 green) — Sentinel Gate

**4 HITL sentinel test suites (all required before W7 closes):**
- `tests/governance/test_apps_rg_hitl_no_adhoc_input.py` — asserts no `input()` outside `cli_hitl_adapter.py`
- `tests/governance/test_apps_rg_hitl_x3b_disposition.py` — every HITL path emits Exit X3B and exactly one final X3 disposition
- `tests/governance/test_apps_rg_hitl_replay.py` — human decisions are replayable and hash-bound (`decision_hash` + `input_manifest_hash` round-trip)
- `tests/governance/test_apps_rg_hitl_no_l4_write.py` — no direct L4 write from HITL layer; all durable writes go through Exit → UWG → L4

**6 trigger scenarios (all must have coverage):**
1. Missing company brief → HITL freeze → human provides path → re-clearance → Exit X3
2. Stale company brief → HITL freeze → human approves/rejects → Exit X3
3. Unsupported resume claim → HITL freeze → human edits/overrides → L5 re-clearance → Exit X3
4. Low confidence final artifact → HITL freeze → human approves/rejects release → Exit X3
5. Final release approval → HITL freeze → human approves → Exit X3 → cache promotion via UWG
6. Cache promotion approval → HITL freeze → human approves → Exit X3 → L4 write via UWG only

---

---

## RuntimeAuthorGate Design Proposal (W7)

> **Status:** Architecture proposal only. No code changes. Implementation deferred until W6 green.
> **Goal:** Allow runtime HITL in apps_rg similar to Cascade AuthorGate — pause the run, show recommendations + confidence + evidence + bounded options, collect Amit's decision, persist as replayable evidence, re-clear through L5, resume only through canonical Exit.

### Hard Constraints (from user — non-negotiable)

1. **No ad hoc `input()`** inside U0, L1, L0, PA, L2, or any apps_rg helper. Single `input()` chokepoint lives only in `cli_hitl_adapter.py`.
2. **X3B anchor** — `RuntimeAuthorGate` is anchored in Exit X3B HITL freeze/review/re-clearance. It does not invent a new disposition type.
3. **00C / L2 recommend; they do not prompt** — 00C Runtime Gates and L2 may request HITL by emitting a structured trigger request. They MUST NOT call `input()` or resume the run.
4. **L5 re-clearance treats human input as `human_review` data, not sovereign authority** — the re-clearance receipt is a `GateVerdict` with `source=human_review`; it does not bypass L5 policy.
5. **HITL MUST NOT write L4 directly** — all durable writes and cache promotions after a human decision go through `Exit → UWG → L4`.
6. **L6 consumption is post-Exit only** — L6 may consume the human decision only after Exit finalizes the run, for future-run learning.

### Data Flow (happy path with HITL)

```
U0 intake → L1 plan → L0 decision → L2 DAG step
   ↓ (trigger: low confidence / missing brief / approval required)
00C / L2 emits RuntimeAuthorGateDecisionRequest
   ↓
RuntimeAuthorGate.freeze()
   → emits X3B freeze packet into Exit pipeline
   → calls cli_hitl_adapter.prompt(request) → HumanReviewDecision
   → persists HumanReviewDecision to hitl_replay_store (hash-bound)
   → calls L5.re_clear(human_review_decision) → L5ReClearanceReceipt
   ↓
Exit V6 receives X3B + L5ReClearanceReceipt
   → produces final X3 disposition (allow or deny)
   → if allow + cache_promotion: commits via UWG → L4
   → L6 records human_decision for future learning
```

### Schema Designs

#### `RuntimeAuthorGateDecisionRequest`
```python
@dataclass
class RuntimeAuthorGateDecisionRequest:
    request_id: str                     # uuid
    trigger_kind: str                   # MISSING_BRIEF | STALE_BRIEF | UNSUPPORTED_CLAIM
                                        # | LOW_CONFIDENCE | RELEASE_APPROVAL | CACHE_PROMOTION
    run_id: str                         # links to governed_run context
    input_manifest_hash: str            # sha256 of PreloadedInputContextManifest
    recommendations: list[str]          # ordered list of recommendations to show
    confidence_score: float             # 0.0–1.0
    evidence_refs: list[str]            # artifact paths / citation keys
    bounded_options: list[BoundedOption] # exactly the set of valid choices
    replay_key: str                     # deterministic from run_id + trigger_kind

@dataclass
class BoundedOption:
    option_id: str
    label: str
    consequence: str                    # what happens if chosen
    is_recommended: bool
```

#### `HumanReviewDecision`
```python
@dataclass
class HumanReviewDecision:
    decision_id: str                    # uuid
    request_id: str                     # links to RuntimeAuthorGateDecisionRequest
    chosen_option_id: str
    decision_timestamp: str             # ISO-8601 UTC
    input_manifest_hash: str            # must match request.input_manifest_hash
    decision_hash: str                  # sha256(decision_id + chosen_option_id + input_manifest_hash)
    replay_key: str                     # must match request.replay_key
    operator_id: str                    # e.g. "amit" — not sovereign, just attribution
```

#### `HITLReviewPacket` → Exit X3B mapping
```
HITLReviewPacket.freeze_reason        → ExitX3BPacket.freeze_code
HITLReviewPacket.input_manifest_hash  → ExitX3BPacket.context_binding_hash
HITLReviewPacket.decision             → ExitX3BPacket.human_review_payload
HITLReviewPacket.l5_receipt           → ExitX3BPacket.re_clearance_receipt
```
The X3B packet is the ONLY carrier of the human decision into the Exit pipeline. No other channel.

#### `L5ReClearanceReceipt`
```python
@dataclass
class L5ReClearanceReceipt:
    receipt_id: str
    decision_id: str                    # links to HumanReviewDecision
    gate_verdict: GateVerdict           # source=human_review — NOT sovereign
    cleared_at: str                     # ISO-8601 UTC
    policy_hash: str                    # L5 policy in effect at re-clearance time
    binding_hash: str                   # sha256(decision_id + policy_hash)
```

### File List (W7 new files)

| File | Purpose | LoC est. |
|------|---------|----------|
| `apps_rg/hitl/hitl_schemas.py` | All dataclasses above + BoundedOption | ~120 |
| `apps_rg/hitl/cli_hitl_adapter.py` | Single `input()` chokepoint; renders decision request; returns `HumanReviewDecision` | ~80 |
| `apps_rg/hitl/runtime_author_gate.py` | Gate core: freeze → prompt → persist → L5 re-clear → hand to Exit | ~200 |
| `apps_rg/hitl/hitl_replay_store.py` | Append-only JSONL replay log with hash verification | ~60 |
| `apps_rg/config/hitl_trigger_policy.yaml` | Declarative 6-trigger policy; thresholds for LOW_CONFIDENCE etc. | ~50 lines YAML |
| `apps_rg/hitl/__init__.py` | Package marker | 1 |

**Total W7 new files:** 6 (5 Python + 1 YAML)

### Test List (W7 required)

| Test file | What it proves |
|-----------|---------------|
| `tests/governance/test_apps_rg_hitl_no_adhoc_input.py` | AST scan: no `input()` outside `cli_hitl_adapter.py` in all `apps_rg/` modules |
| `tests/governance/test_apps_rg_hitl_x3b_disposition.py` | Every HITL trigger path emits X3B freeze packet; only one final X3 disposition per run; X3B precedes X3 |
| `tests/governance/test_apps_rg_hitl_replay.py` | `decision_hash = sha256(decision_id + chosen_option_id + input_manifest_hash)` round-trip; `replay_key` matches request |
| `tests/governance/test_apps_rg_hitl_no_l4_write.py` | Mock UWG: asserts no direct L4 write from `runtime_author_gate.py`; all durable writes arrive via `UWG.commit()` |
| `tests/governance/test_apps_rg_hitl_l5_source.py` | L5 re-clearance receipt has `gate_verdict.source == 'human_review'` (not sovereign); policy_hash matches active L5 policy |
| `tests/governance/test_apps_rg_hitl_l6_post_exit_only.py` | L6 `record_human_decision()` is only called after Exit X3 finalizes; never before |

### Risk Analysis

| Risk | Severity | Mitigation |
|------|----------|------------|
| X3B freeze packet type may not exist in current Exit V6 implementation | HIGH | Audit `agentic_core/L3_orchestration/exit_eval/v6/types.py` before W7 starts; if absent, add type — do not fake it |
| L5 `re_clear()` API may not accept `human_review` source type | HIGH | Audit `agentic_core/L5_safety/runtime_gates/` before coding; extend carefully under Author-Gate |
| Human decision replay diverges from original run if context mutated | MEDIUM | `input_manifest_hash` in both request + decision provides the binding; replay verifier checks hash equality |
| `cli_hitl_adapter.py` `input()` could be called from test harness unexpectedly (interactive hang) | MEDIUM | Adapter checks `sys.stdin.isatty()`; CI mock replaces `input` via monkeypatch fixture in conftest |
| L6 consumption races Exit finalization | MEDIUM | L6 consumer only wired after `gr.__exit__()` returns; governed_run unwind is the synchronization point |
| UWG rejects cache promotion request if `source_surface != Exit` | LOW | `HITLReviewPacket` carries `source_surface=Exit`; UWG check passes; consistent with existing chunk commit path |
| W7 scope creep into `agentic_core` L5/Exit internals | HIGH | Prefer extension over modification; if L5/Exit requires structural change, open a separate plan + ADR |

### Layer Responsibility Matrix

| Layer / Component | Role in HITL | Forbidden action |
|-------------------|-------------|------------------|
| U0, L1 | May detect trigger condition | Call `input()`, emit X3B, write L4 |
| L0 | Decision-only; may emit trigger request | Execute fallback, call `input()`, bypass Exit |
| 00C Runtime Gates | Emit `RuntimeAuthorGateDecisionRequest` | Call `input()`, resume run, write L4 |
| L2 static DAG step | Emit trigger if confidence threshold breached | Call `input()`, write L4 directly |
| `RuntimeAuthorGate` (new) | Freeze, prompt (via adapter), persist, re-clear, hand to Exit | Write L4, compute X3, produce X3B unaided |
| `cli_hitl_adapter` (new) | ONLY `input()` chokepoint; render + collect | Write any state, call Exit, write L4 |
| Exit V6 | Receive X3B + L5 receipt; produce final X3 | Skip X3B re-clearance if HITL was triggered |
| L5 | Re-clearance with `source=human_review` | Treat human input as sovereign authority |
| UWG / L4 | Accept commit from Exit after X3 | Accept direct write from HITL layer |
| L6 | Record decision for future-run learning | Consume before Exit finalizes |

---

## Rollback Plan

```bash
# Per-wave atomic rollback
git diff --stat HEAD~1                     # see what changed
git restore <file>                          # revert single file
git reset --hard HEAD~<N>                   # revert N commits (full wave)

# Plan-level rollback (full revert)
rm .windsurf/plans/apps-rg-canonical-wireup-c8a4f2.md
rm .windsurf/state/apps-rg-wireup-progress.txt
git restore apps_rg/__main__.py
# (other files only if W2+ landed)
```

---

## Notion Registration

Per constitutional §36, this plan must be registered in the Notion Plans DB before W2 starts. Registration deferred to W6 batch per `notion-plan-wave-deferral.md` (we are between W1 and W2; not mid-wave). However, the user requested visibility — explicit Notion-registration now is permitted via NOTION_WAVE_DEFERRAL_BYPASS=1 if needed.

PLAN_CREATED: slug=apps-rg-canonical-wireup id=c8a4f2 file=.windsurf/plans/apps-rg-canonical-wireup-c8a4f2.md status=Live exists_on_disk=true

---

## SR_SUMMARY (rolling)

**W1 outcome:**
- 2 BLOCKERS resolved: L0 subprocess deleted; R5 paths route through Exit V6
- 1 file changed: `apps_rg/__main__.py` (3 surgical edits)
- 1 helper added: `_emit_r5_terminal_via_exit(gr, reason_code, exit_code)`
- 0 tests run (deferred to W6 — XFAIL flip needs P3 done first)
- DECISION_CAPTURED: tier-scope=all-three-tiers, p3-substrate=B
- Lessons: `integrated_single_action_run.py` is NOT a generic dispatcher — verify before claiming reuse
