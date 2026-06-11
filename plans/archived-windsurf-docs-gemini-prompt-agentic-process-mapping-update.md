---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\gemini-prompt-agentic-process-mapping-update.md'
original_relative_path: 'gemini-prompt-agentic-process-mapping-update.md'
source_sha256: c6ebd42713c2e98dc66bda1588e17cae7200b22c7852b331666182a0f56fec07
recovered_status: LOST_RECOVERED
last_commit: '8730830964b'
last_commit_date: '2026-04-05 17:47:48 -0400'
created_date: '2026-03-05'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Gemini Prompt: Update Agentic Process Mapping Document

**Task:** Update `docs/technical/agentic_process_mapping.md` to reflect the current architectural state of the Agentic-Workflow repository as of March 2026.

**Context:** This is a production-grade sovereign AI architecture with 7 enforced layers (L0-L6), 2,300+ tests, 17 CI gates, and constitutional governance rules. The document is a widescreen ASCII art diagram (353 lines, 150+ character width) showing data flow, layer boundaries, and enforcement mechanisms.

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


## Repository State Analysis

### Layer Structure & File Counts
```
agentic_core/
├── L0_routing/          270 items (routing, legacy allowlist, agent discovery)
├── L1_cognition/         68 items (orchestration, shadow routers)
├── L2_execution/        173 items (UniversalWriteGateway, instruction packets, CID registry)
├── L3_orchestration/     88 items (healing arbitration, change packages)
├── L4_state/             81 items (embedding store, knowledge artifacts)
├── L5_safety/           308 items (100+ guards, SSOT scanner, classification kernel)
├── L6_observability/     75 items (immutable audit ledger, telemetry)
├── base_agents/          10 items (canonical base classes)
├── prompt_governance/    90 items (deterministic assembly, orphan detection)
├── runtime/              55 items
├── interfaces/           26 items
├── knowledge/           224 items
└── mixins/               72 items
```

### Constitutional Rules (.windsurfrules)
8 sections enforcing:
- **§1 Execution Modality:** Phased execution, evidence bundling, no scope drift
- **§2 Evidence Contract:** Two-commit model, ASCII-only, contradiction detection
- **§3 Scope & Determinism:** AST-only analysis, canonical paths, no heuristics
- **§4 Testing:** 2,300+ tests, collection vs execution reconciliation
- **§5 Architecture Locks:** Layer boundaries, SSOT enforcement, tooling/runtime separation
- **§6 CI & Contract Gates:** 17 workflows, unified gate runner
- **§7 Response Discipline:** No narrative, deterministic acceptance criteria
- **§8 Artifact Location:** Version-controlled paths only (docs/reports/plans/)

### Key SSOT Components

#### Classification Kernel (Phase 2b Bulletproof Hardening)
- **Location:** `agentic_core/L5_safety/core_kernel/classification_kernel.py`
- **Design:** Zero dependencies (stdlib only), LRU cache (maxsize=1024), 19-priority queue
- **Exports:**
  - `FileType` — Literal type with 20 values (AGENT, ENGINE, ORCHESTRATOR, etc.)
  - `classify_file_standalone(path) -> FileType` — Full AST classification
  - `is_agent_file(path) -> bool` — Convenience predicate
  - `is_agent_or_orchestrator(path) -> bool` — Extended predicate
  - `clear_classification_cache()` — Cache invalidation
  - `classification_cache_info()` — LRU statistics
  - `classification_cache_context()` — Context manager for batch operations
- **Impact:** Consolidated 10 files, removed 400+ lines of bespoke classification logic
- **Consumers:** FileClassificationAgent, full_agent_discovery, complexity_visitor_util, discovery_util, ssot_scanner, governance tests
- **CI Enforcement:** `.github/workflows/ssot-kernel-guardrail.yml`

#### Agent Registry
- **Location:** `artifacts/discovery/agent_discovery_full.json`
- **Status:** 190 candidates verified, 0 invalid
- **Guardrail:** 0 ERRORS, 2601 files scanned

#### Structure Blueprint
- **Location:** `agentic_core/L5_safety/config/structure_blueprint.py`
- **Role:** Structural SSOT for validator/healer symmetry
- **Contract:** Both validator and healer read identical canonical export surface

---

## Required Updates

### 1. Classification Kernel SSOT (Lines 10, 30)

**Current State:**
```
Line 10: | reasoning/ (38 agents) [SSOT: classification_kernel]     |
Line 30: | [SCOPE] TOOLS STRICTLY SEGMENTED BY ROUTE/ROLE/AGENT     |
```

**Update Required:**
Add detailed subsection after apps_shared box (around line 32):

