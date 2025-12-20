# Outreach Engine (E3) - Zero-Side Effect (ZSE) Documentation

## Overview

The Outreach Engine (E3) implements a Zero-Side Effect (ZSE) policy for high-impact external actions (email outreach). It ensures no email is sent unless all security and quality gates pass, with strict enforcement through P8 egress filtering, P6 consensus vetting, and P10 shadow mode refinement.

## Architecture

### Core Components

1. **Networking Utility** - P8 Egress Filter for domain whitelisting
2. **Pitch Generator** - Personalized outreach content creation
3. **Shadow Mode Engine** - P10 pre-flight refinement
4. **L5 Consolidated Knowledge** - P6 consensus via multi-model checking
5. **Outreach Engine ZSE** - Main orchestrator with ZSE loop
6. **P5 Dead Man's Switch** - Watchdog for rapid action detection

### ZSE Policy

The Zero-Side Effect policy ensures:

- No external actions without pre-flight validation
- Maximum 2 refinement attempts (MAX_PITCH_REFINEMENTS=2)
- All network traffic passes P8 egress filter
- All pitches pass P6 consensus check
- Mock email sending by default (dry_run=True)

## Phases and Components

### P8: Egress Filter

Located in `agentic_core/utils/networking.py`

```python
from agentic_core.utils.networking import strict_egress_filter, get_networking_utility

# Check if URL is allowed
network = get_networking_utility()
result = network.strict_egress_filter(url)
if result.status == "FAIL":
    # Block and abort
    handle_egress_block(result.reason)
```

**Features:**

- Domain whitelisting with subdomain support
- Centralized network traffic control
- Mock fetching for safety during development
- Statistics tracking for allowed/blocked requests

### P6: Consensus Vetting

Located in `agentic_core/knowledge/l5_consolidated.py`

```python
from agentic_core.knowledge.l5_consolidated import get_consolidated_knowledge

# Multi-model consensus check
knowledge = get_consolidated_knowledge()
result = knowledge.query_consensus(pitch, brand_guidelines)
if result["status"] == "FAIL":
    # Trigger P10 refinement
    trigger_shadow_mode(result["reason"])
```

**Features:**

- Brand compliance checking
- Spam detection
- Professionalism validation
- Requires all models to pass for consensus

### P10: Shadow Mode

Located in `agentic_core/utils/shadow_mode.py`

```python
from agentic_core.utils.shadow_mode import ShadowModeEngine

# Refine pitch in shadow mode
shadow = ShadowModeEngine()
result = shadow.refine_pitch(pitch, error_reason)
if result.confidence >= 0.7:
    # Apply refinement
    pitch = shadow.apply_refinement(pitch, result)
```

**Features:**

- Pre-flight refinement simulation
- Confidence scoring for improvements
- Rule-based and LLM-based refinement
- Detailed improvement tracking

### P5: Dead Man's Switch

Located in `agentic_core/utils/dead_man_switch.py`

```python
from agentic_core.utils.dead_man_switch import watchdog, track_action

@watchdog(max_actions=10, time_window=300)
def send_email_batch():
    # Will kill process if 10+ actions in 5 minutes
    pass

# Manual tracking
track_action("OutreachEngine", "SEND_EMAIL")
```

**Features:**

- Action frequency monitoring
- Automatic process termination on abuse
- Configurable thresholds
- Background monitoring thread

## Usage

### Basic Outreach

```python
from agentic_core.engines.outreach_engine_zse import OutreachEngineZSE

# Initialize engine (dry_run=True by default)
engine = OutreachEngineZSE(output_dir="output", dry_run=True)

# Execute outreach with ZSE protection
exit_reason, result = engine.execute_outreach(
    company_url="https://linkedin.com/company/techcorp",
    contact_email="hiring@techcorp.com"
)

if exit_reason == ExitReason.ZSE_SUCCESS:
    print(f"Success! Refinements: {result['refinements']}")
else:
    print(f"Failed: {exit_reason.value}")
```

### Production Mode

```python
# WARNING: Only disable dry_run in production with proper safeguards
engine = OutreachEngineZSE(
    output_dir="production/output",
    dry_run=False  # Enables real email sending
)
```

### Custom Configuration

```python
# Custom egress filter whitelist
from agentic_core.utils.networking import get_networking_utility

network = get_networking_utility(allowed_hosts={
    "linkedin.com",
    "crunchbase.com",
    "your-domain.com"
})

# Custom brand guidelines
brand_guidelines = {
    "tone": "professional",
    "prohibited_words": ["amazing", "incredible"],
    "max_length": 200
}
```

## Exit Codes and Reasons

| Exit Reason | Description | Action |
|-------------|-------------|--------|
| ZSE_SUCCESS | Pitch passed all checks | Email sent (or dry run) |
| P8_EGRESS_BLOCK | Domain not whitelisted | Check URL/domain |
| ZSE_MAX_REFINEMENTS | Failed after 2 refinements | Review pitch strategy |
| CRITICAL_ERROR | System error | Check logs |

## Test Coverage

The test suite (`tests/test_outreach_engine_zse.py`) covers:

