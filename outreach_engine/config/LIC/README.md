# LIC Configuration Profile

This directory contains configuration profiles for the LIC (Legal/Intellectual/Compliance) outreach pipeline.

## Files

- `lic_profile.py`: Main configuration definitions and default profiles
- `README.md`: This documentation file

## Usage

### Default Profile
```python
from config.LIC.lic_profile import DEFAULT_LIC_PROFILE

# Use default LIC settings
profile = DEFAULT_LIC_PROFILE
print(profile.default_llm_model)  # "gpt-4"
print(profile.safety_strictness)  # "standard"
```

### Named Profiles
```python
from config.LIC.lic_profile import get_lic_profile

# Get predefined profile
dev_profile = get_lic_profile("development")
prod_profile = get_lic_profile("production")
research_profile = get_lic_profile("research")
```

### Custom Profiles
```python
from config.LIC.lic_profile import create_custom_profile

# Create custom profile with overrides
custom_profile = create_custom_profile(
    safety_strictness="strict",
    max_parallel_tasks=8,
    cost_limit_per_run=20.0
)
```

## Configuration Options

### LLM Configuration
- `default_llm_model`: Default language model to use
- `temperature_envelope`: Temperature settings for different reasoning intensities
- `max_tokens`: Maximum tokens per generation

### Reasoning Configuration
- `default_reasoning_intensity`: Default reasoning intensity level
- `retrieval_depth`: Number of documents to retrieve
- `kg_usage_flags`: Knowledge graph usage settings

### Concurrency Settings
- `concurrency_mode`: How to execute tasks (sequential/parallel/batch)
- `max_parallel_tasks`: Maximum parallel tasks
- `batch_size`: Size of batches for batch processing

### Safety Configuration
- `safety_strictness`: Safety strictness level (permissive/standard/strict)
- `enable_pii_sanitization`: Whether to enable PII sanitization
- `enable_bias_auditing`: Whether to enable bias auditing

### Performance Configuration
- `cost_limit_per_run`: Maximum cost per run
- `latency_limit_seconds`: Maximum allowed latency
- `enable_telemetry`: Whether to enable performance telemetry

## Override Strategy

Profiles are designed to be composable and overrideable:

1. **Base defaults**: Defined in `LICHyperparameters.__post_init__()`
2. **Named profiles**: Predefined configurations for common use cases
3. **Runtime overrides**: Custom profiles created with `create_custom_profile()`

This allows for flexible configuration while maintaining sensible defaults.
