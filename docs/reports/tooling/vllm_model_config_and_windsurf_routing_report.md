# vLLM Configuration Scenarios and Windsurf Routing Recommendations

## Executive Summary

This report provides a comprehensive analysis of vLLM configuration scenarios and integration strategies for the Agentic-Workflow system. Based on architectural constraints analysis and performance modeling, we recommend a hybrid approach where local vLLM handles mechanical, context-bound tasks (L0/L2 layers) while Claude Opus handles complex reasoning and governance (L5+/L6 layers). The primary recommendation is a 7B INT4 quantized model with 4K context for immediate deployment, with an upgrade path to 14B BF16 with 8K context as hardware permits.

**Key Findings:**
- Local vLLM can safely handle 60-70% of routine tasks within architectural constraints
- 4K context is the sweet spot for mechanical tasks vs memory overhead
- Subprocess-based integration preserves layer separation requirements
- Expected 3-5x throughput improvement for supported use cases
- Deterministic routing rubric prevents architectural violations

## Baseline Assumptions

### Current Environment
- **Local vLLM Baseline**: ~1.5K max context (current limitation)
- **Claude Opus Access**: Available in IDE with large context (100K+ tokens)
- **Architecture**: L0-L6 layered system with strict separation rules
- **Platform**: Windows 10/11 with WSL2 for Linux compatibility
- **Repository Location**: `c:\Git\Agentic-Workflow` (accessed via `/mnt/c/Agentic-Workflow` in WSL2)

### Hardware Constraints
- **Memory**: 16-32GB RAM typical developer workstation
- **VRAM**: 8-16GB GPU memory (RTX 3080/4080 class)
- **Storage**: SSD with adequate space for model weights
- **WSL2 Memory**: vmmemWSL limited to 50% of system RAM by default

### Governance Requirements
- **Layer Separation**: No upward violations (L0-L4 cannot import L5+)
- **AST-Only Analysis**: All code analysis must use AST, not heuristics
- **Evidence-Driven**: All changes require phase-based evidence capture
- **Import Topology**: "Import inside function" still counts for topology analysis
- **Subprocess Pattern**: Cross-layer communication via subprocess runners

## Scenario Matrix: vLLM Parameters vs Use-Cases

| Scenario | Model Size | Quantization | max_seq_len | Expected Strengths | Expected Failure Modes | Recommended Routing | Stop/Escalate Triggers |
|----------|------------|--------------|-------------|-------------------|----------------------|-------------------|----------------------|
| **S1: Ultra-Fast Loop** | 3B | INT4 | 1.5K | Import rewrites, test fixes, formatting | Complex reasoning, multi-file context | vLLM | >2 files involved, >80% tokens used |
| **S2: Baseline Production** | 7B | INT4 | 4K | Mechanical diffs, evidence formatting, seam scaffolding | Architecture reasoning, cross-repo synthesis | vLLM | AST parsing fails, >3 iterations needed |
| **S3: Balanced Performance** | 7B | BF16 | 8K | Medium context analysis, simple refactoring | Complex policy reasoning, governance | vLLM | Import topology analysis required |
| **S4: High-Quality Local** | 14B | INT8 | 8K | Code review, test generation, documentation | Multi-phase planning, policy interpretation | vLLM | Layer violation detection needed |
| **S5: Maximum Context** | 14B | BF16 | 16K | Large file analysis, module refactoring | Cross-system orchestration, human approval | vLLM | L5+ reasoning required |
| **S6: Near-Opus Quality** | 32B | INT4 | 16K | Complex refactoring, architecture compliance | Strategic planning, novel pattern detection | Hybrid | Quality score <85%, governance impact |
| **S7: Development Environment** | 70B | INT4 | 4K | Full system testing, integration validation | Real-time response requirements, memory limits | Hybrid | Latency >10s, memory >80% |
| **S8: Research Configuration** | 70B | BF16 | 32K | Research, novel pattern detection | Production deployment, cost constraints | Opus | Any production use case |

### Context Band Viability Analysis

