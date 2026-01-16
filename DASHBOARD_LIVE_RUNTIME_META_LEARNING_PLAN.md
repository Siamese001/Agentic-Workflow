# Dashboard Live Runtime Meta-Learning Implementation Plan

## Executive Summary

Design and implement a comprehensive Live Runtime dashboard tab that visualizes meta-learning processes as `canon_validator_agentic_v2_thin.py` executes. The dashboard will show real-time agent execution flow, Redis caching operations, Pinecone vector storage, and meta-learning pattern extraction.

---

## Current State Analysis

### Existing Infrastructure

**Runtime State Tracking** (`canon_validator_agentic_v2_thin.py:65-93`)
- `runtime_state.json` file for dashboard polling
- Basic state tracking: status, current_agent, events
- Event logging with timestamps

**Meta-Learning Agent** (`agentic_core/L1_cognition/learning/MetaLearningAgent.py`)
- Experience replay buffer (capacity: 1000)
- Strategy weight optimization (CoT, ToT, ReAct, Reflection)
- Pattern extraction from experiences
- Reward-based learning

**Redis Integration** (`agentic_core/utils/core_extensions/redis.py`)
- `SovereignRedisClient` with audit logging
- Connection pooling with fallback
- Cache operations tracking

**Pinecone Integration** (inferred from grep results)
- Vector storage for semantic memory
- Experience embeddings
- Pattern clustering

---

## Phase 1: Data Collection Infrastructure

### 1.1 Enhanced Runtime State Schema

**File**: `canon_validator_agentic_v2_thin.py`

**Objective**: Expand `runtime_state.json` to capture meta-learning metrics

**Implementation Steps**:

1. **Extend Runtime State Structure**
   ```python
   _runtime_state = {
       "status": "idle",  # idle | running | completed | error
       "start_time": None,
       "end_time": None,
       "current_agent": None,
       "current_layer": None,
       "agents_order": [],
       "total_agents": 0,
       "completed_agents": [],
       "events": [],
       
       # NEW: Meta-Learning Metrics
       "meta_learning": {
           "enabled": False,
           "total_experiences": 0,
           "patterns_extracted": 0,
           "strategy_weights": {
               "cot": 1.0,
               "tot": 1.0,
               "react": 1.0,
               "reflection": 1.0
           },
           "recent_experiences": [],  # Last 10 experiences
           "pattern_history": []  # Pattern extraction timeline
       },
       
       # NEW: Redis Metrics
       "redis": {
           "connected": False,
           "operations": {
               "get": 0,
               "set": 0,
               "delete": 0,
               "total": 0
           },
           "cache_hits": 0,
           "cache_misses": 0,
           "hit_rate": 0.0,
           "recent_operations": []  # Last 20 operations
       },
       
       # NEW: Pinecone Metrics
       "pinecone": {
           "connected": False,
           "operations": {
               "upsert": 0,
               "query": 0,
               "delete": 0,
               "total": 0
           },
           "vectors_stored": 0,
           "avg_similarity": 0.0,
           "recent_queries": []  # Last 10 queries with results
       },
       
       # NEW: Agent Execution Timeline
       "execution_timeline": []  # [{agent, start, end, duration, success}]
   }
   ```

2. **Add Instrumentation Hooks**
   - Hook into `MetaLearningAgent.store_experience()` to capture experiences
   - Hook into `SovereignRedisClient` operations to track cache activity
   - Hook into Pinecone operations to track vector storage
   - Add timing instrumentation for each agent execution

3. **Create Update Functions**
   ```python
   def _update_meta_learning_state(experience: Experience):
       """Update runtime state with new meta-learning experience."""
       
   def _update_redis_state(operation: str, key: str, success: bool):
       """Update runtime state with Redis operation."""
       
   def _update_pinecone_state(operation: str, vector_id: str, metadata: dict):
       """Update runtime state with Pinecone operation."""
       
   def _update_agent_execution(agent_name: str, layer: str, duration: float, success: bool):
       """Update execution timeline with agent completion."""
   ```

### 1.2 Meta-Learning Agent Instrumentation

**File**: `agentic_core/L1_cognition/learning/MetaLearningAgent.py`

**Objective**: Add telemetry hooks for dashboard observability

**Implementation Steps**:

1. **Add Telemetry Callback System**
   ```python
   class MetaLearningAgent(MCPHardenedMixin, HealerMixin):
       def __init__(self, replay_capacity: int = 1000, telemetry_callback=None):
           # ... existing init ...
           self.telemetry_callback = telemetry_callback
   ```

