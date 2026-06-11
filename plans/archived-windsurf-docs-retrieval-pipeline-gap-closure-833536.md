---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\retrieval-pipeline-gap-closure-833536.md'
original_relative_path: 'retrieval-pipeline-gap-closure-833536.md'
source_sha256: 002b19b07fbb10ac38cbe4a2a7059c3c6004525c08b35c1fd606780cb3f893b1
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-04-01'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Retrieval Pipeline Gap Closure Implementation Plan

Comprehensive plan to address gaps between the documented "Ingestion and Retrieval Pipeline" and current implementation, focusing on observability instrumentation, telemetry wiring, and runtime ADG consumption.

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| Wave 0 | 0.1-0.3 | Prometheus instrumentation prerequisites | 18,500 🟢 | Requirements.txt editable; no existing prometheus_client conflicts | Not Started | `/metrics` endpoint returns agentic_workflow_* metrics |
| Wave 1 | 1.1-1.4 | Trace decorators + apps_* agent span coverage | 28,000 🟢 | TracingMixin inheritance exists; IntegratedTracingMixin functional | Not Started | All apps_* agent methods emit OTel spans; 16/16 E2E tests pass |
| Wave 2 | 2.1-2.4 | Snapshot ADG extraction + semantic edge types | 22,000 🟢 | Runtime ADG materializer exists; span schema extensible | Not Started | Snapshots contain all 13 edge types; validation passes |
| Wave 3 | 3.1-3.4 | Runtime ADG persistence + query API exposure | 26,500 🟢 | FileBackedRuntimeADGStore functional; L4 compliance verified | Not Started | Query API <100ms p95; persistence survives restart |
| Wave 4 | 4.1-4.3 | Grafana dashboards + operational visibility | 19,000 🟢 | K8s ConfigMap accessible; Grafana provisioning enabled | Not Started | Dashboards show per-agent metrics; drill-down functional |
| Wave 5 | 5.1-5.4 | Eval-to-meta-learning wiring | 32,000 🟢 | MetaLearningBus exists; FeatureBundle schema stable | Not Started | Eval spans consumed by ML bus within 30s |
| Wave 6 | 6.1-6.5 | Runtime ADG consumption by agents | 38,000 🟢 | Query client from Wave 3; agent decision points identifiable | Not Started | Agents query ADG for pattern-based decisions |

**Total: 184,000 tokens across 7 waves, all GREEN (within 197K safe threshold)**

---

## Gap Register

**GAP-1: No Prometheus Client Instrumentation (DEFECT-001)**
- **Location**: `agentic_core/` (entire module)
- **Current State**: K8s YAML configs exist but zero Python code to emit metrics
- **Impact**: Operators deploy Prometheus to empty targets; no operational visibility
- **Required Fix**: Create `prometheus_metrics.py` with Counter/Histogram/Gauge; add `metrics_server.py` with `start_http_server()`

**GAP-2: apps_* Agents Don't Create OTel Spans (DEFECT-002)**
- **Location**: `apps_lic/reasoning/`, `apps_rg/reasoning/`, `apps_eval/reasoning/`
- **Current State**: Agents inherit TracingMixin but never call `start_span()`
- **Impact**: Traces only capture top-level orchestration, missing reasoning granularity
- **Required Fix**: Add `@trace_cognitive`, `@trace_action`, `@trace_tool` decorators; audit all apps_* Agent classes

**GAP-3: Snapshot ADG Missing Semantic Edge Types (Pipeline C Gap)**
- **Location**: `system_learning/runtime_adg/materializer.py`
- **Current State**: Only `parent_child` and `temporal_sequence` edges extracted
- **Impact**: Pipeline C "4 parallel lanes" (Fast Terminal, Rerank, Heap, Matrix) not represented in runtime ADG
- **Required Fix**: Add `_extract_semantic_edges()` for `orchestration_handoff`, `tool_invocation`, `retry`, `evaluation`, `policy_validation`

**GAP-4: Runtime ADG Not Queryable by Agents (DEFECT-007)**
- **Location**: `system_learning/runtime_adg/l6_integration.py`
- **Current State**: `L6MetaLearningBridge.get_execution_patterns()` exists but not exposed to agents
- **Impact**: Pipeline C "Reading Room" can't access historical execution patterns for decision support
- **Required Fix**: Create `runtime_adg_query_client.py`; expose query methods to agents during execution

