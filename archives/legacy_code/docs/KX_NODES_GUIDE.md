# K.X Nodes Guide - Knowledge Extraction Nodes

Complete guide for using K.X (Knowledge Extraction) nodes extracted from legacy resume and outreach engines.

## Overview

K.X nodes represent structured knowledge extraction and generation steps with:
- **Configurable reasoning strategies** (CoT, ToT, Hybrid)
- **RAG integration** with source weighting
- **Validation rules** for quality assurance
- **Decoding parameters** for fine-tuned generation
- **Metadata** for workflow orchestration

---

## Architecture

### Resume Engine K.X Nodes (K.0 - K.11)

**Header Nodes (K.0):**
- `K.0_Name` - Candidate name
- `K.0_Headline` - Professional headline
- `K.0_Contact` - Contact information

**Content Nodes (K.1 - K.11):**
- `K.1_Executive_Summary` - 3-4 sentence value proposition
- `K.2_Unify_Overview` - Company overview (Unify)
- `K.2_Unify_Bullets` - Achievement bullets (Unify)
- `K.3_IBM_Overview` - Company overview (IBM)
- `K.3_IBM_Bullets` - Achievement bullets (IBM)
- `K.4_TraderSense_Narrative` - Experience narrative
- `K.5_EY_Narrative` - Experience narrative (EY)
- `K.6_Early_Career_Narrative` - Early career summary
- `K.7_Education` - Education details
- `K.8_Certifications` - Certifications and credentials
- `K.9_Competencies` - Strategic and technical competencies
- `K.10_Skills` - Skills list
- `K.11_Cover_Letter` - Cover letter generation

### Outreach Engine K.X Nodes (K.1 - K.7)

**Routing & Analysis (K.1 - K.2):**
- `K.1_Message_Type_Routing` - Channel classification and routing
- `K.2_Recipient_Analysis` - Persona and context extraction

**Content Generation (K.3 - K.6):**
- `K.3_Message_Body` - Personalized message content
- `K.4_Value_Proposition` - Compelling offer articulation
- `K.5_CTA_Generation` - Call-to-action with temporal framing
- `K.6_Salutation_Signature` - Professional formatting

**Assembly (K.7):**
- `K.7_Final_Assembly` - Message composition and validation

**Connection Request Variants:**
- `CONNECTION_REQ_K.3_COMPRESSED` - 280 char compressed message
- `CONNECTION_REQ_K.5_MICRO` - 5 word micro CTA

---

## Usage

### Basic K.X Node Retrieval

```python
from runtime.shared import get_resume_kx_node, get_outreach_kx_node

# Get resume node
summary_config = get_resume_kx_node("K.1_Executive_Summary")
print(f"Node: {summary_config.element}")
print(f"Strategy: {summary_config.reasoning_strategy.value}")
print(f"Max words: {summary_config.max_words}")

# Get outreach node
message_config = get_outreach_kx_node("K.3_Message_Body")
print(f"RAG enabled: {message_config.rag_config.enabled}")
print(f"Max chars: {message_config.max_chars}")

# Get connection request variant
compressed = get_outreach_kx_node("CONNECTION_REQ_K.3_COMPRESSED", connection_request=True)
print(f"Mode: {compressed.metadata.get('mode')}")
```

### Execute K.X Node

```python
from runtime.shared import execute_kx_node, create_agent_executor, Provider

# Create agent executor
executor = create_agent_executor(
    provider=Provider.OPENAI,
    model="gpt-4o",
    temperature=0.3,
)

# Prepare source data
source_data = {
    "query": "executive summary",
    "company": "Unify",
    "role": "Senior Software Engineer",
    "achievements": [
        "Led team of 5 engineers",
        "Improved system performance by 40%",
        "Reduced deployment time from 2 hours to 15 minutes"
    ],
}

# Execute K.X node
result = execute_kx_node(
    node_key="K.1_Executive_Summary",
    agent_executor=executor,
    source_data=source_data,
    engine="resume",
)

print(f"Generated content: {result.content}")
print(f"Validation passed: {result.metadata['validation_passed']}")
print(f"Tokens used: {result.usage['total_tokens']}")
```

