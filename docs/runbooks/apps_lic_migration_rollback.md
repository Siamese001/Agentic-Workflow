# W5 Migration Rollback Runbook

**apps_lic Multi-Touch Infrastructure Migration**

W5.P3: Rollback Procedures

---

## 1. Overview

This runbook describes rollback procedures for the W5 migration from legacy apps_lic campaigns to the new multi-touch infrastructure.

**Migration Scope:**
- Campaign state migration
- Recipient identity migration
- Touch history conversion
- Template mapping

**Rollback Triggers:**
- Data corruption detected
- Performance degradation >50%
- API errors >5% for 10 minutes
- Customer escalation requiring reversal

---

## 2. Pre-Migration Checklist

Before running W5 migration, ensure:

- [ ] Full database backup created (`/backup/apps_lic/pre_w5/`)
- [ ] Migration inventory exported (`campaign_inventory.json`)
- [ ] Compatibility report reviewed
- [ ] Rollback window confirmed (maintenance window active)
- [ ] On-call engineer notified
- [ ] Monitoring dashboards active

---

## 3. Rollback Scenarios

### 3.1 Scenario A: Dry-Run Failure

**Symptoms:**
- Compatibility check shows >20% blocked campaigns
- Inventory scan reveals unexpected data format

**Action:**
```bash
# 1. Stop migration (do not proceed to execute)
# 2. Document findings
echo "W5 dry-run failed - see report" > logs/w5_blocker.txt

# 3. Exit maintenance mode
python -m ops_scripts.maintenance.set_maintenance_mode --off
```

**Recovery Time:** < 5 minutes (no data modified)

---

### 3.2 Scenario B: Partial Migration Failure

**Symptoms:**
- Some campaigns migrated successfully
- Others failed with errors
- Data in mixed state

**Action:**
```bash
# 1. Stop ongoing migration
pkill -f "w5_migration"

# 2. Identify failed campaigns
cat artifacts/w5_migration_report.json | jq '.results[] | select(.status == "failed")'

# 3. Quarantine affected campaigns
python -m apps_lic.migrations.w5_migration --quarantine-failed

# 4. Decide: complete or rollback
# Option A: Complete (migrate remaining individually)
python -m apps_lic.migrations.w5_migration --execute --campaigns-only failed_campaigns.txt

# Option B: Rollback (see section 4)
```

**Recovery Time:** 15-30 minutes

---

### 3.3 Scenario C: Post-Migration Data Corruption

**Symptoms:**
- Touch counts don't match
- Recipient identity mismatches
- Campaign state inconsistent

**Action:**
```bash
# 1. Immediately enter safe mode
python -m ops_scripts.maintenance.set_maintenance_mode --on --reason="w5_rollback"

# 2. Execute full rollback (see section 4.3)
python -m apps_lic.migrations.w5_rollback --full-restore

# 3. Verify restoration
python -m apps_lic.migrations.w5_migration --verify-only
```

**Recovery Time:** 30-60 minutes

---

## 4. Rollback Procedures

### 4.1 Standard Rollback (Last 24 Hours)

For migrations executed within last 24 hours:

```bash
#!/bin/bash
# rollback_w5_standard.sh

set -e

echo "Starting W5 standard rollback..."

# 1. Verify backup exists
if [ ! -d "/backup/apps_lic/pre_w5/$(date +%Y%m%d)" ]; then
    echo "ERROR: Backup not found"
    exit 1
fi

# 2. Stop apps_lic services
systemctl stop apps_lic_worker
systemctl stop apps_lic_api

# 3. Restore database
pg_restore -d apps_lic_prod /backup/apps_lic/pre_w5/$(date +%Y%m%d)/db.dump

# 4. Clear migration state
redis-cli DEL "migration:w5:state"

# 5. Restart services
systemctl start apps_lic_api
systemctl start apps_lic_worker

# 6. Verify
curl -s http://localhost:8080/health | grep "ok"

echo "Rollback complete"
```

