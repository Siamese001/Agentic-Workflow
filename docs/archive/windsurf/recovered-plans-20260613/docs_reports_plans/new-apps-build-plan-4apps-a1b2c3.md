# Build Plan: Four New Application Folders
**ADG Ingestion Date:** 2026-03-13
**ADG Artifact:** `adg_indexed_03132026_0745.sqlite` (8,059 modules, 220,147 relations, 0 layer violations)
**Plan Version:** 1.0
**Status:** DRAFT — Awaiting approval

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## ADG Architecture Findings (Basis for This Plan)

### Current App Portfolio (from ADG)

| App Folder | Modules (L_APP) | Domain |
|---|---|---|
| `apps_rg` | 275 | Resume Generation |
| `apps_lic` | 258 | LinkedIn Intelligent Campaigns |
| `apps_exec` | ~50 | Executive Brief Generator |
| `apps_rfp` | ~50 | RFP / Proposal Generator |
| `apps_research` | ~50 | Research Artifact Engine |
| `apps_eval` | ~50 | Evaluation Lab |
| `apps_shared` | 651 (L_SHARED) | Cross-app utilities, types, enforcement |

### ADG Structural Facts Driving Design

1. **Layer discipline:** 0 violations. L_APP imports only L_SHARED and L0–L6 core. New apps must follow the same gravity rules.
2. **Hottest shared symbol:** `apps_shared/types/sovereign_severity_types.py` (fan-out 1,146) — all new apps consume this.
3. **Canonical spine:** `apps_shared/spine/base_spine_adapter.py` + `CIDRegistry` + deterministic CID derivation — all new apps wire in via a named prefix.
4. **Control plane pattern:** `apps_lic/engines/control_plane.py` → `ControlPlane.evaluate_input/output` — new apps with sensitive data domains must replicate.
5. **Orchestrator pattern:** Multi-hop pipeline, explicit gate, `run_summary.json`, `trace_id`, `BriefStatus`-style enum, `hop_checkpoints` list.
6. **Guardian registry:** `apps_shared/config/app_guardian_registry.py` → `APP_GUARDIAN_REGISTRY` — every new app gets AGS check IDs appended.
7. **Dead import debt:** 4,466 dead import edges across the repo — new apps must be born clean (ruff F401 = zero on day one).
8. **Test coverage gap:** L_SHARED has many modules with zero `covers` edges — new apps must ship tests in `tests/<app>/`.

### Canonical App Folder Structure (from `apps/APPS_PORTFOLIO_OVERVIEW.md`)

```
apps_<name>/
├── config/
│   ├── __init__.py
│   ├── agent_spec_config.py        # Pydantic config schema, CLI defaults
│   └── reasoning_toggles_config.py # Feature flags, dry-run, gate modes
├── engines/
│   ├── __init__.py
│   ├── base_<name>_engine.py       # Abstract base, shared engine contract
│   └── <domain>_engine.py ...      # One file per pipeline stage
├── reasoning/
│   ├── __init__.py
│   ├── <Name>Orchestrator.py       # Primary multi-hop orchestrator
│   ├── <Name>HealingOrchestrator.py
│   └── <AgentName>Agent.py ...
├── scripts/
│   ├── __init__.py
│   └── run_<name>.py               # CLI entrypoint
├── types/
│   ├── __init__.py
│   └── <name>_types.py             # Pydantic models: Request, Result, Status enum, RunSummary
├── validators/
│   ├── __init__.py
│   └── <gate>_validator.py
├── __init__.py
├── __main__.py                     # `python -m apps_<name>` entrypoint
├── README.md
├── PRODUCT_SPEC.md
├── OUTPUT_CONTRACTS.md
├── CLI_SPEC.md
└── TEST_STRATEGY.md
```

---

## Global Design Rules (All Four New Apps)

These rules are **non-negotiable** and mirror `apps/APPS_PORTFOLIO_OVERVIEW.md §Global Design Rules`:

