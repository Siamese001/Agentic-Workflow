---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\cascade_ast_dependency_graph_hardening_summary.md'
original_relative_path: 'cascade_ast_dependency_graph_hardening_summary.md'
source_sha256: 4dda0a628b358c8765e22eb9b4dff7fb28da9bd8eb2360641e3d402227d9fdb7
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-09'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Cascade AST Dependency Graph Hardening Summary

**Date:** 2026-03-09
**Objective:** Harden Cascade configuration to enforce rigorous testing standards and make AST dependency graphs the absolute default for all code analysis.

**Constitutional Principle:** **DEFAULT = DETAILED AST DEPENDENCY GRAPH**

---

## Wave Structure

| Waves | Metric | Scope | Checkpoint | Tokens |
|-------|--------|-------|------------|---------|
| Wave 1 | Analysis & Discovery | Review current state | A | 25,000 🟢 |
| Wave 2 | Implementation | Core changes | B | 50,000 🟢 |
| Wave 3 | Testing & Validation | Verify changes | C | 30,000 🟢 |
| Wave 4 | Documentation & Cleanup | Finalize | D | 15,000 🟢 |

**Total: 120,000 tokens across 4 waves, all GREEN**

---


## Executive Summary

Comprehensive hardening of Cascade rules, skills, and workflows to enforce:
1. AST dependency graphs as the PRIMARY and DEFAULT analysis method
2. Automatic blocking of all code investigation until dependency graph is built
3. Mandatory graph-backed evidence in all analysis and modifications
4. Rigorous testing standards with graph-backed test selection
5. Fail-closed discipline when AST parsing fails

---

## Changes to `.windsurfrules`

### New §0: DEFAULT ANALYSIS MODE

Added comprehensive default analysis mode section that establishes AST dependency graphs as the mandatory starting point for ALL code work.

**Key Requirements:**
- Build AST dependency graph FIRST (before any other analysis)
- Use graph as PRIMARY evidence (text search only as secondary confirmation)
- Block work if graph cannot be built (fail-closed, no silent fallback)
- Document graph in all evidence (DEPENDENCY_GRAPH section mandatory)

**Automatic Triggers:**
- User mentions: files, functions, classes, modules, imports, dependencies
- User asks: "what uses this", "what depends on", "impact of", "blast radius"
- User requests: refactor, modify, analyze, investigate, debug, trace
- User inquires: test coverage, dead code, duplicates, boundaries

**Immediate Actions (before responding):**
1. Invoke `dependency-graph-analysis` skill
2. Build graph per `graph_construction_protocol.md`
3. Extract all required relationships
4. Document in DEPENDENCY_GRAPH section
5. THEN proceed with user request using graph-backed evidence

**Forbidden Default Behavior:**
- ❌ Starting with grep/ripgrep
- ❌ Starting with filename searches
- ❌ Starting with text pattern matching
- ❌ Assuming relationships without graph proof
- ❌ Claiming "no dependencies" without graph analysis

### Updated §1.1: Zero-tolerance testing

Added prerequisite: Build AST dependency graph to identify test coverage edges.

**New Requirements:**
- Use dependency graph to find existing test coverage edges
- Use dependency graph to identify coverage gaps
- Create new tests for any function/class without test coverage edge

### Updated §3.1: Scope declaration

Added prerequisite: Build AST dependency graph to determine true scope.

**New Process:**
1. Build dependency graph from proposed changes
2. Identify all upstream dependencies
3. Identify all downstream dependents
4. Identify all required test files via graph edges
5. Declare scope with graph justification for each file

**Requirement:** Each file in scope MUST have graph justification (§3.7).

### Updated §3.2: Scope contamination

Added graph justification check to contamination detection.

**New Steps:**
1. Record unrelated files
2. **Check if files have graph justification (§3.7)**
3. If NO graph justification → scope contamination
4. Reset to baseline
5. Restore declared files only
6. Verify diff
7. Verify each file has graph justification

