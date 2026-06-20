-- sync_health_ledger.schema.sql — Schema for Notion sync health tracking
-- 
-- Tracks every sync attempt, failure, and drift event for observability.
-- Aligned with §24 deferred-scope capture and §30 Author-Gate capture health.

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Main sync attempts log
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sync_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL DEFAULT (julianday('now')),
    
    -- Target identification
    slug TEXT NOT NULL,
    page_id TEXT,
    database_id TEXT,
    
    -- Operation details
    operation TEXT NOT NULL CHECK (operation IN (
        'wave_start', 'wave_complete', 'plan_complete',
        'status_patch', 'summary_append', 'property_update'
    )),
    
    -- HTTP-level result
    status_code INTEGER,
    latency_ms REAL,
    retry_count INTEGER DEFAULT 0,
    
    -- Outcome
    success BOOLEAN NOT NULL DEFAULT 0,
    failure_type TEXT CHECK (failure_type IN (
        'http_4xx', 'http_5xx', 'network', 'timeout', 'circuit_open', 'unknown'
    )),
    error_message TEXT,
    
    -- Context
    trigger_source TEXT CHECK (trigger_source IN (
        'wave_lifecycle_writer', 'cursor_agent_marker', 'manual_sync', 'reconciler'
    )),
    
    -- Index for time-series queries
    UNIQUE(slug, timestamp, operation)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_sync_attempts_slug ON sync_attempts(slug);
CREATE INDEX IF NOT EXISTS idx_sync_attempts_time ON sync_attempts(timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_attempts_success ON sync_attempts(success);
CREATE INDEX IF NOT EXISTS idx_sync_attempts_failure_type ON sync_attempts(failure_type);

-- ---------------------------------------------------------------------------
-- Sync failures (long-lived until resolved)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sync_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_seen REAL NOT NULL DEFAULT (julianday('now')),
    last_seen REAL NOT NULL DEFAULT (julianday('now')),
    resolved_at REAL,
    
    -- Target
    slug TEXT NOT NULL,
    page_id TEXT,
    
    -- Failure classification
    failure_type TEXT NOT NULL CHECK (failure_type IN (
        'http_4xx', 'http_5xx', 'network', 'timeout', 'circuit_open', 'schema_validation'
    )),
    error_message TEXT,
    
    -- Tracking
    occurrence_count INTEGER DEFAULT 1,
    resolution_status TEXT DEFAULT 'unresolved' CHECK (resolution_status IN (
        'unresolved', 'auto_resolved', 'manual_resolved', 'suppressed'
    )),
    
    UNIQUE(slug, failure_type)
);

CREATE INDEX IF NOT EXISTS idx_sync_failures_unresolved 
    ON sync_failures(resolution_status) 
    WHERE resolution_status = 'unresolved';

-- ---------------------------------------------------------------------------
-- Drift events
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS drift_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    detected_at REAL NOT NULL DEFAULT (julianday('now')),
    resolved_at REAL,
    
    -- Target
    slug TEXT NOT NULL,
    page_id TEXT,
    
    -- Drift classification
    drift_type TEXT NOT NULL CHECK (drift_type IN (
        'STATUS', 'PROPERTY', 'EXISTENCE', 'MISSING_FILE', 'EXTRA_FILE'
    )),
    severity TEXT NOT NULL CHECK (severity IN (
        'trivial', 'minor', 'major', 'critical'
    )),
    
    -- Specifics
    property_name TEXT,
    expected_value TEXT,
    actual_value TEXT,
    
    -- Resolution
    auto_reconcilable BOOLEAN DEFAULT 0,
    reconciliation_action TEXT CHECK (reconciliation_action IN (
        'pending', 'auto_reconciled', 'manual_reconciled', 'ignored', 'escalated'
    )) DEFAULT 'pending',
    
    UNIQUE(slug, drift_type, property_name) 
    WHERE reconciliation_action = 'pending'
);

