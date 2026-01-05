# Intelligent Agent Discovery Trigger Model

## Executive Summary

**Problem:** Confusion about when to run `full_agent_discovery.py` (6-8 minute scan) vs. when to use cached `agent_discovery_full.json`.

**Solution:** Intelligent trigger system with staleness detection, automatic invalidation, and smart caching.

---

## Current State Analysis

### What `full_agent_discovery.py` Does
- **Purpose:** Single Source of Truth (SSOT) for all agent metadata
- **Output:** `agent_discovery_full.json` (~312 agents, ~407 total classes)
- **Runtime:** 6-8 minutes with progress bar
- **Scope:** Full AST parsing of all Python files in `agentic_core/`

### Current Consumers (12+ scripts/tools)
1. `canon_validator_agentic_v2_thin.py --report` (dashboard generation)
2. `AutonomyGuardianAgent.generate_compliance_report()`
3. `NamingAgent._build_agent_stem_cache()`
4. `HierarchyAgent.detect_layer_sprawl_violations()`
5. `scan_testing_compliance.py`
6. `bulk_mcp_harden.py`
7. `check_base_class_violations.py`
8. Unit tests (3+ test files)
9. Dashboard live server (file watcher)
10. Analysis scripts (5+ scripts)

### Current Pain Points
1. **No staleness detection** - JSON could be hours/days old
2. **Manual invocation** - User must remember to run it
3. **No invalidation triggers** - Unclear when cache is stale
4. **Redundant scans** - Multiple tools may trigger unnecessary scans
5. **No feedback** - Consumers don't know if data is fresh

---

## Proposed Intelligent Trigger Model

### Decision Tree: When to Run Discovery

```
START
  │
  ├─ Is agent_discovery_full.json missing?
  │    YES → RUN DISCOVERY (mandatory)
  │    NO  → Continue
  │
  ├─ Are we in CI/CD pipeline?
  │    YES → Check if JSON is committed and fresh
  │         ├─ Fresh (< 1 hour old) → USE CACHE
  │         └─ Stale or missing → RUN DISCOVERY
  │    NO  → Continue
  │
  ├─ Has any .py file in agentic_core/ changed since JSON timestamp?
  │    YES → Continue to smart invalidation
  │    NO  → USE CACHE
  │
  ├─ SMART INVALIDATION: What changed?
  │    ├─ New agent file created → RUN DISCOVERY
  │    ├─ Agent file deleted → RUN DISCOVERY
  │    ├─ Agent file renamed → RUN DISCOVERY
  │    ├─ Class definition modified (new class, deleted class) → RUN DISCOVERY
  │    ├─ Method signature changed (affects discovery metadata) → RUN DISCOVERY
  │    ├─ Only method body changed (no structural change) → USE CACHE
  │    └─ Only comments/docstrings changed → USE CACHE
  │
  └─ RESULT: USE CACHE or RUN DISCOVERY
```

---

## Implementation Phases

### Phase 1: Staleness Detection (Foundation)
**Goal:** Know when cache is stale without parsing files

**Components:**
1. **Manifest File** (`agent_discovery_full.manifest.json`)
   ```json
   {
     "generated_at": "2026-01-05T12:00:00Z",
     "scan_duration_seconds": 387,
     "agent_count": 312,
     "file_count": 450,
     "content_hash": "sha256:abc123...",
     "source_files": {
       "agentic_core/L5_safety/validators/NamingAgent.py": {
         "mtime": 1704470400,
         "size": 15234,
         "hash": "sha256:def456..."
       }
     }
   }
   ```

2. **Staleness Checker** (`scripts/check_discovery_staleness.py`)
   - Compare JSON timestamp vs. newest .py file mtime
   - Fast filesystem scan (no AST parsing)
   - Exit codes: 0=fresh, 1=stale, 2=missing

**Dependencies:**
- Python stdlib: `pathlib`, `json`, `hashlib`, `datetime`
- No external dependencies

**Deliverables:**
- `agent_discovery_full.manifest.json` (generated alongside JSON)
- `scripts/check_discovery_staleness.py` (standalone checker)
- Modified `full_agent_discovery.py` to generate manifest

