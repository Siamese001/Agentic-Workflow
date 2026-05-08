# C0 Policy Incident Response Runbook

> **Plan**: `c0-policy-rectification-phase2-deferred-a3f7e2` (W5)  
> **Status**: Completed 2026-05-08  
> **Owner**: Agentic Core Team  
> **Severity Levels**: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)

## Quick Reference

| Alert | Threshold | Severity | Page? | Auto-Response |
|-------|-----------|----------|-------|---------------|
| `c0_policy_none_rate` > 5% | Migration incomplete | P1 | Yes | None |
| `c0_bypass_legacy_ratio` > 10% | Typed adoption lag | P2 | No | Slack notify |
| `pa_boundary_rejection_rate` spike | >2x baseline | P1 | Yes | Investigate |
| `l0_l1_c0_disagreement_rate` > 1% | L0 authority issue | P0 | Yes | Rollback ready |

## Alert: C0_POLICY_NONE_RATE > 5%

**Meaning**: More than 5% of RouteContracts lack the `c0_policy` field.

### Diagnosis

```bash
# Check migration status
python -m tools.c0_migration.background_contract_updater \
    --source-db contracts.db \
    --dry-run

# Query specific routes without c0_policy
sqlite3 contracts.db "SELECT route_id, created_at FROM route_contracts WHERE c0_policy IS NULL"
```

### Response

1. **Immediate (< 15 min)**
   - Run eager migration if not already done:
     ```bash
     python -m tools.c0_migration.background_contract_updater \
         --source-db contracts.db \
         --batch-size 100
     ```

2. **Short-term (< 1 hour)**
   - Verify migration completed successfully
   - Check logs for any failed migrations
   - Re-run with smaller batch size if failures

3. **Root Cause**
   - New contracts being created without c0_policy field
   - Identify source and fix at creation point

## Alert: C0_BYPASS_LEGACY_RATIO > 10%

**Meaning**: More than 10% of C0 bypasses use deprecated legacy reasons.

### Diagnosis

```bash
# Check bypass reason distribution
tail -10000 artifacts/c0_bypass_log.jsonl | \
    jq -r '.c0_bypass_reason' | \
    sort | uniq -c | sort -rn

# Find entrypoints using legacy reasons
grep -r "GROUNDING_NOT_REQUIRED\|TERMINAL_SHORTCIRCUIT" apps_* --include="*.py"
```

### Response

1. **Immediate (< 30 min)**
   - Audit entrypoints using legacy reasons
   - Map legacy → typed equivalents:
     - `GROUNDING_NOT_REQUIRED` → `BYPASS_PRELOADED_CONTEXT` or `NOT_REQUIRED`
     - `CACHE_REUSE_PRIOR_EVIDENCE` → `BYPASS_CACHE_RETURN`
     - `FALLBACK_NO_RETRIEVAL` → `BYPASS_FALLBACK`

2. **Short-term (< 2 hours)**
   - Update code to use typed reasons
   - Deploy fix
   - Verify ratio drops

3. **Prevention**
   - CI gate blocks new legacy reason usage
   - Weekly report tracks trend

## Alert: PA_BOUNDARY_REJECTION_RATE Spike

**Meaning**: PA boundary rejection rate is >2x baseline.

### Diagnosis

```bash
# Check recent OTEL spans for PA failures
sqlite3 artifacts/otel_spans.db "SELECT COUNT(*), status FROM otel_spans WHERE span_name = 'pa.0.boundary_check' AND timestamp > datetime('now', '-1 hour') GROUP BY status"

# Check specific fail reasons
sqlite3 artifacts/otel_spans.db "SELECT fail_reason, COUNT(*) FROM otel_spans WHERE span_name = 'pa.0.boundary_check' AND status = 'ERROR' AND timestamp > datetime('now', '-1 hour') GROUP BY fail_reason"
```

### Response

1. **Immediate (< 15 min)**
   - Identify if spike is due to:
     - Evidence contract quality issues
     - Route misconfiguration
     - C0 policy inconsistency