1. **TC-E3-101**: Standard ZSE Success
2. **TC-E3-102**: P8 Egress Filter Block
3. **TC-E3-201**: P6 Compliance Failure (ZSE Loop)
4. **TC-E3-202**: P10 Refinement Success
5. **TC-E3-203**: ZSE Max Refinements Failure
6. **TC-E3-301**: P5 Watchdog Kill Condition
7. **TC-E3-302**: L4 Time Utility Check

### Running Tests

```bash
# Run all tests
python tests/test_outreach_engine_zse.py

# Run specific test
python -m unittest tests.test_outreach_engine_zse.TestStandardZSESuccess
```

## Configuration

### Allowed Hosts (P8)

Default whitelist in `agentic_core/utils/networking.py`:

```python
OUTREACH_ALLOWED_HOSTS = {
    "linkedin.com",
    "crunchbase.com",
    "techcrunch.com",
    "venturebeat.com",
    "company-websites.com",
    "api.email-service.com"
}
```

### Brand Guidelines (P6)

```json
{
  "tone": "professional",
  "prohibited_words": ["amazing", "incredible", "revolutionary", "guarantee"],
  "max_exclamation": 1,
  "min_length": 100,
  "max_length": 200
}
```

### Watchdog Settings (P5)

```python
# Default: Kill if 10+ actions in 5 minutes
max_actions = 10
time_window = 300  # seconds
```

## Logging

All actions are logged to `logs/outreach_engine_zlg.log`:

```
2024-12-16 10:00:00 - agentic_core.engines.outreach_engine_zse - INFO - P5_REGISTER: OutreachEngine (PID: 12345)
2024-12-16 10:00:01 - agentic_core.engines.outreach_engine_zse - INFO - ACTION: L1_FETCH_START | {'company_url': 'https://linkedin.com/company/test'}
2024-12-16 10:00:02 - agentic_core.engines.outreach_engine_zse - INFO - ACTION: P8_EGRESS_BLOCK | {'host': 'malicious.com'}
2024-12-16 10:00:03 - agentic_core.engines.outreach_engine_zse - INFO - ACTION: P10_START | {'attempt': 1}
2024-12-16 10:00:04 - agentic_core.engines.outreach_engine_zse - INFO - ACTION: ZSE_SUCCESS
2024-12-16 10:00:05 - agentic_core.engines.outreach_engine_zse - INFO - ACTION: SEND_EMAIL_SUCCESS | {'to': 'test@example.com', 'dry_run': True}
```

## Security Considerations

### Zero-Side Effect Guarantees

1. **P8 Egress Filter** - Blocks all non-whitelisted network traffic
2. **P6 Consensus** - Requires multi-model approval for content
3. **P10 Shadow Mode** - Pre-flight refinement before side effects
4. **P5 Watchdog** - Kills process on rapid action bursts
5. **Dry Run Default** - Email sending disabled by default

### Threat Mitigation

- **Domain Whitelisting** - Prevents connections to malicious sites
- **Content Validation** - Blocks spam and non-compliant content
- **Rate Limiting** - Prevents email spam bursts
- **Process Isolation** - Watchdog can terminate misbehaving processes

### Performance Considerations

#### Optimization Strategies

1. **Caching** - Company context and contact relationships
2. **Batch Processing** - Multiple outreach campaigns
3. **Shadow Mode** - Reduces failed sends by pre-validation
4. **Async Operations** - Non-blocking network requests

### Monitoring

Track these metrics:
- Success rate (target >90%)
- Refinement rate (target <30%)
- P8 block rate (target <5%)
- Average execution time

## Troubleshooting

### Common Issues

1. **P8 Egress Blocks**
   - Check domain whitelist
   - Verify URL format
   - Review network configuration

2. **P6 Consensus Failures**
   - Review brand guidelines
   - Check prohibited words
   - Adjust tone requirements

3. **Max Refinements Reached**
   - Lower brand compliance thresholds
   - Improve pitch templates
   - Review target audience

4. **P5 Watchdog Kills**
   - Increase action thresholds
   - Implement batching
   - Check for infinite loops

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('agentic_core.engines.outreach_engine_zse').setLevel(logging.DEBUG)

# Run with debug
engine = OutreachEngineZSE(output_dir="debug/output")
exit_reason, result = engine.execute_outreach("test-url")
```

## Future Enhancements

### Planned Features

1. **Multi-Channel Support**
   - LinkedIn messaging
   - Twitter outreach
   - SMS messaging

2. **Advanced Personalization**
   - AI-powered tone matching
   - Cultural adaptation
   - Industry-specific templates

3. **Safety Improvements**
   - Human approval gates
   - Audit trail logging
   - Compliance reporting

4. **Performance**
   - Parallel processing
   - Distributed sending
   - Real-time analytics

### Extension Points

- Custom egress filters
- Additional consensus models
- Alternative refinement strategies
- Custom watchdog rules

## Conclusion

The Outreach Engine ZSE provides a robust, secure framework for external outreach with zero side effects guaranteed. By implementing multiple layers of validation and pre-flight checks, it ensures professional, compliant communication while preventing abuse and errors.
