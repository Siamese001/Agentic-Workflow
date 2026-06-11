---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\l0-routing-v15-only-cutover-c9e2f1.md'
original_relative_path: '_archive\\2026-05\\l0-routing-v15-only-cutover-c9e2f1.md'
source_sha256: 609f25973e1e96901c80fd20d87810a8fccb57a0208bf25127919966e9172b43
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: l0-routing-v15-only-cutover-c9e2f1
plan_type: platform_core_change
touches_agentic_core: true
touches_governance_ci: true
touches_cursor_rules: false
touches_plan_templates: false
core_addition_author_gate_required: true
author_gate_receipt_ref: ""
dod_exempt: false
---

# L0 Routing — v15-Only Cutover

Retire v12 route-id surface (`R-HITL`, `R-PAR`, `R-LOOP`, …) so **all runtime L0 routing** emits and consumes **v15 `V15RouteContract` only** (six canonical routes + aspects: `TIER_HITL`, `hitl_pause_points`, `HITL_REQUIRED`).

> **plan_id discipline**: `plan=l0-routing-v15-only-cutover-c9e2f1`

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: COMPLETE
CURRENT_WAVE: W4
LAST_COMPLETED_WAVE: W4
LAST_UPDATED: 2026-05-24
NOTION_STATUS: Completed
PLAN_COMPLETED: 2026-05-24
CLOSEOUT_RECEIPT: docs/reports/agentic_core/l0_v15_only_cutover_w4_receipt_20260525.md
DEFERRED_SCOPE: none — all waves W1–W4 complete; no further waves in plan
PROOF_ARTIFACT: artifacts/governance/l0_v12_fanin_inventory.json; artifacts/governance/l0_v15_e2e_proof_bundle_20260525/bundle.json; artifacts/governance/l0_v15_route_coverage_proof_20260525/bundle.json
PROOF_GATE: ops_scripts/ci/check_l0_v15_no_v12_hotpath.py; ops_scripts/ci/check_l0_parent_invariants.py; ops_scripts/ci/check_replay_proof.py
NOTION_PAGE_ID: 36727693-f55c-81e9-b053-ef58e79f02fb
NOTION_RECONCILED: 2026-05-24
TRIPLECHECK: closed — v15-only cutover W1–W4 complete; v12 hot path archived
WAITING_FOR:
PLAN_CREATED: slug=l0-routing-v15-only-cutover-c9e2f1 path=.cursor/plans/l0-routing-v15-only-cutover-c9e2f1.md status=Waiting

---

## ADG generation baseline (2026-05-21)

Pre-cutover structural snapshot — **pin W1.1 inventory queries to this generation** (replaces prior canonical `05202026_1131`).

| Field | Value |
|-------|-------|
| **Snapshot ID** | `05212026_0548` |
| **Indexed SQLite** | [adg_indexed_05212026_0548.sqlite](artifacts/adg/adg_indexed_05212026_0548.sqlite) (~683 MB) |
| **Graph projection** | [adg_graph_05212026_0548.sqlite](artifacts/adg/adg_graph_05212026_0548.sqlite) |
| **in-toto envelope** | [adg_indexed_05212026_0548.sqlite.intoto.jsonl](artifacts/adg/adg_indexed_05212026_0548.sqlite.intoto.jsonl) |
| **Generation** | `python -m tools.generate.generate_full_adg --force` (`ADG_SKIP_GIT=1`) |
| **Exit / wall time** | **0** / ~905s |
| **P0 two-pass runner** | PASSED (Phase B: full P0 clean) |
| **P2 ratchet** | **1/1** stable (`+0`; ceiling auto-ratcheted from 158 → 1 after guardian burndown) |
| **Guardian exemptions** | 1830 violations filtered |
| **Post-ADG gates** | wiring, config-ref, lifecycle, except-contract, test-coverage — **all PASS** |
| **ADR-071 authority breaches** | 8 rows — all attributed to exempt [l0_binding.py](apps_lic/runtime/bindings/l0_binding.py) (not L0 routing) |
| **Redis hot cache** | Ingested from `0548` snapshot (MCP `adg_health` → `adg_snapshot_id=05212026_0548`) |

