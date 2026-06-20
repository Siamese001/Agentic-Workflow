======================================================================================================================================================================
                                          L5 SAFETY ENFORCEMENT PLANE — CROSS-CUTTING GOVERNANCE & STRUCTURAL INTEGRITY
======================================================================================================================================================================

L5 is a **horizontal enforcement plane** consulted by all layers (L0, L1, L2, L3, L6) at both compile-time and runtime.
It provides four foundational services:

1. **Classification Kernel** — File type taxonomy and AST-based detection
2. **Structure Blueprint** — Path validation, territory enforcement, test placement
3. **Agent Execution Profile Registry** — Compile-time frozen agent metadata
4. **Sovereign LLM Gateway** — Sole LLM egress seam with provider abstraction

======================================================================================================================================================================
  1. CLASSIFICATION KERNEL [agentic_core/L5_safety/core_kernel/classification_kernel.py]
======================================================================================================================================================================

**Purpose**: Zero-dependency SSOT for file type classification across all layers

**FileType Taxonomy** (20 canonical types):
- AGENT, ORCHESTRATOR, ENGINE, MIXIN, PROTOCOL, STRATEGY
- TOOL, VALIDATOR, CONFIG, CONFIG_WITH_LOGIC
- HEALER, DETECTOR, ANALYZER, ROUTER, GATEWAY
- UTIL, TEST, SCRIPT, UNKNOWN, SHIM

**Core API**:
```python
classify_file_standalone(path: str) -> FileType
is_agent_file(path: str) -> bool
is_agent_or_orchestrator(path: str) -> bool
clear_classification_cache() -> None
classification_cache_info() -> CacheInfo
classification_cache_context() -> ContextManager
```

**Classification Algorithm**:
- AST-based detection with 19-priority queue (first match wins)
- Priority order:
  1. Shim detection (imports only, `__all__`, docstring)
  2. Agent detection (`BaseAgent` inheritance, `@agent` decorator)
  3. Orchestrator detection (`BaseOrchestrator` inheritance)
  4. Engine detection (`Engine` suffix, orchestration methods)
  5. Mixin detection (`Mixin` suffix, abstract methods)
  6. Protocol detection (`Protocol` inheritance, `@runtime_checkable`)
  7. Strategy detection (`Strategy` suffix, policy methods)
  8. Tool detection (`@tool` decorator, `ToolResult` return)
  9. Validator detection (`Validator` suffix, `validate()` method)
  10. Healer detection (`Healer` suffix, `heal()` method)
  11. Detector detection (`Detector` suffix, `detect()` method)
  12. Analyzer detection (`Analyzer` suffix, `analyze()` method)
  13. Router detection (`Router` suffix, `route()` method)
  14. Gateway detection (`Gateway` suffix, singleton pattern)
  15. Config detection (`.py` in `config/`, dataclass/Pydantic)
  16. Config-with-logic detection (config + executable methods)
  17. Test detection (`test_*.py`, `*_test.py`)
  18. Script detection (executable, `if __name__ == "__main__"`)
  19. Util detection (fallback for `.py` files)

**Performance Optimization**:
- LRU cache: `@lru_cache(maxsize=1024)` on `_classify_impl()`
- Cache hit rate: ~95% in typical batch scans
- Cache context manager for batch operations (clear on entry/exit)

**Error Hardening**:
- `SyntaxError` → logged with file path + line number, returns `UNKNOWN`
- `UnicodeDecodeError` → logged with encoding info, returns `UNKNOWN`
- `OSError` → logged with permission/path details, returns `UNKNOWN`
- Catch-all guard prevents batch crash on unexpected errors

**Dual-Tag Conflict Detection**:
- Scans for files matching multiple classification patterns
- Example: `config_engine.py` matches both CONFIG and ENGINE
- Emits warning, uses first-match priority to resolve

**CONFIG_WITH_LOGIC Detection**:
- Flags config files containing executable methods (not just data)
- Violation pattern: business logic in config files
- Used by governance scanners to enforce separation of concerns

