# SVP Engineering Review — apps_rg

**Application:** apps_rg (AI Résumé Generator)
**Review Date:** 2026-05-02
**Status:** SVP+ candidate; doc package gap closed in this review
**Test Pass Rate:** unit tests under `tests/unit/apps_rg/` and `apps_rg/tests/`; coverage rollup TBD

---

## What's Specifically Hard About This Domain

apps_rg generates résumés — documents that represent a candidate to a hiring committee and must survive automated ATS screening before any human reads them. That sets a unique engineering bar:

1. **Fabrication is unrecoverable.** A résumé claim that doesn't trace to the candidate's actual history harms the candidate's interview preparation and creates trust risk if discovered. The fabrication validator REFUSES render, not just flags.
2. **ATS coverage is a structural floor, not an aesthetic.** Below ~80% keyword coverage of the target-role posting, the résumé does not reach a human. Generation that is "high-quality" but ATS-blind fails its job.
3. **Anti-overfitting matters more than per-section polish.** A résumé that compresses six positions into three inflated entries scores high on per-section quality but loses evidence density — and a real interviewer will notice.
4. **Candidate trust is the SLO, not raw latency.** A résumé must be trustworthy, every time. 30 extra seconds of generation is a fair trade for fabrication-zero.

This drives the architecture: 52 specialist engines under `engines/` (one per résumé concern — achievement prioritization, ATS coverage, length governance, etc.), evidence-binding at every claim site, anti-overfitting evidence-density gate, fabrication validator as a hard gate, ATS coverage gate.

## Non-Goals (deliberately out of scope)

- **Application portal submission.** Out of scope — apps_rg produces the document.
- **Recruiter follow-up workflow.** Different workflow (apps_lic).
- **Cover letter generation.** Lives in apps_lic outreach engine.
- **Self-improving optimization against a "résumé score".** Scores diverge from interview outcomes — autonomous optimization invites Goodhart's law.

## Alternatives Considered (and rejected)

### Alternative 1: Soft fabrication warning instead of hard gate
**Rejected:** soft warnings get ignored under deadline pressure. Hard gate refuses render; user must update the profile to support the claim.

### Alternative 2: Auto-pad ATS keywords to hit 80%
**Rejected:** keyword-stuffing without evidence is just fabrication with extra steps. Surface ATS gap as `[ATS_GAP]` markers; user decides whether to expand profile or accept the gap.

### Alternative 3: Single monolithic résumé engine
**Rejected:** monolithic engines diverge from per-domain rigor. apps_rg uses 52 specialist engines so each résumé concern (length, ATS, evidence, prioritization) has a dedicated, auditable surface.

## Architectural Differentiation From Peer Apps

apps_rg is the only app with:
- **Fabrication-zero enforcement as a hard gate** (candidate trust makes this non-negotiable)
- **ATS-coverage gate** (structural quality floor, not aesthetic)
- **Anti-overfitting evidence-density check** (claims-to-evidence ratio)
- **52 specialist engines** under `engines/` (per-concern decomposition)

apps_rg is the only app where **rendering with explicit gaps is preferable to rendering complete-but-fabricated**.

## SVP Standards Compliance

### 1. Domain Contracts

| Component | Status | Notes |
|-----------|--------|-------|
| ResumeRequest | ✅ | Input contract (candidate_name + target_role + target_industry + experience_level) |
| ResumeResult | ✅ | Output contract with gate_violations |
| AchievementClaim | ✅ | Evidence-binding (every claim traces to profile entry) |
| ATSCoverageReport | ✅ | Per-keyword coverage breakdown |
| ProfileEntry | ✅ | Source-of-truth claim ground truth |

### 2. Integration Adapters

| Adapter | Integration |
|---------|-------------|
| Hop integration adapters | Multi-stage pipeline orchestration |
| anti_overfitting.py | Evidence-density gate |
| ats_coverage.py | ATS coverage gate |
| anthropic_rag_entrypoint.py | Direct PromptEnvelope consumer |

### 3. Output Renderers

| Renderer | Formats | Purpose |
|----------|---------|---------|
| Markdown renderer | .md | Primary résumé output |
| Manifest renderer | JSON | Section + ATS-coverage manifest |

### 4. Configuration

| Config File | Purpose |
|-------------|---------|
| spine_manifest.yaml | Static spine-route claim (R3_grounded_read) |
| config/agent_spec_config.py | Agent specification |
| config/hop_pipeline.py | Multi-stage HOP pipeline definition |
| config/domain_contract/*.yaml | Domain contracts (capability/eval/fixtures/etc.) |

---

## Architecture Rigor

### Layer Alignment
- **L0 Routing:** AgenticRouter R3_grounded_read dispatch
- **L1 Cognition:** profile_planner, message_planner; query_planner.decompose_query consumer
- **L2 Execution:** HardenedanthropicexecutorStrategy
- **L3 Orchestration:** 52 specialist engines coordinated under reasoning/
- **L4 State:** Resume run summaries with provenance

### Key Design Principles

1. **Zero Fabrication:** every claim must trace to a profile entry; no exceptions
2. **Evidence-Based:** evidence-density score per claim, gated at floor
3. **Read-Only Spine Posture:** R3_grounded_read — no durable writes (per spine_manifest.yaml)
4. **Bounded:** length bounds, ATS coverage floor, evidence-density floor
5. **Traceable:** trace_id propagated through all artifacts

---

## Production Readiness

| Criterion | Status |
|-----------|--------|
| Type Safety | ✅ Pydantic contracts |
| Error Handling | ✅ Explicit gate violations |
| Observability | ✅ OTEL spans through bootstrap_runtime |
| Configurability | ✅ YAML configs under config/domain_contract |
| Documentation | ✅ This review (closed in 2026-05-02 doc package) |
| Test Coverage | 🟡 Unit tests in place; rollup pending |

---

## SVP Engineering Standards Checklist

- [x] Domain contracts with validators
- [x] Explicit validation (no silent exceptions)
- [x] Evidence-based decision tracking
- [x] Integration adapters for system handoff
- [x] Per-concern engine decomposition
- [x] YAML configuration
- [x] OTEL telemetry through bootstrap
- [x] Full provenance in all artifacts
- [x] Bounded numeric constraints (length, ATS coverage, evidence density)
- [x] Spine manifest claim (R3_grounded_read)
- [x] Companion docs (README, RUNBOOK, SLO, SVP review) — closed 2026-05-02

---

**Approved for Production Use**
*SVP Engineering Quality Certification — 2026-05-02*