**GAP-5: Evaluation Signals Don't Feed Meta-Learning (DEFECT-005, DEFECT-008)**
- **Location**: `apps_eval/integrations/observability_adapter.py`, `system_learning/engines/meta_learning_bus.py`
- **Current State**: Eval results stay in memory (stub adapter); ML bus consumes synthetic signals not live traces
- **Impact**: Evaluation loop doesn't drive intelligence improvement; learning based on stale/aggregated data
- **Required Fix**: Wire `OpenTelemetrySpanStore` to `MetaLearningBus.process_traces()`; convert span attributes to FeatureBundles

**GAP-6: Grafana Dashboards Static Only (DEFECT-003)**
- **Location**: `k8s/grafana-dashboards-configmap.yaml`
- **Current State**: Static JSON dashboards; no template variables or drill-down
- **Impact**: Operators can't filter by agent instance, trace ID, replay key
- **Required Fix**: Add template variables for `agent_type`, `trace_id`, `mission`; create drill-down links to Jaeger

**GAP-7: Missing Pipeline B Chunking Strategies (Documentation Gap)**
- **Location**: `agentic_core/L1_cognition/`
- **Current State**: Generic chunking only; no corpus-specific strategies documented in "Ingestion and Retrieval Pipeline.md"
- **Impact**: Policy documents, incident traces, code files all chunked with same strategy = suboptimal retrieval
- **Required Fix**: Implement corpus-specific chunking per Pipeline B section 4: Policy/Long Document, Incident/Trace, Code/Config, Visuals/Tables

---

## Execution Plan

### Wave 0 — Prometheus Instrumentation Prerequisites (2-3 days)

**Scope**: Enable metric emission and local Prometheus endpoint

#### Phase 0.1 — Requirements and Module Structure
```bash
# Add dependency
python -c "import pkg_resources; print('prometheus_client>=0.19.0')" >> requirements.txt

# Create module structure
mkdir -p agentic_core/L6_observability/metrics
mkdir -p agentic_core/L6_observability/engines
```

**Files to Create**:
- `agentic_core/L6_observability/metrics/__init__.py`
- `agentic_core/L6_observability/metrics/prometheus_metrics.py`
- `agentic_core/L6_observability/engines/__init__.py`
- `agentic_core/L6_observability/engines/metrics_server.py`

#### Phase 0.2 — Prometheus Metrics Module
**File**: `agentic_core/L6_observability/metrics/prometheus_metrics.py`

**Implementation**:
```python
from prometheus_client import Counter, Histogram, Gauge, Info

# Routing metrics
ROUTING_DECISIONS_TOTAL = Counter(
    'agentic_workflow_routing_decisions_total',
    'Total routing decisions by layer and destination',
    ['layer', 'destination']
)

ROUTING_LATENCY_SECONDS = Histogram(
    'agentic_workflow_routing_latency_seconds',
    'Routing decision latency',
    ['layer'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# Cache metrics
CACHE_HITS_TOTAL = Counter(
    'agentic_workflow_cache_hits_total',
    'Total cache hits by cache type',
    ['cache_type']
)

CACHE_MISSES_TOTAL = Counter(
    'agentic_workflow_cache_misses_total',
    'Total cache misses by cache type',
    ['cache_type']
)

# Guardrail metrics
GUARDRAIL_TRIGGERS_TOTAL = Counter(
    'agentic_workflow_guardrail_triggers_total',
    'Total guardrail triggers by policy type and outcome',
    ['policy_type', 'outcome']
)

# Retrieval quality metrics
RETRIEVAL_GROUNDEDNESS_SCORE = Gauge(
    'agentic_workflow_retrieval_groundedness_score',
    'Retrieval groundedness score for query results',
    ['query_type']
)

# Runtime ADG metrics
SNAPSHOT_GENERATION_TOTAL = Counter(
    'agentic_workflow_snapshot_generation_total',
    'Total runtime ADG snapshots generated',
    ['mission_type']
)
```

#### Phase 0.3 — Metrics Server
**File**: `agentic_core/L6_observability/engines/metrics_server.py`

**Implementation**:
```python
from prometheus_client import start_http_server, REGISTRY
from agentic_core.L6_observability.metrics.prometheus_metrics import *

def start_metrics_server(port: int = 8000, addr: str = '0.0.0.0') -> None:
    """Start Prometheus metrics HTTP server."""
    start_http_server(port, addr)
    
def stop_metrics_server() -> None:
    """Stop metrics server (for testing)."""
    # Implementation for graceful shutdown
```