| Rule | Enforcement |
|---|---|
| No silent fallback | Gate failures stop the pipeline; violations listed in `run_summary.json` |
| No fake success states | Status enums: `GENERATING`, `GATE_CHECKING`, `COMPLETE`, `DRY_RUN`, `FAILED` |
| Provenance on every output | `run_summary.json` always written with `provenance`, `trace_id`, `app` key |
| Dry-run support | `--dry-run` flag; dry-run never writes artifact files |
| Deterministic trace IDs | SHA-256 of canonical request fields; first 16 chars used |
| Explicit quality gates | Named validator with rule IDs (`<APP>-GATE-001` etc.) |
| Explicit failure reporting | Exit codes: 0=success, 1=gate failure, 2=regression |
| Testable acceptance criteria | Every spec has ≥5 assertion-level criteria |
| Spine adapter required | Subclass `BaseSpineAdapter` with named prefix `"<app>-"` |
| Layer gravity respected | L_APP may only import L_SHARED, L0–L6 |
| AGS check IDs registered | Add entries to `APP_GUARDIAN_REGISTRY` in `apps_shared/config/app_guardian_registry.py` |
| Zero dead imports at launch | ruff F401 = 0 on initial commit |
| ADG re-scan after each phase | Run `python tools/generate_full_adg.py` after phase completion |

---

## App 1: `apps_coaching` — Career Coaching & Interview Prep Engine

### Product Purpose
Generates personalised coaching plans, STAR-method interview answers, and salary negotiation scripts from a candidate profile + target role. Complements `apps_rg` (resumes) and `apps_lic` (campaigns) to complete the job-search lifecycle.

### Reviewer Persona
Career coaches, HR tech leads, senior hiring-panel reviewers wanting to see end-to-end candidate-journey tooling.

### Domain Rationale (ADG-grounded)
- `apps_rg` engines (`skill_score_normalizer`, `competency_item`, `gap_closure_engine`) are callable from `apps_shared` but unused beyond resume context — coaching engine reuses these as read-only inputs.
- `apps_shared/utils/tone_voice_util.py` (20 KB) already encodes tone models; coaching uses `COACHING` tone profile.
- `apps_shared/validators/talent_signal_enhancer_validator.py` (13 KB) covers signal quality checks applicable to coaching session validation.

### Pipeline Stages (Multi-Hop)

| Hop | Engine | Input → Output |
|---|---|---|
| HOP-1 | `ProfileIngestionEngine` | Candidate JSON + job description → `ProfileContext` |
| HOP-2 | `GapAnalysisEngine` | `ProfileContext` → `SkillGapMatrix` |
| HOP-3 | `CoachingPlanEngine` | `SkillGapMatrix` → `CoachingPlan` (structured sections) |
| HOP-4 | `InterviewPrepEngine` | `CoachingPlan` + JD → `STARAnswerSet` |
| HOP-5 | `NegotiationScriptEngine` | `ProfileContext` + market data → `NegotiationScript` |
| HOP-6 | `CoachingGateValidator` | All outputs → `GateResult` |
| HOP-7 | `ArtifactEmitter` | Validated outputs → `.md` + `.json` artifacts |

### File Manifest

```
apps_coaching/
├── config/
│   ├── __init__.py
│   ├── agent_spec_config.py
│   └── reasoning_toggles_config.py
├── engines/
│   ├── __init__.py
│   ├── base_coaching_engine.py
│   ├── profile_ingestion_engine.py
│   ├── gap_analysis_engine.py
│   ├── coaching_plan_engine.py
│   ├── interview_prep_engine.py
│   ├── negotiation_script_engine.py
│   └── artifact_emitter_engine.py
├── reasoning/
│   ├── __init__.py
│   ├── CoachingOrchestrator.py
│   ├── CoachingHealingOrchestrator.py
│   ├── GapAnalysisAgent.py
│   ├── InterviewPrepAgent.py
│   ├── NegotiationAgent.py
│   ├── CoachingReflectionAgent.py
│   └── coaching_spine_adapter.py
├── scripts/
│   ├── __init__.py
│   └── run_coaching.py
├── types/
│   ├── __init__.py
│   └── coaching_types.py          # CoachingRequest, CoachingResult, CoachingStatus, STARAnswer, RunSummary
├── validators/
│   ├── __init__.py
│   └── coaching_gate_validator.py  # Rules: COACH-GATE-001..005
├── __init__.py
├── __main__.py
├── README.md
├── PRODUCT_SPEC.md
├── OUTPUT_CONTRACTS.md
├── CLI_SPEC.md
└── TEST_STRATEGY.md
```

