---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-underwriting-feature-complete-aa79a7.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-underwriting-feature-complete-aa79a7.md'
source_sha256: 1cd7a28caa25e4a9e5046744ae4a592452a3eaa840376d167465db5b89ce90e1
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Plan — `apps_underwriting_ai` Feature-Complete Domain Logic

**Slug:** `apps-underwriting-feature-complete-aa79a7`
**Created:** 2026-05-02
**Tier:** T3 (cross-module, multi-file, regulated-domain surface)
**Driver:** DEFERRED_SCOPE row from `apps-completeness-remediation-907fac` (completed 2026-05-02)
**Status:** Completed (2026-05-02)
**Predecessors:**
- `.windsurf/plans/apps-completeness-remediation-907fac.md` (Completed 2026-05-02 — built canonical skeleton)
- `.windsurf/plans/apps-completeness-followups-287d2a.md` (Completed 2026-05-02 — docs + contract tests)
- `.windsurf/plans/apps-underwriting-ai-activation-e8a3c5.md` (concurrent, in motion — already landed `DeterministicRiskScorer` + LLM rationale enrichment)

## Goal

Close the remaining skeleton-to-functional gap in `apps_underwriting_ai`. Explicitly stays on the skeleton-to-functional side of the SME cliff — **real actuarial/regulatory domain logic remains deferred** and requires jurisdiction-specific review (see `SVP_ENGINEERING_REVIEW.md` §"Skeleton Boundary" and `engines/risk_scorer.py` module docstring).

This plan completes the **structural and surface parity** with `apps_rfp` (the canonical sibling) after the activation effort lands. It does NOT promote the package to regulator-grade underwriting.

## Scope Boundary (IMPORTANT)

**IN scope:**
- `parsers/` package — minimal document parsers (PDF text extraction, structured-JSON ingestion, CSV)
- `validators/` package — minimal compliance gates (required-field presence, risk-score ceiling/floor invariants, rubric-coverage gates)
- `services/` package — rubric-wiring service, LLM judge telemetry service, pre-migration audit tooling service
- `tools/` package — CLI utilities matching apps_rfp shape (`run_underwriting.py`, `audit_spine_manifest.py`)
- Rubric wiring — cleanly connect `policy/rubrics/judge_underwriting_decision.yaml` to assembler telemetry
- Contract tests for the new surfaces (parsers, validators, services)

**OUT of scope (deferred):**
- Actuarial model replacing `DeterministicRiskScorer` — requires jurisdictional SME
- Bias / fairness audit — requires external party
- Regulatory review (FCA / OCC / FINRA / FDIC / SEC / CFPB jurisdictions)
- Real OCR of PDF evidence — requires OCR provider + prompt-injection defense
- Production LLM routing — current Qwen-first cascade is demonstration-grade only

## Files In Scope (NEW)

### Wave 1 — Parsers
- `apps_underwriting_ai/parsers/__init__.py` (expand from ~200b stub to full package)
- `apps_underwriting_ai/parsers/document_parser.py` (NEW — base class)
- `apps_underwriting_ai/parsers/json_document_parser.py` (NEW — structured JSON ingress)
- `apps_underwriting_ai/parsers/csv_document_parser.py` (NEW — CSV evidence tables)
- `apps_underwriting_ai/parsers/pdf_text_parser.py` (NEW — text-only PDF extraction via `pypdf`)

### Wave 2 — Validators
- `apps_underwriting_ai/validators/__init__.py` (expand)
- `apps_underwriting_ai/validators/required_field_validator.py` (NEW)
- `apps_underwriting_ai/validators/risk_score_bounds_validator.py` (NEW)
- `apps_underwriting_ai/validators/rubric_coverage_validator.py` (NEW)
- `apps_underwriting_ai/validators/decision_packet_validator.py` (NEW — composite)

### Wave 3 — Services
- `apps_underwriting_ai/services/__init__.py` (NEW package)
- `apps_underwriting_ai/services/rubric_wiring_service.py` (NEW — loads `policy/rubrics/judge_underwriting_decision.yaml` into assembler)
- `apps_underwriting_ai/services/llm_judge_telemetry_service.py` (NEW — emits judge-result events to ObservabilityAdapter)
- `apps_underwriting_ai/services/pre_migration_audit_service.py` (NEW — scans the package for durable-write leakage, consumed by spine_manifest)

### Wave 4 — Tools
- `apps_underwriting_ai/tools/__init__.py` (NEW package)
- `apps_underwriting_ai/tools/run_underwriting.py` (NEW — CLI mirror of apps_rfp)
- `apps_underwriting_ai/tools/audit_spine_manifest.py` (NEW — validates `spine_manifest.yaml` claims against source)

### Wave 5 — Rubric wiring
- `apps_underwriting_ai/engines/decision_packet_assembler.py` (EDIT — wire `RubricWiringService` into rationale enrichment flow)
- `apps_underwriting_ai/integrations/observability_adapter.py` (EDIT — new `emit_judge_result` method)