```
==============================================================================================================================================================================================================================================================================
  CLASSIFICATION KERNEL — SINGLE SOURCE OF TRUTH (SSOT)
==============================================================================================================================================================================================================================================================================
+--------------------------------------------------------------------------------------------------------------------------+
| agentic_core/L5_safety/core_kernel/classification_kernel.py                                                             |
|--------------------------------------------------------------------------------------------------------------------------|
| ZERO DEPENDENCIES: stdlib only (ast, logging, re, contextlib, functools, pathlib, typing)                               |
| DESIGN: LRU cache (maxsize=1024), 19-priority queue, catch-all exception guard                                          |
|--------------------------------------------------------------------------------------------------------------------------|
| EXPORTS:                                                                                                                 |
|   • FileType — Literal[AGENT, ENGINE, ORCHESTRATOR, VALIDATOR, FACTORY, CONFIG, ADAPTER, STRATEGY, ...]  (20 values)   |
|   • classify_file_standalone(path) -> FileType — Full AST classification, @lru_cache via _classify_impl()              |
|   • is_agent_file(path) -> bool — Convenience predicate (inherits cache)                                                |
|   • is_agent_or_orchestrator(path) -> bool — Extended predicate (inherits cache)                                        |
|   • clear_classification_cache() — Cache invalidation for tests                                                         |
|   • classification_cache_info() — LRU cache statistics                                                                  |
|   • classification_cache_context() — Context manager: clears cache on entry + exit for batch operations                 |
|--------------------------------------------------------------------------------------------------------------------------|
| CONSUMERS (10+ files consolidated):                                                                                     |
|   • FileClassificationAgent.py (L5_safety) — full AST classification                                                    |
|   • full_agent_discovery.py (L0_routing) — agent manifest generation (uses cache context)                               |
|   • complexity_visitor_util.py (L0_routing) — dashboard discovery                                                       |
|   • discovery_util.py (runtime) — runtime agent registry                                                                |
|   • file_intent.py (prompt_governance) — prompt intent classification                                                   |
|   • ssot_scanner.py, registry_verification.py (L5 enforcement)                                                          |
|   • tests/guardian/*, tests/integration/* — governance tests                                                            |
|--------------------------------------------------------------------------------------------------------------------------|
| PHASE 2B IMPACT (Bulletproof Hardening):                                                                                |
|   • Shadow liquidation: 7 errors → 0                                                                                    |
|   • Files delegated: generate_agent_table_simple_util, pascal_sovereignty_fixer, mece_test_rebaseline                  |
|   • Files renamed (collision avoidance): analyze_app_files_util → classify_app_domain,                                 |
|     class_info → classify_migration_disposition, agent_disposition_analyzer → _classify_disposition,                   |
|     file_classification → _classify_audit_category                                                                      |
|   • Error hardening: SyntaxError/UnicodeDecodeError/OSError logged with details, catch-all guard prevents batch crash  |
|   • Code removed: 400+ lines of bespoke classification logic eliminated                                                 |
|--------------------------------------------------------------------------------------------------------------------------|
| CI ENFORCEMENT: .github/workflows/ssot-kernel-guardrail.yml — runs guardrail + contract tests on push/PR                |
| AGENT COUNT: 190 candidates, 190 verified, 0 invalid                                                                    |
| GUARDRAIL STATUS: 0 ERRORS, 2601 files scanned                                                                          |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 2. Agent Execution Profile Registry (Lines 135-139)

**Current State:**
```
AGENT EXECUTION PROFILE ENFORCEMENT
- Every agent must be registered in AgentExecutionProfileRegistry
- Profiles: LOW (deterministic only), HIGH (LLM via Gateway only)
- Unregistered agent invocation -> HARD FAIL
- Registry hash included in determinism digest
```

**Update Required:**
Expand with implementation details:

```
AGENT EXECUTION PROFILE ENFORCEMENT
+--------------------------------------------------------------------------------------------------------------------------+
| REGISTRY LOCATION: agentic_core/L0_routing/config/agent_execution_profile_registry.py                                   |
|--------------------------------------------------------------------------------------------------------------------------|
| PROFILES:                                                                                                                |
|   • LOW (AgentExecutionProfile.LOW) — Deterministic only, no LLM calls permitted                                        |
|   • HIGH (AgentExecutionProfile.HIGH) — LLM via SovereignLLMGateway only (no direct SDK calls)                          |
|--------------------------------------------------------------------------------------------------------------------------|
| ENFORCEMENT MECHANISMS:                                                                                                  |
|   1. AST Scanner: Blocks unregistered agent invocation at CI time                                                        |
|   2. Runtime Guard: Raises ToolNotAllowedError on unregistered agent execution                                           |
|   3. Determinism Digest: Registry hash included in W<n>-DETERMINISM-DIGEST artifact                                     |
|   4. Gateway Integration: SovereignLLMGateway validates profile before LLM egress                                        |
|--------------------------------------------------------------------------------------------------------------------------|
| VIOLATION HANDLING:                                                                                                      |
|   • Unregistered agent → HARD FAIL (CI blocks merge)                                                                    |
|   • LOW profile agent calling LLM → SovereigntyError                                                                    |
|   • HIGH profile agent bypassing gateway → AST scanner CRITICAL violation                                               |
|--------------------------------------------------------------------------------------------------------------------------|
| LINKED TO: Sovereign LLM Gateway (lines 101-116), Determinism Proof Standard (lines 268-274)                            |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 3. Prompt Governance Layer (New Section)

