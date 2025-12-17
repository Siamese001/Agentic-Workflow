# WSL2 Optimization Plan - 32GB RAM / 8-Core Allocation
## Agentic Workflow Pipeline Performance Enhancement

**Created:** December 17, 2025  
**WSL2 Resources:** 32GB RAM, 8 CPU Cores  
**Target:** 50-70% pipeline throughput improvement

---

## Executive Summary

With the new 32GB/8-core WSL2 allocation, we can transform the sequential HOP pipeline into a high-throughput multi-agent swarm. This plan outlines architectural changes to leverage parallel processing, in-memory vector stores, and batch optimization.

---

## Current Architecture Analysis

### Identified Pipeline Phases

**Subatomic HOP Architecture** (`scripts/runtime/core/subatomic_hop.py`):
- 5 micro-stages: PRE_CHECK → THINK → ACT → CRITIQUE → COMMIT
- Currently sequential execution with `asyncio` support
- Circuit breaker protection on LLM calls
- Checkpoint-based recovery system

**Titanium RAG Pipeline** (`scripts/runtime/shared/titanium_rag_pipeline.py`):
- Phase 1: Precision Layer (Contextual Compression)
- Phase 2: Reasoning Layer (Query Decomposition & Dynamic Scoring)
- Phase 3: SOTA Layer (Semantic Cache & Cross-Encoder Reranking)
- Currently processes queries sequentially

**Resume Generation Pipeline** (`apps_rg/`):
- Multiple resume engines processing one document at a time
- Vector store lookups per resume
- Embedding generation per section

---

## Concurrency Opportunities

### 1. **Parallel HOP Execution** (High Impact)

**Current State:**
- Single HOP processes one micro-stage at a time
- Multiple HOPs in a DAG execute sequentially

**Optimization:**
```python
# Use asyncio.gather for independent HOPs
async def execute_parallel_hops(hops: List[SubatomicHop]):
    results = await asyncio.gather(
        *[hop.run(**kwargs) for hop in hops],
        return_exceptions=True
    )
    return results
```

**Expected Gain:** 3-4x throughput for independent HOPs

---

### 2. **Batch Embedding Generation** (High Impact)

**Current State:**
- Embeddings generated one-by-one for resume sections
- Network round-trip per embedding call

**Optimization:**
```python
from concurrent.futures import ThreadPoolExecutor

class BatchEmbeddingService:
    def __init__(self, batch_size=32, max_workers=4):
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        # Process in batches of 32 with 4 parallel workers
        batches = [texts[i:i+self.batch_size] 
                   for i in range(0, len(texts), self.batch_size)]
        
        loop = asyncio.get_event_loop()
        results = await asyncio.gather(*[
            loop.run_in_executor(self.executor, self._embed_single_batch, batch)
            for batch in batches
        ])
        return [emb for batch_result in results for emb in batch_result]
```

**Expected Gain:** 5-8x faster embedding generation

---

### 3. **In-Memory Vector Store** (High Impact)

**Current State:**
- Qdrant running in Docker with disk persistence
- Network calls for every vector search

**Optimization:**
```python
import chromadb
from chromadb.config import Settings

class InMemoryVectorCache:
    def __init__(self, max_memory_gb=8):
        # Allocate 8GB for in-memory ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=None,  # In-memory only
            anonymized_telemetry=False
        ))
        self.collections = {}
    
    def load_hot_collections(self, collection_names: List[str]):
        # Pre-load frequently accessed collections into RAM
        for name in collection_names:
            self.collections[name] = self.client.get_or_create_collection(name)
```

**Memory Budget:**
- 8GB for hot vector collections
- 16GB for application runtime
- 8GB for OS/buffers

**Expected Gain:** 10-50x faster vector lookups (no network latency)

---

### 4. **Multi-Process Resume Generation** (Medium Impact)

**Current State:**
- Single process generates resumes sequentially

**Optimization:**
```python
from multiprocessing import Pool, cpu_count

class ResumeSwarm:
    def __init__(self, num_workers=6):
        # Use 6 of 8 cores (leave 2 for system)
        self.pool = Pool(processes=num_workers)
    
    def generate_batch(self, job_descriptions: List[str]) -> List[Resume]:
        # Distribute resume generation across workers
        results = self.pool.map(self._generate_single_resume, job_descriptions)
        return results
    
    def _generate_single_resume(self, job_desc: str) -> Resume:
        # Each worker has its own LLM client and vector store connection
        # Isolated state prevents race conditions
        pass
```

**Expected Gain:** 5-6x throughput for batch resume generation

---

### 5. **Async RAG Pipeline Stages** (Medium Impact)

**Current State:**
- RAG phases execute sequentially: Precision → Reasoning → SOTA

