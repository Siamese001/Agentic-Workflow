<!-- VERSION: 0.1.0 -->
# OUTPUT REQUIREMENTS (STRICT) — v5.4.2 STRUCTURE (REQUIRED ORDER)

You MUST output the following sections, in this exact order:

## SECTION A — CURRENT STATE (REPO-DERIVED)

You MUST derive these from the repository (discovery JSON + deterministic scans; no assumptions):

### A1. CURRENT CAPABILITY MATRIX (GLOBAL + LAYERED)
| Layer | Component | Exists? | Enforced? | Entry Controlled? | Evidence |
|------|-----------|---------|-----------|-------------------|----------|

Mandatory inclusions (boundary clarity; if unknown, mark as MISSING/FAIL with evidence):
* `agentic_core/**/prompt_governance` (registry + composition chokepoint)
* `apps_*` → `agentic_core` entry boundary (no direct L2/LLM/provider calls)
* prompt ownership enforcement (0.7.2) as a P6 boundary check

### A2. CURRENT ARTIFACT MATRIX (FLOW-BOUND)
| Artifact | Schema Locked? | Validated? | Emitted By | Allowed Layer | Evidence |
|---------|-----------------|------------|------------|---------------|----------|

Mandatory inclusions (prompt ownership must be traceable):
* `TokenControl` (or equivalent pre-guard token/budget artifact) MUST include a deterministic `prompt_hash` (0.7.3, §6.3)
* `RouteDecision` (or equivalent) MUST bind to `policy_hash` / config pointer and show the prompt composition source
* Any `apps_*` prompt assets MUST be represented as inputs to the composed prompt lineage (no opaque string concatenation)

### A3. CURRENT MUTATION SURFACE
| Mutation Source | Gated? | Approval Required? | Sandbox Guard? | Evidence |
|----------------|--------|--------------------|----------------|----------|

Mandatory inclusions:
* any write/mutation path originating from `apps_*` (expected: NONE; otherwise FAIL/P0)
* prompt template mutation in `agentic_core/**/prompt_governance` (must be gated + traceable)

## SECTION B — TARGET STATE (PNG/V15-ALIGNED)

You MUST express the target using the capability list in §1–§16 and the following control-plane rules:

1) **Single sanctioned execution path**
2) **No mutation outside L2**
3) **All mutation requires explicit L3 approval when phase requires**
4) **All artifacts are schema-locked + layer-legal**
5) **Phase ordering is deterministic + test-locked**
6) **Apply mode is idempotent**
7) **Prompt ownership boundary:** `apps_*` may contribute only domain fragments; `agentic_core/**/prompt_governance` composes the final prompt and MUST emit deterministic `prompt_hash` lineage captured in boundary artifacts (0.7, P4/P6)

### B1. TARGET CAPABILITY MATRIX
### B2. TARGET ARTIFACT MATRIX
### B3. TARGET CONTROL-PLANE GUARANTEES

## SECTION C — GAP SET (MECHANICAL)

For every mismatch between Section A and Section B, output:

| GAP_ID | Category | Severity | Current Evidence | Target Requirement (capability refs) |
|-------|----------|----------|------------------|--------------------------------------|

Category ∈ {Boundary, PromptOwnership, Artifact, Enforcement, Ordering, Mutation, Routing}
Severity ∈ {Critical, High, Medium, Low}

Severity mapping rule (deterministic):
* If GAP violates P1–P6 → Severity = Critical
* If GAP blocks execution path (§1, §2, §3, §7, §10, §11) → Severity = High
* If GAP impacts observability or cognitive safety only (§6, §15) → Severity = Medium
* Else → Severity = Low

GAP_ID format:
* MUST be `G-<incremental integer>` in sorted deterministic order.

## SECTION D — IMPLEMENTATION PLAN (CLOSE ALL GAPS)

For each GAP_ID, produce a wave item:

| Wave | Priority | GAP_ID | Capability IDs | Work Item | Scope (repo-grounded) | Acceptance Evidence (exact commands) |
|------|----------|--------|----------------|----------|------------------------|--------------------------------------|

Hard rule: No GAP_ID may exist without at least one wave row that closes it.

Coverage assertion (mandatory):
* Every GAP_ID from Section C MUST appear in Section D at least once.
* If any GAP_ID is missing → FAIL audit integrity and STOP.

