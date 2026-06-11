---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\w6-w7-continuation-a7b3d2.md'
original_relative_path: 'w6-w7-continuation-a7b3d2.md'
source_sha256: e92819425e0913606851f515ebe471150346d8ad06dae77e591e0bd8fb071b30
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-24'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_type: refactor
---

# W6/W7 Continuation — Batch Closure

- **Plan ID**: `w6-w7-continuation-a7b3d2`
- **Parent**: `ssot-and-guardian-backlog-f1a5c4` + `sc1-structural-block-closure-f9e3b1`
- **ADR references**: ADR-051 (SC-1 remediation)
- **Status**: In-Progress
- **Start**: 2026-04-24
- **Target completion**: same session (T3 scope, bounded)

## Intent

Close the continuation list from the prior session in one consolidated pass:

1. Verify concurrent-agent idle (done: HEAD `b4c9565ae9`, clean tree)
2. Run W6.2b+c prefix codemod (docs/reports, adr, plans, scripts, artifacts/windsurf)
3. Execute W6.3-P1 (34-site ACCIDENTAL_CONCAT+TEMPLATE codemod + 20-site LOG_MESSAGE allowlist)
4. Build + run W7.1-P0 SC-1 subtype classifier
5. Defer W6.1 (BARE-guardian pass) to dedicated sessions per Author-Gate selection — high collision risk with L5 work from concurrent agent

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| **W1** | P0 | Verify agent idle + plan authoring | 1,500 | git log clean | Done | Plan file + Notion row posted |
| **W2** | P1 | W6.2b+c prefix codemod | 4,000 | codemod tool stable; runner pattern works | Todo | 4 literals applied; py_compile clean; commit + push |
| **W3** | P2 | W6.3-P1 codemod + allowlist | 6,000 | triage report accurate; SSOT probe exemption config exists | Todo | 34 sites rewritten; 20 allowlist entries added; tests pass |
| **W4** | P3 | W7.1-P0 SC-1 classifier | 4,500 | ADG snapshot available; `v_structural_conformance` view present | Todo | Classifier tool authored; 54 violations triaged; report published |
| **W5** | P4 | Notion sync + deferred-scope | 1,500 | MCP notion API available | Todo | Done rows posted for W1–W4; W6.1 captured as deferred |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| P0 | Plan + agent-idle verify | `.windsurf/plans/w6-w7-continuation-a7b3d2.md` + Notion row | Concurrent agent may re-awaken mid-session; use file-logging runner pattern to detect hangs | 1,500 | Done |
| P1 | W6.2b+c prefix codemod | runner `tools/debug/_w6_2bc_runner.py` calls migrator with 4 non-`artifacts/adg` literals | Codemod may hang if concurrent process holds file locks; each literal gated by the 60s internal py_compile timeout | 4,000 | Todo |
| P2 | W6.3-P1 codemod + allowlist | 34 ACCIDENTAL_CONCAT/TEMPLATE sites + config entry for 20 LOG_MESSAGE exemptions | Need to author a minimal codemod (f-string interpolation of SSOT constants for already-classified sites); allowlist location needs to be located first | 6,000 | Todo |
| P3 | W7.1-P0 SC-1 classifier | NEW `tools/debug/_sc1_subtype_classifier.py` + report `docs/reports/sc1_subtype_triage_20260424.md` | Need to locate `v_structural_conformance` schema + subtype heuristics calibration; ADG snapshot path from `artifacts/adg/` | 4,500 | Todo |
| P4 | Notion sync | 4 Wave/Phase rows + relation to parent plans | MCP serialization: 1 call per response | 1,500 | Todo |

## Gap Register

| Gap | Impact | Mitigation |
|---|---|---|
| Concurrent agent may commit/push during execution | Merge conflicts + corrupted stdout | File-based logging (`_w6_*_runner.py` pattern); spot-check `git log` before each push |
| W6.3-P1 codemod is new code (not previously authored) | Unproven tool; compile failures possible | Use same `ast.Constant` coord-rewrite pattern as W5 migrator; mandatory py_compile post-verification; revert on fail |
| SC-1 classifier needs ADG snapshot | Classifier blocked if snapshot stale | Use latest `artifacts/adg/adg_indexed_*.sqlite` (auto-pick newest) |
| W6.1 BARE-guardian pass excluded from this plan | 1696 site backlog remains | Captured as DEFERRED_SCOPE markers in final response; owns dedicated sessions per Author-Gate selection |

## ADG_HOTSPOT_REPORT

This plan is execution-oriented, not a refactor of a hotspot-ranked module set. The
underlying refactor targets (W6.2 prefix migration, W6.3 substring cleanup,
W7.1-P0 SC-1 classification) each draw on the canonical hotspot rankings in
their parent plans:

