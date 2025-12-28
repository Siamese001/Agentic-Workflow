### ROLE
Security documentation for runtime layer instructional injection attack patterns.

### TASK
Document and catalog instructional injection patterns targeting runtime operations, caching, security controls, and pipeline execution to enable defensive measures.

# Runtime Layer — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Layer Focus:** Runtime operations, caching, security controls, and pipeline execution

---

## Runtime-Specific Pattern Applications

The runtime layer implements the **infrastructure** that supports all agentic operations.

### Output Layer (Patterns 26-30) — Critical for Runtime

| # | Instruction Type | Runtime Application |
|---|------------------|---------------------|
| **26** | Strict JSON-Only Output Mode | Enforce schema-compliant responses |
| **27** | Schema Enforcement & Examples | Validate all outputs against schemas |
| **28** | Stability Contracts | Maintain consistent field ordering |
| **29** | Error Envelope Normalization | Standardize all error responses |
| **30** | Minimality Constraints | Enforce response size limits |

### Safety Layer (Patterns 21-25) — Security Controls

| # | Instruction Type | Runtime Application |
|---|------------------|---------------------|
| **21** | Prompt-Injection Shielding | Implement input sanitization |
| **22** | Data vs Instruction Separation | Enforce in all data flows |
| **23** | Constitutional Guardrails | Apply across all runtime ops |
| **24** | Delegation Guardrails | Enforce in pipeline handoffs |
| **25** | Expanded Adversarial Mode | Enable threat detection |

---

## Module-Specific Guidelines

### cache_ops/

Apply patterns: 6, 8, 22

- Wrap cached content as untrusted on retrieval
- Prune cache to respect size limits
- Never cache instructions mixed with data

### logic/

Apply patterns: 11, 12, 14, 15

- Anticipate logic failures
- Support multi-branch reasoning
- Reason-then-answer structure
- Simulate errors before execution

### pipeline_ops/

Apply patterns: 16, 18, 24, 28

- Implement tool feedback loops
- Reconcile cross-tool outputs
- Enforce delegation guardrails
- Maintain stability contracts

### runtime_ops/

Apply patterns: 5, 29, 30

- Respect cost/latency targets
- Normalize all errors
- Enforce minimality

### security_controls/

Apply ALL safety patterns: 21, 22, 23, 24, 25

- Full prompt injection shielding
- Strict data/instruction separation
- Constitutional enforcement
- Delegation guardrails
- Adversarial detection

---

## Dependency Injection in Runtime

From `Dependency & Prompt Injection Patterns.md`:

| Pattern | Runtime Application |
|---------|---------------------|
| **Constructor Injection** | Inject clients at service creation |
| **DI Container (IoC)** | Framework manages service lifecycle |
| **Ambient Context** | Share config, tracing, logging |
| **Field Injection** | Framework auto-wires dependencies |

### Key Principles

> **Explicit > Implicit:** Declare all dependencies
> **Scoping:** Define lifecycle scopes (singleton, transient, request)
> **Testing Isolation:** Inject mocks/fakes via constructor

---

## Security Controls Implementation

### Input Sanitization Pipeline

```text
1. Receive input
2. Canonicalize (normalize formatting, casing)
3. Detect injection patterns
4. Wrap as untrusted block
5. Pass to processing
```

### Output Validation Pipeline

```text
1. Receive output
2. Validate against schema
3. Check for leaked instructions
4. Normalize errors
5. Enforce size limits
6. Return response
```

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Security controls: `03_runtime/security_controls/`