2. **Instrument Key Methods**
   ```python
   def store_experience(self, state, thought_type, outcome, reward):
       exp = Experience(...)
       self.replay_buffer.append(exp)
       self.total_experiences += 1
       
       # NEW: Telemetry hook
       if self.telemetry_callback:
           self.telemetry_callback('experience_stored', {
               'experience_id': exp_id,
               'thought_type': thought_type,
               'reward': reward,
               'buffer_size': len(self.replay_buffer)
           })
       
       return exp_id
   
   def extract_patterns(self):
       patterns = [...]  # Pattern extraction logic
       self.patterns_extracted += 1
       
       # NEW: Telemetry hook
       if self.telemetry_callback:
           self.telemetry_callback('patterns_extracted', {
               'patterns': patterns,
               'total_patterns': self.patterns_extracted
           })
       
       return patterns
   ```

3. **Add Real-Time Statistics Method**
   ```python
   def get_live_statistics(self) -> Dict[str, Any]:
       """Get current meta-learning statistics for dashboard."""
       return {
           'total_experiences': self.total_experiences,
           'buffer_size': len(self.replay_buffer),
           'buffer_capacity': self.replay_capacity,
           'patterns_extracted': self.patterns_extracted,
           'strategy_weights': self.strategy_weights,
           'recent_experiences': [
               {
                   'thought_type': exp.thought_type,
                   'reward': exp.reward,
                   'timestamp': exp.timestamp.isoformat()
               }
               for exp in self.replay_buffer[-10:]
           ]
       }
   ```

### 1.3 Redis Client Instrumentation

**File**: `agentic_core/utils/core_extensions/redis.py`

**Objective**: Track all cache operations for dashboard visualization

**Implementation Steps**:

1. **Add Operation Tracking**
   ```python
   class SovereignRedisClient(MCPHardenedMixin, HealerMixin):
       def __init__(self, url=None, telemetry_callback=None):
           # ... existing init ...
           self.telemetry_callback = telemetry_callback
           self.operation_stats = {
               'get': 0, 'set': 0, 'delete': 0,
               'hits': 0, 'misses': 0
           }
   ```

2. **Instrument Cache Operations**
   ```python
   def get(self, key: str) -> Optional[Any]:
       """Get value with telemetry."""
       result = self._get_client().get(key)
       
       # Track hit/miss
       if result is not None:
           self.operation_stats['hits'] += 1
       else:
           self.operation_stats['misses'] += 1
       
       self.operation_stats['get'] += 1
       
       # Telemetry hook
       if self.telemetry_callback:
           self.telemetry_callback('redis_get', {
               'key': key,
               'hit': result is not None,
               'timestamp': datetime.now().isoformat()
           })
       
       return result
   ```

3. **Add Statistics Method**
   ```python
   def get_statistics(self) -> Dict[str, Any]:
       """Get Redis operation statistics."""
       total_ops = sum(self.operation_stats.values())
       hit_rate = (self.operation_stats['hits'] / total_ops 
                   if total_ops > 0 else 0.0)
       
       return {
           'connected': not self._use_fallback,
           'operations': self.operation_stats.copy(),
           'hit_rate': hit_rate,
           'total_operations': total_ops
       }
   ```

### 1.4 Pinecone Client Instrumentation

**File**: Create `agentic_core/L4_state/vector_stores/pinecone_telemetry.py`

**Objective**: Wrap Pinecone operations with telemetry

**Implementation Steps**:

1. **Create Telemetry Wrapper**
   ```python
   class PineconeTelemetryWrapper:
       """Wraps Pinecone client with telemetry hooks."""
       
       def __init__(self, pinecone_client, telemetry_callback=None):
           self.client = pinecone_client
           self.telemetry_callback = telemetry_callback
           self.stats = {
               'upsert': 0,
               'query': 0,
               'delete': 0,
               'vectors_stored': 0
           }
       
       def upsert(self, vectors, namespace=''):
           """Upsert with telemetry."""
           result = self.client.upsert(vectors, namespace=namespace)
           
           self.stats['upsert'] += 1
           self.stats['vectors_stored'] += len(vectors)
           
           if self.telemetry_callback:
               self.telemetry_callback('pinecone_upsert', {
                   'count': len(vectors),
                   'namespace': namespace,
                   'timestamp': datetime.now().isoformat()
               })
           
           return result
       
       def query(self, vector, top_k=10, namespace=''):
           """Query with telemetry."""
           result = self.client.query(vector, top_k=top_k, namespace=namespace)
           
           self.stats['query'] += 1
           
           if self.telemetry_callback:
               self.telemetry_callback('pinecone_query', {
                   'top_k': top_k,
                   'results_count': len(result.matches),
                   'avg_score': sum(m.score for m in result.matches) / len(result.matches),
                   'namespace': namespace,
                   'timestamp': datetime.now().isoformat()
               })
           
           return result
   ```