**Insert after L6 Observability section (around line 50) or as standalone governance layer:**

```
==============================================================================================================================================================================================================================================================================
  PROMPT GOVERNANCE LAYER (L5 ENFORCEMENT + CI GATES)
==============================================================================================================================================================================================================================================================================
+--------------------------------------------------------------------------------------------------------------------------+
| agentic_core/prompt_governance/ (90 items)                                                                              |
|--------------------------------------------------------------------------------------------------------------------------|
| PHASE 0: Deterministic Assembly Gate                                                                                    |
|   • Location: docs/reports/assessments/prompt-modules/validation/assemble.py                                            |
|   • Validation: docs/reports/assessments/prompt-modules/validation/validate_assembly.py                                 |
|   • CI Workflow: .github/workflows/prompt-governance.yml                                                                |
|   • Canonical Artifact: docs/reports/assessments/Prompt v5.4 State Gap Implementation.md                                |
|   • SHA256: de0a349ba2894f54e2b4ee2fb164b75e75fd28c328d0e019d068f28dca4a18af (immutable)                                |
|--------------------------------------------------------------------------------------------------------------------------|
| PHASE 10/11: No Orphan Prompt Invariant                                                                                 |
|   • Invariant Test: tests/architecture/test_prompt_governance_no_orphans.py                                             |
|   • Enforcement: Every prompt/template file under data/prompt_governance/** MUST be referenced by apps_lic or apps_rg   |
|   • Detection Method: AST-based reference scanning (no regex, per §3)                                                   |
|   • Violation: CI fails if orphan prompts detected                                                                      |
|--------------------------------------------------------------------------------------------------------------------------|
| GOVERNANCE RULES:                                                                                                        |
|   • No orphan prompts: All prompt files must have at least one engine reference                                         |
|   • Deterministic assembly: Prompt composition must be reproducible across runs                                         |
|   • Version control: All prompts tracked in git, no dynamic generation without audit trail                              |
|   • AST enforcement: Reference detection uses AST parsing, not string matching                                          |
|--------------------------------------------------------------------------------------------------------------------------|
| CI INTEGRATION:                                                                                                          |
|   • Workflow: .github/workflows/prompt-governance.yml                                                                   |
|   • Gate: python ops_scripts/ci/check_prompt_orphans.py (hypothetical, verify actual script name)                       |
|   • Failure Mode: CI blocks merge on orphan detection or assembly validation failure                                    |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 4. Evidence Contract & Two-Commit Model (New Section)

**Insert after CONTROL SPINE section (around line 140) or in new GOVERNANCE PROTOCOLS section:**

```
==============================================================================================================================================================================================================================================================================
  EVIDENCE CONTRACT — TWO-COMMIT MODEL (§2 CONSTITUTIONAL RULE)
