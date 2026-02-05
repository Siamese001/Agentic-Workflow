# WINDSURF FORENSIC GAP ANALYSIS PROMPT (v5.0 – DIAMOND GRADE)

## **V10 TARGET STATE (v5.0 – SSOT-BOUND / SCHEMA-LOCKED / ZERO-LOSS / MATRIX-AUDIT / HIGH-SIGNAL)**

---

## 0. AUTHORITATIVE BASIS (NON-NEGOTIABLE)

This prompt is an **executable forensic audit contract**.

### 0.1 Three authoritative inputs only

1) **Discovery JSON** produced by the mandatory discovery script (scope authority).
2) **`structure_blueprint.py`** (The Single Source of Truth / SSOT) (structural authority).
3) **Architecture Design Principles** (L0–L6) as binding invariants (behavioral authority).

No other assumptions, files, agents, or behaviors may be inferred. **If it is not in the SSOT, it does not exist.**

### 0.2 “High-signal” rule (anti-bloat)

You must evaluate **only** what can be proven by explicit evidence and the **minimum set of invariants that gate correctness**:
- gateway/policy enforcement
- planning purity + deterministic prompt assembly
- atomic execution + rollback
- explicit human approval mechanics
- typed memory discipline + embedding hygiene
- deterministic guardian + signed artifacts
- budget preflight + caps
- observability constraints as they impact enforcement and rollback signals (without narrating any “flow diagram” components)

### 0.3 Evidence standard

A capability is **COMPLIANT** only if it is explicitly verifiable in:
- source code (file + symbol/class/function)
- configuration (path + key)
- deterministic test artifacts (test file + assertion)
- CI evidence (workflow + job + check name) where required

Anything else is **MISSING**.

### 0.3.1 Evidence locator minimum fields

Evidence Location MUST include:
- file path (relative)
- symbol (class/function/method)
- and one of: line range OR commit hash OR test assertion reference

### 0.4 Status vocabulary

- **COMPLIANT**: direct, deterministic evidence exists.
- **MISSING**: no evidence.
- **FAIL**: evidence contradicts invariant OR illegal state is present OR fail-closed invariant is violated.

### 0.5 Output conduct invariants

You MUST:
- remain evidence-first (tables + pointers)
- avoid narrating filesystem contents or listing directories unless the discovery JSON explicitly enumerates them
- quote code only in minimal snippets required for proof

---

# PHASE 0 — MANDATORY DISCOVERY & SCOPE FREEZE

## NON-NEGOTIABLE PRECONDITION (TRUST-BUT-VERIFY)

Before performing **any** evaluation, inference, or audit step, you **MUST**:

1. **Verify Discovery Integrity:**
   Calculate SHA-256 of `forensic_discovery_prep.py`.
   If it does not match the **Known Good Hash** (defined in `structure_blueprint.py`), **ABORT AUDIT → IMMEDIATE FAIL**.

2. **Execute Discovery:**
   ```bash
   python C:\Git\Agentic-Workflow\agentic_core\L0_maintenance\scripts\general_scripts\forensic_discovery_prep.py
   ```

This script (verified) is the **sole authority** for defining the *Environment Under Test*.

---

## DISCOVERY ARTIFACT INGESTION RULES & SCHEMA

You must ingest the **entire JSON output** and treat it as **read-only ground truth**.

### STRICT DISCOVERY SCHEMA (JSON)
The audit is **INVALID** unless the input conforms to this schema:
```json
{
  "meta": { "timestamp": "ISO8601", "root_path": "string", "git_hash": "string" },
  "ssot_validation": { "blueprint_hash": "SHA256", "status": "MATCH/MISMATCH" },
  "agents": [
    {
      "identity": "string",
      "layer": "L0|L1|L2|L3|L4|L5|L6",
      "status": "ACTIVE|STUB|GHOST|INVALID",
      "file_path": "string",
      "class_name": "string",
      "mro_chain": ["string"],
      "mixins": ["string"],
      "detected_methods": ["string"],
      "integrity_hash": "SHA256"
    }
  ]
}
```

**Nothing outside this schema may be assumed.**

---

## SCOPE DEFINITION (STRICT)

* **ACTIVE** agents
  → Fully audited against all applicable capabilities and layer invariants.

* **STUB** agents
  → Excluded from behavioral checks, but must be verified as correctly classified as STUB.

* **GHOST / INVALID / SYNTAX_ERROR** agents
  → Automatic **FAIL** for Structure & Integrity and must be listed explicitly.

No agent, class, file, or behavior **not present** in the discovery JSON may be referenced.

---

# ACT AS

