# ADG Generation & QA Workflow

Complete quality assurance workflow for ADG generation, validation, and deployment.

## QA Checks During ADG Generation & Redis Load

### 1. Structural Validation
- Entity count verification: 64,860 entities
- Relation count verification: 220,958 relations
- Edge count verification: 214,951 edges

### 2. Graph Plane Coverage Analysis
```
[ADG] Graph plane coverage:
      G1_imports=48018
      G3_implements=2085
      G4_calls=17829  (Gap 1 resolved)
      GT_covers=7664  (Gap 2 resolved)
      GV_violates=2  (Gap 3+4 resolved)
      GG_governance=141  (Gap 5 resolved)
```

### 3. Enhancement 5-10 Analysis (E5-E10 QA suite)
```
[ADG] Enhancement 5-10 analysis:
      E5 impact: 1686 impacted  0 tests  risk=MEDIUM (0.2057)
      E6 graph_hash=2286eaeb7a74266f...  nodes=64512  edges=214951
      E7 drift: ADG diff: +138 edges, -1 edges
      E8 ownership: 6007 modules  high_criticality=1760
      E9 confidence: avg=0.8676  high=113122  low=35574
      E10 repair routes: 14 routes  by_severity={'critical': 2, 'medium': 12}
```

### 4. Violation Detection
- `GV_violates=2` — detected 2 critical violations
- Memory MCP persistence: `2/2 violations (critical=2)`

### 5. Digest Verification
- Generates cryptographic digest: `341133c4d35561975b07bc05fdcae6160538e91b2cc8f10c6baa1c8b171290c3`
- Artifact digest: `1c05f53013630a5f...`
- Graph hash: `2286eaeb7a74266f...`

### 6. Diff Analysis
- Compares against previous run
- Reports: `+138 edges, -1 edges`

### 7. Redis Ingest Verification
```
[ADG] ✓ Redis ingest complete — ADG cache is HOT
      [redis] snapshot stored
      [redis] meta written
      [done] ADG -> Redis ingest complete
```

### 8. Pre-Commit Hooks
- **T0-guard**: Agent Deletion Authorization check
- **T0**: Trailing Whitespace check
- **T0**: End-of-File Fixer (auto-fixes missing newlines)
- Auto-fixes formatting issues in staged files
- Ensures code quality standards before commit
- Can be bypassed with `--no-verify` flag if needed

### 9. GitHub Sync
- Commits all changes with descriptive message
- Pushes to remote repository (e.g., `origin/ADG_v7`)
- Syncs ADG artifacts and code changes
- Maintains version history and collaboration
- Enables team coordination and rollback capability

## Summary

The ADG generation script performs comprehensive QA including:
- ✅ Structural validation
- ✅ Coverage analysis
- ✅ Violation detection
- ✅ Drift monitoring
- ✅ Cryptographic verification
- ✅ Redis hot cache population
- ✅ Pre-commit quality gates
- ✅ Version control sync

All checks must pass before the Redis cache is marked as "HOT" and ready for use. After generation, pre-commit hooks enforce code quality standards, and changes are synced to GitHub for version control and team collaboration.

## Command Reference

```bash
# Full ADG regeneration with Redis auto-ingest
python C:\Git\Agentic-Workflow\tools\generate_full_adg.py

# Commit with pre-commit hooks
git commit -m "Your commit message"

# Commit bypassing pre-commit hooks (use sparingly)
git commit --no-verify -m "Your commit message"

# Push to remote
git push
```