### Output Contracts

| Artifact | Path Pattern | Format |
|---|---|---|
| Coaching plan | `reports/coaching/coaching_plan_<trace>.md` | Markdown |
| STAR answers | `reports/coaching/star_answers_<trace>.json` | JSON |
| Negotiation script | `reports/coaching/negotiation_<trace>.md` | Markdown |
| Run summary | `reports/coaching/run_summary_<trace>.json` | JSON |

### Quality Gates (`CoachingGateValidator`)

| Rule ID | Check | Severity |
|---|---|---|
| COACH-GATE-001 | Coaching plan has ≥3 distinct skill sections | HIGH |
| COACH-GATE-002 | Each STAR answer has all four components (S, T, A, R) | HIGH |
| COACH-GATE-003 | No PII in negotiation script (routed through `ControlPlane`) | CRITICAL |
| COACH-GATE-004 | Quality score ≥ 0.75 | MEDIUM |
| COACH-GATE-005 | All sections tagged `is_deterministic` | LOW |

### CLI

```bash
python -m apps_coaching \
  --profile data/candidate.json \
  --job-description "Senior Platform Engineer at Acme Corp" \
  --mode full \
  --dry-run
```

### Spine Adapter
`CoachingSpineAdapter(prefix="coaching-")` subclasses `BaseSpineAdapter`.

### AGS IDs to Register
`AGS-010` (apps_coaching), `AGS-011` (apps_coaching PII gate compliance)

### Test Targets (in `tests/apps_coaching/`)
- `test_coaching_orchestrator.py` — end-to-end dry-run, gate pass, gate fail
- `test_gap_analysis_engine.py` — unit: known skill gaps detected correctly
- `test_interview_prep_engine.py` — STAR structure completeness
- `test_coaching_gate_validator.py` — all 5 rules individually

---

## App 2: `apps_intel` — Market Intelligence & Competitive Analysis Engine

### Product Purpose
Generates structured competitive intelligence reports: market landscape, competitor positioning matrices, SWOT analyses, and emerging-trend radars. Combines web-grounded retrieval (via `apps_shared/utils/graph_rag_fusion_util.py`) with sovereign synthesis.

### Reviewer Persona
Strategy leads, VC analysts, AI platform PMs evaluating platform depth for business intelligence use cases.

### Domain Rationale (ADG-grounded)
- `apps_shared/utils/graph_rag_fusion_util.py` (19 KB) already implements GraphRAG + BM25 hybrid fusion — `apps_intel` is the primary consumer that exercises this fully.
- `apps_shared/utils/late_interaction_reranker_util.py` (9 KB) — ColBERT-style late-interaction reranking, purpose-built for ranked intelligence signals.
- `apps_shared/utils/signal_weighter_util.py` (15 KB) — multi-signal weighting, directly applicable to competitive signal aggregation.
- `apps_research` covers generic research; `apps_intel` specialises on competitive/market domains with structured output schemas.

### Pipeline Stages (Multi-Hop)

| Hop | Engine | Input → Output |
|---|---|---|
| HOP-1 | `QueryExpansionEngine` | Raw topic + scope → `ExpandedQuerySet` |
| HOP-2 | `GroundedRetrievalEngine` | `ExpandedQuerySet` → `RetrievedEvidenceCorpus` (GraphRAG) |
| HOP-3 | `SignalRankingEngine` | `RetrievedEvidenceCorpus` → `RankedSignalSet` |
| HOP-4 | `CompetitorMatrixEngine` | `RankedSignalSet` → `CompetitorMatrix` |
| HOP-5 | `SWOTEngine` | `CompetitorMatrix` → `SWOTAnalysis` |
| HOP-6 | `TrendRadarEngine` | `RankedSignalSet` → `TrendRadar` |
| HOP-7 | `IntelGateValidator` | All outputs → `GateResult` |
| HOP-8 | `ArtifactEmitter` | Validated outputs → `.md` + `.json` artifacts |

### File Manifest

