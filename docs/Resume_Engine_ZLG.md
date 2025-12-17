# Resume Engine (E2) - Zero-Loss Generation (ZLG) Documentation

## Overview

The Resume Engine (E2) implements a Zero-Loss Generation (ZLG) policy for hyper-personalized, secure document generation. It consolidates multiple layers of the agentic system to provide unified access to knowledge and security protocols.

## Architecture

### Core Components

1. **Security Utilities (L1)** - Consolidated P3 Firewall and P4 Fact Checker
2. **L5 Consolidated Knowledge** - Unified access to profiles and templates
3. **Core Utilities** - Draft generation, semantic scoring, file management
4. **Shadow Mode Engine (P10)** - Self-correction simulation
5. **Resume Engine ZLG** - Main orchestrator with ZLG loop

### ZLG Policy

The Zero-Loss Generation policy ensures:

- No output fails security checks without self-correction attempts
- Maximum 3 rewrite attempts (MAX_REWRITE_ATTEMPTS=3)
- All inputs pass through P3 firewall
- All outputs validated by P4 fact checker
- Quality threshold enforced (MIN_ACCEPTABLE_SCORE=0.5)

## Phases and Components

### P3: Prompt Firewall

Located in `agentic_core/security/security_utilities.py`

```python
from agentic_core.security.security_utilities import PromptFirewall, scan_for_injection

# Scan input for injections
result = scan_for_injection(user_input)
if result.status == SecurityStatus.FAIL:
    # Block and log
    handle_injection(result.reason)
```

**Features:**

- Detects prompt injection patterns
- Identifies suspicious keyword density
- Sanitizes input when needed
- Returns structured SecurityResult

#### P4: Fact Checker

Located in `agentic_core/security/security_utilities.py`

```python
from agentic_core.security.security_utilities import FactChecker, validate_facts

# Validate skills against truth anchors
result = validate_facts(draft_content)
if result.status == SecurityStatus.FAIL:
    # Trigger rewrite
    trigger_shadow_mode(result.reason)
```

**Features:**

- Validates skills against golden record
- Checks experience claims
- Configurable truth anchors
- Detailed violation reporting

#### L5: Consolidated Knowledge

Located in `agentic_core/knowledge/l5_consolidated.py`

```python
from agentic_core.knowledge.l5_consolidated import get_consolidated_knowledge

# Retrieve profile and template
knowledge = get_consolidated_knowledge().search_knowledge(
    query="user profile and cover letter template",
    types=["profile", "template"]
)
```

**Features:**

- Unified access to MEMemory (profiles) and Pinecone (templates)
- Automatic fallback to local storage
- Graceful handling of service failures
- Metadata tracking for sources

#### P10: Shadow Mode

Located in `agentic_core/engines/resume_engine_zlg.py`

```python
from agentic_core.engines.resume_engine_zlg import ShadowModeEngine

# Rewrite draft in shadow mode
shadow = ShadowModeEngine()
result = shadow.rewrite_draft(draft, error_reason)
```

**Features:**

- Simulates rewrite before applying
- LLM-based or rule-based improvements
- Tracks improvements and confidence
- Reduces token cost on failed attempts

## Usage

### Basic Generation

```python
from agentic_core.engines.resume_engine_zlg import ResumeEngineZLG

# Initialize engine
engine = ResumeEngineZLG(output_dir="output")

# Generate cover letter
exit_reason, output_path = engine.generate_cover_letter(
    job_url="https://example.com/job/123",
    user_id="user123"
)

if exit_reason == ExitReason.ZLG_SUCCESS:
    print(f"Success! Cover letter saved to: {output_path}")
else:
    print(f"Failed: {exit_reason.value}")
```

### Custom Configuration

```python
# Custom output directory
engine = ResumeEngineZLG(output_dir="custom/output")

# With custom LLM client
from my_llm import MyLLMClient
engine = ResumeEngineZLG(
    output_dir="output",
    llm_client=MyLLMClient()
)
```

### Exit Codes and Reasons

| Exit Reason | Description | Action |
|-------------|-------------|--------|
| ZLG_SUCCESS | Generated successfully | Output file created |
| P3_INJECTION_BLOCK | Input contained injection | Review input content |
| ZLG_MAX_ATTEMPTS | Failed after 3 rewrites | Review profile/template |
| CRITICAL_ERROR | System error | Check logs |

### Test Coverage

The test suite (`tests/test_resume_engine_zlg.py`) covers:

1. **TC-E2-101**: Standard ZLG Success
2. **TC-E2-102**: P3 Input Injection Block
3. **TC-E2-201**: P4 Hallucination Trigger (ZLG Loop)
4. **TC-E2-202**: Low Quality Trigger (ZLG Loop)
5. **TC-E2-203**: ZLG Max Attempts Failure
6. **TC-E2-301**: L5 Consolidated Knowledge
7. **TC-E2-302**: P5 Activity Logging

### Running Tests

