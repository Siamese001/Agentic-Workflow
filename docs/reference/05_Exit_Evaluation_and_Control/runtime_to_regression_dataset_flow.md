========================================================================================================================
MECE ALIGNMENT FULL OVERWRITE HEADER
Canonical folder: 05_Exit_Evaluation_and_Control
Canonical file: runtime_to_regression_dataset_flow.md
Overwrite mode: full-file, no-overlap, implementation-grade, source-refreshed
Source refreshed from: runtime_to_regression_dataset_flow.md
Owner summary: Exit checkout and disposition. Owns ExitReviewPacket normalization, X1 checkout checks, X2 aggregation, exactly one X3 disposition, HITL freeze/reclear, UWG handoff, response return, and runtime exhaust.

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

# Runtime → Regression Dataset Promotion Flow

**Parent**: `05_Live_Runtime_Exit_Control_&_Evaluation_v4.md`
**Closes gaps**: G3 (capability/regression tracks), G10 (runtime-to-regression pipeline)
**Date**: 2026-04-24

This spec defines the pipeline from live runtime telemetry (BUS P + BUS T) to a curated, versioned regression dataset consumed by future X1A baselines. It closes the compounding-asset loop: every production interaction either affirms, refines, or extends the golden set.

---

## 1. Why This Pipeline Exists

v3 emitted two async exhaust buses (BUS P for prefs/grades, BUS T for telem/trace) with the invariant that learning signals do not mutate the current run. v3 did not specify where those signals went next. Industry practice (Google Cloud G1) is explicit:

> The most robust test suites blend multiple techniques to generate diverse, relevant, and realistic data at scale: synthesize conversations with "dueling LLMs"; use and anonymize production data; human-in-the-loop curation — developers save valuable interactive sessions from logs or traces as permanent test cases, continuously enriching the test suite with meaningful examples.

Without this pipeline:

- Regression evals are frozen at launch and grow stale.
- Edge cases discovered in production die as one-off traces.
- Capability-track graduations (G3) have no mechanical path into regression.
- The async exhaust accumulates without producing a durable evaluation asset.

---

## 2. Pipeline Overview

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Runtime run      │───► │ BUS P / BUS T    │───► │ Candidate Pool   │───► │ Curation Gate    │
│ emits dispositio │     │ (raw exhaust)    │     │ (filtered)       │     │ (human + auto)   │
│ + dimension_vec  │     │                  │     │                  │     │                  │
│ + trajectory     │     │ - per-run row    │     │ - dedup by hash  │     │ - SME review     │
│ + track          │     │ - per-dim scores │     │ - anonymize PII  │     │ - label intent   │
│                  │     │ - full trace     │     │ - score by       │     │ - assign track   │
│                  │     │                  │     │   promotion      │     │ - assign         │
│                  │     │                  │     │   heuristic      │     │   trajectory_cls │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └─────────┬────────┘
                                                                                     │
                                                                                     ▼
                                                                          ┌──────────────────┐
                                                                          │ Golden Set       │
                                                                          │ (versioned)      │
                                                                          │                  │
                                                                          │ - capability/    │
                                                                          │ - regression/    │
                                                                          │ - adversarial/   │
                                                                          └─────────┬────────┘
                                                                                    │
                                                                                    ▼
                                                                          ┌──────────────────┐
                                                                          │ Consumed by X1A  │
                                                                          │ baselines and    │
                                                                          │ offline suites   │
                                                                          └──────────────────┘
```

All stages run **after** the runtime boundary. No stage mutates the current run.

---

## 3. Stage Specifications

### 3.1 BUS P / BUS T capture (already v3)

v4 enriches what flows onto the buses (per `grader_composition_spec.md` §7):

- **BUS P row per gate**: run_id, gate, rubric_version, composition, aggregate score, dimension_vector, reason_codes, track, trajectory_class.
- **BUS T row per run**: run_id, full trajectory (tool calls, arguments, intermediate reasoning, handoffs, outputs), environment snapshot, disposition.

Both buses are append-only. No stage downstream may edit existing rows.

### 3.2 Candidate Pool (filtered)

The raw exhaust is too noisy to feed directly into a regression suite. The candidate pool applies:

**Deduplication**
- Hash each run by `(trajectory_class, normalized_input, output_class)`.
- Collapse duplicates to a single representative with a frequency count.

**Anonymization**
- Strip PII per the repo's standard anonymization filter.
- Replace user-specific identifiers with stable placeholders (`USER_001`, `ORDER_001`).
- Runs that cannot be safely anonymized are flagged and excluded.

**Promotion heuristic — which runs are *interesting*?**

Score each run on promotion-worthiness; higher scores move to curation first:

| Signal | Weight | Rationale |
|---|---|---|
| X3B escalation (HITL reviewed) | 3.0 | Human already looked at it; highest value per minute of curation. |
| X1F adversarial failure | 2.5 | Security-relevant; regression suite must remember. |
| X1E trajectory-suspect (right answer, broken path) | 2.0 | Latent brittleness; critical for robustness. |
| `JUDGE_ABSTAINED` on any dimension | 1.5 | Calibration signal; rubric may need revision. |
| Near-miss (aggregate score within 0.05 of threshold) | 1.5 | Partial-credit signal (G7). |
| Novel trajectory_class (not in current golden set) | 1.3 | Coverage expansion. |
| `pass^k` recent dip (was ≥ 0.95, now < 0.95) | 1.8 | Drift signal; regression guard priority. |
| Routine pass on well-covered trajectory_class | 0.2 | Low signal; sample only. |

Runs with composite score ≥ threshold move to curation. Threshold is tuned to keep curation queue ≤ N/day where N is the SME team's declared capacity.

### 3.3 Curation Gate

Every candidate is reviewed by a human curator (or a calibrated auto-curator for low-risk categories). The curator:

1. **Confirms anonymization** is complete.
2. **Labels the intent**: what was the user actually trying to do?
3. **Assigns or confirms `trajectory_class`** for `pass^k` aggregation.
4. **Assigns track**:
   - `capability/` — task the system currently struggles with (hill-climb target).
   - `regression/` — task the system must continue to handle (drift-guard).
   - `adversarial/` — adversarial/security test case.
5. **Labels expected disposition and expected per-dimension scores**.
6. **Flags** any task that should be *quarantined* (too sensitive, demographically unbalanced, legally risky).

Rejected candidates are marked `curation_rejected` with reason; retained for audit, not consumed.

### 3.4 Golden Set

The golden set is the durable asset this pipeline produces.

**Structure**:

```
data/eval/
  golden/
    capability/
      <trajectory_class>/
        <case_id>.json          # input + expected output + expected dimension_vector
    regression/
      <trajectory_class>/
        <case_id>.json
    adversarial/
      <category>/               # prompt_injection, jailbreak, bias, robustness
        <case_id>.json