==============================================================================================================================================================================================================================================================================
+--------------------------------------------------------------------------------------------------------------------------+
| CANONICAL LOCATION: docs/reports/plans/ (version-controlled, NEVER .windsurf/plans/)                                    |
|--------------------------------------------------------------------------------------------------------------------------|
| EVIDENCE FILE STRUCTURE (Canonical Shape):                                                                              |
|   1. # <Phase Title> (H1)                                                                                               |
|   2. ## Scope                                                                                                            |
|   3. ## CODE_COMMIT — exactly one 40-hex hash                                                                           |
|   4. ## EVIDENCE_COMMIT — exactly one 40-hex hash (or PENDING in draft mode)                                            |
|   5. ## FILES_CHANGED_CODE — verbatim `git show --name-only --pretty=format: <CODE_COMMIT>`                             |
|   6. ## FILES_CHANGED_EVIDENCE — verbatim `git show --name-only --pretty=format: <EVIDENCE_COMMIT>`                     |
|   7. ## INSPECTED_FILES — file paths only, no content                                                                   |
|   8. ## <CommandTitle> sections — one per required command: `$ <cmd>`, full stdout, `EXIT CODE: N` only if N≠0         |
|--------------------------------------------------------------------------------------------------------------------------|
| TWO-COMMIT MODEL (Canonical Workflow):                                                                                  |
|   1. Commit code changes → CODE_COMMIT                                                                                  |
|   2. Run evidence runner in draft mode: `--code-commit <CODE_COMMIT>` (no --evidence-commit)                            |
|      • CODE_COMMIT MAY equal HEAD in draft mode                                                                         |
|   3. Commit evidence file → EVIDENCE_COMMIT                                                                             |
|   4. Re-run runner in seal mode: `--code-commit <CODE_COMMIT> --evidence-commit <EVIDENCE_COMMIT>`                      |
|      • In seal mode: CODE_COMMIT MUST NOT equal HEAD                                                                    |
|   5. Commit sealed evidence                                                                                             |
|--------------------------------------------------------------------------------------------------------------------------|
| MANDATORY RULES:                                                                                                         |
|   • All commands: subprocess.run(argv, shell=False, encoding="utf-8", errors="replace")                                 |
|   • FORBIDDEN: argv0 contains 'pwsh' or 'powershell' (Windows PowerShell parsing issues)                                |
|   • pytest invocation: `python -m pytest -q --color=no` (authoritative command)                                         |
|   • ANSI stripping: Strip all ANSI escape sequences before writing to evidence file                                     |
|   • ASCII-only: Byte-scan final evidence file, hard-fail if any byte > 0x7F (no ✅ ❌ 🚨, use OK:/FAIL:/ERROR:)         |
|   • No source embedding: Do NOT embed source file contents (no INSPECTED_FILE_CONTENTS section)                         |
|     Reason: Source code contains EXIT CODE:/ERROR: strings that corrupt contradiction detection                         |
|   • Evidence rebuild: evidence_lines = [] (rebuilt from scratch every run, no append mode)                              |
|--------------------------------------------------------------------------------------------------------------------------|
| CONTRADICTION DETECTION (Hard Fail):                                                                                     |
|   • Definition: Within a single command output fence, both failure marker AND success marker present                    |
|   • Failure markers: EXIT CODE: [1-9], ^FAILED , ERROR: N gate(s) failed                                                |
|   • Success markers: OK:, passed                                                                                         |
|   • Action: Evidence runner hard-fails (sys.exit(1)), do NOT commit evidence containing contradictions                  |
|--------------------------------------------------------------------------------------------------------------------------|
| CODE_COMMIT SELECTION:                                                                                                   |
|   • Identify by content: `git log -n 30 --name-only --pretty=oneline -- <scope_dirs>`                                   |
|   • Pick commit whose file list includes the phase's actual code artifacts                                              |
|   • NEVER use "parent of HEAD" as proxy if it breaks FILES_CHANGED_CODE fidelity                                        |
|--------------------------------------------------------------------------------------------------------------------------|
| PHASE COMPLETION CRITERIA:                                                                                               |
|   • pytest exits 0 (full suite per pytest.ini testpaths)                                                                |
|   • git status clean (no uncommitted changes)                                                                           |
|   • Evidence file committed with valid CODE_COMMIT and EVIDENCE_COMMIT hashes                                           |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 5. CI Contract Gates (Lines scattered, consolidate)

**Replace/consolidate scattered CI references with unified section:**