**Acceptance Criteria**:
- `python -c "from agentic_core.L6_observability import start_metrics_server; start_metrics_server(8000)"` exposes `/metrics`
- `curl localhost:8000/metrics | grep agentic_workflow` returns non-empty output
- All counter/histogram/gauge definitions importable without error

**Proof Artifacts**:
- Screenshot of `/metrics` endpoint showing `agentic_workflow_*` metrics
- Output of `curl localhost:8000/metrics`

---

### Wave 1 — Trace Decorators + apps_* Agent Coverage (3-4 days)

**Scope**: Ensure all execution seams emit traceable, reconstructable telemetry

#### Phase 1.1 — Tracing Decorators Module
**File**: `agentic_core/mixins/tracing_decorators.py` (new)

**Implementation**:
```python
import functools
from typing import Callable, Any
from agentic_core.L6_observability.utils.tracing_mixin import TracingMixin

def trace_cognitive(operation_type: str):
    """Decorator for cognitive/reasoning operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'start_span'):
                with self.start_span(f"cognitive.{operation_type}") as span:
                    span.set_attribute("layer", "L1")
                    span.set_attribute("operation", operation_type)
                    result = func(self, *args, **kwargs)
                    span.set_attribute("success", True)
                    return result
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def trace_action(action_type: str):
    """Decorator for action/tool execution operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'start_span'):
                with self.start_span(f"action.{action_type}") as span:
                    span.set_attribute("layer", "L2")
                    span.set_attribute("action", action_type)
                    result = func(self, *args, **kwargs)
                    span.set_attribute("success", True)
                    return result
            return func(self, *args, **kwargs)
        return wrapper
    return decorator

def trace_tool(tool_name: str):
    """Decorator for tool invocation operations."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'start_span'):
                with self.start_span(f"tool.{tool_name}") as span:
                    span.set_attribute("layer", "L2")
                    span.set_attribute("tool", tool_name)
                    result = func(self, *args, **kwargs)
                    span.set_attribute("success", True)
                    return result
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
```

#### Phase 1.2 — apps_lic Agent Instrumentation
**Files to Modify**:
- `apps_lic/reasoning/OutreachMessageAgent.py`
- `apps_lic/reasoning/DeliverabilityAgent.py`
- `apps_lic/reasoning/CampaignBalanceAgent.py`
- `apps_lic/reasoning/ArchetypeIndicatorsAgent.py`
- (11 additional files in `apps_lic/reasoning/`)

**Pattern to Apply**:
```python
from agentic_core.mixins.tracing_decorators import trace_cognitive, trace_action

class OutreachMessageAgent(SovereignBaseAgent):
    
    @trace_cognitive("message_generation")
    def generate_message(self, context: dict) -> str:
        # Existing implementation
        pass
    
    @trace_action("send_outreach")
    def send_outreach(self, message: str, recipient: str) -> dict:
        # Existing implementation
        pass
```

#### Phase 1.3 — apps_rg + apps_eval Agent Instrumentation
**Files to Modify**:
- `apps_rg/reasoning/*.py` (all 31 agent files)
- `apps_eval/reasoning/*.py` (5 agent files)

#### Phase 1.4 — Trace Correlation Integration
**File**: `agentic_core/L0_routing/seams/observability_seam.py`

**Implementation**:
```python
def ensure_trace_id_propagation(context: dict) -> dict:
    """Ensure trace_id propagates across all ingress points."""
    if 'trace_id' not in context:
        context['trace_id'] = generate_trace_id()
    return context
```

**Acceptance Criteria**:
- `pytest tests/e2e/test_runtime_adg_e2e.py -v` passes with 16/16 tests
- All apps_* agent method calls create at least one span
- Span attributes include `layer`, `component`, `mission`

**Proof Artifacts**:
- `test_runtime_adg_e2e.py` test output showing 16/16 pass
- Sample span JSON showing complete attribute set
- Jaeger UI screenshot showing trace hierarchy

---

### Wave 2 — Snapshot ADG Extraction + Semantic Edge Types (2-3 days)

**Scope**: Ensure runtime telemetry produces valid Snapshot ADG artifacts with Pipeline C lane representations

#### Phase 2.1 — Span Schema Extension
**File**: `apps_shared/utils/open_telemetry_tracing_adapter_util.py`

