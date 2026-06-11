---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\wave_execution_checklist.md'
original_relative_path: 'wave_execution_checklist.md'
source_sha256: 473fcca7c44a3572fc0f6922af354c3fbc704d83b96e73b08c3eea6cbd0763a4
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Wave Execution Checklist
## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Success Criteria & Validation Gates

---

## Wave 1: Critical Dependencies (Days 1-3)

### Micro-Wave 1.1: Missing Core Modules
**Success Criteria:**
- [ ] `agentic_core.discovery` module created and functional
- [ ] All L0 enforcement `__init__.py` files have proper exports
- [ ] No circular import errors in L0-L2 chain
- [ ] Basic import test passes: `from agentic_core.L0_routing.enforcement import ExecutionGatewayError`

**Validation Commands:**
```bash
python -c "from agentic_core.discovery import AgentRegistry; print('✓ discovery module works')"
python -c "from agentic_core.L0_routing.enforcement import ExecutionGatewayError; print('✓ L0 enforcement imports work')"
```

**Exit Gate:** All critical dependencies resolved, basic imports working

---

### Micro-Wave 1.2: Import Path Validation
**Success Criteria:**
- [ ] Import path correction matrix completed
- [ ] All 205 reconstructed tests have valid import paths
- [ ] No "ModuleNotFoundError" in import validation
- [ ] Path mapping document created

**Validation Commands:**
```bash
python tools/validate_import_paths.py --all-reconstructed
python tools/check_import_matrix.py --coverage
```

**Exit Gate:** 95% of reconstructed tests have valid import paths

---

### Micro-Wave 1.3: Dependency Graph Analysis
**Success Criteria:**
- [ ] Comprehensive dependency graph built
- [ ] All missing dependencies identified and documented
- [ ] Priority resolution order established
- [ ] Dependency resolution workflow created

**Validation Commands:**
```bash
python tools/build_dependency_graph.py --output=deps.json
python tools/analyze_missing_deps.py --report
```

**Exit Gate:** Dependency analysis complete, resolution workflow ready

---

## Wave 2: L0 Routing Completion (Days 4-5)

### Micro-Wave 2.1: L0 Enforcement Fix
**Success Criteria:**
- [ ] All 75 L0 routing tests can import successfully
- [ ] L0 enforcement module exports enabled
- [ ] No import errors in L0 layer
- [ ] Basic pytest collection works for L0

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/L0_routing/ --collect-only -q
python tools/test_imports.py --layer=L0
```

**Exit Gate:** L0 layer 90% import success rate

---

### Micro-Wave 2.2: L0 Types & Config
**Success Criteria:**
- [ ] boundary_types and action_capability_config imports fixed
- [ ] All L0 types and config modules functional
- [ ] L0 layer completeness achieved
- [ ] Cross-module dependencies within L0 working

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/L0_routing/types/ --collect-only -q
python -m pytest tests/unit/agentic_core/L0_routing/config/ --collect-only -q
```

**Exit Gate:** L0 layer 90% functional success rate

---

## Wave 3: Tool Chain Optimization (Days 6-8)

### Micro-Wave 3.1: Automated Import Detection
**Success Criteria:**
- [ ] Missing dependency detector functional
- [ ] Import path validation tool working
- [ ] Batch import fixing script operational
- [ ] Tool effectiveness validated on sample

**Validation Commands:**
```bash
python tools/detect_missing_deps.py --sample=10
python tools/validate_import_paths.py --auto-fix
```

**Exit Gate:** Automated tools working with 95% accuracy

---

### Micro-Wave 3.2: Progressive Fixing Pipeline
**Success Criteria:**
- [ ] Progressive import fixing pipeline operational
- [ ] Test-after-each-fix validation working
- [ ] Rollback capability tested and functional
- [ ] Progress dashboard created

**Validation Commands:**
```bash
python tools/progressive_fix.py --test-mode
python tools/validate_pipeline.py --rollback-test
```

**Exit Gate:** Tool chain ready for scale deployment

---

## Wave 4: L2 Execution Layer (Days 9-11)

### Micro-Wave 4.1: L2 Core & Engines
**Success Criteria:**
- [ ] L2 execution core imports fixed (target: 40/52 files)
- [ ] Engine module dependencies resolved
- [ ] Tools and apps modules completed
- [ ] Basic L2 functionality validated

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/L2_execution/core/ --collect-only -q
python -m pytest tests/unit/agentic_core/L2_execution/engines/ --collect-only -q
```

**Exit Gate:** L2 core 80% import success rate

---

### Micro-Wave 4.2: L2 Reasoning & Enforcement
**Success Criteria:**
- [ ] Reasoning module import issues resolved
- [ ] PTC tool contracts and policy enforcer completed
- [ ] Agent registry dependencies fixed
- [ ] L2 enforcement chain validated

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/L2_execution/reasoning/ --collect-only -q
python -m pytest tests/unit/agentic_core/L2_execution/enforcement/ --collect-only -q
```

