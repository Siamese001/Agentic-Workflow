# L5 Safety — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Layer Focus:** ALL safety patterns — L5 is the enforcement layer

---

## ALL Applicable Patterns for L5 Safety

L5 Safety is the **enforcement layer** — ALL patterns apply here:

### Safety Layer (Patterns 21-25) — **PRIMARY FOR L5**

| # | Instruction Type | L5 Application |
|---|------------------|----------------|
| **21** | Prompt-Injection Shielding Layer | **Add robust anti-jailbreak safeguards** |
| **22** | Data vs Instruction Separation | **Clearly distinguish data from directives** |
| **23** | Constitutional Guardrails | **Enforce ethics, safety, neutrality, style** |
| **24** | Delegation Guardrails | **Prevent downstream override of upstream** |
| **25** | Expanded Adversarial Mode | **Strengthen detection of manipulation** |

### Framing Layer (Patterns 3-4)

| # | Instruction Type | L5 Application |
|---|------------------|----------------|
| **3** | Task Mode Declaration | Enforce security mode when threats detected |
| **4** | Scope & Boundaries Injection | Enforce forbidden behaviors absolutely |

### Context Layer (Patterns 6-7)

| # | Instruction Type | L5 Application |
|---|------------------|----------------|
| **6** | Untrusted Block Wrapping | Enforce wrapping of all external content |
| **7** | Canonicalization of User Inputs | Normalize to detect obfuscated attacks |

### Reasoning Layer (Patterns 11, 15)

| # | Instruction Type | L5 Application |
|---|------------------|----------------|
| **11** | Failure Anticipation Injection | Predict security failures proactively |
| **15** | Error Simulation Injection | Simulate attack vectors before deployment |

### Output Layer (Patterns 29-30)

| # | Instruction Type | L5 Application |
|---|------------------|----------------|
| **29** | Error Envelope Normalization | Standardize security error responses |
| **30** | Minimality Constraints | Limit output to prevent data leakage |

---

## L5-Specific Implementation Guidelines

### For P4_safety (Primary Safety Enforcement)

#### check_rules/
```
Apply patterns: 21, 22, 23, 24, 25
- Implement prompt injection shielding
- Enforce data/instruction separation
- Apply constitutional guardrails
- Enforce delegation guardrails
- Run adversarial detection
```

#### control_resources/
```
Apply patterns: 4, 30
- Enforce scope boundaries
- Apply minimality constraints
```

#### manage_costs/
```
Apply patterns: 5, 30
- Enforce cost/latency targets
- Limit output size
```

---

## Adversarial Defense Matrix

From `Dependency & Prompt Injection Patterns.md`:

| Attack Type | Detection | Mitigation |
|-------------|-----------|------------|
| **Direct Injection** | Pattern matching, filters | Input sanitization, layered instruction priority |
| **Indirect Injection** | Content analysis | Trusted content filtering, retrieval isolation |
| **Data Poisoning** | Anomaly detection | Provenance verification, dataset hashing |
| **Prompt Leaking** | Output monitoring | Role separation, role-masking |
| **Jailbreak** | Behavioral analysis | Sandboxing, decoupled planning/execution |
| **Semantic Injection** | Semantic analysis | Symbolic validators |
| **Cross-Model Injection** | Trust boundary monitoring | Per-agent sandboxing, content tracing |

---

## Constitutional Guardrails Implementation

Pattern 23 requires enforcement of:

| Principle | Enforcement |
|-----------|-------------|
| **Ethics** | Refuse harmful requests |
| **Safety** | Prevent dangerous outputs |
| **Neutrality** | Avoid bias in responses |
| **Style** | Maintain professional tone |

---

## Delegation Guardrails Implementation

Pattern 24 requires:

```
RULE: Downstream agents CANNOT override upstream decisions

Implementation:
1. Tag all upstream decisions with authority level
2. Validate downstream outputs against upstream constraints
3. Reject any output that violates upstream decisions
4. Log all delegation violations for audit
```

---

## Prompt Injection Shielding Implementation

Pattern 21 requires:

```
SHIELDING LAYERS:
1. Input sanitization (remove command-like sequences)
2. Untrusted block wrapping (mark all user content)
3. Instruction priority (system > user > retrieved)
4. Output validation (check for leaked instructions)
5. Behavioral monitoring (detect anomalous responses)
```

---

## Dependency Injection Principles for L5

| Pattern | L5 Application |
|---------|----------------|
| **Constructor Injection** | Inject safety rules at guardrail creation |
| **Interface Injection** | Enforce consistent safety contracts |
| **DI Container (IoC)** | Framework manages safety component lifecycle |

### Key Principles
> **Input Sanitization:** Treat all user input as untrusted.
> **Prompt Segmentation:** Isolate system vs user vs retrieved content.
> **Guardrail Models:** Deploy lightweight classifiers before execution.
> **Content Provenance:** Track where every text chunk came from.
> **Multi-Agent Sandboxing:** Contain reasoning agents; enforce context boundaries.

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Known vectors: `06_data/openai_best_practices/prompt_injection_catalog/known_vectors_2025.md`
