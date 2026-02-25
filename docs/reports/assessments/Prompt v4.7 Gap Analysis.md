

# 🔒 WINDSURF FORENSIC GAP ANALYSIS PROMPT (v4.7)

## **V10 TARGET STATE (v4.7 – DISCOVERY-FIRST / ZERO-LOSS / MATRIX-AUDIT / SCRIPT-ALIGNED)**

---

## PHASE 0 — MANDATORY DISCOVERY & SCOPE FREEZE

### **NON-NEGOTIABLE PRECONDITION**

Before performing **any** evaluation, inference, or audit step, you **MUST** execute the discovery script exactly once and treat its output as immutable:

```bash
python C:\Git\Agentic-Workflow\agentic_core\L0_maintenance\scripts\forensic_discovery_prep.py
```

This script is the **sole authority** for defining the *Environment Under Test* .

---

### **DISCOVERY ARTIFACT INGESTION RULES**

You must ingest the **entire JSON output** and treat it as **read-only ground truth**.

The artifact defines **all** of the following, and **nothing outside it may be assumed**:

* Agent identity
* Agent file path
* Agent layer
* Agent class name
* Exact declared MRO signature (base class order)
* Agent status (`ACTIVE | STUB | GHOST | INVALID | SYNTAX_ERROR`)
* Methods detected on the primary agent class

---

### **SCOPE DEFINITION (STRICT)**

* **ACTIVE** agents
  → **Fully audited** against all PER-AGENT capabilities.

* **STUB** agents
  → **Excluded from behavioral checks**, but **must** be verified as correctly classified as STUB.

* **GHOST / INVALID / SYNTAX_ERROR** agents
  → **Automatic FAILURE** for **Structure & Integrity**
  → Must be listed explicitly in the final report.

No agent, class, or file **not present in the discovery JSON** may be audited, referenced, or inferred.

---

## ACT AS

**Principal AI Architect & Systems Auditor**

---

## EXECUTION ROLE CONSTRAINT (ABSOLUTE)

You are a **Static Capability Auditor**.

You **MUST NOT**:

* Infer intent, architectural direction, or “good faith”
* Assume equivalence (“different hash but same idea”)
* Accept partial implementations
* Propose fixes, refactors, plans, or code changes
* Use probabilistic or hedging language
  (`seems`, `appears`, `likely`, `probably`)

A capability is **COMPLIANT** *only* if it is **explicitly present and verifiable** in:

* Source code referenced by discovery
* Configuration referenced by discovery
* Deterministic test artifacts referenced by discovery

Anything else is **MISSING**.

---

## OBJECTIVE

Perform a **forensic, evidence-based Gap Analysis** against the **V10 Target State (v4.7)** using a **Discovery-Matrix Strategy**:

1. **Global Framework Capabilities**
   Audited **once** across the system.

2. **Per-Agent Capabilities**
   Audited **independently for every ACTIVE agent** discovered in Phase 0.

No capability may be evaluated outside its designated scope.

---

# V10 TARGET STATE — CONSOLIDATED CAPABILITY LIST (v4.7)

> **Every numbered item below is an independent, auditable capability.**
> Absence of direct evidence = **MISSING**.

---

## 1. Zero-Loss Inter-Agent Data Contract (SurgicalManifest)

1.1 All code modification operations are expressed **exclusively** via a strict, versioned `SurgicalManifest`.

1.2 The following are **FORBIDDEN as execution inputs** (debug metadata only):

* raw file paths as locators
* line numbers
* regex operations
* unified diffs / patches
* free-form text instructions

1.3 `SurgicalManifest` schema **must include all fields**:

* `schema_version` (semver)
* `node_id` (canonical AST identity; no line numbers)
* `ast_snippet` (deterministic serialization)
* `serialization_canon`
* `fix_constraint`
* `manifest_hash` (SHA-256 hex)
* `change_history` (append-only)

1.4 AST serialization is deterministic (`LibCST` or sorted `ast.dump`); formatter-dependent output is invalid.

1.5 `manifest_hash` is computed from the canonical byte representation of `ast_snippet`.

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

---

## 4. Policy Immutability & Feedback Safety

4.1 `policy_config` is read-once per healing wave.

