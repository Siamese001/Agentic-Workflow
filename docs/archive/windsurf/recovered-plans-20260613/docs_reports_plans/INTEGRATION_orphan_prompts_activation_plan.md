# INTEGRATION: Orphan Prompts Activation Plan

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

**Issue**: 11 orphan prompts in `data/prompt_governance` with zero usage in agentic_core or apps_* folders.

**Mission**: Integrate all orphan prompts into the active agentic model to eliminate waste and unlock capabilities.

**Impact**:
- Activate 11 high-quality prompts currently sitting unused
- Enhance agentic capabilities with executive, outreach, and resume domain expertise
- Eliminate architectural waste

---

## 1. Orphan Prompt Inventory

### 1.1 Executive Domain Prompts (3 files)

| File | Purpose | Current Status | Integration Target |
|------|---------|----------------|-------------------|
| `k11_shadow_audit.yaml` | Shadow audit for executive decisions | ORPHANED | `apps_lic/engines/` |
| `k12_strategy_roadmap.yaml` | 30-60- execution planning | ORPHANED | `apps_lic/engines/` |
| `k13_interviewer_sim.yaml` | Interviewer profiling & preparation | ORPHANED | `apps_lic/engines/` |

### 1.2 Outreach Domain Prompts (4 files)

| File | Purpose | Current Status | Integration Target |
|------|---------|----------------|-------------------|
| `k3_message_body_agent.yaml` | Message body generation | ORPHANED | `apps_lic/engines/` |
| `connection_request.md` | LinkedIn connection requests | ORPHANED | `apps_lic/engines/` |
| `cold_outreach_template.md` | Cold outreach templates | ORPHANED | `apps_lic/engines/` |
| `followup_template.md` | Follow-up message templates | ORPHANED | `apps_lic/engines/` |

### 1.3 Resume Domain Prompts (4 files)

| File | Purpose | Current Status | Integration Target |
|------|---------|----------------|-------------------|
| `k7_assembly_agent.yaml` | Resume assembly & optimization | ORPHANED | `apps_rg/engines/` |
| `skills_template.md` | Skills section templates | ORPHANED | `apps_rg/engines/` |
| `summary_template.md` | Executive summary templates | ORPHANED | `apps_rg/engines/` |
| `connection_request.md` | Networking connection requests | ORPHANED | `apps_rg/engines/` |

---

## 2. Integration Architecture

### 2.1 Prompt Loading Infrastructure

**Create**: `agentic_core/prompt_governance/prompt_loader.py`

```python
class PromptLoader:
    """Centralized prompt loading and caching system."""

    def __init__(self):
        self._prompt_cache: dict[str, dict] = {}
        self._prompt_dir = Path("data/prompt_governance")

    def load_prompt(self, domain: str, name: str) -> dict:
        """Load and cache prompt by domain and name."""
        cache_key = f"{domain}:{name}"
        if cache_key not in self._prompt_cache:
            prompt_file = self._prompt_dir / domain / f"{name}.yaml"
            with open(prompt_file) as f:
                self._prompt_cache[cache_key] = yaml.safe_load(f)
        return self._prompt_cache[cache_key]

    def get_template(self, domain: str, name: str, **kwargs) -> str:
        """Get formatted prompt template with variables."""
        prompt_data = self.load_prompt(domain, name)
        template = prompt_data["template"]
        constraints = "\n".join(prompt_data.get("constraints", []))

        return template.format(
            constraints=constraints,
            **kwargs
        )
```

### 2.2 Domain-Specific Integration

#### Executive Domain Integration (apps_lic)

**Target Engine**: `ExecutiveStrategyAgent.py`