**Add Standardized Attributes**:
```python
# In span creation methods
span.set_attribute("agent_type", agent_type)
span.set_attribute("operation", operation_name)
span.set_attribute("status", status)
span.set_attribute("layer", layer)
span.set_attribute("lane", lane)  # NEW: fast_terminal, rerank, heap, matrix
```

#### Phase 2.2 — Semantic Edge Extraction
**File**: `system_learning/runtime_adg/materializer.py`

**Add Function**:
```python
def _extract_semantic_edges(self, spans: list[dict]) -> list[RuntimeADGEdge]:
    """Extract semantic edges for Pipeline C lanes."""
    edges = []
    
    # Group spans by lane
    lane_spans = defaultdict(list)
    for span in spans:
        lane = span.get('attributes', {}).get('lane', 'unknown')
        lane_spans[lane].append(span)
    
    # Create orchestration handoff edges between lanes
    lane_order = ['fast_terminal', 'rerank', 'heap', 'matrix']
    for i in range(len(lane_order) - 1):
        current_lane = lane_order[i]
        next_lane = lane_order[i + 1]
        
        for curr_span in lane_spans[current_lane]:
            for next_span in lane_spans[next_lane]:
                edges.append(RuntimeADGEdge(
                    src_id=curr_span['span_id'],
                    dst_id=next_span['span_id'],
                    relation='orchestration_handoff'
                ))
    
    # Create tool invocation edges
    for span in spans:
        if span.get('attributes', {}).get('operation') == 'tool_invoke':
            edges.append(RuntimeADGEdge(
                src_id=span['span_id'],
                dst_id=span['attributes'].get('tool_target', 'unknown'),
                relation='tool_invocation'
            ))
    
    return edges
```

#### Phase 2.3 — Snapshot Validation
**File**: `system_learning/runtime_adg/snapshot.py`

**Add Method**:
```python
def validate(self) -> tuple[bool, list[str]]:
    """Validate snapshot integrity."""
    errors = []
    
    # Check all nodes have required fields
    for node in self.nodes:
        if not node.node_id:
            errors.append(f"Node missing node_id")
        if not node.layer:
            errors.append(f"Node {node.node_id} missing layer")
    
    # Check all edges reference valid nodes
    node_ids = {n.node_id for n in self.nodes}
    for edge in self.edges:
        if edge.src_id not in node_ids and edge.src_id != "__root__":
            errors.append(f"Edge references unknown src: {edge.src_id}")
        if edge.dst_id not in node_ids:
            errors.append(f"Edge references unknown dst: {edge.dst_id}")
    
    # Check for required edge types
    edge_types = {e.relation for e in self.edges}
    required_types = {'parent_child', 'temporal_sequence', 'orchestration_handoff'}
    missing = required_types - edge_types
    if missing:
        errors.append(f"Missing required edge types: {missing}")
    
    return len(errors) == 0, errors
```

#### Phase 2.4 — Edge Type Registry
**File**: `agentic_core/adg/schema.py`

**Add Edge Types**:
```python
# Add to existing RelationType or create new registry
RUNTIME_EDGE_TYPES = frozenset([
    'parent_child',
    'temporal_sequence', 
    'orchestration_handoff',
    'tool_invocation',
    'retry',
    'evaluation',
    'policy_validation',
])
```

**Acceptance Criteria**:
- Snapshot contains all 13 edge types from Gap Register
- Node attributes include `agent_type`, `operation`, `layer`
- `snapshot.validate()` returns True for all generated snapshots

---

### Wave 3 — Persistence + Query API Exposure (3-4 days)

**Scope**: Ensure Snapshot ADG artifacts are persisted and queryable by agents at runtime

#### Phase 3.1 — Store Indexing Enhancement
**File**: `system_learning/runtime_adg/store.py`

**Add Indexing**:
```python
def _update_indexes(self, snapshot: RuntimeADGSnapshot, version_id: str) -> None:
    """Update query indexes for fast retrieval."""
    # Index by agent_type
    for node in snapshot.nodes:
        agent_type = node.attributes.get('agent_type', 'unknown')
        if agent_type not in self._agent_type_index:
            self._agent_type_index[agent_type] = set()
        self._agent_type_index[agent_type].add(version_id)
    
    # Index by mission
    if snapshot.mission:
        if snapshot.mission not in self._mission_index:
            self._mission_index[snapshot.mission] = set()
        self._mission_index[snapshot.mission].add(version_id)
    
    # Index by outcome (success/error)
    has_errors = any(n.status == 'error' for n in snapshot.nodes)
    outcome = 'error' if has_errors else 'success'
    if outcome not in self._outcome_index:
        self._outcome_index[outcome] = set()
    self._outcome_index[outcome].add(version_id)
```