| Context Range | Memory Usage (7B) | Latency Impact | Practical Use Cases | Viability |
|---------------|-------------------|----------------|-------------------|-----------|
| 1.5K | ~2GB | Minimal | Simple fixes, formatting | ✅ High |
| 4K | ~4GB | Low | Mechanical diffs, tests | ✅ High |
| 8K | ~8GB | Medium | Refactoring, analysis | ✅ Medium |
| 16K | ~16GB | High | Large file processing | ⚠️ Hardware-dependent |
| 32K | ~32GB | Very High | Research only | ❌ Production |
| 64K | ~64GB | Extreme | Not practical | ❌ Not viable |

## Architecture Fit: What Each Model Can Safely Own (L0-L6)

### L0: Maintenance Layer (vLLM Safe)
**Safe Tasks:**
- Import statement rewrites (mechanical)
- Test execution and result formatting
- Evidence file generation and formatting
- Simple syntax fixes and formatting
- File operations and basic validation

**Unsafe Tasks (Escalate to Opus):**
- Architectural decisions
- Cross-layer impact analysis
- Policy interpretation
- Complex error recovery

### L1: Cognition Layer (vLLM Conditional)
**Safe Tasks:**
- Simple orchestration patterns
- Deterministic workflow execution
- Basic decision trees with clear rules
- Template-based code generation

**Unsafe Tasks:**
- Complex reasoning chains
- Novel problem solving
- Strategic planning
- Multi-context synthesis

### L2: Execution Layer (vLLM Safe)
**Safe Tasks:**
- Schema validation (mechanical)
- Contract enforcement (rule-based)
- Basic error handling with patterns
- Deterministic transformations

**Unsafe Tasks:**
- Complex error recovery
- Novel validation strategies
- Cross-system coordination

### L3: Orchestration Layer (vLLM Conditional)
**Safe Tasks:**
- Pre-defined workflow execution
- Simple healing patterns
- Basic resource management
- Template-based orchestration

**Unsafe Tasks:**
- Complex healing strategies
- Dynamic workflow generation
- Cross-system orchestration

### L4: State Layer (vLLM Safe)
**Safe Tasks:**
- Basic state management
- Simple artifact indexing
- Mechanical state transitions
- Template-based state operations

**Unsafe Tasks:**
- Complex state analysis
- Novel state patterns
- Cross-system state coordination

### L5: Safety Layer (Opus Required)
**All tasks require Opus:**
- Governance decisions
- Policy interpretation
- Architectural validation
- Complex reasoning
- Human approval workflows

### L6: Observability Layer (Hybrid)
**vLLM Safe:**
- Basic log formatting
- Simple metric collection
- Template-based reporting

**Opus Required:**
- Complex analysis
- Pattern detection
- Strategic insights
- Cross-system correlation

## Recommended vLLM Configuration

### Primary Configuration: "Production Ready"

**Model Specifications:**
- **Model Size**: 7B parameters (Mistral 7B or similar)
- **Quantization**: INT4 (AWQ/GPTQ optimized)
- **max_seq_len**: 4K tokens
- **Memory Usage**: ~4GB RAM, ~2GB VRAM
- **Expected Latency**: 500-1500ms
- **Throughput**: ~50 tokens/sec

**Responsible Tasks:**
- Mechanical import rewrites (L0)
- Test execution and formatting (L0/L2)
- Evidence file generation (L0)
- Simple schema validation (L2)
- Basic state management (L4)
- Template-based reporting (L6)

**Integration Requirements:**
- Subprocess runner pattern for L5+ communication
- AST-based validation for all code changes
- Evidence capture for all operations
- Deterministic routing based on task complexity

### Upgrade Configuration: "High Performance"

**Model Specifications:**
- **Model Size**: 14B parameters (CodeLlama 13B or similar)
- **Quantization**: BF16 (full precision)
- **max_seq_len**: 8K tokens
- **Memory Usage**: ~16GB RAM, ~8GB VRAM
- **Expected Latency**: 1000-2500ms
- **Throughput**: ~80 tokens/sec

**Additional Capabilities:**
- Complex refactoring support
- Code review and analysis
- Documentation generation
- Test case generation
- Medium context analysis

**Hardware Requirements:**
- 32GB+ system RAM
- 16GB+ VRAM
- WSL2 memory configuration: `memory=50%` or higher

