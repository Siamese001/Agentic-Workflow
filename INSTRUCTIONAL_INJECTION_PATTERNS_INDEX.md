# Instructional Injection Patterns — Master Index

> **Canonical Sources:**
> - `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> - `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`

---

## Pattern Distribution Across Architecture

These critical instructional patterns have been disseminated to all relevant folders:

### Agentic Core (01_agentic_core/)

| Layer | File | Primary Patterns |
|-------|------|------------------|
| L1 Cognition | `L1_cognition/INSTRUCTIONAL_INJECTION_PATTERNS.md` | Framing (1-5), Context (6-10), Reasoning (11-15) |
| L2 Execution | `L2_execution/INSTRUCTIONAL_INJECTION_PATTERNS.md` | Tooling (16-20), Output (26-30) |
| L3 Orchestration | `L3_orchestration/INSTRUCTIONAL_INJECTION_PATTERNS.md` | Framing (1-5), Safety (21-25) |
| L4 Memory | `L4_memory/INSTRUCTIONAL_INJECTION_PATTERNS.md` | Context (6-10), Tooling (16-18), Safety (21-22) |
| L5 Safety | `L5_safety/INSTRUCTIONAL_INJECTION_PATTERNS.md` | ALL Safety (21-25), plus enforcement patterns |

### Runtime (03_runtime/)

| Module | File | Primary Patterns |
|--------|------|------------------|
| Runtime Root | `INSTRUCTIONAL_INJECTION_PATTERNS.md` | Output (26-30), Safety (21-25) |
| Security Controls | `security_controls/INSTRUCTIONAL_INJECTION_PATTERNS.md` | ALL Safety patterns, adversarial defense |

### Applications (09_apps/)

| App | File | Primary Patterns |
|-----|------|------------------|
| LIC (Outreach) | `apps_lic/INSTRUCTIONAL_INJECTION_PATTERNS.md` | Framing, Context, Safety for outreach |
| RG (Resume) | `apps_rg/INSTRUCTIONAL_INJECTION_PATTERNS.md` | Framing, Context, Output for resume gen |

---

## Quick Reference: 30 Instructional Injection Patterns

### Framing Layer (1-5)

| # | Pattern | Purpose |
|---|---------|---------|
| 1 | Global Goal-State Injection | Anchor reasoning to objective |
| 2 | Success Criteria Injection | Define quality thresholds |
| 3 | Task Mode Declaration | Specify cognitive mode |
| 4 | Scope & Boundaries Injection | State constraints |
| 5 | Cost/Latency Targets | Guide efficiency |

### Context Layer (6-10)

| # | Pattern | Purpose |
|---|---------|---------|
| 6 | Untrusted Block Wrapping | Encapsulate user data |
| 7 | Canonicalization | Normalize inputs |
| 8 | Context Pruning Rules | Filter irrelevant |
| 9 | Cross-Field Consistency | Verify alignment |
| 10 | Structured Context Ordering | Deterministic sequence |

### Reasoning Layer (11-15)

| # | Pattern | Purpose |
|---|---------|---------|
| 11 | Failure Anticipation | Predict mistakes |
| 12 | Self-Consistency / Multi-Branch | Vote for strongest |
| 13 | Confidence & Uncertainty | Numeric confidence |
| 14 | Reason-Then-Answer | Think first |
| 15 | Error Simulation | Simulate failures |

### Tooling Layer (16-20)

| # | Pattern | Purpose |
|---|---------|---------|
| 16 | Tool-Feedback Loop | Incorporate outputs |
| 17 | Evidence Binding | Ground to sources |
| 18 | Cross-Tool Reconciliation | Resolve conflicts |
| 19 | Shadow Validation | Sanity check |
| 20 | Model-Switch Aware | Adapt to model |

### Safety Layer (21-25)

| # | Pattern | Purpose |
|---|---------|---------|
| 21 | Prompt-Injection Shielding | Anti-jailbreak |
| 22 | Data vs Instruction Separation | Distinguish types |
| 23 | Constitutional Guardrails | Ethics/safety |
| 24 | Delegation Guardrails | Prevent override |
| 25 | Expanded Adversarial Mode | Detect manipulation |

### Output Layer (26-30)

| # | Pattern | Purpose |
|---|---------|---------|
| 26 | Strict JSON-Only | Schema compliance |
| 27 | Schema Enforcement | Validate output |
| 28 | Stability Contracts | Consistent fields |
| 29 | Error Envelope | Standardize errors |
| 30 | Minimality Constraints | Limit size |

---

## Adversarial Defense Summary

From `Dependency & Prompt Injection Patterns.md`:

| Attack | Defense |
|--------|---------|
| Direct Injection | Input sanitization, instruction priority |
| Indirect Injection | Trusted content filtering, isolation |
| Data Poisoning | Provenance verification, hashing |
| Prompt Leaking | Role separation, masking |
| Jailbreak | Sandboxing, decoupled planning |
| Semantic Injection | Symbolic validators |
| Cross-Model Injection | Per-agent sandboxing, tracing |

---

## Key Principles

1. **Explicit > Implicit** — Declare all dependencies and constraints
2. **Input Sanitization** — Treat all user input as untrusted
3. **Prompt Segmentation** — Isolate system vs user vs retrieved
4. **Content Provenance** — Track where every text chunk came from
5. **Multi-Agent Sandboxing** — Contain agents; enforce boundaries

---

## Usage

Each layer-specific file contains:
- Applicable patterns for that layer
- Implementation guidelines per subfolder (P1-P4)
- Dependency injection principles
- Cross-references to source documents

Developers should consult the layer-specific file when implementing agents or operations in that layer.
