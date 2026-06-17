# apps_* Domain Contract — Implementation Status Report

> **Status**: Waves 1–3 + W7 partial **DELIVERED**. Waves 4–6 + W7 remainder + W8 **DEFERRED** with visible hooks.
> **Plan**: `.claude/plans/apps-domain-contract-fortknox-c4d8e2.md`
> **Discovery**: `docs/reference/apps_domain_contract_discovery.md`
> **Date**: 2026-05-01

This report documents what the current pass delivered, what it proved, and
what remains.

---

## 1. What's done

### W1 — Shared `AppDomainContract` schema (Phase 1) — ✅ COMPLETE

| File | Role |
|---|---|
| `agentic_core/L4_state/contracts/app_domain.py` | 13 frozen dataclass records: `AppDomainContractRecord`, `AppInputContractRecord`, `AppOutputSchemaRecord`, `AppEvalRubricRecord`, `AppThresholdProfileRecord`, `AppGraderRosterRecord`, `AppRetrievalProfileRecord`, `AppPromptProfileRecord`, `AppCapabilityProfileRecord`, `AppRouteProfileRecord`, `AppOrchestrationProfileRecord`, `AppFixtureRecord`, `AppNegativeControlRecord` + building blocks (`ScoreDimension`, `TaskClassEntry`) + closed vocabularies + `AppDomainContractError` |
| `agentic_core/L4_state/contracts/app_domain_lookup.py` | `InMemoryAppDomainStore` (read tier) + `UnknownAppContractError` / `DeprecatedAppContractError` / `DraftAppContractError` (fail-closed) |
| `agentic_core/L4_state/contracts/__init__.py` | Re-exports for `from agentic_core.L4_state.contracts import AppDomainContractRecord, ...` |

**Invariants encoded in the schema**:
- Every record is `frozen=True`, carries `schema_version` + `deterministic_digest`
- `app_id` MUST start with `"apps_"`
- `owner_surface == app_id` enforced
- `status ∈ {draft, active, deprecated}`
- Active contracts MUST have ≥1 task_class and ≥1 negative_control_ref
- `ScoreDimension.grader_type ∈ {deterministic, llm_as_judge, hybrid}`
- `ScoreDimension.weight ∈ [0, 1]`; `min_required_score ∈ [0, 1] ∪ {-1}`
- Duplicate `dimension_id` within a rubric is rejected
- `AppOutputSchemaRecord.output_type` / `AppRetrievalProfileRecord.freshness_class` / `AppCapabilityProfileRecord.side_effect_class` / `AppFixtureRecord.fixture_type` all drawn from closed vocabularies
- `AppThresholdProfileRecord` enforces per-dimension minimums ∈ [0, 1]
- `AppGraderRosterRecord` requires at least one grader of any kind

### W3 — UWG registration (Phase 3) — ✅ COMPLETE

| File | Role |
|---|---|
| `agentic_core/L4_state/uwg/durable_write_gateway.py` | Extended `ALLOWED_OPERATIONS` with `app_domain_contract_register` (one-line surgical edit; zero blast radius on existing behavior) |
| `agentic_core/L4_state/uwg/app_domain_registration.py` | `AppDomainContractBundle`, `register_bundle(bundle)`, `RegistrationReceipt`. Registration builds one `StateDiff` per record, wraps in a `CommitRequest` with `source_surface="Exit"` (preserves UWG invariant), submits via `DurableWriteGateway.commit()`, hydrates the read tier on accept. |
| `agentic_core/L4_state/uwg/app_domain_loader.py` | YAML → `AppDomainContractBundle` parser (`load_bundle_from_dir`, `discover_app_contract_dirs`). Used by the CLI registrar. |
| `agentic_core/L4_state/uwg/__init__.py` | Re-exports |