---

## Phase 2: Backend API Endpoints

### 2.1 Real-Time State API

**File**: Create `agentic_core/L6_observability/api/runtime_api.py`

**Objective**: Serve runtime state to dashboard via HTTP

**Implementation Steps**:

1. **Create FastAPI Server**
   ```python
   from fastapi import FastAPI
   from fastapi.middleware.cors import CORSMiddleware
   import json
   from pathlib import Path
   
   app = FastAPI(title="Dashboard Runtime API")
   
   # Enable CORS for dashboard
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_methods=["*"],
       allow_headers=["*"]
   )
   
   RUNTIME_STATE_FILE = Path("runtime_state.json")
   ```

2. **Define API Endpoints**
   ```python
   @app.get("/api/runtime/state")
   async def get_runtime_state():
       """Get current runtime state."""
       if RUNTIME_STATE_FILE.exists():
           return json.loads(RUNTIME_STATE_FILE.read_text())
       return {"status": "idle"}
   
   @app.get("/api/meta-learning/activity")
   async def get_meta_learning_activity():
       """Get meta-learning specific metrics."""
       state = json.loads(RUNTIME_STATE_FILE.read_text())
       return state.get('meta_learning', {})
   
   @app.get("/api/redis/stats")
   async def get_redis_stats():
       """Get Redis operation statistics."""
       state = json.loads(RUNTIME_STATE_FILE.read_text())
       return state.get('redis', {})
   
   @app.get("/api/pinecone/stats")
   async def get_pinecone_stats():
       """Get Pinecone operation statistics."""
       state = json.loads(RUNTIME_STATE_FILE.read_text())
       return state.get('pinecone', {})
   
   @app.get("/api/execution/timeline")
   async def get_execution_timeline():
       """Get agent execution timeline."""
       state = json.loads(RUNTIME_STATE_FILE.read_text())
       return state.get('execution_timeline', [])
   ```

3. **Add Server Startup Script**
   ```python
   # scripts/start_runtime_api.py
   import uvicorn
   
   if __name__ == "__main__":
       uvicorn.run(
           "agentic_core.L6_observability.api.runtime_api:app",
           host="0.0.0.0",
           port=8081,
           reload=True
       )
   ```

---

## Phase 3: Dashboard Frontend Components

### 3.1 Meta-Learning Visualization Panel

**File**: `agentic_core/L6_observability/dashboards/js/components/meta-learning-panel.js`

**Objective**: Real-time visualization of meta-learning activity

**Implementation Steps**:

1. **Create Experience Stream Component**
   ```javascript
   class ExperienceStream {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
           this.experiences = [];
           this.maxDisplay = 50;
       }
       
       addExperience(exp) {
           this.experiences.unshift(exp);
           if (this.experiences.length > this.maxDisplay) {
               this.experiences.pop();
           }
           this.render();
       }
       
       render() {
           const html = this.experiences.map(exp => `
               <div class="experience-item ${this.getRewardClass(exp.reward)}">
                   <span class="exp-type">${exp.thought_type}</span>
                   <span class="exp-reward">Reward: ${exp.reward.toFixed(2)}</span>
                   <span class="exp-time">${this.formatTime(exp.timestamp)}</span>
               </div>
           `).join('');
           
           this.container.innerHTML = html;
       }
       
       getRewardClass(reward) {
           if (reward > 0.7) return 'reward-high';
           if (reward > 0.3) return 'reward-medium';
           return 'reward-low';
       }
   }
   ```

2. **Create Strategy Weights Visualization**
   ```javascript
   class StrategyWeightsChart {
       constructor(canvasId) {
           this.ctx = document.getElementById(canvasId).getContext('2d');
           this.chart = new Chart(this.ctx, {
               type: 'bar',
               data: {
                   labels: ['CoT', 'ToT', 'ReAct', 'Reflection'],
                   datasets: [{
                       label: 'Strategy Weight',
                       data: [1.0, 1.0, 1.0, 1.0],
                       backgroundColor: [
                           'rgba(59, 130, 246, 0.8)',
                           'rgba(16, 185, 129, 0.8)',
                           'rgba(245, 158, 11, 0.8)',
                           'rgba(139, 92, 246, 0.8)'
                       ]
                   }]
               },
               options: {
                   responsive: true,
                   scales: {
                       y: { beginAtZero: true, max: 2.0 }
                   }
               }
           });
       }
       
       update(weights) {
           this.chart.data.datasets[0].data = [
               weights.cot,
               weights.tot,
               weights.react,
               weights.reflection
           ];
           this.chart.update();
       }
   }
   ```

