---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\agentic-core-eval-control-audit-b7d4a2.md'
original_relative_path: '_archive\\2026-05\\agentic-core-eval-control-audit-b7d4a2.md'
source_sha256: 29c576ee3ba50ea2bdfebc79892c2b75a8b912e47b8ac48985ff6d288d19ea2d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — `agentic_core` Evaluation/Control Pattern Audit

- **Plan ID**: `agentic-core-eval-control-audit-b7d4a2`
- **Owner**: Cursor Agent (audit author)
- **Status**: Draft
- **Tier**: T3 (read-only audit, repo-wide scope across all `agentic_core` layers + adjacent proof/test surfaces)
- **Created**: 2026-05-02
- **Type**: Read-only audit — deliverable is a Markdown report. NO code changes, NO file writes outside the report, NO patches, NO refactors.

---

## 1. Goal

Produce a single audit deliverable that, for every relevant `agentic_core` surface (and adjacent proof/test/registry surfaces), recommends the cheapest safe evaluation/control pattern from this fixed enum:

1. **None** (deterministic only)
2. **Judge** (single LLM judge — Qwen 32B via vLLM by default)
3. **Hybrid** (Judge + targeted Ensemble escalation)
4. **Ensemble Only**

The deliverable is six fixed sections (Executive Summary + 5 tables) defined verbatim in the user request. Recommendations must be grounded in repo evidence; missing evidence is logged as a gap, never invented.

## 2. Non-Goals

- No code changes, no patches, no refactors, no new abstractions, no invented files.
- No execution of judges, ensembles, or any runtime probe.
- No prose outside the six requested sections in the final deliverable.
- No broad rule/skill/hook authoring as a side-effect of the audit.
- Does NOT replace existing ADRs (e.g., ADR-023 HITL, ADR-050 ledger family, ADR-079 L2 graph-layer contract, ADR-080 RTC Phase D); audit cross-references them, never overrides.

## 3. Hard Constraints (from request — verbatim invariants)

- L0 emits exactly one deterministic RouteContract; no retrieval/exec/model/state/promotion.
- L3 only when `execution_form = MANAGED_WORKFLOW`; shapes managed steps; no re-decide of L0, no direct retrieval/exec/model/L4 mutation/promotion.
- L2 executes the bounded packet/workflow step; emits `proposed_state_diff` only; no L4 writes; healing is same-authority/local/bounded.
- Runtime Gates emit `GateVerdict` only; UNKNOWN ≠ PASS; not the final `ExitDisposition`; no routing/retrieval/prompt-assembly/exec/release/commit/cert/promotion.
- Exit owns X1/X2/X3; may use LLM-as-Judge for semantic checks; no exec/retrieval/L4 mutation/L6 rescue.
- Judge cannot retrieve, execute tools, override X3, write L4, or invent facts.
- Default cost-optimized judge: **Qwen 32B via vLLM**.
- L6 observes completed-run exhaust only; cannot rescue/mutate the current run.

These are the hard scoring rules the audit must enforce on every row.

## 4. Scope — Surface Inventory Targets

The audit MUST inventory the following surfaces inside `agentic_core/` and adjacent dirs. The surface list is the row keyspace for Section 2.