**Author-Gate decision recorded** (§P3.1): **synthetic-Exit pseudo-run** chosen over extending `NON_AUTHORIZED_SOURCES` exemption. Rationale: keeps the UWG `source_surface=="Exit"` invariant pure. Registration pretends to be an Exit commit whose `cleared_exit_review_packet_ref` carries the deterministic bundle digest.

### W2 — Per-app YAML contracts (Phase 2) — ✅ ALL 8 APPS

| App | Layout | Size | Notes |
|---|---|---|---|
| `apps_rg` | 14 hand-authored YAMLs | 15 records | Full domain specificity per user spec: factual_grounding, role_alignment, ats_readability, executive_positioning, specificity, concision, format_compliance, no_fabrication + 2 golden fixtures + 2 negative controls (fabricated_employer, unsupported_metric) |
| `apps_lic` | 14 hand-authored YAMLs | 16 records | Full domain specificity: audience_fit, personalization_integrity, offer_clarity, response_likelihood, brevity_and_channel_fit, compliance, sequence_coherence, brand_voice, no_fake_personalization, no_sensitive_targeting + 2 golden fixtures + 3 negative controls (fake_personalization, sensitive_targeting, channel_length) |
| `apps_eval` | 14 generated YAMLs | 14 records | self-eval task_class with grader_calibration, rubric_consistency, taxonomy_correctness, threshold_alignment, no_self_contradiction, reporting_completeness |
| `apps_exec` | 14 generated YAMLs | 14 records | brief_assembly with exec_signal_density, factual_grounding, concision, priority_ordering, no_boilerplate, decision_clarity |
| `apps_research` | 14 generated YAMLs | 14 records | company_brief with factual_grounding, source_quality, freshness, completeness, balance, concision, no_speculation |
| `apps_rfp` | 14 generated YAMLs | 15 records | rfp_response with requirement_coverage, factual_grounding, compliance_with_rfp_constraints, competitive_positioning, win_theme_alignment, no_fabricated_credentials, pricing_integrity |
| `apps_qna` | 14 generated YAMLs | 14 records | qna_pack_build (filled the pre-existing policy gap) with route_fit, factual_grounding, de_duplication, coverage, freshness, no_paste_of_forbidden_content |
| `apps_underwriting_ai` | 14 generated YAMLs | 15 records | underwriting_decision at `status=draft` (TODO_FAILING_TEST — stub app) with evidence_sufficiency, feature_derivation_correctness, policy_compliance, explainability, fairness |

**Total records registered**: 117 StateDiffs across 8 apps.