4.2 SHA-256 hash of policy config is captured at wave start and verified unchanged before **every** routing decision.

4.3 Any mutation during a wave is a **critical incident**.

---

## 5. Signal Detection & Deduplication (**PER-AGENT**)

5.1 All signals pass through a deduplication layer using **cryptographic hashes (SHA-256)**.

5.2 Error signatures are computed deterministically from:
`error type + target node ID + time bucket`.

5.3 Correlated signals collapse into a single incident with max severity.

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

---

## 7. Guardian Physics (Deterministic Safety)

7.1 Guardian files are **pure deterministic Python scripts** (no LLMs).

7.2 Guardian execution emits a **signed artifact** containing:

* environment metadata
* commit hash
* pass/fail result
* cryptographic signature

7.3 Absence of artifact = **automatic failure**.

7.4 A **Meta-Guardian** enforces ≥95% invariant coverage in CI.

---

## 8. Native MRO & Structural Integrity (**PER-AGENT**)

8.1 Adapter patterns are **PROHIBITED**.

8.2 All behavior is composed via mixins.

8.3 **Safety mixins MUST appear LEFT of base classes** in the inheritance tuple.

8.4 MRO verification **must use the `mro_signature` provided by discovery JSON**, not inference.

8.5 Any violation fails regardless of runtime behavior.

---

## 9. Separation of Responsibilities (**PER-AGENT**)

9.1 Shared mixins contain **only generic tools**.

9.2 Agent `heal()` methods contain **only domain-specific reasoning**.

9.3 Core healing logic is never delegated to adapters, factories, or orchestrators.

---

## 10. Atomic Execution & Rollback

10.1 All healing occurs inside a transactional boundary.

10.2 Snapshots include:

* filesystem
* git state
* agent memory

10.3 Post-rollback state hash must exactly match the pre-wave snapshot.

---

## 11. Budget & Resource Guards

11.1 Budget guard executes **before** any LLM call.

11.2 Budget enforcement is cumulative and session-scoped.

---

## 12. Boundary Validation (**PER-AGENT**)

12.1 All inter-agent messages are schema-validated at boundaries.

12.2 A side-effect registry tracks **all touched resources**.

---

## 13. Determinism & Time

13.1 All timestamps originate from a unified deterministic source.

13.2 No wall-clock ambiguity in hashes, signatures, or deduplication.

---

## 14. Auditor Output Discipline

14.1 Evaluation is strictly evidence-based.

14.2 Absence of explicit evidence = **MISSING**.

---

# OUTPUT REQUIREMENTS (STRICT)

---

## SECTION 1 — GLOBAL FRAMEWORK AUDIT

(Capabilities: 1, 3, 4, 6, 7, 10, 11, 13, 14)

**Format:** Table

| ID | Status | Evidence Location (File + Symbol) | Notes |
| -- | ------ | --------------------------------- | ----- |

---

## SECTION 2 — AGENT MATRIX AUDIT

(Capabilities: 2, 5, 8, 9, 12)

For **each ACTIVE agent** in discovery:

```markdown
### Agent: <agent_name>  (from discovery JSON)

Declared MRO Signature:
<exact mro_signature array from discovery>

| ID  | Capability | Status | Evidence (File + Symbol) | MRO Check |
|-----|-----------|--------|--------------------------|-----------|
| 2.1 | Validator |        |                          | N/A       |
| 8.3 | MRO Order |        |                          | PASS/FAIL |
```

---

## SECTION 3 — FORENSIC SUMMARY

* Total capabilities evaluated
* Global compliance %
* Per-agent compliance %
* List of **GHOST / INVALID / SYNTAX_ERROR** agents
* Explicit confirmation that **no remediation content was generated**

---

## HARD PROHIBITIONS (ENFORCED)

Your output **MUST NOT** contain:

* fixes
* plans
* recommendations
* “should / need to / implement” language

Violation invalidates the audit.

---

## FINAL RULE

This is a **forensic audit**, not a design review.

If a capability is not **explicit, deterministic, and provable** in the code or discovery artifact, it is **MISSING**.

---

## START EXECUTION

1. Run discovery script
2. Ingest JSON
3. Freeze scope
4. Execute Gap Analysis
5. Emit report

---
