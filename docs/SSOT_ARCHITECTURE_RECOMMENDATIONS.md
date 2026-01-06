# Dashboard Data Pipeline: SSOT Architecture Review & Recommendations

**Date:** 2026-01-05  
**Author:** Cascade AI  
**Status:** PROPOSAL

---

## 1. Current Architecture Analysis

### 1.1 Data Flow Diagram (Current State)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CURRENT DATA FLOW (INEFFICIENT)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐                                                    │
│  │ full_agent_discovery │──────► agent_discovery_full.json (SSOT)           │
│  │       .py            │        - 316 agents                                │
│  │   (AST scan #1)      │        - invocation, healing, layer, etc.          │
│  └──────────────────────┘                                                    │
│            ▼                                                                 │
│  ┌──────────────────────┐                                                    │
│  │ AutonomyGuardianAgent│                                                    │
│  │  .generate_report()  │                                                    │
│  │                      │                                                    │
│  │  ┌─────────────────┐ │                                                    │
│  │  │ _load_registry  │◄┼─── Reads JSON (good)                               │
│  │  └─────────────────┘ │                                                    │
│  │          ▼           │                                                    │
│  │  ┌─────────────────┐ │                                                    │
│  │  │ _process_territ │ │                                                    │
│  │  │      ories      │ │                                                    │
│  │  │  (22 file reads │◄┼─── REDUNDANT: Re-reads files already parsed        │
│  │  │   11 AST parses)│ │     in discovery                                   │
│  │  └─────────────────┘ │                                                    │
│  │          ▼           │                                                    │
│  │  ┌─────────────────┐ │                                                    │
│  │  │_save_markdown   │ │                                                    │
│  │  │    _report      │ │                                                    │
│  │  │ (re-reads files │◄┼─── REDUNDANT: Third pass over same files           │
│  │  │  for metrics)   │ │                                                    │
│  │  └─────────────────┘ │                                                    │
│  │          ▼           │                                                    │
│  │  ┌─────────────────┐ │                                                    │
│  │  │_generate_self   │ │                                                    │
│  │  │ _contained_dash │ │                                                    │
│  │  │ (ANOTHER scan)  │◄┼─── REDUNDANT: Fourth pass, recalculates everything │
│  │  └─────────────────┘ │                                                    │
│  └──────────────────────┘                                                    │
│            ▼                                                                 │
│  ┌──────────────────────┐                                                    │
│  │ autonomy_dashboard   │                                                    │
│  │      .html           │                                                    │
│  └──────────────────────┘                                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Identified Issues

| Issue | Location | Impact |
|-------|----------|--------|
| **Multiple file reads** | AutonomyGuardianAgent | 22 `.read_text()` calls per run |
| **Redundant AST parsing** | AutonomyGuardianAgent | 11 `ast.parse()` calls per run |
| **Duplicate metric calculation** | `_save_markdown_report`, `_generate_self_contained_dashboard` | Same metrics computed 3-4 times |
| **String-based detection fallback** | `_detect_healing_invocation`, `_detect_healing_capability` | Bypasses JSON SSOT |
| **Stale cache returning old values** | `metrics_cache` | Required SSOT override fix |
| **32+ consumers of JSON** | See grep results | Each potentially re-parsing data |

### 1.3 Data Hops Count (Current)

```
Source Files → [HOP 1] → full_agent_discovery.py (AST parse)
            → [HOP 2] → agent_discovery_full.json
            → [HOP 3] → AutonomyGuardianAgent._load_registry()
            → [HOP 4] → _process_territories() re-reads files
            → [HOP 5] → _save_markdown_report() re-reads files  
            → [HOP 6] → _generate_self_contained_dashboard() re-reads
            → [HOP 7] → autonomy_dashboard.html (embedded JSON)

Total: 7 hops, 4 redundant file scan passes
```

---

## 2. Recommended SSOT Architecture

### 2.1 Target Data Flow (Optimized)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROPOSED DATA FLOW (SSOT-FIRST)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────┐                                                    │
│  │ full_agent_discovery │──────► agent_discovery_full.json                   │
│  │       .py            │        (COMPLETE SSOT)                             │
│  │  (SINGLE AST scan)   │                                                    │
│  │                      │        Contains ALL metrics:                       │
│  │  - invocation        │        - invocation ✓                              │
│  │  - healing_cap       │        - healing_cap ✓                             │
│  │  - mcp_hardened      │        - mcp_hardened ✓                            │
│  │  - has_tests         │        - has_tests (NEW)                           │
│  │  - typed_pct         │        - typed_pct (NEW)                           │
│  │  - documented_pct    │        - documented_pct (NEW)                      │
│  │  - observable        │        - observable (NEW)                          │
│  │  - cc (complexity)   │        - cc (NEW)                                  │
│  │  - loc               │        - loc ✓                                     │
│  └──────────────────────┘                                                    │
│            │                                                                 │
│            ▼ (SINGLE HOP)                                                    │
│  ┌──────────────────────┐                                                    │
│  │ AutonomyGuardianAgent│                                                    │
│  │  .generate_report()  │                                                    │
│  │                      │                                                    │
│  │  PURE AGGREGATION:   │                                                    │
│  │  - No file reads     │                                                    │
│  │  - No AST parsing    │                                                    │
│  │  - Just JSON math    │                                                    │
│  └──────────────────────┘                                                    │
│            │                                                                 │
│            ▼ (SINGLE HOP)                                                    │
│  ┌──────────────────────┐                                                    │
│  │ autonomy_dashboard   │                                                    │
│  │      .html           │                                                    │
│  └──────────────────────┘                                                    │
│                                                                              │
│  Total: 3 hops, 0 redundant file scans                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Implementation Phases

#### Phase 1: Extend Discovery JSON (LOW RISK)

Add these fields to `full_agent_discovery.py` output:

```python
# In agents.append({...})
{
    'class_name': node.name,
    'path': str(rel_path),
    'layer': layer,
    'invocation': invocation,           # ✓ Already added
    'has_healing': has_healing,         # ✓ Already exists
    
    # NEW FIELDS TO ADD:
    'has_tests': detect_tests(node, source),
    'mcp_hardened': detect_mcp_hardened(node, source),
    'typed_pct': calculate_typed_pct(node),
    'documented_pct': calculate_docstring_coverage(node),
    'observable': detect_observability(node, source),
    'cyclomatic_complexity': calculate_cc(node),
    'loc': loc,                         # ✓ Already exists
    'used_elsewhere': False,            # Computed post-scan
}
```

#### Phase 2: Refactor AutonomyGuardianAgent (MEDIUM RISK)

Replace file-scanning methods with JSON aggregation:

```python
# BEFORE (current)
def _analyze_single_agent(self, agent: Path, ...):
    content = agent.read_text()  # File I/O
    tree = ast.parse(content)    # CPU intensive
    # ... 50+ lines of detection logic

# AFTER (proposed)
def _analyze_single_agent(self, registry_entry: dict, ...):
    # Pure data extraction - no I/O
    return {
        "healing_invoke": 1 if registry_entry["invocation"] in ("Yes", "Inherited") else 0,
        "healing_cap": 1 if registry_entry["has_healing"] else 0,
        "hardened": 1 if registry_entry["mcp_hardened"] else 0,
        "tests": 1 if registry_entry["has_tests"] else 0,
        "typed": registry_entry.get("typed_pct", 0),
        "documented": registry_entry.get("documented_pct", 0),
        "observable": 1 if registry_entry.get("observable") else 0,
        "cc_sum": registry_entry.get("cyclomatic_complexity", 0),
        "loc": registry_entry.get("loc", 0),
    }
```

#### Phase 3: Eliminate Redundant Methods (LOW RISK)

Delete or deprecate:
- `_detect_healing_invocation()` - Use JSON
- `_detect_healing_capability()` - Use JSON
- `_detect_mcp_hardening()` - Use JSON
- `_detect_mcp_capability()` - Use JSON
- `_detect_tests()` - Use JSON
- String-based detection in `_save_markdown_report()`

---

## 3. Optimal Execution Model for full_agent_discovery.py

### 3.1 Current Execution Model

```
CURRENT: Manual execution only
  - Developer runs: python scripts/full_agent_discovery.py
  - No automatic triggers
  - JSON can become stale
  - Dashboard shows outdated data
```

### 3.2 Proposed Execution Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SMART DISCOVERY EXECUTION MODEL                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TRIGGER CONDITIONS (ANY of these):                                          │
│                                                                              │
│  1. FILE CHANGE TRIGGERS (git pre-commit hook)                               │
│     ├─ New .py file created in agentic_core/ or apps_*/                     │
│     ├─ Class renamed (Agent suffix added/removed)                           │
│     ├─ heal_repository method added/removed                                  │
│     └─ HealerMixin added/removed from class bases                           │
│                                                                              │
│  2. SCHEDULED TRIGGERS (CI/CD)                                               │
│     ├─ On PR merge to main                                                   │
│     ├─ Daily at 00:00 UTC (catch drift)                                     │
│     └─ Before dashboard generation                                           │
│                                                                              │
│  3. ON-DEMAND TRIGGERS                                                       │
│     ├─ Before generate_compliance_report() if JSON stale                    │
│     ├─ CLI: python -m agentic_core.discovery --refresh                      │
│     └─ IDE: Ctrl+Shift+D (VS Code task)                                     │
│                                                                              │
│  STALENESS DETECTION:                                                        │
│     ├─ Compare JSON mtime vs latest .py mtime in agentic_core/              │
│     ├─ Compare agent count vs EXPECTED_AGENT_COUNT                          │
│     └─ Compare manifest.json hash vs current file hashes                    │
│                                                                              │
│  EXECUTION OPTIMIZATION:                                                     │
│     ├─ INCREMENTAL MODE: Only scan changed files                            │
│     │   - Use file hashes from manifest                                      │
│     │   - Skip unchanged files                                               │
│     │   - ~10x faster for small changes                                     │
│     │                                                                        │
│     └─ FULL MODE: Complete rescan                                            │
│         - Triggered when incremental would miss structural changes          │
│         - Required after refactors, renames, moves                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Implementation: Smart Discovery Runner

```python
# Proposed: scripts/smart_discovery.py

import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
DISCOVERY_JSON = PROJECT_ROOT / "agent_discovery_full.json"
MANIFEST_JSON = PROJECT_ROOT / "agent_discovery_full.manifest.json"
STALENESS_THRESHOLD = timedelta(hours=1)  # Max age before auto-refresh

def is_discovery_stale() -> bool:
    """Check if discovery JSON needs refresh."""
    if not DISCOVERY_JSON.exists():
        return True
    
    # Check JSON age
    json_mtime = datetime.fromtimestamp(DISCOVERY_JSON.stat().st_mtime)
    if datetime.now() - json_mtime > STALENESS_THRESHOLD:
        return True
    
    # Check if any source files are newer than JSON
    for py_file in (PROJECT_ROOT / "agentic_core").rglob("*.py"):
        if py_file.stat().st_mtime > DISCOVERY_JSON.stat().st_mtime:
            return True
    
    return False

def get_changed_files() -> list[Path]:
    """Get files changed since last discovery."""
    if not MANIFEST_JSON.exists():
        return []  # Force full scan
    
    manifest = json.loads(MANIFEST_JSON.read_text())
    file_hashes = manifest.get("file_hashes", {})
    changed = []
    
    for py_file in (PROJECT_ROOT / "agentic_core").rglob("*.py"):
        rel_path = str(py_file.relative_to(PROJECT_ROOT))
        current_hash = hashlib.md5(py_file.read_bytes()).hexdigest()
        if file_hashes.get(rel_path) != current_hash:
            changed.append(py_file)
    
    return changed

def run_discovery(incremental: bool = True) -> None:
    """Run discovery with smart mode selection."""
    changed = get_changed_files()
    
    if not incremental or len(changed) > 50:  # Full scan threshold
        print("Running FULL discovery scan...")
        import subprocess
        subprocess.run(["python", "scripts/full_agent_discovery.py"])
    else:
        print(f"Running INCREMENTAL scan ({len(changed)} files)...")
        # TODO: Implement incremental update
        # For now, fall back to full scan
        import subprocess
        subprocess.run(["python", "scripts/full_agent_discovery.py"])

def ensure_fresh_discovery() -> None:
    """Called by AutonomyGuardianAgent before report generation."""
    if is_discovery_stale():
        print("[DISCOVERY] JSON is stale, refreshing...")
        run_discovery()
    else:
        print("[DISCOVERY] JSON is fresh, skipping scan")
```

### 3.4 Git Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if any agent files changed
AGENT_FILES=$(git diff --cached --name-only | grep -E '^agentic_core/.*Agent.*\.py$')

if [ -n "$AGENT_FILES" ]; then
    echo "Agent files changed, running discovery..."
    python scripts/full_agent_discovery.py --quick
    git add agent_discovery_full.json agent_discovery_full.manifest.json
fi
```

---

## 4. Migration Path

### 4.1 Backward Compatibility

During migration, support both modes:

```python
# In AutonomyGuardianAgent.__init__
self.use_ssot_mode = os.environ.get("DASHBOARD_SSOT_MODE", "true").lower() == "true"

# In _analyze_single_agent
if self.use_ssot_mode:
    return self._analyze_from_json(registry_entry)
else:
    return self._analyze_from_file(agent_path)  # Legacy
```

### 4.2 Validation

Add dashboard QA test:

```python
def test_ssot_parity():
    """Ensure JSON-based metrics match file-based metrics."""
    # Run both modes
    json_metrics = generate_report(ssot_mode=True)
    file_metrics = generate_report(ssot_mode=False)
    
    # Compare key metrics
    assert json_metrics["invocation_pct"] == file_metrics["invocation_pct"]
    assert json_metrics["healing_cap_pct"] == file_metrics["healing_cap_pct"]
    # ...
```

---

## 5. Expected Benefits

| Metric | Current | After SSOT | Improvement |
|--------|---------|------------|-------------|
| File reads per report | 22+ | 0 | 100% reduction |
| AST parses per report | 11+ | 0 | 100% reduction |
| Report generation time | ~15s | ~1s | 15x faster |
| Data consistency bugs | Frequent | Eliminated | 100% |
| Code complexity (CC) | 257 | ~50 | 80% reduction |

---

## 6. Summary of Recommendations

1. **Extend `full_agent_discovery.py`** to compute ALL metrics (tests, typing, observability, complexity)
2. **Refactor `AutonomyGuardianAgent`** to be a pure JSON aggregator with zero file I/O
3. **Implement smart discovery execution** with staleness detection and incremental updates
4. **Add git pre-commit hook** to auto-refresh discovery on agent file changes
5. **Deprecate string-based detection** methods that bypass SSOT
6. **Add SSOT parity tests** to prevent regression

---

## Appendix A: Files to Modify

| File | Changes |
|------|---------|
| `scripts/full_agent_discovery.py` | Add tests, typing, observability, CC metrics |
| `AutonomyGuardianAgent.py` | Remove file scanning, use JSON only |
| `structure_blueprint.py` | Add SSOT validation rules |
| `.git/hooks/pre-commit` | Add discovery trigger |
| `scripts/smart_discovery.py` | New file - smart execution logic |

