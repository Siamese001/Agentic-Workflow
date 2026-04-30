# SVP+ Apps Hardening — Multi-Wave Execution Plan

**Plan ID:** apps-svp-plus-hardening-7c4e3a
**Author:** Cascade (in service of the user's SVP+ Engineering job hunt @ $600K+)
**Status:** In-progress
**Scope:** apps_eval, apps_exec, apps_lic, apps_research, apps_rfp, apps_underwriting_ai, apps_shared (apps_rg explicitly excluded per user)
**Tier:** T3 (cross-app, cross-layer, multi-file)

---

## Why This Plan Exists

A senior Cascade review of all `apps_*` (excl. `apps_rg`) found that the existing SVP_ENGINEERING_REVIEW.md files pass the user's own internal rubric but **do not yet demonstrate SVP+ judgment to an external hiring panel**. Three credibility risks in particular:

1. **Six near-identical SVP review docs** that differ only in noun substitution — reads as templated, not deliberate.
2. **Test depth doesn't match the claim** — 26–31 tests at "100% pass" for 50–100 file domain apps is Pydantic-validator-only coverage.
3. **Module-top-level `_emit_*` calls** that look like compliance theater. Investigation: they are actually a **Python-syntax DSL for declaring ADG semantic edges** (AST-scanned, populating 2,482 `emits_side_effect` edges across apps_*). They are NOT theater for ADG, but they ARE theater for runtime telemetry. The dual-purpose nature requires Author-Gate to refactor — DEFERRED to Wave 4.

This plan delivers **Waves 1–3 in this session** (deterministic, safe, high-ROI) and DEFERS Wave 4 (architectural, requires Author-Gate design).

---

## Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| **W1** | W1.1–W1.6 | Documentation hardening — SLO, runbook, threat model, differentiated SVP reviews | ~25k | Each app's domain shape is already understood from the review; docs are additive (no code change) | In-progress | Each in-scope app has SLO.md + RUNBOOK.md; apps_underwriting_ai + apps_lic have THREAT_MODEL.md; SVP reviews differentiated for top-3 apps; CODEOWNERS in place |
| **W2** | W2.1–W2.3 | Test hardening — contract-test seed + property-based test seed per app, pytest pass | ~12k | Existing test infra/fixtures usable; hypothesis already in deps | Pending | Each app has a `tests/test_contract.py` golden-input/asserted-output file; pytest passes on all touched apps |
| **W3** | W3.1–W3.3 | apps_shared purity CI gate | ~5k | apps_shared currently has no enforced "no domain-app imports" boundary | Pending | `ops_scripts/ci/check_apps_shared_purity.py` exists, wired into pre-commit, passes |
| **W4** | W4.1–W4.4 | DEFERRED — architectural changes requiring Author-Gate design | n/a | Each item is genuinely T2/T3 and unsafe to execute without explicit decision | DEFERRED (markers emitted) | DEFERRED_SCOPE markers persist into Wave/Phase Convergence |

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W1.1 | SLO.md per in-scope app (×7) | `apps_*/SLO.md` | Real numbers vs. defensible defaults; cost ceiling tied to Qwen $/call | ~5k | Pending |
| W1.2 | RUNBOOK.md per in-scope app (×7) | `apps_*/RUNBOOK.md` | Top-3 failure modes must be domain-specific, not boilerplate | ~5k | Pending |
| W1.3 | THREAT_MODEL.md for regulated apps | `apps_underwriting_ai/THREAT_MODEL.md`, `apps_lic/THREAT_MODEL.md` | PII / regulatory boundaries + redaction posture | ~3k | Pending |
| W1.4 | Differentiated SVP_ENGINEERING_REVIEW for top-3 apps | apps_underwriting_ai, apps_lic, apps_eval | "What's hard about THIS domain" + non-goals + alternatives considered | ~5k | Pending |
| W1.5 | Author missing SVP review for apps_lic | `apps_lic/SVP_ENGINEERING_REVIEW.md`, `apps_lic/TECHNICAL_SPEC.md`, `apps_lic/TEST_STRATEGY.md` | apps_lic is the largest app (882KB, 97 files) yet has no SVP doc | ~3k | Pending |
| W1.6 | Author missing SVP review for apps_underwriting_ai | `apps_underwriting_ai/SVP_ENGINEERING_REVIEW.md`, `apps_underwriting_ai/TECHNICAL_SPEC.md`, `apps_underwriting_ai/TEST_STRATEGY.md` | Most-regulated domain, strongest portfolio narrative | ~3k | Pending |
| W1.7 | CODEOWNERS at repo root | `CODEOWNERS` | Demonstrates ownership thinking | ~1k | Pending |
| W2.1 | Contract-test seed per in-scope app (×7) | `apps_*/tests/test_contract.py` | Each app has a different ingress/output shape — no generic template | ~7k | Pending |
| W2.2 | Property-based test seed for top-3 apps | `apps_eval/tests/test_properties.py`, `apps_lic/tests/test_properties.py`, `apps_underwriting_ai/tests/test_properties.py` | Hypothesis strategies tailored to Pydantic types | ~3k | Pending |
| W2.3 | pytest pass | `pytest apps_*` | Existing test infrastructure may not collect new tests cleanly | ~2k | Pending |
| W3.1 | Author `check_apps_shared_purity.py` | `ops_scripts/ci/check_apps_shared_purity.py` | Must use ADG SQLite, not grep, per §5/§28 | ~2k | Pending |
| W3.2 | Wire purity gate into pre-commit + run_contract_gates | `.pre-commit-config.yaml`, `ops_scripts/ci/run_contract_gates.py` | Both files have established schemas | ~1k | Pending |
| W3.3 | Run gate, fix any violations | varies | No violations expected based on initial probe; if found, surface as DEFERRED | ~2k | Pending |
| W4.1 | DEFERRED — apps_eval → L6 promotion/regret wiring | (deferred) | Architectural; needs Author-Gate on flywheel topology | n/a | Deferred |
| W4.2 | DEFERRED — split runtime telemetry from ADG-edge-declarations | (deferred) | Author-Gate on dual-purpose `_emit_*` calls; risk of breaking 2482 ADG edges | n/a | Deferred |
| W4.3 | DEFERRED — per-app cost telemetry rollup ($/call) | (deferred) | Cross-cutting infra; needs design pass | n/a | Deferred |
| W4.4 | DEFERRED — contract-test framework infra (pytest plugin + fixtures) | (deferred) | Test architecture; W2.1 is the seed, not the framework | n/a | Deferred |

---

## ADG_HOTSPOT_REPORT (constitutional §5/§22)

Source: `artifacts/adg/adg_indexed_04292026_1606.sqlite` (2026-04-29 20:24, 650MB)

| File | Edges | Archetype | Surface | Layer | Why it matters |
|------|------:|-----------|---------|------:|----------------|
| `apps_lic/tools/run_workflow_lic.py` | 85 emits | ORCHESTRATOR | Execution | L_APP | Largest emit-edge concentration; orchestration entry |
| `apps_shared/proof/proof_runner.py` | 60 | STATE_NODE | Observability | L_SHARED | Shared infra; high downstream blast radius |
| `apps_*/outputs/enterprise_*_renderer.py` (×4) | ~45 each | ORCHESTRATOR | Write | L_APP | Output rendering — cross-app duplication smell |
| `apps_underwriting_ai/reasoning/feature_interpreter.py` | 42 | CENTRAL_DEPENDENCY | Security (PII) | L_APP | Regulated-domain reasoning, PII-adjacent |

These hotspots **inform documentation priorities** in W1 (RUNBOOK + SLO must address them) but are NOT modified in this plan — code-shape changes are DEFERRED to W4.

---

## ADG_GRAPH_LAYER_EVIDENCE (constitutional §22)

Source: same SQLite snapshot. Direct query (MCP transport closed at plan time, §28 fallback used).

**Materialized views consulted** (≥3 required):
1. `mv_graph_reverse_dependency_hotspots` — informed CODEOWNERS prioritization (W1.7)
2. `mv_graph_critical_path_blast_radius` — confirmed apps_shared as L_SHARED (W3 purity gate justification)
3. `mv_hotspot_centrality` — apps_lic/tools/run_workflow_lic.py confirmed as orchestration centroid (W1.2 RUNBOOK priority)

**Semantic edges used:**
- `emits_side_effect` (2,482 edges across apps_*, excl apps_rg) — informed Wave 4.2 deferral
- `imports` (used in W3.1 purity gate query)
- `flows_to`, `reads_from`, `writes_to` — informed apps_underwriting_ai THREAT_MODEL.md PII flow analysis (W1.3)

**P-views cross-referenced:**
- `v_p1_mis_layered_infra` — apps_shared candidate file list for W3 gate
- `v_p2_duplicated_adapters` — informed W1.4 differentiation (the four `enterprise_*_renderer.py` are cross-app duplicates)

---

## Provenance

ADG Provenance: backend=sqlite, snapshot=adg_indexed_04292026_1606.sqlite

---

## Gap Register

| ID | Risk | Mitigation |
|----|------|------------|
| GAP-1 | SLO numbers without measurement infra are aspirational | Each SLO.md tagged "TARGETS, not measured" until W4.3 cost/latency telemetry lands |
| GAP-2 | Contract-test seed doesn't replace a real golden corpus | W2.1 explicitly labeled "seed" — golden corpus is W4.4 |
| GAP-3 | apps_lic THREAT_MODEL covers control-plane but not full hop registry | Scoped to W1.3; full hop-stage threat decomposition is post-W4 |
| GAP-4 | Property-based tests only on top-3 apps in W2.2 | Other 4 apps get contract-test only; property-based deferred to a NEXT_STEP |