3. **Create Pattern Extraction Timeline**
   ```javascript
   class PatternTimeline {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
           this.patterns = [];
       }
       
       addPattern(pattern) {
           this.patterns.push(pattern);
           this.render();
       }
       
       render() {
           const html = `
               <div class="timeline">
                   ${this.patterns.map((p, i) => `
                       <div class="timeline-item">
                           <div class="timeline-marker">${i + 1}</div>
                           <div class="timeline-content">
                               <strong>${p.type}</strong>
                               <span>Threshold: ${p.threshold}</span>
                               <span class="time">${this.formatTime(p.timestamp)}</span>
                           </div>
                       </div>
                   `).join('')}
               </div>
           `;
           this.container.innerHTML = html;
       }
   }
   ```

### 3.2 Redis Activity Monitor

**File**: `agentic_core/L6_observability/dashboards/js/components/redis-monitor.js`

**Objective**: Visualize Redis cache operations

**Implementation Steps**:

1. **Create Operation Counter**
   ```javascript
   class RedisOperationCounter {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
       }
       
       update(stats) {
           const hitRate = (stats.hit_rate * 100).toFixed(1);
           const html = `
               <div class="redis-stats-grid">
                   <div class="stat-box">
                       <div class="stat-label">GET Operations</div>
                       <div class="stat-value">${stats.operations.get}</div>
                   </div>
                   <div class="stat-box">
                       <div class="stat-label">SET Operations</div>
                       <div class="stat-value">${stats.operations.set}</div>
                   </div>
                   <div class="stat-box">
                       <div class="stat-label">Cache Hit Rate</div>
                       <div class="stat-value ${this.getHitRateClass(hitRate)}">${hitRate}%</div>
                   </div>
                   <div class="stat-box">
                       <div class="stat-label">Total Operations</div>
                       <div class="stat-value">${stats.operations.total}</div>
                   </div>
               </div>
           `;
           this.container.innerHTML = html;
       }
       
       getHitRateClass(rate) {
           if (rate > 80) return 'hit-rate-excellent';
           if (rate > 60) return 'hit-rate-good';
           return 'hit-rate-poor';
       }
   }
   ```

2. **Create Recent Operations Log**
   ```javascript
   class RedisOperationLog {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
           this.operations = [];
           this.maxDisplay = 20;
       }
       
       addOperation(op) {
           this.operations.unshift(op);
           if (this.operations.length > this.maxDisplay) {
               this.operations.pop();
           }
           this.render();
       }
       
       render() {
           const html = `
               <div class="operation-log">
                   ${this.operations.map(op => `
                       <div class="log-entry ${op.hit ? 'cache-hit' : 'cache-miss'}">
                           <span class="op-type">${op.operation}</span>
                           <span class="op-key">${op.key}</span>
                           <span class="op-result">${op.hit ? '✓ HIT' : '✗ MISS'}</span>
                           <span class="op-time">${this.formatTime(op.timestamp)}</span>
                       </div>
                   `).join('')}
               </div>
           `;
           this.container.innerHTML = html;
       }
   }
   ```

### 3.3 Pinecone Vector Operations Monitor

**File**: `agentic_core/L6_observability/dashboards/js/components/pinecone-monitor.js`

**Objective**: Visualize vector storage and similarity search

**Implementation Steps**:

1. **Create Vector Operations Dashboard**
   ```javascript
   class PineconeOperationsDashboard {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
       }
       
       update(stats) {
           const html = `
               <div class="pinecone-stats-grid">
                   <div class="stat-box">
                       <div class="stat-label">Vectors Stored</div>
                       <div class="stat-value">${stats.vectors_stored}</div>
                   </div>
                   <div class="stat-box">
                       <div class="stat-label">Upsert Operations</div>
                       <div class="stat-value">${stats.operations.upsert}</div>
                   </div>
                   <div class="stat-box">
                       <div class="stat-label">Query Operations</div>
                       <div class="stat-value">${stats.operations.query}</div>
                   </div>
                   <div class="stat-box">
                       <div class="stat-label">Avg Similarity</div>
                       <div class="stat-value">${(stats.avg_similarity * 100).toFixed(1)}%</div>
                   </div>
               </div>
           `;
           this.container.innerHTML = html;
       }
   }
   ```

2. **Create Query Results Visualizer**
   ```javascript
   class QueryResultsVisualizer {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
       }
       
       displayResults(queries) {
           const html = `
               <div class="query-results">
                   ${queries.map(q => `
                       <div class="query-item">
                           <div class="query-header">
                               <strong>Query</strong>
                               <span class="query-time">${this.formatTime(q.timestamp)}</span>
                           </div>
                           <div class="query-results-list">
                               ${q.results.map((r, i) => `
                                   <div class="result-item">
                                       <span class="result-rank">#${i + 1}</span>
                                       <span class="result-id">${r.id}</span>
                                       <span class="result-score">${(r.score * 100).toFixed(1)}%</span>
                                   </div>
                               `).join('')}
                           </div>
                       </div>
                   `).join('')}
               </div>
           `;
           this.container.innerHTML = html;
       }
   }
   ```