### Execute with RAG

```python
from runtime.shared import (
    execute_kx_node,
    create_agent_executor,
    get_vector_store,
    VectorStoreProvider,
)

# Setup vector store
vector_store = get_vector_store(VectorStoreProvider.CHROMA)

# Execute with RAG
result = execute_kx_node(
    node_key="K.2_Unify_Bullets",
    agent_executor=executor,
    source_data={
        "query": "achievement bullets for Unify",
        "role": "Senior Engineer",
        "projects": ["API redesign", "Performance optimization"],
    },
    vector_store=vector_store,
    engine="resume",
)

print(f"RAG sources used: {len(result.rag_sources)}")
for i, source in enumerate(result.rag_sources[:3]):
    print(f"Source {i+1}: {source['metadata'].get('source_type')}")
    print(f"Weight: {source['weight']}")
```

### Outreach Message Generation

```python
from runtime.shared import execute_kx_node, create_agent_executor

executor = create_agent_executor(provider=Provider.OPENAI)

# K.1: Message Type Routing
routing_result = execute_kx_node(
    node_key="K.1_Message_Type_Routing",
    agent_executor=executor,
    source_data={
        "recipient_title": "VP of Engineering",
        "company": "TechCorp",
        "connection_status": "2nd degree",
    },
    engine="outreach",
)

# K.3: Message Body
message_result = execute_kx_node(
    node_key="K.3_Message_Body",
    agent_executor=executor,
    source_data={
        "recipient_name": "John Smith",
        "recipient_title": "VP of Engineering",
        "company": "TechCorp",
        "context": "Applying for Senior Engineer role",
        "message_type": "EXECUTIVE",
    },
    engine="outreach",
)

print(f"Message: {message_result.content}")

# K.5: CTA Generation
cta_result = execute_kx_node(
    node_key="K.5_CTA_Generation",
    agent_executor=executor,
    source_data={
        "context": "Request for informational interview",
        "timeline": "this week",
    },
    engine="outreach",
)

print(f"CTA: {cta_result.content}")
```

### Connection Request (Compressed Mode)

```python
# Use compressed variant for connection requests
compressed_result = execute_kx_node(
    node_key="CONNECTION_REQ_K.3_COMPRESSED",
    agent_executor=executor,
    source_data={
        "recipient_name": "Jane Doe",
        "common_interest": "AI/ML",
        "job_application": {
            "job_title": "ML Engineer",
            "req_number": "12345",
        },
    },
    engine="outreach",
)

print(f"Compressed message ({len(compressed_result.content)} chars): {compressed_result.content}")

# Micro CTA for connection requests
micro_cta = execute_kx_node(
    node_key="CONNECTION_REQ_K.5_MICRO",
    agent_executor=executor,
    source_data={},
    engine="outreach",
)

print(f"Micro CTA: {micro_cta.content}")
```

---

## Configuration Details

### Reasoning Strategies

**Chain of Thought (CoT):**
```python
config = get_resume_kx_node("K.0_Name")
assert config.reasoning_strategy == ReasoningStrategy.COT
# Simple step-by-step reasoning
```

**Tree of Thought (ToT):**
```python
config = get_resume_kx_node("K.1_Executive_Summary")
assert config.reasoning_strategy == ReasoningStrategy.HYBRID_COT_TOT
assert config.tot_branches == 5  # Explore 5 different approaches
assert config.tot_depth == 3     # 3 levels deep
```

**Self-Consistency:**
```python
config = get_resume_kx_node("K.2_Unify_Bullets")
assert config.self_consistency_runs == 4  # Generate 4 times, pick best
```

### RAG Configuration

**Source Weighting:**
```python
config = get_resume_kx_node("K.2_Unify_Bullets")
rag_config = config.rag_config

# Premium sources (1.5x weight)
assert rag_config.source_weighting["podcast_appearance"] == 1.5
assert rag_config.source_weighting["video_interview"] == 1.5

# Primary sources (1.2x weight)
assert rag_config.source_weighting["authored_blog_post"] == 1.2

# Secondary sources (1.0x weight)
assert rag_config.source_weighting["news_article"] == 1.0

# Low signal (0.5x weight)
assert rag_config.source_weighting["generic_bio"] == 0.5
```