**Optimization:**
```python
class ParallelRAGPipeline:
    async def retrieve_with_parallel_strategies(self, query: str):
        # Run multiple retrieval strategies in parallel
        semantic_task = asyncio.create_task(self._semantic_search(query))
        keyword_task = asyncio.create_task(self._keyword_search(query))
        graphrag_task = asyncio.create_task(self._graphrag_search(query))
        
        # Wait for all strategies
        semantic_docs, keyword_docs, graph_docs = await asyncio.gather(
            semantic_task, keyword_task, graphrag_task
        )
        
        # Merge and rerank
        return self._merge_and_rerank(semantic_docs, keyword_docs, graph_docs)
```

**Expected Gain:** 2-3x faster retrieval with parallel strategies

---

## Memory Optimization Strategy

### Vector Store Memory Allocation

**Hot Data (8GB in RAM):**
- Resume section embeddings (most recent 10K resumes)
- Job description embeddings (most recent 5K jobs)
- Skill taxonomy vectors
- Company intelligence vectors

**Warm Data (Qdrant on SSD):**
- Historical resume archive
- Full job posting database
- Extended company profiles

**Access Pattern:**
```python
class TieredVectorStore:
    def __init__(self):
        self.hot_cache = InMemoryVectorCache(max_memory_gb=8)
        self.warm_store = QdrantClient(url="http://localhost:6333")
    
    async def search(self, query_vector, top_k=10):
        # Try hot cache first
        hot_results = await self.hot_cache.search(query_vector, top_k)
        
        if len(hot_results) >= top_k:
            return hot_results
        
        # Fallback to warm store
        warm_results = await self.warm_store.search(query_vector, top_k)
        
        # Promote frequently accessed items to hot cache
        self._promote_to_hot(warm_results)
        
        return self._merge_results(hot_results, warm_results, top_k)
```

---

### Embedding Cache Strategy

**Redis Cache (2GB allocation):**
```python
class EmbeddingCache:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis = redis.Redis.from_url(redis_url)
        self.ttl = 86400  # 24 hours
    
    async def get_or_create_embedding(self, text: str, model: str):
        cache_key = f"emb:{model}:{hashlib.sha256(text.encode()).hexdigest()}"
        
        # Check cache
        cached = self.redis.get(cache_key)
        if cached:
            return np.frombuffer(cached, dtype=np.float32)
        
        # Generate and cache
        embedding = await self._generate_embedding(text, model)
        self.redis.setex(cache_key, self.ttl, embedding.tobytes())
        
        return embedding
```

**Expected Cache Hit Rate:** 60-80% for resume sections (high reuse)

---

## Task Queue Architecture

### Celery-Based Swarm Orchestration

**Queue Structure:**
```
High Priority Queue (P0):
├── User-facing resume generation
└── Real-time job matching

Medium Priority Queue (P1):
├── Batch resume updates
└── Vector store indexing

Low Priority Queue (P2):
├── Analytics processing
└── Model fine-tuning
```

**Worker Configuration:**
```python
# celeryconfig.py
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'

worker_concurrency = 8  # Match CPU cores
worker_prefetch_multiplier = 2
task_acks_late = True
task_reject_on_worker_lost = True

# Memory management
worker_max_memory_per_child = 4_000_000  # 4GB per worker (8 workers = 32GB)
```

**Task Definition:**
```python
from celery import Celery

app = Celery('agentic_workflow')

@app.task(bind=True, max_retries=3)
def generate_resume_task(self, job_description: str, user_profile: dict):
    try:
        # Each task runs in isolated process
        hop = SubatomicHop(hop_function=resume_generator)
        result = asyncio.run(hop.run(
            job_description=job_description,
            user_profile=user_profile
        ))
        return result
    except Exception as exc:
        # Exponential backoff retry
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

**Tasks:**
1. ✅ Create `.codeiumignore` to optimize IDE performance
2. ✅ Update `docker-compose.yml` resource limits
3. Implement `BatchEmbeddingService` in `scripts/runtime/shared/batch_embeddings.py`
4. Create `InMemoryVectorCache` in `scripts/runtime/shared/memory_vector_store.py`
5. Add `EmbeddingCache` to existing Redis integration

**Validation:**
- Measure embedding generation time (before/after batching)
- Measure vector search latency (disk vs. in-memory)
- Monitor memory usage with `docker stats`

---

### Phase 2: Parallel Execution (Week 2)

**Tasks:**
1. Refactor `SubatomicHop` to support parallel execution
2. Implement `execute_parallel_hops()` in DAG executor
3. Add `ParallelRAGPipeline` for multi-strategy retrieval
4. Create `ResumeSwarm` with multiprocessing pool

**Validation:**
- Benchmark single vs. parallel HOP execution
- Measure end-to-end resume generation throughput
- Verify no race conditions with concurrent writes

---

### Phase 3: Task Queue Integration (Week 3)

**Tasks:**
1. Install and configure Celery + Redis broker
2. Convert resume generation to Celery tasks
3. Implement priority queues (P0/P1/P2)
4. Add monitoring dashboard (Flower)

**Validation:**
- Process 100 resumes in parallel
- Measure queue latency and worker utilization
- Test failure recovery and retry logic

---

### Phase 4: Optimization & Tuning (Week 4)

**Tasks:**
1. Profile memory usage and optimize allocations
2. Tune batch sizes for optimal throughput
3. Implement adaptive concurrency based on load
4. Add metrics collection (Prometheus + Grafana)

**Validation:**
- Achieve 50-70% throughput improvement target
- Memory usage stays under 30GB (2GB buffer)
- CPU utilization 70-85% under load

---

## Docker Compose Resource Updates

**Updated Limits:**
```yaml
services:
  redis-stack:
    deploy:
      resources:
        limits:
          memory: 2G  # Increased from 1G for embedding cache
          cpus: '1.0'
  
  vector-db:
    deploy:
      resources:
        limits:
          memory: 4G  # Warm storage tier
          cpus: '2.0'
  
  agentic-app:
    deploy:
      resources:
        limits:
          memory: 24G  # Main application (8GB vectors + 16GB runtime)
          cpus: '6.0'  # Leave 2 cores for system