```
apps_intel/
├── config/
│   ├── __init__.py
│   ├── agent_spec_config.py
│   └── reasoning_toggles_config.py
├── engines/
│   ├── __init__.py
│   ├── base_intel_engine.py
│   ├── query_expansion_engine.py
│   ├── grounded_retrieval_engine.py    # wraps graph_rag_fusion_util
│   ├── signal_ranking_engine.py        # wraps late_interaction_reranker_util
│   ├── competitor_matrix_engine.py
│   ├── swot_engine.py
│   ├── trend_radar_engine.py
│   └── artifact_emitter_engine.py
├── reasoning/
│   ├── __init__.py
│   ├── IntelOrchestrator.py
│   ├── IntelHealingOrchestrator.py
│   ├── QueryExpansionAgent.py
│   ├── CompetitorAnalysisAgent.py
│   ├── TrendSynthesisAgent.py
│   ├── IntelReflectionAgent.py
│   └── intel_spine_adapter.py
├── scripts/
│   ├── __init__.py
│   └── run_intel.py
├── types/
│   ├── __init__.py
│   └── intel_types.py         # IntelRequest, IntelResult, IntelStatus, CompetitorEntry, TrendSignal, RunSummary
├── validators/
│   ├── __init__.py
│   └── intel_gate_validator.py # INTEL-GATE-001..006
├── __init__.py
├── __main__.py
├── README.md
├── PRODUCT_SPEC.md
├── OUTPUT_CONTRACTS.md
├── CLI_SPEC.md
└── TEST_STRATEGY.md
```

### Output Contracts

| Artifact | Path Pattern | Format |
|---|---|---|
| Intel report | `reports/intel/intel_report_<mode>_<trace>.md` | Markdown |
| Competitor matrix | `reports/intel/competitor_matrix_<trace>.json` | JSON |
| SWOT analysis | `reports/intel/swot_<trace>.json` | JSON |
| Trend radar | `reports/intel/trend_radar_<trace>.json` | JSON |
| Run summary | `reports/intel/run_summary_<trace>.json` | JSON |

### Quality Gates (`IntelGateValidator`)

| Rule ID | Check | Severity |
|---|---|---|
| INTEL-GATE-001 | ≥3 competitors identified in matrix | HIGH |
| INTEL-GATE-002 | Each SWOT quadrant has ≥2 items | HIGH |
| INTEL-GATE-003 | Trend radar has ≥5 signals with confidence scores | MEDIUM |
| INTEL-GATE-004 | All claims have epistemic type label (`direct_evidence`, `inference`, `assumption`) | HIGH |
| INTEL-GATE-005 | Groundedness score ≥ 0.70 (from `scores_groundedness` ADG edge pattern) | MEDIUM |
| INTEL-GATE-006 | Quality score ≥ 0.75 | MEDIUM |

### CLI

```bash
python -m apps_intel \
  --topic "Agentic AI platforms" \
  --mode competitive \
  --competitors "LangChain,AutoGen,CrewAI,LlamaIndex" \
  --dry-run
```

### Spine Adapter
`IntelSpineAdapter(prefix="intel-")` subclasses `BaseSpineAdapter`.

### AGS IDs to Register
`AGS-012` (apps_intel layer compliance), `AGS-013` (apps_intel groundedness gate)

### Test Targets (in `tests/apps_intel/`)
- `test_intel_orchestrator.py` — end-to-end dry-run, full run with mocked retrieval
- `test_signal_ranking_engine.py` — ranking order correctness
- `test_competitor_matrix_engine.py` — matrix structure validation
- `test_intel_gate_validator.py` — all 6 gate rules individually

---

## App 3: `apps_comply` — Regulatory Compliance & Risk Documentation Engine

### Product Purpose
Generates structured regulatory compliance assessments, risk registers, and gap analysis reports from a system description + target regulatory framework (SOC 2, HIPAA, GDPR, ISO 27001, EU AI Act). Demonstrates the platform's governance-first posture in enterprise/regulated markets.

### Reviewer Persona
CTOs at regulated enterprises, Heads of AI Risk, compliance officers evaluating AI platform vendor governance posture.

