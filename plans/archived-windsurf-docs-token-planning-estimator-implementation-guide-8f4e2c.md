---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\token-planning-estimator-implementation-guide-8f4e2c.md'
original_relative_path: 'token-planning-estimator-implementation-guide-8f4e2c.md'
source_sha256: bd843ab5f642d257915757f715cc150676a6b90de4b6db948f80ef57abef75b7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-26'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Token Planning Estimator Implementation Guide

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Overview

The Context Window Estimator provides deterministic token budget management for SWE 1.5 planning phases and waves. It ensures every step stays safely within the 200K context window by estimating tokens from the actual assembled payload before each model call.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Planning Step   │───▶│ Preflight Hook   │───▶│ Token Estimator │
│ (files, prompts)│    │ (integration)    │    │ (core logic)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Compression     │◀───│ Budget Report    │◀───│ Token Estimate  │
│ Policies        │    │ (JSON output)    │    │ (detailed)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Components

### 1. ContextWindowEstimator (`agentic_core/planning/token_estimator.py`)

Core estimation engine that:
- Analyzes the actual payload content
- Applies conservative token estimation rates
- Implements compression policies
- Generates detailed budget reports

**Key Features:**
- Conservative token rates (biased high to avoid underestimation)
- Content type detection (code, text, JSON, diffs, logs)
- Automatic compression when over budget
- Detailed contributor analysis

### 2. PlanningPreflightHook (`agentic_core/planning/preflight_hook.py`)

Integration layer that:
- Wraps every planning step with budget checking
- Maintains budget history across sessions
- Provides decorator for automatic enforcement
- Raises errors for exceeded hard limits

**Key Features:**
- Persistent budget history logging
- Decorator-based enforcement
- Budget summary statistics
- Automatic preflight checking

### 3. Token Budget Configuration

```python
@dataclass
class TokenBudget:
    HARD_MAX_CONTEXT: int = 200000      # Absolute maximum
    SAFE_OPERATING_CAP: int = 170000     # Safe upper limit
    WARNING_THRESHOLD: int = 150000     # Warning zone
    DEFAULT_RESERVED_OUTPUT: int = 12000 # Reserved for model output
    DEFAULT_SAFETY_BUFFER: int = 8000    # Safety margin
    DEFAULT_MAX_INPUT_TARGET: int = 150000 # Target input limit
```

## Token Estimation Rates

Conservative character-to-token ratios (biased high):

| Content Type | Rate (chars → tokens) | Description |
|--------------|---------------------|-------------|
| code         | 0.35                | ~3 chars per token |
| text         | 0.40                | ~2.5 chars per token |
| json         | 0.33                | ~3 chars per token |
| diff         | 0.30                | ~3.3 chars per token |
| log          | 0.38                | ~2.6 chars per token |
| system       | 0.42                | ~2.4 chars per token |

## Integration Methods

### Method 1: Manual Preflight Check

```python
from agentic_core.planning.preflight_hook import PlanningPreflightHook

# Initialize hook
hook = PlanningPreflightHook()

# Before each planning step
estimate = hook.preflight_check(
    plan_step="implement_feature_x",
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    files=file_contents,
    diffs=diff_contents,
    logs=log_outputs,
    retrieved_context=retrieved_chunks,
    prior_steps=prior_step_contents
)

# Check if proceed
if estimate.action == 'proceed':
    # Execute the step
    result = execute_step(...)
elif estimate.action == 'compress':
    # Step was auto-compressed, proceed
    result = execute_step(...)
else:  # 'block'
    # Handle budget exceeded
    raise Exception("Token budget exceeded")
```

### Method 2: Decorator-Based Enforcement

```python
from agentic_core.planning.preflight_hook import require_token_budget

# Initialize hook
hook = PlanningPreflightHook()

@require_token_budget(hook)
def execute_plan_step(plan_step, system_prompt, user_prompt, files, diffs, logs, 
                     retrieved_context, prior_steps, **kwargs):
    """Execute a planning step with automatic token budget enforcement"""
    # Step implementation
    return process_step(...)

# Usage - preflight check happens automatically
result = execute_plan_step(
    plan_step="implement_feature_x",
    system_prompt=system_prompt,
    user_prompt=user_prompt,
    files=file_contents,
    diffs=diff_contents,
    logs=log_outputs,
    retrieved_context=retrieved_chunks,
    prior_steps=prior_step_contents
)
```

### Method 3: Planning Pipeline Integration

```python
class PlanningPipeline:
    def __init__(self):
        self.preflight_hook = PlanningPreflightHook()
    
    def execute_step(self, step_config):
        """Execute a planning step with budget enforcement"""
        # Extract context from step config
        context = self._extract_context(step_config)
        
        # Preflight check
        estimate = self.preflight_hook.preflight_check(**context)
        
        # Execute based on estimate
        if estimate.action == 'block':
            raise TokenBudgetExceededError(
                f"Step blocked: {estimate.total_projected_tokens:,} tokens"
            )
        
        # Execute step
        return self._execute_step_with_context(step_config, estimate)
```

## Compression Policies

When over budget, the estimator applies compression in this order:

1. **Remove Duplicates** - Eliminate duplicate content
2. **Trim Retry History** - Keep only recent retry attempts
3. **Summarize Large Files** - Replace files >1000 lines with summaries
4. **Trim Logs to Errors** - Keep only error lines and context
5. **Reduce Retrieval Chunks** - Limit to top 10 most relevant chunks
6. **Prefer Diff Over File** - Use diff OR full file, not both
7. **Drop Low Relevance Files** - Remove generated/lock files

## Budget Report Format

```json
{
  "plan_step": "implement_feature_x",
  "estimated_input_tokens": 125000,
  "reserved_output_tokens": 12000,
  "safety_buffer_tokens": 8000,
  "total_projected_tokens": 145000,
  "status": "green",
  "action": "proceed",
  "top_contributors": [
    {"type": "files", "tokens": 80000},
    {"type": "system_prompt", "tokens": 25000},
    {"type": "retrieval", "tokens": 15000},
    {"type": "logs", "tokens": 3000},
    {"type": "diffs", "tokens": 2000}
  ],
  "recommended_reductions": [],
  "compression_applied": []
}
```

## Status Levels

| Status | Token Range | Action | Description |
|--------|-------------|--------|-------------|
| green  | ≤ 150,000   | proceed | Safe to execute |
| yellow | 150,001-170,000 | compress | Auto-compress then proceed |
| red    | > 170,000   | block   | Must reduce context |

## Budget History

The system maintains a persistent log of all budget estimates:

```python
# Get budget summary
summary = hook.get_budget_summary()
print(f"Total steps: {summary['total_steps']}")
print(f"Average tokens: {summary['average_tokens_per_step']}")
print(f"Status distribution: {summary['status_distribution']}")
```

History is saved to: `docs/reports/plans/token_budget_log.json`

## Testing

Run the test suite:

```bash
# Run all token estimator tests
python -m pytest tests/unit/agentic_core/planning/test_token_estimator.py -v

# Run specific test categories
python -m pytest tests/unit/agentic_core/planning/test_token_estimator.py::TestContextWindowEstimator -v
python -m pytest tests/unit/agentic_core/planning/test_token_estimator.py::TestPlanningPreflightHook -v
```

## Configuration Options

### Custom Budget Limits

```python
from agentic_core.planning.token_estimator import TokenBudget, ContextWindowEstimator

# Custom budget
custom_budget = TokenBudget(
    HARD_MAX_CONTEXT=180000,  # Lower hard limit
    WARNING_THRESHOLD=120000  # Earlier warning
)

estimator = ContextWindowEstimator(budget=custom_budget)
```

### Custom Compression Policies

```python
# Modify compression policies
estimator.compression_policies['max_log_lines'] = 30  # Stricter log trimming
estimator.compression_policies['file_summary_threshold'] = 500  # Earlier summarization
```

### Custom Token Rates

```python
# Adjust token estimation rates
estimator.token_rates['code'] = 0.4  # More conservative for code
estimator.token_rates['text'] = 0.35  # Less conservative for text
```

## Error Handling

### TokenBudgetExceededError

Raised when the hard limit is exceeded:

```python
from agentic_core.planning.preflight_hook import TokenBudgetExceededError

try:
    hook.preflight_check(...)
except TokenBudgetExceededError as e:
    print(f"Budget exceeded: {e}")
    # Handle budget exceeded - reduce context and retry
```

### Logging

The estimator provides detailed logging:

```python
import logging

# Enable debug logging
logging.getLogger('agentic_core.planning.token_estimator').setLevel(logging.DEBUG)
logging.getLogger('agentic_core.planning.preflight_hook').setLevel(logging.DEBUG)
```

## Performance Considerations

- **Estimation Speed**: Token estimation is O(n) in content size
- **Memory Usage**: Minimal - processes content incrementally
- **Compression Overhead**: Applied only when over budget
- **History Storage**: JSON file grows linearly with step count

## Best Practices

1. **Always Use Preflight**: Never skip the preflight check
2. **Monitor Budget History**: Review trends and optimize
3. **Adjust Thresholds**: Tune based on your specific use case
4. **Handle Compression**: Be aware content may be auto-compressed
5. **Test Edge Cases**: Verify behavior with large payloads

## Troubleshooting

### Common Issues

1. **Underestimation**: Increase token rates for more conservative estimates
2. **Over-compression**: Adjust compression thresholds
3. **Performance**: Reduce content size before estimation
4. **History Bloat**: Clear history periodically with `hook.clear_history()`

### Debug Information

Enable debug logging to see detailed estimation breakdown:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

This will show:
- Content type detection
- Token calculation details
- Compression decisions
- Budget analysis

## Integration Checklist

- [ ] Initialize PlanningPreflightHook in your planning pipeline
- [ ] Add preflight check before each SWE 1.5 call
- [ ] Configure budget thresholds for your use case
- [ ] Set up budget history monitoring
- [ ] Add error handling for TokenBudgetExceededError
- [ ] Test with various payload sizes
- [ ] Verify compression policies work as expected
- [ ] Monitor budget trends over time

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

