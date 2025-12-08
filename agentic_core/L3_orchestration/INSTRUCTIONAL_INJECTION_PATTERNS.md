# L3 Orchestration — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Layer Focus:** Cross-agent coordination and workflow patterns

---

## Applicable Patterns for L3 Orchestration

L3 Orchestration handles **workflow coordination** — these patterns are critical:

### Framing Layer (Patterns 1-5)

| # | Instruction Type | L3 Application |
|---|------------------|----------------|
| **1** | Global Goal-State Injection | Propagate overarching objective to all agents |
| **2** | Success Criteria Injection | Define workflow completion thresholds |
| **3** | Task Mode Declaration | Coordinate cognitive modes across agents |
| **4** | Scope & Boundaries Injection | Enforce workflow boundaries and constraints |
| **5** | Cost/Latency Targets | Manage resource budgets across workflow |

### Safety Layer (Patterns 21-25) — **CRITICAL FOR L3**

| # | Instruction Type | L3 Application |
|---|------------------|----------------|
| **21** | Prompt-Injection Shielding | Protect system instructions across agent handoffs |
| **22** | Data vs Instruction Separation | Clearly distinguish data from directives in handoffs |
| **23** | Constitutional Guardrails | Enforce ethics/safety across all orchestrated agents |
| **24** | Delegation Guardrails | **Prevent downstream agents from overriding upstream** |
| **25** | Expanded Adversarial Mode | Detect manipulation across agent boundaries |

---

## L3-Specific Implementation Guidelines

### For P1_retrieve (Workflow State)
```
Apply patterns: 1, 22
- Retrieve workflow state with clear data/instruction separation
- Anchor all state to global goal
```

### For P2_inspect (Agent Coordination)
```
Apply patterns: 24, 25
- Enforce delegation guardrails between agents
- Detect adversarial patterns in agent outputs
```

### For P3_aggregate (Workflow Synthesis)
```
Apply patterns: 2, 3, 5
- Aggregate results against success criteria
- Coordinate task modes across agents
- Respect cost/latency budgets
```

### For P4_safety (Workflow Guardrails)
```
Apply patterns: 4, 21, 23
- Enforce scope boundaries
- Shield against prompt injection in handoffs
- Apply constitutional guardrails
```

---

## Cross-Agent Injection Defense

From `Dependency & Prompt Injection Patterns.md`:

### Critical Risk: Cross-Model Injection
> One model injects adversarial prompts into another (multi-agent chains).
> An LLM passes poisoned context to another.

### L3 Mitigations

| Defense | Implementation |
|---------|----------------|
| **Per-Agent Sandboxing** | Isolate each agent's context |
| **Content Tracing** | Track provenance of all data across agents |
| **Trust Boundaries** | Define explicit trust levels between agents |
| **Delegation Guardrails** | Downstream cannot override upstream decisions |

---

## Dependency Injection Principles for L3

| Pattern | L3 Application |
|---------|----------------|
| **Constructor Injection** | Inject agent dependencies at workflow creation |
| **DI Container (IoC)** | Framework manages agent lifecycle and wiring |
| **Ambient Context** | Share workflow-wide context (config, tracing) |

### Key Principle
> **Multi-Agent Sandboxing:** Contain reasoning agents; enforce context boundaries.

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Safety rules: `01_agentic_core/L5_safety/`