### 3.4 Agent Execution Flow Diagram

**File**: `agentic_core/L6_observability/dashboards/js/components/execution-flow.js`

**Objective**: Visualize agent execution sequence and timing

**Implementation Steps**:

1. **Create Timeline Visualization**
   ```javascript
   class AgentExecutionTimeline {
       constructor(canvasId) {
           this.canvas = document.getElementById(canvasId);
           this.ctx = this.canvas.getContext('2d');
           this.timeline = [];
       }
       
       addExecution(agent, layer, start, end, success) {
           this.timeline.push({
               agent, layer, start, end,
               duration: end - start,
               success
           });
           this.render();
       }
       
       render() {
           // Clear canvas
           this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
           
           // Draw timeline bars
           const maxDuration = Math.max(...this.timeline.map(t => t.duration));
           const barHeight = 30;
           const spacing = 10;
           
           this.timeline.forEach((exec, i) => {
               const y = i * (barHeight + spacing);
               const width = (exec.duration / maxDuration) * (this.canvas.width - 200);
               
               // Draw bar
               this.ctx.fillStyle = exec.success ? '#10b981' : '#ef4444';
               this.ctx.fillRect(150, y, width, barHeight);
               
               // Draw label
               this.ctx.fillStyle = '#000';
               this.ctx.font = '12px sans-serif';
               this.ctx.fillText(exec.agent, 10, y + 20);
               
               // Draw duration
               this.ctx.fillText(`${exec.duration.toFixed(2)}s`, 160 + width, y + 20);
           });
       }
   }
   ```

2. **Create Layer Flow Diagram**
   ```javascript
   class LayerFlowDiagram {
       constructor(containerId) {
           this.container = document.getElementById(containerId);
           this.layers = ['L5', 'L4', 'L3', 'L2', 'L1', 'L0'];
       }
       
       update(currentLayer, completedLayers) {
           const html = `
               <div class="layer-flow">
                   ${this.layers.map(layer => `
                       <div class="layer-node ${this.getLayerClass(layer, currentLayer, completedLayers)}">
                           <div class="layer-name">${layer}</div>
                           <div class="layer-status">${this.getLayerStatus(layer, currentLayer, completedLayers)}</div>
                       </div>
                   `).join('<div class="layer-arrow">→</div>')}
               </div>
           `;
           this.container.innerHTML = html;
       }
       
       getLayerClass(layer, current, completed) {
           if (completed.includes(layer)) return 'layer-completed';
           if (layer === current) return 'layer-active';
           return 'layer-pending';
       }
   }
   ```

---

## Phase 4: Real-Time Data Polling

### 4.1 Dashboard Polling Controller

**File**: `agentic_core/L6_observability/dashboards/js/controllers/meta-learning-controller.js`

**Objective**: Poll API endpoints and update UI components

**Implementation Steps**:

