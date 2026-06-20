---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-e2e-two-gate-certification-d8b3a1.md'
original_relative_path: '_archive\\2026-05\\apps-e2e-two-gate-certification-d8b3a1.md'
source_sha256: 1a794c366c3107fcc4f1837e30245948cced06641109da1b90d4a9fcec1983a2
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Apps_E2E Two-Gate Certification — Implementation Plan

**Plan ID**: `apps-e2e-two-gate-certification-d8b3a1`
**Status**: Draft v2 — hardening amendments applied 2026-05-02 06:28 UTC; ready for W1 execution
**Tier**: T3 (multi-app, governance-critical, alters CI semantics)
**Sibling plan**: `apps-e2e-auditability-harness-7c2a91.md` (closed 2026-05-02 — assumed as input here)
**Author-Gate decision (silent)**: `architecture_choice` — split one CI gate into two with explicit certification levels rather than retire `--apps-e2e-dry-run` or weaken default-emit. Same harness, two enforcement modes, one source of truth.

DECISION_CAPTURED: type=architecture_choice, repo_area=tools/certification/apps_e2e, selected=two-gates-with-certification-levels, outcome=plan-only, principle=green-CI-must-not-imply-certification, precedent=strong

---

## 0.1 Amendment Log (v1 → v2, 2026-05-02 06:28 UTC)

Seven hardening categories applied before W1 execution:

1. **Exit/L6 separated** — `runtime_exit_disposition_ref` is now an always-on certification requirement (`exit_required=True`, implicit, not a per-app flag). `l6_required` renamed to `l6_exhaust_required` and gates ONLY `runtime_exhaust_ref`. ExitReviewPacket and X3 disposition are no longer described as L6-owned. (See §4, §6.)
2. **Execution form normalized** — `BYPASS` removed as an `expected_execution_form` value (it is a *path outcome*, not an execution form). New enum: `TERMINAL_SHORTCIRCUIT | SINGLE_STEP | MANAGED_WORKFLOW`. New parallel field `expected_l3_path ∈ {RAN, BYPASSED}` captures whether L3 ran or was bypassed. Receipt selection (§6) keys off `expected_l3_path`, not `expected_execution_form`. (See §4, §6.)
3. **Fixture-rule clarification** — `fixture_data_used=True` is **allowed** in strict mode (deterministic input is fine). `fixture_runtime_mode=True`, `mock_mode_detected=True`, `synthetic_trace_detected=True` are **rejected** in strict mode. Deterministic fixture input is NOT fake runtime proof. (See §5.3, §9.)
4. **`certification_level` is verifier-owned** — always computed by `compute_level()`, never trusted from the bundle. `bundle.success=True` is legal *only* when computed `certification_level=SPINE_COMPLETE_CERTIFIED`. Any weaker level with `success=True` is a strict-mode violation. (See §3, §5.3.)
5. **Hash rules tightened** — smoke mode hash-verifies every declared `*_ref` but does NOT require all spine receipts. Strict mode requires all expected receipts AND hash-verifies every declared `*_ref` AND requires every `*_ref` to appear in the artifact manifest with `{artifact_kind, path, sha256, run_id}`. (See §5.2, §6.5.)
6. **Artifact-kind enum + checks** — new enum `ArtifactKind ∈ {route_contract, l1_plan_contract, l3_runtime_receipt, l3_bypass_receipt, exit_x3_disposition, runtime_exhaust_bundle, otel_trace, runtime_adg_trace}`. Strict mode fails if a required kind is missing, duplicated, or mismatched against the slot it occupies. (See §6.5.)
7. **5 new negative controls** — N16 (success=true with weaker computed level), N17 (fixture_data_used=true on real runtime, MUST PASS), N18 (fixture_runtime_mode=true, MUST FAIL), N19 (declared ref absent from manifest, MUST FAIL), N20 (duplicate artifact_kind=route_contract, MUST FAIL). (See §9.)

After amendments are reflected in §3–§9, W1–W6 execute exactly as previously planned in §10–§11.

---

## 0. TL;DR

The current harness conflates two distinct properties:

1. **Bundle emission** — every app produces a hash-bound, run_id-bound proof bundle.
2. **Spine certification** — the app actually runs through the governed `agentic_core` runtime spine and emits all required receipts.

Today's CI gate (`ops_scripts/ci/check_apps_e2e_harness`) is green when **only #1 is true** for 6 of 7 runnable apps. That is misleading. The fix is to **split one gate into two**, add explicit per-app `CertificationLevel`, extend `AppSpec` with required-receipt declarations, give the verifier three enforcement modes (smoke / warn / strict), and add a negative-control suite that mutates real bundles to prove strict mode rejects everything it must.

**Expected post-implementation state**:

| Gate | Today | After this plan |
|---|---|---|
| `apps_e2e_bundle_emission` | (does not exist as separate gate) | **GREEN** — all 7 runnable apps emit valid bundles |
| `apps_e2e_spine_certification` | (does not exist) | **RED** — only `apps_rg` is `SPINE_COMPLETE_CERTIFIED`; the other 6 are `FAILS_CLOSED_WITH_GAPS` until they emit real spine receipts |

Dry-run is explicitly **NOT certification**. Dry-run is a smoke-only path. Strict mode rejects bundles whose `runtime_mode` indicates a short-circuit happened.

---

## 1. Motivation — What's Broken

### 1.1 The misleading-green problem

Current state observed in the live matrix (apps_e2e_matrix.json, 2026-05-02):

| App | success | gaps | runtime_mode |
|---|:-:|---:|---|
| apps_rg | True | 0 | `live_run` |
| apps_eval | False | 9 | `standalone_orchestrator_pre_spine` |
| apps_exec | False | 8 | `standalone_orchestrator_pre_spine` |
| apps_lic | False | 9 | `standalone_orchestrator_pre_spine` |
| apps_qna | False | 6 | `standalone_orchestrator_pre_spine` (BYPASS app) |
| apps_research | False | 9 | `standalone_orchestrator_pre_spine` |
| apps_rfp | False | 9 | `standalone_orchestrator_pre_spine` |

The CI gate `check_apps_e2e_harness` returns `0` ("8 specs registered"). A reader could mistake this for "all apps are spine-complete." They are not. Only `apps_rg` is.

### 1.2 The dry-run-as-certification trap

`--apps-e2e-dry-run` short-circuits 5 apps' `__main__.main()` BEFORE `_adg_bootstrap()` runs. The bundle emitted in this case is honest (success=false, 8–9 gaps, runtime_mode=`standalone_orchestrator_pre_spine`), but a future reader could plausibly add `--apps-e2e-dry-run` to a CI driver and silently downgrade certification to smoke. We need a verifier rule that explicitly **rejects dry-run runtime_modes from strict mode**.

### 1.3 The missing-receipt-is-not-a-violation problem

