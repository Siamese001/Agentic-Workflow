# L1 Cognition — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Layer Focus:** Framing, Context, and Reasoning patterns for L1 planning operations

---

## Applicable Patterns for L1 Cognition

L1 Cognition handles **planning and understanding** — these patterns are critical:

### Framing Layer (Patterns 1-5)

| # | Instruction Type | L1 Application |
|---|------------------|----------------|
| **1** | Global Goal-State Injection | Anchor all L1 planning to the user's overarching objective |
| **2** | Success Criteria Injection | Define explicit quality thresholds for plan outputs |
| **3** | Task Mode Declaration | Specify cognitive mode: analytical, synthesis, adversarial, meta |
| **4** | Scope & Boundaries Injection | State exact constraints and forbidden behaviors for planning |
| **5** | Cost/Latency Targets | Guide L1 toward efficient planning under resource limits |

### Context Layer (Patterns 6-10)

| # | Instruction Type | L1 Application |
|---|------------------|----------------|
| **6** | Untrusted Block Wrapping | Encapsulate user-provided text as neutral data-only segments |
| **7** | Canonicalization of User Inputs | Normalize formatting, casing, spacing before planning |
| **8** | Context Pruning Rules | Filter irrelevant material to respect token budgets |
| **9** | Cross-Field Consistency Checks | Verify inputs align without contradictions |
| **10** | Structured Context Ordering | Present inputs in deterministic, stable sequence |

### Reasoning Layer (Patterns 11-15)

| # | Instruction Type | L1 Application |
|---|------------------|----------------|
| **11** | Failure Anticipation Injection | Predict likely planning mistakes and mitigate proactively |
| **12** | Self-Consistency / Multi-Branch | Generate multiple plan branches and vote for strongest |
| **13** | Confidence & Uncertainty Injection | Provide numeric confidence for plan quality |
| **14** | Reason-Then-Answer Structure | Think privately first, then output structured plan |
| **15** | Error Simulation Injection | Simulate potential failures before finalizing plan |

---

## L1-Specific Implementation Guidelines

### For P1_retrieve (Understanding)
```
Apply patterns: 6, 7, 8, 10
- Wrap all retrieved context as untrusted blocks
- Canonicalize before semantic analysis
- Prune irrelevant context aggressively
```

### For P2_inspect (Analysis)
```
Apply patterns: 9, 11, 12, 13
- Cross-check consistency across all inputs
- Anticipate analysis failures
- Generate multiple interpretation branches
```

### For P3_aggregate (Synthesis)
```
Apply patterns: 1, 2, 14, 15
- Anchor synthesis to global goal
- Define success criteria for aggregation
- Reason-then-answer for final plan
```

### For P4_safety (Guardrails)
```
Apply patterns: 3, 4, 5
- Declare task mode explicitly
- Enforce scope boundaries
- Respect cost/latency targets
```

---

## Dependency Injection Principles for L1

From `Dependency & Prompt Injection Patterns.md`:

| Pattern | L1 Application |
|---------|----------------|
| **Constructor Injection** | Inject all required context at plan creation |
| **Method Injection** | Pass request-specific context per planning operation |
| **Interface Injection** | Enforce consistent planning contracts across agents |

### Key Principle
> **Explicit > Implicit:** Always declare planning dependencies rather than discovering them dynamically.

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Safety rules: `01_agentic_core/L5_safety/`
