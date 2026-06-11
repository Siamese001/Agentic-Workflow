---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\dedup_stop_sprawl_policy.md'
original_relative_path: 'dedup_stop_sprawl_policy.md'
source_sha256: e5298ed8f592f85dc35894a7c4e671402e0dc93eec5ccfa4601e5327765d4e34
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-02-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
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