**Consumers** (10+ files across layers):
- **L0**: Agent discovery, routing table construction
- **L1**: Prompt template classification
- **L2**: File validation before execution, healer registration
- **L3**: Orchestrator detection, workflow assembly
- **L6**: Audit log classification, telemetry categorization
- **Runtime**: Dynamic agent loading, hot-reload validation
- **Apps**: Domain-specific agent discovery (apps_lic, apps_rg)
- **Tests**: Test placement validation, MECE coverage checks

**CI Enforcement**:
- Workflow: `.github/workflows/ssot-kernel-guardrail.yml`
- Runs on: push, pull_request
- Checks:
  - 0 ERRORS required (no classification failures)
  - 0 dual-tag conflicts
  - 0 CONFIG_WITH_LOGIC violations
  - Contract tests pass (68 parametrized cases)
- Blocks merge on failure

**Phase History**:
- **Phase 1 (Consolidation)**: Refactored 10 files, removed 400+ lines of bespoke logic
- **Phase 2 (Architectural Hardening)**: Added LRU cache, contract tests, SSOT guardrail
- **Phase 2b (Bulletproof Hardening)**: Shadow liquidation (7 errors → 0), error hardening, cache context

**Metrics**:
- Agent count: 190 candidates, 190 verified, 0 invalid
- Guardrail: 0 ERRORS, 2601 files scanned
- Cache hit rate: 95%+
- Classification time: <1ms per file (cached), <10ms (uncached)

======================================================================================================================================================================
  2. STRUCTURE BLUEPRINT [agentic_core/L5_safety/config/structure_blueprint/]
======================================================================================================================================================================

**Purpose**: Sovereign territory enforcement, path validation, test placement SSOT

**Core Modules**:
- `ssot.py` — Layer roots, territory definitions, path allowlists
- `sovereign_kernel.py` — Immutable kernel components, modular extensions
- `path_validator.py` — Cross-domain deportation, depth enforcement
- `test_placement.py` — Canonical test location mapping

**Territory Definitions** (`ssot.py`):

```python
LAYER_ROOTS = {
    "L0": "agentic_core/L0_routing",
    "L1": "agentic_core/L1_cognitive",
    "L2": "agentic_core/L2_execution",
    "L3": "agentic_core/L3_orchestration",
    "L4": "agentic_core/L4_state",
    "L5": "agentic_core/L5_safety",
    "L6": "agentic_core/L6_observability"
}

ENFORCED_TERRITORIES = {
    "agentic_core/core": "Kernel-only (classification, determinism)",
    "agentic_core/agents": "Agent registry, base classes",
    "agentic_core/L2_execution/enforcement": "Gateway, UWG, boundaries"
}

CODE_TERRITORIES = [
    "agentic_core/",
    "apps_lic/",
    "apps_rg/",
    "apps_shared/",
    "system_learning/"
]

VOLATILE_TERRITORIES = [
    "artifacts/",
    "docs/reports/",
    "logs/",
    "temp/"
]
```

**Sovereign Kernel Components** (`sovereign_kernel.py`):

62 immutable components that form the system kernel:
- Classification kernel
- Determinism core (SemanticClock, ReplayGuard, DigestCalculator)
- Agent registry
- Sovereign LLM Gateway
- Universal Write Gateway
- Healing tier router
- Structure blueprint itself
- (Full list in file)

**Modular Extensions**:
- Removable without breaking kernel
- Examples: specific healers, detectors, analyzers
- Must not be imported by kernel components

**Path Validation** (`is_path_allowed()`):

Enforcement rules:
1. **Cross-domain deportation**: L2 cannot import from L3, L3 cannot import from L1
2. **Depth enforcement**: Max 4 levels deep within any layer
3. **L4 specialization approval**: L4 subdirectories require explicit allowlist entry
4. **Forbidden patterns**:
   - Duplicate prefixes (e.g., `agent_agent_*.py`)
   - Versioned files (e.g., `module_v2.py`)
   - Legacy markers (e.g., `*_old.py`, `*_backup.py`)
   - Stuttering suffixes (e.g., `validator_validator.py`)