```
==============================================================================================================================================================================================================================================================================
  CI & CONTRACT GATES — UNIFIED ENFORCEMENT (§6 CONSTITUTIONAL RULE)
==============================================================================================================================================================================================================================================================================
+--------------------------------------------------------------------------------------------------------------------------+
| SINGLE ENTRYPOINT: ops_scripts/ci/run_contract_gates.py                                                                 |
|--------------------------------------------------------------------------------------------------------------------------|
| GATE EXECUTION SEQUENCE (Ordered, Immutable):                                                                           |
|   1. python -m pytest -q --color=no                          # Full test suite (2,300+ tests)                           |
|   2. python ops_scripts/ci/check_evidence_contract_v2.py --paths docs/reports/plans  # Evidence validation              |
|   3. python ops_scripts/ci/check_tooling_apps_boundary.py   # AST-based boundary enforcement                            |
|--------------------------------------------------------------------------------------------------------------------------|
| 17 GITHUB WORKFLOWS:                                                                                                     |
|   • ssot-kernel-guardrail.yml — Classification kernel SSOT compliance                                                   |
|   • agent-sprawl-check.yml — Prevents duplicate agent creation                                                          |
|   • guardian-tests.yml — Runs constitutional/sovereignty/ssot marker tests                                              |
|   • dashboard-freshness.yml — Validates observability dashboard data                                                    |
|   • prompt-governance.yml — Orphan prompt detection + assembly validation                                               |
|   • [12 additional workflows for layer boundaries, import cycles, determinism, etc.]                                    |
|--------------------------------------------------------------------------------------------------------------------------|
| CI INVARIANTS:                                                                                                           |
|   • CI MUST FAIL on any condition requiring repair (no auto-fixes)                                                      |
|   • CI MUST NOT mutate baselines (maintenance flags forbidden: --update-phantom-baseline, --init-phantom-baseline)      |
|   • CI must assert zero working tree mutations post-run                                                                 |
|   • CI must verify no new files outside allowlisted roots                                                               |
|   • Local execution MUST be identical to CI execution (same commands, same order)                                       |
|--------------------------------------------------------------------------------------------------------------------------|
| PRE-COMMIT BYPASS POLICY:                                                                                                |
|   • --no-verify FORBIDDEN except:                                                                                       |
|     1. Change set is ONLY governance/config files (.windsurfrules, .gitattributes, .editorconfig, .gitignore)           |
|     2. Pre-commit fails on repo-wide unrelated violations not touched by the change                                     |
|     3. Failing hook output captured verbatim in evidence                                                                |
|     4. Follow-on remediation issue opened and recorded in evidence                                                      |
|--------------------------------------------------------------------------------------------------------------------------|
| CITATION REQUIREMENT:                                                                                                    |
|   • "Guaranteed in CI" requires citation of CI workflow file and job name                                               |
|   • Example: "Enforced by .github/workflows/ssot-kernel-guardrail.yml, job: verify-ssot-compliance"                     |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 6. Tooling/Runtime Boundary (Line 30, expand)

**Current State:**
```
Line 30: | [SCOPE] TOOLS STRICTLY SEGMENTED BY ROUTE/ROLE/AGENT     |
```

**Update Required:**
Replace with detailed enforcement section:

```
+--------------------------------------------------------------------------------------------------------------------------+
| TOOLING/RUNTIME BOUNDARY — AST-ENFORCED SEPARATION (§5 CONSTITUTIONAL RULE)                                             |
|--------------------------------------------------------------------------------------------------------------------------|
| FORBIDDEN IMPORTS:                                                                                                       |
|   • tools/evidence/ MUST NOT `import apps_*` or `from apps_* import`                                                    |
|   • ops_scripts/ci/ MUST NOT `import apps_*` or `from apps_* import`                                                    |
|   • ops_scripts/hooks/ MUST NOT `import apps_*` or `from apps_* import`                                                 |
|--------------------------------------------------------------------------------------------------------------------------|
| PERMITTED REFERENCES:                                                                                                    |
|   • apps_* may only appear as string paths (e.g., in INSPECTED_FILES lists)                                             |
|   • Example: inspected_files = ["apps_lic/engines/control_plane.py"]  # OK (string literal)                             |
|   • Example: from apps_lic.engines import control_plane  # FORBIDDEN (import statement)                                 |
|--------------------------------------------------------------------------------------------------------------------------|
| ENFORCEMENT:                                                                                                             |
|   • Script: ops_scripts/ci/check_tooling_apps_boundary.py (AST-based, no regex)                                         |
|   • CI Workflow: Part of unified contract gate runner                                                                   |
|   • Detection: Parses all .py files in tooling directories, scans AST for Import/ImportFrom nodes                       |
|   • Violation: HARD FAIL, CI blocks merge                                                                               |
|--------------------------------------------------------------------------------------------------------------------------|
| RATIONALE:                                                                                                               |
|   • Tooling must remain domain-agnostic (no coupling to apps_lic or apps_rg business logic)                             |
|   • Evidence generation must work across all domains without runtime dependencies                                       |
|   • Prevents circular dependencies between infrastructure and application layers                                        |
|--------------------------------------------------------------------------------------------------------------------------|
| SCAN_ROOTS:                                                                                                              |
|   • Explicit and hard-coded (no silent expansion, no heuristic scanning per §3)                                         |
|   • Example: SCAN_ROOTS = ["tools/evidence", "ops_scripts/ci", "ops_scripts/hooks"]                                     |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 7. Test Suite Integrity (New Section)

**Insert after CI Gates section or as part of L6 Observability:**