```python
class ExecutiveStrategyAgent(SovereignBaseAgent):
    """Executive strategy and planning capabilities."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.prompt_loader = PromptLoader()

    def generate_strategy_roadmap(self, audit_data: dict) -> str:
        """Generate 30-60- strategy roadmap."""
        return self.prompt_loader.get_template(
            domain="executive",
            name="k12_strategy_roadmap",
            **audit_data
        )

    def conduct_shadow_audit(self, organization_data: dict) -> str:
        """Conduct executive shadow audit."""
        return self.prompt_loader.get_template(
            domain="executive",
            name="k11_shadow_audit",
            **organization_data
        )

    def profile_interviewer(self, interviewer_data: dict) -> str:
        """Generate interviewer profiling and preparation guide."""
        return self.prompt_loader.get_template(
            domain="executive",
            name="k13_interviewer_sim",
            **interviewer_data
        )
```

#### Outreach Domain Integration (apps_lic)

**Target Engine**: `OutreachMessageAgent.py`

```python
class OutreachMessageAgent(SovereignBaseAgent):
    """Personalized outreach message generation."""

    def generate_connection_request(self, profile_data: dict) -> str:
        """Generate LinkedIn connection request."""
        template = self._load_markdown_template("outreach", "connection_request")
        return self._format_template(template, **profile_data)

    def generate_cold_outreach(self, prospect_data: dict) -> str:
        """Generate personalized cold outreach."""
        template = self._load_markdown_template("outreach", "cold_outreach_template")
        return self._format_template(template, **prospect_data)

    def generate_followup(self, context_data: dict) -> str:
        """Generate follow-up message."""
        template = self._load_markdown_template("outreach", "followup_template")
        return self._format_template(template, **context_data)

    def generate_message_body(self, message_data: dict) -> str:
        """Generate message body using K3 agent."""
        prompt_data = self.prompt_loader.load_prompt("outreach", "k3_message_body_agent")
        return self._format_template(prompt_data["template"], **message_data)
```

#### Resume Domain Integration (apps_rg)

**Target Engine**: `ResumeAssemblyAgent.py`

```python
class ResumeAssemblyAgent(RGAgentBase):
    """Resume assembly and optimization using domain prompts."""

    def assemble_resume(self, profile_data: dict) -> str:
        """Assemble complete resume using K7 agent."""
        prompt_data = self.prompt_loader.load_prompt("resume", "k7_assembly_agent")
        return self._format_template(prompt_data["template"], **profile_data)

    def generate_skills_section(self, skills_data: dict) -> str:
        """Generate skills section."""
        template = self._load_markdown_template("resume", "skills_template")
        return self._format_template(template, **skills_data)

    def generate_executive_summary(self, summary_data: dict) -> str:
        """Generate executive summary."""
        template = self._load_markdown_template("resume", "summary_template")
        return self._format_template(template, **summary_data)

    def generate_networking_request(self, networking_data: dict) -> str:
        """Generate networking connection request."""
        template = self._load_markdown_template("resume", "connection_request")
        return self._format_template(template, **networking_data)
```

---

## 3. Implementation Plan

### Phase 1: Infrastructure Setup (Day 1-2)

1. **Create Prompt Loading System**
   ```bash
   # Create prompt loading infrastructure
   touch agentic_core/prompt_governance/prompt_loader.py
   touch agentic_core/prompt_governance/__init__.py
   ```

2. **Add Prompt Loader to Core**
   ```python
   # agentic_core/prompt_governance/__init__.py
   from .prompt_loader import PromptLoader

   __all__ = ["PromptLoader"]
   ```

3. **Update Base Agent Classes**
   ```python
   # Add prompt loading capability to base agents
   # Both SovereignBaseAgent and RGAgentBase
   ```

### Phase 2: Executive Domain Integration (Day 3-4)

1. **Create ExecutiveStrategyAgent**
   ```bash
   touch apps_lic/engines/ExecutiveStrategyAgent.py
   ```

2. **Implement Strategy Methods**
   - `generate_strategy_roadmap()`
   - `conduct_shadow_audit()`
   - `profile_interviewer()`

3. **Add to LIC Agent Registry**
   ```python
   # Register new executive capabilities
   ```

### Phase 3: Outreach Domain Integration (Day 5-6)