**Test Placement SSOT** (`TEST_CANONICAL_LOCATION_MAP`):

```python
TEST_CANONICAL_LOCATION_MAP = {
    "agentic_core/L0_routing": "tests/routing/",
    "agentic_core/L1_cognitive": "tests/cognitive/",
    "agentic_core/L2_execution": "tests/execution/",
    "agentic_core/L3_orchestration": "tests/orchestration/",
    "agentic_core/L4_state": "tests/state/",
    "agentic_core/L5_safety": "tests/safety/",
    "agentic_core/L6_observability": "tests/observability/",
    "agentic_core/agents": "tests/agents/",
    "agentic_core/core": "tests/core/",
    "apps_lic": "tests/apps_lic/",
    "apps_rg": "tests/apps_rg/",
    "apps_shared": "tests/apps_shared/",
    "system_learning": "tests/system_learning/"
}
```

Function: `get_canonical_test_path(source_file: str) -> str`

**Root Protection**:

Static protected files:
- `.codex/rules`
- `pyproject.toml`
- `pytest.ini`
- `README.md`
- `.gitignore`

Dynamic protected files (generated at runtime):
- `agentic_core/core/classification_kernel.py`
- `agentic_core/L5_safety/config/structure_blueprint/ssot.py`
- `agentic_core/agents/agent_registry.py`

**PROJECT_ROOT_WHITELIST**:
- Allowed root-level files (non-code)
- Examples: `LICENSE`, `CHANGELOG.md`, `requirements.txt`

**Naming Discipline**:

```python
VALIDATED_FILE_EXTENSIONS = [
    ".py", ".md", ".json", ".yaml", ".yml", ".toml", ".txt"
]

NAMING_EXEMPT_FILES = [
    "__init__.py",
    "__main__.py",
    "conftest.py"
]

NAMING_EXEMPT_DIRS = [
    "__pycache__",
    ".git",
    ".pytest_cache",
    "node_modules"
]
```

**CI Verification**:
- Exact invocation: `python -m agentic_core.L5_safety.config.structure_blueprint._verify`
- Runs on: pre-commit, CI pipeline
- Checks:
  - All paths valid (no forbidden patterns)
  - No cross-domain imports
  - No depth violations
  - Test placement matches canonical map
  - Root files protected
- Blocks commit/merge on failure

======================================================================================================================================================================
  3. AGENT EXECUTION PROFILE REGISTRY [agentic_core/agents/agent_registry.py]
======================================================================================================================================================================

**Purpose**: Compile-time frozen SSOT for agent metadata, execution modes, model allowlists

**Data Structure**:

```python
@dataclass(frozen=True)
class AgentExecutionProfile:
    agent_id: str
    reasoning_intensity: ReasoningIntensity  # LOW | HIGH
    execution_mode: ExecutionMode            # DETERMINISTIC | LLM_API
    allowed_models: tuple[str, ...]          # Empty for DETERMINISTIC

AGENT_REGISTRY: dict[str, AgentExecutionProfile] = {
    "code_healer": AgentExecutionProfile(
        agent_id="code_healer",
        reasoning_intensity=ReasoningIntensity.HIGH,
        execution_mode=ExecutionMode.LLM_API,
        allowed_models=("gpt-4o", "claude-3.5-sonnet", "gemini-2.5-pro")
    ),
    "import_boundary_detector": AgentExecutionProfile(
        agent_id="import_boundary_detector",
        reasoning_intensity=ReasoningIntensity.LOW,
        execution_mode=ExecutionMode.DETERMINISTIC,
        allowed_models=()
    ),
    # ... 188 more agents
}
```

**Reasoning Intensity**:
- **LOW**: Simple rule-based logic, AST scanning, deterministic checks
- **HIGH**: Complex reasoning, multi-step analysis, requires LLM

**Execution Mode**:
- **DETERMINISTIC**: No LLM calls, pure AST/deterministic logic, `allowed_models=()`
- **LLM_API**: Requires SovereignLLMGateway, `allowed_models` must be non-empty tuple