2. **Evidence Quality Issues**
   - Check evidence contract retrieval pipeline
   - Verify C0.1 retrieval is functioning
   - Review support scores

3. **Route Misconfiguration**
   - Review recent route changes
   - Verify c0_policy field consistency
   - Check evidence_required vs evidence_present mismatch

## Alert: L0_L1_C0_DISAGREEMENT_RATE > 1%

**Meaning**: L0 (RouteContract) and L1 (C0Advisory) disagree on C0 policy more than 1% of the time.

**This is CRITICAL** — L0 authority must be respected.

### Diagnosis

```bash
# Find disagreement cases
sqlite3 artifacts/otel_spans.db "SELECT route_id, route_c0_mode, l1_grounding_required FROM otel_spans WHERE span_name = 'c0.0.preflight' AND (route_c0_mode = 'NOT_REQUIRED' AND l1_grounding_required = 1) OR (route_c0_mode = 'RETRIEVE_REQUIRED' AND l1_grounding_required = 0)"
```

### Response

1. **Immediate (< 5 min)**
   - **STOP** if disagreement rate > 5% — potential system issue
   - Check if `C0_POLICY_STRICT_MODE=0` fallback is active
   - Verify L0 routing is producing correct c0_policy

2. **Root Cause Analysis**
   - L0 routing bug: RouteContract.c0_policy incorrectly set
   - L1 advisory bug: C0Advisor ignoring L0 signal
   - Race condition: RouteContract updated but not propagated

3. **Recovery**
   ```bash
   # Emergency fallback if needed
   export C0_POLICY_STRICT_MODE=0  # Allow legacy behavior temporarily
   ```

4. **Fix and Deploy**
   - Fix root cause
   - Re-enable strict mode
   - Verify disagreement rate drops to <1%

## Escalation Path

| Severity | Response Time | Escalation |
|----------|---------------|------------|
| P0 (Critical) | 15 min | Page SVP Engineering immediately |
| P1 (High) | 1 hour | Page Agentic Core Team lead |
| P2 (Medium) | 4 hours | Slack notify team, handle during business hours |
| P3 (Low) | 24 hours | Track in weekly report |

## Rollback Procedures

### Emergency Rollback: Disable C0 Policy Enforcement

If C0 policy is causing widespread failures:

```bash
# 1. Disable strict mode (allows legacy behavior)
export C0_POLICY_STRICT_MODE=0

# 2. Restart affected services
systemctl restart agentic-core-{pa,l3,l0}

# 3. Verify recovery
python ops_scripts/monitoring/c0_policy_dashboard.py --output-format json
```

### Partial Rollback: Specific Route

If only specific routes are affected:

```bash
# Update route to use legacy bypass reason temporarily
python -c "
import sqlite3
conn = sqlite3.connect('contracts.db')
conn.execute(\"UPDATE route_contracts SET c0_policy = NULL WHERE route_id = 'R3_AFFECTED'\")
conn.commit()
conn.close()
"
```

## Post-Incident Review

After any P0 or P1 incident:

1. **Within 24 hours**: Document timeline in incident channel
2. **Within 48 hours**: Author post-mortem at `docs/incidents/<YYYY-MM-DD>-c0-policy.md`
3. **Within 1 week**: Update this runbook if procedures changed

## Weekly Review

Every Monday:

1. Review previous week's C0 policy metrics
2. Check for any alerts that fired
3. Verify action items from weekly report are complete
4. Update Notion with current status

## References

- **Plan**: [c0-policy-rectification-phase2-deferred-a3f7e2](https://www.notion.so/c0-policy-rectification-phase2-deferred-a3f7e2)
- **Migration Guide**: [C0_POLICY_MIGRATION.md](../operations/C0_POLICY_MIGRATION.md)
- **Dashboard**: `ops_scripts/monitoring/c0_policy_dashboard.py`
- **Weekly Report**: `ops_scripts/monitoring/c0_policy_weekly_report.py`
- **Migration Tool**: `tools/c0_migration/background_contract_updater.py`
- **Hard Cutoff Gate**: `ops_scripts/ci/check_c0_policy_required.py`