1. **Create OutreachMessageAgent**
   ```bash
   touch apps_lic/engines/OutreachMessageAgent.py
   ```

2. **Implement Outreach Methods**
   - `generate_connection_request()`
   - `generate_cold_outreach()`
   - `generate_followup()`
   - `generate_message_body()`

3. **Integrate with Existing Outreach Flow**
   ```python
   # Connect to existing outreach infrastructure
   ```

### Phase 4: Resume Domain Integration (Day 7-8)

1. **Create ResumeAssemblyAgent**
   ```bash
   touch apps_rg/engines/ResumeAssemblyAgent.py
   ```

2. **Implement Resume Methods**
   - `assemble_resume()`
   - `generate_skills_section()`
   - `generate_executive_summary()`
   - `generate_networking_request()`

3. **Integrate with RG Pipeline**
   ```python
   # Connect to existing resume generation flow
   ```

### Phase 5: Testing & Validation (Day 9-10)

1. **Unit Tests**
   ```python
   # Test each new agent method
   # Verify prompt loading works correctly
   # Validate template formatting
   ```

2. **Integration Tests**
   ```python
   # Test full pipeline integration
   # Verify end-to-end functionality
   ```

3. **Performance Tests**
   ```python
   # Ensure prompt loading is efficient
   # Verify caching works properly
   ```

---

## 4. Integration Benefits

### 4.1 Capability Enhancement

**Executive Domain**:
- Strategic planning capabilities
- Interview preparation tools
- Shadow audit functionality

**Outreach Domain**:
- Personalized message generation
- LinkedIn optimization
- Follow-up automation

**Resume Domain**:
- Professional resume assembly
- Skills section optimization
- Executive summary generation

### 4.2 Architectural Benefits

- **Zero Orphan Prompts**: All 11 prompts activated
- **Centralized Management**: Single prompt loading system
- **Domain Organization**: Clear domain-based structure
- **Reusable Infrastructure**: Prompt loader usable across all apps

---

## 5. Success Metrics

### 5.1 Integration Metrics

- ✅ **11/11 prompts integrated** (100% activation)
- ✅ **3 new agents created** (ExecutiveStrategy, OutreachMessage, ResumeAssembly)
- ✅ **12 new methods implemented** (4 per domain)
- ✅ **Zero orphan files remaining**

### 5.2 Quality Metrics

- ✅ **All tests passing** (unit + integration)
- ✅ **Performance benchmarks met** (<100ms prompt load)
- ✅ **Template formatting verified** (no rendering errors)
- ✅ **Domain expertise validated** (subject matter expert review)

---

## 6. Risk Mitigation

### 6.1 Technical Risks

**Risk**: Prompt loading performance issues
**Mitigation**: Implement caching and lazy loading

**Risk**: Template formatting errors
**Mitigation**: Comprehensive template validation

**Risk**: Integration conflicts with existing code
**Mitigation**: Backward compatibility and gradual rollout

### 6.2 Operational Risks

**Risk**: Agent capability overlap
**Mitigation**: Clear domain boundaries and responsibility mapping

**Risk**: Increased complexity
**Mitigation**: Comprehensive documentation and training

---

## 7. Implementation Timeline

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Infrastructure |  | Prompt loading system |
| Phase 2: Executive Integration |  | ExecutiveStrategyAgent |
| Phase 3: Outreach Integration |  | OutreachMessageAgent |
| Phase 4: Resume Integration |  | ResumeAssemblyAgent |
| Phase 5: Testing & Validation |  | Complete test suite |
| **TOTAL** | **** | **Full integration** |

---

## 8. Conclusion

**This integration plan will activate all 11 orphan prompts, adding significant capabilities to the agentic system while eliminating architectural waste.**

The phased approach ensures safe, systematic integration with minimal risk and maximum impact.

---

**Status**: ✅ **PLAN READY** - Awaiting implementation approval
**Date**: 2026-02-15
**Priority**: HIGH - Eliminates waste and unlocks significant capabilities

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

