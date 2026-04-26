========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 06_L6_Shadow_Evaluation_System_Learning
Canonical file: 06_Shadow_Evaluation_System_Learning_exec.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: 06_Shadow_Evaluation_System_Learning_exec.md
Owner summary: L6 after-runtime shadow evaluation and future-run learning only. Owns sealed exhaust ingest, evaluation, calibration, RCA, proposals, gauntlet, and UWG promotion requests.

GLOBAL NO-OVERLAP LAW
- 00A L5 owns governance certification evidence, not live runtime dispositions and not durable write admission.
- 00B L4/UWG owns durable system-of-record state and durable write admission, not planning, routing, retrieval, execution, Exit disposition, or L6 learning mechanics.
- 00C Runtime Gates owns G01-G29 current-run GateVerdict law, not final Exit X3 aggregation and not L5 certification evidence.
- 00X owns traceability and no-loss mapping only.
- 01 Intake owns request envelope validation and identity/session/tenant baseline only.
- 02 L1 owns advisory interpretation and planning only.
- 03 L0/L3 owns deterministic route selection and optional workflow orchestration only.
- C0 owns retrieval/evidence contracts only.
- PA owns prompt packet construction only.
- 04 L2 owns bounded execution and sealing only.
- 05 Exit owns current-run checkout aggregation and exactly one X3 disposition only.
- 06 L6 owns completed-run evaluation, RCA, and future-run learning proposals only.
- 99 owns proof harnesses only; it does not own runtime behavior.

REFERENCE POINTERS
- Cross-cutting governance/certification evidence: 00A_L5_Governance_Safety/
- Durable state and Universal Write Gateway: 00B_L4_State_Archive_and_UWG/
- Current-run reusable gate mesh: 00C_Runtime_Gates_Current_Run_Mesh/
- Traceability and zero-loss proof: 00X_Requirements_Traceability_and_No_Loss_Map.md
- End-to-end runtime proof harness: 99_End_to_End_Runtime_Proof_and_Acceptance/
========================================================================================================================

# 06 — Shadow Evaluation → System Learning (v5, Normative)

> **Companion to the v4 diagram** (`06_Shadow_Evaluation_System_Learning_v4.md`).
> The v4 file remains the canonical visual; v5 adds the **normative prose**,
> **measurable KPIs**, and **contract references** that industry peers
> (OpenAI Model Spec, Anthropic Constitution, Google Agent Eval pillars)
> pair with their diagrams. v5 does **not** change the v4 architecture.

- **Status**: draft
- **Supersedes**: none (v4 is retained; v5 augments)
- **Cross-refs**: `agentic_process_mapping_v33.md §6`, ADR-023 (runtime HITL), ADR-036 (trace grader), ADR-041 (hallucination vs. groundedness), `.windsurf/rules/evaluation-promotion-gate.md`, `.windsurf/rules/judge-calibration-cadence.md`

---

## 0. Why this file exists

The v4 diagram defines *what* the Night-Shift/Board-Meeting architecture is
(ingest → evaluate → RCA → promote). Implementers still need four things the
diagram cannot carry:

1. **Normative language** — which behaviors are MUST, SHOULD, MAY.
2. **Measurable KPIs** — so "the eval pipeline is healthy" is falsifiable.
3. **Contract references** — which engines and rules own each step.
4. **Invariant expansions** — precise statements of Observer Law, UWG Ink Path,
   Eval-Before-Learning firewall, No-Silent-Promote, and No-Partial-Bypass.

Industry peers ship this layer: OpenAI Model Spec / Evals docs pair diagrams
with normative behavior; Anthropic's Constitution is prose + rubric; Google's
"methodical agent evaluation" is explicitly a 4-pillar written contract.

---

## 1. Normative invariants (RFC-2119)

### 1.1 Observer Law (Phase 6A — INGEST)
- The ingest path **MUST** only read from runtime surfaces (OTel spans, artifacts, HITL packets, exit decisions).
- The ingest path **MUST NOT** write to L4 state, publish to BUS U, or mutate any live policy, prompt, rubric, or baseline.
- Ingest implementations **SHOULD** preserve lineage identifiers (`trace_id`, `run_id`, `replay_key`) on every normalized record.
- Owner: `engines/telemetry_consumer.py`, `engines/historical_ingestion_orchestrator.py`, `adapters/otel_telemetry_store_adapter.py`.
- Invariant checker: `engines/surface_isolation_validator.py`, `engines/stage_barrier_enforcer.py`.