| Surface group | Anchor paths to scan | Expected row count (rough) |
|---|---|---|
| U0 intake | `agentic_core/L0_routing/` (intake side), `apps_*/integrations/*ingress*` | 5–10 |
| L0 routing | `agentic_core/L0_routing/` (route contract emit, namespace bandit, path router, ensemble router) | 10–20 |
| L1 planning / cognition | `agentic_core/L1_cognition/` | 8–15 |
| L3 orchestration | `agentic_core/L3_orchestration/` (managed workflow, retries, joins, sealed packages) | 8–15 |
| C0 context / retrieval | `agentic_core/L0_routing/c0_retrieval/`, `agentic_core/L1_cognition/c0_context/` | 5–12 |
| Prompt assembly | grep-equivalent ADG query for `prompt_assembly`, `assemble_prompt`, `PromptAssembly` | 4–8 |
| L2 execution | `agentic_core/L2_execution/` (capability, audit, healers, PTC sandbox if present) | 15–25 |
| L2 healing | `agentic_core/L2_execution/healers/` | 4–8 |
| PTC sandbox | search for `ptc_`, `sandbox`, `bounded_executor` under L2 | 2–6 |
| Runtime Gates G01–G29 | `agentic_core/*/gates/`, `ops_scripts/ci/*gate*.py` (runtime vs CI separation noted per row) | up to 29 |
| Exit (X1/X2/X3) | search `exit_`, `x1_`, `x2_`, `x3_`, `ExitDisposition` | 6–12 |
| L5 governance / certification | `agentic_core/L5_*`, `scripts/compile_requirement_signoff.py`, `scripts/verify_*` | 6–10 |
| L4 / UWG state / write admission | `agentic_core/L4_*`, UWG modules | 5–10 |
| L6 shadow evaluation | `agentic_core/L6_observability/`, promotion gates, regret accounting | 5–10 |
| Registries | `agentic_core/*/registry*`, `apps_shared/config/app_guardian_registry.py` | 4–8 |
| Model gateway / provider routing | `agentic_core/*/providers/`, gateway adapters | 4–8 |
| Replay / audit / OTEL proof surfaces | `tools/adg/`, `scripts/proof/`, OTEL bootstrap | 4–8 |
| Tests / proof harnesses encoding runtime eval behavior | `tests/_apps_contract/`, `tests/proof/`, `tests/runtime_*` | 5–10 |

**Estimated total rows in Section 2: 110–200.** Cap at ≤220; if more candidates surface, group by archetype (e.g., one row for "G01–G05 schema-shape gates" with shared rationale) and call out outliers individually.

## 5. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1, P1.2, P1.3 | Surface inventory via ADG + read-only scan | ~12k | ADG snapshot fresh; `adg_sqlite` healthy | Pending | Every surface group has ≥1 candidate row with file path + role |
| W2 | P2.1, P2.2 | Per-row decision scoring (None/Judge/Hybrid/Ensemble) using boundary rules + heuristics | ~18k | Boundary rules in §3 are non-negotiable | Pending | Every row has decision + qwen_role + rationale + evidence ref |
| W3 | P3.1, P3.2, P3.3 | Cross-row consistency pass + by-layer rollup + high-risk exception extraction | ~8k | Section 2 stable | Pending | Section 3 + 4 derived deterministically from Section 2 |
| W4 | P4.1, P4.2 | Cost optimization summary + gap register + final assembly into one Markdown file | ~6k | No new evidence-gathering after W3 freeze | Pending | Single deliverable file, six sections, no extra prose |

## 6. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | ADG-driven surface enumeration | `adg_sqlite` queries on `agentic_core/L0_routing`, `L1_cognition`, `L2_execution`, `L3_orchestration`, `L4_*`, `L5_*`, `L6_observability` (one query per layer) | ADG MCP must be healthy; if degraded → direct sqlite read of latest `artifacts/adg/adg_indexed_<ts>.sqlite` per constitutional §28 | ~5k | Pending |
| P1.2 | Adjacent surface enumeration | runtime gates, exit, registries, gateway, replay, prompt-assembly, PTC sandbox | Runtime gates may be split between `agentic_core/` and `ops_scripts/ci/` — must classify each row as runtime vs CI | ~4k | Pending |
| P1.3 | Test/proof-harness enumeration | `tests/_apps_contract/`, `tests/proof/`, `scripts/proof/`, harnesses that encode runtime eval behavior | Distinguish "encodes runtime behavior" (in scope) from "ordinary unit tests" (out of scope) | ~3k | Pending |
| P2.1 | Decision scoring pass — deterministic-first surfaces | Schema/hash/registry/replay/import-boundary/OTEL-presence rows | Must default to None unless semantic judgment is structurally required | ~9k | Pending |
| P2.2 | Decision scoring pass — semantic surfaces | Exit X1/X2, output-quality checks, groundedness, trajectory critique, repairability, ambiguous-plan quality | Justify every Judge/Hybrid/Ensemble vs cheaper option; record qwen_role precisely | ~9k | Pending |
| P3.1 | Cross-row consistency check | All Section-2 rows | Catch inconsistent rationale across siblings (e.g., G01 schema vs G02 schema getting different decisions without justification) | ~3k | Pending |
| P3.2 | By-layer rollup synthesis | Section 3 derivation | Default-pattern per layer must be the modal recommendation across that layer's rows | ~2k | Pending |
| P3.3 | High-risk exception extraction | Section 4 derivation | Exception = recommendation diverges from layer default AND `risk_level ≥ high` | ~3k | Pending |
| P4.1 | Cost optimization summary + gap register | Sections 5 + 6 | Cost categories: deterministic-only, Qwen-judge, ensemble-escalation, external-model-escalation; gaps must be actionable | ~3k | Pending |
| P4.2 | Final deliverable assembly | Single file at `docs/reports/agentic_core_eval_control_audit/<YYYY-MM-DD>.md` | No prose outside the six sections; verbatim section headings; ground every row | ~3k | Pending |