### Enhanced §3.4-§3.7: Dependency Graph Requirements

Previously added comprehensive dependency graph requirements:
- §3.4: AST dependency graphs as mandatory primary analysis primitive
- §3.5: Forbidden low-signal search methods
- §3.6: Fail-closed discipline for parse failures
- §3.7: DEPENDENCY_GRAPH evidence contract

### Enhanced §4.4: Dependency graph before edit

Previously added requirement for graph-backed impact analysis before any code edit.

### Enhanced §5.2: Graph-backed test selection

Previously added requirement for dependency-graph-backed test selection.

---

## New Skills Created

### 1. `ast-first-gate` Skill

**Purpose:** BLOCKS all code investigation and analysis work until AST dependency graph is built.

**Files:**
- `SKILL.md` - Skill overview and integration
- `pre_analysis_gate.md` - Mandatory gate protocol that blocks work
- `ast_first_checklist.md` - Quick compliance checklist

**Key Features:**
- Automatic triggers for code-related requests
- Blocks all work until graph is built and documented
- Enforces §0 DEFAULT ANALYSIS MODE
- No bypass conditions (except explicit user override with warning)
- Integrates with all other skills as prerequisite

**Gate Protocol:**
1. Detect code investigation request
2. BLOCK until graph built
3. Build dependency graph
4. Document DEPENDENCY_GRAPH section
5. Validate graph completeness
6. Gate decision (open/blocked)

**Fail-Closed Behavior:**
- If graph construction fails → BLOCK
- Record exact parse errors
- Mark analysis as PARTIAL
- Reduce confidence level to LOW
- Report limitation explicitly to user
- Offer remediation path

### 2. `dependency-graph-analysis` Skill (Previously Created)

**Purpose:** Provides AST-based dependency graph analysis workflows.

**Files:**
- `SKILL.md` - Skill overview
- `graph_construction_protocol.md` - Step-by-step graph building
- `impact_analysis_template.md` - Complete impact analysis template
- `fail_closed_discipline.md` - Parse failure handling protocol
- `forbidden_methods_checklist.md` - Verification checklist

**Mandatory For:**
- Root cause analysis
- Impact analysis
- File selection
- Duplicate detection
- Dead code detection
- Boundary validation
- Layer inversion detection
- Test selection
- Healing scope
- Refactor planning
- Execution path analysis
- Registry and wiring validation

---

## Updates to Existing Skills

### `test-rigor-enforcement` Skill

**Changes:**
- Added PREREQUISITE: `ast-first-gate` skill MUST be invoked first
- Updated description to emphasize AST dependency graph backing
- Enhanced `pre_code_generation_gate.md`:
  - Added Step 2: Build Dependency Graph (mandatory before identifying surfaces)
  - Added Step 4: Identify Required Tests via Dependency Graph
  - Updated gate decision to block if graph not built
  - Added graph justification for all changed surfaces
  - Updated example with complete dependency graph analysis
  - Added constitutional references for §0, §3.4-§3.7, §4.4, §5.2

### `scope-guard` Skill

**Changes:**
- Added PREREQUISITE: `ast-first-gate` skill MUST be invoked first
- Updated description to emphasize AST dependency graph analysis
- Enhanced `scope_precheck.md`:
  - Added Step 1: Build Dependency Graph (mandatory before declaring scope)
  - Updated Step 2: Declare scope with graph justification for each file
  - Updated Step 4: Verify files have graph justification
  - Added graph-backed verification protocol
- Enhanced `SKILL.md`:
  - Added constitutional requirements enforced (§0, §3.4, §3.5, §3.7, §4.4)

### `evidence-bundle` Skill