**Enforcement Rules**:
1. Unregistered agent invocation → **HARD FAIL** (KeyError with available agents list)
2. DETERMINISTIC agents cannot call LLM Gateway
3. LLM_API agents must have non-empty `allowed_models`
4. Model substitution forbidden (must use models from allowlist)

**Registry Digest**:

```python
def registry_digest() -> str:
    """Generates deterministic hash for validation."""
    entries = []
    for agent_id in sorted(AGENT_REGISTRY.keys()):
        profile = AGENT_REGISTRY[agent_id]
        entry = f"{agent_id}:{profile.reasoning_intensity.value}:{profile.execution_mode.value}"
        entries.append(entry)
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()
```

**Consumers**:
- **L0 Routing**: Validates agent_id before routing
- **L2 Sovereign LLM Gateway**: Enforces execution_mode and allowed_models
- **L2.3 Healing Tier Router**: Checks TIERING_ALLOWLIST membership
- **Determinism.py**: Includes registry_digest() in P5/W6 digest
- **CI**: Validates registry integrity on build

**Registry Hash in Determinism Digest** (REQ-413):
- P5-DETERMINISM-DIGEST includes `registry_digest()`
- Ensures agent profiles are frozen at deployment
- Prevents runtime agent substitution attacks

**Agent Count**: 190 total
- 142 LLM_API agents
- 48 DETERMINISTIC agents

======================================================================================================================================================================
  4. SOVEREIGN LLM GATEWAY [agentic_core/L2_execution/enforcement/SovereignLLMGateway.py]
======================================================================================================================================================================

**Purpose**: Sole LLM egress seam with provider abstraction, injection detection, audit logging

**Singleton Pattern**:

```python
class SovereignLLMGateway:
    _instance: Optional["SovereignLLMGateway"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

Single gateway for entire system — prevents provider proliferation

**Provider Support**:
- **OpenAI**: GPT-4, GPT-4o, o1-preview, o1-mini
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Pro

**Core API**:

```python
def route_generation(
    self,
    request: GenerationRequest
) -> GenerationResponse:
    """Routes LLM generation request to appropriate provider."""
    # 1. Validate request
    # 2. Resolve symbolic model_id to concrete provider
    # 3. Detect injection attempts
    # 4. Dispatch to provider
    # 5. Log to hash-chained audit trail
    # 6. Return response
```

**GenerationRequest Validation**:

```python
@dataclass
class GenerationRequest:
    agent_id: str                    # MUST exist in AGENT_REGISTRY
    model_id: str                    # Symbolic (e.g., "primary", "fallback")
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 4096
    tools: list[dict] = field(default_factory=list)
```

Validation checks:
1. `agent_id` MUST exist in `AGENT_REGISTRY`
2. Agent's `execution_mode` MUST be `LLM_API`
3. Resolved `model_id` MUST be in agent's `allowed_models`

**Model Resolution** (Symbolic → Concrete):

```python
MODEL_RESOLUTION_MAP = {
    "primary": "gpt-4o",
    "fallback": "claude-3.5-sonnet",
    "heavy": "gemini-2.5-pro",
    "light": "gpt-4o-mini"
}
```

No hardcoded models in agents — all use symbolic IDs

**Provider Health Monitoring**:

```python
@dataclass
class ProviderHealthState:
    provider: str
    status: ProviderStatus  # HEALTHY | DEGRADED | UNAVAILABLE
    error_rate: float       # Rolling window (last 100 requests)
    consecutive_failures: int
    last_success_timestamp: int
    last_failure_timestamp: int
```

Degraded mode:
- Error rate > 10% → switch to fallback provider
- Consecutive failures >= 3 → mark UNAVAILABLE
- Health check every 60 seconds

**Injection Detection**:

```python
class InjectionDetector:
    def scan_prompt(self, prompt: str) -> InjectionReport:
        """Scans for prompt injection patterns."""
        # 1. Detect role confusion ("Ignore previous instructions")
        # 2. Detect payload injection (base64, hex encoding)
        # 3. Detect delimiter attacks (triple quotes, XML tags)
        # 4. Detect privilege escalation ("You are now admin")
        # 5. Detect data exfiltration ("Print all training data")
