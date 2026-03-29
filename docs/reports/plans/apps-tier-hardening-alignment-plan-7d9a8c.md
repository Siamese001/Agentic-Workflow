# Apps Tier Hardening Plan — Structural Alignment with apps_lic/apps_rg Gold Standard

## Executive Summary

This plan hardens apps_eval, apps_exec, apps_research, and apps_rfp to match the architectural rigor, depth, and integration quality of apps_lic and apps_rg (the original gold-standard apps).

**Target State:** All apps_* folders achieve:
- Full lifecycle trace contract integration (P0-P4)
- Complete ADG edge coverage (31/31 dimensions at 100%)
- Structural depth parity (services/, enforcement/, reasoning/ agents)
- End-to-end integration test coverage
- Sovereign territory compliance per Structure Blueprint

---

## Gap Analysis Summary

| Dimension | apps_lic | apps_rg | apps_eval | apps_exec | apps_research | apps_rfp |
|-----------|----------|---------|-----------|-----------|---------------|----------|
| config/ files | 11 | 3 | 3 | 4 | 3 | 3 |
| engines/ files | 5 | 45 | 4 | 4 | 2 | 2 |
| reasoning/ agents | 33 | 21 | 1 | 1 | 1 | 1 |
| services/ files | 42 | 28 | 0 | 0 | 0 | 0 |
| types/ files | 20 | 15 | 1 | 2 | 2 | 2 |
| utils/ files | 8 | 10 | 1 | 1 | 1 | 1 |
| validators/ files | 5 | 4 | 1 | 1 | 1 | 1 |
| enforcement/ | No | Yes | No | No | No | No |
| Full lifecycle trace | Partial | Full | Minimal | Minimal | Minimal | Minimal |

---

## Phase 1: Foundation & Config Hardening

### 1.1 Lifecycle Trace Contract Integration
**Scope:** All apps_*/config/agent_spec_config.py

**Pattern (from apps_rg):**
```python
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_reads_policy_state,
    _emit_snapshots_state,
    # ... all 31 emitters
)

# Self-bootstrap calls for P0-P4 coverage
_emit_applies_guardrail("p0", "agent_spec_config", "p0_governance")
_emit_reads_policy_state("p0", "agent_spec_config", "policy_binding")
# ... all 31 dimensions
```

**Per-App Target:**
- apps_eval: Add 90+ _emit_* calls for P0-P4 coverage
- apps_exec: Add 90+ _emit_* calls for P0-P4 coverage
- apps_research: Add 90+ _emit_* calls for P0-P4 coverage
- apps_rfp: Add 90+ _emit_* calls for P0-P4 coverage

### 1.2 Agent Spec Schema Completion
**Pattern (from apps_rg):**
- Pydantic BaseModel with Field validators
- model_validator for cross-field validation
- LayerSegment imports for trace context
- Full __all__ exports

**Implementation:**
Each app's config must define:
- Root config class (e.g., `EvalAgentSpecs`, `ExecAgentSpecs`)
- Sub-configs for each capability area
- Validation methods with trace emission

---

## Phase 2: Structural Depth (services/, enforcement/)

### 2.1 services/ Layer Construction
**Gold Standard Pattern (apps_lic):**
- Services as discrete capability units
- Each service has single responsibility
- Unified error handling via SovereignBase patterns
- Trace emission at entry/exit points

**Implementation Per App:**

**apps_eval/services/:**
- `test_discovery_service.py` - Discover and catalog tests
- `scenario_loader_service.py` - Load test scenarios
- `metric_collector_service.py` - Collect evaluation metrics
- `benchmark_runner_service.py` - Execute benchmarks
- `result_aggregator_service.py` - Aggregate results
- `regression_detector_service.py` - Detect regressions
- `coverage_analyzer_service.py` - Analyze coverage
- `quality_assessor_service.py` - Assess output quality

**apps_exec/services/:**
- `document_ingestion_service.py` - Ingest source docs
- `capability_extractor_service.py` - Extract capabilities
- `audience_analyzer_service.py` - Analyze target audience
- `content_synthesizer_service.py` - Synthesize content
- `brief_assembler_service.py` - Assemble executive briefs
- `evidence_collector_service.py` - Collect evidence
- `style_validator_service.py` - Validate style compliance
- `artifact_exporter_service.py` - Export final artifacts

**apps_research/services/:**
- `source_discovery_service.py` - Discover research sources
- `content_harvester_service.py` - Harvest content
- `credibility_scorer_service.py` - Score source credibility
- `insight_extractor_service.py` - Extract insights
- `synthesis_engine_service.py` - Synthesize findings
- `citation_manager_service.py` - Manage citations
- `knowledge_integrator_service.py` - Integrate knowledge
- `report_compiler_service.py` - Compile research reports

**apps_rfp/services/:**
- `requirement_parser_service.py` - Parse RFP requirements
- `compliance_checker_service.py` - Check compliance
- `capability_mapper_service.py` - Map capabilities
- `proposal_architect_service.py` - Architect proposals
- `response_generator_service.py` - Generate responses
- `differentiation_analyzer_service.py` - Analyze differentiation
- `risk_assessor_service.py` - Assess risks
- `submission_validator_service.py` - Validate submissions

### 2.2 enforcement/ Layer (Optional Enhancement)
**Pattern (from apps_rg):**
- Strategy pattern for enforcement
- Hardened executors with safety checks
- Boundary validation

**Decision:** Add to apps_eval first (evaluation safety critical), others as needed.

