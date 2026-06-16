---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\rtc-w2b-consensus-jury-rewrite-9a4c71.md'
original_relative_path: '_archive\\2026-05\\rtc-w2b-consensus-jury-rewrite-9a4c71.md'
source_sha256: 9928f8a766b2b0608442a60b3bfb22996faa687a03c6fcb9b912198827cb5b1b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# RTC W2b Rewrite — Consensus-Jury LLM-as-Judge

- **Plan ID**: `rtc-w2b-consensus-jury-rewrite-9a4c71`
- **Supersedes**: `.cursor/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md` (provider-ladder design flaw)
- **Base branch**: `rtc-w2b-live-provider-allow-proof-clean` @ `faf0a0b785`
- **Working branch**: `rtc-w2b-consensus-jury-rewrite`
- **Tier**: T3 (cross-layer — L0 model registry + certification-path code + tests + CI)
- **Status**: DRAFT — awaiting execution
- **Author**: Cursor Agent, 2026-05-01
- **User directive**: 2026-05-01 11:59 UTC — "start working now but update the base models to these three — the ones in the SSOT are old"

---

## 1. Why this plan supersedes W2b-b24f8e

The original W2b (`rtc-w2b-live-provider-allow-proof-b24f8e.md`) shipped with an architecturally defective provider ladder:

| Defect | Original W2b | Correct per SSOT |
|---|---|---|
| Provider ladder | `local_qwen → anthropic_haiku` | Consensus jury (per user directive) |
| Anthropic as tier | Used as veto fallback | Consensus juror only (per `model_registry.py:100-110`) |
| Env var names | `LOCAL_QWEN_ENDPOINT`, `LOCAL_QWEN_MODEL` | `VLLM_BASE_URL`, `VLLM_MODEL_NAME` (SSOT) |
| Model ids | Hardcoded strings in LLMJudgeVeto | Imported from `agentic_core.L0_routing.config.model_registry` |
| Stale models | `claude-3-haiku-20240307` (2024), `gpt-4o` (old), `gemini-2.5-pro` (old) | User's 2026 pins: `gpt-5.5`, `claude-sonnet-4-6`, `gemini-3.1-pro-preview` |

Root cause: W2b was implemented without an Author-Gate. The provider choices were made by Cursor Agent in isolation without consulting the L0 routing SSOT.

### Evidence from 2026-05-01 Scenario A execution

- Scenario A against `Qwen/Qwen2.5-32B-Instruct-AWQ` produced `veto_outcome=UNKNOWN` on the integrated canonical pair
- Fail-closed worked correctly; no attestation forged
- User diagnosis: single-model judging is the wrong pattern for certification-grade evaluation; consensus is required

---

## 2. Target architecture

### 2.1 Judge fleet

| Juror | Registry env var | New default | API key env | Cost (rough) |
|---|---|---|---|---|
| OpenAI | `OPENAI_MODEL` | `gpt-5.5` | `OPENAI_API_KEY` | ~$0.003/verdict |
| Anthropic | `ANTHROPIC_MODEL` | `claude-sonnet-4-6` (unchanged) | `ANTHROPIC_API_KEY` | ~$0.008/verdict |
| Google | `GEMINI_PRO_MODEL` | `gemini-3.1-pro-preview` | `GOOGLE_API_KEY` | ~$0.010/verdict |
| **Optional 4th** | n/a (local) | `QWEN_LOCAL_MODEL_ID` via `USE_CERT_JURY_QWEN=1` | vLLM endpoint up | $0 |

Total per certification run (3 jurors): ~$0.02. Quarterly certification cadence: ~$0.08/year. Economically trivial.

### 2.2 Aggregation

