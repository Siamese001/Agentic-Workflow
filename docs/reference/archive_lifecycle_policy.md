# Archive Lifecycle Policy

**Effective Date:** 2026-05-06  
**Applies To:** `archives/`, `.codex/plans/_archive/`

## Policy Goals

1. Prevent indefinite accumulation of archived artifacts
2. Enable recovery of archived content within defined windows
3. Automate compression and cold storage transitions
4. Ensure no active references exist before permanent deletion

## Retention Tiers

### Tier 1: Hot Archive (0-90 days)
- **Location:** `archives/tools_archive_2026/`, `.codex/plans/_archive/2026-*/`
- **State:** Uncompressed, direct file access
- **Access:** Immediate
- **Action:** Monitor for active references

### Tier 2: Warm Archive (90 days - 1 year)
- **Location:** Same folders, compressed
- **State:** `.tar.gz` compressed bundles per month/quarter
- **Access:** Decompress on demand (~minutes)
- **Action:** Automatic compression via scheduled job

### Tier 3: Cold Storage (1-2 years)
- **Location:** Separate repo or S3-compatible storage
- **State:** Compressed, off-primary-storage
- **Access:** Restore request (~hours)
- **Action:** Quarterly migration to cold storage

### Tier 4: Expunged (>2 years)
- **State:** Deleted
- **Prerequisite:** Reference audit confirms zero active dependencies
- **Action:** Permanent deletion with audit trail

## Compression Schedule

```bash
# Monthly compression job (runs 1st of month)
python tools/maintenance/compress_archives.py --older-than 90 --dry-run

# Quarterly cold storage migration (runs Jan/Apr/Jul/Oct 1st)
python tools/maintenance/migrate_to_cold_storage.py --older-than 365 --dry-run
```

## Reference Audit Process

Before any Tier 3→4 transition (deletion):

1. **Automated scan:** `grep -r <archive_path>` across codebase
2. **ADG analysis:** Check for import/dependency edges from archived files
3. **Manual review:** Human sign-off on deletion candidate list
4. **30-day grace:** Move to `_pending_deletion/` with timestamp
5. **Final purge:** Delete after grace period expires

## Monitoring

| Metric | Target | Alert |
|--------|--------|-------|
| Archive folder count | < 10,000 | WARN at 8,000 |
| Archive total size | < 500 MB | WARN at 400 MB |
| Compression job success | 100% | CRIT on failure |
| Cold storage lag | < 30 days | WARN at 14 days |

## Enforcement

- CI gate: `check_archive_lifecycle_compliance.py` (T7r tier)
- Audit: `post_cursor_agent_archive_audit.py` logs to `artifacts/windsurf/archive_lifecycle.jsonl`
- Bypass: `ARCHIVE_LIFECYCLE_BYPASS=1`

## Related

- Parent plan: `repo-wide-deduplication-c5d2a8` (W3)
- This policy: `repo-dedup-deferred-followup-d5e2a9` (W2 P1)