#### Phase 3.2 — Query Client Implementation
**File**: `agentic_core/L6_observability/query/runtime_adg_query_client.py` (new)

**Implementation**:
```python
from system_learning.runtime_adg.l6_integration import L6MetaLearningBridge

class RuntimeADGQueryClient:
    """Client for agents to query historical runtime ADG snapshots."""
    
    def __init__(self) -> None:
        self._bridge = L6MetaLearningBridge()
    
    def query_similar_executions(
        self,
        mission_type: str,
        agent_type: str | None = None,
        limit: int = 10
    ) -> list[dict]:
        """Query similar past executions for decision support."""
        patterns = self._bridge.get_execution_patterns()
        
        # Filter by mission type similarity
        similar = [
            p for p in patterns
            if p.get('mission_type') == mission_type
        ]
        
        if agent_type:
            similar = [p for p in similar if p.get('agent_type') == agent_type]
        
        return similar[:limit]
    
    def query_error_patterns(
        self,
        component: str,
        time_window_hours: int = 24
    ) -> list[dict]:
        """Query recent error patterns for a component."""
        # Implementation using evolution log
        pass
```

#### Phase 3.3 — L6 Bridge Query Methods
**File**: `system_learning/runtime_adg/l6_integration.py`

**Add Methods**:
```python
def query_similar_executions(
    self,
    mission_type: str,
    agent_type: str | None = None,
    outcome: str | None = None,
    limit: int = 10
) -> list[dict]:
    """Query similar executions with filters."""
    results = []
    
    for ml_id, metadata in self._snapshot_index.items():
        if metadata['mission'] == mission_type:
            if agent_type and metadata.get('agent_type') != agent_type:
                continue
            if outcome and metadata.get('outcome') != outcome:
                continue
            results.append(metadata)
    
    # Sort by timestamp desc
    results.sort(key=lambda x: x['timestamp'], reverse=True)
    return results[:limit]
```

#### Phase 3.4 — REST API (Optional)
**File**: `agentic_core/L6_observability/api/runtime_adg_api.py` (new)

**Implementation**:
```python
from fastapi import FastAPI
from agentic_core.L6_observability.query.runtime_adg_query_client import RuntimeADGQueryClient

app = FastAPI()
client = RuntimeADGQueryClient()

@app.get("/api/v1/similar-executions")
async def similar_executions(
    mission_type: str,
    agent_type: str | None = None,
    limit: int = 10
):
    return client.query_similar_executions(mission_type, agent_type, limit)
```

**Acceptance Criteria**:
- Agent can query: "show me similar past executions for this mission type" 
- Query returns list of snapshots within 100ms (p95)
- Persistence survives process restart

---

### Wave 4 — Grafana Dashboards + Operational Visibility (2-3 days)

**Scope**: Make failure and quality visible in Prometheus/Grafana

#### Phase 4.1 — Dashboard Template Variables
**File**: `k8s/grafana-dashboards-configmap.yaml`

**Add to Existing Dashboards**:
```json
{
  "templating": {
    "list": [
      {
        "name": "agent_type",
        "type": "query",
        "query": "label_values(agentic_workflow_routing_decisions_total, layer)"
      },
      {
        "name": "trace_id",
        "type": "custom",
        "query": ".*"
      },
      {
        "name": "mission",
        "type": "custom", 
        "query": ".*"
      }
    ]
  }
}
```

#### Phase 4.2 — Retrieval Quality Dashboard
**Add New Dashboard**: "Retrieval Quality"

**Panels**:
- `retrieval_groundedness_score` gauge
- `faithfulness_ratio` over time
- `citation_completeness` by query type
- Top-N underperforming queries

#### Phase 4.3 — Healing Effectiveness Dashboard
**Add New Dashboard**: "Healing Effectiveness"

**Panels**:
- `heal_attempts_total` vs `heal_success_total`
- `heal_duration_seconds` histogram
- Healing success rate by type

**Acceptance Criteria**:
- Grafana dashboards show per-agent metrics
- Drill-down from dashboard to trace works
- Alerts fire on retrieval quality < 0.8 for 5m

---

### Wave 5 — Eval-to-Meta-Learning Wiring (4-5 days)

**Scope**: Ensure evaluation signals feed the meta-learning bus

