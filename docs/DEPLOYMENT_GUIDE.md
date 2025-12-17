# Hardened Agentic Architecture Deployment Guide

## I. Architectural Summary (The 10-MCP Stack)

The agent operates by chaining tools across the following layers, prioritizing cost and auditability:

### Layer 5: Context & Audit

- **MEMemory (L5)**: Non-repudiable audit logging for all critical actions
- Primary Functions: `add_observations`, `search_nodes`

### Layer 4: State, Time & Cache

- **Redis/LangCache (L4)**: Atomic state management, cost governance, LLM caching
- **Time (L4)**: Freshness constraints, audit timestamps
- Primary Functions: `string_get`, `string_set`, `incr`, `get_current_time`, `get_from_langcache`, `set_to_langcache`

### Layer 3: RAG & Wisdom

- **Pinecone (L3)**: Hybrid search across specialized indexes, audited fixes
- Primary Functions: `search_records`, `execute_hybrid_fix_search`

### Layer 2: Automation & Design

- **Playwright (L2)**: Resilient browser interaction with adaptive recovery
- **Figma (L2)**: Version-locked design integrity, change detection
- Primary Functions: `browser_navigate`, `browser_click`, `browser_type`, `get_variable_defs`, `get_file_versions`

### Layer 1: I/O & Search

- **GitKraken (L1)**: Commit audit, version control
- **Filesystem (L1)**: Immutable artifact storage with fallbacks
- **Fetch (L1)**: Bulk data retrieval
- **Brave Search (L1/L3)**: Cost-governed web search with rate limiting
- Primary Functions: `commit`, `add`, `write_file`, `read_file`, `fetch`, `brave_search`

### Action Layer

- **Send Email**: Rate-limited communication with governance controls

## II. Core Governance Policies (Hardening Enforcement)

### Cost Control Policies

1. **Brave Search Rate Limiting**: Enforced via `execute_cost_controlled_search`
   - Daily quota: 100 searches
   - Redis key: `brave_search:daily_count`

2. **LLM Generation Budget**: Enforced via `execute_governed_prompt_caching`
   - Daily quota: 5 generations per user
   - Redis key: `llm:daily_budget:{user_name}`

### Data Integrity Policies

1. **Figma Version Locking**: All design retrievals must specify `version_id`
   - Change detection via `execute_version_locked_design_audit`
   - Audit log: `DesignAudit` entity in MEMemory

2. **Time-Bound Freshness**: Salary and market data filtered by 6-month window
   - Implemented in `execute_time_bound_salary_benchmarking`
   - Time MCP integration for accurate date calculations

### Non-Repudiation Requirements

- All commits logged with: `commit_id`, `timestamp`, `issue_id`
- All applications logged with: `company`, `position`, `date`
- All fixes logged with: `source_index`, `confidence_score`, `audit_status`

## III. Engine-Specific Master Workflows

### Canon Validator Engine

**Master Function**: `execute_cost_governed_vulnerability_check`

**Tool Chain**:

1. Brave Search (cost-controlled) → Check for public fixes
2. Pinecone Hybrid Search (fallback) → Audited canonical fixes
3. Filesystem → Apply code edits
4. Redis (atomic) → Transaction state management
5. MEMemory → Audit trail

**Key Files**:

- `canon_validator_engine.py`: Main orchestrator
- `redis_langcache_pipeline.py`: Atomic operations
- `mcp_hardening.py`: Hardened MCP wrappers

### Resume Engine

**Master Function**: `execute_governed_prompt_caching`

**Tool Chain**:

1. LangCache → Check for cached drafts
2. Redis → Enforce daily budget
3. Time → Calculate freshness window
4. Figma → Version-locked template validation
5. Brave Search → Fresh salary data
6. LLM → Generate content (if budget allows)
7. Filesystem → Save final draft

**Key Files**:

- `resume_engine.py`: Main orchestrator
- `redis_langcache_pipeline.py`: Caching logic
- `time_bound_benchmarking.py`: Salary freshness

### Outreach Engine

**Master Function**: `execute_resilient_application_pipeline_hardened`

**Tool Chain**:

1. Playwright (loop) → Form interaction with retry
2. Redis → Rate limiting and state persistence
3. GitKraken → Commit application records
4. Time → Immutable timestamps
5. MEMemory → Complete audit trail

**Key Files**:

- `outreach_engine.py`: Main orchestrator
- `mcp_hardening.py`: Resilient browser handling

## IV. Specialized Pinecone Indexes

### 1. code-canon-fixes

- Purpose: Audited production fixes
- Metadata: `audit_status`, `version`, `confidence`
- Query Pattern: Hybrid search with metadata filters

### 2. career-data-graph

- Purpose: Skills with salary band metadata
- Metadata: `salary_range`, `demand_level`, `location`
- Query Pattern: Semantic matching with salary constraints

### 3. outreach-templates

- Purpose: Pitches with success tracking
- Metadata: `success_rate`, `industry`, `tone`
- Query Pattern: Weighted by success metrics

## V. Redis Key Structure

### Governance Keys

```text
llm:daily_budget:{user_name}     # LLM generation quota
brave_search:daily_count         # Search rate limit
browser:last_working_proxy       # Browser state
validation_status:{user_name}    # Cache status
fix_state:{fix_hash}             # Atomic fix state
```

### Cache Keys

```text
llm:draft:{job_hash}:{user}      # LangCache for drafts
validation_cache:{component}     # Design validation
rate_limit:{lead}:{action}       # Outreach rate limiting
```

## VI. Final Deployment Checklist

### Pre-Deployment Verification

1. **Redis Server Status**

   ```bash
   redis-cli ping
   # Expected: PONG
   ```

2. **Initialize Governance Keys**

   ```python
   string_set("llm:daily_budget:default", "5")
   string_set("brave_search:daily_count", "0")
   string_set("browser:last_working_proxy", "none")
   ```

3. **Pinecone Index Verification**

   ```python
   # Verify index exists and has vectors
   describe_index("code-canon-fixes")
   describe_index("career-data-graph")
   describe_index("outreach-templates")
   ```

4. **Filesystem Permissions**

   ```python
   # Test write access
   write_file("reports/deployment_test.txt", "SUCCESS")
   ```

### Runtime Monitoring

1. **Cost Governance Dashboard**

   - Track LLM generations per user
   - Monitor Brave Search usage
   - Alert on quota exhaustion

2. **Audit Trail Verification**

   - Daily MEMemory export for compliance
   - Verify all actions have timestamps
   - Check for non-repudiation compliance

3. **Performance Metrics**

   - Cache hit ratios (LangCache)
   - Pinecone query latency
   - Redis transaction success rate

## VII. Security & Compliance

### Data Protection

- PII scrubbing before MEMory storage
- Encrypted Redis connections
- Audit log immutability

### Access Control

- MCP tool authentication
- Rate limiting per API key
- Circuit breaker patterns

### Compliance Features

- GDPR-compliant audit logs
- Data retention policies
- Right to deletion implementation

## VIII. Troubleshooting Guide

### Common Issues

1. **Redis Connection Failed**

   - Check Redis server status
   - Verify connection string
   - Test with simple SET/GET

2. **Pinecone Query Timeout**

   - Increase timeout value
   - Check index size
   - Verify API key permissions

3. **Figma Version Lock Error**

   - Verify version_id exists
   - Check file permissions
   - Fallback to latest version

### Emergency Procedures

1. **Circuit Breaker Activation**

   - All expensive MCPs disabled
   - Fallback to cached data only
   - Alert administrators

2. **Audit Trail Recovery**

   - Export MEMemory to backup
   - Verify log integrity
   - Restore from last checkpoint

## IX. Future Enhancements

### Planned Features

1. **Multi-Region Deployment**

   - Geo-distributed Redis
   - Local Pinecone replicas
   - CDN for static assets

2. **Advanced Analytics**

   - Real-time cost tracking
   - Performance optimization
   - Predictive scaling

3. **Additional MCPs**

   - Slack integration
   - Jira connectivity
   - Salesforce automation

This deployment guide serves as the definitive reference for operating the hardened agentic architecture in production.
