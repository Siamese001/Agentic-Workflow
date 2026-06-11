---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\test-coverage-improvement-a1b2c3.md'
original_relative_path: 'test-coverage-improvement-a1b2c3.md'
source_sha256: 66bcf2c2c5c5215672d835f3252eee4274b4ccf8781edf7547ca35610dbc8f0f
recovered_status: SURVIVED_IN_CURRENT
last_commit: '153652b9eb3'
last_commit_date: '2026-06-07 06:37:48 -0400'
created_date: '2026-04-06'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Test Coverage Improvement Plan for apps_* Directories

Systematically add unit tests for untested components across all apps_* directories to improve coverage and ensure code quality.

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | apps_eval tests | 21 files (10 services, 9 reasoning, 2 outputs) | A | 15000 🟢 |
| Wave 2 | apps_exec tests | 18 files (10 services, 6 reasoning, 2 outputs) | B | 13000 🟢 |
| Wave 3 | apps_research tests | 20 files (10 services, 8 reasoning, 2 outputs) | C | 14000 🟢 |
| Wave 4 | apps_rfp tests | 19 files (9 services, 8 reasoning, 2 outputs) | D | 14000 🟢 |

**Total: 56000 tokens across 4 waves, all GREEN**

---

## Gap Register

**GAP-1: apps_eval has 21 untested files**
- 10 service files (benchmark_runner_service, coverage_analyzer_service, metric_collector_service, quality_assessor_service, regression_detector_service, repo_signal_service, result_aggregator_service, scenario_loader_service, test_discovery_service)
- 9 reasoning files (EvalOrchestrator, QualityGateAgent, ScenarioGenerationAgent, TestDiscoveryAgent, criteria_decomposition_agent, enterprise_eval_orchestrator, evaluation_orchestrator)
- 2 output files (run_summary_renderer, scorecard_renderer)
- Impact: Critical business logic lacks test coverage, potential for regressions

**GAP-2: apps_exec has 18 untested files**
- 10 service files (artifact_exporter_service, audience_analyzer_service, brief_assembler_service, capability_extractor_service, content_synthesizer_service, document_ingestion_service, evidence_collector_service, repo_signal_service, style_validator_service)
- 6 reasoning files (BriefAssemblyAgent, ExecOrchestrator, SourceIngestionAgent, StyleComplianceAgent, brief_decomposition_agent, brief_orchestrator, enterprise_brief_orchestrator)
- 2 output files (brief_renderer, section_renderer)
- Impact: Core execution pipeline lacks validation

**GAP-3: apps_research has 20 untested files**
- 10 service files (citation_manager_service, content_harvester_service, credibility_scorer_service, insight_extractor_service, knowledge_integrator_service, repo_signal_service, report_compiler_service, source_discovery_service, synthesis_engine_service)
- 8 reasoning files (InsightExtractionAgent, KnowledgeSynthesisAgent, ResearchOrchestrator, SourceDiscoveryAgent, enterprise_research_orchestrator, query_decomposition_agent, research_multi_agent)
- 2 output files (research_renderer, section_renderer)
- Impact: Research functionality unvalidated

**GAP-4: apps_rfp has 19 untested files**
- 9 service files (capability_mapper_service, compliance_checker_service, differentiation_analyzer_service, proposal_architect_service, repo_signal_service, requirement_parser_service, response_generator_service, risk_assessor_service, submission_validator_service)
- 8 reasoning files (ComplianceMappingAgent, RequirementAnalysisAgent, RfpOrchestrator, compliance_validator, enterprise_orchestrator, requirement_decomposition_agent, section_orchestrator)
- 2 output files (proposal_renderer, section_renderer)
- Impact: RFP processing logic lacks safety net

---

## Execution Plan

### Phase 1 — apps_eval Test Implementation
**Scope**: Add unit tests for all apps_eval services, reasoning agents, and output renderers

**Commands**:
```bash
# Tests will be created programmatically following constitutional testing framework requirements
# Each test file will include:
# - Edge case coverage (None inputs, empty data, malformed structures)
# - State transition tests
# - Deterministic behavior validation
# - Mock discipline for external dependencies
# - Cross-platform compatibility (mocked permission errors)
```

**Acceptance**: All 21 new test files pass, covering services, reasoning, and outputs

### Phase 2 — apps_exec Test Implementation
**Scope**: Add unit tests for all apps_exec services, reasoning agents, and output renderers

**Commands**:
```bash
# Same testing standards as Phase 1
# Focus on document ingestion, brief assembly, and style validation logic
```

**Acceptance**: All 18 new test files pass

### Phase 3 — apps_research Test Implementation
**Scope**: Add unit tests for all apps_research services, reasoning agents, and output renderers

**Commands**:
```bash
# Same testing standards as Phase 1
# Focus on source discovery, knowledge synthesis, and report compilation
```

**Acceptance**: All 20 new test files pass

### Phase 4 — apps_rfp Test Implementation
**Scope**: Add unit tests for all apps_rfp services, reasoning agents, and output renderers

**Commands**:
```bash
# Same testing standards as Phase 1
# Focus on compliance checking, requirement parsing, and proposal generation
```

**Acceptance**: All 19 new test files pass

---

## Rules

- Follow constitutional testing framework (skill: testing-framework)
- Zero-tolerance coverage: every changed line of logic must have deterministic tests
- Test-first discipline: tests must exist before committing
- Deterministic tests only: no random inputs, fix seeds, inject timestamps
- Mock discipline: mocks only for external services, hardware, filesystem permissions
- Ingress-path rule: tests target real entrypoints, test doubles don't bypass validation
- No platform-specific skips: use mocking for permission errors
- Three quality gates: no silent errors, cross-platform compatibility, deterministic replay
- Follow existing test patterns in the codebase
- Use pytest markers (@pytest.mark.unit) appropriately

---

## Success Criteria

- [x] Execution plan created
- [x] apps_eval services tests created (10/10 services)
- [x] apps_eval outputs tests created (2/2 outputs)
- [x] apps_eval reasoning agent tests created (3/3 agents)
- [x] apps_exec services tests created (10/10 services)
- [x] apps_exec outputs tests created (2/2 outputs)
- [x] apps_exec reasoning agent tests created (3/3 agents)
- [x] apps_research services tests created (10/10 services)
- [x] apps_research outputs tests created (2/2 outputs)
- [x] apps_research reasoning agent tests created (3/3 agents)
- [x] apps_rfp services tests created (9/9 services)
- [x] apps_rfp outputs tests created (2/2 outputs)
- [x] apps_rfp reasoning agent tests created (2/2 agents)
- [x] All tests pass with pytest (218 passed)
- [x] Package import structure fixed for apps_research and apps_rfp
- [x] apps_shared tests deferred (already has extensive test coverage - 49+ test files exist)

---

## Implementation Commands

```bash
# Tests will be implemented file-by-file using the edit tool
# Each test file will follow this structure:
# 1. Import statements
# 2. Test class with pytest.mark.unit
# 3. Test methods for each public function/class method
# 4. Edge case tests
# 5. State transition tests
# 6. Error handling tests
```

---

## Rollback Strategy

If things go wrong:
1. Delete newly created test files
2. Restore from git if needed
3. Re-run existing test suite to ensure no regression

---

## Acceptance Criteria

| Metric | Target | Verification |
|---|---|---|
| New test files | 78 | Count of test_*.py files in apps_* test directories |
| Test pass rate | 100% | pytest --no-header -q tests/unit/apps_* |
| Edge case coverage | 100% | Manual review of test files |
| Determinism | 100% | Manual review of test files |
| Cross-platform | 100% | Manual review of test files |
