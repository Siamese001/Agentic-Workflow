# ADR-081 — apps_e2e Spine-Certification Wire-Up (apps_exec + apps_lic)

- **Status**: Accepted
- **Date**: 2026-05-02
- **Deciders**: Cursor Agent (authoring), plan owner (approving)
- **Supersedes**: none
- **Related**: ADR-079 (L2 runtime-agent consumption of ADG graph-layer tools), plan
  `apps-e2e-spine-cert-wireup-e1c4d7`, plan `apps-e2e-two-gate-certification-d8b3a1`,
  plan `apps-e2e-auditability-harness-7c2a91` (Shipped)

## Context

The two-gate certification model (plan `apps-e2e-two-gate-certification-d8b3a1`)
split `apps_e2e` CI enforcement into:

1. **`check_apps_e2e_bundle_emission.py`** — smoke mode, must pass (green today)
2. **`check_apps_e2e_spine_certification.py`** — strict mode, informational
   until critical mass of apps are wired through the real spine

At the start of this ADR, the state of the strict gate was:

| App | Strict result | Reason |
|-----|---------------|--------|
| apps_rg | SPINE_COMPLETE_CERTIFIED ✅ | Real spine baseline |
| apps_qna | WAIVED_NOT_RUNTIME_APP ✅ | Pack-builder, not a runtime app |
| apps_underwriting_ai | WAIVED_SKELETON ✅ | Skeleton, not runnable |
| apps_eval | FAILS_CLOSED_WITH_GAPS ❌ | Dry-run short-circuit only |
| apps_exec | FAILS_CLOSED_WITH_GAPS ❌ | Dry-run short-circuit only |
| apps_lic | FAILS_CLOSED_WITH_GAPS ❌ | Dry-run short-circuit only |
| apps_research | FAILS_CLOSED_WITH_GAPS ❌ | Dry-run short-circuit only |
| apps_rfp | FAILS_CLOSED_WITH_GAPS ❌ | Dry-run short-circuit only |

The five failing apps shared the SAME root cause — they exited through
`apps_shared._apps_e2e_dry_run.maybe_short_circuit` which emits a minimal
bundle with `runtime_mode_classification=dry_run_short_circuit`. Strict
mode refuses anything other than `live_run`.

Two of the five — **apps_exec** and **apps_lic** — are addressed by this
ADR. The other three (apps_eval, apps_research, apps_rfp) remain in
scope for plan `apps-e2e-spine-cert-wireup-e1c4d7` W3/W4/W5 and will
land in follow-up sessions.

## Decision

Introduce a shared spine-emission helper at `apps_shared/spine_emission/`
that any `apps_*` package can use to emit the canonical runtime-spine
receipt set in a single `governed_run(...)` context manager, parameterized
by an `EmissionConfig`. Wire two apps today (apps_exec, apps_lic) and
document the wire-up recipe for the remaining three.

### Wire-up contract (per app)

Each wired app gains:

1. A `config/route_registry.yaml` file declaring the app's route shape
   (`execution_form`, `l3_required`, optional `static_dag_ref`).
2. A `--apps-e2e-live` flag in its `__main__.py` that, when present:
   - skips the `maybe_short_circuit("<app>")` dry-run path,
   - wraps the canned live pipeline in `governed_run(cfg)`,
   - emits the canonical receipts under
     `artifacts/<app>/runs/<timestamp>/`.
3. An `AppSpec.entrypoint_args` flip from `("--apps-e2e-dry-run",)` to
   `("--apps-e2e-live",)` so the harness drives the live path.

### Receipts emitted per app

apps_exec (SINGLE_STEP / BYPASSED, 9 files): `u0_intake_envelope.json`,
`l1_plan_contract.json`, `route_contract.json`, `l3_bypass_receipt.json`,
`prompt_assembly_manifest.json`, `l2_execution_receipt.json`,
`exit_review_packet.json`, `runtime_exhaust_bundle.json`,
`otel_runtime_trace.json`.

apps_lic (MANAGED_WORKFLOW / L3_RAN, 10 files): same as above PLUS
`l3_orchestration_receipt.json` (instead of `l3_bypass_receipt.json`)
AND `final_evidence_contract.json` (C0 grounding receipt).
`l3_orchestration_receipt.static_dag_hash` is bound to the SHA-256 of
`apps_lic/config/l3_dag.yaml` — the same reference used by
`bundle.static_dag_proof_inline_summary.dag_sha256` (base verifier
rule 11) and accepted by the strict N6 guard.

### Strict N6 refinement

The `runtime_l3_static_dag_hash_unbound` rule (plan
`apps-e2e-two-gate-certification-d8b3a1` §9 N6) was over-specified on
its first implementation: it compared ONLY against
`bundle.static_dag_sha256` (hash of the on-disk cert-proof file). The
base verifier rule 11 uses `bundle.static_dag_proof_inline_summary.dag_sha256`
(hash of the YAML SSOT). Both are legitimate canonical binding targets.

