# Agent Sprawl Prevention Policy

## Purpose

Prevent regression of agent count after consolidation by enforcing
uniqueness constraints on new agent creation.

## Rules

### 1. Single Responsibility Constraint

Every agent MUST have a clearly defined, non-overlapping responsibility.
The responsibility MUST be documented in the class docstring.

### 2. Uniqueness Proof Required

Before creating a new agent, the developer MUST:
1. Run `python artifacts/dedup/run_dedup_analysis.py` to check for existing overlap
2. Demonstrate that no existing agent covers >60% of the proposed responsibility
3. Document the uniqueness justification in the PR description

### 3. Cluster Check Gate

A CI gate MUST run similarity checks on every PR that adds a new agent:
```bash
python artifacts/dedup/run_dedup_analysis.py
# Fails if any new agent has code_similarity >= 0.75 with an existing agent
```

### 4. Shared Core Reuse

If a new agent shares >50% of its logic with an existing agent, the shared
logic MUST be extracted to a shared module and both agents must import from it.

### 5. Waiver Process

Exceptions require:
- Written justification explaining why the overlap is necessary
- Approval from project architect
- Documented in `artifacts/dedup/waivers/` with agent name and date

## CI Gate Invocation

```yaml
# .github/workflows/agent-sprawl-check.yml
name: Agent Sprawl Check
on: [pull_request]
jobs:
  sprawl-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m agentic_core.L0_maintenance.scripts.full_agent_discovery
      - run: python artifacts/dedup/run_dedup_analysis.py
      - run: python artifacts/dedup/sprawl_gate.py --max-similarity 0.75
```

## Findings

[Document key findings from the investigation]

---

## Evidence

[Provide evidence supporting the findings]

---