**W1.1 pre-scan (grep; formal JSON still required):**

| Surface | Production import sites (agentic_core) | apps_* imports |
|---------|--------------------------------------|----------------|
| `v12_route_selector` | Self-chain only (via `fallback_chains_loader` + `route_contract_v12_extensions`) | **0** |
| `route_contract_v12_extensions` | `fallback_chains_loader.py`, `cold_start_safeguard.py`, `route_contract_v15_bridge.py` | **0** |
| `route_contract_v15_bridge` / `v12_to_v15` | Bridge module only (hot-path retirement target W3.2) | **0** |
| `fallback_chains_loader` (v12 YAML) | `v12_route_selector.py` | **0** |
| `select_route_v15` | N/A (v15) | `apps_shared/proof/scenario_base.py` (+ tests); **no** `apps_rg` production import |

**Implication:** L0 v12/v15 duality is **platform-contained** — cutover blast radius is `agentic_core/L0_routing/**` + proof harness, not app overlays. W1.1 must still emit [l0_v12_fanin_inventory.json](artifacts/governance/l0_v12_fanin_inventory.json) from snapshot `05212026_0548` (ADG MCP `adg_edge_fanin` / `adg_nodes_by_file` on module nodes).

**Unrelated (same ADG run):** Repo-wide P2 guardian burndown and post-gate baseline regen completed in parallel session — does not change L0 scope but **unblocks** W2+ platform edits under clean `generate_full_adg`.

---

## Context (SCQA)

- **Situation** — v15 types and `v15_route_selector` exist and are wired for proof/spine paths (`apps_shared/proof`, `test_l0_route_selector_wireup`, e2e `RouteId.*` v15 enums). v12 remains parallel: `route_contract_v12_extensions`, `v12_route_selector`, `config/routing/fallback_chains.yaml` (v12 route ids), `fallback_chains_loader` (v12 types), `route_contract_v15_bridge` (lossy translator). Doctrine `03.3` already models HITL as **posture**, not sovereign route.
- **Complication** — Two contract versions confuse operators (“is HITL `R-HITL` or `TIER_HITL`?”), duplicate fallback SSOT (YAML v12 vs hardcoded `_default_fallback_for` in v15), and force every change through bridge semantics. Fort Knox replay digests and REQ gates assume stable route vocabulary.
- **Question** — How do we cut over to v15-only without breaking replay, proof harness, or apps spine emission?
- **Answer** — **Inventory → v15 SSOT for fallbacks/calibration → switch all selectors/loaders → shrink bridge to replay-archive only → delete v12 production surface → prove with targeted pytest + e2e + `run_contract_gates`.**

---

## Status Tables

### Wave Progress

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1 | W1.1–W1.3 | Inventory + v15 fallback/calibration SSOT | ~25K | v15 doctrine doc exists on disk | ✅ DONE | v15 YAML loader passes unit tests; no v12 ids in new SSOT |
| W2 | W2.1–W2.4 | Wire production paths to v15-only | ~40K | W1 SSOT merged | ✅ DONE | `select_route_v15` sole selector; bridge not on hot path |
| W3 | W3.1–W3.3 | Retire v12 surface + test migration | ~35K | W2 green | ✅ DONE | v12 modules in `_archive`; `check_l0_v15_no_v12_hotpath` OK |
| W4 | W4.1–W4.2 | Proof/replay + closeout receipt | ~20K | W3 green | ✅ DONE | e2e harness 67/67; proof bundles on disk; W4 receipt |