1. **Create Polling Manager**
   ```javascript
   class MetaLearningController {
       constructor() {
           this.pollingInterval = 1000; // 1 second
           this.components = {
               experienceStream: new ExperienceStream('experience-stream'),
               strategyWeights: new StrategyWeightsChart('strategy-chart'),
               patternTimeline: new PatternTimeline('pattern-timeline'),
               redisMonitor: new RedisOperationCounter('redis-stats'),
               redisLog: new RedisOperationLog('redis-log'),
               pineconeMonitor: new PineconeOperationsDashboard('pinecone-stats'),
               executionTimeline: new AgentExecutionTimeline('execution-canvas')
           };
           
           this.lastExperienceCount = 0;
           this.lastRedisOpCount = 0;
           this.lastPineconeOpCount = 0;
       }
       
       async start() {
           this.intervalId = setInterval(() => this.poll(), this.pollingInterval);
       }
       
       stop() {
           if (this.intervalId) {
               clearInterval(this.intervalId);
           }
       }
       
       async poll() {
           try {
               // Fetch all data in parallel
               const [metaData, redisData, pineconeData, timelineData] = await Promise.all([
                   fetch('http://localhost:8081/api/meta-learning/activity').then(r => r.json()),
                   fetch('http://localhost:8081/api/redis/stats').then(r => r.json()),
                   fetch('http://localhost:8081/api/pinecone/stats').then(r => r.json()),
                   fetch('http://localhost:8081/api/execution/timeline').then(r => r.json())
               ]);
               
               // Update meta-learning components
               this.updateMetaLearning(metaData);
               
               // Update Redis components
               this.updateRedis(redisData);
               
               // Update Pinecone components
               this.updatePinecone(pineconeData);
               
               // Update execution timeline
               this.updateTimeline(timelineData);
               
           } catch (error) {
               console.error('Polling error:', error);
           }
       }
       
       updateMetaLearning(data) {
           // Update strategy weights
           if (data.strategy_weights) {
               this.components.strategyWeights.update(data.strategy_weights);
           }
           
           // Add new experiences
           if (data.recent_experiences) {
               const newExperiences = data.recent_experiences.slice(this.lastExperienceCount);
               newExperiences.forEach(exp => {
                   this.components.experienceStream.addExperience(exp);
               });
               this.lastExperienceCount = data.total_experiences;
           }
           
           // Add new patterns
           if (data.pattern_history) {
               data.pattern_history.forEach(pattern => {
                   this.components.patternTimeline.addPattern(pattern);
               });
           }
       }
       
       updateRedis(data) {
           this.components.redisMonitor.update(data);
           
           // Add new operations to log
           if (data.recent_operations) {
               const newOps = data.recent_operations.slice(this.lastRedisOpCount);
               newOps.forEach(op => {
                   this.components.redisLog.addOperation(op);
               });
               this.lastRedisOpCount = data.operations.total;
           }
       }
       
       updatePinecone(data) {
           this.components.pineconeMonitor.update(data);
       }
       
       updateTimeline(data) {
           // Update execution timeline with new completions
           data.forEach(exec => {
               this.components.executionTimeline.addExecution(
                   exec.agent,
                   exec.layer,
                   exec.start,
                   exec.end,
                   exec.success
               );
           });
       }
   }
   ```

2. **Initialize on Page Load**
   ```javascript
   // In main.js
   document.addEventListener('DOMContentLoaded', () => {
       if (window.location.hash === '#runtime') {
           const controller = new MetaLearningController();
           controller.start();
           
           // Stop polling when leaving tab
           window.addEventListener('hashchange', () => {
               if (window.location.hash !== '#runtime') {
                   controller.stop();
               }
           });
       }
   });
   ```

---

## Phase 5: UI Layout and Styling

### 5.1 Live Runtime Tab Layout

**File**: `agentic_core/L6_observability/dashboards/autonomy_dashboard.html`

**Objective**: Design comprehensive meta-learning dashboard layout

**Implementation Steps**:

1. **Add HTML Structure to Runtime Tab**
   ```html
   <div id="runtime-content" class="tab-content">
       <!-- Meta-Learning Section -->
       <div class="meta-learning-section">
           <h2>🧠 Meta-Learning Activity</h2>
           
           <div class="meta-grid">
               <!-- Strategy Weights Chart -->
               <div class="chart-card">
                   <h3>Strategy Weights</h3>
                   <canvas id="strategy-chart"></canvas>
               </div>
               
               <!-- Experience Stream -->
               <div class="chart-card">
                   <h3>Experience Stream (Last 50)</h3>
                   <div id="experience-stream" class="scrollable-list"></div>
               </div>
               
               <!-- Pattern Timeline -->
               <div class="chart-card full-width">
                   <h3>Pattern Extraction Timeline</h3>
                   <div id="pattern-timeline"></div>
               </div>
           </div>
       </div>
       
       <!-- Redis Activity Section -->
       <div class="redis-section">
           <h2>💾 Redis Cache Activity</h2>
           
           <div class="redis-grid">
               <!-- Stats Dashboard -->
               <div class="chart-card">
                   <h3>Operation Statistics</h3>
                   <div id="redis-stats"></div>
               </div>
               
               <!-- Recent Operations Log -->
               <div class="chart-card">
                   <h3>Recent Operations (Last 20)</h3>
                   <div id="redis-log" class="scrollable-list"></div>
               </div>
           </div>
       </div>
       
       <!-- Pinecone Activity Section -->
       <div class="pinecone-section">
           <h2>🔍 Pinecone Vector Operations</h2>
           
           <div class="pinecone-grid">
               <!-- Stats Dashboard -->
               <div class="chart-card">
                   <h3>Vector Storage Statistics</h3>
                   <div id="pinecone-stats"></div>
               </div>
               
               <!-- Query Results -->
               <div class="chart-card">
                   <h3>Recent Queries</h3>
                   <div id="pinecone-queries" class="scrollable-list"></div>
               </div>
           </div>
       </div>
       
       <!-- Agent Execution Flow Section -->
       <div class="execution-section">
           <h2>⚡ Agent Execution Flow</h2>
           
           <div class="execution-grid">
               <!-- Timeline Canvas -->
               <div class="chart-card full-width">
                   <h3>Execution Timeline</h3>
                   <canvas id="execution-canvas" width="1200" height="600"></canvas>
               </div>
               
               <!-- Layer Flow Diagram -->
               <div class="chart-card">
                   <h3>Layer Progression</h3>
                   <div id="layer-flow"></div>
               </div>
           </div>
       </div>
   </div>
   ```