## SECTION 1 — GLOBAL FRAMEWORK EVIDENCE TABLE (KEEP)

Capabilities: 1, 3, 4, 6, 7, 10, 11, 13, 14, 15, 16

**Format:** Table

| ID | Status (COMPLIANT / MISSING / FAIL) | Evidence Location (File + Symbol) | Notes |
| -- | ----------------------------------- | --------------------------------- | ----- |

Notes column rules:
* Strictly factual.
* Reference gating invariant (P1–P6) only if it materially changes status.
* No remediation language.

Completeness assertions (mandatory):
* All Global capability IDs listed for Section 1 MUST appear exactly once each with a non-empty Status.
* If any required cell is blank → FAIL audit integrity and STOP per 0.6.4.

---

## SECTION 2 — AGENT MATRIX EVIDENCE TABLE (KEEP)

Capabilities: 2, 3, 5, 6, 7, 8, 9, 11, 12, 13, 15

### Agent: <agent_name> (Layer <L#>)

**Discovery Identity:** `<identity>` | **File:** `<file_path>` | **Integrity Hash:** `<integrity_hash>`
**SSOT Status:** MATCH / MISMATCH | **MRO Chain:** `<exact mro_chain>`

| ID   | Capability                              | Status          | Evidence Location                          | Gating Invariant Impact | SSOT Validated? |
|------|-----------------------------------------|-----------------|--------------------------------------------|--------------------------|-----------------|
| 2.1  | Validator emits SurgicalManifest        |                 |                                            |                          |                 |
| 2.2  | Validator Safety Emulation (No Side-Effect) |           |                                            | P2                       |                 |
| 2.3  | Validator Permission Check (L5)         |                 |                                            | P5                       |                 |
| 2.4  | Boundary schema validation              |                 |                                            | P6                       |                 |
| 2.5  | Pipe order enforced (1..10)             |                 |                                            | P1                       |                 |
| 2.6  | ≥2 hash mismatches → human escalation   |                 |                                            | P5                       |                 |
| 3.4  | Human Evidence Pack Generation          |                 |                                            | P4                       |                 |
| 3.7  | Policy Challenge/Exception Loop         |                 |                                            | P5                       |                 |
| 5.1  | Dedupe uses SHA-256                     |                 |                                            | P2                       |                 |
| 5.2  | Error signature (type+node+vector_clock) |                 |                                            | P4                       |                 |
| 5.3  | Correlated collapse (Root Scope Pinning)|                 |                                            | P3                       |                 |
| 5.4  | L6 Self-Healing Trigger Emission        |                 |                                            | P1                       |                 |
| 6.5  | RAG Artifact Chain Enforced             |                 |                                            | P4                       |                 |
| 6.8  | Memory Hypostate Persistence            |                 |                                            | P2                       |                 |
| 7.2  | Artifact Guard (Replay Comparison)      |                 |                                            | P5                       |                 |
| 7.2.1| Artifact Guard (Signature Verification) |                 |                                            | P5                       |                 |
| 7.4  | GuardianArtifact Emission (Signed)      |                 |                                            | P5                       |                 |
| 8.1  | Adapters prohibited                     |                 |                                            |                          |                 |
| 8.2  | Mixins for composition                  |                 |                                            |                          |                 |
| 8.3  | Safety mixins LEFT in MRO               |                 |                                            | P1                       | PASS/FAIL       |
| 8.4  | MRO verification via discovery signature|                 |                                            | P2                       | PASS/FAIL       |
| 8.5  | MRO violation → fail                    |                 |                                            | P1                       | PASS/FAIL       |
| 9.1  | Shared mixins generic only              |                 |                                            |                          |                 |
| 9.2  | heal() domain reasoning only            |                 |                                            | P3                       |                 |
| 9.3  | No delegation to adapters/orchestrators |                 |                                            |                          |                 |
| 12.1 | Inter-agent schema validation           |                 |                                            | P6                       |                 |
| 12.2 | Side-effect registry                    |                 |                                            | P3                       |                 |
| 11.1 | TokenCap & Perms Artifacts              |                 |                                            | P1                       |                 |
| 13.1 | Semantic Clock Implementation           |                 |                                            | P2                       |                 |
| 15.1 | Tier III Evacuation Ready               |                 |                                            | P1                       |                 |
| 15.2 | Cognitive Diff Bundle Generation        |                 |                                            | P4                       |                 |