- W6.2 targets: no specific hotspots — path-literal migration is a broad
  sweep across `L_SHARED` (tools, diag, adg) with fan_in = total violation
  count per literal.
- W6.3 targets: 34 sites classified as ACCIDENTAL_CONCAT/TEMPLATE in
  `tools/debug/_w6_3_substring_triage.py` — not ranked by
  `mv_hotspot_centrality` because the impact is formatting, not structural.
- W7.1-P0: produces its own hotspot report per ADR-051 + the SC-1 plan; this
  continuation plan only bootstraps the classifier tool.

| Target | Layer | Archetype | Surface | Impact Notes |
|---|---|---|---|---|
| W6.2 artifacts/adg + 4 literals | L_SHARED | n/a (path migration) | State | All 5 SSOT literals tracked in `agentic_core/L0_routing/config/path_constants.py` |
| W6.3 P1 sites | L_SHARED | n/a (formatting) | State | Already triaged into 4 disposition buckets |
| W7.1-P0 | L5 (will classify L0..L5 sites) | will produce classification | Security+State+Write+Execution | 54 SC-1 violations to subtype |

## ADG_GRAPH_LAYER_EVIDENCE

### Materialized views cited (≥3 required per constitutional §22)

1. **`v_structural_conformance`** — SC-1 violation SSOT; W7.1-P0 classifier
   queries this for the 54 violations to sub-classify.
2. **`mv_graph_critical_path_blast_radius`** — informs W7.1-P0 ranking and
   will be picked up by the classifier; cross-referenced in the downstream
   W7.1 P1–P4 remediation plan.
3. **`mv_hotspot_centrality`** — used in the SC-1 classifier to flag any
   `CENTRAL_DEPENDENCY` or `ORCHESTRATOR` module among the 54 violations,
   which escalates remediation priority.
4. **`mv_dependency_cone_risk`** — cross-references violations with active
   risk cones; the classifier emits a `cone_intersects=true` flag when a
   violation sits inside an already-tracked risk surface.

### Semantic edges used

- `imports` — primary edge for SC-1 gravity/cycle detection.
- `writes_to` — tags subtype-1 direct-mutation bypass.
- `emits_side_effect` — tags subtype-4 exit-control skip.
- `controls_flow` — tags subtype-3 ingress shortcut.
- `resolves_callsite` — optional cross-check on suspected adapter bypass.

### P-view cross-references

- `v_p0_apps_direct_infra` — intersects SC-1 subtype-2 (boundary bypass).
- `v_p0_write_bypass_uwg` — intersects SC-1 subtype-1 (direct mutation).
- `v_p1_mis_layered_infra` — informs remediation direction (relocate vs rewire).

## Author-Gate Checkpoints

Per `.windsurf/rules/author-gate-enforcement.md` + constitutional §8, scored
Author-Gate required before:

- Adding any new anti-pattern instance (P2/P3 must not introduce any).
- Any `pytest.mark.skip` or xfail introduction (forbidden per §2).
- Any cross-layer refactor >5 files encountered in P3 classifier (T3 boundary).

This plan as authored introduces no new anti-patterns, no test skips, and no
T3 refactors — it only authors classifier tooling and applies pre-triaged
codemods. No Author-Gate expected during execution; any that fires is a
genuine mid-session decision point.

## Success Criteria

1. **W6.2b+c**: ≥10 sites migrated across the 4 non-`artifacts/adg` literals
   (strict safety filters may reject more than expected); py_compile clean.
2. **W6.3-P1**: 34 sites rewritten to f-string form; 20-site allowlist entries
   added to the correct config file; py_compile clean.
3. **W7.1-P0**: classifier tool authored, runs against latest ADG snapshot,
   emits report with per-violation subtype + module + layer + surface + fan_in.
4. **Notion**: 4 Wave/Phase Done rows (one per phase W1–W4) posted; parent
   plan rows updated with links to this continuation plan.
5. **Commits**: each wave committed separately with clear message, all pushed
   to origin/main.

## Non-Goals

- Not executing W6.1 BARE-guardian pass (1696 sites) — too large + too
  collision-prone with active L5 work; deferred.
- Not executing W7.1 P1–P4 SC-1 remediation — requires P0 output first; owns
  dedicated plan `sc1-structural-block-closure-f9e3b1.md`.
- Not refactoring any production code beyond the triaged sites.

## Token Budget

Total: **17,500 tokens** (1,500 + 4,000 + 6,000 + 4,500 + 1,500).
Status: 🟢 GREEN (T2/T3 ceiling is 30,000).

## Execution Order

Execute P1 → P2 → P3 → P4 sequentially. Each phase ends with git commit +
push before the next starts. If any phase fails, capture state as DEFERRED_SCOPE
marker + proceed to the next phase.