```

**Versioning**:
- Each addition, deletion, or material edit to a case bumps a dataset version tag.
- The golden set is consumed by X1A baselines with an explicit version pin.
- Golden-set versions are immutable once published. Corrections produce a new version.

**Graduation** (closes G3):
- When a capability-track case reaches `pass^k ≥ 0.95` over k=10 in successive weekly evaluation runs, it auto-graduates to regression.
- Graduation is recorded in the dataset changelog.

### 3.5 Consumption

Offline evaluation harnesses and runtime X1A baselines consume the golden set:

- **Capability eval runs** (offline, nightly) score the agent against `capability/`. Low pass rates are the hill-climb target.
- **Regression eval runs** (offline + pre-deploy gate) score against `regression/`. Near-100% pass rate is required; drops trigger blocks.
- **Adversarial eval runs** (offline + periodic) score against `adversarial/`. Pass rates here gate X1F policy updates.
- **Runtime X1A** loads the current regression baseline fingerprint to validate the agent's policy alignment on entry.

---

## 4. Anonymization Policy (required by pipeline, defined elsewhere)

Anonymization is not solved here — it is a dependency. Requirements this pipeline places on the anonymization layer:

- Must be **reversible** only via an SME-gated key ceremony (for audit and legal disputes).
- Must be **deterministic** per run so that duplicate detection is stable.
- Must **log what was redacted** so curators know what they're not seeing.
- Must **fail-closed**: if anonymization cannot confirm safe output, the candidate is excluded, not partially released.

---

## 5. Retention and Legal

- **BUS P / BUS T raw rows**: retained per the repo's data-retention policy. Default 90 days unless longer-retention is justified.
- **Candidate pool**: retained 30 days for re-curation opportunities.
- **Golden set**: indefinite retention (this is the compounding asset); full-history preserved.
- **Rejected candidates**: retained for audit only (metadata, not content).

---

## 6. Invariants

1. **No stage mutates the current run** — all processing is post-runtime (inherited from v3, strengthened here).
2. **No un-anonymized production data lands in the golden set** — anonymization fail-closes.
3. **Golden-set versions are immutable** — corrections produce a new version, not an edit.
4. **Curation is audit-logged** — every promotion/rejection records curator identity, timestamp, reason.
5. **Graduation is mechanical, not negotiable** — capability → regression promotion follows `pass^k ≥ 0.95` over declared window; no one-off promotions.
6. **X1A consumes pinned versions** — runtime policy never reads "latest"; it reads a specific version tag so drift is an explicit policy change, not a silent one.

---

## 7. Minimal Viable Implementation Order

If this pipeline is implemented incrementally, suggested order:

1. **Enrich BUS P / BUS T rows** to match `grader_composition_spec.md` §7 schema. *(Smallest change; enables everything else.)*
2. **Stand up the candidate pool** with dedup + anonymization + promotion heuristic. *(No curation yet — just a queue.)*
3. **Add curation UI + workflow**. *(Can start with a spreadsheet + review meetings; automate later.)*
4. **Materialize the golden set directories** under `data/eval/golden/`. *(Start with hand-curated seed cases; migrate existing test fixtures here.)*
5. **Wire X1A to load pinned golden-set version** as its policy input.
6. **Add graduation automation** (capability → regression).
7. **Close the loop**: wire X1G `pass^k` computation to read from the regression-track BUS T history scoped by `trajectory_class`.

Steps 1–4 are largely independent; step 5 requires 4; step 6 requires 5; step 7 requires 1 and 5.

---

## 8. Open Questions (not blockers for v4)

- **Curator capacity model**: how is the daily curation budget set, and what happens when the candidate queue exceeds it? (Proposal: bump the promotion-heuristic threshold until queue fits; log the shift.)
- **Auto-curation for high-volume low-risk categories**: what agreement rate against SME curators qualifies an auto-curator for deployment? (Proposal: Cohen's κ ≥ 0.85 on a rolling 200-case audit.)
- **Cross-cohort fairness guardrail**: how does the pipeline prevent the golden set from drifting toward over-represented user cohorts? (Proposal: per-cohort quotas in the promotion heuristic.)

These are implementation-time design questions, not architectural gaps in the flow itself.