2. **Add CSS Styling**
   ```css
   /* Meta-Learning Styles */
   .meta-learning-section {
       margin-bottom: 40px;
   }
   
   .meta-grid {
       display: grid;
       grid-template-columns: 1fr 1fr;
       gap: 20px;
   }
   
   .full-width {
       grid-column: 1 / -1;
   }
   
   .experience-item {
       padding: 8px 12px;
       margin-bottom: 8px;
       border-radius: 4px;
       display: flex;
       justify-content: space-between;
       align-items: center;
   }
   
   .reward-high {
       background: #d1fae5;
       border-left: 4px solid #10b981;
   }
   
   .reward-medium {
       background: #fef3c7;
       border-left: 4px solid #f59e0b;
   }
   
   .reward-low {
       background: #fee2e2;
       border-left: 4px solid #ef4444;
   }
   
   /* Redis Styles */
   .redis-stats-grid {
       display: grid;
       grid-template-columns: repeat(2, 1fr);
       gap: 15px;
   }
   
   .stat-box {
       padding: 15px;
       background: #f9fafb;
       border-radius: 8px;
       text-align: center;
   }
   
   .stat-label {
       font-size: 0.9em;
       color: #6b7280;
       margin-bottom: 8px;
   }
   
   .stat-value {
       font-size: 2em;
       font-weight: bold;
       color: #111827;
   }
   
   .cache-hit {
       background: #d1fae5;
   }
   
   .cache-miss {
       background: #fee2e2;
   }
   
   /* Pinecone Styles */
   .pinecone-stats-grid {
       display: grid;
       grid-template-columns: repeat(2, 1fr);
       gap: 15px;
   }
   
   /* Execution Flow Styles */
   .layer-flow {
       display: flex;
       align-items: center;
       justify-content: space-around;
       padding: 20px;
   }
   
   .layer-node {
       padding: 15px 25px;
       border-radius: 8px;
       text-align: center;
       min-width: 100px;
   }
   
   .layer-completed {
       background: #10b981;
       color: white;
   }
   
   .layer-active {
       background: #3b82f6;
       color: white;
       animation: pulse 2s infinite;
   }
   
   .layer-pending {
       background: #e5e7eb;
       color: #6b7280;
   }
   
   @keyframes pulse {
       0%, 100% { opacity: 1; }
       50% { opacity: 0.7; }
   }
   
   .scrollable-list {
       max-height: 400px;
       overflow-y: auto;
   }
   ```

---

## Phase 6: Integration and Testing

### 6.1 Integration Checklist

1. **Backend Integration**
   - [ ] Instrument `canon_validator_agentic_v2_thin.py` with telemetry hooks
   - [ ] Add telemetry callbacks to `MetaLearningAgent`
   - [ ] Add telemetry callbacks to `SovereignRedisClient`
   - [ ] Create Pinecone telemetry wrapper
   - [ ] Implement FastAPI runtime API server
   - [ ] Test API endpoints return correct data

2. **Frontend Integration**
   - [ ] Add all JavaScript components to dashboard
   - [ ] Create `meta-learning-controller.js` polling manager
   - [ ] Update `autonomy_dashboard.html` with new layout
   - [ ] Add CSS styling for all components
   - [ ] Test component rendering with mock data

3. **End-to-End Testing**
   - [ ] Run `canon_validator_agentic_v2_thin.py --heal`
   - [ ] Verify `runtime_state.json` updates correctly
   - [ ] Verify API endpoints serve live data
   - [ ] Verify dashboard polls and updates in real-time
   - [ ] Test all visualizations display correctly

### 6.2 Testing Scenarios

**Scenario 1: Meta-Learning Experience Capture**
```bash
# Terminal 1: Start API server
python scripts/start_runtime_api.py

# Terminal 2: Run canon validator
python canon_validator_agentic_v2_thin.py --heal --execute

# Terminal 3: Monitor dashboard
# Open http://localhost:8765/autonomy_dashboard.html#runtime
# Verify experience stream updates
# Verify strategy weights change over time
```

**Scenario 2: Redis Cache Activity**
```bash
# Verify Redis operations appear in dashboard
# Check cache hit rate updates
# Verify recent operations log shows GET/SET operations
```

**Scenario 3: Pinecone Vector Operations**
```bash
# Verify vector upsert operations appear
# Check query results display with similarity scores
# Verify vectors stored counter increments
```