Generator at `tools/apps_proof/generate_compact_app_contracts.py` — compact declarative spec → 14 YAML files per app. Re-runnable. apps_rg and apps_lic YAMLs are hand-authored and NOT regenerated (per user's named-exemplar requirement).

### W7 (partial) — Tests — ✅ 39 tests passing

| File | Count | Coverage |
|---|---|---|
| `tests/_apps_contract/test_app_domain_schema.py` | 28 tests | Every record's `__post_init__` invariants; closed-vocabulary rejection; digest determinism |
| `tests/_apps_contract/test_app_domain_uwg_registration.py` | 11 tests | Direct-L4-write rejection (`apps_rg` source_surface blocked); registration produces UWGCommitReceipt; digests stable; L4 records carry deterministic_digest; deprecated / draft resolution fail-closed; **full 8-app E2E registration sweep**; `apps_underwriting_ai` draft status enforced |

`pytest tests/_apps_contract/` → **59 passed** (39 new + 20 pre-existing platform contract tests).

### CLI tools — ✅ DELIVERED

- `python -m tools.apps_proof.register_app_domain_contracts --app all` → registers all apps through UWG, prints per-app + summary outcomes
- `python -m tools.apps_proof.register_app_domain_contracts --app apps_rg` → single-app registration
- `python -m tools.apps_proof.validate_app_domain_contracts --app all` → dry-run validation (no UWG submission)
- `python -m tools.apps_proof.generate_compact_app_contracts` → regenerate compact YAMLs for the 6 non-exemplar apps

Current dry-run sweep: **`Summary: accepted=8 blocked=0 total_state_diffs=117`**

---

## 2. What's deferred — explicit handoff for the next pass

The following waves were NOT delivered in this pass. Each has visible hooks
in the current code or is clearly isolated so continuation is safe.

### W4 — Runtime resolution (RouteContract + ingress migration) — ⏸ DEFERRED

**Scope**: Extend `RouteContract` / `V15RouteContract` with `app_id`, `task_class`, `domain_contract_ref`, `rubric_ref`, `threshold_profile_ref`, `grader_roster_ref`, `retrieval_profile_ref`, `prompt_profile_ref`, `capability_profile_ref`. New `agentic_core/L0_routing/app_domain_resolver.py` that reads `get_default_app_domain_store()` at L0 dispatch and injects refs. Migrate 8 ingress runners to stop direct YAML reads.

**Why deferred**: RouteContract is a high-fan-in central dependency (see discovery §ADG_HOTSPOT). Blast-radius of extending its schema touches C0, Prompt Assembly, L2 executor, Exit pipeline, and every downstream consumer. Proper SR_PLAN for W4 entry required.

**Handoff hook**: `InMemoryAppDomainStore.get_contract(app_id, task_class)` is ready and tested. The resolver is a thin wrapper around it.

### W5 — Exit evaluation consumption — ⏸ DEFERRED

**Scope**: Extend `ExitReviewPacket` + `X3CommitRequestPacket` with app-specific refs. New `agentic_core/L3_orchestration/exit_eval/v6/app_specific_evaluator.py` that resolves `rubric_ref`/`threshold_profile_ref`/`grader_roster_ref` from L4 and runs per-dimension scoring with UNKNOWN fail-closed semantics. Hook into X1/X2/X3 stages.

**Why deferred**: Depends on W4 (RouteContract must carry refs before Exit can pull them). ExitReviewPacket is a frozen dataclass whose field set is replay-key-sensitive.

**Handoff hook**: The `AppEvalRubricRecord.score_dimensions[i].fail_closed_if_unknown` field is already there; the evaluator just consumes it.

### W6 — OTEL app.* attributes + proof bundle — ⏸ DEFERRED

**Scope**: Emit `app.id`, `app.task_class`, `app.domain_contract_ref`, `app.domain_contract_digest`, `app.rubric_ref`, etc. on L0/L2/Exit spans. Extend `apps_shared/proof/proof_runner.py` proof bundle schema with the app-contract refs.

**Why deferred**: Must land after W4+W5 so the attributes actually carry resolved values.

### W7 (remainder) — Runtime + Exit + E2E proof tests — ⏸ DEFERRED

**Scope**: `test_app_domain_runtime_resolution.py` (proves RouteContract carries app refs), `test_app_domain_exit_evaluation.py` (proves UNKNOWN fail-closed + per-dimension minimums), `test_app_domain_e2e_proof.py` (8 apps × 2 golden + 8 × 2 negatives = 32 parametrized E2E cases).

**Why deferred**: Depends on W4+W5+W6.

### W8 — Acceptance sweep — ⏸ DEFERRED

Depends on all above.

---

## 3. Acceptance-bar status (from user spec)

| # | Criterion | Status |
|---|---|---|
| 1 | Every apps_* has a domain contract | ✅ 8/8 |
| 2 | Every active task_class has input, output, rubric, threshold, grader, retrieval, prompt, capability, fixture, negative control | ✅ 8/8 apps; apps_underwriting_ai draft-status by design |
| 3 | Domain contracts are registered into L4 through UWG | ✅ 117 StateDiffs all accepted |
| 4 | Runtime resolves app-specific contracts from L4, not directly from app YAML | ⏸ W4 — store ready, resolver + ingress migration pending |
| 5 | Exit consumes app-specific rubric and thresholds | ⏸ W5 |
| 6 | X3 disposition references app-specific eval results | ⏸ W5 |
| 7 | L6 receives app-specific evaluation refs in runtime exhaust | ⏸ W6 |
| 8 | OTEL spans include app-specific contract refs and digests | ⏸ W6 |
| 9 | E2E proof bundle shows the app contract governed runtime behavior | ⏸ W6+W7 |
| 10 | Negative controls fail for expected app-specific reasons | 🔵 Declared in YAML (`expected_failure_dimension` + `expected_failure_reason` in every `AppNegativeControlRecord`). Enforcement pending W5. |
| 11 | Direct app-to-L4 writes are impossible and tested | ✅ `TestAppCannotWriteDirectly::test_app_surface_rejected_as_commit_source` passes |
| 12 | Missing app-specific rubric or threshold fails closed | ✅ `UnknownAppContractError` raised; schema rejects missing required fields |
| 13 | UNKNOWN required app-specific eval dimension never passes | 🔵 Declared (`ScoreDimension.fail_closed_if_unknown=True` enforced in schema). Runtime enforcement pending W5. |

**Current acceptance**: 4 / 13 hard-green + 2 soft-green (declared-but-runtime-pending). Remaining 7 items are downstream of W4/W5/W6 and cannot be delivered without them.

---

## 4. Files created / modified

### New (delivered this pass)

**Schema & read tier**:
- `agentic_core/L4_state/contracts/app_domain.py`
- `agentic_core/L4_state/contracts/app_domain_lookup.py`

**UWG registration**:
- `agentic_core/L4_state/uwg/app_domain_registration.py`
- `agentic_core/L4_state/uwg/app_domain_loader.py`

**CLI + generator**:
- `tools/apps_proof/register_app_domain_contracts.py`
- `tools/apps_proof/validate_app_domain_contracts.py`
- `tools/apps_proof/generate_compact_app_contracts.py`

**Per-app YAMLs** (8 apps × 14 files each = 112 files):
- `apps_rg/config/domain_contract/*.yaml` (hand-authored)
- `apps_lic/config/domain_contract/*.yaml` (hand-authored)
- `apps_eval/config/domain_contract/*.yaml` (generated)
- `apps_exec/config/domain_contract/*.yaml` (generated)
- `apps_research/config/domain_contract/*.yaml` (generated)
- `apps_rfp/config/domain_contract/*.yaml` (generated)
- `apps_qna/config/domain_contract/*.yaml` (generated)
- `apps_underwriting_ai/config/domain_contract/*.yaml` (generated, status=draft)

**Tests**:
- `tests/_apps_contract/test_app_domain_schema.py`
- `tests/_apps_contract/test_app_domain_uwg_registration.py`

**Documentation**:
- `docs/reference/apps_domain_contract_discovery.md`
- `docs/reference/apps_domain_contract_implementation_status.md` (this file)
- `.claude/plans/apps-domain-contract-fortknox-c4d8e2.md`

### Modified

- `agentic_core/L4_state/contracts/__init__.py` — re-exports for new app-domain types
- `agentic_core/L4_state/uwg/__init__.py` — re-exports for registration + loader
- `agentic_core/L4_state/uwg/durable_write_gateway.py` — added `app_domain_contract_register` to `ALLOWED_OPERATIONS`

**None of the modifications touched pre-existing behavior paths.** All changes are additive.

---

## 5. Commands (runnable today)

```powershell
# 1. Validate all app contracts (dry-run; no UWG submission)
.venv\Scripts\python.exe -m tools.apps_proof.validate_app_domain_contracts --app all

# 2. Register all app contracts through UWG into L4
.venv\Scripts\python.exe -m tools.apps_proof.register_app_domain_contracts --app all

# 3. Single app
.venv\Scripts\python.exe -m tools.apps_proof.register_app_domain_contracts --app apps_rg

# 4. Regenerate the 6 non-exemplar apps' YAMLs (if spec changes)
.venv\Scripts\python.exe -m tools.apps_proof.generate_compact_app_contracts

# 5. Schema + registration unit tests (39 tests)
.venv\Scripts\python.exe -m pytest tests/_apps_contract/test_app_domain_schema.py tests/_apps_contract/test_app_domain_uwg_registration.py -v

# 6. Full _apps_contract directory (59 tests — includes pre-existing platform tests)
.venv\Scripts\python.exe -m pytest tests/_apps_contract/ -v
```

---

## 6. Known gaps & follow-ups

1. **Runtime resolution not yet wired**: `apps_<name>/integrations/*_ingress_runner.py` still read their own YAML directly. W4 addresses this. Until W4 lands, the L4 records are registered but not consulted at runtime.

2. **Exit evaluation not yet app-specific**: X1/X2/X3 in `agentic_core/L3_orchestration/exit_eval/v6/pipeline.py` still use generic V6 verdicts. Per-app rubric + threshold consumption is W5.

3. **OTEL spans not yet carrying `app.*` attributes**: W6.

4. **`apps_underwriting_ai` is explicit stub**: registered at `status=draft`; requires a full implementation pass before it can be promoted to `active`. Captured by `test_apps_underwriting_ai_is_draft` (intentionally passing as a TODO_FAILING_TEST sentinel).

5. **`apps_qna` task_class ambiguity** (from discovery §8): this pass chose `qna_pack_build` as the single task_class. If the runtime later demonstrates need for a separate `qna_route_select` or `qna_paste_set` task_class, extend `task_classes.yaml` accordingly. No code change required.

6. **Pre-existing router_l4_uwg ledger writer warning** (`no such table: events`): emitted by the closed-loop router helper when the ledger SQLite schema is not initialized. Fail-soft in UWG — does NOT affect registration outcomes. Not introduced by this pass.

7. **`apps_eval/config/rubrics/` still exists**: the original per-app rubrics in that folder were the seed for `apps_<name>/config/domain_contract/eval_rubrics.yaml`. During transition (W4+W5 rollout) both locations coexist. Deprecation of the old location is a post-W5 step; `test_rubric_dual_location_drift` is still TODO.

---

## 7. Constitutional compliance

- **§22 ADG graph-layer evidence**: Plan has `ADG_GRAPH_LAYER_EVIDENCE` section citing `mv_graph_chokepoint_bridges`, `v_p0_apps_direct_infra`, etc.
- **§23 ADG canonical invariants**: Hotspot report has archetype + 5-surface cross-reference; L4 is treated as canonical truth (this pack does not introduce any other "authority").
- **§28 SQLite over grep**: This pass used `code_search` (ADG MCP-backed) for all dependency questions — no grep for structural analysis.
- **§31 SSOT folder routing**: New files land in canonical folders — `agentic_core/L4_state/contracts/`, `agentic_core/L4_state/uwg/`, `tools/apps_proof/`, `tests/_apps_contract/`, `apps_<name>/config/domain_contract/`. Zero violations.
- **§15 exception handling**: No bare `except:` introduced. Custom exception hierarchy (`AppDomainContractError`, `AppDomainLookupError`, `UnknownAppContractError`, `DeprecatedAppContractError`, `DraftAppContractError`) for precise catch-and-handle.
- **§19 mode separation**: Phase 0 was pure discovery (no edits); Phases 1+ were implementation only after user approval. Honored.
- **Plan SSOT**: Plan at `.claude/plans/apps-domain-contract-fortknox-c4d8e2.md`; discovery at `docs/reference/apps_domain_contract_discovery.md`; this status at `docs/reference/apps_domain_contract_implementation_status.md`. No plan-file drift.

---

## 8. Provenance stamp

```
ADG Provenance: backend=sqlite, snapshot=artifacts/adg/adg_indexed_<latest>.sqlite
Plan-ref: apps-domain-contract-fortknox-c4d8e2
Tests green: tests/_apps_contract/ → 59 passed
CLI sweep: accepted=8 blocked=0 total_state_diffs=117
```