### Domain Rationale (ADG-grounded)
- `apps_shared/utils/input_guardrail_util.py` (18 KB) + `apps_shared/utils/injection_patterns_util.py` (2 KB) — already implemented; compliance engine leverages for input sanitisation.
- `apps_shared/utils/secure_config_manager_util.py` (13 KB) — secure config patterns applicable to handling sensitive compliance artifacts.
- ADG shows `applies_guardrail: 68` edges — this app becomes the primary showcase for the guardrail plane.
- ADG shows `reads_policy_state: 1,191` edges — compliance engine exercises this at scale.
- ADG shows `escalates_to_human: 12` edges — compliance gate introduces human-review triggers for critical regulatory gaps.

### Pipeline Stages (Multi-Hop)

| Hop | Engine | Input → Output |
|---|---|---|
| HOP-1 | `SystemDescriptionIngestionEngine` | System description doc + framework choice → `SystemProfile` |
| HOP-2 | `ControlMappingEngine` | `SystemProfile` + framework controls → `ControlMappingMatrix` |
| HOP-3 | `GapAnalysisEngine` | `ControlMappingMatrix` → `ComplianceGapList` |
| HOP-4 | `RiskRegisterEngine` | `ComplianceGapList` → `RiskRegister` |
| HOP-5 | `RemediationPlanEngine` | `RiskRegister` → `RemediationRoadmap` |
| HOP-6 | `HumanEscalationEngine` | Critical gaps → escalation flags (ties to `escalates_to_human` ADG plane) |
| HOP-7 | `ComplyGateValidator` | All outputs → `GateResult` |
| HOP-8 | `ArtifactEmitter` | Validated outputs → `.md` + `.json` + `.csv` artifacts |

### File Manifest

```
apps_comply/
├── config/
│   ├── __init__.py
│   ├── agent_spec_config.py
│   ├── framework_definitions_config.py  # SOC2, HIPAA, GDPR, ISO27001, EU_AI_ACT control lists
│   └── reasoning_toggles_config.py
├── engines/
│   ├── __init__.py
│   ├── base_comply_engine.py
│   ├── system_description_ingestion_engine.py
│   ├── control_mapping_engine.py
│   ├── gap_analysis_engine.py
│   ├── risk_register_engine.py
│   ├── remediation_plan_engine.py
│   ├── human_escalation_engine.py
│   └── artifact_emitter_engine.py
├── reasoning/
│   ├── __init__.py
│   ├── ComplyOrchestrator.py
│   ├── ComplyHealingOrchestrator.py
│   ├── ControlMappingAgent.py
│   ├── RiskAssessmentAgent.py
│   ├── RemediationPlannerAgent.py
│   ├── ComplyReflectionAgent.py
│   └── comply_spine_adapter.py
├── scripts/
│   ├── __init__.py
│   └── run_comply.py
├── types/
│   ├── __init__.py
│   └── comply_types.py   # ComplyRequest, ComplyResult, ComplyStatus, ControlGap, RiskItem, RunSummary
├── validators/
│   ├── __init__.py
│   └── comply_gate_validator.py   # COMPLY-GATE-001..007
├── __init__.py
├── __main__.py
├── README.md
├── PRODUCT_SPEC.md
├── OUTPUT_CONTRACTS.md
├── CLI_SPEC.md
└── TEST_STRATEGY.md
```

### Output Contracts

| Artifact | Path Pattern | Format |
|---|---|---|
| Compliance assessment | `reports/comply/compliance_<framework>_<trace>.md` | Markdown |
| Control mapping matrix | `reports/comply/control_matrix_<trace>.json` | JSON |
| Risk register | `reports/comply/risk_register_<trace>.csv` | CSV |
| Remediation roadmap | `reports/comply/remediation_<trace>.json` | JSON |
| Escalation flags | `reports/comply/escalations_<trace>.json` | JSON |
| Run summary | `reports/comply/run_summary_<trace>.json` | JSON |

### Quality Gates (`ComplyGateValidator`)

