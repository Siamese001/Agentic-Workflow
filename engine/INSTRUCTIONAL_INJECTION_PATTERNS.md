# Shared Engine Ops — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Module Focus:** Engine operations shared across cognition, execution, and aggregation

---

## Applicable Patterns for Shared Engine Ops

### Reasoning Layer (Patterns 11-15)

| # | Instruction Type | Engine Ops Application |
|---|------------------|----------------------|
| **11** | Failure Anticipation | Predict operation failures |
| **12** | Self-Consistency | Multi-branch aggregation |
| **13** | Confidence & Uncertainty | Score confidence |
| **14** | Reason-Then-Answer | Structured reasoning |
| **15** | Error Simulation | Pre-validate operations |

### Tooling Layer (Patterns 16-20)

| # | Instruction Type | Engine Ops Application |
|---|------------------|----------------------|
| **16** | Tool-Feedback Loop | Incorporate tool results |
| **17** | Evidence Binding | Bind to sources |
| **18** | Cross-Tool Reconciliation | Resolve conflicts |
| **19** | Shadow Validation | Sanity check results |
| **20** | Model-Switch Aware | Adapt to model type |

---

## Module-Specific Guidelines

### aggregation_ops/

Apply patterns: 12, 18

- Multi-branch voting for best result
- Reconcile conflicting sources

### cognition_ops/

Apply patterns: 11, 13, 14

- Anticipate understanding failures
- Provide confidence scores
- Reason-then-answer structure

### embedding_ops/

Apply patterns: 17, 19

- Bind embeddings to source text
- Validate similarity scores

### safety_ops/

Apply patterns: 21, 22, 25

- Prompt injection shielding
- Data/instruction separation
- Adversarial detection

### scoring_ops/

Apply patterns: 13, 19

- Confidence scoring
- Shadow validation of scores

### inspection_ops/

Apply patterns: 9, 15

- Cross-field consistency
- Error simulation

### tool_ops/

Apply patterns: 16, 18, 20

- Tool feedback integration
- Cross-tool reconciliation
- Model-aware instructions

### update_ops/

Apply patterns: 28, 29

- Stability contracts for updates
- Error envelope normalization

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Master index: `INSTRUCTIONAL_INJECTION_PATTERNS_INDEX.md`