#### Phase 5.1 — Eval Adapter Enhancement
**File**: `apps_eval/integrations/observability_adapter.py`

**Implementation**:
```python
from apps_shared.utils.open_telemetry_tracing_adapter_util import OpenTelemetryTracingAdapter

def emit_eval_complete(self, result: EvalResult) -> dict[str, Any]:
    """Emit evaluation completion as OTel span."""
    # Create span via OTel adapter
    tracer = OpenTelemetryTracingAdapter()
    
    with tracer.start_span("eval.complete") as span:
        span.set_attribute("trace_id", result.trace_id)
        span.set_attribute("overall_score", result.overall_score)
        span.set_attribute("gate_passed", result.passed_gate)
        span.set_attribute("violations", len(result.gate_violations))
        
        # Also emit to internal metrics
        event = {
            "event_type": "eval_complete",
            "trace_id": result.trace_id,
            "status": result.status,
            "overall_score": result.overall_score,
            "gate_passed": result.passed_gate,
            "violations": len(result.gate_violations),
            "timestamp": self._timestamp(),
        }
        self._metrics.append(event)
        return event
```

#### Phase 5.2 — Telemetry Store Ingestion
**File**: `system_learning/stores/otel_telemetry_store.py`

**Add Method**:
```python
def ingest_eval_spans(self, spans: list[dict]) -> None:
    """Ingest evaluation-specific spans."""
    for span in spans:
        if span.get('attributes', {}).get('span_kind') == 'eval':
            self._eval_span_index[span['span_id']] = span
            self._persist_eval_span(span)
```

#### Phase 5.3 — ML Bus Consumption
**File**: `system_learning/engines/meta_learning_bus.py`

**Add Method**:
```python
def consume_eval_spans(self, spans: list[dict]) -> list[GovernanceRewardSignal]:
    """Convert eval spans to FeatureBundles for learning."""
    signals = []
    
    for span in spans:
        attrs = span.get('attributes', {})
        
        # Create FeatureBundle from eval attributes
        bundle = FeatureBundle(
            trace_id=span['trace_id'],
            eval_score=attrs.get('overall_score', 0.0),
            gate_passed=attrs.get('gate_passed', False),
            violations=attrs.get('violations', 0),
        )
        
        # Convert to reward signal
        signal = self._bundle_to_reward_signal(bundle)
        signals.append(signal)
    
    return signals
```

#### Phase 5.4 — EvalOrchestrator Wiring
**File**: `apps_eval/reasoning/EvalOrchestrator.py`

**Add Call**:
```python
async def run_evaluation(self, request: EvalRequest) -> EvalResult:
    # ... existing evaluation logic ...
    
    # Emit to observability
    self.observability_adapter.emit_eval_complete(result)
    
    # NEW: Also emit as OTel span for meta-learning
    await self._emit_eval_span(result)
    
    return result

async def _emit_eval_span(self, result: EvalResult) -> None:
    """Emit eval result as OTel span for meta-learning consumption."""
    from apps_shared.utils.open_telemetry_tracing_adapter_util import OpenTelemetryTracingAdapter
    
    tracer = OpenTelemetryTracingAdapter()
    with tracer.start_span("eval.complete") as span:
        span.set_attribute("eval.trace_id", result.trace_id)
        span.set_attribute("eval.score", result.overall_score)
        span.set_attribute("eval.gate_passed", result.passed_gate)
```

**Acceptance Criteria**:
- Eval completion triggers span emission to telemetry store
- Meta-learning bus consumes eval spans within 30s
- Eval results influence proposal generation within 1 hour

---

### Wave 6 — Runtime ADG Consumption by Agents (5-7 days)

**Scope**: Enable agents and scripts to improve from runtime ADG evidence

#### Phase 6.1 — Query Client Pattern Matching
**File**: `agentic_core/L6_observability/query/runtime_adg_query_client.py`

**Add Methods**:
```python
def find_similar_error_patterns(
    self,
    error_signature: str,
    component: str | None = None
) -> list[dict]:
    """Find executions with similar error patterns."""
    patterns = self._bridge.get_execution_patterns()
    
    similar_errors = [
        p for p in patterns
        if any(
            error_signature in e.get('signature', '')
            for e in p.get('error_patterns', [])
        )
    ]
    
    if component:
        similar_errors = [
            p for p in similar_errors
            if p.get('component') == component
        ]
    
    return similar_errors

def get_historical_route_performance(
    self,
    route_name: str,
    time_window_hours: int = 168  # 1 week
) -> dict:
    """Get performance metrics for a route over time."""
    # Query pattern index for route performance
    pass
```