Today's `shared_verifier.verify_bundle()` returns an empty violation list when the bundle declares `success=false` with explicit `blocking_gaps`. That is correct for bundle emission (the bundle is internally consistent). It is **wrong for certification** (the app provably did not engage the spine). Strict mode needs a new fail-closed path: missing required receipts → certification violation, even when the bundle is internally consistent.

---

## 2. Goal (verbatim contract)

Split apps_e2e enforcement into two explicit gates so green CI cannot be mistaken for full apps_* auditability certification:

### 2.1 Gate `apps_e2e_bundle_emission`

- Every runnable apps_* emits a valid, hash-bound, run_id-bound proof bundle.
- May pass even when `success=false`, **provided** `blocking_gaps` is non-empty AND every gap is structurally well-formed (rule_id present, stage present).
- Schema-level violations (missing required top-level field, hash mismatch, app_name mismatch, timestamp not ISO-UTC) still fail this gate.

### 2.2 Gate `apps_e2e_spine_certification`

- Every `certification_required` runnable apps_* must have `success=true`.
- `blocking_gaps` MUST be empty for any spec with `certification_required=True`.
- Every required spine receipt (per AppSpec required-receipt flags) must exist on disk AND hash-verify against `run_info.artifacts[].sha256`.
- Missing receipts fail closed (no "honest gap" exemption in strict mode).
- Waiver rows require explicit reason / owner / expiry; expired waivers fail strict.
- Apps in `runtime_mode` indicating a dry-run / short-circuit / mock fail strict.

---

## 3. Certification Levels (5 explicit values)

A new enum lives at `tools/certification/apps_e2e/certification_levels.py`. Every per-app row in `apps_e2e_matrix.json` carries exactly one `certification_level`.

| Level | Meaning | Eligible If |
|---|---|---|
| `EMITS_BUNDLE` | A valid, hash-bound bundle exists, but neither success nor full-receipt is asserted. Smoke-only. | bundle parses, schema valid, harness_pass=True |
| `FAILS_CLOSED_WITH_GAPS` | Bundle is valid AND honestly declares `success=false` AND `blocking_gaps` is non-empty AND every gap is structurally well-formed. | all of the above + success=False + len(gaps)>0 |
| `SPINE_COMPLETE_CERTIFIED` | success=true, blocking_gaps empty, every required receipt present + hash-verified, runtime_mode is a real-spine value (not dry-run / mock / fixture). | all of the above + receipts on disk + sha256 match + runtime_mode ∈ APPROVED_LIVE_MODES |
| `WAIVED_SKELETON` | Spec declares `runnable=False` and AppSpec has a valid waiver block. Bundle may be absent. | spec.runnable=False AND waiver complete + non-expired |
| `WAIVED_NOT_RUNTIME_APP` | Spec opts out of certification (`certification_required=False`) with a valid waiver — e.g., a pure pack-builder / non-spine app. Must still emit a bundle for bundle_emission gate. | spec.certification_required=False AND waiver complete + non-expired |

**Hard rules**:

- Levels are computed by the verifier, never hand-set in AppSpec.
- A spec without a waiver block CANNOT land in `WAIVED_*`.
- A spec with `certification_required=True` and `runnable=True` whose bundle is anything other than `SPINE_COMPLETE_CERTIFIED` is a **strict-mode violation**.
- `apps_e2e_matrix.json` totals must include level breakdown: `{emits_bundle, fails_closed_with_gaps, spine_complete_certified, waived_skeleton, waived_not_runtime_app}` — sum must equal `discovered`.

---

## 4. Extended AppSpec — 11 New Fields

### 4.1 Field roster (additive; no rename)

```python
@dataclass(frozen=True)
class AppSpec:
    # ----- existing fields preserved -----
    app_name: str
    app_package: str
    runnable: bool
    expected_route_form: str             # MANAGED_WORKFLOW | BYPASS | UNKNOWN
    expects_static_dag: bool
    expects_c0_grounding: bool           # legacy alias of c0_required (see §4.3)
    expects_prompt_assembly: bool        # legacy alias of prompt_assembly_required
    expects_l2_execution: bool           # legacy alias of l2_required
    expects_durable_mutation: bool       # legacy alias of uwg_required
    runs_root_glob: str
    entrypoint_args: tuple[str, ...] = ()
    notes: str = ""

    # ----- NEW: certification-level-required fields -----
    certification_required: bool = True              # T2/T3 enforcement target
    expected_execution_form: str = "UNKNOWN"         # TERMINAL_SHORTCIRCUIT | SINGLE_STEP | MANAGED_WORKFLOW | UNKNOWN
    expected_l3_path: str = "UNKNOWN"                # RAN | BYPASSED | UNKNOWN  (path outcome, not form)
    c0_required: bool | None = None                  # None → fall back to expects_c0_grounding
    prompt_assembly_required: bool | None = None     # None → fall back to expects_prompt_assembly
    l2_required: bool | None = None                  # None → fall back to expects_l2_execution
    l3_required: bool | None = None                  # None → True iff expected_l3_path == "RAN"
    uwg_required: bool | None = None                 # None → fall back to expects_durable_mutation
    l6_exhaust_required: bool = True                 # runtime_exhaust_ref (RuntimeExhaustBundle) required
    otel_required: bool = True                       # OTEL or runtime-ADG trace required
    # NOTE: exit_required is implicit and ALWAYS True for certification — not a configurable
    # field. ExitReviewPacket / X3 disposition is NOT an L6 artifact; it is the exit-control
    # contract that must precede any L6 emission.

    # ----- NEW: waiver block (all-or-nothing) -----
    waiver_reason: str | None = None
    waiver_owner: str | None = None
    waiver_expiry: str | None = None                 # ISO-8601 UTC
```

**Execution form vs. L3 path — do not conflate**:

- `expected_execution_form` describes the *shape of the run*: was it terminal-shortcircuit (no spine engagement intended), single-step (one governed cycle, no DAG), or managed-workflow (multi-step DAG-driven)?
- `expected_l3_path` describes the *L3 receipt outcome*: did L3 RUN (emitted `l3_runtime_receipt`), or was it BYPASSED (emitted `l3_bypass_receipt`)?
- A `MANAGED_WORKFLOW` form implies `expected_l3_path=RAN`. A `TERMINAL_SHORTCIRCUIT` or `SINGLE_STEP` form typically implies `expected_l3_path=BYPASSED`. The verifier asserts this consistency in W2.4.

### 4.2 Resolution rule — `effective_*_required(spec) -> bool`

The verifier never reads `c0_required` directly; it calls `effective_c0_required(spec)` which:

1. If `spec.c0_required is not None`, return it.
2. Else return `spec.expects_c0_grounding`.

Same pattern for the 4 other `*_required` fields with explicit `expects_*` legacy names. This preserves backward compatibility with existing AppSpec rows: a row with no new fields has identical behavior to today's row except `certification_required` defaults to `True` and `l6_required` / `otel_required` default to `True`.

