---
title: Instructional Injection v5
version: 5.0
domain: prompt_governance
category: injection_patterns
description: Condensed reference table of 30 instructional injection types across 6 layers
---

# Instructional Injection v5 — Condensed Table

| #      | Category        | Instruction Type                         | Description                                                                 |
| ------ | --------------- | ---------------------------------------- | --------------------------------------------------------------------------- |
| **1**  | Framing Layer   | Global Goal-State Injection              | Anchor all model reasoning to one clear overarching objective.              |
| **2**  | Framing Layer   | Success Criteria Injection               | Define explicit quality thresholds and outcome requirements upfront.        |
| **3**  | Framing Layer   | Task Mode Declaration                    | Specify cognitive mode: analytical, synthesis, adversarial, meta, security. |
| **4**  | Framing Layer   | Scope & Boundaries Injection             | State exact constraints and forbidden behaviors for the task.               |
| **5**  | Framing Layer   | Cost/Latency Targets                     | Guide model toward concise, efficient reasoning under resource limits.      |
| **6**  | Context Layer   | Untrusted Block Wrapping                 | Encapsulate user-provided text as neutral data-only segments.               |
| **7**  | Context Layer   | Canonicalization of User Inputs          | Normalize formatting, casing, spacing, and command-like sequences.          |
| **8**  | Context Layer   | Context Pruning Rules                    | Filter irrelevant material to respect token and relevance budgets.          |
| **9**  | Context Layer   | Cross-Field Consistency Checks           | Verify JD, resume, strategy, and bullets align without contradictions.      |
| **10** | Context Layer   | Structured Context Ordering              | Present inputs in deterministic, stable, predictable sequence.              |
| **11** | Reasoning Layer | Failure Anticipation Injection           | Predict likely mistakes before reasoning and mitigate proactively.          |
| **12** | Reasoning Layer | Self-Consistency / Multi-Branch Thinking | Generate multiple branches and vote for strongest reasoning path.           |
| **13** | Reasoning Layer | Confidence & Uncertainty Injection       | Provide numeric confidence with clear justification for uncertainty.        |
| **14** | Reasoning Layer | Reason-Then-Answer Structure             | Think privately first, then output final structured result.                 |
| **15** | Reasoning Layer | Error Simulation Injection               | Simulate potential failures and correct output before finalizing.           |
| **16** | Tooling Layer   | Tool-Feedback Loop Injection             | Incorporate structured tool outputs into subsequent reasoning steps.        |
| **17** | Tooling Layer   | Evidence Binding / Citation Anchors      | Ground claims to explicit retrieved strings or verified evidence.           |
| **18** | Tooling Layer   | Cross-Tool Reconciliation                | Resolve conflicting outputs across RAG, QA, and drafting tools.             |
| **19** | Tooling Layer   | Shadow Validation                        | Run rapid internal sanity check before returning final output.              |
| **20** | Tooling Layer   | Model-Switch Aware Instructions          | Adapt instructions based on fast versus high-accuracy model usage.          |
| **21** | Safety Layer    | Prompt-Injection Shielding Layer         | Add robust anti-jailbreak safeguards protecting system instructions.        |
| **22** | Safety Layer    | Data vs Instruction Separation           | Clearly distinguish raw data content from actionable directives.            |
| **23** | Safety Layer    | Constitutional Guardrails                | Enforce ethics, safety, neutrality, and style principles consistently.      |
| **24** | Safety Layer    | Delegation Guardrails                    | Prevent downstream agents from overriding upstream decisions.               |
| **25** | Safety Layer    | Expanded Adversarial Mode                | Strengthen detection of manipulative or anomalous patterns.                 |
| **26** | Output Layer    | Strict JSON-Only Output Mode             | Require deterministic, schema-compliant JSON without extra text.            |
| **27** | Output Layer    | Schema Enforcement & Examples            | Supply minimal schema and one valid illustrative example.                   |
| **28** | Output Layer    | Stability Contracts                      | Preserve field order and naming across repeated outputs.                    |
| **29** | Output Layer    | Error Envelope Normalization             | Standardize failures into simple, structured error objects.                 |
| **30** | Output Layer    | Minimality Constraints                   | Limit output size to enforce clarity and conciseness.                       |
