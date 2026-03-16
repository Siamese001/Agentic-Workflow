ROLE
Deterministic Codemap Deepener (Atomic Zero-Loss Architecture)

OBJECTIVE
Generate additional codemap outputs that clarify the system at “atomic” granularity (single responsibility units + invariants + call edges), consistent with the L0–L6 flow provided.

CONSTRAINTS
- Do not change code.
- Use only repository inspection (rg, tree, open files).
- Every codemap block must include:
  (a) entrypoint,
  (b) NON-MUTATING vs MUTATING classification for every step,
  (c) invariants embedded inline inside the ASCII boxes,
  (d) file:line anchors for each step.
- No duplication: each codemap block must cover a distinct atomic view.
- Provide exactly 6 codemap blocks.
- Each block must be “widescreen” with a single master flow line per stage and explicit seam boundaries.
- If any path/anchor is uncertain, locate it first via rg; do not guess.

OUTPUT FORMAT (STRICT)
Return exactly 6 sections. For each section:
TITLE:
SCOPE:
ATOMIC FLOW (ASCII):
ANCHORS (file:line list):

Produce codemap blocks only. No commentary.

REQUIRED BLOCKS (EXACTLY THESE 6)
1) TITLE: L0→L2 Envelope: Single Durable Mutation Point
   - Show L2.0 validate -> L2.1 guardian -> L2.2 commit -> L2.3 heal retry loop
   - Invariants embedded in boxes:
     - Only L2.2 may do durable writes
     - Rollback integrity verified
     - No same-cycle signal influence

2) TITLE: Manifest Contract & Hash Binding
   - Show manifest structure + where hashes are validated
   - Invariants:
     - Missing hashes => reject (when required)
     - Hash mismatch => reject
     - Hashes computed from canonical bytes

3) TITLE: Guardian Gate: Allow/Block/Escalate & Budgets
   - Show guardian decision creation, enforcement points, violation surfacing
   - Invariants:
     - Block occurs before commit
     - Escalation changes mode only via routing policy
     - Decision logged/snapshotted

4) TITLE: L4 Retrieval: Anchored Results & Coverage Enforcement
   - Show retrieval -> anchors -> reasoning consumption -> enforcement of coverage
   - Invariants:
     - Every retrieved chunk has anchor
     - Reasoning referencing retrieval must include anchors
     - Anchors include doc_id/chunk_id/offsets/version_hash

5) TITLE: L3 Orchestration: Depth, Routing, Deterministic Threshold Reads
   - Show mission start -> agent loop -> depth breaker -> mode selection
   - Invariants:
     - Depth breaker reads versioned config
     - No inline constants for thresholds
     - Mode routing is policy driven

6) TITLE: L6 Detection → L4 Persistence → L0 Time-Shift Routing
   - Show detection computed at end -> stored with commit tick -> next run reads prior-only -> routing decision
   - Invariants:
     - L6 is NON-AUTHORITY (no blocking)
     - Prior-only semantics: commit_tick < execution_start_tick
     - Same-cycle signal is structurally invisible

COMMANDS (REQUIRED FOR ANCHORS)
- rg -n "class V15ExecutionGateway|def execute\\(|_validate_manifest|_guardian_validate|_commit_mutation|_heal_and_retry" agentic_core
- rg -n "GuardianDecision|validate\\(|validate_manifest_hashes|ManifestHashError" agentic_core
- rg -n "RetrievalAnchor|AnchoredResult|enforce_anchor_coverage" agentic_core
- rg -n "depth_breaker|max_hops|max_k|get_active_configs\\(" agentic_core
- rg -n "DetectionSignal|store_detection_signal|fetch_latest|timeshift_router|commit_tick|execution_start_tick" agentic_core

ACCEPTANCE CRITERIA
- Exactly 6 codemap blocks produced.
- Every step labeled MUTATING or NON-MUTATING.
- Invariants embedded inside the ASCII boxes.
- Every box has at least one verified file:line anchor.
- No contradictions across blocks.

DELIVERABLE
- Codemap output only in the specified format.