### Wave 6 — Tests
- `apps_underwriting_ai/tests/test_parsers.py` (NEW — ≥12 tests)
- `apps_underwriting_ai/tests/test_validators.py` (NEW — ≥15 tests)
- `apps_underwriting_ai/tests/test_services.py` (NEW — ≥10 tests)
- `apps_underwriting_ai/tests/test_tools.py` (NEW — ≥6 tests)

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 | P1.1–P1.4 | `parsers/` package | ~6k | `pypdf` available; JSON/CSV stdlib | DONE | 4 parser modules shipped (base + JSON + CSV + PDF-text); registry auto-registers on import |
| W2 | P2.1–P2.4 | `validators/` package | ~5k | ValidationResult dataclass + composite pattern | DONE | 4 validators shipped (required-field + risk-score-bounds + rubric-coverage + composite); all severities enforced |
| W3 | P3.1–P3.3 | `services/` package | ~5k | Rubric YAML present; AST scan service | DONE | 3 services shipped (rubric wiring with lru_cache + judge telemetry + pre-migration audit with tests/ exclusion) |
| W4 | P4.1, P4.2 | `tools/` package | ~3k | CLI mirrors apps_rfp | DONE | 2 CLIs shipped (`run_underwriting.py` with --request/--out/--format/--trace-id, `audit_spine_manifest.py` with dotted-path resolver) |
| W5 | P5.1, P5.2 | Rubric wiring | ~3k | Assembler seam exists | DONE | `_emit_marker` now loads live rubric id/version via `RubricWiringService` (fail-soft) AND emits `judge_result` via `LLMJudgeTelemetryService`; `ObservabilityAdapter.emit_judge_result` added |
| W6 | P6.1–P6.4 | Test suites | ~8k | No property tests | DONE | **132 tests pass** (61 pre-existing + 71 new): 22 parsers + 26 validators + 13 services + 10 tools |

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Parser base class + registry | `parsers/document_parser.py` | Union `bytes \| Path` input; registry with ext-key dispatch | ~1.5k | DONE |
| P1.2 | JSON document parser | `parsers/json_document_parser.py` | Rejects list/scalar roots; key-sorted text | ~1k | DONE |
| P1.3 | CSV document parser | `parsers/csv_document_parser.py` | Header required; UTF-8 BOM tolerated; row ceiling 10k | ~1.5k | DONE |
| P1.4 | PDF text parser | `parsers/pdf_text_parser.py` | `OptionalDependencyMissing` when pypdf absent; per-page failure tolerated | ~2k | DONE |
| P2.1 | Required-field validator | `validators/required_field_validator.py` | Per-product field list; universal fallback | ~1k | DONE |
| P2.2 | Risk-score bounds validator | `validators/risk_score_bounds_validator.py` | APPROVE/REFER/DECLINE band invariants; [0,100] / [0,1] bounds | ~1k | DONE |
| P2.3 | Rubric-coverage validator | `validators/rubric_coverage_validator.py` | Configurable required feature keys; min-rationale-chars | ~1.5k | DONE |
| P2.4 | Composite decision_packet validator | `validators/decision_packet_validator.py` | Skips sub-validators with missing inputs; only error-severity blocks | ~1.5k | DONE |
| P3.1 | Rubric wiring service | `services/rubric_wiring_service.py` | `lru_cache` keyed by resolved path; `reload()` bypass | ~1.5k | DONE |
| P3.2 | LLM judge telemetry service | `services/llm_judge_telemetry_service.py` | Frozen `JudgeTelemetryEvent`; delegates to `emit_judge_result` | ~1.5k | DONE |
| P3.3 | Pre-migration audit service | `services/pre_migration_audit_service.py` | Excludes `tests/` + `__pycache__` by default; configurable | ~2k | DONE |
| P4.1 | `run_underwriting.py` CLI | `tools/run_underwriting.py` | argparse; `--request` / `--out` / `--format` / `--trace-id` | ~1.5k | DONE |
| P4.2 | `audit_spine_manifest.py` | `tools/audit_spine_manifest.py` | Longest-prefix module resolver handles `pkg.mod.Class.method` | ~1.5k | DONE |
| P5.1 | Wire rubric service into assembler | `engines/decision_packet_assembler.py::_emit_marker` | Additive: live rubric id/version, fail-soft telemetry; existing LLM cascade untouched | ~1.5k | DONE |
| P5.2 | Add `emit_judge_result` to ObservabilityAdapter | `integrations/observability_adapter.py` | Scalar-only payload (no PII); existing emitters unchanged | ~1k | DONE |
| P6.1 | `test_parsers.py` | 22 tests | Registry + JSON + CSV + PDF + frozen dataclass | ~2k | DONE |
| P6.2 | `test_validators.py` | 26 tests | All 4 validators + composite + severity enforcement | ~2.5k | DONE |
| P6.3 | `test_services.py` | 13 tests | RubricWiringService + telemetry + audit (synthetic + live) | ~2k | DONE |
| P6.4 | `test_tools.py` | 10 tests | CLI happy/error paths + resolver unit tests | ~1.5k | DONE |