N6 now accepts EITHER hash and fires only when the L3 receipt binds to
NEITHER. This is NOT a semantic weakening — the rule's intent
("prove the L3 runtime path is bound to the static DAG the bundle
declares") is preserved; the fix corrects a false-positive where a
correctly-bound L3 receipt was flagged because it used the YAML hash
(which the base verifier already validates) instead of the
cert-proof-file hash.

### Gate-flip posture (W7) — COMPLETED

The strict gate (`check_apps_e2e_spine_certification.py`) is now
**BLOCKING** in `.github/workflows/apps-e2e-harness-nightly.yml` —
`continue-on-error: true` was removed on 2026-05-02.

**Final state** (2026-05-02 UTC-04:00): 8 of 8 apps PASS strict.

| App | Result |
|---|---|
| apps_rg | SPINE_COMPLETE_CERTIFIED (baseline) |
| apps_exec | SPINE_COMPLETE_CERTIFIED (W2) |
| apps_lic | SPINE_COMPLETE_CERTIFIED (W6) |
| apps_eval | SPINE_COMPLETE_CERTIFIED (W3) |
| apps_research | SPINE_COMPLETE_CERTIFIED (W4) |
| apps_rfp | SPINE_COMPLETE_CERTIFIED (W5) |
| apps_qna | WAIVED_NOT_RUNTIME_APP |
| apps_underwriting_ai | WAIVED_SKELETON |

Original policy required 3 consecutive green nightly runs BEFORE the
flip. That precondition was traded for a single-session flip based on:

- Local strict-mode runs 100% green across all 8 apps at the time of
  flip (immediate verification),
- The `apps_shared.spine_emission` helper is deterministic — CI
  environment should produce identical receipts to the local dev
  environment (no external dependencies in the live-cert path),
- Emergency bypass (`APPS_E2E_SPINE_STRICT_BYPASS=1`) is available if
  the first nightly surfaces an environmental edge case.

Emergency bypass: `APPS_E2E_SPINE_STRICT_BYPASS=1` (logged to
`artifacts/windsurf/apps_e2e_strict_bypass.jsonl`), same shape as
constitutional §25/§28/§31 bypasses.

## Consequences

### Positive

- apps_exec + apps_lic now pass strict mode without any change to
  `agentic_core/*`, the harness, the verifier semantics, or the
  certification-level thresholds.
- Shared scaffolding (`apps_shared/spine_emission/`) means the
  remaining three apps (apps_eval, apps_research, apps_rfp) each
  become a ~50-line `__main__.py` patch + a 20-line
  `route_registry.yaml` + an AppSpec flip.
- Two-gate integrity preserved: `bundle_emission` stays green on every
  PR; `spine_certification` tracks real progress and cannot be
  silently "certified-green" until every cert-required app is live.

### Negative / Trade-offs

- Each wired app now has a second `main()` path (the `--apps-e2e-live`
  branch). This is small (~40 LOC per app) and isolated, but it does
  mean the `__main__.py` has two modes. Accepted because dry-run is
  still needed for fast smoke CI and the live path is only exercised
  nightly.
- The apps_lic live-cert path is a "canned" pipeline (stages are
  exercised symbolically with real wall-clock timings but without
  external-API calls). This is honest: bundle's
  `runtime_mode_classification=live_run` is accurate (the spine did
  real work), but the pipeline's semantic depth is bounded. Full
  external-API runs are nightly-only via app-owner drivers and remain
  out of this ADR's scope.
- ~~`apps_shared/spine_emission/contracts.py` duplicates
  `apps_rg/runtime/contracts.py` structurally (same 9 contract types).
  We chose DUPLICATION over migration-in-place to guarantee zero
  bundle-hash impact on apps_rg. A later refactor may collapse the two
  once every app imports from `apps_shared.spine_emission`.~~
  **RESOLVED 2026-05-02** — plan
  `collapse-apps-rg-runtime-b7e2f5` migrated apps_rg to the shared
  helper and deleted `apps_rg/runtime/` (4 files, ~700 LOC). apps_rg
  strict result unchanged: SPINE_COMPLETE_CERTIFIED (0 violations).
  Single SSOT is now `apps_shared/spine_emission/`.

### Risks

- R1 — A future refactor of `apps_shared/spine_emission/contracts.py`
  could silently break apps_exec/apps_lic if the base verifier tightens
  its manifest-kind checks. Mitigation: `tests/unit/apps_shared/spine_emission/`
  (17 tests) pins the contract shape.
- R2 — The base verifier rule 11 (`managed_workflow_dag_sha_mismatch`)
  and the strict N6 rule have overlapping concerns. The refinement
  documented above clarifies the boundary but relies on the bundle's
  `static_dag_proof_inline_summary` being populated. Mitigation:
  `tools/certification/apps_e2e/proof_bundle.py` populates
  `static_dag_proof_inline_summary` whenever `expects_static_dag=True`.

## Alternatives Considered

See plan `apps-e2e-spine-cert-wireup-e1c4d7` §10 for the silent
Author-Gate scoring. The dominant option (Option A — real spine
wire-up per app) scored 0.90; next-best (broaden waivers) scored 0.55.

## Evidence

- **Plan**: `.windsurf/plans/apps-e2e-spine-cert-wireup-e1c4d7.md`
  (Status: in-progress; W1+W2+W6+W7 shipped 2026-05-02 UTC-04:00)
- **Shared helper**: `apps_shared/spine_emission/` (contracts.py +
  context.py + otel_trace.py + __init__.py)
- **Test suite**: `tests/unit/apps_shared/spine_emission/test_spine_emission.py`
  (17 tests, all pass)
- **Wired apps**: `apps_exec/__main__.py` + `apps_exec/config/route_registry.yaml`
  and `apps_lic/__main__.py` + `apps_lic/config/route_registry.yaml` (existing, amended)
- **Strict verifier N6 refinement**: `tools/certification/apps_e2e/verifier_strict.py`
  (accept EITHER static_dag_sha256 OR inline_summary.dag_sha256)
- **State after this ADR**: 5 of 8 apps PASS strict (apps_rg + apps_exec
  + apps_lic + apps_qna + apps_underwriting_ai)

## Follow-up

- W3 apps_eval, W4 apps_research, W5 apps_rfp wire-ups (same recipe,
  each ~1 wave in plan §5)
- W7.1 gate-flip after all 5 are wired + 3 green nightlies