---

## Phase 3: Agent Ecosystem Expansion

### 3.1 Reasoning Layer Agents
**Gold Standard:** apps_lic has 33 agents across HOP pipeline

**apps_eval/reasoning/:**
- `TestDiscoveryAgent.py` - Discover tests from ADG
- `ScenarioGenerationAgent.py` - Generate test scenarios
- `BaselineCaptureAgent.py` - Capture performance baselines
- `RegressionDetectionAgent.py` - Detect performance regressions
- `CoverageAnalysisAgent.py` - Analyze test coverage
- `QualityGateAgent.py` - Enforce quality gates
- `EvaluationReportingAgent.py` - Generate evaluation reports

**apps_exec/reasoning/:**
- `SourceIngestionAgent.py` - Ingest source materials
- `CapabilityExtractionAgent.py` - Extract capabilities
- `AudienceAnalysisAgent.py` - Analyze target audience
- `ContentSynthesisAgent.py` - Synthesize content
- `BriefAssemblyAgent.py` - Assemble executive briefs
- `EvidenceValidationAgent.py` - Validate evidence
- `StyleComplianceAgent.py` - Check style compliance

**apps_research/reasoning/:**
- `SourceDiscoveryAgent.py` - Discover sources
- `ContentHarvestingAgent.py` - Harvest content
- `CredibilityAssessmentAgent.py` - Assess credibility
- `InsightExtractionAgent.py` - Extract insights
- `KnowledgeSynthesisAgent.py` - Synthesize knowledge
- `CitationManagementAgent.py` - Manage citations
- `ResearchReportingAgent.py` - Generate reports

**apps_rfp/reasoning/:**
- `RequirementAnalysisAgent.py` - Analyze requirements
- `ComplianceMappingAgent.py` - Map compliance needs
- `CapabilityAlignmentAgent.py` - Align capabilities
- `ProposalArchitectureAgent.py` - Architect proposals
- `ResponseDraftingAgent.py` - Draft responses
- `DifferentiationHighlightingAgent.py` - Highlight differentiation
- `SubmissionValidationAgent.py` - Validate submissions

---

## Phase 4: ADG Integration & Spine Wiring

### 4.1 Spine Adapter Enhancement
**Pattern:** Each app has spine/spine_adapter.py but minimal wiring

**Enhancement:**
- Full ADG client integration
- Lifecycle trace emission at adapter boundaries
- Circuit breaker pattern for resilience
- Routing tier integration

### 4.2 ADG Edge Coverage Target
**Goal:** 31/31 P0-P4 dimensions at 100% for each app

**Implementation Strategy:**
- Batch wiring via script (similar to P0-P4 hardening)
- Self-bootstrap in agent_spec_config.py
- Visitor updates in static_scanner.py for app-specific patterns

---

## Phase 5: End-to-End Integration Testing

### 5.1 Integration Test Structure
```
tests/integration/apps_eval/
  test_eval_end_to_end.py
  test_eval_spine_integration.py
  test_eval_adg_integration.py
  
tests/integration/apps_exec/
  test_exec_end_to_end.py
  test_exec_spine_integration.py
  test_exec_adg_integration.py
  
[similar for apps_research, apps_rfp]
```

### 5.2 Test Coverage Requirements
- Config loading and validation
- Engine initialization and execution
- Service orchestration
- Agent reasoning chains
- Spine adapter routing
- ADG trace emission
- Error handling and recovery

---

## Phase 6: Validation Gates

### 6.1 Per-App Validation Checklist
- [ ] All config files have lifecycle trace integration
- [ ] All engines import and use agent_spec_config
- [ ] All services emit traces at boundaries
- [ ] All agents validate capabilities before execution
- [ ] Spine adapter routes correctly to agentic_core
- [ ] ADG shows 31/31 dimensions for app modules
- [ ] Integration tests pass
- [ ] No import errors or circular dependencies

### 6.2 Cross-App Validation
- [ ] Consistent patterns across all apps_*
- [ ] Shared utils properly factored to apps_shared
- [ ] No code duplication between apps
- [ ] Enforcement patterns consistent

---

## Execution Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 1 day | Hardened configs with full trace integration |
| Phase 2 | 2 days | services/ layer for all 4 apps |
| Phase 3 | 2 days | Agent ecosystem expansion |
| Phase 4 | 1 day | ADG integration and spine wiring |
| Phase 5 | 1 day | End-to-end integration tests |
| Phase 6 | 1 day | Validation gates and documentation |
| **Total** | **8 days** | Full rigor parity with apps_lic/apps_rg |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scope creep | Strict pattern adherence to apps_lic/apps_rg |
| ADG contamination | Denominator lock gate before/after each phase |
| Test instability | Incremental ADG regeneration, full test per phase |
| Import cycles | Layer boundary enforcement (L0-L6 gravity rules) |

---

## Success Criteria

1. **Structural Depth:** All apps have services/, reasoning/ agents, enforcement/ (where applicable)
2. **Trace Coverage:** 31/31 P0-P4 dimensions at 100% per ADG
3. **Integration:** All end-to-end tests pass
4. **Quality:** No new ADG violations introduced
5. **Documentation:** Updated specs and contracts per app

---

## Plan Metadata

- **Created:** 2026-03-29
- **Author:** Cascade
- **Target Path:** docs/reports/plans/apps-tier-hardening-alignment-plan-7d9a8c.md
- **Status:** Ready for execution