### Phase Progress

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | v12 fan-in inventory | ADG snapshot `05212026_0548` + grep manifest | Hidden v12 imports in apps (**pre-scan: 0 apps_***) | ~8K | ✅ DONE |
| W1.2 | v15 `fallback_chains_v15.yaml` + loader | `config/routing/`, `fallback_chains_loader_v15.py` | HITL aspect in chain (managed→R5) | ~10K | ✅ DONE |
| W1.3 | v15 calibration SSOT | `routing_calibration.yaml` v12 section → v15 | Threshold drift | ~7K | ✅ DONE |
| W2.1 | v15 selector uses YAML loader | `v15_route_selector.py` | Replace `_default_fallback_for` hardcode | ~12K | ✅ DONE |
| W2.2 | Cold-start + doctrine on v15 types | `cold_start_safeguard.py`, `doctrine/selector.py` | Doctrine still v12-shaped signals | ~10K | ✅ DONE |
| W2.3 | Classifier shaper vocabulary | `classifier_shaper.py` | `L5_HITL` mapping unchanged | ~6K | ✅ DONE |
| W2.4 | Spine/proof path audit | `apps_shared/spine_emission`, `scripts/proof/` | No silent v12 annex | ~12K | ✅ DONE |
| W3.1 | Deprecate v12 selector + loader | `v12_route_selector.py`, `fallback_chains_loader.py` | Test breakage | ~15K | ✅ DONE |
| W3.2 | Bridge shrink | `route_contract_v15_bridge.py` | Historical replay needs | ~10K | ✅ DONE |
| W3.3 | Delete or archive v12 types | `route_contract_v12_extensions.py` | HMAC/digest stability | ~10K | ✅ DONE |
| W4.1 | REQ + e2e proof | `tier4_cluster_refs`, `tests/e2e/proof/` | `HITL_POSTURE` scenarios | ~12K | ✅ DONE |
| W4.2 | Closeout receipt + Notion | `docs/reports/agentic_core/` | Backlog linkage | ~8K | ✅ DONE |

---

## Out Of Scope

- Cursor **Author-Gate** HITL (developer-loop) — not L0 routing; no change.
- App-specific route profiles (`apps_*` bindings) — only if they import v12 types directly (fix in W1.1 if found).
- Rewriting full L3 managed-workflow engine — routing contract only.
- Notion/archived DB migrations unrelated to L0.

---

## v12 → v15 Route Mapping (SSOT for cutover)

| v12 `route_id` | v15 `route_id` | Aspects / notes |
|----------------|----------------|-----------------|
| `R1A` | `R1A_EXACT_CACHE` | Terminal |
| `R1B` | `R1B_SEMANTIC_CACHE` | Terminal |
| `R3_GROUNDED` | `R3_SIMPLE_GROUNDED_READ` | |
| `R4_ACTION` | `R4_SINGLE_ACTION` | |
| `R3R4_WORKFLOW` | `R3R4_MANAGED_WORKFLOW` | |
| `R5_FALLBACK` | `R5_FALLBACK` | Always chain terminus |
| `R-HITL` | `R3R4_MANAGED_WORKFLOW` | `TIER_HITL`, `HITL_REQUIRED`, `hitl_pause_points` |
| `R-PAR` / `R-LOOP` / `R-CASC` | `R3R4_MANAGED_WORKFLOW` | `MULTI_STEP_REQUIRED` reason |

Implementation reference: [`route_contract_v15_bridge.py`](agentic_core/L0_routing/types/route_contract_v15_bridge.py).

---

## Wave 1 — SSOT and inventory

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Phases**:
- **W1.1** — ADG fan-in on `v12_route_selector`, `route_contract_v12_extensions`, `get_fallback_chain` using snapshot **`05212026_0548`**; emit [l0_v12_fanin_inventory.json](artifacts/governance/l0_v12_fanin_inventory.json) (pre-scan: v12 confined to L0 chain; zero `apps_*` v12 imports) | ~8K | PHASE_STATUS: TODO
- **W1.2** — Add `config/routing/fallback_chains_v15.yaml` (six routes; managed-workflow fallbacks encode HITL as `TIER_HITL` entry, not `R-HITL`); add `fallback_chains_loader_v15.py` using `RouteIdV15` / `FallbackEntryV15` | ~10K | PHASE_STATUS: TODO
- **W1.3** — Move `routing_calibration.yaml` `v12` block → `v15` keys; loader reads v15 thresholds for `v15_route_selector` / cold-start | ~7K | PHASE_STATUS: TODO