**Scenario 4: Agent Execution Flow**
```bash
# Verify execution timeline shows agent sequence
# Check layer flow diagram updates as agents complete
# Verify timing information is accurate
```

---

## Phase 7: Documentation and Deployment

### 7.1 User Documentation

**File**: Create `docs/DASHBOARD_META_LEARNING_GUIDE.md`

**Content**:
- Overview of meta-learning visualization
- How to interpret experience stream
- Understanding strategy weights
- Redis cache optimization tips
- Pinecone vector storage insights
- Troubleshooting common issues

### 7.2 Developer Documentation

**File**: Create `docs/META_LEARNING_TELEMETRY_API.md`

**Content**:
- Telemetry callback interface specification
- How to add new telemetry hooks
- API endpoint documentation
- Data schema definitions
- Extension points for custom metrics

### 7.3 Deployment Steps

1. **Install Dependencies**
   ```bash
   pip install fastapi uvicorn
   ```

2. **Start API Server**
   ```bash
   python scripts/start_runtime_api.py
   ```

3. **Start Dashboard Server**
   ```bash
   python -m http.server 8765 --directory agentic_core/L6_observability/dashboards
   ```

4. **Access Dashboard**
   ```
   http://localhost:8765/autonomy_dashboard.html#runtime
   ```

---

## Success Metrics

### Functional Metrics
- ✅ Real-time experience stream updates (< 1s latency)
- ✅ Strategy weights visualization accuracy
- ✅ Redis operation tracking (100% coverage)
- ✅ Pinecone query visualization
- ✅ Agent execution timeline accuracy

### Performance Metrics
- API response time < 50ms
- Dashboard polling overhead < 5% CPU
- Memory footprint < 100MB
- Support 1000+ experiences in buffer

### User Experience Metrics
- Dashboard loads in < 2 seconds
- Smooth animations (60 FPS)
- Intuitive navigation
- Clear data presentation

---

## Future Enhancements

### Phase 8: Advanced Analytics
- Pattern clustering visualization
- Experience replay analysis
- Strategy optimization recommendations
- Anomaly detection in meta-learning

### Phase 9: Interactive Controls
- Manual strategy weight adjustment
- Experience filtering and search
- Export data to CSV/JSON
- Playback historical runs

### Phase 10: Multi-Agent Coordination
- Cross-agent learning visualization
- Shared experience pool
- Collaborative pattern extraction
- Distributed meta-learning

---

## Appendix

### A. Data Flow Diagram
```
canon_validator_agentic_v2_thin.py
    ↓ (telemetry callbacks)
MetaLearningAgent / Redis / Pinecone
    ↓ (write)
runtime_state.json
    ↓ (read)
FastAPI Runtime API (port 8081)
    ↓ (HTTP polling)
Dashboard JavaScript (port 8765)
    ↓ (render)
Live Runtime Tab UI
```

### B. Technology Stack
- **Backend**: Python 3.10+, FastAPI, Uvicorn
- **Frontend**: Vanilla JavaScript, Chart.js, Canvas API
- **Data Storage**: JSON files, Redis, Pinecone
- **Communication**: HTTP REST API, Server-Sent Events (future)

### C. File Structure
```
agentic_core/
├── L1_cognition/
│   └── learning/
│       └── MetaLearningAgent.py (instrumented)
├── L4_state/
│   └── vector_stores/
│       └── pinecone_telemetry.py (new)
├── L6_observability/
│   ├── api/
│   │   └── runtime_api.py (new)
│   └── dashboards/
│       ├── autonomy_dashboard.html (updated)
│       ├── js/
│       │   ├── components/
│       │   │   ├── meta-learning-panel.js (new)
│       │   │   ├── redis-monitor.js (new)
│       │   │   ├── pinecone-monitor.js (new)
│       │   │   └── execution-flow.js (new)
│       │   └── controllers/
│       │       └── meta-learning-controller.js (new)
│       └── css/
│           └── meta-learning.css (new)
├── utils/
│   └── core_extensions/
│       └── redis.py (instrumented)
└── canon_validator_agentic_v2_thin.py (instrumented)

scripts/
└── start_runtime_api.py (new)

docs/
├── DASHBOARD_META_LEARNING_GUIDE.md (new)
└── META_LEARNING_TELEMETRY_API.md (new)
```

---

## Implementation Timeline

**Phase 1-2**: 2-3 days (Backend instrumentation + API)
**Phase 3-4**: 3-4 days (Frontend components + polling)
**Phase 5**: 1-2 days (UI layout + styling)
**Phase 6**: 2-3 days (Integration + testing)
**Phase 7**: 1 day (Documentation + deployment)

**Total Estimated Time**: 9-13 days

---

**END OF IMPLEMENTATION PLAN**
