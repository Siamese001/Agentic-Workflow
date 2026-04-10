# LIC vs RG Architecture Comparison & Alignment Plan

**Generated:** 2026-01-24
**Purpose:** Detailed comparison of `apps_lic` and `apps_rg` architectures with implementation plan to align RG with LIC patterns.

---

## Executive Summary

The **LIC (LinkedIn Canonical)** architecture represents a mature, hardened implementation with:
- 9 sequential HOPs (HOP1-HOP9) with a dedicated orchestrator
- Unified base class (`LICAgentBase`) with consistent mixin integration
- Immutable state management via `ImmutableStagingBuffer`
- Centralized tracing via `TraceRegistry`
- JSON-based configuration with Pydantic schemas (`AgentSpecs`)
- Reasoning toggles for CoT/ToT control

The **RG (Resume Generation)** architecture has:
- 2 HOPs currently implemented (HOP1, HOP2)
- Dual base classes (`BaseRGEngine` in two files)
- Direct context passing instead of immutable buffers
- Inline knowledge base (Python-based `FROZEN_SNAPSHOT`)
- Missing core infrastructure (ImmutableBuffer, TraceRegistry, ReasoningToggles)

---

## Detailed Architecture Comparison

### 1. Directory Structure

| Component | LIC (`apps_lic/`) | RG (`apps_rg/`) | Gap |
|-----------|-------------------|-----------------|-----|
| **engines/** | 60 agent files (flat) | 19 files + 6 subdirs | ✅ Similar |
| **shared/core/** | `agent_base.py`, `immutable_buffer.py`, `trace_registry.py`, `mixins.py` | Missing | ❌ Critical Gap |
| **shared/tools/** | 55 tool files | 3 tool files | ⚠️ Partial |
| **shared/reasoning/** | `toggles.py` | Missing | ❌ Gap |
| **domain/config/** | `loader.py`, `schemas.py`, `agent_specs.json` | `knowledge_base.py` only | ⚠️ Different approach |

### 2. Base Class Architecture

#### LIC Pattern (`apps_lic/shared/core/agent_base.py`)
```python
class LICAgentBase(MCPHardenedMixin, HealerMixin, ABC):
    def __init__(self, llm_client: Any | None = None) -> None:
        super().__init__()
        self.config: AgentSpecs = load_agent_specs()  # JSON-based
        self.toggles: ReasoningToggles = ReasoningToggles()
        self.llm = llm_client

    def run_phase(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        # Wraps _process with tracing and error handling
        ...

    @abstractmethod
    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        pass
```

#### RG Pattern (`apps_rg/engines/base/base_resume_engine.py`)
```python
class BaseRGEngine(MCPHardenedMixin, HealerMixin, ABC):
    def __init__(self, ctx: Any, node_id: Optional[str] = None) -> None:
        super().__init__()
        self.ctx = ctx  # Direct context passing
        self.config = get_node_config(node_id)  # Python-based

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        pass
```

**Key Differences:**
| Aspect | LIC | RG | Alignment Needed |
|--------|-----|-----|------------------|
| Execution method | `run_phase()` → `_process()` | `execute()` | Standardize to LIC pattern |
| State passing | `ImmutableStagingBuffer` | Direct `ctx` object | Add ImmutableBuffer |
| Tracing | `TraceRegistry` parameter | None | Add TraceRegistry |
| Config loading | JSON + Pydantic schemas | Python dict | Add JSON config layer |
| Reasoning toggles | `ReasoningToggles` class | None | Add toggles |
| Async | Sync `_process()` | Async `execute()` | Keep async, wrap properly |

### 3. HOP Architecture

#### LIC HOPs (9 total)
| HOP | Agent | Purpose |
|-----|-------|---------|
| HOP1 | `HOP1ProfileAnalysisAgent` | Profile analysis, archetype classification |
| HOP2 | `HOP2ResearchAgent` | K.3 retrieval planning, evidence artifacts |
| HOP3 | `HOP3SenderGroundingAgent` | Sender context grounding |
| HOP4 | `HOP4RoutingAgent` | Message routing decisions |
| HOP5 | `HOP5GenerationAgent` | Message generation |
| HOP6 | `HOP6ValidationAgent` | Content validation |
| HOP7 | `HOP7GateDecisionAgent` | Pass/fail gate decisions |
| HOP8 | `HOP8QAReportAgent` | QA reporting |
| HOP9 | `HOP9IntegrationAgent` | Final integration |

#### RG HOPs (2 implemented, needs expansion)
| HOP | Agent | Purpose | Status |
|-----|-------|---------|--------|
| HOP0 | (inline in orchestrator) | JD validation | ⚠️ Not extracted |
| HOP1 | `ClerkExtractionEngine` | Structural extraction | ✅ Exists |
| HOP2 | `EnrichmentEngine` | Logic enrichment | ✅ Exists |
| HOP3-6 | (missing) | Generation, validation, refinement | ❌ Need creation |

### 4. State Management

#### LIC: ImmutableStagingBuffer
```python
@dataclass
class ImmutableStagingBuffer(MCPHardenedMixin, HealerMixin):
    _buffer: dict[str, Any] = field(default_factory=dict)
    _locked_keys: set[str] = field(default_factory=set)

    def write_once(self, key: str, value: Any) -> None:
        if key in self._locked_keys:
            raise ValueError(f"Key '{key}' is immutable")
        self._buffer[key] = value
        self._locked_keys.add(key)

    def read(self, key: str) -> Any | None:
        return self._buffer.get(key)
```

#### RG: Direct Context
```python
# Current RG pattern - mutable context
self.ctx.master_resume = data
result = self.ctx.get_failed_results()
```

**Gap:** RG lacks immutability guarantees. State can be mutated anywhere.

### 5. Tracing & Observability

#### LIC: TraceRegistry
```python
@dataclass
class TraceRegistry(MCPHardenedMixin):
    persistence_path: Path = None
    _traces: list[dict[str, Any]] = field(default_factory=list)

    def add_trace(self, event_type: str, details: dict[str, Any]) -> None:
        entry = {"timestamp": datetime.utcnow().isoformat(), "type": event_type, "details": details}
        self._traces.append(entry)
        if self.persistence_path:
            self._append_to_disk(entry)
```

#### RG: Inline Logging
```python
# Current RG pattern - basic logging
Logger.info(f"[{self.name}] LLM call with {len(prompt)} chars")
self._mcp_audit("engine_init")
```

**Gap:** RG lacks structured tracing with persistence.

### 6. Configuration Management

#### LIC: JSON + Pydantic Schemas
```
apps_lic/domain/config/
├── agent_specs.json      # Raw configuration
├── schemas.py            # Pydantic models (AgentSpecs, ProfileAnalysisConfig, etc.)
├── loader.py             # load_agent_specs() with caching
└── prompts.json          # Prompt templates
```

#### RG: Python-based Knowledge Base
```
apps_rg/domain/
├── knowledge_base.py     # FROZEN_SNAPSHOT with inline Pydantic models
└── __init__.py
```

**Gap:** RG embeds config in Python code. LIC separates config (JSON) from schema (Python).

### 7. Orchestrator Pattern

#### LIC: HOPOrchestratorAgent
- Manages HOP1-HOP9 execution
- Handles retry loops (HOP5→HOP7 cycle)
- Uses `ImmutableStagingBuffer` for state
- Tracks global step limits
- Supports buffer forking for retries

#### RG: ResumeOrchestratorEngine
- Manages HOP0-HOP2 only
- Uses direct context passing
- Checkpoints via `HopCheckpoint` dataclass
- Missing retry loop logic

---

## Implementation Plan

### Phase 1: Core Infrastructure (Priority: Critical)

#### 1.1 Create `apps_rg/shared/core/` Directory
```
apps_rg/shared/core/
├── __init__.py
├── agent_base.py          # RGAgentBase (LIC-aligned)
├── immutable_buffer.py    # ImmutableStagingBuffer
├── trace_registry.py      # TraceRegistry
└── mixins.py              # Re-exports
```

#### 1.2 Implement ImmutableStagingBuffer
- Copy from LIC with RG-specific adaptations
- Add resume-specific keys validation
- Integrate with existing `BaseRGEngine`

#### 1.3 Implement TraceRegistry
- Copy from LIC
- Configure persistence path for RG logs
- Add resume-specific trace types

#### 1.4 Create RGAgentBase
```python
class RGAgentBase(MCPHardenedMixin, HealerMixin, ABC):
    def __init__(self, llm_client: Any | None = None) -> None:
        super().__init__()
        self.config: RGAgentSpecs = load_rg_specs()
        self.toggles: ReasoningToggles = ReasoningToggles()
        self.llm = llm_client

    def run_phase(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        # Wrap async _process with tracing
        ...

    @abstractmethod
    async def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        pass
```

### Phase 2: Configuration Layer (Priority: High)

#### 2.1 Create `apps_rg/domain/config/` Directory
```
apps_rg/domain/config/
├── __init__.py
├── agent_specs.json       # RG agent configurations
├── schemas.py             # RGAgentSpecs, HOP configs
├── loader.py              # load_rg_specs()
└── prompts.json           # Extracted from knowledge_base.py
```

#### 2.2 Extract Prompts to JSON
- Move `FROZEN_SNAPSHOT.prompts` to `prompts.json`
- Keep `knowledge_base.py` for K-node definitions only

#### 2.3 Create RG-Specific Schemas
```python
class RGAgentSpecs(BaseModel):
    clerk_extraction: ClerkConfig
    enrichment: EnrichmentConfig
    generation: GenerationConfig
    validation: ValidationConfig
    orchestrator: OrchestratorConfig
```

### Phase 3: Reasoning Toggles (Priority: Medium)

#### 3.1 Create `apps_rg/shared/reasoning/`
```
apps_rg/shared/reasoning/
├── __init__.py
└── toggles.py             # ReasoningToggles (copy from LIC)
```

### Phase 4: HOP Expansion (Priority: High)

#### 4.1 Refactor Existing HOPs
- `hop1_clerk_engine.py` → `HOP1ClerkAgent.py`
- `hop2_enrichment_engine.py` → `HOP2EnrichmentAgent.py`
- Update to use `RGAgentBase`, `ImmutableStagingBuffer`, `TraceRegistry`

#### 4.2 Create Missing HOPs
| HOP | Agent | Purpose |
|-----|-------|---------|
| HOP0 | `HOP0JDValidationAgent` | Extract from orchestrator |
| HOP3 | `HOP3GenerationAgent` | Resume section generation |
| HOP4 | `HOP4ValidationAgent` | Quality validation |
| HOP5 | `HOP5GateDecisionAgent` | Pass/fail decisions |
| HOP6 | `HOP6RefinementAgent` | Content refinement |
| HOP7 | `HOP7QAReportAgent` | Final QA report |

#### 4.3 Update Orchestrator
- Implement full HOP0-HOP7 flow
- Add retry loop logic (HOP3→HOP5 cycle)
- Use `ImmutableStagingBuffer` for state
- Implement buffer forking for retries

### Phase 5: Migration & Cleanup (Priority: Medium)

#### 5.1 Migrate Existing Engines
- Update all engines in `apps_rg/engines/` to use new base class
- Replace direct `ctx` usage with buffer reads/writes
- Add trace calls throughout

#### 5.2 Consolidate Base Classes
- Remove duplicate `base_resume_engine.py` and `base_resume_agent.py`
- Single source of truth: `apps_rg/shared/core/agent_base.py`

#### 5.3 Update Imports
- All engines import from `apps_rg.shared.core`
- Remove legacy import patterns

---

## File Mapping: LIC → RG

| LIC File | RG Equivalent | Action |
|----------|---------------|--------|
| `shared/core/agent_base.py` | `shared/core/agent_base.py` | **Create** |
| `shared/core/immutable_buffer.py` | `shared/core/immutable_buffer.py` | **Create** |
| `shared/core/trace_registry.py` | `shared/core/trace_registry.py` | **Create** |
| `shared/core/mixins.py` | `shared/core/mixins.py` | **Create** |
| `shared/reasoning/toggles.py` | `shared/reasoning/toggles.py` | **Create** |
| `domain/config/schemas.py` | `domain/config/schemas.py` | **Create** |
| `domain/config/loader.py` | `domain/config/loader.py` | **Create** |
| `domain/config/agent_specs.json` | `domain/config/agent_specs.json` | **Create** |
| `engines/HOPOrchestratorAgent.py` | `engines/RGOrchestratorAgent.py` | **Refactor** |
| `engines/HOP1ProfileAnalysisAgent.py` | `engines/HOP1ClerkAgent.py` | **Refactor** |
| `engines/HOP2ResearchAgent.py` | `engines/HOP2EnrichmentAgent.py` | **Refactor** |

---

## Estimated Effort

| Phase | Files | Effort |
|-------|-------|--------|
| Phase 1: Core Infrastructure | 5 new files | 4-6 hours |
| Phase 2: Configuration Layer | 4 new files | 3-4 hours |
| Phase 3: Reasoning Toggles | 2 new files | 1-2 hours |
| Phase 4: HOP Expansion | 7 new/refactored files | 6-8 hours |
| Phase 5: Migration & Cleanup | 20+ file updates | 4-6 hours |
| **Total** | ~40 files | **18-26 hours** |

---

## Success Criteria

1. ✅ All RG engines inherit from `RGAgentBase`
2. ✅ State passed via `ImmutableStagingBuffer` (no direct ctx mutation)
3. ✅ All operations traced via `TraceRegistry`
4. ✅ Configuration loaded from JSON via Pydantic schemas
5. ✅ Reasoning toggles control CoT/ToT behavior
6. ✅ Orchestrator manages HOP0-HOP7 with retry loops
7. ✅ All existing tests pass after migration