| Rule ID | Check | Severity |
|---|---|---|
| COMPLY-GATE-001 | Framework recognised and controls loaded (non-empty) | CRITICAL |
| COMPLY-GATE-002 | All critical controls have a gap status (PASS/FAIL/PARTIAL) | CRITICAL |
| COMPLY-GATE-003 | Risk register contains severity scores (LOW/MEDIUM/HIGH/CRITICAL) | HIGH |
| COMPLY-GATE-004 | Each CRITICAL gap has a remediation action | HIGH |
| COMPLY-GATE-005 | Human escalation flags raised for ≥1 CRITICAL unmitigated gap | HIGH |
| COMPLY-GATE-006 | No PII in artifacts (ControlPlane.evaluate_output) | CRITICAL |
| COMPLY-GATE-007 | Quality score ≥ 0.80 | MEDIUM |

### CLI

```bash
python -m apps_comply \
  --system-description docs/architecture/system_overview.md \
  --framework GDPR \
  --mode gap_analysis \
  --dry-run
```

### Spine Adapter
`ComplySpineAdapter(prefix="comply-")` subclasses `BaseSpineAdapter`.
**Additional:** `ControlPlane` wired for both `evaluate_input` and `evaluate_output` (sensitive domain).

### AGS IDs to Register
`AGS-014` (apps_comply layer compliance), `AGS-015` (apps_comply PII gate), `AGS-016` (apps_comply human escalation wiring)

### Test Targets (in `tests/apps_comply/`)
- `test_comply_orchestrator.py` — dry-run, GDPR run, SOC2 run (mocked LLM)
- `test_control_mapping_engine.py` — all 5 framework control lists load correctly
- `test_risk_register_engine.py` — severity scoring logic unit tests
- `test_comply_gate_validator.py` — all 7 rules individually

---

## App 4: `apps_onboard` — Employee & System Onboarding Workflow Engine

### Product Purpose
Generates structured onboarding programmes for new employees or new system integrations. For people onboarding: role-specific 30-60- plans, stakeholder maps, knowledge transfer checklists. For system onboarding: dependency maps, integration runbooks, rollback procedures. Targets enterprise platform teams and HR automation buyers.

### Reviewer Persona
Heads of Engineering, HR automation leads, platform engineering managers evaluating workflow automation depth.

### Domain Rationale (ADG-grounded)
- `apps_shared/utils/async_coordinator_util.py` (13 KB) — multi-agent coordination patterns applicable to parallel onboarding task generation.
- `apps_shared/utils/mutation_phase_util.py` (11 KB) — phased mutation / rollback patterns directly map to 30-60- phase model.
- `apps_shared/utils/checkpoint_integrity_error_validator.py` (via validators) — checkpoint-driven progress gates.
- ADG shows `stamps_work_contract: 13` edges — onboarding engine introduces `WorkContractStamper` as a new consumer.
- `apps_shared/utils/waterfall_reconciliation_util.py` (9 KB) — reconciliation patterns map to onboarding dependency resolution.

### Pipeline Stages (Multi-Hop)

| Hop | Engine | Input → Output |
|---|---|---|
| HOP-1 | `RoleProfileIngestionEngine` | Role spec + org chart → `RoleContext` |
| HOP-2 | `StakeholderMapEngine` | `RoleContext` → `StakeholderMap` |
| HOP-3 | `KnowledgeTransferPlanEngine` | `RoleContext` + knowledge base → `KTPlan` |
| HOP-4 | `PhasedPlanEngine` | `KTPlan` → `OnboardingPlan` (30/60/ phases) |
| HOP-5 | `DependencyRunbookEngine` | System description → `IntegrationRunbook` (system mode) |
| HOP-6 | `CheckpointGateEngine` | Phase milestones → validated `CheckpointSet` |
| HOP-7 | `OnboardGateValidator` | All outputs → `GateResult` |
| HOP-8 | `ArtifactEmitter` | Validated outputs → `.md` + `.json` artifacts |

### File Manifest

