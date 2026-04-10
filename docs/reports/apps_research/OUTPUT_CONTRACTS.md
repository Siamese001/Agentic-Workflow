# OUTPUT CONTRACTS — apps_research: Autonomous Research Engine

## Overview

Every run of `apps_research` produces three artifacts (or zero in dry-run mode).
All claims in the brief artifact carry explicit epistemic labels. The source register
is a machine-readable companion to every artifact.

---

## Artifact 1: Research Artifact (`research_<mode>_<trace_id[:8]>.md`)

**Type:** Markdown
**Location:** `{output_dir}/research_{mode}_{trace_id[:8]}.md`
**Emitted when:** Status is `COMPLETE`

### Schema

```markdown
# Research Artifact — {topic}

**Mode:** {mode}
**Trace ID:** `{trace_id}`
**Quality Score:** {quality_score:.0%}

---

## {Section Heading} `[{claim_type}]`

{section.body}

---
...

## Comparison Matrix          ← (comparison mode only)

| Subject | Architecture Model | Governance Approach | ... |
|---------|-------------------|---------------------|-----|
| ...     | ...               | ...                 | ... |
```

### Section Body Claim-Type Convention

Every section body MUST include at least one labeled claim.
Format: `**{Claim label} [{CLAIM_TYPE}]:** {claim text}`

Valid claim type labels: `DIRECT_EVIDENCE`, `INTERPRETATION`, `ANALYST_INFERENCE`, `ASSUMPTION`

---

## Artifact 2: Source Register (`source_register_<trace_id[:8]>.json`)

**Type:** JSON array
**Location:** `{output_dir}/source_register_{trace_id[:8]}.json`
**Emitted when:** Status is `COMPLETE`

### Schema (per entry)

```json
{
  "source_id": "SRC-001",
  "title": "string",
  "claim_type": "direct_evidence | interpretation | analyst_inference | assumption",
  "confidence": 0.95,
  "summary": "string",
  "url": "string",
  "section_id": "string"
}
```

### Field Constraints

| Field         | Constraint                          |
|---------------|-------------------------------------|
| `source_id`   | Format `SRC-NNN`; unique per run    |
| `confidence`  | Float 0.0–1.0; never null           |
| `claim_type`  | One of four defined enum values     |
| `section_id`  | Matches a section in the artifact   |

---

## Artifact 3: Run Summary (`run_summary_<trace_id[:8]>.json`)

**Type:** JSON
**Location:** `{output_dir}/run_summary_{trace_id[:8]}.json`

### Schema

```json
{
  "trace_id": "string",
  "app": "apps_research",
  "version": "1.0.0",
  "status": "complete | failed | dry_run",
  "topic": "string",
  "mode": "brief | comparison | trend | position | thought_leadership",
  "sections_generated": 0,
  "sources_registered": 0,
  "quality_score": 0.0,
  "gate_violations": [],
  "artifacts": [],
  "dry_run": false,
  "error": "",
  "provenance": {
    "trace_id": "string",
    "topic": "string",
    "mode": "string",
    "app": "apps_research",
    "checkpoints": ["HOP-1-ASSEMBLY", "HOP-2-GATE", "HOP-3-EMIT"]
  }
}
```

---

## Comparison Matrix Contract (comparison mode)

When mode is `comparison`:
- At least 2 `ComparisonRow` objects required
- Every row MUST have the same set of dimension keys
- Unknown subjects use value `"Unknown — requires primary research"` (never empty string)
- The matrix is rendered as a Markdown table in the artifact

---

## Epistemic Transparency Commitment

**No claim in any artifact is unlabeled.**

The following guarantee holds for every `ResearchSection`:
1. `claim_type` is always set (never defaults to `None`)
2. Section body contains at least one inline claim label `[CLAIM_TYPE]`
3. `source_register` contains at least one entry pointing to this section

Violations of this guarantee are surfaced by `ResearchGateValidator` as `BLOCK` violations.

---

## Dry-Run and Failure Contracts

**Dry-run:** No files written. Sections and source register are assembled in memory and returned
in `ResearchResult`. Quality score is computed. Status = `"dry_run"`.

**Gate failure:** Only `run_summary.json` written. Artifact `.md` and source register NOT written.
Exit code 1.