- **Input**: canonical safe-reuse pair → 3 parallel juror prompts with shared rubric
- **Per-juror output**: one of `{SAFE, UNSAFE_DIFFERENT_INTENT, UNSAFE_POLICY_DRIFT, UNCERTAIN, ERROR}`
- **Aggregate allow rule**: strict majority SAFE
  - 3/3 SAFE → `allow=True`, mode=`unanimous`
  - 2/3 SAFE → `allow=True`, mode=`majority`, dissent recorded
  - 1/3 SAFE → `allow=False`, reason=`CONSENSUS_NO_MAJORITY`
  - 0/3 SAFE → `allow=False`, reason=`UNANIMOUS_NOT_SAFE`
- **Partial failure (any juror returns ERROR)**: `allow=False`, reason=`CONSENSUS_INCOMPLETE` — fail-closed
- **Optional 4th Qwen juror active**: majority = 3/4 (already implemented via `consensus_majority_threshold()`)

### 2.3 Attestation extension (schema v2)

Current `live_provider_attestation.json` (schema v1) records single provider. Schema v2 extends with `per_juror` array:

```json
{
  "schema_version": 2,
  "aggregate": {
    "allow": true,
    "aggregation_mode": "majority",
    "safe_count": 2,
    "dissent_count": 1
  },
  "per_juror": [
    {"juror_id": "openai_gpt_5_5", "verdict": "SAFE", "confidence": 0.92, "latency_ms": 1240, "raw_response_sha256": "..."},
    {"juror_id": "anthropic_claude-sonnet-4-6", "verdict": "SAFE", "confidence": 0.88, "latency_ms": 2100, "raw_response_sha256": "..."},
    {"juror_id": "google_gemini-3.1-pro-preview", "verdict": "UNCERTAIN", "confidence": 0.40, "latency_ms": 3500, "raw_response_sha256": "..."}
  ],
  "canonical_pair_hash_sha256": "...",
  "rubric_hash_sha256": "..."
}
```

---

## 3. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W2bR-1 | R1.1, R1.2 | SSOT registry refresh | ~6k | User-approved pins land as registry defaults | Todo | `model_registry.py` defaults match user pins; tests updated; no other consumers break |
| W2bR-2 | R2.1, R2.2, R2.3 | Consensus juror infrastructure | ~18k | Three API keys provisioned; parallel-call pattern using `asyncio.gather` or sequential fallback | Todo | `ConsensusVeto` class returns aggregated verdict; per-juror provenance captured |
| W2bR-3 | R3.1, R3.2, R3.3 | Probe + composer + verifier rewrite | ~14k | Schema v2 attestation payload; composer rejection matrix extends to consensus reasons | Todo | Probes emit schema-v2 attestation; composer accepts ≥2/3 SAFE; verifier rejection matrix covers all failure modes |
| W2bR-4 | R4.1, R4.2 | Tests + CI workflow | ~12k | Mock-based unit tests; live integration tests behind `@pytest.mark.integration` | Todo | ≥20 new test cases pass; CI `consensus_jury_acceptance` job dispatchable |
| W2bR-5 | R5.1, R5.2 | Evidence + report + cleanup | ~6k | Old W2b branches archived; Scenario naming updated (no A/B/C; verdict is aggregate) | Todo | W2b report explains the rewrite; supersession note in old plan |

---