**Estimated Effort:** 2-3 hours

---

### Phase 2: Smart Wrapper (Automatic Triggering)
**Goal:** Consumers call wrapper, wrapper decides whether to scan

**Components:**
1. **Discovery Wrapper** (`scripts/ensure_discovery_fresh.py`)
   ```python
   def ensure_discovery_fresh(
       max_age_seconds: int = 3600,
       force: bool = False,
       quiet: bool = False
   ) -> Path:
       """
       Ensure agent_discovery_full.json is fresh.
       
       Returns: Path to fresh JSON file
       Raises: DiscoveryError if scan fails
       """
   ```

2. **Integration Points**
   - Modify all 12+ consumers to call wrapper instead of reading JSON directly
   - Wrapper checks staleness, runs discovery if needed, returns path

**Decision Logic:**
```python
if force:
    run_discovery()
elif not json_exists():
    run_discovery()
elif is_stale(max_age_seconds):
    run_discovery()
else:
    use_cache()
```

**Dependencies:**
- Phase 1 (staleness detection)
- Modify 12+ consumer scripts

**Deliverables:**
- `scripts/ensure_discovery_fresh.py` (wrapper)
- Updated consumers (12+ files)
- Unit tests for wrapper logic

**Estimated Effort:** 4-6 hours

---

### Phase 3: Git-Aware Invalidation (Smart Caching)
**Goal:** Only re-scan when structural changes occur

**Components:**
1. **Git Change Analyzer** (`scripts/analyze_git_changes.py`)
   - Use `git diff --name-status` to detect changed files
   - Parse changed files to detect structural changes
   - Fast AST parsing of only changed files

2. **Structural Change Detection**
   ```python
   def has_structural_changes(file_path: Path) -> bool:
       """
       Returns True if file has changes that affect discovery:
       - New/deleted classes
       - Class renamed
       - Method signature changes
       - Decorator changes
       - Import changes
       
       Returns False for:
       - Method body changes
       - Comment/docstring changes
       - Whitespace changes
       """
   ```

3. **Incremental Update** (optional optimization)
   - Instead of full re-scan, update only changed files
   - Merge with existing JSON
   - Validate consistency

**Decision Logic:**
```python
changed_files = get_changed_files_since(json_timestamp)
if not changed_files:
    use_cache()
elif any(has_structural_changes(f) for f in changed_files):
    run_discovery()
else:
    use_cache()
```

**Dependencies:**
- Phase 1 (manifest with file hashes)
- Phase 2 (wrapper infrastructure)
- Git repository (for change detection)

**Deliverables:**
- `scripts/analyze_git_changes.py` (change analyzer)
- Enhanced `ensure_discovery_fresh.py` with git-aware logic
- Unit tests for structural change detection

**Estimated Effort:** 6-8 hours

---

### Phase 4: CI/CD Integration (Automation)
**Goal:** Automatic discovery in CI pipeline, cached locally