```bash
# Run all tests
python tests/test_resume_engine_zlg.py

# Run specific test
python -m unittest tests.test_resume_engine_zlg.TestStandardZLGSuccess

# Verbose output
python tests/test_resume_engine_zlg.py -v
```

## Logging

### P5 Compliance Logging

All actions are logged to `logs/resume_engine_zlg.log`:

```
2024-12-16 10:00:00 - agentic_core.engines.resume_engine_zlg - INFO - P5_REGISTER: ResumeEngine (PID: 12345)
2024-12-16 10:00:01 - agentic_core.engines.resume_engine_zlg - INFO - ACTION: L1_FETCH_START | {'job_url': 'https://example.com/job'}
2024-12-16 10:00:02 - agentic_core.engines.resume_engine_zlg - INFO - ACTION: P3_START
2024-12-16 10:00:03 - agentic_core.engines.resume_engine_zlg - INFO - ACTION: ZLG_FINAL_SUCCESS | {'output_file': 'output/cover_letter.txt', 'score': 0.85}
```

### Log Levels

- **INFO**: Normal operation flow
- **WARNING**: Recoverable issues (fallbacks used)
- **ERROR**: Failures (injections, max attempts)

## Configuration

### Golden Record (P4)

Location: `config/golden_record.json`

```json
{
  "skills": {
    "python": {"level": "expert", "verified": true},
    "javascript": {"level": "advanced", "verified": true},
    "react": {"level": "intermediate", "verified": true},
    "docker": {"level": "intermediate", "verified": true},
    "aws": {"level": "beginner", "verified": true}
  },
  "experience": {
    "years_total": 5,
    "companies": ["TechCorp", "StartupXYZ"],
    "positions": ["Senior Developer", "Lead Engineer"]
  },
  "education": {
    "degree": "Bachelor of Science",
    "field": "Computer Science",
    "university": "State University"
  }
}
```

### Template Configuration

Templates include:
- Structure (header, greeting, body paragraphs, closing)
- Tone (formal, casual)
- Length preferences
- Field-specific placeholders

### Integration

#### With LLM Providers

```python
# OpenAI integration
from openai import OpenAI
llm_client = OpenAI(api_key="your-key")
engine = ResumeEngineZLG(llm_client=llm_client)

# Anthropic integration
from anthropic import Anthropic
llm_client = Anthropic(api_key="your-key")
engine = ResumeEngineZLG(llm_client=llm_client)
```

### With Memory Systems

```python
# MEMemory integration
from memory_system import MEMemoryClient
memory_client = MEMemoryClient(url="memory-url")

# Pinecone integration
from pinecone import Pinecone
pinecone_client = Pinecone(api_key="your-key")

# Update consolidated knowledge
knowledge = get_consolidated_knowledge(
    memory_client=memory_client,
    pinecone_client=pinecone_client
)
```

### Performance Considerations

#### Optimization Strategies

1. **Caching**: Template and profile caching
2. **Batch Processing**: Multiple generations in parallel
3. **Shadow Mode**: Reduces LLM calls on failures
4. **Fallbacks**: Local storage for service failures

### Monitoring

Track these metrics:
- Success rate (should be >90%)
- Average rewrite attempts
- P3/P4 failure rates
- Generation latency

### Troubleshooting

#### Common Issues

1. **P3 Injection False Positives**
   - Review injection patterns
   - Adjust keyword thresholds
   - Add domain-specific exceptions

2. **P4 Validation Failures**
   - Update golden record
   - Check skill name matching
   - Review experience rules

3. **Low Quality Scores**
   - Adjust scoring thresholds
   - Update template structure
   - Review draft generation logic

4. **Max Attempts Reached**
   - Check profile completeness
   - Verify template quality
   - Review job description parsing

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('agentic_core.engines.resume_engine_zlg').setLevel(logging.DEBUG)

# Run with debug
engine = ResumeEngineZLG(output_dir="debug/output")
exit_reason, output_path = engine.generate_cover_letter("test-url")
```

## Future Enhancements

### Planned Features

1. **Multi-language Support**
   - Language detection
   - Translation capabilities
   - Culture-specific templates

2. **Advanced Personalization**
   - Company research integration
   - Hiring manager analysis
   - Culture matching

3. **Quality Improvements**
   - A/B testing framework
   - User feedback integration
   - Adaptive scoring

4. **Performance**
   - Async generation
   - Streaming responses
   - Edge deployment

### Extension Points

- Custom security rules
- Additional validation gates
- Alternative LLM integrations
- Custom quality metrics

## Security Considerations

### Data Protection

- PII detection and scrubbing
- Secure storage of profiles
- Audit logging for compliance

### Threat Mitigation

- Prompt injection prevention
- Output validation
- Rate limiting
- Access controls

## Conclusion

The Resume Engine ZLG provides a robust, secure, and self-correcting system for document generation. By consolidating security protocols and knowledge access, it ensures consistent quality while maintaining flexibility for customization and extension.