### 1.2 Eval-Before-Learning firewall (Phase 6B precedes 6C/6D)
- No synthesis (6C) or promotion (6D) step **MAY** execute against raw ingest without a completed 6B evaluation record.
- The firewall **MUST** be deterministic and replay-verifiable.
- Rationale: meta-learning amplifies; if evaluation is bypassed, recursive degradation is an accepted architectural risk — so bypass is forbidden.

### 1.3 Rubric integrity
- Rubrics **MUST** be content-addressed (rubric_hash = SHA-256 of canonicalized YAML).
- Rubric upgrades **MUST** bump `version` and MUST be re-calibrated against the golden set before promotion.
- Judge outputs **MUST** allow `Unknown` ("give the LLM a way out", per Anthropic).
- Owner: `config/judges/rubrics.yaml`, `config/judges/trace_rubric.yaml`, `system_learning/rubrics/registry.py` (new in G2).

### 1.4 UWG Sole Ink Path (Phase 6D)
- Only `engines/l4_state_writer.py` **MAY** write to the canonical L4 store.
- Every write **MUST** carry: `proposal_id`, `gauntlet_receipt`, `content_hash`, `signer_identity`.
- Silent promotions (writes without a gauntlet receipt) are a CI failure.

### 1.5 No-Partial-Bypass
- If *any* stage (6A/6B/6C/6D) fails for a proposal, the proposal **MUST** be rejected as a whole. Partial promotion (e.g., "prompt accepted, rubric held") is forbidden without an explicit ADR that scopes the exception.

### 1.6 Future-run only
- Learning signals **MUST NOT** rescue the completed run. They update BUS U surfaces consumed at `run_start` of the next run.

---

## 2. Measurable KPIs

Each KPI has a canonical source, a calculation, and a threshold. "Healthy"
means every KPI is green simultaneously over a rolling 7-day window.

| KPI | Phase | Calculation | Green | Yellow | Red | Owner |
|---|---|---|:---:|:---:|:---:|---|
| Trace-ingest freshness | 6A | max(age of newest ingested span) in minutes | ≤ 10 | ≤ 60 | > 60 | `telemetry_consumer` |
| Eval coverage of runs | 6B | pct of last-24h runs with a completed eval record | ≥ 98% | ≥ 90% | < 90% | `outcome_evaluation_engine`, `trajectory_evaluation_engine` |
| Judge unknown-budget compliance | 6B | pct of judge invocations within their rubric `unknown_budget` | ≥ 95% | ≥ 85% | < 85% | consensus judges |
| Judge-human κ (calibration freshness) | 6B (S2D) | max age of latest κ computation per rubric in days | ≤ 7 | ≤ 30 | > 30 | `human_calibration_engine` (future: `judge_calibration_watchdog` per G8) |
| RCA-to-proposal lead time | 6C | p95(hours from incident close to proposal emit) | ≤ 24 | ≤ 72 | > 72 | `rca_engine`, `rule_drafting_engine` |
| Gauntlet false-promote rate | 6D (S4A/S4B) | count of promotions later reverted / total promotions | ≤ 1% | ≤ 3% | > 3% | `approval_gauntlet_engine` |
| UWG ink-path uniqueness | 6D (S4C) | count of non-`l4_state_writer` writers detected in L4 | = 0 | — | > 0 (any) | `l4_audit_reader` |
| Replay divergence localization | 6D (S4A) | pct of failed replays where divergence scorer pinpoints a span | ≥ 90% | ≥ 70% | < 70% | `trajectory_divergence_scorer` (new in G4) |
| Eval-freshness on write | 6D (S4B) | pct of L4 writes whose gating eval is within TTL | = 100% | — | < 100% (any) | `eval_freshness_gate` (new in G7) |
| Exemplar-hit rate | cross-phase | pct of plans that consulted `trajectory_exemplar_store` and used a hit | ≥ 20% | ≥ 5% | < 5% | new in G6 |
| Saturation watch | 6B | pct of capability evals that have been static ≥ 30 days | ≤ 10% | ≤ 25% | > 25% | saturation detector (existing plan GAP-11) |

