# Security Controls — Instructional Injection Patterns

> **Source:** `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
> **Layer Focus:** ALL security-related patterns — this is the enforcement point

---

## Critical Patterns for Security Controls

### Safety Layer (Patterns 21-25) — MANDATORY

| # | Instruction Type | Implementation |
|---|------------------|----------------|
| **21** | Prompt-Injection Shielding Layer | Anti-jailbreak safeguards |
| **22** | Data vs Instruction Separation | Content type tagging |
| **23** | Constitutional Guardrails | Ethics/safety enforcement |
| **24** | Delegation Guardrails | Upstream authority preservation |
| **25** | Expanded Adversarial Mode | Manipulation detection |

### Context Layer (Patterns 6-7) — Input Processing

| # | Instruction Type | Implementation |
|---|------------------|----------------|
| **6** | Untrusted Block Wrapping | Mark all external content |
| **7** | Canonicalization | Normalize to detect obfuscation |

---

## Adversarial Attack Defense Matrix

From `Dependency & Prompt Injection Patterns.md`:

| Attack Type | Detection Method | Mitigation |
|-------------|------------------|------------|
| **Direct Injection** | Pattern matching | Input sanitization, instruction priority |
| **Indirect Injection** | Content analysis | Trusted content filtering, isolation |
| **Data Poisoning** | Anomaly detection | Provenance verification, hashing |
| **Prompt Leaking** | Output monitoring | Role separation, masking |
| **Jailbreak** | Behavioral analysis | Sandboxing, decoupled planning |
| **Semantic Injection** | Semantic analysis | Symbolic validators |
| **Cross-Model Injection** | Trust boundaries | Per-agent sandboxing, tracing |

---

## Implementation Checklist

### Pattern 21: Prompt-Injection Shielding

- [ ] Input sanitization removes command-like sequences
- [ ] All user content wrapped as untrusted
- [ ] Instruction priority: system > user > retrieved
- [ ] Output validation checks for leaked instructions
- [ ] Behavioral monitoring detects anomalies

### Pattern 22: Data vs Instruction Separation

- [ ] All content tagged with type (data/instruction)
- [ ] Data blocks cannot execute as instructions
- [ ] Clear visual/structural separation in prompts
- [ ] Validation rejects mixed content

### Pattern 23: Constitutional Guardrails

- [ ] Ethics rules loaded and enforced
- [ ] Safety rules block harmful outputs
- [ ] Neutrality rules prevent bias
- [ ] Style rules maintain professionalism

### Pattern 24: Delegation Guardrails

- [ ] Upstream decisions tagged with authority
- [ ] Downstream outputs validated against upstream
- [ ] Violations rejected and logged
- [ ] Audit trail maintained

### Pattern 25: Expanded Adversarial Mode

- [ ] Manipulation patterns detected
- [ ] Anomalous requests flagged
- [ ] Suspicious sequences blocked
- [ ] Threat intelligence updated

---

## Guardrails Implementation

### guardrails/check_rules/

```text
RULE CATEGORIES:
1. policy_check_safety - Safety policy enforcement
2. policy_check_ethics - Ethics policy enforcement
3. policy_check_content - Content policy enforcement
4. policy_check_injection - Injection detection
```

### Input Validation Flow

```text
INPUT → Canonicalize → Detect Patterns → Wrap Untrusted → Validate → PROCESS
         ↓              ↓                 ↓               ↓
      Normalize      Flag threats      Tag as data    Check rules
```

### Output Validation Flow

```text
OUTPUT → Schema Check → Leak Detection → Size Limit → Normalize → RETURN
          ↓              ↓                ↓            ↓
       Validate       Check for        Enforce      Standardize
       structure      instructions     minimality   errors
```

---

## Best Practices

From `Dependency & Prompt Injection Patterns.md`:

1. **Input Sanitization:** Treat all user input as untrusted
2. **Prompt Segmentation:** Isolate system vs user vs retrieved
3. **Guardrail Models:** Deploy lightweight classifiers before execution
4. **Content Provenance:** Track where every text chunk came from
5. **Multi-Agent Sandboxing:** Contain agents; enforce context boundaries

---

## Cross-Reference

- Full patterns: `06_data/prompt_libraries/injections/Instructional_Injection_Enhanced_v5.md`
- DI patterns: `06_data/prompt_libraries/injections/Dependency & Prompt Injection Patterns.md`
- Known vectors: `06_data/openai_best_practices/prompt_injection_catalog/`
- L5 Safety: `01_agentic_core/L5_safety/`
