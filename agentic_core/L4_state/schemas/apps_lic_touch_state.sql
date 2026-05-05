-- apps_lic Touch State Schema
-- Wave 1, Phase 1 of apps-lic-infra-prerequisites-unblock-p2p3
-- 
-- Purpose: Durable state persistence for multi-touch sequences in apps_lic
-- Layer: L4 State (agentic_core/L4_state/schemas/)
-- App: apps_lic
--
-- Dependencies: UWG (DurableWriteGateway) for writes
-- Coordination Fabric for scheduled wake triggers

-- Main touch state table
CREATE TABLE IF NOT EXISTS apps_lic_touch_state (
    -- Primary identifier
    touch_id TEXT PRIMARY KEY,
    
    -- Identity and campaign linkage
    recipient_hash TEXT NOT NULL,           -- Hashed recipient identifier (PII-safe)
    campaign_id TEXT NOT NULL,               -- Parent campaign for this touch sequence
    
    -- Touch sequence metadata
    touch_sequence INTEGER NOT NULL,         -- Position in sequence (1, 2, 3...)
    touch_state TEXT NOT NULL,               -- Current state: scheduled|sent|replied|bounced|converted|expired
    
    -- Scheduling and timing
    next_scheduled_wake TIMESTAMP,           -- When to wake for next touch (coordination fabric)
    scheduled_count INTEGER DEFAULT 0,       -- How many times this touch has been scheduled
    last_wake_at TIMESTAMP,                -- Last time this touch was woken
    
    -- Context carry-forward (serialized JSON)
    context_carry_forward TEXT,              -- JSON: {prior_touch_id, prior_context, accumulated_signals}
    
    -- Signal tracking
    trigger_signal TEXT,                     -- What triggered this touch (resurfacing signal type)
    trigger_confidence REAL,                 -- Confidence score for trigger (0.0-1.0)
    
    -- Outcome tracking
    sent_at TIMESTAMP,                       -- When message was sent
    reply_received_at TIMESTAMP,             -- When reply was received
    reply_classification TEXT,               -- positive|negative|neutral|opt_out
    bounce_reason TEXT,                      -- If bounced: reason code
    
    -- HITL tracking
    hitl_review_required BOOLEAN DEFAULT FALSE,
    hitl_review_id TEXT,                   -- Link to L5 HITL review record
    hitl_decision TEXT,                      -- approved|rejected|modified
    
    -- Audit timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Soft delete for audit trail
    deleted_at TIMESTAMP,
    deleted_reason TEXT
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_touch_state_recipient_campaign 
    ON apps_lic_touch_state(recipient_hash, campaign_id) 
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_touch_state_wake 
    ON apps_lic_touch_state(next_scheduled_wake) 
    WHERE deleted_at IS NULL AND touch_state = 'scheduled';

CREATE INDEX IF NOT EXISTS idx_touch_state_campaign_sequence 
    ON apps_lic_touch_state(campaign_id, touch_sequence) 
    WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_touch_state_hitl 
    ON apps_lic_touch_state(hitl_review_required, hitl_review_id) 
    WHERE hitl_review_required = TRUE AND deleted_at IS NULL;

-- Touch state transition audit log (append-only)
CREATE TABLE IF NOT EXISTS apps_lic_touch_state_transitions (
    transition_id TEXT PRIMARY KEY,
    touch_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    transitioned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    transitioned_by TEXT,                    -- Component that triggered transition
    transition_reason TEXT,                  -- Human-readable reason
    context_diff TEXT,                       -- JSON diff of what changed
    
    FOREIGN KEY (touch_id) REFERENCES apps_lic_touch_state(touch_id)
);

CREATE INDEX IF NOT EXISTS idx_transitions_touch 
    ON apps_lic_touch_state_transitions(touch_id, transitioned_at);

-- Touch state state machine constraints (enforced at application layer, documented here)
--
-- Valid transitions:
--   scheduled -> sent (when coordination fabric wakes and sends)
--   scheduled -> cancelled (when campaign ends or recipient opts out)
--   sent -> replied (when reply received)
--   sent -> bounced (when delivery fails)
--   sent -> expired (when timeout reached)
--   replied -> scheduled (for next touch in sequence)
--   replied -> converted (when positive outcome achieved)
--   bounced -> scheduled (for retry, with backoff)
--   bounced -> failed (max retries exceeded)
--   (any) -> expired (campaign timeout)

-- View: Active touches due for wake
CREATE VIEW IF NOT EXISTS v_apps_lic_touches_due AS
SELECT 
    touch_id,
    recipient_hash,
    campaign_id,
    touch_sequence,
    touch_state,
    next_scheduled_wake,
    context_carry_forward,
    trigger_signal,
    trigger_confidence
FROM apps_lic_touch_state
WHERE deleted_at IS NULL
    AND touch_state = 'scheduled'
    AND next_scheduled_wake <= CURRENT_TIMESTAMP;

-- View: Touch sequence summary per campaign/recipient
CREATE VIEW IF NOT EXISTS v_apps_lic_touch_sequences AS
SELECT 
    campaign_id,
    recipient_hash,
    COUNT(*) as total_touches,
    MAX(touch_sequence) as current_sequence_position,
    MAX(CASE WHEN touch_state = 'converted' THEN 1 ELSE 0 END) as has_converted,
    MAX(CASE WHEN touch_state = 'replied' THEN 1 ELSE 0 END) as has_replied,
    MAX(CASE WHEN touch_state = 'expired' THEN 1 ELSE 0 END) as has_expired,
    MAX(updated_at) as last_activity_at
FROM apps_lic_touch_state
WHERE deleted_at IS NULL
GROUP BY campaign_id, recipient_hash;
