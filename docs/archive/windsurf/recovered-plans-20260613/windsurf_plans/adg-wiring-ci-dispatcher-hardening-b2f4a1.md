# ADG Wiring-CI Dispatcher Hardening (H6-H10)

**Slug:** `adg-wiring-ci-dispatcher-hardening-b2f4a1`
**Parent:** `adg-wiring-ci-hardening-7a5d84` (gate fleet shipped — 48 gates, commit `63e688ebb6`)
**Status:** Todo (follow-on from parent plan's optional H-track)
**Tier:** T2 (multi-file, single-layer ops-tooling)

## Context

Parent plan `adg-wiring-ci-hardening-7a5d84` shipped 23/24 gates across W3–W6 (1 deferred as W5.3 Gate L — CVE propagation, see separate DEFERRED_SCOPE). The H-track items H1–H5 (dispatcher + graph-native integration + canonical fold) landed pre-plan. **H6–H10 were explicitly scoped as optional, non-blocking improvements** on top of the green 48-gate fleet. This plan captures them for execution when capacity permits.

All five items are ops-tooling changes to `ops_scripts/ci/adg_gates/` and related CI infra. None touch production agentic code (L0–L6); layer classification is `L_OPS`.

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---:|---|---|---|
| H6 | H6.1 | Shared ro connection pool | 4,000 | 48-gate fleet stays stable; SQLite ro handles are thread-safe | Todo | Fleet wall-clock drops ≥25%; per-gate conn opens ≤1 per run |
| H7 | H7.1 | Dispatcher filter flags | 3,000 | Existing GateSpec.owner/tier/band fields sufficient | Todo | `--owner`, `--band`, `--tier` flags work; CI PR-quick subset documented |
| H8 | H8.1 | GitHub Actions matrix | 2,000 | H7 shipped first (flags drive matrix strategy) | Todo | Two parallel CI jobs (canonical / wiring); total CI time cut ≥40% |
| H9 | H9.1 | Waiver-expiry enforcement | 3,000 | T7l gate exists; waiver file schema TBD | Todo | `waivers.yaml` schema locked; expired waivers block CI |
| H10 | H10.1 | CVE/OSV client + Gate L | 6,000 | External HTTP allowed in CI; OSV API rate-limit acceptable | Todo | `check_w5_cve_propagation.py` live; W5.3 unblocked |

**Total est. tokens: 18,000** 🟡 (within YELLOW 24k threshold per single-agent run)

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| H6.1 | Shared SQLite ro connection pool | `ops_scripts/ci/adg_gates/run.py`, `_adg_wiring_gate_base.py`, `_adg_snapshot_diff.py` | Thread-safety of shared `sqlite3.Connection`; must not break `--seed` paths | 4,000 | Todo |
| H7.1 | `--owner`/`--band`/`--tier` filters | `ops_scripts/ci/adg_gates/run.py` only | Flag composition semantics (AND vs OR); docstring drift | 3,000 | Todo |
| H8.1 | GH Actions matrix split | `.github/workflows/adg-ci-gates.yml`, `author-gate-gates.yml` | Artifact path coordination across matrix jobs | 2,000 | Todo |
| H9.1 | Waiver-expiry enforcement | `ops_scripts/ci/check_wiring_waiver_expiry.py` (exists, empty), `config/wiring_waivers.yaml` (new) | Waiver schema alignment with Constitutional Rules Registry; no existing consumers | 3,000 | Todo |
| H10.1 | CVE/OSV client + Gate L | `tools/supply_chain/osv_client.py` (new), `ops_scripts/ci/check_w5_cve_propagation.py` (new), `ops_scripts/ci/baselines/wiring_cve_propagation_ratchet.json` (new) | External HTTP dependency; needs `enhanced_http` MCP or direct aiohttp; rate limiting | 6,000 | Todo |

## Gap Register

| ID | Description | Blocks |
|---|---|---|
| G1 | OSV API auth model unclear (anonymous vs key) — research before H10.1 | H10.1 |
| G2 | Waiver schema SSOT — aligns with `constitutional.md` §8 exemption format or new schema? — Author-Gate decision | H9.1 |
| G3 | CI minutes budget for matrix — is parallelization worth the compute uplift? | H8.1 |

## ADG_HOTSPOT_REPORT

All phases target `ops_scripts/ci/adg_gates/` (L_OPS, non-production). Hotspot analysis N/A for ops tooling — dispatcher code has no production fan-in. Referenced for completeness only.

| File | Archetype | Layer | Fan-in | Surface | Impact |
|---|---|---|---:|---|---:|
| `ops_scripts/ci/adg_gates/run.py` | ORCHESTRATOR | L_OPS | 0 (entry point) | Observability | 1.0 |
| `ops_scripts/ci/_adg_wiring_gate_base.py` | CENTRAL_DEPENDENCY | L_OPS | 25 (all wiring gates) | Observability | 1.75 |

## ADG_GRAPH_LAYER_EVIDENCE

H6–H10 do not modify production code flows — they modify the harness that reads the ADG. Standard graph-layer evidence rule (§22) applies to refactors of production code; for ops-tooling plans, the evidence requirement is satisfied by citing:

- **`mv_hotspot_centrality`** — confirms zero production fan-in for `ops_scripts/ci/adg_gates/*`
- **`mv_dependency_cone_risk`** — confirms no L0–L6 modules depend on these files
- **`v_p3_isolated_experimental`** — verifies these files are not misclassified as experimental/dead

Full MV + semantic-edge evidence will be re-derived per phase before execution — phase plans must attach evidence specific to any code actually changed outside `ops_scripts/ci/adg_gates/`.

## Rollout Discipline

- Each phase ships as its own commit; no phase-combined PRs.
- `python -m ops_scripts.ci.adg_gates.run` must stay green after every phase.
- No phase merges if fleet wall-clock regresses (current baseline: ~22s for 48 gates).
- H10 is gated by G1 resolution (OSV auth model research).

## References

- Parent plan: `.windsurf/plans/adg-wiring-ci-hardening-7a5d84.md`
- Fleet last run: `artifacts/adg/adg_gate_results_20260423_161634.json` (48 gates, overall_exit=1 on real violations)
- Deferred-scope rule: `.windsurf/rules/deferred-scope-capture.md`
- Constitutional §22 (graph-layer evidence): `.windsurf/rules/constitutional.md`