### 4.3 Why two field names per concern (`expects_*` and `*_required`)

Today's harness uses `expects_*` (which the bundle emitter already reads). The new gate semantics need the same information but framed as "required for certification." Rather than rename and risk breaking existing readers, we add a parallel `*_required` field that defaults to `None` and falls back to `expects_*`. After one full release cycle, a follow-up plan can deprecate `expects_*` (out of scope here).

### 4.4 Waiver block invariant

A waiver is valid iff:

- `runnable=False` AND `waiver_reason`, `waiver_owner`, `waiver_expiry` all set, OR
- `certification_required=False` AND `waiver_reason`, `waiver_owner`, `waiver_expiry` all set, AND
- `waiver_expiry` parses as ISO-8601 UTC AND is in the future at verifier-run time.

Any AppSpec setting `runnable=False` OR `certification_required=False` without the full triple is a **strict-mode failure** (`waiver_incomplete` or `waiver_expired`).

---

## 5. Verifier Modes

### 5.1 CLI surface

```bash
python -m tools.certification.apps_e2e.shared_verifier --mode smoke   [--app <name>] [--matrix <path>]
python -m tools.certification.apps_e2e.shared_verifier --mode warn    [--app <name>] [--matrix <path>]
python -m tools.certification.apps_e2e.shared_verifier --mode strict  [--app <name>] [--matrix <path>]
```

`--mode` is required (no implicit default — forces a deliberate choice in scripts).

### 5.2 Mode semantics

| Mode | Bundle valid? | Gaps allowed? | Required receipts must hash-verify? | Waiver enforcement | Exit code on violation |
|---|:-:|:-:|:-:|---|:-:|
| `smoke` | yes | yes (any) | no | none | 1 only on schema/hash violations |
| `warn` | yes | yes (any) | no | none | **0** always; emits machine-readable diff to stderr |
| `strict` | yes | **no** for `certification_required` apps | yes (all expected) | required | 1 on any §5.3 rule |

**Hash-verification scope by mode**:

- All modes hash-verify every `*_ref` that is declared in the bundle (you cannot lie about what is on disk).
- Smoke + warn modes do NOT require receipts that aren't in the bundle.
- Strict mode additionally requires every receipt in `required_receipts(spec)` to be declared, present, hash-verified, AND registered in the artifact manifest with `{artifact_kind, path, sha256, run_id}`.

### 5.3 Strict-mode rules (each is a fail-closed check)

For every spec where `effective_certification_required(spec)=True`:

- **S1** — `bundle.success` must be `True`.
- **S2** — `bundle.blocking_gaps` must be empty.
- **S3** — Every receipt named by `required_receipts(spec)` (see §6) must exist on disk, have a matching `run_info.artifacts[].sha256` entry, AND have an artifact-manifest row with the expected `artifact_kind` (§6.5).
- **S4** — Runtime-mode classification must satisfy:
  - `bundle.runtime_mode_classification == "live_run"` (no `dry_run_short_circuit`, no `standalone_orchestrator_pre_spine`, no `skeleton_only`).
  - `bundle.fixture_runtime_mode != True` — fixture runtime mode is rejected.
  - `bundle.mock_mode_detected != True` — mock mode is rejected.
  - `bundle.synthetic_trace_detected != True` — synthetic OTEL is rejected.
  - `bundle.fixture_data_used` IS PERMITTED — deterministic input is fine if the run engaged real runtime. (Per amendment 3.)
- **S5** — `bundle.app_overlay_authority_status` must be `OK` (no spine artifact emitted by an `apps_*` module).
- **S6** — `bundle.agentic_core_spine_status` must be `OK`.
- **S7** — Computed `certification_level` (see §3 + amendment 4) must equal `SPINE_COMPLETE_CERTIFIED`. The bundle's self-declared `certification_level`, if present, is **never trusted** — the verifier always recomputes.
- **S8** — `bundle.success=True` is legal ONLY when computed level equals `SPINE_COMPLETE_CERTIFIED`. `success=True` paired with any weaker computed level is a strict failure (`success_true_but_level_weaker_than_certified`).
- **S9** — `bundle.runtime_exit_disposition_ref` must be present, on-disk, hash-verified, and bound to `artifact_kind=exit_x3_disposition`. (Exit is implicit and ALWAYS required — amendment 1.)
- **S10** — If `effective_l6_exhaust_required(spec)`, `bundle.runtime_exhaust_ref` must be present, on-disk, hash-verified, and bound to `artifact_kind=runtime_exhaust_bundle`. The exhaust check is **separate** from the exit check.
- **S11** — If `bundle.l6_observability_ref` is present, its timestamp must be strictly AFTER `runtime_exit_disposition_ref.finished_at_utc`. (L6 cannot precede Exit.)
- **S12** — `expected_execution_form != "UNKNOWN"`. Unknown form under certification is a failure (`execution_form_unknown_under_certification`).
- **S13** — Consistency: `expected_execution_form == "MANAGED_WORKFLOW"` requires `expected_l3_path == "RAN"`. `expected_execution_form ∈ {"TERMINAL_SHORTCIRCUIT", "SINGLE_STEP"}` requires `expected_l3_path == "BYPASSED"`.
- **S14** — Negative-control invariants (§9) all must NOT fire.

For every spec where `runnable=False` OR `certification_required=False`:

- **S15** — Waiver block must be complete (`reason`, `owner`, `expiry` all set).
- **S16** — `waiver_expiry` must parse as ISO-8601 UTC AND be in the future.

For every runnable spec regardless of certification (smoke + warn + strict):

- **S17** — Bundle file at canonical path must exist and parse.
- **S18** — `harness_pass` must be `True`.
- **S19** — Every `*_ref` declared in the bundle must resolve to a real file under the repo root AND hash-verify against `run_info.artifacts[].sha256`. (This is the *declared-ref* hash check; it applies in ALL modes per amendment 5.)

### 5.4 Output format

`shared_verifier --mode strict` writes:

- `artifacts/certification/apps_e2e/verifier_report.json` — per-app rows with `certification_level`, violations, mode, exit_code.
- Stdout console summary table (per-app row, one line each).
- Stderr machine-readable JSONL on violations (one line per violation, for CI log-parsers).

---

## 6. Required-Receipt Resolver