## 7. Files In Scope (read-only)

- All of `agentic_core/**/*.py` (read via ADG queries + targeted `read_file`)
- `apps_shared/enforcement/`, `apps_shared/config/app_guardian_registry.py` (cross-cutting strategies)
- `scripts/proof/`, `scripts/compile_requirement_signoff.py`, `scripts/verify_*` (proof surfaces)
- `tests/_apps_contract/`, `tests/proof/`, `tests/runtime_*` (runtime-encoded harnesses)
- `ops_scripts/ci/*gate*.py` (CI vs runtime gate disambiguation only)
- `artifacts/adg/adg_indexed_<ts>.sqlite` (read-only)
- ADRs referenced for cross-validation: ADR-023, ADR-050, ADR-074, ADR-079, ADR-080, ADR-081

## 8. Files Out of Scope

- `apps_lic/`, `apps_rg/`, `apps_eval/`, `apps_exec/`, `apps_research/`, `apps_rfp/`, `apps_qna/`, `apps_underwriting_ai/` (app-domain code; audit only references when a strategy is shared via `apps_shared/`)
- `infrastructure/` MCP catalog (out of scope unless it gates runtime eval behavior)
- `system_learning/` except where directly invoked by L4/UWG/L6 in scope
- Any code change anywhere

## 9. Methodology

### 9.1 Surface enumeration (W1)

- ADG-first per constitutional §22/§28: `adg_nodes_by_layer` for L0..L6; `adg_nodes_by_file` to expand a layer; `adg_edge_fanin` for centrality on candidate nodes.
- Direct SQLite fallback if MCP unhealthy. NEVER grep for dependency analysis.
- Classify each enumerated node into one of the surface groups in §4.

### 9.2 Decision scoring (W2)

For every candidate row, evaluate the four-step decision tree in this order:

1. **Is the expected answer objectively checkable?** (schema, hash, registry, replay, policy_hash equality, OTEL presence, artifact existence, import boundary, enum value)
   - YES → **None**. `qwen_32b_vllm_role = not_used`. Stop.
2. **Does the surface require semantic judgment AND can it be graded against a clear rubric/evidence/schema?**
   - YES → continue. NO → likely **None** with a deterministic gap recorded.
3. **Is the surface high-impact / user-visible / policy-sensitive / cross-step / durable-mutation-readiness, OR will Qwen UNKNOWN/low-confidence need cross-check?**
   - YES → **Hybrid**. `qwen_32b_vllm_role = primary_judge` with ensemble_trigger described.
   - NO → **Judge**. `qwen_32b_vllm_role = primary_judge`.
4. **Is the value of the row diversity-of-outputs itself (shadow eval, pass^k, calibration, model variance, candidate generation comparison)?**
   - YES → **Ensemble Only**. `qwen_32b_vllm_role` ∈ `{not_used, fallback_judge}` per row.

Boundary violations (per §3) override heuristics. Example: a Runtime Gate that "wants" to be Judge but `grader_type=code` and the check is hash equality → **None**.

