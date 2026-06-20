---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-lic-hop-domain-logic-b8c4c4.md'
original_relative_path: '_archive\\2026-05\\apps-lic-hop-domain-logic-b8c4c4.md'
source_sha256: 06f2ba99ae80110d1fa96331ec370f972406f488653595a1f4398a2f013d3ab9
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-lic-hop-domain-logic-b8c4c4
plan_type: refactor
---

# apps_lic HOP Engines — Real Domain Logic

Fills the 9 apps_lic HOP engines (landed as scaffolded in plan `apps-hop-substrate-f7751b` Wave 2) with real LLM generation, fact-check, hallucination detection, and compliance scanning.

---

## Context (SCQA)

- **Situation** — apps_lic 9-stage HOP pipeline is structurally complete (`apps_lic/config/hop_pipeline.py` + 9 engines + `LicCampaignOrchestrator` + `GovernedLicRun` wire-up with `hop_checkpoints` field). End-to-end smoke passes with 9/9 `COMPLETED` and `composite_score=1.0`. The 9 engines have correct I/O contracts but deterministic scaffold bodies — no LLM call, no real fact-check, no real compliance scan.
- **Complication** — The 2026-02-08 consolidation deleted the pre-refactor HOP1..HOP9 agent bodies and they are unrecoverable from git. Filling each engine requires Author-Gate decisions about provider/library/source choices (LLM gateway priority, hallucination detector, compliance keyword source) — each a distinct architecture call.
- **Question** — How do we fill the apps_lic HOP engines with production-grade domain logic without introducing provider lock-in, silently breaking compliance posture, or blowing latency budgets?
- **Answer** — Per-engine Author-Gate pass: each of HOP5 (generation), HOP6 (validation), HOP7 (gate_decision) surfaces as its own architecture_choice decision; HOP1..HOP4, HOP8, HOP9 get lighter decisions (prompt structure, evidence ordering, score weights). Each wave lands one engine end-to-end with unit + integration tests before moving to the next.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| `apps_lic/engines/*_engine.py` | current scaffold bodies | 🔲 |
| `apps_rg/engines/clerk_extraction_engine.py` + siblings | apps_rg is the working multi-hop reference | 🔲 |
| `agentic_core/L3_orchestration/inference/qwen_vllm/` | Qwen gateway to wire into HOP5 | 🔲 |
| `apps_lic/types/lic_models_types.py` | domain types (compliance levels, archetypes) | 🔲 |
| ADR-055 embedding model enforcement | constraint on validation embedding model | 🔲 |

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | HOP5 generation real LLM wiring | Qwen + Gemini fallback; prompt template resolver | A | ~12K 🟢 |
| Wave 2 | HOP6 validation + HOP7 gate semantics | Real fact-check against evidence_bundle + hallucination detector + compliance keyword scan | B | ~14K 🟢 |
| Wave 3 | HOP1-HOP4, HOP8, HOP9 real bodies | Lighter: profile feature extraction, evidence normalization, sender persona, routing, QA report, record assembly | C | ~10K 🟢 |

**Total: ~36K tokens across 3 waves**

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| 1.1 | Author-Gate — generation provider preference | (decision packet, no code) | AG-5 | ~1K | 🔲 TODO |
| 1.2 | Wire Qwen gateway into `generation_engine.py` | `apps_lic/engines/generation_engine.py` (edit) | PP-1 | ~6K | 🔲 TODO |
| 1.3 | Gemini fallback + prompt template resolver | `apps_lic/engines/generation_engine.py` (edit) | PP-1 | ~4K | 🔲 TODO |
| 1.4 | Integration + latency test | tests | PP-2 | ~1K | 🔲 TODO |
| 2.1 | Author-Gate — hallucination detector library | (decision packet) | AG-6 | ~1K | 🔲 TODO |
| 2.2 | Real fact-check against evidence_bundle | `apps_lic/engines/validation_engine.py` (edit) | PP-3 | ~6K | 🔲 TODO |
| 2.3 | Author-Gate — compliance keyword source | (decision packet) | AG-7 | ~1K | 🔲 TODO |
| 2.4 | Compliance scan in `gate_decision_engine.py` | edit | PP-4 | ~5K | 🔲 TODO |
| 2.5 | Tests | — | — | ~1K | 🔲 TODO |
| 3.1 | HOP1 profile feature extraction from campaign config | edit | PP-5 | ~2K | 🔲 TODO |
| 3.2 | HOP2 evidence normalization with reranking | edit | PP-5 | ~2K | 🔲 TODO |
| 3.3 | HOP3 sender persona from config + archetype | edit | PP-5 | ~2K | 🔲 TODO |
| 3.4 | HOP4 routing with real template resolution | edit | PP-5 | ~2K | 🔲 TODO |
| 3.5 | HOP8 real QA scorecard | edit | PP-5 | ~1K | 🔲 TODO |
| 3.6 | HOP9 real record assembly | edit | PP-5 | ~1K | 🔲 TODO |

---

## Gap Register

**GAP-1 — Provider preference**: Qwen (local, low-cost) vs Gemini (higher quality). apps_rg prefers Qwen with Gemini fallback. Wave 1.1 decides whether apps_lic follows or diverges.

**GAP-2 — Hallucination detector**: options include embedding-based similarity (fast, cheap), LLM-as-judge (slow, costly, higher quality), or rule-based entity extraction.

**GAP-3 — Compliance keyword source**: regulated-industry lists (LinkedIn-style outreach) are jurisdiction-specific. Options: hardcoded list, YAML config, external service.

---

## Rules

- Each Author-Gate sub-decision captured with `DECISION_CAPTURED:` marker.
- No breaking changes to `GovernedLicRun.run_governed_e2e` signature.
- `hop_checkpoints` shape preserved — only stage bodies change.
- Golden-output snapshot test per engine before edit.

---

## Success Criteria

- [ ] Real LLM draft emitted when retrieval bundle is non-empty.
- [ ] Fact-check catches at least 3 synthetic hallucinations in test fixture.
- [ ] Compliance gate halts when draft contains any keyword from the configured list.
- [ ] `composite_score` reflects actual quality, not scaffold's flat 1.0.
- [ ] 9 engines each have ≥2 unit tests.

---

## Rollback Strategy

Per-wave. Scaffold engines committed in plan `apps-hop-substrate-f7751b` are the known-good baseline. Reverting a wave reverts to scaffold.

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| HOP5 generation latency p95 | <3s on Qwen local | integration test |
| HOP6 fact-check precision on synthetic fixtures | ≥0.90 | unit test |
| HOP7 compliance gate false-positive rate | ≤0.05 on golden fixtures | unit test |

## Cursor Agent Alignment Checks

- Keep always-on rules lean; place detailed procedures in skills or workflows.
- Retrieve local or scoped evidence before synthesis.
- Prefer exact or structural matches before broad semantic expansion.
- For high-risk outputs, extract evidence or quotes before summarizing.
- Reserve deterministic enforcement for hooks or scripts, not template prose.