```
==============================================================================================================================================================================================================================================================================
  TEST SUITE INTEGRITY — AUTHORITATIVE SUITE (§4 CONSTITUTIONAL RULE)
==============================================================================================================================================================================================================================================================================
+--------------------------------------------------------------------------------------------------------------------------+
| SUITE METRICS:                                                                                                           |
|   • Total Tests: 2,300+ (unit, integration, governance, architecture, sovereignty)                                      |
|   • Registered Markers: 25 types (constitutional, ssot, sovereignty, negative_control, determinism, guardian, etc.)     |
|   • Test Paths: Defined in pytest.ini testpaths (changes require same-commit update to test_testpaths_contract.py)      |
|--------------------------------------------------------------------------------------------------------------------------|
| AUTHORITATIVE COMMAND:                                                                                                   |
|   • `python -m pytest -q --color=no` (full suite per pytest.ini testpaths)                                              |
|   • FORBIDDEN: Narrowing pytest scope to hide failures, running subset while claiming full suite passes                 |
|--------------------------------------------------------------------------------------------------------------------------|
| COLLECTION VS EXECUTION RECONCILIATION:                                                                                  |
|   • Check: `pytest --collect-only -q` vs actual execution count                                                         |
|   • If counts differ: Audit conftest.py pytest_collection_modifyitems hooks (can silently deselect tests)               |
|   • Evidence MUST show "collected X / executed Y" counts                                                                |
|   • Any deselection must be explained in evidence file                                                                  |
|--------------------------------------------------------------------------------------------------------------------------|
| MARKER REGISTRATION:                                                                                                     |
|   • All test markers MUST be registered in pytest.ini [markers] section                                                 |
|   • New test files MUST use existing marker taxonomy (no ad-hoc markers)                                                |
|   • Unregistered marker → pytest warning → CI failure                                                                   |
|--------------------------------------------------------------------------------------------------------------------------|
| PHASE COMPLETION CRITERIA:                                                                                               |
|   • pytest exits 0 (zero failures, zero errors)                                                                         |
|   • git status clean (no uncommitted test files or artifacts)                                                           |
|   • Evidence file committed showing full suite execution                                                                |
|--------------------------------------------------------------------------------------------------------------------------|
| INTEGRITY TESTS:                                                                                                         |
|   • tests/unit_min_deps/test_testpaths_contract.py — Validates pytest.ini testpaths consistency                         |
|   • tests/architecture/test_no_legacy_shells.py — Prevents shell script proliferation                                   |
|   • tests/ci/test_sovereignty_attack_suite.py — Validates sovereignty enforcement                                       |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 8. Scope Decontamination Protocol (New Section)

**Insert in L3 Orchestration or L5 Safety section:**

```
+--------------------------------------------------------------------------------------------------------------------------+
| SCOPE DECONTAMINATION PROTOCOL (§3 CONSTITUTIONAL RULE)                                                                  |
|--------------------------------------------------------------------------------------------------------------------------|
| PRE-EDIT SCOPE DECLARATION:                                                                                              |
|   • Record: `git diff --name-only` (baseline state)                                                                     |
|   • Declare: Planned file count N (exact number of files to be modified)                                                |
|   • Verify: All paths normalized by one canonical function (forward slashes, no .., no absolute, no leading /)          |
|--------------------------------------------------------------------------------------------------------------------------|
| SCOPE VIOLATION DETECTION:                                                                                               |
|   • Trigger: Actual modified files > N (declared count)                                                                 |
|   • Action: STOP immediately, do not partially apply changes                                                            |
|   • Evidence: Document unexpected files in evidence file                                                                |
|--------------------------------------------------------------------------------------------------------------------------|
| DECONTAMINATION SEQUENCE (If Unrelated Files Appear):                                                                    |
|   1. Document unexpected files in evidence with full paths                                                              |
|   2. `git reset --hard <baseline>` (return to clean state)                                                              |
|   3. `git checkout <target> -- <declared_files>` (restore only declared files)                                          |
|   4. Verify with `git diff --name-only` (must match declared scope exactly)                                             |
|   5. If verification fails: HARD FAIL, phase is BLOCKED                                                                 |
|--------------------------------------------------------------------------------------------------------------------------|
| CANONICAL PATH NORMALIZATION (§3 Lock):                                                                                  |
|   • Single canonical function for all path operations                                                                   |
|   • Forward slashes only (no backslashes, even on Windows)                                                              |
|   • No .. segments, no absolute paths in baselines, no leading / or . segments                                          |
|   • Non-canonical path in baseline JSON → HARD FAIL                                                                     |
|--------------------------------------------------------------------------------------------------------------------------|
| DETERMINISM REQUIREMENTS:                                                                                                |
|   • No randomness in file selection or ordering                                                                         |
|   • No time-based behavior (wall-clock forbidden, SemanticClock only)                                                   |
|   • Deterministic inputs → deterministic outputs (same scope declaration → same file set)                               |
|--------------------------------------------------------------------------------------------------------------------------|
| HEURISTIC PROHIBITION:                                                                                                   |
|   • SCAN_ROOTS explicit and hard-coded (no silent expansion)                                                            |
|   • No heuristic scanning (no "find all Python files" without explicit root list)                                       |
|   • All code analysis MUST use AST parsing (regex/grep for structural logic FORBIDDEN per §3)                           |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 9. Base Agents Canonical Location (Add to SSOT section)

**Insert near Classification Kernel section:**

```
+--------------------------------------------------------------------------------------------------------------------------+
| BASE AGENTS CANONICAL LOCATION (§5 SSOT RULE)                                                                            |
|--------------------------------------------------------------------------------------------------------------------------|
| LOCATION: agentic_core/base_agents/ (10 items)                                                                           |
|--------------------------------------------------------------------------------------------------------------------------|
| NAMING CONVENTION:                                                                                                       |
|   • All base agents MUST use suffix: *Base.py or *BaseAgent.py                                                          |
|   • Example: AgentBase.py, OrchestratorBase.py, ValidatorBaseAgent.py                                                   |
|--------------------------------------------------------------------------------------------------------------------------|
| SSOT INVARIANT:                                                                                                          |
|   • No duplicate agents: 1 file ↔ 1 canonical class                                                                     |
|   • AST-scan for semantic duplicates before creating new utilities                                                      |
|   • Duplicate detection enforced by: ops_scripts/ci/check_agent_duplicates.py (hypothetical, verify actual script)      |
|--------------------------------------------------------------------------------------------------------------------------|
| AGENT DISCOVERY:                                                                                                         |
|   • Registry: artifacts/discovery/agent_discovery_full.json                                                             |
|   • Status: 190 candidates verified, 0 invalid                                                                          |
|   • Discovery Script: agentic_core/L0_routing/scripts/full_agent_discovery.py                                           |
|   • Uses: classification_cache_context() for batch classification efficiency                                            |
|--------------------------------------------------------------------------------------------------------------------------|
| ENFORCEMENT:                                                                                                             |
|   • CI Workflow: .github/workflows/agent-sprawl-check.yml                                                               |
|   • Violation: Creating base agent outside base_agents/ → CI blocks merge                                               |
|   • Duplicate agent creation → HARD FAIL                                                                                |
+--------------------------------------------------------------------------------------------------------------------------+
```