**Acceptance**:
- New loader tests: chain depth ≤ 8, R5 last, `TIER_HITL` only on managed-workflow entries
- Inventory JSON lists every production import of v12 symbols (target: zero after W3)

**Commands (W1)**:
```bash
# ADG SSOT for fan-in (MCP adg_health first; snapshot 05212026_0548)
python -m tools.generate.generate_full_adg --force
# W1.1 inventory emit (to be scripted; query modules under agentic_core/L0_routing/)
rg "v12_route_selector|route_contract_v12|v12_to_v15|fallback_chains_loader" agentic_core/ apps_*/ --glob "*.py"
python -m pytest tests/unit/agentic_core/L0_routing/test_v15_route_contract.py -q
python -m pytest tests/agentic_core/L0_routing/config/test_fallback_chains_loader_v15.py -q
```

---

## Wave 2 — Hot path v15-only

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: B

**Authorization**: REQUIRED — `touches_agentic_core=true`; Author-Gate before W2.1 edits (deletion strategy: archive vs delete v12).

**Phases**:
- **W2.1** — `v15_route_selector._default_fallback_for` → `get_fallback_chain_v15()` from YAML | ~12K | PHASE_STATUS: TODO
- **W2.2** — `cold_start_safeguard` + `doctrine/selector.py` consume `RouteIdV15` / `RouteSignalsV15` (or thin adapter at doctrine boundary) | ~10K | PHASE_STATUS: TODO
- **W2.3** — Confirm `classifier_shaper` `HITL_REQUIRED` → `L5_HITL` unchanged; document in plan note | ~6K | PHASE_STATUS: TODO
- **W2.4** — Grep proof: no `v12_to_v15` on runtime dispatch path; `apps_shared/proof` and `run_end_to_end_runtime_proof.py` already v15 — add negative test if missing | ~12K | PHASE_STATUS: TODO

**Acceptance**:
- `select_route_v15` is the only selector invoked from spine/proof entrypoints
- Fallback chains loaded from v15 YAML, not v12 hardcode

**Commands (W2)**:
```bash
python -m pytest tests/runtime/test_l0_route_selector_wireup.py -q
python -m pytest tests/unit/agentic_core/L0_routing/reasoning/test_v15_route_selector.py -q
python -m pytest tests/proof/test_wave_bridges.py -q -k v15
```

---

## Wave 3 — Retire v12 production surface

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Remove `v12_route_selector` from production imports; move to `agentic_core/L0_routing/_archive/v12/` OR delete if tests migrated | ~15K | PHASE_STATUS: TODO
- **W3.2** — Shrink `route_contract_v15_bridge`: keep `v12_to_v15` **only** under `tests/` or `replay/` for historical manifests; remove from runtime | ~10K | PHASE_STATUS: TODO
- **W3.3** — Retire `fallback_chains.yaml` (v12) + `fallback_chains_loader.py`; migrate `test_v12_route_extensions.py` → v15 equivalents or archive | ~10K | PHASE_STATUS: TODO

**Acceptance**:
- `rg 'route_contract_v12|v12_route_selector|R-HITL' agentic_core/` → zero (except `_archive` or bridge test-only)
- `config/routing/fallback_chains.yaml` removed or marked deprecated with CI guard

**Commands (W3)**:
```bash
python -m pytest tests/unit/agentic_core/L0_routing/ -q
python -m pytest tests/agentic_core/L0_routing/ -q
```

---

## Wave 4 — Proof, gates, closeout (final wave)