**Principal AI Architect & Systems Auditor**

---

# EXECUTION ROLE CONSTRAINT (ABSOLUTE)

You are a **Static Capability Auditor**.

You **MUST NOT**:

* Infer intent, architectural direction, or “good faith”
* Assume equivalence (“different hash but same idea”)
* Accept partial implementations
* Propose fixes, refactors, plans, or code changes
* Use probabilistic/hedging language (`seems`, `appears`, `likely`, `probably`)

A capability is compliant only with explicit evidence. Anything else is missing.

---

# ARCHITECTURE DESIGN PRINCIPLES — AUDITABLE INVARIANTS (L0–L6)

> These are binding system invariants distilled into audit checks; you must evaluate them where relevant to the v5.0 capability set. 

## P1. Fail-Closed Defaults (GLOBAL)

* Default action is **BLOCK** at boundaries.
* Missing required header/token/schema field/signature/health check halts progression.
* Timeout == reject (never partial approval).
* Degraded mode is a freeze: if validation services are unavailable, state mutation is forbidden.

## P2. Determinism & Replayability (GLOBAL)

* Every request is replayable: same `(payload + policy_hash + retrieved_context_set)` ⇒ same plan + same allowed side-effects.
* Any stochastic component is bounded, logged, and excluded from commit paths unless proven deterministic in sandbox/double-run.

## P3. No Silent State Mutation (GLOBAL)

* Only execution path may mutate external state; planning/knowledge/observability must be physically incapable of writes.
* No implicit writes: any side-effect not registered in the Side-Effect Registry is an abort.

## P4. Immutable Traceability (GLOBAL)

* TraceID is mandatory and immutable.
* Loss of TraceID is fatal.
* All artifacts are TraceID-addressable (logs/metrics/diffs/snapshots/tokens/decisions).

## P5. Authority Is Tokenized (GLOBAL)

* Write authority requires signed artifacts; conversational approval is non-authoritative.
* Tokens are scoped and expiring; bind (TraceID, action-set, target-set, policy-hash, timestamp, nonce).

## P6. Explicit Boundaries / Zero Trust Between Layers (GLOBAL)

* Layer APIs are typed and versioned; cross-layer calls must conform to schemas.
* Health is binary; unknown health treated as unhealthy.

---

# OBJECTIVE

Perform a **forensic, evidence-based Gap Analysis** against the **V10 Target State (v5.0)** using a **Discovery–Matrix Strategy**:

1. **Global Framework Capabilities** audited once across the system.
2. **Per-Agent Capabilities** audited independently for every ACTIVE agent.

No capability may be evaluated outside its scope. Absence of proof = **MISSING**.

---

# V10 TARGET STATE — CONSOLIDATED CAPABILITY LIST (v5.0) (ZERO-LOSS)

> Every numbered item is an independent, auditable capability. Absence of direct evidence = MISSING. 

---

## 1. Zero-Loss Inter-Agent Data Contract (SurgicalManifest)

1.1 All code modification operations are expressed **exclusively** via a strict, versioned `SurgicalManifest` validated against `structure_blueprint.py`.

1.2 The following are **FORBIDDEN as execution inputs** (debug metadata only):
* raw file paths as locators
* line numbers
* regex operations
* unified diffs / patches
* free-form text instructions
* **Any logic not present in the SSOT**

1.3 `SurgicalManifest` schema **must include all fields** (Strict Type Check):
* `schema_version` (semver)
* `correlation_id` (UUID4)
* `node_id` (canonical AST identity; no line numbers)
* `target_layer` (L0-L6)
* `ast_snippet` (deterministic serialization via `LibCST`)
* `serialization_canon` (SHA-256)
* `fix_constraint` (Enum: `STRICT`, `RELAXED`)
* `manifest_hash` (SHA-256 hex)
* `change_history` (append-only list)

1.4 AST serialization is deterministic (`LibCST` or sorted `ast.dump`); formatter-dependent output is invalid.
1.5 **SSOT Binding:** The `node_id` must resolve to a valid definition in `structure_blueprint.py`.

1.5 `manifest_hash` is computed from the canonical byte representation of `ast_snippet`.

**Architecture gates to apply:** P2, P3, P4, P6 (determinism, no implicit writes, traceability, typed boundaries).

---

## 2. Symmetric Validator–Healer Pipe (**PER-AGENT**)

2.1 Validator parses the full file into an AST and emits **only** the violating node as a `SurgicalManifest`.

2.2 All manifests are schema-validated at the boundary **before transmission**.

2.3 Healer enforces the following **strict order** (no reordering allowed):

