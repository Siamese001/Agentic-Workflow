---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-lic-p3-multi-touch-resurfacing-readiness.md'
original_relative_path: '_archive\\2026-05\\apps-lic-p3-multi-touch-resurfacing-readiness.md'
source_sha256: 571ccea859f239724c223b2bb6a1e205d54b6e2a9339c0570884e5c7047e8a01
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic P3 Multi-Touch & Resurfacing — Readiness Design

**Plan ID:** apps-lic-p3-multi-touch-resurfacing-readiness  
**Parent Plan:** apps-lic-signal-enhancements-p2p3-spine-aligned  
**Status:** Draft → Waiting → Live  
**Created:** 2026-05-05  
**Target Completion:** Deferred pending state/HITL/L4 policy readiness

---

## 1. Executive Summary

This child plan defines the P3 signal enhancement scope (multi-touch cadence and resurfacing triggers) that was **intentionally deferred** from the parent P2/P3 plan. P3 requires infrastructure that does not yet exist in the `apps_lic` spine: durable state persistence, HITL integration for re-engagement decisions, and L4 coordination fabric policy for cross-touch state management.

**Deferred Scope Principle:** P3 concepts are preserved and designed, but implementation is gated on prerequisite system capabilities. This plan captures the design to enable rapid activation when prerequisites are met.

---

## 2. Prerequisites for P3 Activation

| Prerequisite | Current Status | Blocker Until |
|--------------|----------------|---------------|
| L4 State Persistence (UWG) | Partial — no app-specific state tables | L4 adds `apps_lic_touch_state` table |
| HITL Re-engagement Policy | Undefined | L5 defines re-engagement HITL rules |
| L4 Coordination Fabric | Basic — no time-series triggers | Coordination adds scheduled wake |
| Cross-Touch Identity | Not implemented | Identity propagation for recipient + sender pair |
| apps_lic State Machine | Not implemented | State DAG design + state transition policy |

---

## 3. P3a: Multi-Touch Cadence Engine

### 3.1 Purpose
Orchestrates sequences of touches for high-value recipients where single-touch is insufficient. Manages timing, content evolution, and escalation based on recipient engagement signals.

### 3.2 State Model
```
TOUCH_STATE_MACHINE:
  states:
    - initial_draft        # First outreach composed
    - sent                 # Draft sent to recipient
    - opened               # Recipient opened message
    - clicked              # Recipient clicked link
    - replied              # Recipient replied
    - no_response_7d       # 7 days no response
    - no_response_14d      # 14 days no response
    - resurfaced           # P3b triggered
    - escalated_hitl       # HITL review required
    - closed_won           # Positive outcome
    - closed_lost          # Negative outcome / stop

  transitions:
    initial_draft → sent
    sent → opened | no_response_7d
    opened → clicked | no_response_14d
    clicked → replied | no_response_14d
    no_response_7d → resurfaced | escalated_hitl
    no_response_14d → closed_lost | escalated_hitl
```

### 3.3 Cadence Policies

**Executive Track (CTO/VP Eng):**
- Touch 1: Asymmetric insight (P2a) + technical tone (P2b)
- Touch 2 (7d no-response): Differentiated proof point (P2c competitive landscape)
- Touch 3 (14d no-response): HITL review for warm intro vs. close

**Recruiter Track:**
- Touch 1: Fit signal (compact arc)
- Touch 2 (3d no-response): Role evolution update
- Touch 3 (7d no-response): Close with "keep in touch"

### 3.4 Implementation Gaps
- State persistence: Need `touch_sequence_state` table in L4
- State transition hooks: DAG stages for each transition
- Timer triggers: Coordination fabric scheduled wakes

---

## 4. P3b: Resurfacing Trigger Detection

### 4.1 Purpose
Detects events that justify re-engagement with previously non-responsive recipients, triggering a new touch with updated context.

### 4.2 Trigger Taxonomy