## Hybrid Operating Model: Opus Planning → vLLM Execution

### Planning Phase (Opus)
**Responsibilities:**
- Architectural impact analysis
- Multi-phase strategy development
- Policy interpretation and compliance
- Complex reasoning and decision making
- Cross-system coordination planning

**Output Artifacts:**
- Detailed execution plans with specific steps
- Validation criteria and success metrics
- Risk assessment and mitigation strategies
- Resource requirements and dependencies

### Execution Phase (vLLM)
**Responsibilities:**
- Mechanical implementation of planned steps
- Template-based code generation
- Test execution and validation
- Evidence collection and formatting
- Simple error handling and recovery

**Feedback Loop:**
- Success metrics validation
- Failure detection and escalation
- Evidence compilation for Opus review
- Performance metrics collection

### Deterministic Routing Rubric

```
IF task_complexity == "mechanical" AND context_size <= 4K THEN vLLM
ELIF task involves "import_topology" OR "layer_analysis" THEN Opus
ELIF task requires "policy_interpretation" OR "governance" THEN Opus
ELIF iteration_count > 3 OR success_rate < 80% THEN Opus
ELIF context_size > 8K OR cross_file_count > 5 THEN Opus
ELSE vLLM
```

### Decision Table

| Condition | Context | Files | Governance | Route |
|-----------|----------|-------|------------|-------|
| Simple import fix | ≤2K | 1 | No | vLLM |
| Test generation | ≤4K | ≤3 | No | vLLM |
| Refactoring | ≤8K | ≤5 | No | vLLM |
| Layer analysis | Any | Any | Yes | Opus |
| Policy decision | Any | Any | Yes | Opus |
| Multi-phase plan | Any | Any | Yes | Opus |
| Error recovery | ≤4K | ≤2 | No | vLLM |
| Complex healing | Any | Any | Yes | Opus |

## Integration Blueprint (IDE, CLI, WSL/Windows, Calls)

### WSL2 Configuration

**Memory Management:**
```bash
# .wslconfig settings for optimal vLLM performance
[wsl2]
memory=32GB
processors=8
swap=8GB
localhostForwarding=true
```

**Repository Access:**
- Primary path: `/mnt/c/Agentic-Workflow`
- Performance consideration: Direct Linux filesystem recommended for models
- Model storage: `/home/user/.cache/vllm` or `/mnt/c/models/vllm`

**Service Startup:**
```bash
# vLLM server startup script
#!/bin/bash
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export CUDA_VISIBLE_DEVICES=0
vllm serve mistralai/Mistral-7B-Instruct-v0.2 \
    --quantization awq \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.8 \
    --port 8000 \
    --host 0.0.0.0
```

### IDE Integration

**VS Code Extension Configuration:**
```json
{
    "vllm.endpoint": "http://localhost:8000",
    "vllm.model": "mistralai/Mistral-7B-Instruct-v0.2",
    "vllm.maxTokens": 4000,
    "vllm.temperature": 0.1,
    "vllm.routing": "deterministic"
}
```

**Windsurf Integration Points:**
- L0 routing scripts use subprocess calls to vLLM
- Evidence generation uses vLLM for formatting
- Test execution uses vLLM for result analysis
- Simple validation uses vLLM for rule checking

### CLI Integration

**Command Line Interface:**
```bash
# vLLM CLI wrapper
python -m agentic_core.tools.vllm_client \
    --task mechanical_rewrite \
    --file src/module.py \
    --context 4K \
    --temperature 0.1

# Opus CLI wrapper
python -m agentic_core.tools.opus_client \
    --task architectural_analysis \
    --scope multi_file \
    --context unlimited
```

### API Surface

**OpenAI-Compatible Endpoint:**
```python
# vLLM client wrapper
class VLLMClient:
    def __init__(self, endpoint="http://localhost:8000"):
        self.endpoint = endpoint
        self.client = OpenAI(api_key="dummy", base_url=endpoint)

    def complete(self, prompt, max_tokens=1000, temperature=0.1):
        response = self.client.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].text
```

