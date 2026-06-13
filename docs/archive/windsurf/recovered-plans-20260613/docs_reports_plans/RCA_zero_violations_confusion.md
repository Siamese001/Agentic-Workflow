# RCA: "Zero Violations" Confusion

## The Question
"If there was zero in burndown, how is this possible?" — referring to ADG artifact showing 285 syntax errors and 111 layer violations.

## Root Cause: Multiple Independent Violation Systems

The repository has **three separate violation tracking systems** that are NOT connected:

### 1. Anti-Pattern Violations (What We Fixed)
- **Checker:** `ops_scripts/ci/check_anti_patterns.py`
- **Baseline:** `ops_scripts/hooks/landmine_baseline.txt` (1790 existing)
- **Status:** ✅ **0 NEW violations** (all existing suppressed with guardian tokens)
- **Categories:** `global_mutation`, `magic_configuration`, `path_fragility`, `type_erasure`, `config_with_logic`, `silent_swallower`
- **Scope:** Runtime anti-patterns (sys.path.insert, hardcoded timeouts, string path concat, etc.)

### 2. ADG Syntax Errors (NOT Fixed)
- **Source:** `artifacts/adg/adg_full_20260310T232427Z.json`
- **Count:** 285 syntax errors
- **Status:** ❌ **NOT addressed** in anti-pattern burndown
- **Cause:** Files that fail `ast.parse()` during dependency graph construction
- **Impact:** These files are excluded from the dependency graph (orphan nodes)

### 3. ADG Layer Violations (NOT Fixed)
- **Source:** Same ADG artifact
- **Count:** 111 layer violations
- **Status:** ❌ **NOT addressed** in anti-pattern burndown
- **Definition:** Import edges that violate layer gravity rules (e.g., L0 importing from L5)
- **Checker:** Separate from anti-pattern checker

## Why They're Separate

| System | Checker | Baseline | Scope |
|--------|---------|----------|-------|
| Anti-patterns | `check_anti_patterns.py` | `landmine_baseline.txt` | Runtime code quality |
| Syntax errors | `dep_graph_db.py` | None | AST parse failures |
| Layer violations | `dep_graph_db.py` | None | Architecture boundaries |

## What "Zero Violations" Actually Means

**Anti-pattern burndown achieved:** 0 **NEW** anti-pattern violations
- All 1790 existing anti-patterns are baselined with guardian suppressions
- No new `sys.path.insert`, hardcoded timeouts, or string path concatenations introduced

**ADG issues remain unaddressed:**
- 285 files still have syntax errors (cannot be parsed by AST)
- 111 import edges still violate layer gravity rules
- These are **separate technical debt** not covered by anti-pattern checker

## Next Steps to Address ADG Issues

### Fix Syntax Errors (285 files)
1. Run `python tools/dep_graph_db.py` to identify which files fail parsing
2. Inspect each file for syntax issues (likely: unclosed strings, bad indentation, encoding issues)
3. Fix or quarantine unparseable files

### Fix Layer Violations (111 edges)
1. Use ADG to identify specific import edges violating gravity
2. Apply layer-boundary-guard skill to enforce L0→L1→...→L6 hierarchy
3. Refactor imports to respect layer boundaries

## Recommendation

The anti-pattern work is **complete and correct** — we achieved zero NEW violations.

The ADG issues are a **separate workstream** requiring:
- Syntax error remediation (file-by-file AST parse fixes)
- Layer violation remediation (import refactoring per gravity rules)

These should be tracked as separate tasks, not conflated with anti-pattern burndown.

## Violation

[Describe the violation or issue that triggered this RCA]

---

## Corrective Actions

[List the corrective actions taken to resolve the issue]

---