Additional required per-agent gating checks (only as evidence-linked rows in Notes; do not invent new IDs):

* P1 Fail-closed (missing schema/signature/health => reject)
* P3 No silent state mutation (no writes outside execution boundary)
* P4 TraceID propagation to artifacts
* P5 Tokenized authority (if agent participates in write/commit decisions)
* P6 Typed/versioned boundaries

Completeness assertions (mandatory):
* For every emitted per-agent matrix, every row MUST have Status populated (COMPLIANT/MISSING/FAIL).
* If any Status is blank → FAIL audit integrity and STOP per 0.6.4.

---

## SECTION 3 — SUMMARY (KEEP, BUT MUST REFERENCE SECTION A/B/C/D)

| Forensic Summary |
|-----------------|
| Total capabilities evaluated: 16 |
| Global compliance: Y% (COMPLIANT / total) |
| ACTIVE agents audited: N |
| Per-agent compliance table: |

Compliance calculation rule:
* Global compliance % = (#COMPLIANT global capabilities) / 10
* Per-agent compliance % = (#COMPLIANT per-agent rows) / total per-agent rows
* Round to nearest whole integer.

Do NOT estimate percentages if abort condition triggered.

| Agent | Compliance % | FAIL Count | Critical Gates Violated |
|-------|--------------|------------|--------------------------|
| ...   |              |            |                          |

| Non-ACTIVE Agents |
|-------------------|
| GHOST / INVALID / SYNTAX_ERROR agents: |
| • agent_name (file_path) — reason |

| Audit Integrity Confirmations |
| • No remediation language generated |
| • No out-of-scope references |
| • Evaluation bounded to discovery JSON + SSOT + P1–P6 only |

---

## SECTION 4 — GAP SET (DETERMINISTIC) (KEEP, BUT MUST ALSO PRODUCE GAP_ID TABLE IN SECTION C)

Return a table containing ONLY capabilities with status MISSING or FAIL.

| Capability ID | Status (MISSING/FAIL) | Layer Scope (GLOBAL / L0..L6) | Evidence Pointer (if FAIL) |
|--------------|------------------------|------------------------------|----------------------------|

Rules:
* Include GLOBAL capabilities (Section 1) and per-agent capabilities (Section 2) in one unified set.
* If the same capability is missing across multiple agents, list it once as an aggregated Gap with `Impacted Agents: N` in Notes.

Aggregation rules (non-negotiable):
* Aggregation key = `(capability_id, layer_scope)`.
* Status precedence: if ANY underlying instance is FAIL → aggregated Status = FAIL; else MISSING.
* Evidence Pointer: required for FAIL (include ≥1 representative contradiction pointer); optional for MISSING.

Deduplication rule:
* A capability MUST NOT appear twice in Section 4.

---

## SECTION 5 — IMPLEMENTATION PLAN (DETERMINISTIC / NO HEURISTICS) (KEEP, BUT MUST MAP 1:1 TO SECTION C GAP_IDs)

Generate an implementation plan by applying the rules in §17 exactly.

Format:
| Wave | Priority (P0/P1/P2) | Capability IDs | Work Item (noun phrase) | Scope (files/agents) | Acceptance Evidence (exact commands) |
|------|----------------------|---------------|--------------------------|----------------------|--------------------------------------|

Constraints:
* "Work Item" MUST NOT describe code edits; it must describe the missing system element (e.g., "Define Typed Artifact Schemas", "Add Guardian Signature Verification Gate").
* "Scope" MUST be discovery-grounded (agent identities or file paths from discovery JSON). If unknown, write `UNKNOWN (requires discovery evidence)` and treat as blocking for that Wave.
* "Acceptance Evidence" MUST be fixed commands (pytest targets, hash checks, schema validations) and MUST be sufficient to prove closure of the referenced capability IDs.

Determinism rule:
* Acceptance Evidence commands MUST NOT contain placeholders except `<repo_root>`.
* If `<repo_root>` used, it MUST match discovery `meta.root_path`.

Fallback evidence rule (mandatory):
* If no pytest target is discoverable for a work item, Acceptance Evidence MUST include:
  1) a schema/model import + instantiation check for the relevant artifact(s), AND
  2) a deterministic CLI/script validation (e.g., discovery run, schema validator run), AND
  3) a repo-wide grep/rg check proving wiring presence for the capability boundary.

---