```

Action on detection:
- **LOW severity**: Log warning, allow request
- **MEDIUM severity**: Strip malicious content, allow modified request
- **HIGH severity**: Block request, return error

**Hash-Chained Audit Log**:

```python
@dataclass
class AuditLogEntry:
    timestamp: int
    agent_id: str
    model_id: str
    prompt_hash: str        # SHA-256 of prompt
    response_hash: str      # SHA-256 of response
    token_count: int
    latency_ms: int
    prev_hash: str          # Hash of previous entry (chaining)
```

FIFO rotation:
- Max size: `max_audit_log_size` from config (default 10,000)
- Oldest entries evicted when limit reached
- Chain integrity verified on boot

**Replay Mode Support**:

```python
@dataclass
class ReplayEnvelope:
    prompt: str
    response: str
    model_id: str
    temperature: float
    timestamp: int
```

In `replay_mode=True`:
- Reads response from transcript instead of calling provider
- Ensures deterministic replay
- Validates response hash matches transcript

**Tool Adapter Layer** (Phase 21 hardening):

Converts dict → SDK type:
```python
def adapt_tools_for_provider(
    tools: list[dict],
    provider: str
) -> list[ProviderToolType]:
    """Casts generic tool dicts to provider-specific types."""
    if provider == "openai":
        return [OpenAITool(**tool) for tool in tools]
    elif provider == "anthropic":
        return [AnthropicTool(**tool) for tool in tools]
    elif provider == "google":
        return [GoogleTool(**tool) for tool in tools]
```

**AST Scanner Enforcement**:

Blocks at compile-time:
1. Direct provider SDK imports (e.g., `import openai`)
2. Model literals in code (e.g., `model="gpt-4"`)
3. Embedding instantiation outside factory
4. Direct API key usage (must use config)

**Fail-Closed Kill-Switch**:
- Provider substitution forbidden
- Unregistered agents rejected
- Invalid model_id → HARD FAIL
- No fallback to default model

**CI Enforcement**:
- AST scanner runs on every commit
- Zero CRITICAL violations required
- Blocks merge on:
  - Direct SDK imports
  - Model literals
  - Hardcoded API keys
  - Unregistered agent calls

======================================================================================================================================================================
  L5 INTERACTION MATRIX — WHO CALLS WHAT, WHEN
======================================================================================================================================================================

| L5 Component                  | Called By                          | When                                      | Purpose                                    |
|-------------------------------|------------------------------------|--------------------------------------------|---------------------------------------------|
| Classification Kernel         | L0, L1, L2, L3, L6, Apps, Tests    | Agent discovery, file validation, audit    | Determine file type via AST                |
| Structure Blueprint           | CI, L2 (runtime), Tests            | Build-time, path validation, test placement| Enforce territory boundaries               |
| Agent Registry                | L0, L2 Gateway, L2.3 Tier Router   | Routing, profile lookup, allowlist check   | Validate agent metadata                    |
| Sovereign LLM Gateway         | L2 Execution (agents)              | When agent needs LLM call                  | Abstract provider, detect injection, audit |

======================================================================================================================================================================
  L5 ENFORCEMENT TIMELINE
======================================================================================================================================================================

**Compile-Time** (CI Pipeline):
1. Structure Blueprint verifies path validity, test placement
2. AST Scanner blocks direct SDK imports, model literals
3. Classification Kernel contract tests validate taxonomy
4. Agent Registry integrity check (no duplicates, valid profiles)

**Boot-Time** (Application Startup):
1. Agent Registry frozen (immutable after import)
2. Classification Kernel cache initialized
3. Sovereign LLM Gateway singleton created
4. Audit log chain integrity verified

**Runtime** (Request Processing):
1. L0 consults Agent Registry for routing
2. L2 consults Classification Kernel for file validation
3. L2 agents call Sovereign LLM Gateway for LLM requests
4. L2.3 consults Agent Registry for tier allowlist
5. L6 consults Classification Kernel for audit categorization

======================================================================================================================================================================