## Gap Register

- `parsers/` package is declared in `TECHNICAL_SPEC.md` §5 as a skeleton seam but currently an empty namespace package (~200b `__init__.py`).
- `validators/` same situation — declared, declared, empty.
- `services/` package not yet created; `apps_rfp` has a `services/` pattern apps_underwriting_ai should mirror.
- `tools/` package not yet created; `apps_rfp` has `tools/` pattern.
- `policy/rubrics/judge_underwriting_decision.yaml` exists (from activation effort) but is not yet wired into runtime code — it's documentation-only until rubric wiring service lands.
- Test parity gap: 61 contract tests exist (from `287d2a`) but no coverage for parsers/validators/services/tools/CLI.

## DEFERRED_SCOPE (post-this-plan)

DEFERRED_SCOPE: title=`apps_underwriting_ai regulator-grade actuarial model` reason=`replacing DeterministicRiskScorer with jurisdictional actuarial model requires SME engagement, bias audit, and regulatory review; plan aa79a7 deliberately stays on skeleton-to-functional side` plan=`TBD` predecessor=`apps-underwriting-feature-complete-aa79a7`

DEFERRED_SCOPE: title=`apps_underwriting_ai real OCR evidence ingestion` reason=`PDF text parser (W1 P1.4) handles text-only PDFs; image-PDF OCR requires OCR provider integration + prompt-injection defense; separate security-reviewed scope` plan=`TBD` predecessor=`apps-underwriting-feature-complete-aa79a7`

## ADG_HOTSPOT_REPORT

Skipped: this is a **structural-completeness / skeleton-graduation** plan, not a hotspot-driven refactor. Targets are determined by apps_rfp parity-gap enumeration. Per `.windsurf/rules/adg-graph-layer-enforcement.md`, hotspot ordering is required for **anti-pattern burndown / refactoring** plans; this is neither.

## ADG_GRAPH_LAYER_EVIDENCE

When executed, this plan should verify:
- **`mv_task_contract_gaps`** for `apps_underwriting_ai` — reduces as parsers/validators/services land with real contract edges
- **`mv_trace_replay_eval_gaps`** — reduces as LLM judge telemetry service lands
- **`mv_prompt_assembly_wiring_gaps`** — reduces as rubric wiring service lands (connects YAML → runtime code)
- **`mv_runtime_spine_gaps`** — `audit_spine_manifest.py` (P4.2) validates the spine_manifest claims programmatically
- Semantic edges: `reads_from` (rubric YAML), `resolves_callsite` (rubric dispatch into assembler), `controls_flow` (validator composition)
- `v_p1_*` / `v_p2_*` views: apps_underwriting_ai rows should decrease as stubs become real

## Verification Strategy (when executed)

- **W1 done** = `pytest apps_underwriting_ai/tests/test_parsers.py -v` passes; ≥12 tests
- **W2 done** = `pytest apps_underwriting_ai/tests/test_validators.py -v` passes; ≥15 tests
- **W3 done** = `pytest apps_underwriting_ai/tests/test_services.py -v` passes; ≥10 tests
- **W4 done** = `pytest apps_underwriting_ai/tests/test_tools.py -v` passes; ≥6 tests; `python -m apps_underwriting_ai.tools.run_underwriting --help` works
- **W5 done** = Assembler emits `judge_result` event when rubric wiring enabled; existing 10-test contract suite still passes
- **W6 done** = Total `pytest apps_underwriting_ai/tests/` ≥104 tests, all pass
- **Plan done** = `python -m apps_underwriting_ai --demo` still emits valid DecisionPacket end-to-end AND rubric coverage is non-zero AND pre-migration audit passes

## Coordination With Activation Plan

Plan `apps-underwriting-ai-activation-e8a3c5` is in motion concurrently. Coordination points:
- This plan's P5.1 (rubric wiring into assembler) touches the same file as the activation plan's LLM enrichment — **sequence AFTER activation plan completes** to avoid merge conflict
- Do not modify `engines/risk_scorer.py` — owned by activation plan
- Do not modify `engines/decision_packet_assembler.py` imports — owned by activation plan; only add new method calls, do not rearrange
- Pre-execution: verify activation plan status is `Completed` before starting W5

## References

- Predecessor plan (skeleton build): `.windsurf/plans/apps-completeness-remediation-907fac.md`
- Predecessor plan (docs + tests): `.windsurf/plans/apps-completeness-followups-287d2a.md`
- Concurrent plan: `.windsurf/plans/apps-underwriting-ai-activation-e8a3c5.md`
- Canonical sibling pattern: `apps_rfp/` (tests, services, tools, integrations)
- Constitutional §22 (graph-layer primary), §28 (ADG over grep)
