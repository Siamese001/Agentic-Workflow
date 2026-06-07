---
plan_id: apps-underwriting-ai-deferred-scope-e8b2f4
plan_type: deferred_scope
parent_plan: apps-underwriting-ai-spine-hardening-d7f3b2
status: Not Started
---

# apps_underwriting_ai — Deferred Scope (post spine-hardening)

Deferred scope items from `apps-underwriting-ai-spine-hardening-d7f3b2` (Completed 2026-05-05).
**DO NOT IMPLEMENT** — planning document only. Items are ordered by priority band.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| D1 | D1.1–D1.3 | End-to-end integration test harness | ~12k | ⬜ Not Started |
| D2 | D2.1–D2.2 | R1A exact-cache hash-gate hardening | ~8k | ⬜ Not Started |
| D3 | D3.1–D3.3 | LLM rationale judge: real scoring + calibration | ~16k | ⬜ Not Started |
| D4 | D4.1–D4.2 | OTEL span wiring (runtime observability) | ~8k | ⬜ Not Started |
| D5 | D5.1–D5.2 | PublicTrustReceipt JSON schema + validation gate | ~6k | ⬜ Not Started |
| D6 | D6.1–D6.2 | `apps_underwriting_ai` eval harness RAG dims wire-up | ~8k | ⬜ Not Started |
| D7 | D7.1 | Legacy `DeterministicRiskScorer` quarantine / archival | ~4k | ⬜ Not Started |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|--------------|-------------|-------------|--------|
| D1.1 | E2E fixture-driven test runner | New `tests/e2e/test_underwriting_e2e.py` + fixture loader | Must not require live LLM; use deterministic fallback path | ~5k | ⬜ |
| D1.2 | Fixture → spine → exit round-trip assertion | Same file; 4 fixture packets → assert X3 disposition | Fixture YAML parsing + X3 selector wiring | ~4k | ⬜ |
| D1.3 | E2E regression gate in CI | `ops_scripts/ci/check_underwriting_e2e_fixtures.py` | Must run without network; fixture-only mode | ~3k | ⬜ |
| D2.1 | R1A cache key specification | `apps_underwriting_ai/integrations/underwriting_route_selector.py` (extend) | Key = SHA-256(request_envelope + doc_hashes + policy_hash + blueprint_hash + scorer_version + schema_version) | ~4k | ⬜ |
| D2.2 | R1A hit-path tests (5) | `tests/governance/test_apps_underwriting_ai_routing.py` (extend) | Must verify exact match is not replayed if any hash component drifts | ~4k | ⬜ |
| D3.1 | LLM rationale judge stub → real grader | `apps_underwriting_ai/engines/judges/` (new) | Spearman ≥ 0.80 vs human-labeled holdout required before promotion | ~6k | ⬜ |
| D3.2 | Judge calibration harness | `ops_scripts/calibration/underwriting_judge_calibration.py` | Needs human-labeled set of 30+ rationale/verdict pairs | ~6k | ⬜ |
| D3.3 | Judge disagreement → HITL_HARD_FREEZE wiring | `apps_underwriting_ai/integrations/underwriting_exit_fec_producer.py` (extend) | Judge UNKNOWN must already fail-closed; disagreement must add HARD_FREEZE | ~4k | ⬜ |
| D4.1 | OTEL span emission per L2 stage | `apps_underwriting_ai/integrations/underwriting_l2_step_adapters.py` (extend) | One span per E1–E5 stage; include verdict_hash in span attributes | ~4k | ⬜ |
| D4.2 | Exit X3 span + PublicTrustReceipt in OTEL | `apps_underwriting_ai/integrations/underwriting_exit_fec_producer.py` (extend) | Span must include x3_disposition + demo_packet_id | ~4k | ⬜ |
| D5.1 | `PublicTrustReceipt` JSON Schema file | `apps_underwriting_ai/schemas/public_trust_receipt.schema.json` (new) | All 15 fields from `PublicTrustReceipt` dataclass; required vs optional declared | ~3k | ⬜ |
| D5.2 | Schema validation gate | `ops_scripts/ci/check_underwriting_public_trust_receipt_schema.py` (new) | Validate every fixture packet's expected PTR against schema | ~3k | ⬜ |
| D6.1 | Wire RAG dims into eval rubric | `apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml` (extend) | 3 RAG dims: context_recall, context_precision, answer_relevancy; intentional_failopen until C0 producers wire | ~4k | ⬜ |
| D6.2 | Eval harness round-trip test | `tests/_apps_contract/` (new test file) | Verify FEC flows into ExitReviewPacket.final_evidence_contract | ~4k | ⬜ |
| D7.1 | Legacy runner quarantine | `apps_underwriting_ai/engines/` audit; move superseded stubs to `_archived/` | Must not break any active import; 0 tests reference archived files | ~4k | ⬜ |

---

## Deferred Item Details

### D1 — End-to-End Integration Test Harness

**Why deferred:** The spine hardening plan enforced unit-level governance tests only (no network, no LLM). A fixture-driven E2E runner requires the deterministic fallback path to be wired into a CLI harness — feasible but out-of-scope for the hardening pass.

**Acceptance criteria:**
- All 4 demo fixture packets (approve/missing/refer/decline) can be run through the full spine path end-to-end using the deterministic fallback (no LLM call required).
- Each packet produces the expected `x3_disposition`.
- CI gate runs in < 10 seconds, no network required.