#### Phase 6.2 — Intent Expansion Integration
**File**: `agentic_core/L1_cognition/engines/intent_expansion.py`

**Integration**:
```python
from agentic_core.L6_observability.query.runtime_adg_query_client import RuntimeADGQueryClient

def expand_intent(self, query: str, context: dict) -> list[str]:
    """Expand intent with historical pattern support."""
    # Query runtime ADG for similar past intents
    client = RuntimeADGQueryClient()
    similar = client.query_similar_executions(
        mission_type='intent_expansion',
        limit=5
    )
    
    # Incorporate historical patterns into expansion
    historical_expansions = [
        s.get('final_intent') for s in similar
        if s.get('final_intent')
    ]
    
    # Merge with standard expansion
    return self._merge_expansions(query, historical_expansions)
```

#### Phase 6.3 — Healing Strategy Integration
**File**: `agentic_core/L3_orchestration/enforcement/healing_strategy.py`

**Integration**:
```python
def select_healing_action(self, failure_context: dict) -> str:
    """Select healing action based on historical success rates."""
    client = RuntimeADGQueryClient()
    
    # Query for similar past healing outcomes
    similar_healings = client.find_similar_error_patterns(
        error_signature=failure_context.get('error_type', 'unknown'),
        component=failure_context.get('component')
    )
    
    # Calculate success rate by healing type
    success_rates = {}
    for healing in similar_healings:
        action = healing.get('healing_action', 'unknown')
        outcome = healing.get('outcome', 'unknown')
        
        if action not in success_rates:
            success_rates[action] = {'success': 0, 'total': 0}
        
        success_rates[action]['total'] += 1
        if outcome == 'success':
            success_rates[action]['success'] += 1
    
    # Select action with highest success rate
    best_action = max(
        success_rates.items(),
        key=lambda x: x[1]['success'] / max(x[1]['total'], 1)
    )[0] if success_rates else 'default_heal'
    
    return best_action
```

#### Phase 6.4 — Routing Engine Integration
**File**: `agentic_core/L0_routing/engines/routing_engine.py`

**Integration**:
```python
def select_route(
    self,
    intent: str,
    available_routes: list[str],
    context: dict
) -> str:
    """Select route considering historical performance."""
    client = RuntimeADGQueryClient()
    
    # Get historical latency for each route
    route_scores = {}
    for route in available_routes:
        performance = client.get_historical_route_performance(route)
        avg_latency = performance.get('avg_latency_ms', 1000)
        success_rate = performance.get('success_rate', 0.5)
        
        # Score based on latency and success
        route_scores[route] = (
            success_rate * 0.7 +  # Weight success higher
            (1 / (1 + avg_latency / 1000)) * 0.3  # Latency factor
        )
    
    # Select best route
    best_route = max(route_scores.items(), key=lambda x: x[1])[0]
    return best_route
```

#### Phase 6.5 — Meta-Learning Pipeline Integration
**File**: `system_learning/pipelines/meta_learning_pipeline.py`

**Integration**:
```python
def generate_proposals(
    self,
    context: CrossRepoLearningContext
) -> list[ImprovementProposal]:
    """Generate proposals using runtime ADG patterns."""
    # Query runtime ADG for execution patterns
    patterns = self._get_runtime_adg_patterns()
    
    # Incorporate into proposal generation
    for pattern in patterns:
        if pattern.get('error_rate', 0) > 0.1:
            # Generate proposal to address high error rate
            proposal = ImprovementProposal(
                target=pattern['component'],
                issue=f"High error rate: {pattern['error_rate']:.2%}",
                evidence=f"Runtime ADG pattern: {pattern['pattern_id']}",
            )
            self._proposals.append(proposal)
    
    return self._proposals
```

**Acceptance Criteria**:
- Intent expansion queries runtime ADG for similar past intents
- Healing decisions influenced by historical healing success rates
- Routing decisions consider historical route latency
- Meta-learning proposals reference runtime ADG patterns

---

## Rules

1. **Never modify existing test behavior** — add new tests for new functionality
2. **Maintain L0-L6 layer boundaries** — no upward imports from lower layers
3. **All new code must have lifecycle_trace_contract emissions** — document graph edges
4. **Prometheus metrics must have cardinalities < 100** — avoid unbounded label values
5. **Runtime ADG queries must complete within 100ms p95** — add query timeout enforcement
6. **Eval-to-ML wiring must be idempotent** — duplicate spans should not double-count