CREATE INDEX IF NOT EXISTS idx_drift_events_slug ON drift_events(slug);
CREATE INDEX IF NOT EXISTS idx_drift_events_pending 
    ON drift_events(reconciliation_action) 
    WHERE reconciliation_action = 'pending';

-- ---------------------------------------------------------------------------
-- Circuit breaker state log
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS circuit_state_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL DEFAULT (julianday('now')),
    
    circuit_name TEXT NOT NULL,
    old_state TEXT NOT NULL CHECK (old_state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
    new_state TEXT NOT NULL CHECK (new_state IN ('CLOSED', 'OPEN', 'HALF_OPEN')),
    
    trigger TEXT CHECK (trigger IN (
        'failure_threshold', 'success_threshold', 'timeout', 'manual_reset', 'probe'
    )),
    
    context_json TEXT  -- JSON blob with stats at time of transition
);

CREATE INDEX IF NOT EXISTS idx_circuit_state_time ON circuit_state_log(timestamp);

-- ---------------------------------------------------------------------------
-- Aggregate metrics (pre-computed for dashboard queries)
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sync_metrics_rollup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_start REAL NOT NULL,
    period_end REAL NOT NULL,
    period_type TEXT NOT NULL CHECK (period_type IN ('hour', 'day', 'week')),
    
    -- Totals
    total_attempts INTEGER DEFAULT 0,
    total_successes INTEGER DEFAULT 0,
    total_failures INTEGER DEFAULT 0,
    
    -- Breakdown
    http_4xx_count INTEGER DEFAULT 0,
    http_5xx_count INTEGER DEFAULT 0,
    network_failures INTEGER DEFAULT 0,
    circuit_open_blocks INTEGER DEFAULT 0,
    
    -- Latency percentiles (ms)
    latency_p50 REAL,
    latency_p99 REAL,
    
    -- Drift
    drift_events_detected INTEGER DEFAULT 0,
    drifts_auto_resolved INTEGER DEFAULT 0,
    drifts_pending INTEGER DEFAULT 0,
    
    UNIQUE(period_type, period_start)
);

-- ---------------------------------------------------------------------------
-- Views for common queries
-- ---------------------------------------------------------------------------

-- Current sync health summary
CREATE VIEW IF NOT EXISTS v_sync_health_summary AS
SELECT 
    COUNT(*) as total_plans_checked,
    SUM(CASE WHEN success THEN 1 ELSE 0 END) as recent_successes,
    SUM(CASE WHEN NOT success THEN 1 ELSE 0 END) as recent_failures,
    AVG(latency_ms) as avg_latency_ms
FROM sync_attempts
WHERE timestamp >= julianday('now', '-24 hours');

-- Unresolved failures requiring attention
CREATE VIEW IF NOT EXISTS v_unresolved_failures AS
SELECT 
    slug,
    failure_type,
    first_seen,
    occurrence_count,
    error_message
FROM sync_failures
WHERE resolution_status = 'unresolved'
ORDER BY occurrence_count DESC;

-- Pending drift events
CREATE VIEW IF NOT EXISTS v_pending_drift AS
SELECT 
    slug,
    drift_type,
    severity,
    property_name,
    detected_at,
    auto_reconcilable
FROM drift_events
WHERE reconciliation_action = 'pending'
ORDER BY 
    CASE severity 
        WHEN 'critical' THEN 1 
        WHEN 'major' THEN 2 
        WHEN 'minor' THEN 3 
        ELSE 4 
    END,
    detected_at;

-- Circuit breaker transitions (last 7 days)
CREATE VIEW IF NOT EXISTS v_recent_circuit_events AS
SELECT 
    circuit_name,
    old_state,
    new_state,
    trigger,
    timestamp,
    datetime(timestamp, 'unixepoch') as human_time
FROM circuit_state_log
WHERE timestamp >= julianday('now', '-7 days')
ORDER BY timestamp DESC;