A new pure function `required_receipts(spec: AppSpec) -> list[ReceiptRequirement]` lives in `tools/certification/apps_e2e/required_receipts.py` (replacing today's `_required_runtime_refs`). Each entry is a `(ref_field, artifact_kind)` tuple so the verifier can check both *presence on disk* AND *manifest-declared kind*.

```
required_receipts(spec) ⊇ [
  ("runtime_route_contract_ref",     ArtifactKind.route_contract),       # always
  ("runtime_l1_plan_ref",            ArtifactKind.l1_plan_contract),     # always
  ("runtime_exit_disposition_ref",   ArtifactKind.exit_x3_disposition),  # always (exit_required implicit)
  ("otel_or_runtime_trace_ref",      {ArtifactKind.otel_trace, ArtifactKind.runtime_adg_trace}),  # if otel_required (set = either kind acceptable)
]

# L3 path
if spec.expected_l3_path == "RAN":
    add ("runtime_l3_receipt_ref",   ArtifactKind.l3_runtime_receipt)
elif spec.expected_l3_path == "BYPASSED":
    add ("runtime_l3_bypass_ref",    ArtifactKind.l3_bypass_receipt)
# UNKNOWN expected_l3_path under certification is a strict-mode failure (S12)

# L6 exhaust (separate from Exit)
if effective_l6_exhaust_required(spec):
    add ("runtime_exhaust_ref",      ArtifactKind.runtime_exhaust_bundle)

# Optional spine surfaces
if effective_c0_required(spec):          add ("runtime_c0_receipt_ref",       ArtifactKind.c0_grounding_receipt)
if effective_prompt_assembly_required:   add ("runtime_prompt_assembly_ref",  ArtifactKind.prompt_assembly_receipt)
if effective_l2_required(spec):          add ("runtime_l2_artifact_ref",      ArtifactKind.l2_sealed_artifact)
if effective_uwg_required(spec):         add ("runtime_uwg_receipt_ref",      ArtifactKind.uwg_durable_write_receipt)
if spec.expects_static_dag:              add ("static_dag_ref",               ArtifactKind.static_l3_dag_proof)
```

**Invariants**:

- Exit and Exhaust are **separately gated**. `runtime_exit_disposition_ref` is implicit-always. `runtime_exhaust_ref` only when `l6_exhaust_required=True`.
- The L3 receipt-or-bypass split is **mutually exclusive**. Strict mode fails if both are set in the bundle, or if neither is set when `expected_l3_path ∈ {RAN, BYPASSED}` is asserted by the spec.
- A spec asserting `expected_l3_path=RAN` but emitting only `runtime_l3_bypass_ref` (or vice versa) is a strict-mode failure (`l3_path_mismatch`).

## 6.5 Artifact Kind Enum + Manifest Contract

A new module `tools/certification/apps_e2e/artifact_kinds.py` defines:

```python
class ArtifactKind(StrEnum):
    route_contract               = "route_contract"
    l1_plan_contract             = "l1_plan_contract"
    l3_runtime_receipt           = "l3_runtime_receipt"
    l3_bypass_receipt            = "l3_bypass_receipt"
    exit_x3_disposition          = "exit_x3_disposition"
    runtime_exhaust_bundle       = "runtime_exhaust_bundle"
    otel_trace                   = "otel_trace"
    runtime_adg_trace            = "runtime_adg_trace"
    c0_grounding_receipt         = "c0_grounding_receipt"
    prompt_assembly_receipt      = "prompt_assembly_receipt"
    l2_sealed_artifact           = "l2_sealed_artifact"
    uwg_durable_write_receipt    = "uwg_durable_write_receipt"
    static_l3_dag_proof          = "static_l3_dag_proof"
    runtime_intake               = "runtime_intake"
    run_log                      = "run_log"
    adg_snapshot                 = "adg_snapshot"
    verifier_result              = "verifier_result"
```

**Manifest contract** (every `*_ref` appearing in a bundle must have a matching artifact-manifest row):

```jsonc
{
  "ref_field":     "runtime_route_contract_ref",   // bundle field that points here
  "artifact_kind": "route_contract",                // ArtifactKind value
  "path":          "artifacts/.../route_contract.json",
  "sha256":        "<64-hex>",
  "run_id":        "<bundle.run_id>"               // MUST equal bundle.run_id
}
```

**Strict-mode artifact-kind rules** (subset of S3, S9, S10):

- A required `*_ref` whose manifest entry has the wrong `artifact_kind` for its slot is a failure (`artifact_kind_mismatch`).
- A required `*_ref` declared in the bundle but absent from the artifact manifest is a failure (`ref_missing_from_manifest`).
- Two manifest rows with the same `artifact_kind` value where the kind is single-occurrence (route_contract, l1_plan_contract, l3_runtime_receipt, l3_bypass_receipt, exit_x3_disposition, runtime_exhaust_bundle) is a failure (`duplicate_artifact_kind`).
- A manifest row whose `run_id` does not equal `bundle.run_id` is a failure (`manifest_run_id_drift`).
- The `otel_or_runtime_trace_ref` slot accepts EITHER `artifact_kind=otel_trace` OR `artifact_kind=runtime_adg_trace`. Any other kind in that slot is a failure.

**Smoke-mode artifact-kind rules**:

- Smoke does NOT require all expected receipts. It only checks that every `*_ref` that IS declared in the bundle resolves on disk AND matches the declared sha256. Manifest-completeness is not checked.

Consumer of the manifest contract: existing `proof_bundle.py` builds `run_info.artifacts[]` today; W1.3 extends each row with `artifact_kind` (computed by the stage collectors) and `ref_field` (computed by the bundle assembler).

---

## 7. Files to Create / Modify (file-grain)

### 7.1 NEW

| File | Purpose | Est. LOC |
|---|---|---:|
| `tools/certification/apps_e2e/certification_levels.py` | `CertificationLevel` enum + `compute_level(bundle, spec, viols) -> CertificationLevel` | ~80 |
| `tools/certification/apps_e2e/verifier_modes.py` | `VerifierMode` enum + dispatch helpers | ~50 |
| `tools/certification/apps_e2e/required_receipts.py` | Pure `required_receipts(spec) -> list[str]` resolver | ~70 |
| `tools/certification/apps_e2e/waivers.py` | Waiver parser + `is_waiver_valid(spec, now_utc) -> bool` | ~60 |
| `ops_scripts/ci/check_apps_e2e_bundle_emission.py` | Gate 1 — ALL runnable apps emit valid bundles | ~80 |
| `ops_scripts/ci/check_apps_e2e_spine_certification.py` | Gate 2 — strict mode across all `certification_required` apps | ~100 |
| `tests/unit/apps_e2e/test_certification_levels.py` | Unit tests for level computation | ~120 |
| `tests/unit/apps_e2e/test_verifier_modes.py` | Unit tests — smoke / warn / strict mode dispatch | ~120 |
| `tests/unit/apps_e2e/test_required_receipts.py` | Unit tests for receipt resolver | ~80 |
| `tests/unit/apps_e2e/test_waivers.py` | Unit tests for waiver validity + expiry | ~60 |
| `tests/runtime/test_apps_e2e_two_gate_negative_controls.py` | Negative-control suite (§9) | ~250 |
| `.cursor/schemas/apps_e2e_verifier_report.schema.json` | Schema for `verifier_report.json` | ~80 |

### 7.2 MODIFY

| File | Change |
|---|---|
| `tools/certification/apps_e2e/app_specs.py` | Add 11 new AppSpec fields + per-app values for the 8 specs |
| `tools/certification/apps_e2e/shared_verifier.py` | Replace `_required_runtime_refs` with `required_receipts`; add `--mode` CLI; integrate level computation |
| `tools/certification/apps_e2e/proof_bundle.py` | Emit `certification_level` and `runtime_mode_classification` fields into bundle |
| `tools/certification/apps_e2e/matrix_builder.py` | Add `certification_level` column + level-breakdown totals |
| `.cursor/schemas/apps_e2e_proof_bundle.schema.json` | Add `certification_level` (enum) + `runtime_mode_classification` |
| `.cursor/schemas/apps_e2e_matrix.schema.json` | Add per-row `certification_level` + level-breakdown totals |
| `ops_scripts/ci/check_apps_e2e_harness.py` | Deprecation shim — delegates to `bundle_emission` gate; emits warning |
| `.github/workflows/apps-e2e-harness-nightly.yml` | Add 2 new jobs: `bundle-emission` (must pass) + `spine-certification` (informational until critical mass) |
| `docs/runbooks/apps_e2e_harness.md` | Document modes, levels, two-gate model, waivers |
| `tools/certification/apps_e2e/live_sweep_findings.yaml` | Add `certification_level` per app |
| `AGENTS.md` | Update Notion writeback table to include `certification_level` if a new Notion column lands |

### 7.3 NOT modified (forbidden in this plan)

- Any `agentic_core/**` module — spine integration of the 6 non-rg apps is out of scope.
- Any `apps_*/**` source — the 6 apps' actual spine wiring is app-owner work, not harness work.
- The shared dry-run helper `apps_shared/_apps_e2e_dry_run.py` — it remains a smoke-only path; we add verifier rules to **reject** dry-run-mode bundles in strict mode.

---

## 8. Per-App Gap Table (current state, 2026-05-02)

Status column shows the level the app earns under §3 with the post-implementation verifier. "Today's gate" shows the level under the existing `check_apps_e2e_harness` gate (which doesn't distinguish levels — everything passing is just "OK").

### 8.1 apps_rg (REFERENCE)

| Field | Value |
|---|---|
| Today's gate | OK |
| Post-impl level | **`SPINE_COMPLETE_CERTIFIED`** |
| Enters agentic_core? | **Yes** — full live run via `--target-company` / `--auto-research-tavily` |
| Missing receipts | none (success=true, gaps=0) |
| Required minimal scenario | already certifiable; this is the reference app |
| Dry-run only smoke? | n/a — apps_rg has no `--apps-e2e-dry-run` short-circuit; the live entrypoint is what runs |
| Files needing modification | none for certification; `app_specs.py` row gets `certification_required=True, expected_execution_form=ExecutionForm.SINGLE_STEP, expected_l3_path=L3Path.BYPASSED` (matches current emitted contract — RouteContract is emitted but no DAG-driven L3 receipt; an L3 bypass receipt represents the outcome) |

### 8.2 apps_eval

| Field | Value |
|---|---|
| Today's gate | OK (misleading) |
| Post-impl level | **`FAILS_CLOSED_WITH_GAPS`** (strict-mode FAIL) |
| Enters agentic_core? | **No** — `--apps-e2e-dry-run` short-circuits before `_adg_bootstrap()` |
| Missing receipts | RouteContract, L1PlanContract, L3 receipt-or-bypass, ExitReviewPacket, RuntimeExhaustBundle, OTEL trace, C0 receipt, PA receipt, L2 sealed artifact (9 gaps) |
| Required minimal scenario | A no-op governed run that emits: synthesize a single eval scoring task → C0 grounding (synthetic) → PA → L2 (deterministic execution) → Exit X3 disposition → RuntimeExhaustBundle → OTEL trace. `expected_execution_form=SINGLE_STEP, expected_l3_path=BYPASSED` is acceptable. |
| Dry-run only smoke? | **Yes**, currently. Under strict mode, dry-run is rejected. |
| Files needing modification | `apps_eval/__main__.py` (replace dry-run short-circuit OR keep it but add a `--apps-e2e-min-cert` path that engages spine); likely `apps_eval/integrations/eval_ingress_runner.py` to call `agentic_core` runtime; possibly `agentic_core/L3_orchestration/` to register an eval bypass route if not present; new fixture under `apps_eval/tests/fixtures/cert_smoke/` |

### 8.3 apps_exec

| Field | Value |
|---|---|
| Today's gate | OK (misleading) |
| Post-impl level | **`FAILS_CLOSED_WITH_GAPS`** (strict-mode FAIL) |
| Enters agentic_core? | **No** — dry-run short-circuit |
| Missing receipts | RouteContract, L1PlanContract, L3 receipt-or-bypass, ExitReviewPacket, RuntimeExhaustBundle, OTEL trace, PA receipt, L2 sealed artifact (8 gaps; no C0 expected) |
| Required minimal scenario | Brief-assembly run that emits: synthesize a single brief target → PA → L2 (assembly engine) → Exit X3 disposition → RuntimeExhaustBundle → OTEL trace. `expected_execution_form=SINGLE_STEP, expected_l3_path=BYPASSED`. |
| Dry-run only smoke? | Yes |
| Files needing modification | `apps_exec/__main__.py`; `apps_exec/integrations/exec_ingress_runner.py`; `apps_exec/engines/brief_assembly_engine.py` to gain a deterministic-fixture path; new fixture under `apps_exec/tests/fixtures/cert_smoke/` |

### 8.4 apps_lic

| Field | Value |
|---|---|
| Today's gate | OK (misleading) |
| Post-impl level | **`FAILS_CLOSED_WITH_GAPS`** (strict-mode FAIL) |
| Enters agentic_core? | **No** — dry-run short-circuit |
| Missing receipts | RouteContract, L1PlanContract, L3 receipt (canonical L3 DAG ships at `apps_lic/config/l3_dag.yaml`), ExitReviewPacket, RuntimeExhaustBundle, OTEL trace, C0 receipt, PA receipt, L2 sealed artifact (9 gaps) |
| Required minimal scenario | One-HOP managed workflow: profile_analysis only (HOP1) → C0 → PA → L2 → L3 receipt threading the static DAG hash → Exit X3 disposition → RuntimeExhaustBundle → OTEL trace. `expected_execution_form=MANAGED_WORKFLOW, expected_l3_path=RAN`. |
| Dry-run only smoke? | Yes |
| Files needing modification | `apps_lic/__main__.py`; `apps_lic/tools/run_workflow_lic.py` to gain a `--single-hop profile_analysis` minimal-cert path; `apps_lic/integrations/governed_lic_run.py`; possibly `agentic_core/L3_orchestration/` to bind the apps_lic L3 DAG hash; new fixture under `apps_lic/tests/fixtures/cert_smoke/HOP1.yaml` |

### 8.5 apps_qna

| Field | Value |
|---|---|
| Today's gate | OK |
| Post-impl level | **`WAIVED_NOT_RUNTIME_APP`** (recommended) OR **`FAILS_CLOSED_WITH_GAPS`** if not waived |
| Enters agentic_core? | **No** — pack-builder/router app, not a managed-workflow app |
| Missing receipts | If certified: RouteContract, L1PlanContract, L3 bypass receipt, Exit X3 disposition, RuntimeExhaustBundle, OTEL trace (6 gaps) |
| Required minimal scenario | If certified: `build --config <fixture> --dry-run` already produces a real exit=0; needs the spine to emit a RouteContract, an L3 bypass receipt (`expected_l3_path=BYPASSED`), Exit X3 disposition, OTEL trace. `expected_execution_form=TERMINAL_SHORTCIRCUIT`. |
| Dry-run only smoke? | apps_qna's own `--dry-run` is a real run (NOT a short-circuit) — it executes the pack-builder honestly. |
| Files needing modification | **Recommended path: waive.** Add `certification_required=False, waiver_reason="Pack-builder/router app — not a governed-runtime workflow", waiver_owner="<owner>", waiver_expiry="2027-01-01T00:00:00Z"`. **Alternative:** add a no-op governed route emission in `apps_qna/router/pack_loader.py` to thread a `TERMINAL_SHORTCIRCUIT` RouteContract + L3 bypass receipt. |

### 8.6 apps_research

| Field | Value |
|---|---|
| Today's gate | OK (misleading) |
| Post-impl level | **`FAILS_CLOSED_WITH_GAPS`** (strict-mode FAIL) |
| Enters agentic_core? | **No** — dry-run short-circuit |
| Missing receipts | RouteContract, L1PlanContract, L3 bypass, ExitReviewPacket, RuntimeExhaustBundle, OTEL trace, C0 receipt, PA receipt, L2 sealed artifact (9 gaps) |
| Required minimal scenario | Single-target deterministic research run with `--auto-research-tavily=false` and a fixture company brief: → C0 (synthetic) → PA → L2 (research engine) → Exit X3 disposition → RuntimeExhaustBundle → OTEL trace. `expected_execution_form=SINGLE_STEP, expected_l3_path=BYPASSED`. `fixture_data_used=True` is permitted in strict mode (per amendment 3). |
| Dry-run only smoke? | Yes |
| Files needing modification | `apps_research/__main__.py`; `apps_research/integrations/governed_research_run.py`; `apps_research/engines/company_brief_engine.py` deterministic-fixture path; new fixture under `apps_research/tests/fixtures/cert_smoke/` |

### 8.7 apps_rfp

| Field | Value |
|---|---|
| Today's gate | OK (misleading) |
| Post-impl level | **`FAILS_CLOSED_WITH_GAPS`** (strict-mode FAIL) |
| Enters agentic_core? | **No** — dry-run short-circuit |
| Missing receipts | RouteContract, L1PlanContract, L3 bypass, ExitReviewPacket, RuntimeExhaustBundle, OTEL trace, C0 receipt, PA receipt, L2 sealed artifact (9 gaps) |
| Required minimal scenario | Single-template proposal-assembly run with a fixture RFP brief: → C0 → PA → L2 (assembly engine) → Exit X3 disposition → RuntimeExhaustBundle → OTEL trace. `expected_execution_form=SINGLE_STEP, expected_l3_path=BYPASSED`. `fixture_data_used=True` is permitted in strict mode (per amendment 3). |
| Dry-run only smoke? | Yes |
| Files needing modification | `apps_rfp/__main__.py`; `apps_rfp/integrations/governed_rfp_run.py`; `apps_rfp/engines/proposal_assembly_engine.py`; new fixture under `apps_rfp/tests/fixtures/cert_smoke/` |

### 8.8 apps_underwriting_ai

| Field | Value |
|---|---|
| Today's gate | n/a (skeleton — bundle emitter classifies `runtime_mode=skeleton_only`) |
| Post-impl level | **`WAIVED_SKELETON`** |
| Enters agentic_core? | n/a — no `__init__.py` / `__main__.py` |
| Files needing modification | `app_specs.py` row gains `runnable=False, waiver_reason="No __init__.py / __main__.py — skeleton-only at this snapshot", waiver_owner="<owner>", waiver_expiry="<TBD>"` |

### 8.9 Strict-mode pass/fail today vs after this plan

```
apps_rg                      SPINE_COMPLETE_CERTIFIED  ✅ pass
apps_qna (if waived)         WAIVED_NOT_RUNTIME_APP    ✅ pass
apps_underwriting_ai         WAIVED_SKELETON           ✅ pass
apps_eval                    FAILS_CLOSED_WITH_GAPS    ❌ FAIL
apps_exec                    FAILS_CLOSED_WITH_GAPS    ❌ FAIL
apps_lic                     FAILS_CLOSED_WITH_GAPS    ❌ FAIL
apps_research                FAILS_CLOSED_WITH_GAPS    ❌ FAIL
apps_rfp                     FAILS_CLOSED_WITH_GAPS    ❌ FAIL
                                                       -----
                                                       5 fails
```

**This is the desired post-implementation state.** Bundle-emission gate is green; spine-certification gate is red and stays red until each of the 5 apps emits real spine receipts.

---

## 9. Negative-Control Plan (anti-fabrication suite)

Lives in `tests/runtime/test_apps_e2e_two_gate_negative_controls.py`. Each test mutates a real bundle (the apps_rg one — currently the only `SPINE_COMPLETE_CERTIFIED` baseline), runs the strict-mode verifier against the mutated copy, and asserts a specific violation fires. **All tests must pass for strict mode to be trusted.**

| ID | Mutation | Expected violation rule_id | Required outcome |
|---|---|---|---|
| N1 | Delete `run_id` from bundle | `bundle_missing_required_field` | strict FAIL |
| N2 | Set `run_id` = "fabricated-not-matching-spine" | `run_id_mismatch_with_route_contract` | strict FAIL |
| N3 | Delete `runtime_route_contract_ref` | `required_receipt_missing` (rule_id=`route_contract_missing`) | strict FAIL |
| N4 | Make `runtime_route_contract_ref` point to two RouteContract files in `run_info.artifacts` | `duplicate_route_contract` | strict FAIL |
| N5 | Delete `runtime_exit_disposition_ref` | `required_receipt_missing` (rule_id=`exit_x3_missing`) | strict FAIL |
| N6 | Bundle declares `runtime_l3_receipt_ref` but `static_dag_ref` is missing OR `static_dag_sha256` does not appear inside the L3 receipt's `static_dag_hash` field | `runtime_l3_static_dag_hash_unbound` | strict FAIL |
| N7 | Synthesize an `l6_observability_ref` whose timestamp precedes `runtime_exit_disposition_ref.finished_at_utc` | `l6_emitted_before_exit` | strict FAIL |
| N8 | Replace OTEL trace contents with synthetic spans (set `synthetic_trace_detected=true`) but keep `success=true` | `synthetic_trace_in_certified_bundle` | strict FAIL |
| N9 | Set `success=true` and `blocking_gaps=["something"]` simultaneously | `success_true_with_nonempty_gaps` | strict FAIL |
| N10 | Set `runtime_mode_classification="dry_run_short_circuit"` while `success=true` | `runtime_mode_not_in_approved_live_modes` | strict FAIL |
| N11 | Tamper with one byte of a referenced receipt file (sha256 in run_info no longer matches file) | `artifact_sha256_mismatch` | strict FAIL |
| N12 | Set `app_overlay_authority_status="VIOLATION"` (apps_* emitted a spine artifact) | `apps_overlay_authority_violation` | strict FAIL |
| N13 | AppSpec sets `runnable=False` without waiver triple | `waiver_incomplete` | strict FAIL |
| N14 | AppSpec waiver_expiry = 2020-01-01T00:00:00Z | `waiver_expired` | strict FAIL |
| N15 | AppSpec sets `expected_execution_form="UNKNOWN"` while `certification_required=True` | `execution_form_unknown_under_certification` | strict FAIL |
| N16 | Bundle declares `success=True` but `certification_level` recomputes to `FAILS_CLOSED_WITH_GAPS` (or any non-`SPINE_COMPLETE_CERTIFIED` level) | `success_true_but_level_weaker_than_certified` | strict FAIL |
| N17 | Bundle has `fixture_data_used=True` AND `runtime_mode_classification="live_run"` AND all required receipts present + hash-verified | (none) | strict **PASS** — deterministic input is allowed when real runtime engaged |
| N18 | Bundle has `fixture_runtime_mode=True` (fake runtime, not just fake input) | `fixture_runtime_mode_in_certified_bundle` | strict FAIL |
| N19 | A required `*_ref` is declared in the bundle but absent from `run_info.artifacts[]` (no manifest row) | `ref_missing_from_manifest` | strict FAIL |
| N20 | Two manifest rows both have `artifact_kind=route_contract` (single-occurrence kind) | `duplicate_artifact_kind` | strict FAIL |

A 21st **positive-control** test asserts the **unmutated** apps_rg bundle passes strict mode. Without that, a bug that fails-everything would look indistinguishable from correct anti-fabrication. (N17 is also a positive control — it must PASS, not fail — but it tests a specific invariant about fixture-data legitimacy.)

**Total**: 19 negative-must-fail + 2 positive-must-pass + 1 final-positive-control (re-run unmutated baseline at end of suite) = 22 logical tests, realised as 23 pytest tests (N6 has two sub-tests: missing-static-ref and mismatched-hash).

**Implementation note (2026-05-02 07:05 UTC)**: All 20 negative controls have been implemented. N2 / N4 / N6 / N7 — initially deferred for follow-up — were closed in a single commit alongside the four matching strict-mode rules (`run_id_mismatch_with_route_contract`, `duplicate_route_contract`, `runtime_l3_static_dag_hash_unbound`, `l6_emitted_before_exit`). Synthetic fixtures for the L3-RAN path (which `apps_rg` baseline cannot exercise because it is L3-bypassed) live inline in `tests/runtime/test_apps_e2e_two_gate_negative_controls.py` with `_negative_control_fixture: true` sentinels. No real artifacts were mutated; all temp files are written under `artifacts/_neg_control_*/` and unlinked in `finally` blocks.

---

## 10. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|---|---|---|---:|---|---|
| **W1 — Schema + Data Model** | W1.1, W1.2, W1.3 | Add 12 AppSpec fields (incl. `expected_l3_path`); add `CertificationLevel` enum + `ArtifactKind` enum; update bundle + matrix schemas; add `ref_field` + `artifact_kind` to manifest rows | ~9k | Todo | Existing `apps_e2e_matrix.json` regenerates with `certification_level` per row; manifest rows carry `artifact_kind`; no data loss |
| **W2 — Verifier Modes + Receipt Resolver** | W2.1, W2.2, W2.3, W2.4 | Author `verifier_modes.py`, `required_receipts.py`, `waivers.py`, `certification_levels.py`; integrate into `shared_verifier.py` with `--mode` CLI | ~10k | Todo | Smoke / warn / strict modes work against current bundles; smoke=PASS, warn=PASS, strict=FAIL on 5 apps |
| W3 — Negative Controls | W3.1, W3.2 | Author full negative-control suite covering N1–N20; positive controls pass; every named mutation fires its rule_id | ~7k | **DONE** | 23 tests green: full N1–N20 coverage + N17 positive control + unmutated baseline run twice (start + end) |
| **W4 — Two CI Gates** | W4.1, W4.2, W4.3 | New `check_apps_e2e_bundle_emission.py` (must pass); new `check_apps_e2e_spine_certification.py` (informational at first); deprecation-shim of old gate | ~5k | Todo | Bundle-emission gate green on a clean checkout; spine-certification gate red with 5 explicit failures |
| **W5 — Runbook + Workflow** | W5.1, W5.2 | Update `docs/runbooks/apps_e2e_harness.md` and `.github/workflows/apps-e2e-harness-nightly.yml` to add 2 new jobs | ~3k | Todo | PR run distinguishes smoke pass from cert pass in workflow logs |
| **W6 — Per-App Spec Tightening** | W6.1, W6.2 | Set `certification_required` and `expected_execution_form` per app; add waiver block for apps_qna + apps_underwriting_ai | ~4k | Todo | Strict-mode output exactly matches §8.9 |

## 11. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---:|---|
| W1.1 | Add 11 AppSpec fields | `app_specs.py`, schemas | Backward compat via `effective_*_required` | ~3k | Todo |
| W1.2 | `CertificationLevel` enum + bundle field | `certification_levels.py`, `proof_bundle.py` | Level computation must be pure | ~2k | Todo |
| W1.3 | Matrix schema + builder update | `matrix_builder.py`, `apps_e2e_matrix.schema.json` | Level-breakdown totals | ~3k | Todo |
| W2.1 | Receipt resolver | `required_receipts.py` | MANAGED_WORKFLOW vs BYPASS XOR | ~3k | Todo |
| W2.2 | Waiver parser | `waivers.py` | ISO-8601 expiry, pure function | ~2k | Todo |
| W2.3 | Verifier mode dispatch | `verifier_modes.py`, `shared_verifier.py` | `--mode` required, no default | ~3k | Todo |
| W2.4 | Verifier integration + CLI | `shared_verifier.py` | Stable JSON output for CI | ~2k | Todo |
| W3.1 | Negative-control framework | `test_apps_e2e_two_gate_negative_controls.py` | Tempfile mutation pattern (do not mutate real artifacts) | ~3k | Todo |
| W3.2 | 15 negative + 1 positive control | same file | Each mutation must produce exactly the expected violation, no extras | ~3k | Todo |
| W4.1 | Bundle-emission gate | `check_apps_e2e_bundle_emission.py` | Schema-level only; tolerates honest gaps | ~2k | Todo |
| W4.2 | Spine-certification gate | `check_apps_e2e_spine_certification.py` | Returns 1 on any strict-mode violation | ~2k | Todo |
| W4.3 | Old-gate deprecation shim | `check_apps_e2e_harness.py` | Emits warning, delegates to bundle_emission | ~1k | Todo |
| W5.1 | Runbook | `docs/runbooks/apps_e2e_harness.md` | Two-gate semantics + level table | ~2k | Todo |
| W5.2 | Workflow | `.github/workflows/apps-e2e-harness-nightly.yml` | Two new jobs; spine-cert is `continue-on-error: true` initially | ~1k | Todo |
| W6.1 | Per-app `certification_required` + `expected_execution_form` | `app_specs.py` | Match §8 verbatim | ~2k | Todo |
| W6.2 | Waiver rows for apps_qna + apps_underwriting_ai | `app_specs.py` | Owner / expiry chosen by user | ~2k | Todo |

---

## 12. Acceptance Commands

```bash
# Bundle emission — must pass after W1-W4
python -m ops_scripts.ci.check_apps_e2e_bundle_emission                # exit 0
python -m tools.certification.apps_e2e.shared_verifier --mode smoke    # exit 0

# Warn mode — must always exit 0; emits gap diff
python -m tools.certification.apps_e2e.shared_verifier --mode warn     # exit 0
# stderr lists 5 failing apps + their gaps

# Strict mode — must FAIL with exactly the 5 expected apps after W6
python -m ops_scripts.ci.check_apps_e2e_spine_certification            # exit 1
python -m tools.certification.apps_e2e.shared_verifier --mode strict   # exit 1
# stdout lists: apps_eval, apps_exec, apps_lic, apps_research, apps_rfp as FAIL

# Negative controls
python -m pytest tests/runtime/test_apps_e2e_two_gate_negative_controls.py -q
# 16 passed (15 negative + 1 positive)

# Existing harness suites still green
python -m pytest tests/unit/apps_e2e/ tests/runtime/test_apps_e2e_*.py tests/runtime/test_agentic_core_spine_proof.py -q
```

---

## 13. Recommended Wiring Order (the 6 non-rg apps)

Order chosen to minimize spine-integration risk: simplest BYPASS apps first, MANAGED_WORKFLOW last; smallest existing surface first.

| # | App | Why this order | Estimated complexity |
|---|---|---|---|
| 1 | **apps_qna** | Recommended path is a **waiver**, not full certification. Closes the spec immediately with a waiver row. Zero spine integration needed. | Trivial (waiver only) |
| 2 | **apps_exec** | Smallest engine surface (single `brief_assembly_engine.py`); no C0 expected; BYPASS form. First app to actually engage spine. | Low |
| 3 | **apps_research** | Single `company_brief_engine.py`; needs C0 + PA + L2; BYPASS form; Tavily can be disabled by fixture. | Low-Medium |
| 4 | **apps_rfp** | Single `proposal_assembly_engine.py`; needs C0 + PA + L2; BYPASS form. Pattern reuses apps_research wiring. | Medium |
| 5 | **apps_eval** | Eval engines are evaluators (not workflows); needs C0 + PA + L2; BYPASS form. Pattern reuses prior 3. | Medium |
| 6 | **apps_lic** | MANAGED_WORKFLOW with 9 HOP stages; static L3 DAG already shipped at `apps_lic/config/l3_dag.yaml`; needs L3 receipt threading the static-DAG hash. Largest surface. | High |

Each of #2–#6 is its own follow-up plan (one slug each). This plan delivers only the gate / verifier / level / negative-control machinery so those follow-up plans have a stable target to land against.

---

## 14. Out of Scope (do not expand)

- Actually wiring the 6 non-rg apps to the spine — each is its own follow-up plan tracked separately.
- Modifying `agentic_core/**` to add new emitters or hooks — current spine surface is sufficient for `apps_rg` and any future app that follows the same pattern.
- Removing or weakening `--apps-e2e-dry-run` — it remains a valid smoke-only path; strict mode rejects it.
- Adding new MCP servers.
- Replacing OTEL or runtime-ADG infrastructure.
- Per-app one-off harness scripts (explicit anti-goal — same as parent plan).

---

## 15. ADG_GRAPH_LAYER_EVIDENCE

Greenfield gating layer — minimal ADG cross-reference required (no refactoring of existing layered code):

- **`mv_hotspot_centrality`** (consult W2.3): identify `tools/certification/apps_e2e/shared_verifier.py` centrality before extending it — it is the canonical entry point and must remain so.
- **`v_p0_apps_direct_infra`**: the negative-control N12 (`apps_overlay_authority_violation`) machine-checks this view — strict mode fails if any apps_* node emits a spine artifact, complementing the static P-view.
- **Semantic edges (`emits_side_effect`, `writes_to`)**: not extended in this plan; existing edges are sufficient for the overlay-authority check.

No further graph-layer evidence required because this plan adds only NEW gating modules and tests; it does not refactor existing layered code.

## 16. ADG_HOTSPOT_REPORT

Not applicable — plan adds gating modules and a negative-control suite; no hotspot-driven refactoring is in scope.

---

## 17. Unresolved Questions

1. **Owner for the apps_qna + apps_underwriting_ai waivers** — needs human decision. Recommended placeholder: the owner of the app's last commit, with a 2027-01-01 expiry.
2. **`expected_execution_form` for apps_rg** — bundle currently emits a RouteContract whose internal `execution_form` field reads `BYPASS` (legacy upstream value). AppSpec sets `expected_execution_form=SINGLE_STEP, expected_l3_path=BYPASSED`. The verifier must NOT propagate the legacy upstream string to AppSpec; `BYPASS` is no longer a valid AppSpec value (per amendment 2). If a future change moves apps_rg to MANAGED_WORKFLOW, AppSpec must update in the same PR.
3. **Timeline for promoting `spine-certification` gate to required CI** — parent question. Recommended: informational (`continue-on-error: true`) until ≥ 4 of 5 currently-failing apps are certified, then flip to required.
4. **`runtime_mode_classification` enumeration** — exact set of allowed values: `live_run`, `dry_run_short_circuit`, `standalone_orchestrator_pre_spine`, `mock_*`, `fixture_*`, `skeleton_only`. Strict mode allows only `live_run`. To be locked in W2.4.

---

**End of plan. No code in this response.**