**Exit Gate:** L2 reasoning 80% import success rate

---

### Micro-Wave 4.3: L2 Integration Testing
**Success Criteria:**
- [ ] L2 integration tests created and passing
- [ ] Cross-module dependencies validated
- [ ] Execution pipeline end-to-end tested
- [ ] 85% L2 success rate achieved

**Validation Commands:**
```bash
python -m pytest tests/integration/L2_execution/ -v
python tools/measure_success_rate.py --layer=L2
```

**Exit Gate:** L2 layer 85% functional success rate

---

## Wave 5: L5 Safety Layer (Days 12-14)

### Micro-Wave 5.1: L5 Enforcement & Reasoning
**Success Criteria:**
- [ ] L5 enforcement module imports fixed (target: 100/198 files)
- [ ] Governance validator and enforcer completed
- [ ] Safety plane dependencies resolved
- [ ] Enforcement chain integrity validated

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/L5_safety/enforcement/ --collect-only -q
python -m pytest tests/unit/agentic_core/L5_safety/reasoning/ --collect-only -q
```

**Exit Gate:** L5 enforcement 75% import success rate

---

### Micro-Wave 5.2: L5 Config & Types
**Success Criteria:**
- [ ] L5 config and types modules completed
- [ ] Constitutional governance types fixed
- [ ] Structure blueprint dependencies resolved
- [ ] Configuration integrity validated

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/L5_safety/config/ --collect-only -q
python -m pytest tests/unit/agentic_core/L5_safety/types/ --collect-only -q
```

**Exit Gate:** L5 config 80% import success rate

---

### Micro-Wave 5.3: L5 Safety Validation
**Success Criteria:**
- [ ] L5 integration tests created and passing
- [ ] Governance enforcement pipeline validated
- [ ] Safety plane response mechanisms tested
- [ ] 80% L5 success rate achieved

**Validation Commands:**
```bash
python -m pytest tests/integration/L5_safety/ -v
python tools/measure_success_rate.py --layer=L5
```

**Exit Gate:** L5 layer 80% functional success rate

---

## Wave 6: Application Layer (Days 15-17)

### Micro-Wave 6.1: Apps Pipeline Completion
**Success Criteria:**
- [ ] apps_eval, apps_exec, apps_reconstruction fixed
- [ ] apps_rfp and apps_rg modules completed
- [ ] Application pipeline dependencies resolved
- [ ] Execution chains validated

**Validation Commands:**
```bash
python -m pytest tests/unit/apps_eval/ tests/unit/apps_exec/ --collect-only -q
python -m pytest tests/unit/apps_rfp/ tests/unit/apps_rg/ --collect-only -q
```

**Exit Gate:** Applications 70% import success rate

---

### Micro-Wave 6.2: Agent & Base Agent Fix
**Success Criteria:**
- [ ] Agent registry and base agent modules fixed
- [ ] agentic_core/agents reconstruction completed
- [ ] Agent initialization dependencies resolved
- [ ] Agent lifecycle management validated

**Validation Commands:**
```bash
python -m pytest tests/unit/agentic_core/agents/ --collect-only -q
python -m pytest tests/unit/agentic_core/base_agents/ --collect-only -q
```

**Exit Gate:** Agents 75% import success rate

---

## Success Metrics Dashboard

### Daily Tracking:
- **Files Processed**: Cumulative count of files handled
- **Import Success Rate**: Percentage of successful imports
- **Test Success Rate**: Percentage of tests passing
- **Blockers Resolved**: Count of critical issues fixed

### Wave Completion:
- **Target vs Actual**: Compare planned vs achieved success rates
- **Quality Gates**: All validation criteria met
- **Dependencies**: Required prerequisites completed
- **Risks**: Identified risks and mitigation status

### Phase Gates:
- **Phase 1**: All critical dependencies resolved, L0 90% functional
- **Phase 2**: Core layers 80%+ functional, integration validated
- **Phase 3**: Advanced components 70%+ functional
- **Phase 4**: Integration validated, quality assured

### Final Success Criteria:
- **Total Files**: 885/885 reconstructed (100%)
- **Functional Tests**: 750/885 passing (85%+)
- **Import Success**: 800/885 modules importable (90%+)
- **Integration Tests**: All critical paths validated

Each wave must meet its exit gate criteria before proceeding to the next wave.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

