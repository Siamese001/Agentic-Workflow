# K.2.5 Deep Research Protocol

## Overview

The **K.2.5 Deep Research Protocol** is a multi-hop research system designed to extract high-density competitive intelligence for the resume generation workflow. It enforces a strict three-layer research methodology that goes beyond surface-level summarization to capture financial metrics, technical implementations, and organizational leadership details.

## Architecture

### Core Components

1. **Data Models** (`apps_rg/L1_cognition/k2_5_deep_research_models.py`)
   - `DeepResearchOutput` - Main output schema
   - `StrategicLayer` - Financial metrics and strategic thesis
   - `TechnicalLayer` - Technology implementations and infrastructure
   - `LeadershipLayer` - Executive profiles and organizational mapping
   - `CitationMap` - Source tracking and attribution

2. **Agent** (`apps_rg/L1_cognition/k2_5_deep_research_agent.py`)
   - `K25DeepResearchAgent` - Main orchestrator
   - Executes 3-hop research protocol
   - Generates structured prompts
   - Assembles multi-layer research output

3. **Integrity Gate** (`apps_rg/L2_execution/integrity_gate_executor.py`)
   - `IntegrityGateExecutor` - Validation engine
   - Checks for unbound metrics, fluff language, orphaned claims
   - Calculates depth score (minimum 0.7 required)
   - Enforces citation coverage requirements

4. **Configuration** (`apps_rg/L3_orchestration/resume_orchestration_config.py`)
   - K.2.5 reasoning config: `rag_hops=3`, `rag_total_calls=24`
   - 4 validation gates for deep research integrity
   - Strict claim verification mode

## Multi-Hop Research Protocol

### Phase 1: Financial & Strategic Hard-Anchoring (Hop 1)

**Query Focus:** 10-K/Q filings, earnings calls, investor letters

**Mandatory Data Points:**
- Revenue/EBITDA/Net Income with YoY comparisons
- Specific cost-reduction drivers
- Strategic thesis or business model pivot

**Example Output:**
```
Q2 2025 Revenue: $3.3B (+25% YoY)
GAAP Net Income: $285M (first profitable quarter)
Insurance expense decreased as % of GOV
```

### Phase 2: Technical & Product Implementation (Hop 2)

**Query Focus:** Engineering blogs, tech stack specs, patent filings

**Mandatory Data Points:**
- Specific model architectures/algorithms
- Infrastructure stack components
- Quantified performance gains

**Example Output:**
```
Gated Mixture-of-Experts architecture for ETA predictions
20% improvement in delivery time accuracy
Kubernetes orchestration with PyTorch ML platform
```

### Phase 3: Organizational & Leadership Mapping (Hop 3)

**Query Focus:** Leadership bios, org charts, LinkedIn profiles

**Mandatory Data Points:**
- Key executives with full titles
- Domain ownership per executive
- Strategic initiatives mapped to leaders

**Example Output:**
```
Stanley Tang (Head of DoorDash Labs) - Autonomous delivery initiatives
Ravi Inukonda (CFO) - Risk & Insurance function, margin expansion
Sudeep Das (Head of ML for New Verticals) - Personalization algorithms
```

## Validation Gates

### VG_K2_5_DEEP_RESEARCH_INTEGRITY

**Execution Point:** POST_K2_5_GENERATION
**Blocking:** True
**Severity:** CRITICAL

**Checks:**
- `no_unbound_metrics` - All metrics must have source citations
- `no_fluff_language` - Fluff words must be followed by technical nouns
- `no_orphaned_claims` - All claims linked to tech/executives
- `minimum_3_citations` - At least 3 sources required
- `depth_score_min_0_7` - Minimum depth score of 0.7

### VG_K2_5_FINANCIAL_LAYER_COMPLETENESS

**Checks:**
- Minimum 2 financial metrics
- All metrics have citations
- Metrics have specific values (not vague)
- YoY comparisons present

### VG_K2_5_TECHNICAL_LAYER_SPECIFICITY

**Checks:**
- Minimum 2 specific technologies
- Implementation details present
- Performance gains quantified
- No generic tech descriptions

### VG_K2_5_LEADERSHIP_MAPPING

**Checks:**
- Minimum 2 executives identified
- Executives have domain ownership
- Initiatives mapped to responsible leaders

## Negative Constraints

The Integrity Gate will **REJECT** output containing:

1. **Unbound Metrics:** Numbers without source citations
2. **Fluff Language:** Words like "cutting-edge", "innovative" without technical nouns
3. **Orphaned Claims:** Initiatives not linked to specific technologies or executives
4. **Insufficient Citations:** Fewer than 3 sources
5. **Low Depth Score:** Score below 0.7 threshold

## Depth Score Calculation

```python
depth_score = average([
    financial_score,    # min(metric_count / 4.0, 1.0)
    technical_score,    # min(tech_count / 3.0, 1.0)
    leadership_score,   # min(exec_count / 3.0, 1.0)
    citation_score,     # min(citation_count / 5.0, 1.0)
    thesis_score        # 1.0 if len(thesis) > 50 else 0.5
])
```

**Minimum Required:** 0.7

## Usage Example

### Basic Usage

```python
from apps_rg.L1_cognition.k2_5_deep_research_agent import create_k25_research_agent

# Create agent
agent = create_k25_research_agent(
    company_name="DoorDash",
    company_url="https://www.doordash.com"
)

# Generate research prompt
prompt = agent.generate_research_prompt()

# Execute research (returns DeepResearchOutput)
research_output = agent.execute_research()

# Output is automatically validated by integrity gate
print(f"Depth Score: {research_output.depth_score}")
```

### Creating Research Output Manually

