# Qwen vLLM Optimization Summary

## Changes Made

### 1. Fixed Critical Issue: EvalOrchestrator.py
- **Problem**: ~80 duplicate guardian comment lines corrupting file
- **Fix**: Removed all duplicate `# guardian: Add error context logging` comments
- **File**: `apps_eval/reasoning/EvalOrchestrator.py:526`

### 2. Created Optimized vLLM Client
**File**: `agentic_core/L2_execution/apps_qwen/optimized_vllm_client.py`

**Features**:
- **Connection Pooling**: HTTP keep-alive with TCP connector (20 total, 10 per host)
- **Request Batching**: Configurable batch size (default 4) with 50ms timeout
- **Concurrency Control**: Async semaphore (default 8 concurrent)
- **Response Caching**: SHA-256 based cache (default 1000 entries)
- **Dynamic Timeouts**: 5min total, 10sec connect, 60sec read

**API**:
```python
from agentic_core.L2_execution.apps_qwen import OptimizedVLLMClient, VLLMRequest

client = OptimizedVLLMClient(
    base_url="http://localhost:8000/v1",
    model="Qwen/Qwen2.5-14B-Instruct-AWQ",
    max_concurrent=8,
    batch_size=4,
)
await client.start()

request = VLLMRequest(
    prompt="What is 2+2?",
    max_tokens=100,
    temperature=0.1,
)
response = await client.infer(request)
```

### 3. Rewrote AppsQwenGateway (Now Uses Real vLLM)
**File**: `agentic_core/L2_execution/apps_qwen/apps_qwen_gateway.py`

**Before**: Mock responses with TODO comment
**After**: Full vLLM integration via OptimizedVLLMClient

**New Features**:
- Real inference to localhost:8000 vLLM server
- Batch inference support (`infer_batch()`)
- Dynamic confidence calculation
- Cache hit tracking
- Token usage reporting

**API**:
```python
from agentic_core.L2_execution.apps_qwen import (
    AppsQwenGateway, AppsQwenRequest, get_apps_qwen_gateway
)

# Option 1: Direct instantiation
gateway = AppsQwenGateway(
    model_id="Qwen/Qwen2.5-14B-Instruct-AWQ",
    max_concurrent=8,
    batch_size=4,
)

# Option 2: Singleton pattern
gateway = await get_apps_qwen_gateway()

# Single inference
request = AppsQwenRequest(
    app_name="apps_eval",
    prompt="Review this code: ...",
    max_tokens=1536,
    temperature=0.05,
)
response = await gateway.infer(request)

# Batch inference
requests = [req1, req2, req3, req4]
responses = await gateway.infer_batch(requests)
```

### 4. Created GPU Memory Monitor
**File**: `agentic_core/L2_execution/apps_qwen/gpu_memory_monitor.py`

**Features**:
- Real-time GPU memory monitoring via nvidia-smi
- Dynamic batch size recommendations
- Memory pressure throttling (50%/75%/85%/95% thresholds)
- Configurable check interval (default 5s)

**API**:
```python
from agentic_core.L2_execution.apps_qwen import get_gpu_monitor, GPUMemoryMonitor

monitor = get_gpu_monitor()
monitor.start()

# Get recommendations
rec = monitor.get_recommendations()
print(f"Recommended batch_size: {rec.batch_size}")
print(f"Should throttle: {rec.should_throttle}")
print(f"Free VRAM: {rec.free_mb} MB")

# Register callback for memory updates
def on_memory_update(info):
    if info.utilization_percent > 85:
        print("GPU memory critical!")

monitor.register_callback(on_memory_update)
```

### 5. Updated Package Exports
**File**: `agentic_core/L2_execution/apps_qwen/__init__.py`

Now exports all optimized components:
- `AppsQwenGateway`, `AppsQwenRequest`, `AppsQwenResponse`
- `OptimizedVLLMClient`, `VLLMRequest`, `VLLMResponse`
- `GPUMemoryMonitor`, `GPUMemoryInfo`, `GPURecommendation`
- `get_apps_qwen_gateway()`, `get_vllm_client()`, `get_gpu_monitor()`

## Expected Performance Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Connection setup | Per-request | Reused (keep-alive) | ~50ms saved per call |
| Batching | None | 4 requests/batch | ~4x throughput |
| Caching | None | SHA-256 based | Instant for repeats |
| Concurrency | Unbounded | 8 parallel | Prevents GPU OOM |
| GPU monitoring | None | Real-time | Dynamic throttling |

## Integration Points

### For apps_eval (EvalOrchestrator):
Already integrated - `evaluate_with_qwen()` method uses gateway singleton.

### For apps_exec (ExecOrchestrator):
Already integrated - `generate_execution_plan_with_qwen()` uses gateway.

### For apps_rg (RgResumeOrchestrator):
Search shows Qwen references - recommend updating to use `get_apps_qwen_gateway()`.

## Next Steps to Activate

1. **Ensure vLLM server is running**:
   ```bash
   wsl -d Ubuntu-24.04 -- bash /mnt/c/Git/Agentic-Workflow/tools/start_vllm_awq.sh
   ```

2. **Test the optimized client**:
   ```python
   python -c "
   import asyncio
   from agentic_core.L2_execution.apps_qwen import get_apps_qwen_gateway, AppsQwenRequest
   
   async def test():
       gateway = await get_apps_qwen_gateway()
       req = AppsQwenRequest(app_name='test', prompt='What is 2+2? Answer in one word.', max_tokens=10)
       resp = await gateway.infer(req)
       print(f'Success: {resp.success}, Response: {resp.response}, Cached: {resp.cached}')
   
   asyncio.run(test())
   "
   ```

3. **Monitor GPU memory**:
   ```python
   from agentic_core.L2_execution.apps_qwen import get_gpu_monitor
   monitor = get_gpu_monitor()
   monitor.start()
   print(monitor.get_recommendations())
   ```

## Files Created/Modified

| File | Action | Purpose |
|------|--------|---------|
| `apps_qwen/optimized_vllm_client.py` | Created | High-performance async client |
| `apps_qwen/apps_qwen_gateway.py` | Rewritten | Real vLLM integration (was mock) |
| `apps_qwen/gpu_memory_monitor.py` | Created | Dynamic GPU optimization |
| `apps_qwen/__init__.py` | Updated | Export all new components |
| `apps_eval/reasoning/EvalOrchestrator.py` | Fixed | Removed guardian corruption |

## Verification

Run this to verify the optimization is working:

```python
import asyncio
from agentic_core.L2_execution.apps_qwen import (
    get_apps_qwen_gateway, 
    get_gpu_monitor,
    AppsQwenRequest
)

async def verify():
    # Test GPU monitor
    gpu = get_gpu_monitor()
    gpu.start()
    rec = gpu.get_recommendations()
    print(f"GPU: {rec.free_mb:.0f}MB free, batch_size={rec.batch_size}")
    
    # Test gateway
    gw = await get_apps_qwen_gateway()
    health = await gw.async_health_check()
    print(f"Gateway health: {health.get('healthy')}")
    
    # Test inference
    req = AppsQwenRequest(
        app_name="verification",
        prompt="Say 'optimization working' and nothing else.",
        max_tokens=20,
        temperature=0.0,
    )
    resp = await gw.infer(req)
    print(f"Inference: success={resp.success}, response='{resp.response}'")
    print(f"Metrics: latency={resp.latency_ms:.1f}ms, cached={resp.cached}")

asyncio.run(verify())
```