```
apps_onboard/
├── config/
│   ├── __init__.py
│   ├── agent_spec_config.py
│   └── reasoning_toggles_config.py
├── engines/
│   ├── __init__.py
│   ├── base_onboard_engine.py
│   ├── role_profile_ingestion_engine.py
│   ├── stakeholder_map_engine.py
│   ├── knowledge_transfer_plan_engine.py
│   ├── phased_plan_engine.py
│   ├── dependency_runbook_engine.py
│   ├── checkpoint_gate_engine.py
│   └── artifact_emitter_engine.py
├── reasoning/
│   ├── __init__.py
│   ├── OnboardOrchestrator.py
│   ├── OnboardHealingOrchestrator.py
│   ├── StakeholderMapAgent.py
│   ├── KnowledgeTransferAgent.py
│   ├── PhasedPlanAgent.py
│   ├── OnboardReflectionAgent.py
│   └── onboard_spine_adapter.py
├── scripts/
│   ├── __init__.py
│   └── run_onboard.py
├── types/
│   ├── __init__.py
│   └── onboard_types.py   # OnboardRequest, OnboardResult, OnboardStatus, Phase, Checkpoint, RunSummary
├── validators/
│   ├── __init__.py
│   └── onboard_gate_validator.py  # ONBOARD-GATE-001..005
├── __init__.py
├── __main__.py
├── README.md
├── PRODUCT_SPEC.md
├── OUTPUT_CONTRACTS.md
├── CLI_SPEC.md
└── TEST_STRATEGY.md
```

### Output Contracts

| Artifact | Path Pattern | Format |
|---|---|---|
| Onboarding plan | `reports/onboard/onboard_plan_<role>_<trace>.md` | Markdown |
| Stakeholder map | `reports/onboard/stakeholder_map_<trace>.json` | JSON |
| Knowledge transfer plan | `reports/onboard/kt_plan_<trace>.md` | Markdown |
| Integration runbook | `reports/onboard/runbook_<trace>.md` | Markdown (system mode) |
| Checkpoints | `reports/onboard/checkpoints_<trace>.json` | JSON |
| Run summary | `reports/onboard/run_summary_<trace>.json` | JSON |

### Quality Gates (`OnboardGateValidator`)

| Rule ID | Check | Severity |
|---|---|---|
| ONBOARD-GATE-001 | All three phases (30/60/90) have ≥3 milestones | HIGH |
| ONBOARD-GATE-002 | Stakeholder map has ≥1 primary sponsor | HIGH |
| ONBOARD-GATE-003 | Knowledge transfer plan has ≥5 items | MEDIUM |
| ONBOARD-GATE-004 | Each checkpoint has an owner and due-date field | MEDIUM |
| ONBOARD-GATE-005 | Quality score ≥ 0.75 | MEDIUM |

### CLI

```bash
# People onboarding
python -m apps_onboard \
  --mode people \
  --role "Senior Platform Engineer" \
  --start-date 2026-04-01 \
  --dry-run

# System onboarding
python -m apps_onboard \
  --mode system \
  --system-spec docs/architecture/system_overview.md \
  --dry-run
```

### Spine Adapter
`OnboardSpineAdapter(prefix="onboard-")` subclasses `BaseSpineAdapter`.

### AGS IDs to Register
`AGS-017` (apps_onboard layer compliance), `AGS-018` (apps_onboard checkpoint gate wiring)

### Test Targets (in `tests/apps_onboard/`)
- `test_onboard_orchestrator.py` — people mode dry-run, system mode dry-run, gate fail
- `test_phased_plan_engine.py` — 30/60/90 structure completeness
- `test_checkpoint_gate_engine.py` — milestone validation logic
- `test_onboard_gate_validator.py` — all 5 gate rules individually

---

## Phased Delivery Schedule

### Phase 1 — Foundation (all four apps in parallel stubs)

**Goal:** Scaffold directory structure, `__init__.py`, `__main__.py`, `types/`, `config/` for all four apps. No LLM calls. Dry-run returns status `DRY_RUN`. Tests skeleton passes.

**Acceptance criteria:**
1. `python -m apps_coaching --dry-run` exits 0
2. `python -m apps_intel --dry-run` exits 0
3. `python -m apps_comply --dry-run` exits 0
4. `python -m apps_onboard --dry-run` exits 0
5. `ruff check apps_coaching apps_intel apps_comply apps_onboard` = 0 violations
6. ADG re-scan shows 4 new L_APP folders, 0 new layer violations

**Files to create per app:** `__init__.py`, `__main__.py`, `config/__init__.py`, `config/agent_spec_config.py`, `types/__init__.py`, `types/<app>_types.py`, `scripts/__init__.py`, `scripts/run_<app>.py`