### 9.3 qwen_32b_vllm_role assignment

- `not_used` — deterministic surface or judge forbidden by boundary.
- `primary_judge` — Qwen is the LLM judge for the row.
- `fallback_judge` — Qwen runs only when a stronger judge abstains or for replay.
- `escalation_only` — Qwen sits behind an external model on a high-risk row, runs only when external is unavailable.
- `not_applicable` — surface doesn't admit any judge (e.g., L4 commit).

### 9.4 Evidence grounding

Every row's `repo_evidence` field cites a file path (and line range when narrow). Rows lacking evidence are marked as gaps in Section 6, not invented.

### 9.5 ADG provenance stamp

Final deliverable carries an `ADG Provenance:` line (per `adg-canonical-invariants.md` §11) with backend + snapshot.

## 10. Deliverable

Single file:

```
docs/reports/agentic_core_eval_control_audit/<YYYY-MM-DD>.md
```

Sections (verbatim from request, no extras):

1. Executive Summary (5–8 bullets)
2. Recommendation Table (13 columns)
3. By-Layer Rollup (6 columns)
4. High-Risk Exceptions (5 columns)
5. Cost Optimization Summary (5 columns)
6. Gaps and Follow-Up Questions (5 columns)

No code changes, no helper scripts, no rule edits, no skill edits. The deliverable is the entire output.

## 11. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Surface explosion (>220 rows) makes Section 2 unwieldy | Medium | Group sibling rows by archetype; call out outliers individually |
| ADG snapshot stale / MCP red | Low | Direct SQLite fallback; if both fail, emit `DEGRADED_FALLBACK:` per §28 and gate the audit on regen |
| Boundary-rule conflict with heuristic (e.g., gate "feels semantic" but is hash-only) | Medium | Boundary rules win; record in rationale |
| Drift between this plan's surface taxonomy and ADG layer assignments | Low | Use ADG `nodes.layer` as source of truth; don't fabricate layer labels |
| Reviewer expects executable validators / probes | N/A | Plan + deliverable are read-only by mandate; gaps in §6 propose follow-ups |

## 12. Success Criteria

- One Markdown deliverable at the specified path containing exactly the six requested sections.
- Every Section-2 row has all 13 columns populated (or explicit `n/a — see §6 gap`).
- Every recommendation traceable to either (a) repo evidence, (b) a §3 hard constraint, or (c) a §6 gap.
- Section 3 rollups match the modal decision per layer in Section 2.
- Section 4 only contains rows whose recommendation diverges from the layer default AND have `risk_level ≥ high`.
- ADG provenance stamp present.
- No code changes anywhere in the repo.

## 13. References

- Constitutional rules: §3 (no agent deletion), §5 (ADG before T2/T3), §22 (graph-layer primary), §28 (SQLite-direct fallback supersedes grep), §29 (closed-loop router enforcement).
- ADRs: ADR-023 (runtime HITL), ADR-050 (intelligence-ledger family), ADR-074 (graph-layer surfaces), ADR-079 (L2 graph-layer consumption contract), ADR-080 (RTC Phase D design), ADR-081 (apps E2E spine cert wireup).
- Skills: `graph-analysis`, `adg-sqlite`, `author-gate-decision-points` (for any ambiguity flagged during scoring).
- Rules: `adg-canonical-invariants.md`, `adg-graph-layer-enforcement.md`, `adg-hotspot-enforcement.md`, `closed-loop-router-enforcement.md`, `evaluation-promotion-gate.md`, `judge-calibration-cadence.md`, `author-gate-enforcement.md`.

## 14. Plan Self-Validation

- [x] Wave Structure table present
- [x] Phase-Level Summary table present
- [x] Files In Scope and Out of Scope explicit
- [x] Non-goals explicit (no code changes, no execution)
- [x] Methodology grounded in §3 boundary rules and the four-step decision tree
- [x] Deliverable path + section list verbatim from user request
- [x] References include constitutional rules, ADRs, skills, and rules used during audit scoring