```

**Total Allocation:** 30GB / 32GB (2GB safety buffer)

---

## Monitoring & Observability

### Key Metrics to Track

**Throughput Metrics:**
- Resumes generated per minute
- HOPs executed per second
- Vector searches per second

**Latency Metrics:**
- P50/P95/P99 resume generation time
- Embedding generation time
- Vector search latency

**Resource Metrics:**
- Memory usage per service
- CPU utilization per core
- Redis cache hit rate
- Vector store query rate

**Dashboard Setup:**
```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

resume_generation_counter = Counter('resumes_generated_total', 'Total resumes generated')
resume_generation_time = Histogram('resume_generation_seconds', 'Resume generation time')
memory_usage_gauge = Gauge('memory_usage_bytes', 'Memory usage by component', ['component'])
```

---

## Risk Mitigation

### Memory Exhaustion Prevention

**Strategy:**
- Set hard limits in Docker Compose (24GB for main app)
- Implement LRU eviction in in-memory vector cache
- Monitor with alerts at 90% threshold

**Circuit Breaker:**
```python
class MemoryCircuitBreaker:
    def __init__(self, max_memory_gb=30):
        self.max_memory_bytes = max_memory_gb * 1024 ** 3
    
    def check_memory(self):
        import psutil
        current = psutil.virtual_memory().used
        
        if current > self.max_memory_bytes:
            raise MemoryError("Circuit breaker: Memory limit exceeded")
```

---

### Deadlock Prevention

**Strategy:**
- Use `asyncio.wait_for()` with timeouts on all async operations
- Implement task timeout in Celery (5 minutes max)
- Add health checks to detect stuck workers

---

### Data Consistency

**Strategy:**
- Use Redis transactions for atomic state updates
- Implement idempotent task design (safe to retry)
- Add checksum validation for vector store writes

---

## Success Criteria

**Performance Targets:**
- ✅ 50-70% reduction in total pipeline time
- ✅ 5x improvement in batch resume generation
- ✅ 10x faster vector lookups (in-memory cache)
- ✅ 80%+ cache hit rate for embeddings

**Stability Targets:**
- ✅ Memory usage < 30GB under peak load
- ✅ CPU utilization 70-85% (not saturated)
- ✅ Zero deadlocks or race conditions
- ✅ 99.9% task success rate

**Developer Experience:**
- ✅ IDE remains responsive (`.codeiumignore` working)
- ✅ Fast Context indexing < 10 seconds
- ✅ Clear metrics dashboard for debugging

---

## Next Steps

1. **Review this plan** and adjust priorities based on business needs
2. **Run baseline benchmarks** to establish current performance
3. **Start Phase 1** implementation (batching + in-memory cache)
4. **Iterate and measure** after each phase

**Questions to Address:**
- Which resume generation use case has highest priority? (batch vs. real-time)
- What is acceptable latency for single resume generation?
- Should we prioritize throughput or latency optimization?

---

## Appendix: Code Locations

**Files to Modify:**
- `scripts/runtime/core/subatomic_hop.py` - Add parallel execution
- `scripts/runtime/shared/titanium_rag_pipeline.py` - Add parallel retrieval
- `apps_rg/resume_engine/resume_generator.py` - Add batch processing
- `docker-compose.yml` - Update resource limits

**New Files to Create:**
- `scripts/runtime/shared/batch_embeddings.py` - Batch embedding service
- `scripts/runtime/shared/memory_vector_store.py` - In-memory vector cache
- `scripts/runtime/shared/tiered_vector_store.py` - Hot/warm tier manager
- `scripts/runtime/shared/resume_swarm.py` - Multi-process resume generator
- `scripts/runtime/shared/celery_tasks.py` - Celery task definitions
- `config/celeryconfig.py` - Celery configuration

---

**End of Optimization Plan**