| Trigger | Signal Source | Privacy Sensitivity | HITL Required |
|---------|---------------|---------------------|---------------|
| Role change (promotion) | Public profile update | Low | No |
| Company funding | Public announcement | Low | No |
| New relevant content | Recipient blog/post | Low | No |
| Company expansion | News/triggers | Low | No |
| Prior engagement anniversary | Time-based | Medium | Optional |
| Referral mention | Third-party signal | High | Yes |

### 4.3 Signal Ingestion Architecture
```
Resurfacing Signal Flow:
  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
  │ External Signal │────▶│ Signal Validator │────▶│ Trigger Matcher │
  │ (RSS/API/Alert) │     │ (permission check)│     │ (recipient map) │
  └─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                           ┌──────────────────────────────┘
                           ▼
              ┌──────────────────────┐
              │ HITL Gate (if required)
              │ (L5 policy decision) │
              └──────────┬───────────┘
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
   ┌─────────────────┐      ┌──────────────────┐
   │ Approve Resurface│      │ Block / Delay    │
   │ → Create touch   │      │ → Log reason     │
   └─────────────────┘      └──────────────────┘
```

### 4.4 Implementation Gaps
- Signal ingestion pipeline: Not implemented
- Signal validator: Privacy/permission engine needed
- Trigger matcher: Recipient→signal association logic
- HITL integration: L5 policy for sensitive triggers

---

## 5. State Persistence Design

### 5.1 Required L4 Schema
```sql
-- apps_lic_touch_state table (proposed)
CREATE TABLE apps_lic_touch_state (
    state_id UUID PRIMARY KEY,
    recipient_id TEXT NOT NULL,           -- Hashed recipient identifier
    sender_id TEXT NOT NULL,              -- Hashed sender identifier  
    recipient_class TEXT,
    current_state TEXT NOT NULL,          -- From TOUCH_STATE_MACHINE
    touch_count INTEGER DEFAULT 0,
    first_touch_at TIMESTAMP,
    last_touch_at TIMESTAMP,
    next_scheduled_wake TIMESTAMP,        -- For coordination fabric
    sequence_context JSONB,                -- Narrative arc context from previous touches
    aggregate_coherence_score FLOAT,      -- P2a: running coherence
    tone_calibration_history JSONB,       -- P2b: archetype evolution
    competitive_context_refs JSONB,       -- P2c: differentiators used
    resurfacing_triggers_acked JSONB,    -- P3b: triggers already surfaced
    hitl_escalation_history JSONB,         -- P3: HITL decisions
    outcome_resolution TEXT,               -- closed_won / closed_lost / open
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(recipient_id, sender_id)
);

CREATE INDEX idx_touch_state_next_wake ON apps_lic_touch_state(next_scheduled_wake) 
WHERE outcome_resolution = 'open';
```

### 5.2 State Access Patterns
- **Read:** Current state lookup by (recipient, sender) pair
- **Write:** State transition with optimistic locking (version/checksum)
- **Query:** All open sequences with wake time <= NOW() (for coordination polling)

---

## 6. HITL Integration for Re-engagement

### 6.1 HITL Triggers
HITL review is **required** for:
- 3+ touch sequences (escalation threshold)
- Any resurfacing trigger classified "High" sensitivity
- State transition to `escalated_hitl`
- Any competitive claim not in P2c source_refs

### 6.2 HITL Decision Schema
```yaml
HITLReengagementDecision:
  hitl_review_id: UUID
  recipient_id_hash: string
  sender_id_hash: string
  decision_type: [approve_touch, approve_resurface, modify_content, block_close]
  reviewer_notes: string
  content_modifications:  # If modify_content
    tone_changes: [shift_formal, shift_casual]
    arc_modifications: [add_proof_point, soften_ask]
    omit_sections: [competitive_landscape]
  approved_touch_count: integer  # If approving sequence extension
  next_hitl_threshold: integer   # When to escalate again
  decided_at: timestamp
  reviewer_attestation: string     # Identity + rationale binding
```

