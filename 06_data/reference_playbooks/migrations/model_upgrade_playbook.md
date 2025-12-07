# Model Upgrade Playbook

## Overview

This playbook guides safe migration between LLM model versions with minimal
disruption and comprehensive validation.

---

## Pre-Migration Checklist

### 1. Compatibility Assessment

```python
# Compare model capabilities
old_model = "gpt-4-0613"
new_model = "gpt-4o-2024-08-06"

compatibility_checks = {
    "context_window": (8192, 128000),
    "function_calling": (True, True),
    "json_mode": (True, True),
    "vision": (False, True),
    "streaming": (True, True),
}

for feature, (old, new) in compatibility_checks.items():
    status = "✓" if new >= old else "⚠️ BREAKING"
    print(f"{feature}: {old} → {new} {status}")
```

### 2. Benchmark Suite

```python
# Run evaluation suite on both models
from eval_suite import run_benchmarks

old_results = run_benchmarks(model=old_model, suite="production")
new_results = run_benchmarks(model=new_model, suite="production")

# Compare metrics
metrics = ["accuracy", "latency_p50", "cost_per_1k", "safety_score"]
for metric in metrics:
    delta = new_results[metric] - old_results[metric]
    print(f"{metric}: {old_results[metric]:.3f} → {new_results[metric]:.3f} ({delta:+.3f})")
```

---

## Migration Strategy

### Phase 1: Shadow Mode (1 week)

```python
# Run both models, compare outputs
async def shadow_compare(request):
    old_response, new_response = await asyncio.gather(
        call_model(old_model, request),
        call_model(new_model, request),
    )

    # Log comparison
    log_comparison(
        request=request,
        old_response=old_response,
        new_response=new_response,
        similarity=compute_similarity(old_response, new_response),
    )

    # Return old model response (production)
    return old_response
```

### Phase 2: Canary Deployment (1 week)

```python
# Route percentage of traffic to new model
def route_request(request, user_id):
    # 5% canary
    if hash(user_id) % 100 < 5:
        return new_model
    return old_model
```

### Phase 3: Gradual Rollout

| Day | New Model % | Monitoring |
|-----|-------------|------------|
| 1 | 5% | Intensive |
| 3 | 25% | High |
| 5 | 50% | Standard |
| 7 | 75% | Standard |
| 10 | 100% | Standard |

---

## Rollback Procedure

### Automatic Triggers

```python
ROLLBACK_THRESHOLDS = {
    "error_rate": 0.05,      # 5% errors
    "latency_p99": 10.0,     # 10 second p99
    "safety_violations": 1,   # Any safety issue
}

def check_rollback_needed(metrics):
    for metric, threshold in ROLLBACK_THRESHOLDS.items():
        if metrics[metric] > threshold:
            return True, metric
    return False, None
```

### Manual Rollback

```bash
# Immediate rollback
kubectl set env deployment/llm-api MODEL_VERSION=gpt-4-0613

# Verify rollback
kubectl rollout status deployment/llm-api
```

---

## Post-Migration

### Validation Checklist

- [ ] All benchmark metrics within acceptable range
- [ ] No increase in safety violations
- [ ] Latency within SLA
- [ ] Cost projections validated
- [ ] User feedback collected
- [ ] Documentation updated

### Deprecation Timeline

| Milestone | Action |
|-----------|--------|
| M+0 | New model in production |
| M+2 | Old model deprecated warning |
| M+4 | Old model removed from config |
| M+6 | Old model API access revoked |