**Changes:**
- Added PREREQUISITE: `ast-first-gate` skill MUST be invoked first
- Updated description to require DEPENDENCY_GRAPH section per §0
- Enhanced `evidence_template.md`:
  - Added comprehensive Section 3: DEPENDENCY_GRAPH (mandatory)
  - Includes: graph roots, node types, edge types, impacted nodes
  - Includes: upstream/downstream dependencies, cross-layer edges
  - Includes: cycle/SCC findings, boundary violations, test surface implications
  - Includes: scope justification with graph evidence for each file
  - Added forbidden methods checklist
  - Added fail-closed discipline checklist
  - Renumbered subsequent sections (4-7)
- Enhanced `command_capture_snippets.ps1`:
  - Added MANDATORY: AST DEPENDENCY GRAPH section at top
  - Provided 3 options for building dependency graphs
  - Added graph documentation requirements
  - Updated pytest section with graph-backed test identification
  - Added test coverage verification against dependency graph

---

## Skill Dependency Hierarchy

```
ast-first-gate (PREREQUISITE for all code work)
    ↓
dependency-graph-analysis (provides graph construction)
    ↓
├── test-rigor-enforcement (uses graph for test identification)
├── scope-guard (uses graph for scope justification)
└── evidence-bundle (uses graph for DEPENDENCY_GRAPH section)
```

**Enforcement Flow:**
1. User makes code-related request
2. `ast-first-gate` automatically triggered
3. Gate BLOCKS until dependency graph built
4. `dependency-graph-analysis` invoked to build graph
5. Graph documented in DEPENDENCY_GRAPH section
6. Gate opens, other skills can proceed with graph-backed evidence

---

## Constitutional Enforcement Summary

### §0: DEFAULT ANALYSIS MODE
- **Status:** HARDENED
- **Enforcement:** Automatic blocking via `ast-first-gate` skill
- **Coverage:** All code investigation, analysis, and modification tasks

### §1: TESTING & EVIDENCE
- **Status:** HARDENED
- **Enforcement:** Graph-backed test identification via `test-rigor-enforcement`
- **Coverage:** All code changes require graph-identified tests

### §3: SCOPE & DETERMINISM
- **Status:** HARDENED
- **Enforcement:** Graph-backed scope justification via `scope-guard`
- **Coverage:** All scope declarations require graph evidence

### §3.4: AST dependency graphs mandatory
- **Status:** HARDENED
- **Enforcement:** Automatic via §0 DEFAULT ANALYSIS MODE
- **Coverage:** All non-trivial code investigations

### §3.5: No low-signal search
- **Status:** HARDENED
- **Enforcement:** `forbidden_methods_checklist.md` verification
- **Coverage:** Grep/regex forbidden as primary analysis method

### §3.6: Fail-closed discipline
- **Status:** HARDENED
- **Enforcement:** `fail_closed_discipline.md` protocol
- **Coverage:** All AST parsing failures

### §3.7: DEPENDENCY_GRAPH evidence contract
- **Status:** HARDENED
- **Enforcement:** Mandatory section in `evidence_template.md`
- **Coverage:** All evidence files for code analysis

### §4.4: Dependency graph before edit
- **Status:** HARDENED
- **Enforcement:** `pre_analysis_gate.md` blocks edits without graph
- **Coverage:** All code edits

### §5.2: Graph-backed test selection
- **Status:** HARDENED
- **Enforcement:** `pre_code_generation_gate.md` Step 4
- **Coverage:** All test identification and selection

---

## Verification Checklist

Use this checklist to verify hardening is effective:

### For Any Code Investigation Request

- [ ] `ast-first-gate` skill automatically triggered
- [ ] Work BLOCKED until dependency graph built
- [ ] Dependency graph built using AST parsing (not grep)
- [ ] All required edge types extracted
- [ ] DEPENDENCY_GRAPH section documented
- [ ] Graph completeness validated
- [ ] Gate opened only after graph complete

### For Any Code Modification

- [ ] Dependency graph built FIRST
- [ ] Scope declared with graph justification for each file
- [ ] Tests identified via graph edges (not filename similarity)
- [ ] Impact analysis includes upstream/downstream from graph
- [ ] Cross-layer edges checked
- [ ] Cycles/boundaries validated
- [ ] Evidence includes complete DEPENDENCY_GRAPH section