**Components:**
1. **Pre-commit Hook** (`.git/hooks/pre-commit`)
   - Check if any agent files changed
   - If yes, suggest running discovery (don't block commit)
   - Optional: Auto-run discovery if < 50 files changed

2. **CI Pipeline Step** (GitHub Actions / Jenkins)
   ```yaml
   - name: Ensure Fresh Agent Discovery
     run: python scripts/ensure_discovery_fresh.py --max-age 3600
   ```

3. **Artifact Caching**
   - Cache `agent_discovery_full.json` + manifest in CI
   - Invalidate cache when agentic_core/ changes
   - Share cache across CI jobs

**Dependencies:**
- Phase 2 (wrapper)
- CI/CD system (GitHub Actions, Jenkins, etc.)

**Deliverables:**
- Pre-commit hook template
- CI pipeline configuration
- Cache invalidation rules

**Estimated Effort:** 3-4 hours

---

### Phase 5: Live Monitoring (Advanced)
**Goal:** Real-time discovery updates during development

**Components:**
1. **File Watcher Daemon** (`scripts/discovery_watcher.py`)
   - Use `watchdog` library to monitor agentic_core/
   - Detect file changes in real-time
   - Trigger incremental discovery on structural changes

2. **Dashboard Live Server Integration**
   - Already has file watcher (`dashboard_live_server.py`)
   - Enhance to use smart invalidation
   - Only regenerate dashboard when discovery changes

3. **Developer Feedback**
   - Desktop notification when discovery is stale
   - VS Code extension integration (optional)
   - Status indicator in terminal prompt

**Dependencies:**
- Phase 3 (structural change detection)
- External: `watchdog` library

**Deliverables:**
- `scripts/discovery_watcher.py` (daemon)
- Enhanced `dashboard_live_server.py`
- Optional: VS Code extension

**Estimated Effort:** 8-10 hours

---

## Dependency Graph

```
Phase 1: Staleness Detection (Foundation)
    ↓
Phase 2: Smart Wrapper (Automatic Triggering)
    ↓
Phase 3: Git-Aware Invalidation (Smart Caching)
    ↓
Phase 4: CI/CD Integration (Automation)
    ↓
Phase 5: Live Monitoring (Advanced)
```

**Critical Path:** Phase 1 → Phase 2 → Phase 3
**Optional:** Phase 4, Phase 5

---

## External Dependencies

### Required (All Phases)
- Python 3.8+ (stdlib only for Phases 1-2)
- Git (for Phase 3+)

### Optional (Phase 5)
- `watchdog` (file monitoring)
- `plyer` (desktop notifications)

### No Breaking Changes
- All existing consumers continue to work
- Wrapper is backward-compatible
- JSON format unchanged

---

## Rollout Strategy

### Week 1: Foundation
- Implement Phase 1 (staleness detection)
- Generate manifest alongside JSON
- Test staleness checker

### Week 2: Integration
- Implement Phase 2 (smart wrapper)
- Update 3-5 high-priority consumers
- Validate wrapper logic

### Week 3: Optimization
- Implement Phase 3 (git-aware invalidation)
- Test structural change detection
- Benchmark performance

### Week 4: Automation (Optional)
- Implement Phase 4 (CI/CD integration)
- Add pre-commit hook
- Configure CI caching

### Future: Advanced (Optional)
- Implement Phase 5 (live monitoring)
- Developer experience enhancements

---

## Success Metrics

### Phase 1-2 (Foundation)
- ✅ Zero manual "should I run discovery?" decisions
- ✅ Consumers always use fresh data
- ✅ No redundant scans (< 1 scan per hour)

### Phase 3 (Optimization)
- ✅ 80% cache hit rate (only scan when needed)
- ✅ < 10 second staleness check
- ✅ Accurate structural change detection

### Phase 4-5 (Automation)
- ✅ CI pipeline always has fresh discovery
- ✅ Developers notified of stale cache
- ✅ Dashboard auto-updates on changes

---

## Risk Mitigation

### Risk: False Negatives (Cache Used When Stale)
**Mitigation:** Conservative invalidation (prefer re-scan over stale cache)

### Risk: False Positives (Unnecessary Scans)
**Mitigation:** Phase 3 structural change detection reduces false positives

### Risk: Performance Regression
**Mitigation:** Benchmark staleness check (must be < 10 seconds)

### Risk: Breaking Changes
**Mitigation:** Wrapper is backward-compatible, gradual rollout

---

## Alternative Approaches Considered

### 1. Always Run Discovery (Rejected)
- **Pro:** Always fresh
- **Con:** 6-8 minute overhead on every operation

### 2. Manual Invalidation (Current State)
- **Pro:** Simple
- **Con:** Error-prone, confusing

### 3. Time-Based Cache (Partial Solution)
- **Pro:** Simple to implement
- **Con:** Doesn't detect structural changes, arbitrary timeout

### 4. Incremental Discovery (Future Enhancement)
- **Pro:** Fast updates for small changes
- **Con:** Complex, risk of inconsistency

---

## Recommendation

**Start with Phases 1-3** (Foundation + Optimization)
- Solves 90% of confusion
- Low risk, high value
- 12-17 hours total effort

**Defer Phases 4-5** (Automation + Advanced)
- Nice-to-have, not critical
- Can be added later if needed

**Immediate Next Step:** Implement Phase 1 (staleness detection) to establish foundation.