WAVE_ID: W4
WAVE_STATUS: COMPLETE
WAVE_COMPLETE: YES
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**W4 closeout comment (2026-05-24):** Final wave. Fixed e2e harness `REPO_ROOT` (`parents[3]`) + `PYTHONPATH` so 99.8 CLI entrypoints run; `test_runtime_proof_harness.py` **67/67**; emitted `l0_v15_e2e_proof_bundle_20260525` and `l0_v15_route_coverage_proof_20260525` (all scenarios PASS incl. `RC-HITL`); L0 gates `check_l0_v15_no_v12_hotpath`, `check_l0_parent_invariants`, `check_replay_proof` PASS. Full `run_contract_gates.py` still fails on unrelated plan `plan_type` taxonomy (6 rows) — not L0 scope. Receipt: [l0_v15_only_cutover_w4_receipt_20260525.md](docs/reports/agentic_core/l0_v15_only_cutover_w4_receipt_20260525.md). **No W5** — plan scope ends at W4.

**Phases**:
- **W4.1** — Run e2e proof validators (`HITL_POSTURE`, managed workflow); `REQ-L0-CACHE-FALLBACK-HITL-001` tier4 cluster | ~12K | PHASE_STATUS: DONE
- **W4.2** — Emit closeout receipt; Notion Completed + comment | ~8K | PHASE_STATUS: DONE

**Acceptance**:
- E2E harness + on-disk proof bundles PASS (see receipt)
- L0-scoped CI gates PASS; full-repo `run_contract_gates` PARTIAL (pre-existing graph-layer plan taxonomy)

**Commands (W4)**:
```bash
python -m pytest tests/e2e/suites/test_runtime_proof_harness.py -q
python -m tests.e2e.harnesses.run_agentic_runtime_proof --scenario-set all --emit-proof-bundle artifacts/governance/l0_v15_e2e_proof_bundle_20260525 --strict
python ops_scripts/ci/check_l0_v15_no_v12_hotpath.py
python ops_scripts/ci/check_l0_parent_invariants.py
python ops_scripts/ci/check_replay_proof.py
```

---

## Gap Register

**GAP-1: Replay corpus may contain v12 annex JSON**
- Keep read-only `v12_to_v15` in `tests/replay/` or `agentic_core/L0_routing/_archive/bridge/` until manifests re-emitted or replay window expires.
- Impact: W3.2 — do not delete bridge until replay audit complete.

**GAP-2: v15 fallback chains not yet externalized**
- `_default_fallback_for` in `v15_route_selector.py` duplicates intent of v12 YAML.
- Impact: W1.2 + W2.1 — single SSOT required before v12 YAML deletion.

**GAP-3: `routing_calibration.yaml` still documents v12 §4.2**
- Cold-start threshold may be v12-named in comments/keys.
- Impact: W1.3 — doc + loader alignment.

**GAP-4: Core boundary / Author-Gate**
- `touches_agentic_core=true` — migration receipt required per `agentic-core-glob-lock.mdc` before W2+ execution.

**GAP-5: ADG pipeline gate (resolved 2026-05-21)**
- Prior runs blocked on P2 ratchet / P0 authority / post-ADG baselines.
- **Current:** `generate_full_adg --force` exits **0** on snapshot `05212026_0548`; W4 contract gates and W1 ADG queries can proceed without ADG debt work.
- Impact: W1.1/W4 — use `0548` as query SSOT; no ADG burndown wave inside this plan.

---

## Definition of Done

DoD-1: **v15-only runtime vocabulary**
- Evidence: `rg 'R-HITL|R_HITL|route_contract_v12_extensions|v12_route_selector' agentic_core/ --glob '!**/_archive/**'` → no matches
- Status: PASS

DoD-2: **v15 fallback SSOT**
- Evidence: `config/routing/fallback_chains_v15.yaml` exists; `get_fallback_chain_v15(RouteIdV15.R4_SINGLE_ACTION)` returns managed-workflow + `TIER_HITL` aspect per doctrine
- Status: PASS