---

## Success Criteria

| Wave | Metric | Target | Verification |
|------|--------|--------|--------------|
| Wave 0 | Prometheus `/metrics` endpoint | Returns non-empty response | `curl localhost:8000/metrics` |
| Wave 0 | Metric definitions | 10+ counters/histograms | `grep -c "^# TYPE"` on /metrics |
| Wave 1 | E2E trace tests | 16/16 pass | `pytest tests/e2e/test_runtime_adg_e2e.py` |
| Wave 1 | apps_* span coverage | 100% of public methods | Code review of decorated methods |
| Wave 2 | Snapshot edge types | 13 types present | `snapshot.validate()` assertion |
| Wave 3 | Query latency | <100ms p95 | Benchmark test output |
| Wave 3 | Persistence | Survives restart | Stop/start verification |
| Wave 4 | Dashboards | 5+ operational | Grafana UI screenshot |
| Wave 5 | Eval span consumption | <30s latency | ML bus log timestamps |
| Wave 6 | ADG-influenced decisions | 5+ integration points | Agent decision logs |

---

## Implementation Commands

```bash
# Pre-flight: Verify ADG is hot
python tools/adg/adg_redis_ingest.py --force

# Wave 0: Prometheus instrumentation
pip install prometheus_client>=0.19.0
python -c "from agentic_core.L6_observability import start_metrics_server; start_metrics_server(8000)"
curl -s localhost:8000/metrics | grep agentic_workflow

# Wave 1: Trace coverage verification
pytest tests/e2e/test_runtime_adg_e2e.py -v --tb=short

# Wave 2: Snapshot validation
python -c "
from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
from system_learning.runtime_adg.snapshot import create_runtime_adg_snapshot
# ... validation logic
"

# Wave 3: Query latency benchmark
pytest tests/performance/test_runtime_adg_query_performance.py -v

# Wave 4: Dashboard verification
kubectl port-forward svc/grafana 3000:3000 -n agentic-workflow
open http://localhost:3000/d/l0-l6-layer-health

# Wave 5: Eval wiring test
pytest tests/e2e/test_eval_meta_learning_wiring_e2e.py -v

# Wave 6: Runtime consumption verification
python -c "
from agentic_core.L1_cognition.engines.intent_expansion import IntentExpander
expander = IntentExpander()
# Verify ADG query in expand_intent
"
```

---

## Rollback Strategy

If critical failure occurs:

1. **Wave 0 failure**: Remove `prometheus_client` from requirements; delete `agentic_core/L6_observability/metrics/` and `engines/metrics_server.py`

2. **Wave 1 failure**: Remove `@trace_*` decorators from all apps_* files; revert to lifecycle_trace_contract emissions only

3. **Wave 2 failure**: Revert materializer to parent_child + temporal_sequence only; comment out semantic edge extraction

4. **Wave 3 failure**: Disable query client imports in agent files; persistence continues working

5. **Wave 4 failure**: Revert ConfigMap to previous version; dashboards return to static state

6. **Wave 5 failure**: Disable eval span emission in EvalOrchestrator; return to in-memory metrics only

7. **Wave 6 failure**: Comment out ADG query calls in intent_expansion, healing_strategy, routing_engine; fall back to static heuristics

---

## Evidence Artifacts

| Wave | Required Artifacts | Location |
|------|-------------------|----------|
| Wave 0 | Prometheus /metrics output | `docs/evidence/prometheus_metrics_output.txt` |
| Wave 0 | Server startup log | `docs/evidence/metrics_server_startup.log` |
| Wave 1 | E2E test output | `docs/evidence/test_runtime_adg_e2e_output.txt` |
| Wave 1 | Span JSON sample | `docs/evidence/sample_span.json` |
| Wave 2 | Snapshot validation report | `docs/evidence/snapshot_validation_report.json` |
| Wave 3 | Query latency benchmark | `docs/evidence/query_latency_benchmark.json` |
| Wave 3 | Persistence test log | `docs/evidence/persistence_test.log` |
| Wave 4 | Grafana screenshots | `docs/evidence/grafana_dashboards.png` |
| Wave 5 | ML bus consumption log | `docs/evidence/ml_bus_consumption.log` |
| Wave 6 | ADG-influenced decision logs | `docs/evidence/adg_influenced_decisions.log` |