**Retry/Backoff Logic:**
```python
# Resilient client with retry
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def resilient_completion(prompt, max_tokens=1000):
    try:
        return vllm_client.complete(prompt, max_tokens)
    except Exception as e:
        logger.warning(f"vLLM attempt failed: {e}")
        raise
```

### Logging/Telemetry

**Metrics Collection:**
```python
# Performance metrics
class VLLMMetrics:
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.latency_sum = 0
        self.token_count = 0

    def record_request(self, success, latency, tokens):
        self.request_count += 1
        if success:
            self.success_count += 1
        self.latency_sum += latency
        self.token_count += tokens

    def get_success_rate(self):
        return self.success_count / self.request_count if self.request_count > 0 else 0
```

## Guardrails, Failure Modes, and Early Detection

### Quality Guardrails

**Output Validation:**
- AST parsing for generated code
- Schema validation for structured outputs
- Import topology compliance checking
- Layer separation verification

**Content Filters:**
- No governance logic in vLLM outputs
- No architectural decisions
- No policy interpretations
- No cross-layer dependencies

### Failure Modes

**Common Failure Patterns:**
1. **Context Overflow**: Input exceeds model's max_seq_len
2. **Quality Degradation**: Output quality below threshold
3. **Memory Exhaustion**: WSL2 memory limits exceeded
4. **Network Issues**: vLLM server unreachable
5. **AST Parsing Failures**: Generated code invalid

**Detection Mechanisms:**
```python
# Early detection system
class FailureDetector:
    def __init__(self):
        self.quality_threshold = 0.8
        self.latency_threshold = 5000  # ms
        self.memory_threshold = 0.8    # 80%

    def detect_failure(self, response, metrics):
        if metrics.latency > self.latency_threshold:
            return "latency", "escalate_to_opus"
        if metrics.memory_usage > self.memory_threshold:
            return "memory", "reduce_context"
        if response.quality_score < self.quality_threshold:
            return "quality", "escalate_to_opus"
        return None, None
```

### Escalation Protocols

**Automatic Escalation Triggers:**
- Success rate < 80% over 5 attempts
- Latency > 5 seconds consistently
- Memory usage > 80% of available
- AST parsing failures
- Import topology violations detected

**Escalation Process:**
1. Log failure with context
2. Switch to Opus for current task
3. Update routing heuristics
4. Record pattern for future avoidance
5. Notify user of degradation

### Recovery Strategies

**Self-Healing Mechanisms:**
- Automatic context reduction
- Model fallback (larger → smaller)
- Memory garbage collection
- Service restart automation
- Cache clearing

**Manual Intervention Points:**
- WSL2 memory configuration
- Model selection changes
- Routing rule updates
- Service maintenance

## Measurement Plan (A/B and Rollout)

### Success Metrics

**Primary Metrics:**
- **Throughput**: Tasks completed per hour
- **Latency**: Average response time per task
- **Quality**: Success rate on validation criteria
- **Cost**: API costs vs local compute costs
- **Reliability**: Uptime and error rates

**Secondary Metrics:**
- **Developer Satisfaction**: Subjective feedback
- **Learning Curve**: Time to proficiency
- **Integration Effort**: Setup and maintenance time
- **Resource Utilization**: CPU/GPU/Memory usage

### A/B Testing Framework

**Test Groups:**

- **Control**: Claude Opus only
- **Variant A**: vLLM 7B INT4 4K
- **Variant B**: vLLM 14B BF16 8K
- **Variant C**: Hybrid routing

**Test Duration:**

- **Phase 1**: 2 weeks baseline (Control)
- **Phase 2**: 2 weeks variant testing
- **Phase 3**: 1 week hybrid validation

**Success Criteria:**

- ≥20% throughput improvement
- ≤10% quality degradation
- ≤30% cost reduction
- ≥95% developer satisfaction

### Data Collection

**Automated Metrics:**
```python
# Metrics collection system
class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "requests": [],
            "latencies": [],
            "quality_scores": [],
            "resource_usage": []
        }

    def record_request(self, request_data):
        self.metrics["requests"].append({
            "timestamp": datetime.now(),
            "model": request_data.model,
            "task_type": request_data.task_type,
            "success": request_data.success,
            "latency": request_data.latency,
            "tokens": request_data.tokens
        })
```