## 4. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| R1.1 | Registry default refresh | `agentic_core/L0_routing/config/model_registry.py` (3 defaults); `tests/agentic_core/L0_routing/test_model_registry.py` (update assertions) | Registry is L0 SSOT; changing defaults affects consensus_validator and any other consumer that uses the default | 3k | Todo |
| R1.2 | Registry consumer audit | `grep_search`-driven check of every file that imports `OPENAI_MODEL_ID`, `ANTHROPIC_MODEL_ID`, `GEMINI_PRO_MODEL_ID`; spot-check no hardcoded overrides assume old values | Audit-only, no code changes unless consumer breaks | 3k | Todo |
| R2.1 | ConsensusVeto class | New `tools/certification/safety/consensus_veto.py`; reuses rubric-loading from `llm_judge_veto.py` | Parallel API calls need timeout bounding; JSON parsing must handle all three families' formatting quirks | 8k | Todo |
| R2.2 | LLMJudgeVeto multi-provider refactor | `tools/certification/safety/llm_judge_veto.py`: keep class for single-juror path; add `_call_openai()`, `_call_anthropic()`, `_call_gemini()` all reading from registry | `_call_anthropic_haiku()` removed entirely; `anthropic_haiku` provider string deprecated | 6k | Todo |
| R2.3 | Attestation schema v2 | `tools/certification/evidence/_live_provider_attestation.py`: add `per_juror`, `aggregate` fields; keep v1 read-back compat for old artifacts | Schema versioning needs explicit migration path for any in-flight v1 artifacts | 4k | Todo |
| R3.1 | Probe rewrite | `probe_live_provider_readiness.py`: checks all 3 API keys; `probe_live_provider_rubric_stability.py`: 3 parallel juror stability; `probe_integrated_runtime_safe_reuse.py`: uses ConsensusVeto | Old `LOCAL_QWEN_*` env vars deprecated; migration note in probe docstrings | 6k | Todo |
| R3.2 | Composer update | `scripts/compose_semantic_cache_subclaims.py`: `APPROVED_PROVIDERS` → `APPROVED_JURY`; 7-condition → 9-condition gate (add consensus_mode, per-juror-not-empty checks) | Rejection matrix must distinguish CONSENSUS_NO_MAJORITY from CONSENSUS_INCOMPLETE | 5k | Todo |
| R3.3 | Verifier update | `ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py`: 8-row matrix → 11-row matrix (3 new reject reasons: `CONSENSUS_NO_MAJORITY`, `CONSENSUS_INCOMPLETE`, `UNAPPROVED_JUROR`) | Old 8 reasons stay for backward compat with any hypothetical v1 attestations in flight | 3k | Todo |
| R4.1 | Unit tests | `tests/runtime/test_consensus_veto.py` (new, 12 cases); update `test_llm_judge_veto*.py`, `test_live_provider_*.py` to drop anthropic_haiku references | Mocking parallel API calls needs `asyncio.gather` patching | 8k | Todo |
| R4.2 | CI workflow update | `.github/workflows/runtime-certification.yml`: rename `live_provider_acceptance` → `consensus_jury_acceptance`; env-probe checks all 3 API keys not just one | Secrets must be added to the repo before the manual-dispatch job can succeed | 4k | Todo |
| R5.1 | W2b report rewrite | `docs/architecture/integrated_runtime_w2b_report.md`: supersession note; new architecture narrative; operator runbook updates | Preserve honest-non-green framing for any single-juror UNCERTAIN scenarios | 3k | Todo |
| R5.2 | Cleanup | Archive old W2b branches; supersede b24f8e plan; emit NEXT_STEP for Qwen-4th-juror activation | Keep git history clean; no force-push outside this branch | 3k | Todo |

---

## 5. Non-Negotiables

- [ ] **N1.** All juror model ids imported from `agentic_core.L0_routing.config.model_registry` — NO hardcoding in W2b code.
- [ ] **N2.** No `anthropic_haiku` provider string anywhere in certification code after R2.2. `grep_search -r "anthropic_haiku"` must return zero hits in `tools/certification/`, `scripts/compose_*`, `ops_scripts/ci/verify_*`, `tests/runtime/`.
- [ ] **N3.** No `LOCAL_QWEN_ENDPOINT` or `LOCAL_QWEN_MODEL` env-var references after R2.2. Replaced by `VLLM_BASE_URL` / `VLLM_MODEL_NAME` (SSOT).
- [ ] **N4.** `mock_safe` remains strictly excluded from certification — the `LLMJUDGEVETO_APPROVED_MOCK_SAFE=1` bypass must produce `verdict=MOCK_NOT_CERTIFIABLE` and block attestation write.
- [ ] **N5.** Attestation is written ONLY when aggregate `allow=True` per §2.2. No attestation for partial-failure or no-majority cases.
- [ ] **N6.** Fail-closed on any juror ERROR, timeout, or parse_fail — `allow=False` regardless of other jurors' verdicts.
- [ ] **N7.** Per-juror raw responses hashed (SHA-256) into attestation. Raw text NOT stored in attestation (privacy/compliance).