**Retrieval Parameters:**
```python
config = get_outreach_kx_node("K.1_Message_Type_Routing")
assert config.rag_config.min_retrievers == 6  # Minimum sources
assert config.rag_config.max_retrievers == 6  # Maximum sources
assert config.rag_config.hops == 3            # Multi-hop retrieval
```

### Decoding Parameters

```python
config = get_resume_kx_node("K.1_Executive_Summary")
params = config.decoding_params

print(f"Temperature: {params.temperature}")      # 0.3 (focused)
print(f"Top-p: {params.top_p}")                  # 0.85
print(f"Top-k: {params.top_k}")                  # 40
print(f"Min-p: {params.min_p}")                  # 0.04
print(f"Repetition penalty: {params.repetition_penalty}")  # 1.1
```

### Validation Rules

```python
config = get_resume_kx_node("K.2_Unify_Bullets")

# Check validation rules
assert "bullet_provenance_check" in config.validation_rules
assert "hallucination_check" in config.validation_rules
assert "redundancy_check" in config.validation_rules
assert "punctuation_check" in config.validation_rules

# Validation results after execution
result = execute_kx_node(...)
for validation in result.validation_results:
    print(f"Rule: {validation['rule']}")
    print(f"Passed: {validation['passed']}")
    print(f"Message: {validation['message']}")
```

---

## Advanced Usage

### Custom K.X Node Registration

```python
from runtime.shared import (
    get_kx_registry,
    KNodeConfig,
    KNodeType,
    ReasoningStrategy,
    RAGConfig,
    DecodingParams,
)

registry = get_kx_registry()

# Create custom node
custom_node = KNodeConfig(
    node_id="K.12",
    element="Custom Portfolio Section",
    node_type=KNodeType.RESUME_SECTION,
    reasoning_strategy=ReasoningStrategy.HYBRID_COT_TOT,
    rag_config=RAGConfig(
        enabled=True,
        min_retrievers=4,
        hops=2,
    ),
    decoding_params=DecodingParams(
        temperature=0.4,
        top_p=0.9,
    ),
    tot_branches=4,
    self_consistency_runs=2,
    max_words=200,
    structure_template="Portfolio highlights with project links",
    validation_rules=["grounding_check", "link_validation"],
    metadata={"section": "portfolio", "optional": True},
)

# Register custom node
registry.register_custom_node("K.12_Portfolio", custom_node, engine="resume")

# Use custom node
result = execute_kx_node(
    node_key="K.12_Portfolio",
    agent_executor=executor,
    source_data={"projects": [...]},
    engine="resume",
)
```

### Workflow Integration

```python
from runtime.shared import WorkflowOrchestrator, Provider

# Create workflow with K.X nodes
orchestrator = WorkflowOrchestrator("resume-gen-001", Provider.OPENAI)

def generate_summary_hop(context):
    """Generate executive summary using K.X node."""
    result = execute_kx_node(
        node_key="K.1_Executive_Summary",
        agent_executor=context.workflow_context.agent_executor,
        source_data=context.get_input("candidate_data"),
        vector_store=context.workflow_context.vector_store,
        engine="resume",
    )
    context.set_output("executive_summary", result.content)
    context.set_output("summary_validation", result.validation_results)

def generate_bullets_hop(context):
    """Generate experience bullets using K.X node."""
    result = execute_kx_node(
        node_key="K.2_Unify_Bullets",
        agent_executor=context.workflow_context.agent_executor,
        source_data=context.get_input("experience_data"),
        vector_store=context.workflow_context.vector_store,
        engine="resume",
    )
    context.set_output("experience_bullets", result.content)

# Register hops
orchestrator.register_hop("summary", generate_summary_hop)
orchestrator.register_hop("bullets", generate_bullets_hop, dependencies=["summary"])

# Execute workflow
outputs = orchestrator.execute(initial_inputs={
    "candidate_data": {...},
    "experience_data": {...},
})

print(outputs["executive_summary"])
print(outputs["experience_bullets"])
```

### Batch K.X Node Execution