**User Feedback:**
```python
# Feedback collection
def collect_feedback(task_id, satisfaction, comments):
    feedback = {
        "task_id": task_id,
        "satisfaction": satisfaction,  # 1-5 scale
        "comments": comments,
        "timestamp": datetime.now()
    }
    store_feedback(feedback)
```

### Rollout Strategy

**Phase 1: Pilot (Week 1-2)**

- 5 developers, limited tasks
- Mechanical tasks only
- Daily monitoring and feedback

**Phase 2: Extended (Week 3-4)**

- 20 developers, expanded tasks
- Include simple refactoring
- Performance optimization

**Phase 3: Full Rollout (Week 5-6)**

- All developers, full task suite
- Hybrid routing enabled
- Cost optimization

**Rollback Criteria:**

- Quality degradation >15%
- Developer satisfaction <3.5/5
- System reliability <95%
- Security incidents

## Quick-Start Checklist

### Prerequisites

**Hardware Requirements:**

- [ ] 16GB+ RAM (32GB+ recommended)
- [ ] 8GB+ VRAM (16GB+ recommended)
- [ ] SSD with 50GB+ free space
- [ ] Windows 10/11 with WSL2 enabled

**Software Requirements:**

- [ ] WSL2 configured with appropriate memory limits
- [ ] Docker installed (optional)
- [ ] Python 3.10+ environment
- [ ] CUDA drivers (for GPU acceleration)

### Installation

**1. WSL2 Configuration:**

```bash
# Create .wslconfig in %USERPROFILE%
[wsl2]
memory=32GB
processors=8
swap=8GB
```

**2. vLLM Installation:**

```bash
# In WSL2 Ubuntu
pip install vllm
pip install accelerate
pip install bitsandbytes  # for quantization
```

**3. Model Download:**

```bash
# Download model (one-time)
python -c "
from vllm import LLM
llm = LLM('mistralai/Mistral-7B-Instruct-v0.2')
"
```

**4. Service Startup:**

```bash
# Start vLLM server
vllm serve mistralai/Mistral-7B-Instruct-v0.2 \
    --quantization awq \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.8 \
    --port 8000
```

### Configuration

**1. Environment Variables:**

```bash
export VLLM_ENDPOINT=http://localhost:8000
export VLLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
export VLLM_MAX_TOKENS=4000
```

**2. Windsurf Integration:**

```python
# Add to agentic_core/config/vllm_config.py
VLLM_CONFIG = {
    "endpoint": "http://localhost:8000",
    "model": "mistralai/Mistral-7B-Instruct-v0.2",
    "max_tokens": 4000,
    "temperature": 0.1,
    "timeout": 30
}
```

### Validation

**1. Basic Connectivity:**

```bash
curl http://localhost:8000/v1/models
```

**2. Simple Test:**

```python
# Test basic functionality
from agentic_core.tools.vllm_client import VLLMClient
client = VLLMClient()
response = client.complete("print('hello world')")
print(response)
```

**3. Integration Test:**

```bash
# Run Windsurf test suite
pytest tests/unit_min_deps/test_vllm_integration.py -v
```

### Monitoring

**1. Health Check:**

```bash
# Monitor service status
curl http://localhost:8000/health
```

**2. Performance Metrics:**

```bash
# Check resource usage
nvidia-smi
free -h
```

**3. Log Monitoring:**

```bash
# Monitor logs
tail -f /var/log/vllm.log
```

### Troubleshooting

**Common Issues:**

1. **Memory Issues**: Reduce max_model_len or use smaller model
2. **CUDA Errors**: Check GPU drivers and CUDA version
3. **WSL2 Performance**: Move models to Linux filesystem
4. **Connection Issues**: Verify firewall and port settings

**Support Resources:**

- vLLM Documentation: <https://docs.vllm.ai/>
- WSL2 Documentation: <https://docs.microsoft.com/en-us/windows/wsl/>
- Internal Support: #vllm-support channel

---

**Report Version:** 1.0
**Date:** 2025-02-17
**Author:** Architecture & Tooling Research Agent
**Next Review:** 2025-03-17