---

## 6. ADG_HOTSPOT_REPORT

This plan is primarily additive + a targeted refactor of one class. Limited hotspot surface.

| File | Role | Archetype | Layer | fan_in | Impact score | Surface |
|---|---|---|---|---|---|---|
| `tools/certification/safety/llm_judge_veto.py` | Modified: multi-provider refactor | SAFETY_GATEKEEPER | (certification support — outside L0-L6 hotspot scoring) | — | — | Security |
| `tools/certification/safety/consensus_veto.py` | New | SAFETY_GATEKEEPER | (new file — no fan-in yet) | 0 | — | Security |
| `agentic_core/L0_routing/config/model_registry.py` | Modified: 2 defaults updated | CENTRAL_DEPENDENCY | L0 | HIGH (see R1.2 audit) | Layer mult ×2.0 | Execution |
| `scripts/compose_semantic_cache_subclaims.py` | Modified: gate logic | SAFETY_GATEKEEPER | scripts (outside layered) | — | — | Security |
| `ops_scripts/ci/verify_r1b_safe_reuse_integrated_runtime.py` | Modified: rejection matrix | SAFETY_GATEKEEPER | ops_scripts | — | — | Security |

**Surface intersections**: All modified files intersect the **Security surface** (rubric-based safety judgment) and **Execution surface** (attestation is an execution artifact binding). Failure in any of these surfaces = poisoned attestation; therefore all 5 files are audit-grade.

**Zero-Loss Propagation**: A false SAFE verdict in ConsensusVeto propagates through ConsensusVeto.evaluate → VetoOrchestrator → integrated_safe_reuse_run → semantic_cache_safe_reuse_decision → attestation writer → composer gate → verifier matrix → certification acceptance. Any of the 4 fail-closed gates in that chain must catch an invalid SAFE before row 056 advances.

---

## 7. ADG_GRAPH_LAYER_EVIDENCE

Queried against `artifacts/adg/adg_indexed_<latest>.sqlite` (see per-run snapshot at `.cursor/scripts/post_cursor_agent_adg_audit.py` output).

- `mv_hotspot_centrality` (materialized view): `agentic_core.L0_routing.config.model_registry` is consumed by ≥8 modules (consensus_validator, healing_router, provider_registry, qwen_judge_provider, cascade_calibrator, anthropic_model_tier_policy, optimized_vllm_client, qwen_inference_gateway). Changing its defaults has blast radius across L0-L3.
- `mv_graph_chokepoint_bridges`: `model_registry.py` bridges `.env` (deployment-variable) to runtime model selection. Verified no P-view (v_p0_*, v_p1_*) violations on current imports.
- `mv_dependency_cone_risk`: ConsensusVeto (new) will have 0 cone risk at creation; will gain fan-in as probes + composer + verifier adopt it.
- **P-view cross-reference**: `v_p0_write_bypass_uwg` — none of the modified files write through UWG; `v_p1_mis_layered_infra` — tools/certification/ is correctly outside the L0-L6 tier per repo convention; no violations introduced.

**Semantic edges touched**:
- `flows_to` from rubric → ConsensusVeto → aggregate verdict → attestation writer
- `resolves_callsite`: `LLMJudgeVeto._call_openai`, `_call_anthropic`, `_call_gemini` resolve to external HTTP calls (external-tool boundary, verified via vector_db retrieval if debugging needed)
- `writes_to`: attestation writer writes `live_provider_attestation.json` under `artifacts/certification/integrated_runtime/c_primary_allow/` — existing well-known write path

---

## 8. Execution Sequence

