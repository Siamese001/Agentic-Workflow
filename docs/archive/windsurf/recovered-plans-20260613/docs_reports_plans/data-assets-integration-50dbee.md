# Data Assets Integration Plan

This plan identifies gaps in data asset utilization across agentic_core and apps_* directories and provides a comprehensive remediation strategy for leveraging the rich content in the data folder.

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Current State Analysis

### ✅ **Already Integrated**
- **Prompt Templates**: `data/prompts/`, `data/prompt_libraries/`, `data/prompt_governance/` - Integrated via PromptLibraryLoader
- **Basic Prompt Governance**: Access control, approval workflows - Partially integrated
- **Agent Discovery**: `data/processed/agent_discovery_full.json` - Used for agent registry

### ❌ **Critical Gaps Identified**

#### **1. Golden Datasets (UNUSED)**
- `data/golden/lic_resume_quality_500.jsonl` - 500 expert-labeled resumes with quality scores
- `data/golden/prompt_injection_attacks_200.jsonl` - 200 prompt injection attack patterns
- `data/golden/tool_use_ground_truth_1000.jsonl` - 1000 tool usage scenarios for training

#### **2. SDK/MCP Infrastructure (UNDERUTILIZED)**
- `data/sdks_mcps/client_wrappers/` - Production-ready OpenAI, Anthropic, Vertex clients
- `data/sdks_mcps/mcp_catalog/` - Model Context Protocol specifications
- `data/sdks_mcps/reference_clients/` - Minimal integration examples

#### **3. Reference Playbooks (UNUSED)**
- `data/external/reference_playbooks/prompt_schema.json` - JSON schema for prompt validation
- `data/external/reference_playbooks/` - Access control, compliance, governance patterns

#### **4. Evaluation Framework (PARTIALLY USED)**
- `data/prompt_governance/evaluations/` - Evaluation sets, regression tests, rubrics
- `data/prompt_governance/registry/` - Prompt manifest, version maps, rollback policies

#### **5. Processed Data (UNDERUTILIZED)**
- `data/processed/semantic_cache/` - Curated chunks for semantic search
- `data/freeze_reports/` - Baseline integrity reports
- `data/output/` - Audit results and outputs

## Remediation Plan

### **Phase 1: Golden Dataset Integration (HIGH PRIORITY)**

#### 1.1 Resume Quality Training Data
- **Target**: `apps_rg` engines and validators
- **Implementation**: Create `ResumeQualityTrainer` using `lic_resume_quality_500.jsonl`
- **Benefits**: Improve resume generation quality, enable quality scoring
- **Files to Create**:
  - `apps_rg/reasoning/ResumeQualityTrainer.py`
  - `apps_rg/validators/ResumeQualityValidator.py`

#### 1.2 Security Training Data
- **Target**: `agentic_core/prompt_governance/security/`
- **Implementation**: Enhance injection detection with `prompt_injection_attacks_200.jsonl`
- **Benefits**: Strengthen prompt injection detection and prevention
- **Files to Enhance**:
  - `agentic_core/prompt_governance/security/injection_detector.py`

#### 1.3 Tool Usage Training
- **Target**: All agent tool calling infrastructure
- **Implementation**: Create `ToolUsageTrainer` using `tool_use_ground_truth_1000.jsonl`
- **Benefits**: Improve tool selection and parameter accuracy
- **Files to Create**:
  - `apps_shared/training/ToolUsageTrainer.py`

### **Phase 2: SDK/MCP Integration (HIGH PRIORITY)**

#### 2.1 Replace Runtime Imports
- **Target**: Replace `runtime.shared.multi_provider_clients` imports
- **Implementation**: Use production clients from `data/sdks_mcps/client_wrappers/`
- **Benefits**: Production-ready, validated, feature-complete clients
- **Files to Update**:
  - `apps_rg/tools/ResumeGenerator.py`
  - `apps_lic/reasoning/*.py`
  - All agent files using Provider/Client imports

#### 2.2 MCP Protocol Integration
- **Target**: Standardize Model Context Protocol usage
- **Implementation**: Use MCP specs from `data/sdks_mcps/mcp_catalog/`
- **Benefits**: Protocol consistency, version management
- **Files to Create**:
  - `apps_shared/protocols/MCPManager.py`

### **Phase 3: Reference Playbooks Integration (MEDIUM PRIORITY)**

#### 3.1 Schema Validation
- **Target**: Prompt template validation
- **Implementation**: Use `prompt_schema.json` for template validation
- **Benefits**: Ensure prompt quality and consistency
- **Files to Enhance**:
  - `apps_shared/utils/prompt_library_loader.py`

#### 3.2 Governance Patterns
- **Target**: Access control and compliance
- **Implementation**: Implement patterns from reference playbooks
- **Benefits**: Standardized governance across all agents
- **Files to Create**:
  - `agentic_core/governance/AccessControlManager.py`

### **Phase 4: Evaluation Framework Integration (MEDIUM PRIORITY)**

#### 4.1 Automated Testing
- **Target**: Prompt quality and regression testing
- **Implementation**: Use evaluation sets for automated testing
- **Benefits**: Continuous quality monitoring
- **Files to Create**:
  - `tests/integration/prompt_evaluation/`
  - `apps_shared/evaluation/PromptEvaluator.py`

#### 4.2 Version Management
- **Target**: Prompt versioning and rollback
- **Implementation**: Use registry for prompt lifecycle management
- **Benefits**: Safe prompt updates and rollbacks
- **Files to Create**:
  - `apps_shared/versioning/PromptVersionManager.py`

### **Phase 5: Processed Data Integration (LOW PRIORITY)**

#### 5.1 Semantic Search
- **Target**: Improve prompt and template discovery
- **Implementation**: Use semantic cache for intelligent prompt matching
- **Benefits**: Better prompt recommendations and discovery
- **Files to Enhance**:
  - `apps_shared/utils/prompt_library_loader.py`

#### 5.2 Audit Integration
- **Target**: Continuous monitoring and reporting
- **Implementation**: Process audit outputs for quality metrics
- **Benefits**: Data-driven quality improvements
- **Files to Create**:
  - `apps_shared/monitoring/AuditProcessor.py`

## Implementation Priority

### **Immediate (Week 1)**
1. Replace runtime client imports with production SDK clients
2. Integrate golden datasets for training and validation
3. Enhance security with prompt injection patterns

### **Short-term (Week 2-3)**
1. Implement reference playbook patterns
2. Create evaluation framework integration
3. Add schema validation for prompts

### **Medium-term (Week 4-6)**
1. Integrate semantic search capabilities
2. Implement comprehensive audit processing
3. Create automated quality monitoring

## Success Metrics

- **100%** of golden datasets actively used in training/validation
- **100%** of agents using production SDK clients
- **90%** of reference playbook patterns implemented
- **Automated evaluation** of all prompts using evaluation sets
- **Semantic search** for prompt discovery with 95% accuracy

## Risk Mitigation

- **Backward Compatibility**: Maintain fallback mechanisms during SDK migration
- **Data Validation**: Validate all golden datasets before integration
- **Gradual Rollout**: Phase integration to minimize disruption
- **Testing**: Comprehensive test coverage for all new integrations

## Expected Outcomes

- **Improved Quality**: 40% improvement in resume generation quality
- **Enhanced Security**: 90% reduction in prompt injection vulnerabilities
- **Better Performance**: 30% improvement in tool usage accuracy
- **Standardization**: 100% protocol compliance across all agents
- **Monitoring**: Real-time quality metrics and alerting

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