Dashboard expected location: `config/dashboards/system_learning.json` (to be
created by existing plan W5 or a follow-up; not in this plan's scope).

---

## 3. Contract references (authoritative modules per v4 step)

| v4 step | Primary module(s) | Notes |
|---|---|---|
| S1A gather exhaust | `engines/telemetry_consumer.py`, `engines/historical_ingestion_orchestrator.py`, `engines/historical_backfill_engine.py`, `engines/prompt_execution_tracer.py`, `adapters/otel_telemetry_store_adapter.py` | Observer-law enforced by S1C |
| S1B normalize evidence | `engines/trace_feature_extractor.py`, `engines/meta_learning_bus.py` (content-addressed inbox) | Lineage preserved |
| S1C observer law | `engines/surface_isolation_validator.py`, `engines/stage_barrier_enforcer.py`, `invariants/` | Hard-fails on mutation attempt |
| S2A outcome evals | `engines/outcome_evaluation_engine.py`, `engines/offline_healing_outcome_evaluator.py` | Consumes `rubrics.yaml` |
| S2B trajectory evals | `engines/trajectory_evaluation_engine.py`, `engines/trace_feature_extractor.py` | Consumes `trace_rubric.yaml` |
| S2C governance regression | `engines/g_gate_regression_checker.py`, `engines/prompt_drift_detector.py`, `engines/shadow_drift_analyzer.py` | |
| S2D human calibration | `engines/human_calibration_engine.py`, `engines/hitl_decision_logger.py` | κ ≥ 0.6 gate per rubric |
| S3A signal fusion | `engines/signal_aggregator_engine.py`, `engines/signal_grouping_engine.py`, `engines/meta_learning_bus.py` | BUS P + BUS T |
| S3B incident RCA | `engines/rca_engine.py`, `engines/rca_cluster_engine.py`, `engines/pattern_analysis_engine.py` | |
| S3C rule drafting | `engines/rule_drafting_engine.py`, `engines/l1_model_proposer.py`, `engines/l5_policy_proposer.py`, `engines/retrieval_profile_proposal.py`, `engines/rag_proposer.py` | Proposal-only |
| S4A gauntlet | `engines/approval_gauntlet_engine.py`, `engines/gauntlet_gate.py`, `engines/deterministic_replay_engine.py`, `engines/replay_validator.py`, `engines/retrieval_profile_replay_check.py` | Shadow-replay primary surface |
| S4B approve/reject | `pipelines/approval_gate_impl.py`, `pipelines/approval_gates.py`, `engines/system_learning_admission_gate.py` | Write-time eval-freshness added in G7 |
| S4C UWG master clerk | `engines/l4_state_writer.py`, `engines/l4_audit_reader.py`, `engines/l4_version_store.py` | Sole ink path |
| S4D ledger proof | `engines/meta_learning_replay_binding.py`, `engines/meta_learning_state_digest.py`, `engines/faiss_startup_integrity.py` | Audit chain hashes |

---

## 4. Relationship to industry references

| Topic | Source | How v5 incorporates |
|---|---|---|
| Evals as the steering wheel | OpenAI Evaluation Best Practices | §1.2 firewall + §2 KPI `eval_coverage_of_runs` |
| Rubric as versioned artifact | Anthropic Constitutional AI / RLAIF | §1.3 content-addressed rubric; G2 registry |
| Outcome + trajectory + UX + safety 4-pillar | Google "methodical agent evaluation" | §2 KPIs cover outcome (trace-ingest, eval coverage), trajectory (divergence localization), governance (ink-path uniqueness, eval-freshness) |
| Trace-first debugging | OpenAI Trace Grading | Already in v4 (6A S1B + 6D S4D); v5 promotes ingest freshness to a KPI |
| Deterministic replay primitives | Sakura / arXiv 2505.17716 | G4 divergence scorer + G6 exemplar store (this plan's B1/D1) |
| Capability vs. regression taxonomy | Anthropic demystifying evals | Already in `rubrics.yaml eval_taxonomy`; v5 cites it |
| Saturation watch | Anthropic demystifying evals, step 7 | §2 `saturation_watch` KPI |

---

## 5. Compatibility with v4

- All v4 boxes (6A/6B/6C/6D with S1A–S4D steps) remain canonical.
- v5 adds normative language + KPIs + module references; it does not rename or re-shape boxes.
- Future edits to v5 MUST keep the v4 diagram consistent. If a v4 shape change is needed, v4 is edited first and v5 re-aligns.

---

## 6. How to update this file

- KPI thresholds are tuned via the existing `shadow-learning-bestpractice-gap-7b3e4c.md` saturation detector (its GAP-11 wave), not by editing this file directly.
- Invariants (§1) are *not* tuned — changing them requires an ADR.
- Contract references (§3) are refreshed automatically when a module moves; if a module is renamed, update this file in the same commit.