DoD-3: **Selector + proof smoke**
- Evidence: wireup 8/8 + v15 unit tests 39/39 (2026-05-25)
- Status: PASS

DoD-4: **E2E + CI gates**
- Evidence: `test_runtime_proof_harness.py` 67/67; L0 gates PASS; full `run_contract_gates.py` PARTIAL (unrelated plan taxonomy)
- Status: PARTIAL

DoD-5: **Closeout + Notion**
- Evidence: [l0_v15_only_cutover_w4_receipt_20260525.md](docs/reports/agentic_core/l0_v15_only_cutover_w4_receipt_20260525.md); Notion Plans `Completed` + W4 comment
- Status: PASS

### Verification vs Deferral

| Item | In plan? | Proof required |
|------|----------|----------------|
| v15-only selectors | W2–W3 | pytest + rg |
| v12 bridge for replay | GAP-1 | replay test subset |
| apps_rg parallel orchestration | Out of scope | separate plan |
| Author-Gate Cursor HITL | Out of scope | N/A |

---

## Scope Expansion Authorization

```
DISCOVERED_SCOPE: plan=l0-routing-v15-only-cutover-c9e2f1 wave=0 phase=0 gap="v12 replay manifests" impact="medium"
```

Defer execution of expansion until W1.1 inventory completes.

---

## Marker Quick Reference

```
WAVE_START: plan=l0-routing-v15-only-cutover-c9e2f1 wave=1
WAVE_COMPLETE: plan=l0-routing-v15-only-cutover-c9e2f1 wave=1 note="+N tests, N files, scope=fallback-v15-ssot"
PLAN_COMPLETE: plan=l0-routing-v15-only-cutover-c9e2f1 note="v15-only L0 routing; v12 retired"
```

---

## Related artifacts

| Artifact | Path |
|----------|------|
| ADG indexed snapshot (W1 SSOT) | [adg_indexed_05212026_0548.sqlite](artifacts/adg/adg_indexed_05212026_0548.sqlite) |
| ADG graph projection | [adg_graph_05212026_0548.sqlite](artifacts/adg/adg_graph_05212026_0548.sqlite) |
| W1.1 inventory (pending) | [l0_v12_fanin_inventory.json](artifacts/governance/l0_v12_fanin_inventory.json) |
| v15 contract | [`route_contract_v15.py`](agentic_core/L0_routing/types/route_contract_v15.py) |
| v15 selector | [`v15_route_selector.py`](agentic_core/L0_routing/reasoning/v15_route_selector.py) |
| Bridge (retire target) | [`route_contract_v15_bridge.py`](agentic_core/L0_routing/types/route_contract_v15_bridge.py) |
| v12 YAML (retire target) | [`fallback_chains.yaml`](config/routing/fallback_chains.yaml) |
| HITL posture doctrine | [`terminal_routes.py`](agentic_core/L0_routing/doctrine/terminal_routes.py) |
| Doctrine doc | `docs/reference/03_L0_Routing/03_L0_Route_Decision_Switching_L3 v15.md` |
---

## ADG_GRAPH_LAYER_EVIDENCE

Preflight scope (Constitutional §22) — MV-driven blast radius before edits:

| MV | Use |
|----|-----|
| `mv_fanin_top` | inbound dependency rank for scoped seam |
| `mv_fanout_top` | outbound consumer rank |
| `mv_blast_radius` | change-impact envelope |
| `mv_chokepoint_score` | sequencing / coupling risk |

Semantic edges: `flows_to`, `reads_from`, `writes_to` · P-view: `v_p0_wave_plan`

---

## ADG_HOTSPOT_REPORT

| Rank | Node | Archetype | Surface | Rationale |
|------|------|-----------|---------|-----------|
| 1 | scoped seam | CENTRAL_DEPENDENCY | Execution Surface | primary edit locus |
| 2 | gate / boundary | SAFETY_GATEKEEPER | Security Surface | fail-closed enforcement |
