# V5 Instructional Injection Framework

## Overview

The V5 Instructional Injection Framework is a comprehensive 6-layer governance system for AI prompt engineering, providing 30 specialized injection prompts organized into hierarchical layers for optimal control, safety, and performance.

## Architecture

### 6-Layer Structure

1. **Framing Layer** (5 prompts) - Establish objectives, constraints, and operational parameters
2. **Context Layer** (5 prompts) - Optimize input processing and context management  
3. **Reasoning Layer** (5 prompts) - Enhance logical reasoning and decision-making processes
4. **Tooling Layer** (5 prompts) - Coordinate tool usage and integration workflows
5. **Safety Layer** (5 prompts) - Enforce security, ethical, and compliance safeguards
6. **Output Layer** (5 prompts) - Standardize output format and quality controls

### File Structure

```yaml
injections/
├── README.md                           # This documentation
├── injections_index.yaml               # Complete mapping of all 30 prompts
├── framing.yaml                        # Framing layer injections (1-5)
├── context_engineering.yaml           # Context layer injections (6-10)
├── reasoning.yaml                      # Reasoning layer injections (11-15)
├── tool_use.yaml                       # Tooling layer injections (16-20)
├── safety.yaml                         # Safety layer injections (21-25)
├── output_governance.yaml              # Output layer injections (26-30)
└── constraints.yaml                    # Additional constraint definitions
```

## Quick Start

### Using the Framework

1. **Reference the Index**: Start with `injections_index.yaml` to understand available prompts
2. **Select Layer**: Choose appropriate layer(s) based on your use case
3. **Apply Injections**: Use the prompt templates from the relevant YAML files
4. **Follow Guidelines**: Adhere to usage contexts and success criteria

### Common Use Cases

#### Resume Optimization

```yaml
Recommended Injections: [1, 2, 4, 6, 7, 9, 11, 13, 14, 17, 19, 21, 23, 26, 27]
Priority: Global Goal-State, Success Criteria, Safety Layer
```

#### Outreach Strategy

```yaml
Recommended Injections: [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 21, 23, 26, 28]
Priority: Global Goal-State, Success Criteria, Safety Layer
```

#### Security-Sensitive Operations

```yaml
Recommended Injections: [3, 4, 5, 6, 21, 22, 23, 24, 25, 26, 29]
Priority: All Safety Layer Injections (21-25)
```

## Layer Details

### Framing Layer (Injections 1-5)

- **1. Global Goal-State**: Anchor reasoning to clear objectives
- **2. Success Criteria**: Define quality thresholds upfront
- **3. Task Mode Declaration**: Specify cognitive mode (analytical, synthesis, etc.)
- **4. Scope & Boundaries**: State constraints and forbidden behaviors
- **5. Cost/Latency Targets**: Guide efficient reasoning under limits

### Context Layer (Injections 6-10)

- **6. Untrusted Block Wrapping**: Encapsulate user input as neutral data
- **7. Canonicalization**: Normalize formatting and command sequences
- **8. Context Pruning**: Filter irrelevant material for token efficiency
- **9. Cross-Field Consistency**: Verify alignment across different fields
- **10. Structured Context Ordering**: Present inputs in deterministic sequence

### Reasoning Layer (Injections 11-15)

- **11. Failure Anticipation**: Predict and mitigate potential mistakes
- **12. Multi-Branch Thinking**: Generate and evaluate multiple reasoning paths
- **13. Confidence & Uncertainty**: Provide numeric confidence with justification
- **14. Reason-Then-Answer**: Think privately before structured output
- **15. Error Simulation**: Test and correct outputs before finalizing

### Tooling Layer (Injections 16-20)

- **16. Tool-Feedback Loop**: Incorporate tool outputs into subsequent steps
- **17. Evidence Binding**: Ground claims to verified evidence with citations
- **18. Cross-Tool Reconciliation**: Resolve conflicting tool outputs
- **19. Shadow Validation**: Run internal sanity checks before output
- **20. Model-Switch Aware**: Adapt instructions for different model types

### Safety Layer (Injections 21-25) - **CRITICAL**

- **21. Prompt-Injection Shielding**: Anti-jailbreak safeguards
- **22. Data vs Instruction Separation**: Distinguish data from directives
- **23. Constitutional Guardrails**: Enforce ethics and safety principles
- **24. Delegation Guardrails**: Prevent unauthorized decision overrides
- **25. Expanded Adversarial Mode**: Detect manipulative patterns

### Output Layer (Injections 26-30)

- **26. Strict JSON-Only Output**: Schema-compliant JSON without extra text
- **27. Schema Enforcement & Examples**: Follow schema with example guidance
- **28. Stability Contracts**: Preserve field order and naming consistency
- **29. Error Envelope Normalization**: Standardize error responses
- **30. Minimality Constraints**: Limit output size for clarity

## Governance & Compliance

### Mandatory Requirements

- **Safety Layer (21-25)**: All injections are mandatory for compliance
- **Documentation**: All usage must be documented and tracked
- **Audit Trail**: Maintain complete audit logs for injection usage

### Recommended Practices

- **Layer Dependencies**: Follow recommended activation order (Framing → Context → Reasoning → Tooling → Safety → Output)
- **Quality Standards**: Validate outputs against success criteria
- **Monitoring**: Track injection effectiveness and performance

### Compliance Frameworks

- **GDPR**: Data protection and privacy compliance
- **SOC2**: Security and operational controls
- **HIPAA**: Healthcare data protection (if applicable)
- **ISO27001**: Information security management
- **NIST CSF**: Cybersecurity framework alignment

## Integration with Registry

The framework is fully integrated with the prompt governance registry:

1. **prompt_index.yaml**: Updated with v5 framework reference
2. **injections_index.yaml**: Complete mapping and metadata
3. **Component Registry**: Includes 6-layer structure
4. **Version Control**: Semantic versioning for all injections

## Maintenance & Updates

### Review Schedule

- **Quarterly**: Full framework review and optimization
- **Monthly**: Security layer updates and threat assessment
- **On-Demand**: Critical security updates and compliance changes

### Update Triggers

- Security incidents or vulnerabilities
- Compliance requirement changes
- Performance degradation or user feedback
- New regulatory requirements

## Usage Examples

### Basic Implementation

```yaml
# Select injections for resume optimization
selected_injections:
  - id: 1  # Global Goal-State
  - id: 2  # Success Criteria
  - id: 21 # Prompt-Injection Shielding
  - id: 23 # Constitutional Guardrails

# Apply in sequence
activation_order: [1, 2, 21, 23]
```

### Advanced Configuration

```yaml
# Full workflow with custom parameters
workflow:
  framing: [1, 2, 3, 4, 5]
  context: [6, 7, 8, 9, 10]
  reasoning: [11, 12, 13, 14, 15]
  tooling: [16, 17, 18, 19, 20]
  safety: [21, 22, 23, 24, 25]  # Always active
  output: [26, 27, 28, 29, 30]
```

## Support & Documentation

- **Index File**: `injections_index.yaml` for complete reference
- **Registry Integration**: See `../registry/prompt_index.yaml`
- **Governance Policies**: See `../governance/` directory
- **Compliance Mapping**: See `../governance/compliance_mapping.yaml`

## Version History

- **v1.0**: Initial framework implementation
- **v5.0**: Current version with 30 injections across 6 layers
- **Future**: Planned enhancements and additional specialized layers

---

**Note**: This framework is designed for enterprise-grade AI prompt governance. Always ensure compliance with your organization's security and regulatory requirements when implementing these injections.