---

### D2 — R1A Exact-Cache Hash-Gate Hardening

**Why deferred:** `UnderwritingRouteSelector` declares R1A as a route mode but the cache key specification (which fields hash into the lookup key) was not fully codified. The routing tests mock the cache hit but do not validate key composition.

**Acceptance criteria:**
- R1A cache key is SHA-256 of: `(request_envelope_hash, doc_content_hashes[], policy_hash, blueprint_hash, scorer_version, schema_version)`.
- Any drift in any hash component (e.g. new document content) produces a cache miss, not a stale hit.
- 5 tests cover: exact hit, policy drift miss, doc drift miss, scorer version bump miss, schema version bump miss.

---

### D3 — LLM Rationale Judge: Real Scoring + Calibration

**Why deferred:** The LLM firewall enforces that the rationale lane cannot change verdict or reason codes. However the rationale *quality* judge (does the rationale accurately reflect the approved reason codes?) is still a stub returning `GRADER_UNKNOWN_SENTINEL`. Real grader requires human-labeled holdout.

**Acceptance criteria:**
- Judge implemented in `apps_underwriting_ai/engines/judges/rationale_quality_judge.py`.
- Spearman rank correlation ≥ 0.80 vs human-labeled set of ≥ 30 rationale/verdict pairs.
- Judge UNKNOWN still fails closed (already wired); judge disagreement triggers `HITL_HARD_FREEZE`.
- Calibration harness in `ops_scripts/calibration/` reports per-dim agreement rate.

**Blocker:** Requires human-labeled holdout dataset. Cannot be auto-generated.

---

### D4 — OTEL Span Wiring (Runtime Observability)

**Why deferred:** L2 adapters and the exit producer emit structured receipts but do not yet emit OTEL spans. The OTEL bootstrap (`scripts/proof/otel_bootstrap.py`) exists but apps_underwriting_ai does not call it.

**Acceptance criteria:**
- One OTEL span per L2 stage (E1–E5) with stage name, verdict_hash (post-E5), and receipt type in span attributes.
- Exit X3 span includes `x3_disposition`, `demo_packet_id`, `hitl_posture`.
- Spans visible in `otel_mcp` anomaly/trace queries.

---

### D5 — PublicTrustReceipt JSON Schema + Validation Gate

**Why deferred:** `PublicTrustReceipt` is a frozen dataclass with 15 fields but no external JSON Schema file. The CI gate for fixture validation requires the schema file to exist first.

**Acceptance criteria:**
- `apps_underwriting_ai/schemas/public_trust_receipt.schema.json` declares all 15 fields with correct types.
- `demo_mode: true` is required (not optional).
- CI gate validates each fixture packet's `expected_x3_disposition` mapping against schema.

---

### D6 — Eval Harness RAG Dims Wire-Up

**Why deferred:** `apps_underwriting_ai/config/domain_contract/eval_rubrics.yaml` has 3 RAG dims added as `intentional_failopen` (context_recall, context_precision, answer_relevancy) per the eval harness closeout plan. These remain fail-open until C0 retrieval sources populate `run_context` with evidence the FEC producer can consume.

**Acceptance criteria:**
- RAG dims flip to `fail_closed_if_unknown: true` once C0 evidence is confirmed flowing into `ExitReviewPacket.final_evidence_contract`.
- E2E test confirms FEC fields appear in the exit packet's `final_evidence_contract`.

---

### D7 — Legacy Runner Quarantine / Archival

**Why deferred:** Several engine files pre-date the spine hardening (e.g. older `DecisionPacketAssembler` shim variants, superseded score helpers). No active import references them post-hardening but they have not been formally audited for archival.

**Acceptance criteria:**
- Audit of `apps_underwriting_ai/engines/` confirms which files are unreachable from `__main__.py` post-hardening.
- Unreachable files moved to `apps_underwriting_ai/engines/_archived/` with tombstone comments.
- 0 tests reference archived files.
- ADG blast-radius check confirms 0 live callers after archival.

---

## Non-Goals

- No new canonical route families.
- No real applicant data, real lender thresholds, or production credit decisions.
- No changes to `agentic_core` core routing, Exit v6, or UWG logic.
- No re-implementation of work already landed in `apps-underwriting-ai-spine-hardening-d7f3b2`.

---

## Gap Register

| ID | Gap | Severity | Resolution Wave |
|---|---|---|---|
| GD1 | No E2E fixture-driven runner; X3 outcomes not validated end-to-end | MEDIUM | D1 |
| GD2 | R1A cache key composition not codified; hash drift test missing | MEDIUM | D2 |
| GD3 | Rationale quality judge is `GRADER_UNKNOWN_SENTINEL` stub | MEDIUM | D3 |
| GD4 | No OTEL spans from L2 adapters or exit producer | LOW | D4 |
| GD5 | No JSON Schema file for `PublicTrustReceipt` | LOW | D5 |
| GD6 | RAG eval dims are intentional_failopen pending C0 evidence flow | LOW | D6 |
| GD7 | Pre-hardening engine stubs not formally audited for archival | LOW | D7 |

---

## Source

Captured from `apps-underwriting-ai-spine-hardening-d7f3b2` session 2026-05-05.
Parent plan Notion page: `35727693-f55c-8130-860b-c4230416ab18`.