### 4.2 Point-in-Time Rollback (Specific Campaigns)

To rollback specific campaigns only:

```bash
# 1. Identify campaigns to rollback
cat > /tmp/rollback_campaigns.txt <<EOF
campaign_001
campaign_002
campaign_003
EOF

# 2. Execute targeted rollback
python -m apps_lic.migrations.w5_rollback \
    --campaigns-file /tmp/rollback_campaigns.txt \
    --restore-point pre_w5

# 3. Verify
python -m apps_lic.migrations.w5_migration \
    --campaigns-file /tmp/rollback_campaigns.txt \
    --verify-only
```

### 4.3 Full System Rollback

**⚠️ WARNING: Destructive operation**

Use only when standard rollback fails:

```bash
# 1. Emergency stop all apps_lic services
python -m ops_scripts.emergency.stop_all --app=apps_lic --force

# 2. Database restoration from cold backup
# (Requires DBA approval)
python -m ops_scripts.db.restore \
    --source=/backup/apps_lic/pre_w5/cold_backup.dump \
    --target=apps_lic_prod \
    --confirm

# 3. Clear all caches
redis-cli FLUSHDB

# 4. Rebuild indexes
python -m apps_lic.db.rebuild_indexes

# 5. Gradual restart
python -m ops_scripts.maintenance.gradual_restart --app=apps_lic --batch-size=10
```

---

## 5. Verification After Rollback

### 5.1 Health Checks

```bash
# Check API health
curl -f http://localhost:8080/health || exit 1

# Check database connectivity
python -c "from apps_lic.db import check_connection; check_connection()"

# Check queue processing
redis-cli LLEN apps_lic:queue:main

# Check error rates (should be < 1%)
python -m ops_scripts.monitoring.check_error_rate --app=apps_lic --threshold=0.01
```

### 5.2 Data Integrity Checks

```bash
# Campaign count matches pre-migration
python -m apps_lic.migrations.w5_migration --count-only | \
    diff - pre_w5_campaign_count.txt

# Touch totals match
python -m apps_lic.db.check_touch_totals --compare-with=pre_w5

# Recipient counts match
python -m apps_lic.db.check_recipient_counts --compare-with=pre_w5
```

---

## 6. Post-Rollback Actions

### 6.1 Immediate

- [ ] Notify on-call engineer
- [ ] Update incident ticket
- [ ] Document root cause
- [ ] Enable enhanced monitoring

### 6.2 Within 24 Hours

- [ ] Schedule post-mortem
- [ ] Update migration plan with lessons learned
- [ ] Review and fix compatibility checker rules
- [ ] Re-test migration in staging

### 6.3 Before Retry

- [ ] Root cause addressed
- [ ] Fix validated in staging
- [ ] Extended monitoring configured
- [ ] Rollback procedure updated if needed

---

## 7. Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| Primary On-Call | #apps_lic-oncall | 15 min |
| Engineering Lead | lead@company.com | 30 min |
| DBA Team | #dba-emergency | Immediate |
| SRE Team | #sre-hotline | 10 min |

---

## 8. Reference

**Related Documents:**
- W5 Migration Plan: `.codex/plans/apps-lic-p2p3-deferred-scope-execution.md`
- W6 Migration Script: `apps_lic/migrations/w6_migration.py`
- Campaign Inventory: `apps_lic/migrations/campaign_inventory.py`
- Compatibility Checker: `apps_lic/migrations/campaign_inventory.py`

**Scripts:**
- `apps_lic/migrations/w5_migration.py` - Migration runner
- `ops_scripts/maintenance/set_maintenance_mode.py` - Maintenance mode
- `ops_scripts/emergency/stop_all.py` - Emergency stop

---

**Version:** 1.0  
**Last Updated:** 2026-05-05  
**Owner:** apps_lic Team