1. **R1.1 first** (registry refresh — small blast radius to verify). Commit: `refactor(L0): refresh model registry defaults per 2026-05-01 fleet`.
2. **R1.2 audit** (confirm no consumer breaks). If any consumer pins an old value, add env-override shim in same commit.
3. **R2.1 + R2.3** (ConsensusVeto + schema v2). Commit: `feat(cert): ConsensusVeto class + schema-v2 attestation`.
4. **R2.2** (LLMJudgeVeto single-juror refactor). Commit: `refactor(cert): multi-provider LLMJudgeVeto, drop anthropic_haiku`.
5. **R3.1 + R3.2 + R3.3** (probes + composer + verifier). Commit: `feat(cert): W2b consensus-jury probe chain + gate matrix`.
6. **R4.1** (tests). Commit: `test(cert): W2b consensus-jury unit tests`.
7. **R4.2** (CI workflow). Commit: `ci: consensus_jury_acceptance manual-dispatch job`.
8. **R5.1 + R5.2** (docs + cleanup). Commit: `docs(cert): W2b rewrite report + supersede b24f8e plan`.

8 commits total on `rtc-w2b-consensus-jury-rewrite`. Each is self-contained and passes existing test suite at that point.

---

## 9. Stop Conditions

- **STOP if R1.1 breaks any test in `tests/agentic_core/L0_routing/`**: registry change has unexpected consumer; investigate before R1.2.
- **STOP if R2.1 requires more than `asyncio.gather` for parallel calls**: any dependency on `anthropic`, `openai`, `google.generativeai` SDK async APIs that aren't available → document and ask user.
- **STOP if R2.2 removes code referenced by a non-W2b caller**: some other module may use `LLMJudgeVeto(provider="anthropic_haiku")` — discover via `grep_search`, treat as separate refactor.
- **STOP if R3.3 rejection matrix grows beyond 11 rows**: design review needed before matrix becomes a correctness liability.
- **STOP if any commit fails pre-commit hooks**: investigate; do not `--no-verify`.

---

## 10. Open Questions (to resolve during execution, not blockers)

- **Q1**: Should the 4th Qwen juror (`USE_CERT_JURY_QWEN=1`) be enabled by default for Cursor Agent-hosted runs, or opt-in only? Default: opt-in.
- **Q2**: Does `asyncio.gather` raise when one juror times out? Need to verify each SDK's timeout behavior; may need per-juror try/except wrapping.
- **Q3**: Gemini 3.1 Pro Preview — stable API? Same request format as gemini-2.5-pro? Discover during R2.2.
- **Q4**: Should schema-v1 attestations be auto-migrated or rejected at the verifier? Default: rejected (forces fresh run under new scheme).
- **Q5**: Does the composer need a new AP for `CONSENSUS_INCOMPLETE` vs treating it as `CONSENSUS_NO_MAJORITY`? Keep distinct for audit clarity.

---

## 11. Success Metric

- [ ] RTC-REQ-056 can progress to ACCEPTED when a consensus jury run produces `aggregate.allow=True` on the integrated canonical pair
- [ ] All 11 CI gates (8 existing + 3 new) pass on the final commit
- [ ] Rubric-stability probe produces 3 juror × 3 run = 9 stable SAFE verdicts on the Apollo 11 canonical pair
- [ ] Attestation file passes schema-v2 validator
- [ ] Verifier rejection matrix rejects all 11 failure modes with correct reason codes
- [ ] No `anthropic_haiku` / `LOCAL_QWEN_*` references anywhere in certification code
- [ ] `model_registry.py` defaults match user's 2026-05-01 fleet

---

## 12. Supersession

This plan supersedes `.cursor/plans/rtc-w2b-live-provider-allow-proof-b24f8e.md`. The old plan is NOT deleted — it remains as historical record of the defective design. R5.1 adds a supersession banner to the old plan file pointing at this one.

The branches `rtc-w2b-live-provider-allow-proof-clean` and `rtc-w2b-scenario-a-local-qwen-v2` are archived (not deleted). Their commits remain as durable evidence that the W2b infrastructure worked end-to-end against a real 32B model — the design just chose the wrong provider ladder. The P2/model-id/timeout fixes from those branches are incorporated (as rebases) into the new branch's R2.1/R2.2/R3.1 phases.
