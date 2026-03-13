# OUTPUT CONTRACTS — apps_rfp: AI Proposal / RFP Generator

## Overview

Every run of `apps_rfp` produces three artifacts (or zero in dry-run mode).
No partial outputs. All artifacts are consistent: `run_summary.json` always references
the same artifact paths that were written.

---

## Artifact 1: Proposal Document (`proposal_<industry>_<trace_id[:8]>.md`)

**Type:** Markdown
**Location:** `{output_dir}/proposal_{industry}_{trace_id[:8]}.md`
**Emitted when:** Status is `COMPLETE`

### Schema

```markdown
# AI Platform Proposal — {Client Problem Statement (truncated to 60 chars)}

**Industry:** {industry}
**Architecture Posture:** {posture}
**Trace ID:** `{trace_id}`
**Status:** COMPLETE

---

## {Section Heading}

{section.body}

---
...

## Implementation Roadmap

| Phase | Name | Duration | Deliverable |
|-------|------|----------|-------------|
| 1     | Discover | 4 weeks | Current-state assessment |
...

## Risk & Governance Matrix

| Risk ID | Title | Severity | Owner | Mitigation |
|---------|-------|----------|-------|------------|
...

## Assumptions

| ID      | Statement | Type |
|---------|-----------|------|
| ASM-001 | ...       | ...  |
```

---

## Artifact 2: Proposal Manifest (`proposal_manifest_<trace_id[:8]>.json`)

**Type:** JSON
**Location:** `{output_dir}/proposal_manifest_{trace_id[:8]}.json`

### Schema

```json
{
  "trace_id": "string",
  "industry": "string",
  "posture": "string",
  "sections": [
    {"section_id": "string", "heading": "string", "word_count": 0, "required": true}
  ],
  "roadmap": [
    {"phase": 1, "name": "string", "duration_weeks": 4, "deliverable": "string"}
  ],
  "risks": [
    {"risk_id": "string", "title": "string", "severity": "HIGH|MEDIUM|LOW",
     "owner": "string", "mitigation": "string", "regulatory_flag": "string"}
  ],
  "assumptions": [
    {"assumption_id": "ASM-NNN", "statement": "string", "type": "string"}
  ]
}
```

---

## Artifact 3: Run Summary (`run_summary_<trace_id[:8]>.json`)

**Type:** JSON
**Location:** `{output_dir}/run_summary_{trace_id[:8]}.json`

### Schema

```json
{
  "trace_id": "string",
  "app": "apps_rfp",
  "version": "1.0.0",
  "status": "complete | failed | dry_run",
  "industry": "string",
  "posture": "string",
  "sections_generated": 6,
  "roadmap_phases": 5,
  "risks_identified": 0,
  "quality_score": 0.0,
  "gate_violations": [],
  "artifacts": [],
  "dry_run": false,
  "error": "",
  "provenance": {
    "trace_id": "string",
    "industry": "string",
    "posture": "string",
    "app": "apps_rfp",
    "checkpoints": ["HOP-1-PARSE", "HOP-2-ASSEMBLE", "HOP-3-GATE", "HOP-4-EMIT"]
  }
}
```

---

## Roadmap Contract

The roadmap always has exactly **5 phases**:

| Phase | Name     | Position | Constraint                        |
|-------|----------|----------|-----------------------------------|
| 1     | Discover | First    | Fixed name                        |
| 2     | Architect| Second   | Fixed name                        |
| 3     | Pilot    | Third    | Fixed name                        |
| 4     | Scale    | Fourth   | Fixed name                        |
| 5     | Govern   | Last     | Must be last; gate checks for it  |

Durations are configurable. Phase names are not user-configurable (intentional design choice
to enforce governance phase presence).

---

## Risk Matrix Contract

Every `RiskItem` MUST have:
- Non-empty `risk_id` (format: `RISK-NNN`)
- Non-empty `mitigation`
- Non-empty `owner` (`"Platform Team"` | `"Client"` | `"Joint"`)
- `severity` is one of `HIGH`, `MEDIUM`, `LOW`

No risk item may have an empty mitigation. No silent "TBD" values.

---

## Assumptions Contract

Every `AssumptionItem` MUST have:
- `assumption_id` in format `ASM-NNN`
- Non-empty `statement`
- `type` from: `"timeline"` | `"resource"` | `"access"` | `"scope"` | `"external_dependency"`

---

## Dry-Run and Failure Contracts

**Dry-run:** Same as apps_exec — no files written, sections assembled, violations computed in memory.

**Gate failure:** Only `run_summary.json` written. Proposal `.md` and manifest NOT written. Exit code 1.