### 6.3 Implementation Gaps
- L5 HITL policy: Define re-engagement review criteria
- L6 observability: Log HITL decisions to `eval_harness_outcome` ledger
- L4 integration: HITL decision → state machine transition

---

## 7. P3 Integration with P2 Engines

### 7.1 P2a Narrative Arc in Multi-Touch
- Touch 1: Full arc (opener → hook → proof → ask)
- Touch 2+: Contextual arc referencing previous touch
- State machine stores `sequence_context` to maintain arc continuity

### 7.2 P2b Archetype Tone Evolution
- Initial calibration stored in state
- Subsequent touches may adjust based on recipient signals
- `tone_calibration_history` tracks evolution

### 7.3 P2c Competitive Landscape in Resurfacing
- Resurfacing trigger may include new competitive signal
- Must validate new source refs before including in resurfacing touch
- `competitive_context_refs` prevents duplicate differentiator claims

---

## 8. Implementation Roadmap (Deferred)

### Phase 1: Infrastructure (Blocked)
- L4: `apps_lic_touch_state` table creation
- L4: UWG integration for touch state durable writes
- Coordination: Scheduled wake mechanism

### Phase 2: State Machine (Blocked)
- State DAG YAML definition
- State transition validation gates
- State-aware L2 step adapters

### Phase 3: Signal Ingestion (Blocked)
- External signal ingestion pipeline
- Signal validator with privacy checks
- Trigger matcher implementation

### Phase 4: HITL Integration (Blocked)
- L5 re-engagement policy definition
- HITL review UI/workflow
- L6 HITL decision logging

### Phase 5: Acceptance (Blocked)
- End-to-end multi-touch test suite
- Resurfacing trigger simulation
- HITL decision path verification

---

## 9. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| State persistence performance | Medium | High | Indexing strategy, partition by sender |
| Privacy violation (re-engagement) | Low | Critical | Signal validator, HITL gating, explicit opt-in checks |
| HITL reviewer fatigue | Medium | Medium | Throttling, batch review UI, automated suggestions |
| Coordination wake storms | Medium | High | Jittered wake times, rate limiting |

---

## 10. Dependencies and Blockers

**Blocked by:**
1. L4 state table design approval
2. Coordination fabric scheduled wake implementation
3. L5 HITL policy for re-engagement
4. Privacy/legal review of signal ingestion

**Blocks:**
- Production deployment of P3 features
- Full-funnel conversion tracking for apps_lic

---

## 11. Wave Structure (This Child Plan)

| Wave | Phase IDs | Focus | Est. Tokens | Status |
|------|-----------|-------|-------------|--------|
| W1 | P1.1-P1.3 | State machine DAG design | ~3k | Design Complete |
| W2 | P2.1-P2.3 | L4 schema & UWG integration spec | ~3k | Design Complete |
| W3 | P3.1-P3.3 | Signal ingestion architecture | ~3k | Design Complete |
| W4 | P4.1-P4.3 | HITL integration design | ~3k | Design Complete |
| W5 | P5.1-P5.3 | Acceptance criteria & test plan | ~2k | Design Complete |

---

## 12. Success Criteria (for P3 Implementation)

- [ ] Multi-touch sequences persist state across touches
- [ ] Resurfacing triggers correctly detected and routed
- [ ] HITL review gates fire on sensitive re-engagement
- [ ] P2 engines (arc, tone, competitive) adapt across touch sequences
- [ ] No direct provider calls from state management
- [ ] All state mutations via UWG → L4
- [ ] 20+ P3-specific governance tests passing

---

## 13. Non-Goals

- Real-time signal ingestion (batch/scheduled only)
- Cross-app touch state sharing (apps_lic only)
- Automatic send without human review (HITL required for P3)
- External CRM integration (state stays in Agentic-Workflow L4)

---

**Plan Status:** `Design Complete — Implementation Deferred`  
**Next Action:** Revisit when L4 state tables and L5 HITL policy are available.