```python
from runtime.shared import get_kx_registry, execute_kx_node

registry = get_kx_registry()

# Get all resume section nodes
section_nodes = registry.get_nodes_by_type(KNodeType.RESUME_SECTION)

# Execute all sections
results = {}
for node_key, config in section_nodes.items():
    if config.metadata.get("required"):
        result = execute_kx_node(
            node_key=node_key,
            agent_executor=executor,
            source_data=source_data_map.get(node_key, {}),
            vector_store=vector_store,
            engine="resume",
        )
        results[node_key] = result.content

print(f"Generated {len(results)} resume sections")
```

---

## Validation Rules Reference

### Resume Engine Validation Rules

- `grounding_check` - Verify content is grounded in source data
- `hallucination_check` - Detect and prevent hallucinations
- `bullet_provenance_check` - Verify bullet points have source attribution
- `redundancy_check` - Detect and remove redundant content
- `punctuation_check` - Validate punctuation and formatting
- `voice_tense_check` - Ensure consistent voice and tense
- `word_count_range` - Validate word count constraints
- `competency_word_count_balance` - Balance competency section length
- `controlled_vocabulary` - Use approved terminology
- `factual_accuracy` - Verify factual correctness
- `date_format` - Validate date formatting

### Outreach Engine Validation Rules

- `message_type_confirmation` - Confirm message type routing
- `persona_extraction` - Validate persona analysis
- `context_grounding` - Verify context is grounded
- `resume_fact_verification` - Cross-check with resume facts
- `temporal_accuracy` - Validate temporal references
- `synthesis_phase_check` - Verify synthesis quality
- `value_clarity` - Ensure value proposition is clear
- `date_specific_cta_rules` - Validate CTA temporal framing
- `temporal_framing` - Check time-based language
- `requires_sender_profile` - Validate sender information
- `final_checks` - Comprehensive final validation
- `character_limit` - Enforce character limits
- `professional_tone` - Validate professional language
- `no_hallucinations` - Final hallucination check

---

## Best Practices

1. **Use appropriate reasoning strategies**
   - CoT for simple extractions
   - Hybrid CoT/ToT for complex generation
   - Self-consistency for critical content

2. **Enable RAG for content-rich nodes**
   - Executive summaries
   - Experience bullets
   - Message personalization

3. **Configure source weighting**
   - Prioritize podcast/video content (1.5x)
   - Use authored content (1.2x)
   - Deprioritize generic bios (0.5x)

4. **Validate all outputs**
   - Check validation results
   - Enforce character/word limits
   - Verify grounding and accuracy

5. **Cache expensive operations**
   - Cache RAG retrievals
   - Cache validation results
   - Reuse embeddings

6. **Monitor token usage**
   - Track usage per node
   - Optimize temperature/top_p
   - Use appropriate models

---

## Troubleshooting

### K.X Node Not Found

```python
config = get_resume_kx_node("K.99_NonExistent")
if config is None:
    print("Node not found - check node key")
    print("Available nodes:", get_kx_registry().list_resume_nodes())
```

### Validation Failures

```python
result = execute_kx_node(...)

failed_validations = [
    v for v in result.validation_results
    if not v.get("passed", False)
]

if failed_validations:
    print("Validation failures:")
    for v in failed_validations:
        print(f"  - {v['rule']}: {v['message']}")
```

### RAG Not Working

```python
config = get_resume_kx_node("K.1_Executive_Summary")

if not config.rag_config.enabled:
    print("RAG is disabled for this node")
elif vector_store is None:
    print("Vector store not provided")
else:
    print(f"RAG configured: {config.rag_config.min_retrievers} retrievers, {config.rag_config.hops} hops")
```

---

## Migration from Legacy

K.X nodes were extracted from:
- **Resume Engine**: `archives/legacy_resume_gen/` (v7.0+ configs)
- **Outreach Engine**: `archives/legacy_lic/` (v7.4+ configs)

All K.X node configurations preserve:
- Original reasoning strategies
- RAG configurations
- Validation rules
- Decoding parameters
- Metadata and constraints

Use `get_kx_registry()` to access all extracted nodes in the unified agentic workflow.