---

### Phase 2 — Engines (one app at a time: coaching → intel → comply → onboard)

**Goal:** Implement all engine files for each app. Engines must be unit-testable in isolation (mock LLM via `apps_shared/utils/unified_executor_util.py`).

**Acceptance criteria per app:**
1. All engine files exist and import cleanly
2. Each engine has a `execute(input) -> output` method
3. Unit tests pass with mocked LLM responses
4. No new dead imports introduced

---

### Phase 3 — Orchestrators & Spine Adapters

**Goal:** Implement `<Name>Orchestrator.py` for all four apps. Wire spine adapters. Wire `ControlPlane` for `apps_comply`.

**Acceptance criteria:**
1. End-to-end pipeline runs with mocked LLM: `COMPLETE` status
2. `run_summary.json` written with `provenance`, `trace_id`, `app` keys
3. Spine adapter CID is deterministic for same input

---

### Phase 4 — Gate Validators & Quality Gates

**Goal:** Implement all `*_gate_validator.py` files with named rule IDs. Hard-fail mode enforced.

**Acceptance criteria:**
1. Gate passes with valid mocked output
2. Gate fails with injected bad output; `result.status = FAILED`
3. All violations appear in `run_summary.json.gate_violations`

---

### Phase 5 — Documentation & AGS Registration

**Goal:** Write `README.md`, `PRODUCT_SPEC.md`, `OUTPUT_CONTRACTS.md`, `CLI_SPEC.md`, `TEST_STRATEGY.md` for all four apps. Register AGS check IDs in `apps_shared/config/app_guardian_registry.py`. Update `apps/APPS_PORTFOLIO_OVERVIEW.md`.

**Acceptance criteria:**
1. All 5 spec docs present per app
2. `APP_GUARDIAN_REGISTRY` has new entries AGS-010 through AGS-018
3. `APPS_PORTFOLIO_OVERVIEW.md` table updated with 4 new apps

---

### Phase 6 — ADG Re-scan & Final Verification

**Goal:** Re-run ADG scan, verify 0 new layer violations, update snapshot.

```bash
python tools/generate_full_adg.py
```

**Acceptance criteria:**
1. `layer_violation_count` remains 0
2. New apps appear in L_APP layer count
3. Spine adapters appear in `implements` edge plane
4. Gate validators appear in `validates_blast_radius` or `applies_guardrail` planes

---

## Cross-App Integration Points

| Integration | From | To | Mechanism |
|---|---|---|---|
| Resume→Coaching skill gap | `apps_rg` output | `apps_coaching` HOP-2 input | JSON artifact hand-off via shared `reports/` path |
| Campaign+Coaching lifecycle | `apps_lic` + `apps_coaching` | `apps_intel` (market signals) | `IntelRequest` can accept LIC campaign data as market signal |
| Compliance review of RFP | `apps_rfp` output | `apps_comply` HOP-1 input | RFP proposal fed as "system description" |
| Onboard knowledge base | `apps_research` output | `apps_onboard` HOP-3 input | Research artifact fed as knowledge base for KT plan |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| apps_shared L_SHARED fan-out grows beyond 1,200 (currently 1,146) | HIGH | MEDIUM | Add new shared symbols only when ≥2 new apps need them; use app-local utils first |
| New engines duplicate existing apps_shared utils | MEDIUM | MEDIUM | Run `dedup-guard` skill before creating each engine file |
| Layer violation from new apps importing L_SL | LOW | HIGH | ADG re-scan required after each phase; CI gate blocks merge |
| Dead imports accumulate | MEDIUM | LOW | `ruff --select F401` in pre-commit config; enforced at Phase 1 |
| Test coverage stays near zero | HIGH | MEDIUM | Phase 2 acceptance criteria require unit tests before engine merge |

## Gap Register

| Gap | Priority | Impact | Status |
|------|----------|--------|---------|
| [Gap 1] | High | Critical | Open |
| [Gap 2] | Medium | Moderate | In Progress |

---

## Execution Plan

1. **Phase 1**: Analysis and Planning
2. **Phase 2**: Implementation
3. **Phase 3**: Testing and Validation
4. **Phase 4**: Documentation and Cleanup

---