### For Any Test Selection

- [ ] Tests identified via dependency graph edges
- [ ] Direct test coverage edges mapped
- [ ] Integration test edges identified
- [ ] Coverage gaps detected via graph
- [ ] No reliance on filename similarity
- [ ] Test selection justified by graph evidence

### For Any Evidence File

- [ ] DEPENDENCY_GRAPH section present
- [ ] Graph roots documented
- [ ] Upstream/downstream dependencies documented
- [ ] Test surface implications documented
- [ ] Scope justification with graph evidence
- [ ] Parse failures recorded (if any)
- [ ] Completeness percentage stated

---

## Impact on Cascade Behavior

### Before Hardening

**Typical Flow:**
1. User asks "what depends on file.py?"
2. Cascade uses grep to search for imports
3. Returns text search results (may be incomplete/incorrect)
4. No graph documentation
5. No validation of completeness

**Problems:**
- Grep misses dynamic imports, registry lookups, factory resolution
- False positives from comments/strings
- Cannot detect cycles or boundaries
- No evidence of analysis method
- Low confidence results

### After Hardening

**Typical Flow:**
1. User asks "what depends on file.py?"
2. `ast-first-gate` automatically triggered
3. Gate BLOCKS response
4. `dependency-graph-analysis` invoked
5. AST dependency graph built with file.py as root
6. All edge types extracted (imports, calls, inheritance, registry, tests)
7. Downstream dependents identified via graph
8. DEPENDENCY_GRAPH section documented
9. Graph validated (completeness, parse errors)
10. Gate opens
11. Cascade responds with graph-backed answer
12. Evidence includes complete DEPENDENCY_GRAPH section

**Benefits:**
- AST parsing catches all dependency types
- No false positives
- Detects cycles and boundaries
- Complete evidence documentation
- High confidence results
- Reproducible analysis

---

## Tools and Scripts Available

### Repository-Specific Tools

1. **`tools/dep_graph_db.py`**
   - Build dependency graph database
   - Query upstream/downstream dependencies
   - Store graph for reuse

2. **`ops_scripts/ci/_ast_process_map_gap_analyzer.py`**
   - AST-based process map analysis
   - Gap detection
   - Boundary validation

### Python AST Module

Direct AST parsing for custom analysis:
```python
import ast
tree = ast.parse(file_content, filename=filepath)
# Extract imports, calls, inheritance, etc.
```

### Graph Construction Options

**Option 1:** Use existing repository tools
```bash
python tools/dep_graph_db.py build --roots file1.py file2.py
python tools/dep_graph_db.py query --downstream file.py
```

**Option 2:** Use AST analysis scripts
```bash
python ops_scripts/ci/_ast_process_map_gap_analyzer.py
```

**Option 3:** Build custom AST graph
```python
# See command_capture_snippets.ps1 for inline AST analysis
```

---

## Training and Adoption

### For Cascade

**Automatic Behavior:**
- Cascade will automatically invoke `ast-first-gate` for code-related requests
- No manual invocation needed
- Gate will block and guide Cascade through graph construction
- Cascade will document DEPENDENCY_GRAPH section automatically

**Checklist Integration:**
- Use `ast_first_checklist.md` before responding to code requests
- Verify all checkboxes before proceeding
- Follow decision tree for graph vs text search

### For Users

**What to Expect:**
- Cascade will build dependency graphs before answering code questions
- Responses will include DEPENDENCY_GRAPH section with graph evidence
- Higher confidence results with AST-backed analysis
- Explicit reporting of parse failures or incomplete graphs

**How to Override:**
- Explicitly request "skip dependency graph" or "use text search only"
- Cascade will warn about constitutional violation and reduced confidence
- User must confirm bypass

---

## Metrics and Success Criteria

### Compliance Metrics

- **Graph-First Rate:** % of code investigations that build graph first
  - Target: 100% (enforced by gate)