### 10. Layer Counts Update (Lines 33-42)

**Current State:**
```
┌────────────────────────────────────────────────────────────────────┐
│  L0  Routing       — Sovereign entry point, allowlist-gated        │
│  L1  Cognition     — Deterministic orchestration & LLM arbitration │
│  L2  Execution     — Universal Write Gateway (all mutations here)  │
│  L3  Orchestration — Healing loops, arbitration, change packages   │
│  L4  State         — Indexed knowledge artifacts, embedding store  │
│  L5  Safety        — 100+ enforcement guards, human review queue   │
│  L6  Observability — Immutable audit ledger, mutation records      │
└────────────────────────────────────────────────────────────────────┘
```

**Update Required:**
```
┌────────────────────────────────────────────────────────────────────┐
│  L0  Routing       — 270 items: routing, legacy allowlist, agent  │
│                      discovery, complexity analysis                │
│  L1  Cognition     — 68 items: orchestration, shadow routers,     │
│                      LLM arbitration                               │
│  L2  Execution     — 173 items: UniversalWriteGateway, instruction│
│                      packets, CID registry, determinism            │
│  L3  Orchestration — 88 items: healing arbitration, change        │
│                      packages, confidence routing                  │
│  L4  State         — 81 items: embedding store, knowledge          │
│                      artifacts, RAG indices                        │
│  L5  Safety        — 308 items: 100+ guards, SSOT scanner,        │
│                      classification kernel, sovereignty fence      │
│  L6  Observability — 75 items: immutable audit ledger, telemetry, │
│                      mutation records                              │
└────────────────────────────────────────────────────────────────────┘
```

---

## Formatting & Style Requirements

### ASCII Art Preservation
- **Maintain widescreen layout:** 150+ character width (document is optimized for widescreen terminals)
- **Preserve box-drawing characters:** Use `+`, `-`, `|` for boxes; `=` for section separators
- **Consistent indentation:** 3 spaces for hierarchy levels within boxes
- **Column alignment:** Align `|` characters vertically for clean box edges

### Typography
- **Section headers:** ALL CAPS with `=` separator lines (80+ characters)
- **Subsection headers:** Title Case with box borders
- **File paths:** Backticks for inline code: `agentic_core/L5_safety/core_kernel/classification_kernel.py`
- **Counts:** Show in parentheses: (190 agents), (2,300+ tests), (17 workflows)
- **Constitutional references:** Use §N notation: (§2 Evidence Contract), (§5 SSOT)

### ASCII-Only Enforcement (§2 Rule)
- **FORBIDDEN:** Any Unicode > 0x7F (no ✅ ❌ 🚨 ⚠️ 🔒 📊)
- **REQUIRED:** ASCII equivalents: OK:, FAIL:, ERROR:, WARNING:, LOCKED:, METRICS:
- **Validation:** Byte-scan final document, hard-fail if any byte > 0x7F

### Citation Format
- **File paths:** Always use forward slashes (canonical normalization per §3)
- **Line references:** "Lines 10-32", "around line 140"
- **Workflow citations:** Full path: `.github/workflows/ssot-kernel-guardrail.yml`
- **Script citations:** Full path from repo root: `ops_scripts/ci/check_tooling_apps_boundary.py`

---

## Validation Checklist

After completing the update, verify:

### Constitutional Compliance
- [ ] All 8 constitutional sections (§1-§8) referenced with proper §N notation
- [ ] No Unicode characters > 0x7F (ASCII-only per §2)
- [ ] No truncation (...) in critical sections (per §7 Response Discipline)
- [ ] All file paths use forward slashes (canonical normalization per §3)

### Content Completeness
- [ ] Classification kernel SSOT documented with file path, exports, consumers, CI enforcement
- [ ] Agent execution profile registry location specified with enforcement mechanisms
- [ ] Prompt governance layer added with Phase 0 and Phase 10/11 details
- [ ] Evidence contract two-commit model explained with canonical workflow
- [ ] CI gate sequence documented with all 17 workflows listed
- [ ] Tooling/runtime boundary AST enforcement detailed
- [ ] Test suite integrity metrics included (2,300+ tests, 25 markers)
- [ ] Scope decontamination protocol detailed with 4-step sequence
- [ ] Layer counts updated with actual file counts (270, 68, 173, 88, 81, 308, 75)
- [ ] Base agents canonical location specified (agentic_core/base_agents/, 10 items)