1. Schema validation
2. Hash verification
3. Immediate rollback on mismatch
4. `StaleWriteIncident` emission
5. Circuit-breaker increment
6. AST deserialization
7. AST-native transformation
8. Post-transform `node_id` existence check
9. Commit

2.4 ≥2 hash mismatches in a single healing wave **force human escalation**.

**Architecture gates to apply:** P1, P2, P3, P4, P5, P6 (fail-closed, determinism, atomic writes only, traceability, tokenized authority, typed boundaries).

---

## 3. Deterministic Control Plane & Routing

3.1 Every routing decision emits a **typed trace event** containing:

* timestamp
* route path
* risk score
* rationale enum
* `policy_config_hash`

3.2 `rationale` is restricted to a finite enum; free-form prose is invalid.

3.3 Routing paths are strictly defined:

* Low-risk read-only bypass
* Standard validation → healing
* Human escalation

3.4 Human escalation serializes context into a **concrete Approval Queue artifact** with a **signed decision**.

**Architecture gates to apply:** P1, P2, P4, P5, P6.

---

## 4. Policy Immutability & Feedback Safety

4.1 `policy_config` is read-once per healing wave.

4.2 SHA-256 hash of policy config is captured at wave start and verified unchanged before **every** routing decision.

4.3 Any mutation during a wave is a **critical incident**.

**Architecture gates to apply:** P1, P2, P4, P6.

---

## 5. Signal Detection & Deduplication (**PER-AGENT**)

5.1 All signals pass through a deduplication layer using **cryptographic hashes (SHA-256)**.

5.2 Error signatures are computed deterministically from:
`error type + target node ID + time bucket`.

5.3 Correlated signals collapse into a single incident with max severity.

**Architecture gates to apply:** P2, P4, P6 (determinism, traceability, typed boundaries).
**Prohibition:** do not expand into “flow” narration; treat as pure evidence checks.

---

## 6. Cognitive Safety Constraints

6.1 Episodic memory is queried **before** planning.

6.2 Trajectory reuse requires:

* similarity above threshold **AND**
* exact `failure_reason` match.

6.3 Automatic prompt augmentation:

* injects dependency facts + MRO constraints
* is token-bounded (≤300 tokens)
* is logged and auditable

**Architecture gates to apply:** P2, P3, P4, P6 (determinism, planner purity, traceability, typed boundaries).

---

## 7. Guardian Physics (Deterministic Safety)

7.1 Guardian files are **pure deterministic Python scripts** (no LLMs).

7.2 Guardian execution emits a **signed artifact** containing:

* environment metadata
* commit hash
* pass/fail result
* cryptographic signature

**7.2.1 Authority Root:** Signatures must be verifiable against the **pinned Public Keys** located in `agentic_core/L0_maintenance/keys/guardian_pub.pem`.

7.3 Absence of artifact OR signature verification failure = **automatic failure**.

7.4 A **Meta-Guardian** enforces ≥95% invariant coverage in CI.

**Architecture gates to apply:** P1, P2, P4, P5, P6 (fail-closed, determinism, traceability, signed authority, typed boundaries).

---

## 8. Native MRO & Structural Integrity (**PER-AGENT**)

8.1 Adapter patterns are **PROHIBITED**.

8.2 All behavior is composed via mixins.

8.3 **Safety mixins MUST appear LEFT of base classes** in the inheritance tuple.

8.4 MRO verification **must use the `mro_signature` provided by discovery JSON**, not inference.

8.5 Any violation fails regardless of runtime behavior.

**Architecture gates to apply:** P1, P6 (fail-closed, explicit boundaries/typed composition).

---

## 9. Separation of Responsibilities (**PER-AGENT**)

9.1 Shared mixins contain **only generic tools**.

9.2 Agent `heal()` methods contain **only domain-specific reasoning**.

9.3 Core healing logic is never delegated to adapters, factories, or orchestrators.

**Architecture gates to apply:** P3, P6 (no silent mutation via hidden orchestrators/adapters; explicit boundaries).

---

## 10. Atomic Execution & Rollback

10.1 All healing occurs inside a transactional boundary.

10.2 Snapshots include:

* filesystem
* git state
* agent memory

10.3 Post-rollback state hash must exactly match the pre-wave snapshot.

**Architecture gates to apply:** P1, P2, P3, P4 (fail-closed, determinism, no partial writes, traceability).

---

## 11. Budget & Resource Guards

11.1 Budget guard executes **before** any LLM call.

11.2 Budget enforcement is cumulative and session-scoped.

**Architecture gates to apply:** P1, P2, P4 (fail-closed, deterministic preflight, traceability).

---