- **DEPENDENCY_GRAPH Documentation Rate:** % of evidence files with graph section
  - Target: 100% (enforced by template)
- **Grep Fallback Rate:** % of analyses that use grep as primary method
  - Target: 0% (forbidden by §3.5)
- **Parse Failure Handling Rate:** % of parse failures that fail closed (no silent fallback)
  - Target: 100% (enforced by §3.6)

### Quality Metrics

- **Graph Completeness:** Average % of files successfully parsed
  - Target: >95%
- **Edge Type Coverage:** Average number of edge types extracted per graph
  - Target: All required types (imports, calls, inheritance, registry, tests)
- **Confidence Level:** % of analyses with HIGH confidence
  - Target: >90%

### Evidence Metrics

- **DEPENDENCY_GRAPH Section Presence:** % of evidence files with complete graph section
  - Target: 100%
- **Scope Justification Rate:** % of files in scope with graph justification
  - Target: 100%
- **Test Selection Graph-Backed Rate:** % of test selections justified by graph edges
  - Target: 100%

---

## Rollback Plan

If hardening causes issues:

### Temporary Bypass

Add to `.windsurfrules`:
```
## §0.1 TEMPORARY BYPASS (remove after issue resolved)
DEFAULT = DETAILED AST DEPENDENCY GRAPH is TEMPORARILY DISABLED
Reason: [describe issue]
Duration: [date range]
Fallback: [alternative method]
```

### Skill Deactivation

Rename skill directories to disable:
```bash
mv .windsurf/skills/ast-first-gate .windsurf/skills/ast-first-gate.disabled
```

### Partial Rollback

Keep dependency graph requirements but remove automatic blocking:
- Keep `dependency-graph-analysis` skill
- Disable `ast-first-gate` skill
- Keep DEPENDENCY_GRAPH section in evidence template
- Make graph building recommended but not mandatory

---

## Future Enhancements

### Phase 2: Graph Caching

- Cache built dependency graphs for reuse
- Incremental graph updates for file changes
- Graph invalidation on significant changes

### Phase 3: Graph Visualization

- Generate visual dependency graphs
- Interactive graph exploration
- Cycle and boundary highlighting

### Phase 4: Graph-Based Refactoring

- Use graph to suggest safe refactorings
- Validate refactorings don't break dependencies
- Automated test selection for refactorings

### Phase 5: Graph Quality Metrics

- Track graph completeness over time
- Identify files with poor parseability
- Measure graph construction performance

---

## Conclusion

This hardening establishes **AST dependency graphs as the absolute default** for all code analysis in Cascade. The `ast-first-gate` skill enforces this at the entry point, blocking all code investigation work until a graph is built and documented.

**Key Achievements:**
1. ✅ §0 DEFAULT ANALYSIS MODE established and enforced
2. ✅ Automatic blocking via `ast-first-gate` skill
3. ✅ Comprehensive graph construction protocols
4. ✅ Mandatory DEPENDENCY_GRAPH evidence section
5. ✅ Graph-backed test selection and scope justification
6. ✅ Fail-closed discipline for parse failures
7. ✅ All existing skills updated with graph prerequisites
8. ✅ Complete verification checklists and decision trees

**Constitutional Compliance:**
- §0: DEFAULT = DETAILED AST DEPENDENCY GRAPH ✅ ENFORCED
- §1: Testing with graph-backed test identification ✅ ENFORCED
- §3: Scope with graph-backed justification ✅ ENFORCED
- §3.4-§3.7: Dependency graph requirements ✅ ENFORCED
- §4.4: Graph before edit ✅ ENFORCED
- §5.2: Graph-backed test selection ✅ ENFORCED

**Result:** Cascade now defaults to rigorous, AST-based dependency graph analysis for all code work, with automatic enforcement and comprehensive evidence documentation.

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

## Success Criteria

- [ ] All objectives completed successfully
- [ ] Validation tests pass
- [ ] Documentation updated
- [ ] Stakeholder approval received

---

