# AutonomyGuardianAgent Duplicate Analysis

**Date**: January 5, 2026  
**Issue**: Two files with same name in different paths not flagged by CodeDeduplicationAgent

---

## Files in Question

1. **Active/Production Version**:
   - Path: `agentic_core/L5_safety/validators/AutonomyGuardianAgent.py`
   - Lines: **3,092**
   - Hash: `2b0e20859312a63a...`
   - Purpose: Production autonomy compliance validator and dashboard generator

2. **Blueprint/Reference Version**:
   - Path: `agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent.py`
   - Lines: **2,211**
   - Hash: `9677f8c0cfe15c63...`
   - Purpose: Blueprint/template version (older snapshot)

---

## Root Cause Analysis

### Why CodeDeduplicationAgent Didn't Flag This

The `CodeDeduplicationAgent.scan_filename_duplicates()` method **DID detect** these files but classified them correctly as **"DIVERGENT CONTENT (RENAME ONLY)"** rather than duplicates requiring consolidation.

**Evidence from the code** (`CodeDeduplicationAgent.py:256-276`):

```python
def scan_filename_duplicates(self, python_files: List[Path], project_root: Path) -> None:
    """Detect duplicate basenames with safety check (identical vs divergent content)."""
    print('\n[*] CodeDeduplicationAgent: Scanning for duplicate filenames (safety-enhanced)...')
    basename_to_entries: Dict[str, List[Tuple[Path, str]]] = defaultdict(list)
    for path in python_files:
        if not path.exists() or 'archives' in str(path) or path.name in {'__init__.py', 'setup.py'}:
            continue
        basename = path.name
        file_hash = self._hash_entire_file(path) or 'ERROR'
        basename_to_entries[basename].append((path, file_hash))
    for basename, entries in basename_to_entries.items():
        if len(entries) > 1:
            hashes = {h for _, h in entries}
            status = "IDENTICAL CONTENT" if len(hashes) == 1 else "DIVERGENT CONTENT (RENAME ONLY)"
            print(f'   [!] DUPLICATE FILENAME: {basename} ({len(entries)} copies) — {status}')
            for p, h in entries:
                rel = p.relative_to(project_root)
                print(f'      -> {rel} (hash: {h[:8]}...)')
            self.filename_duplicates[basename] = entries
```

**Key Logic**:
- Line 268: Computes unique hashes for all files with same basename
- Line 269: If `len(hashes) == 1` → IDENTICAL (consolidate), else → DIVERGENT (rename only)
- Since the two AutonomyGuardianAgent.py files have **different hashes**, they were correctly classified as **DIVERGENT**

### Actual Differences Between Files

**Size difference**: 881 lines (3,092 vs 2,211)

**Major differences** (from diff analysis):
1. **Territory structure**: L5 version has updated territory definitions with Base Class subterritories (added 2026-01-05)
2. **Metrics caching**: L5 version has incremental caching (`metrics_cache_path`, `_load_metrics_cache()`)
3. **Imports**: L5 version imports `hashlib` and `subprocess`
4. **Territory granularity**: Blueprint has older folder-based structure; L5 has new 4-subterritory pattern (Base Class, Core, Infrastructure, Specialized)

**Blueprint version is outdated** - appears to be a reference/template from before the recent territory structure refactoring.

---

## Why This Is NOT a Bug

The CodeDeduplicationAgent is **working as designed**:

1. ✅ **Detected** the duplicate filename
2. ✅ **Analyzed** content hashes
3. ✅ **Correctly classified** as DIVERGENT (different content)
4. ✅ **Recommended** rename-only (not consolidation)

The agent's safety logic prevents it from:
- Deleting the wrong version
- Consolidating files that have diverged functionally
- Making destructive changes without human review

---

## Recommended Actions

### Option 1: Archive the Blueprint Version (Recommended)

The blueprint version appears to be a **reference snapshot** that's now outdated.

**Action**:
```bash
# Move to archives with timestamp
mkdir -p archives/blueprints/2026-01-05
mv agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent.py \
   archives/blueprints/2026-01-05/AutonomyGuardianAgent_blueprint_pre_territory_refactor.py
```

**Rationale**:
- Preserves historical reference
- Removes naming conflict
- Clear timestamp and purpose in filename

### Option 2: Delete the Blueprint Version

If the blueprint is no longer needed as a reference.

**Action**:
```bash
rm agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent.py
```

**Rationale**:
- L5 version is the active, production code
- Blueprint is 881 lines behind
- No active references to blueprint version in codebase

### Option 3: Rename Blueprint to Indicate Purpose

If the blueprint should be kept as a template.

**Action**:
```bash
mv agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent.py \
   agentic_core/config/blueprint_sovereign/AutonomyGuardianAgent_TEMPLATE.py
```

**Rationale**:
- Makes purpose explicit
- Removes naming conflict
- Keeps reference available

---

## CodeDeduplicationAgent Enhancement Opportunities

While the agent worked correctly, we could enhance reporting:

### Enhancement 1: Explicit Divergent File Report

Add a summary section for divergent duplicates that need human review:

```python
def _report_divergent_duplicates(self):
    """Report files with same name but different content requiring manual review."""
    divergent = []
    for basename, entries in self.filename_duplicates.items():
        hashes = {h for _, h in entries}
        if len(hashes) > 1:  # Divergent content
            divergent.append((basename, entries))
    
    if divergent:
        print("\n[!] DIVERGENT DUPLICATES REQUIRING MANUAL REVIEW:")
        for basename, entries in divergent:
            print(f"   {basename}: {len(entries)} versions with different content")
            for path, hash in entries:
                print(f"      - {path} (hash: {hash[:8]}...)")
```

### Enhancement 2: Suggest Archive for Older Versions

Use file modification time to suggest archiving older versions:

```python
def _suggest_archive_older_version(self, entries: List[Tuple[Path, str]]) -> Optional[Path]:
    """Suggest archiving the older of two divergent files."""
    if len(entries) != 2:
        return None
    
    paths_with_mtime = [(p, p.stat().st_mtime) for p, _ in entries]
    paths_with_mtime.sort(key=lambda x: x[1])  # Sort by modification time
    older_path = paths_with_mtime[0][0]
    
    return older_path
```

---

## Conclusion

**CodeDeduplicationAgent is working correctly** - it detected the duplicate filenames and correctly identified them as divergent content requiring manual review rather than automatic consolidation.

The issue is not a bug but a **legitimate naming conflict** that requires human decision:
- Keep blueprint as reference → rename it
- Blueprint is obsolete → archive or delete it
- Both are needed → rename one to clarify purpose

**Recommended immediate action**: Archive the blueprint version to `archives/blueprints/2026-01-05/AutonomyGuardianAgent_blueprint_pre_territory_refactor.py`
