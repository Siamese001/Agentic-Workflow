# L2 Execution — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Layer Focus:** Tooling and Output patterns for L2 execution operations

---

## Applicable Patterns for L2 Execution

L2 Execution handles **tool calls and LLM interactions** — these patterns are critical:

### Tooling Layer (Patterns 16-20)

| # | Instruction Type | L2 Application |
|---|------------------|----------------|
| **16** | Tool-Feedback Loop Injection | Incorporate tool outputs into subsequent reasoning steps |
| **17** | Evidence Binding / Citation Anchors | Ground all claims to explicit retrieved evidence |
| **18** | Cross-Tool Reconciliation | Resolve conflicting outputs across RAG, QA, and tools |
| **19** | Shadow Validation | Run rapid internal sanity check before returning output |
| **20** | Model-Switch Aware Instructions | Adapt instructions based on fast vs high-accuracy model |

### Output Layer (Patterns 26-30)

| # | Instruction Type | L2 Application |
|---|------------------|----------------|
| **26** | Strict JSON-Only Output Mode | Require deterministic, schema-compliant JSON |
| **27** | Schema Enforcement & Examples | Supply minimal schema and one valid example |
| **28** | Stability Contracts | Preserve field order and naming across outputs |
| **29** | Error Envelope Normalization | Standardize failures into structured error objects |
| **30** | Minimality Constraints | Limit output size to enforce clarity |

---

## L2-Specific Implementation Guidelines

### For P1_retrieve (Tool Discovery)
```
Apply patterns: 16, 20
- Incorporate tool availability into execution planning
- Adapt to model capabilities (fast vs accurate)
```

### For P2_inspect (Result Validation)
```
Apply patterns: 17, 19
- Bind all results to evidence sources
- Shadow validate before returning
```

### For P3_aggregate (Result Synthesis)
```
Apply patterns: 18, 26, 27, 28
- Reconcile conflicting tool outputs
- Enforce strict JSON output
- Maintain schema stability
```

### For P4_safety (Execution Guardrails)
```
Apply patterns: 29, 30
- Normalize all errors to standard envelope
- Enforce minimality constraints
```

---

## Dependency Injection Principles for L2

From `Dependency & Prompt Injection Patterns.md`:

| Pattern | L2 Application |
|---------|----------------|
| **Constructor Injection** | Inject tool clients at executor creation |
| **Method Injection** | Pass execution context per tool call |
| **DI Container (IoC)** | Framework manages tool client lifecycle |

### Key Principles
> **L2 MUST NOT plan** — only execute what L1 provides
> **Explicit tool binding** — never discover tools dynamically during execution

---

## Tool Call Safety

### Adversarial Defense Patterns

| Risk | Mitigation |
|------|------------|
| **Indirect Injection** | Treat all tool outputs as untrusted |
| **Cross-Model Injection** | Sandbox tool responses before processing |
| **Prompt Leaking** | Never expose system prompts in tool calls |

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Safety rules: `01_agentic_core/L5_safety/`