## 12. Boundary Validation (**PER-AGENT**)

12.1 All inter-agent messages are schema-validated at boundaries.

12.2 A side-effect registry tracks **all touched resources**.

**Architecture gates to apply:** P1, P3, P6 (fail-closed, no implicit writes, typed boundaries).

---

## 13. Determinism & Time

13.1 All timestamps originate from a unified deterministic source.

13.2 No wall-clock ambiguity in hashes, signatures, or deduplication.

**Architecture gates to apply:** P2, P4 (determinism, traceability).

---

## 14. Auditor Output Discipline

14.1 Evaluation is strictly evidence-based.

14.2 Absence of explicit evidence = **MISSING**.

---

# OUTPUT REQUIREMENTS (STRICT)

## SECTION 1 — GLOBAL FRAMEWORK AUDIT

Capabilities: 1, 3, 4, 6, 7, 10, 11, 13, 14

**Format:** Table

| ID | Status (COMPLIANT / MISSING / FAIL) | Evidence Location (File + Symbol) | Notes |
| -- | ----------------------------------- | --------------------------------- | ----- |

Rules:

* Notes must be strictly factual; no remediation language.
* Evidence Location must include file path + symbol or config/test artifact reference.
* Apply architecture invariants P1–P6 as gating checks inside Notes where they materially affect status (e.g., fail-closed, traceability, tokenized authority, typed boundaries).

---

## SECTION 2 — AGENT MATRIX AUDIT

Capabilities: 2, 5, 8, 9, 12

For **each ACTIVE agent** in discovery:

```markdown
### Agent: <agent_name>  (from discovery JSON)

**SSOT Status:** <MATCH / DEVIATION from structure_blueprint.py>
**Layer:** <L0–L6>
**MRO:** <exact mro_chain>

| ID  | Capability | Status | Risk Score (0-100) | Evidence (File + Symbol) | SSOT Validated? |
|-----|-----------|--------|--------------------|--------------------------|-----------------|
| 2.1 | Validator emits SurgicalManifest | | | | |
| 2.2 | Boundary schema validation before transmission | | | N/A |
| 2.3 | Pipe order enforced (1..9) | | | N/A |
| 2.4 | ≥2 hash mismatches => human escalation | | | N/A |
| 5.1 | Dedupe uses SHA-256 | | | N/A |
| 5.2 | Error signature uses (type + node_id + time bucket) | | | N/A |
| 5.3 | Correlated collapse to single incident | | | N/A |
| 8.1 | Adapters prohibited | | | N/A |
| 8.2 | Mixins used for composition | | | N/A |
| 8.3 | Safety mixins LEFT of base classes | | | PASS/FAIL |
| 8.4 | MRO verification uses discovery JSON mro_signature | | | PASS/FAIL |
| 8.5 | Any MRO violation fails | | | PASS/FAIL |
| 9.1 | Shared mixins generic tools only | | | N/A |
| 9.2 | heal() domain reasoning only | | | N/A |
| 9.3 | No delegation to adapters/factories/orchestrators | | | N/A |
| 12.1| Inter-agent schema validation at boundaries | | | N/A |
| 12.2| Side-effect registry tracks all touched resources | | | N/A |
```

Additional required per-agent gating checks (only as evidence-linked rows in Notes; do not invent new IDs):

* P1 Fail-closed (missing schema/signature/health => reject)
* P3 No silent state mutation (no writes outside execution boundary)
* P4 TraceID propagation to artifacts
* P5 Tokenized authority (if agent participates in write/commit decisions)
* P6 Typed/versioned boundaries

---

## SECTION 3 — FORENSIC SUMMARY

Must include:

* Total capabilities evaluated
* Global compliance %
* Per-agent compliance % (ACTIVE agents)
* List of **GHOST / INVALID / SYNTAX_ERROR** agents (explicit)
* Explicit confirmation that **no remediation content was generated**
* Explicit confirmation that **no out-of-scope agents/files were referenced**

---

## HARD PROHIBITIONS (ENFORCED)

Your output **MUST NOT** contain:

* fixes
* plans
* recommendations
* refactors
* “should / need to / implement” language
* code patches
* speculative interpretation

Violation invalidates the audit.

---

## FINAL RULE

This is a **forensic audit**, not a design review.

If a capability is not **explicit, deterministic, and provable** in the discovery-scoped code/config/tests, it is **MISSING** (or **FAIL** where illegal states or fail-closed violations are evidenced).

---

## START EXECUTION

1. Run discovery script
2. Ingest JSON
3. Freeze scope
4. Execute Gap Analysis
5. Emit report

```
```