### Technical Accuracy
- [ ] All file paths verified against actual repository structure
- [ ] All counts verified (agent count: 190, test count: 2,300+, workflow count: 17)
- [ ] All script names verified (check_tooling_apps_boundary.py, check_evidence_contract_v2.py, etc.)
- [ ] All constitutional rule numbers verified (§1-§8)
- [ ] All layer numbers verified (L0-L6)

### Formatting Consistency
- [ ] Box-drawing characters aligned vertically
- [ ] Section separators use `=` characters (80+ width)
- [ ] Indentation consistent (3 spaces per level)
- [ ] Line width does not exceed 150 characters (widescreen optimization)
- [ ] All boxes properly closed (matching `+` corners)

---

## Output Format

Provide the updated document as:

1. **Complete markdown file** (all 353+ lines with updates integrated)
2. **Diff summary** showing:
   - Sections added (with line number ranges)
   - Sections modified (with before/after snippets)
   - Sections deleted (if any)
3. **Verification notes** confirming:
   - ASCII-only compliance (byte-scan results)
   - Constitutional rule coverage (§1-§8 checklist)
   - Technical accuracy (file path verification)
4. **No narrative padding** (per §7 Response Discipline)

---

## Critical Constraints

### What NOT to Do
- **Do NOT add Unicode emojis** (✅ ❌ 🚨) — Use ASCII equivalents (OK:, FAIL:, ERROR:)
- **Do NOT truncate with ...** — Show full content or explicitly mark continuation
- **Do NOT use relative paths** — Always use full paths from repo root
- **Do NOT add narrative fluff** — No "Let me...", "I will...", "Great idea" (per §7)
- **Do NOT invent file names** — Verify all script/workflow names against actual repo
- **Do NOT use regex for code analysis** — AST-only per §3
- **Do NOT modify core data contracts** (lines 296-320) — These are immutable

### What TO Do
- **DO preserve existing ASCII art structure** — Maintain box-drawing alignment
- **DO use forward slashes in all paths** — Even on Windows (canonical normalization)
- **DO cite constitutional rules** — Use §N notation for all rule references
- **DO show exact counts** — (190 agents), (2,300+ tests), not "many" or "numerous"
- **DO verify file paths** — Check against actual repository structure
- **DO maintain widescreen layout** — 150+ character width for readability
- **DO use AST-based analysis** — No regex/grep for structural logic

---

## Example Integration Pattern

Here's how to integrate a new section (Classification Kernel SSOT):

**Before (Line 10):**
```
| reasoning/ (38 agents) [SSOT: classification_kernel]     |
```

**After (Lines 10-45, expanded):**
```
| reasoning/ (38 agents)                                   |
+----------------------------------------------------------+

==============================================================================
  CLASSIFICATION KERNEL — SINGLE SOURCE OF TRUTH (SSOT)
==============================================================================
+----------------------------------------------------------+
| agentic_core/L5_safety/core_kernel/classification_kernel.py
|----------------------------------------------------------
| ZERO DEPENDENCIES: stdlib only
| DESIGN: LRU cache (maxsize=1024), 19-priority queue
| EXPORTS: FileType, classify_file_standalone(), ...
| CONSUMERS: 10+ files consolidated
| CI ENFORCEMENT: .github/workflows/ssot-kernel-guardrail.yml
| AGENT COUNT: 190 verified, 0 invalid
+----------------------------------------------------------+
```

This pattern:
- Preserves existing content (line 10)
- Adds detailed subsection with box borders
- Maintains ASCII-only characters
- Shows exact counts (190 verified)
- Cites CI enforcement workflow
- Uses forward slashes in file paths

---

## Success Criteria

The update is complete when:

1. **All 10 required updates** integrated into document
2. **ASCII-only validation** passes (no bytes > 0x7F)
3. **Constitutional coverage** complete (all §1-§8 referenced)
4. **Technical accuracy** verified (all file paths exist, all counts correct)
5. **Formatting consistency** maintained (box alignment, indentation, line width)
6. **No narrative padding** (direct, factual content only per §7)
7. **Diff summary** provided showing all changes with line numbers
8. **Verification notes** confirming compliance with all constraints

---

**END OF PROMPT**

This prompt is optimized for Gemini 2.0 Flash Thinking Experimental with:
- Explicit structural requirements (ASCII art, box-drawing)
- Constitutional rule integration (§1-§8 citations)
- Technical accuracy constraints (file path verification)
- Formatting discipline (ASCII-only, no truncation)
- Validation checklist (30+ verification points)
- Example integration patterns (before/after snippets)

## Rules

1. Follow all constitutional rules and guidelines
2. Maintain compliance with established standards
3. Document all changes and decisions
4. Validate all implementations before completion

---