```python
from apps_rg.L1_cognition.k2_5_deep_research_models import (
    DeepResearchOutput,
    StrategicLayer,
    TechnicalLayer,
    LeadershipLayer,
    FinancialMetric,
    TechnicalImplementation,
    ExecutiveProfile,
    CitationMap,
)

# Build strategic layer
strategic_layer = StrategicLayer(
    core_thesis="Company strategic positioning statement",
    financial_proof_points=[
        FinancialMetric(
            metric_name="Q2 2025 Revenue",
            value="$3.3B",
            period="Q2 2025",
            yoy_change="+25%",
            source_citation="cite_1"
        )
    ]
)

# Build technical layer
technical_layer = TechnicalLayer(
    key_technologies=[
        TechnicalImplementation(
            technology_name="Specific Technology",
            implementation_details="Detailed implementation description",
            performance_gain="20% improvement",
            source_citation="cite_2"
        )
    ]
)

# Build leadership layer
leadership_layer = LeadershipLayer(
    key_executives=[
        ExecutiveProfile(
            name="Executive Name",
            title="Title",
            ownership="Domain ownership description"
        )
    ]
)

# Build citation map
citation_map = CitationMap()
citation_map.add_citation("cite_1", "https://source1.com")
citation_map.add_citation("cite_2", "https://source2.com")

# Assemble output
output = DeepResearchOutput(
    company_name="Company Name",
    strategic_layer=strategic_layer,
    technical_layer=technical_layer,
    leadership_layer=leadership_layer,
    citation_map=citation_map
)

# Validate
from apps_rg.L2_execution.integrity_gate_executor import validate_research_output
result = validate_research_output(output)
print(f"Passed: {result.passed}, Depth Score: {result.depth_score}")
```

## DoorDash Benchmark

The DoorDash Executive Summary serves as the **gold standard** for K.2.5 output quality. See:
- `config/prompts/doordash_benchmark_example.md` - Detailed benchmark
- `examples/k2_5_deep_research_example.py` - Runnable example

**Benchmark Metrics:**
- 4 financial metrics with YoY comparisons
- 3 specific technologies with quantified gains
- 4 executives with domain ownership
- 5 citations across financial, technical, organizational domains
- Depth score: 1.0 (perfect)

## Integration with Resume Workflow

The K.2.5 agent integrates into the resume generation pipeline at the **Competitive Positioning** phase:

```
K.0 (Job Description)
  → K.1 (Executive Summary)
  → K.2 (Thematic Analysis)
  → **K.2.5 (Competitive Intelligence)** ← Deep Research Protocol
  → K.3 (Role Mapping)
  → K.4-K.12 (Content Generation)
```

**Configuration:**
- `rag_type`: AGENTIC (full multi-hop)
- `rag_hops`: 3 (financial → technical → leadership)
- `rag_total_calls`: 24 (8 calls per hop)
- `claim_verification_mode`: STRICT
- `self_consistency`: 6 (highest in workflow)

## Prompt Templates

### Main Protocol
`config/prompts/k2_5_deep_research_mandate.md`

### Benchmark Example
`config/prompts/doordash_benchmark_example.md`

## Files Created

1. **Models:** `apps_rg/L1_cognition/k2_5_deep_research_models.py`
2. **Agent:** `apps_rg/L1_cognition/k2_5_deep_research_agent.py`
3. **Validator:** `apps_rg/L2_execution/integrity_gate_executor.py`
4. **Config Updates:** `apps_rg/L3_orchestration/resume_orchestration_config.py`
5. **Prompts:** `config/prompts/k2_5_deep_research_mandate.md`
6. **Benchmark:** `config/prompts/doordash_benchmark_example.md`
7. **Example:** `examples/k2_5_deep_research_example.py`
8. **Documentation:** `docs/k2_5_deep_research_protocol.md`

## Testing

Run the example:
```bash
cd /c/Git/Agentic-Workflow
python examples/k2_5_deep_research_example.py
```

Expected output:
- Generated research prompt
- DoorDash benchmark validation
- Integrity gate results (all checks passed)
- JSON output structure

## Anti-Patterns

### ❌ Surface-Level Summary
```
"DoorDash is a leading food delivery company that uses innovative
technology and has a strong leadership team driving growth."
```

### ✅ Deep Research Output
```
"DoorDash achieved Q2 2025 GAAP profitability ($285M net income)
through logistics optimization powered by Gated MoE models (20% ETA
accuracy improvement) and autonomous delivery pilots (Dot robot),
led by Stanley Tang (Labs) and Ravi Inukonda (CFO/Risk)."
```

## Key Differences from Standard RAG

| Standard RAG | K.2.5 Deep Research |
|--------------|---------------------|
| Single-hop retrieval | 3-hop multi-phase protocol |
| Generic summaries | Hard metrics with citations |
| "They use AI" | "Gated MoE architecture, 20% accuracy gain" |
| "Strong leadership" | "Stanley Tang (Labs) - Autonomous delivery" |
| No validation | Integrity gate with depth scoring |
| Fluff language allowed | Fluff words must precede technical nouns |

## Future Enhancements

1. **RAG Integration:** Connect to live data sources (SEC EDGAR, engineering blogs)
2. **LLM Execution:** Implement actual LLM calls for hop execution
3. **Caching:** Cache research results per company
4. **Incremental Updates:** Refresh only stale data layers
5. **Multi-Company:** Batch research across multiple companies
6. **Competitive Matrix:** Generate side-by-side comparisons

## References

- Resume Orchestration Config: `apps_rg/L3_orchestration/resume_orchestration_config.py:201-213`
- Validation Gates: Lines 464-519
- K.2.5 Reasoning Config: `rag_hops=3`, `rag_total_calls=24`, `claim_verification_mode=STRICT`
