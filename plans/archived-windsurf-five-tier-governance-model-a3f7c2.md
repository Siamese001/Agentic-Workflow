---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\five-tier-governance-model-a3f7c2.md'
original_relative_path: 'five-tier-governance-model-a3f7c2.md'
source_sha256: 07fdfd3ee3f4fcac65904f1a94e5663dc78885f2895777ee2355b2c7d6d8367b
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-07'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Five-Tier Governance Model — Clean Separation of Concerns

Three concerns, cleanly separated:
1. **ADG** = Structural truth engine (topology, blast radius, seams, impact)
2. **Refactor Accelerator** = Change planner (consumes ADG, ranks refactors, orders migrations)
3. **Governance** = Decision authority (allow/deny/require-approval, promotion, policy)

**Companion artifact**: `.windsurf/plans/governance-enforcement-table.md` — enforcement inventory across all 5 tiers.
**Descoped items**: `.windsurf/plans/descoped-items-tracker.md` — items removed from this plan but not lost.

---

## Wave Structure

| Wave | Phases | Focus | Checkpoint | Est. Tokens | Status |
|------|--------|-------|------------|-------------|--------|
| Wave 0 | 0.1 | MCP Green Light prerequisite | Z: constitutional §13 MCP health check | ~2K | ✅ DONE |
| Wave 1 | 1.1–1.8 | Cascade Hooks: 3 hard gates + 1 advisory classifier + 4 advisory post-hooks | A: hooks block pwsh, anti-patterns; classifier tags tier; audit hooks log; response-tail cleanup | ~16K | 🟢 READY |
| Wave 2 | 2.1–2.10 | Policy layer cleanup + MCP simplification + Author-Gate calibration + plan format | B: all rules loading, MCP simplified, Author-Gate calibrated, plan template updated | ~15K | 🟢 READY |
| **Wave 2.5** | **M.1–M.7** | **ADG Generator Modularization** (3,305-line monolith → 7 subpackages) | **B2: `generate_full_adg.py` → package, tests green, pre-commit green** | **~18K** | **✅ DONE** |
| Wave 3 | 3.1–3.7 | ADG structural truth + Refactor Accelerator + syntax/guardian hardening | C: ADG scoped to structure, RA created, syntax gate, guardian idempotent | ~16K | 🟡 DEPENDS ON W2.5 |
| Wave 4 | 4.1–4.6 | Local quality ratchet + CI promotion authority + verification | D: fast pre-commit, explicit promotion criteria, full pipeline green | ~10K | 🟢 READY |
| **Wave 5** | **5.1–5.14** | **Post-plan tech debt cleanup: archive ~800 superseded scripts, rewire RepairOrchestrator, fix paths, consolidate tools/** | **E: zero dangling refs, tools/ from ~1,200→~200 items, pre-commit clean** | **~18K** | **🟡 AFTER W4** |

**Total: ~95K tokens across 7 waves (Wave 0, 1, 2, 2.5, 3, 4, 5)**

Token estimator UNRESOLVED — `token_budget_loader.py` has path bug (uses parent of repo root). Estimates are manual.

---

## Phase-Level Summary (all waves)

| Wave | Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|------|-------|-------|-------|-------------|-------------|--------|
| W0 | 0.1 | MCP Green Light | Add §13 MCP green-light prerequisite to constitutional floor | PP-1 | ~2K | ✅ DONE |
| W1 | 1.1 | Pre-Run Gate (HARD) | Block PowerShell, dangerous commands, PID tracking | PP-4, PP-9 | ~2K | 🟢 |
| W1 | 1.2 | Pre-Write Gate (HARD) | Block anti-patterns, syntax errors (edit reconstruction), MCP config tiered | PP-3, PP-13 | ~3K | 🟢 |
| W1 | 1.3 | Pre-MCP Gate (HARD) | ADG-first enforcement, SQLite lock check, health prerequisite | PP-1, PP-10 | ~2K | 🟢 |
| W1 | 1.4 | Pre-Prompt Classifier (ADVISORY) | Tier classification + context seeding, never blocks | — | ~2K | 🟢 |
| W1 | 1.5 | Post-Write Audit (ADVISORY) | MCP JSON-native lint (schema, env vars, tool count), write telemetry | PP-2 | ~1K | 🟢 |
| W1 | 1.6 | Post-Run Audit (ADVISORY) | Command tracking, best-effort PID registry (no native PID in payload) | PP-9 | ~1K | 🟢 |
| W1 | 1.7 | Post-MCP Audit (ADVISORY) | MCP tool usage telemetry, response time tracking | PP-1 | ~1K | 🟢 |
| W1 | 1.8 | Post-Cascade Cleanup (ADVISORY) | Response-tail cleanup attempt (best-effort, per-response not per-session) | PP-9, PP-10 | ~2K | 🟢 |
| W2 | 2.1 | Fix Rules (Policy) | Fix 5 broken rule triggers, delete 2 duplicates | PP-8 | ~1K | 🟢 |
| W2 | 2.2 | Policy Cleanup | Archive workflow-as-governance, populate global_rules.md | PP-8 | ~1K | 🟢 |
| W2 | 2.3 | Constitutional §13/§14 | Add MCP green light + timeout discipline to constitutional | PP-5 | ~1K | 🟢 |
| W2 | 2.4 | MCP Registry SSOT | Create MCP registry with rationale/scope/overlaps | PP-11 | ~2K | 🟢 |
| W2 | 2.5 | MCP Config Version Check | Lightweight version/deprecation check (research ✅) | PP-12 | ~1K | 🟢 |
| W2 | 2.6 | Exception Vocabulary | Column 5 Precise Exceptions in constitutional §8 | PP-14 | ~1K | 🟢 |
| W2 | 2.7 | MCP Config Simplification | Archive YAML layer, collapse to native JSON (research ✅) | PP-15 | ~2K | 🟢 |
| W2 | 2.8 | Author-Gate SVP Calibration | Ground ⭐ recommendations in measurable target state | PP-16 | ~2K | 🟢 |
| W2 | 2.9 | Plan Format Enforcement | Mandate phase-level summary table at top of all plans | PP-18 | ~1K | 🟢 |
| W2 | 2.10 | Approval & Exception Policy | Define allow/deny/require-approval classes, escalation paths, risk classes | — | ~2K | 🟢 |
| **W2.5** | **M.1** | **Extract utils/** | Move 6 utility functions (file_utils, digest_utils) to subpackage | PP-19 | ~2K | ✅ DONE |
| **W2.5** | **M.2** | **Extract archiving/** | Move 6 archive/zip functions to subpackage | PP-19 | ~2K | ✅ DONE |
| **W2.5** | **M.3** | **Extract validation/** | Move 6 validation/gate functions + rewrite 22 test imports | PP-19 | ~3K | ✅ DONE |
| **W2.5** | **M.4** | **Extract reporting/** | Move defect table (389 lines) + reports (622 lines) to subpackage | PP-19 | ~3K | ✅ DONE |
| **W2.5** | **M.5** | **Extract integration/** | Move 5 integration functions (redis, git, memory, mcp, repair) | PP-19 | ~2K | ✅ DONE |
| **W2.5** | **M.6** | **Extract core/ + main.py** | Move orchestrator + CLI + config to core package, slim monolith to shim | PP-19 | ~3K | ✅ DONE |
| **W2.5** | **M.7** | **Modularization Verification** | Full E2E: generate ADG, tests green, pre-commit green, no import breakage | PP-19 | ~3K | ✅ DONE |
| W3 | 3.1 | ADG Scope Clarification | Explicit in-scope / out-of-scope boundary for ADG | — | ~1K | ✅ DONE |
| W3 | 3.2 | ADG Structural Outputs | Burndown table, blast radius, seam detection, centrality | PP-17 | ~3K | ✅ DONE |
| W3 | 3.3 | Refactor Accelerator Design | RA spec: inputs (ADG + git + lint + test), outputs (ranked candidates, safe cuts) | — | ~3K | ✅ DONE |
| W3 | 3.4 | Refactor Accelerator MVP | RA produces ranked refactor list, impacted tests, migration order | — | ~3K | ✅ DONE |
| W3 | 3.5 | Write-time Syntax Gate | AST parse in pre_write_gate blocks syntax errors | PP-13 | ~2K | ✅ DONE (pre-existing, 25 tests) |
| W3 | 3.6 | Guardian Idempotency | Harden antipattern fixer, block duplicate guardians | PP-14 | ~2K | ✅ DONE |
| W3 | 3.7 | Guardian Quality Scanner | ADG flags weak justifications, P1 ratchet | PP-14 | ~1K | ✅ DONE |
| W4 | 4.1 | Pre-commit Slim-down | Fast local quality ratchet — evidence checks + syntax + format only | — | ~2K | ✅ DONE |
| W4 | 4.2 | Dead Script Archival | Archive 77 dead scripts from ops_scripts/ci/ | GAP-13 | ~2K | ✅ DONE |
| W4 | 4.3 | Wire Missing Gates | Connect 5 existing-but-unwired enforcement scripts | GAP-7,9,10,11,12 | ~2K | ✅ DONE |
| W4 | 4.4 | Eliminate cmd /c | Replaced 13 Windows shell wrappers with py + env: [PYTHONPATH=.] | GAP-14 | ~1K | ✅ DONE |
| W4 | 4.5 | CI Promotion Authority | Explicit promotion criteria, high-risk review path, approval classes | — | ~3K | ✅ DONE |
| W4 | 4.6 | End-to-End Verification | Measurable verification across all 5 tiers | — | ~1K | ✅ DONE |
| **W5** | **5.1** | **Archive ADG Severity Hooks** | Removed 5 commented-out superseded ADG hook blocks (-82 lines) | GAP-6 | ~1K | ✅ DONE |
| **W5** | **5.2** | **Archive MCP YAML Infrastructure** | Archived sync_yaml_to_global.py, validate_mcp_yaml.py, check_mcp_npx_windows.py | PP-15 | ~1K | ✅ DONE |
| **W5** | **5.3** | **Archive Orphan Hook Scripts** | Archived 18 unreferenced scripts + baselines from ops_scripts/hooks/ | GAP-13 | ~1K | ✅ DONE |
| **W5** | **5.4** | **Archive One-Shot MCP Scripts** | Archived 12 one-shot scripts from tools/mcp/ — retained 4 active MCP servers | PP-15 | ~1K | ✅ DONE |
| **W5** | **5.5** | **Rewire RepairOrchestrator** | Pre-existing: _run_p1_p2_auto_fix already wired in generate_full_adg.py line 346 | PP-17 | ~3K | ✅ DONE (pre-existing) |
| **W5** | **5.6** | **Archive Deprecated Windsurf Workflows** | Archived mcp-config-sync.md, preprocess-rules.md, adg-accelerator-optimization.md | GAP-6 | ~1K | ✅ DONE |
| **W5** | **5.7** | **Archive Deprecated CI Workflows** | Archived 29 of 36 GitHub workflows — retained 7 active | GAP-6 | ~1K | ✅ DONE |
| **W5** | **5.8** | **Clean Pre-Commit Config** | Removed stale T10.5/T11.2/T20 refs; updated manual lane list | GAP-14 | ~1K | ✅ DONE |
| **W5** | **5.9** | **Dangling Reference Sweep** | Fixed .windsurfrules MCP SSOT section; archived broken plan-validation-ci.yml | — | ~1K | ✅ DONE |
| **W5** | **5.10** | **Archive ADG Root One-Shot Scripts** | Archived 172 one-shot scripts from tools/adg/ root — retained 9 active | GAP-13 | ~2K | ✅ DONE |
| **W5** | **5.11** | **Archive ADG MCP Duplicates + Stubs** | Archived 5 unreferenced subdirs (accelerators, archives, report_parsers, services, shared_modules) | — | ~1K | ✅ DONE |
| **W5** | **5.12** | **Archive tools/ One-Shot Graveyard** | Archived 23 one-shot dirs (~680 files) — retained tools/otel/ active MCP server | GAP-13 | ~2K | ✅ DONE |
| **W5** | **5.13** | **Fix Hardcoded Paths** | Verified clean — no runtime hardcoded paths in active tools/adg/ code | PP-14 | ~1K | ✅ DONE (clean) |
| **W5** | **5.14** | **tools/ Consolidation + Expanded Verification** | 16/18 checks pass; 2 FAILs are false positives (terms only in doc comments) | — | ~1K | ✅ DONE |

---

## Priority Map (User Pain Points → Gates)

**Key distinction**: Pre-hooks (`pre_*`) = **hard gates** that can BLOCK actions. Post-hooks (`post_*`) = **advisory/audit/cleanup** only.

| ID | Pain Point | Severity | Gate Tier | Hook Type | Hook Event | Wave |
|----|-----------|----------|-----------|-----------|------------|------|
| PP-1 | MCP servers silently failing | **P0** | T1 (advisory) + T2 (policy) | Post | `post_mcp_tool_use` telemetry + `post_cascade_response` health summary | W1 |
| PP-2 | MCP config integrity | **P0** | T1 (advisory) | Post | `post_write_code` JSON-native lint (schema, env vars, tool count) | W1 |
| PP-3 | Silent swallowers / antipatterns | **P0** | T1 (hard) + T3 (structural) | Pre | `pre_write_code` pattern scan | W1 |
| PP-4 | PowerShell causes hangs | **P1** | T1 (hard) | Pre | `pre_run_command` blocks pwsh | W1 |
| PP-5 | Timeouts not implemented | **P1** | T2 (policy) | — | `always_on` rule | W2 |
| PP-6 | Plans missing waves | **P1** | T2 (policy) | — | Plan template + rule enforcement (Phase 2.9). Classifier warns (Phase 1.4). | W2 |
| PP-7 | ADG not used as primary tool | **P2** | T2 (policy) | — | `always_on` rule | W2 |
| PP-8 | Rules using invalid triggers | **P2** | T2 (policy) | — | Fix frontmatter triggers | W2 |
| PP-9 | Zombie processes accumulate | **P0** | T1 (advisory) | Post | `post_run_command` PID registry + `post_cascade_response` cleanup | W1 |
| PP-10 | ADG SQLite lock contention | **P0** | T1 (hard + advisory) | Pre+Post | `pre_mcp_tool_use` lock check + `post_cascade_response` lock release | W1 |
| PP-11 | No MCP registry | **P1** | T2 (policy) | — | MCP registry doc | W2 |
| PP-12 | MCP configs not validated | **P1** | T2 (policy) | — | Lightweight version check (research ✅) | W2 |
| PP-13 | Syntax errors in codebase | **P0** | T1 (hard) + T4 (backstop) | Pre | `pre_write_code` AST parse | W1+W3 |
| PP-14 | Guardian comments corrupted | **P0** | T3 (structural) + T4 (backstop) | — | Guardian idempotency + quality scanner | W3 |
| PP-15 | MCP config over-engineered | **P1** | T2 (policy) | — | Simplify to native JSON | W2 |
| PP-16 | Author-Gate ⭐ not calibrated | **P0** | T2 (policy) | — | Measurable target state | W2 |
| PP-17 | ADG underutilized for refactoring | **P1** | T3 (structural) + RA | — | Blast radius + Refactor Accelerator | W3 |
| PP-18 | Plans lack phase summary | **P1** | T2 (policy) | — | Plan template + rule | W2 |

---

## Gap Register

**GAP-1: No `hooks.json` exists — entire hard-gate mechanism unused**
- Windsurf supports `pre_write_code`, `pre_run_command`, `pre_mcp_tool_use` hooks with exit code 2 = BLOCK
- Zero hooks are configured at any level (system, user, workspace)
- Impact: ALL governance is behavioral (rules in prompt) or downstream (pre-commit/CI)

**GAP-2: 7 of 13 rules use non-standard triggers**
- Official Windsurf activation modes: `always_on`, `model_decision`, `glob`, `manual`
- Rules using `file_change` and `pre_commit` triggers may be silently ignored
- Impact: Over half the rules may never reach Cascade's context

**GAP-3: `global_rules.md` is empty**
- 6,000 character budget for cross-workspace always-on rules — completely unused
- Impact: Wasted enforcement capacity

**GAP-4: Token estimator broken — path resolution bug**
- `token_budget_loader.py` resolves to parent of repo root instead of repo root
- Impact: Plans cannot auto-estimate token budgets (constitutional §10.0 violation)

**GAP-5: No MCP green-light prerequisite**
- MCP health checked ad-hoc via `/mcp-failure-rca` only after failures occur
- Impact: Silent MCP failures compound through entire Cascade sessions

**GAP-6: Massive SSOT duplication across tiers**
- PowerShell ban in: rule (T2) + pre-commit T7.8 + (no hook yet)
- Anti-pattern gate in: rule (T2) + workflow (T2) + pre-commit (T4) + ADG (T3)
- MCP config in: rule (T2) + 2 workflows (T2) + 3 pre-commit hooks (T4) + GitHub CI (T5)
- Plan validation in: 2 rules (T2) + 2 pre-commit hooks (T4) + GitHub CI (T5)
- See `governance-enforcement-table.md` for full dedup analysis

**GAP-7: `check_no_archives_imports.py` not wired**
- Constitutional §12 forbids `from archives.` imports in production code
- Script exists in `ops_scripts/ci/` but has no pre-commit hook or CI workflow
- Fix: Wire as pre-commit T7.13

**GAP-8: `check_terminal_cleanup.py` — runtime concern (no fix needed)**
- Constitutional §11 terminal lifecycle. Script exists but is runtime-only
- Pre-commit cannot enforce runtime behavior — T2 rule is correct SSOT

**GAP-9: `check_memory_health.py` not in CI**
- Memory management rule requires daily health checks. No CI workflow exists
- Fix: Add to `adg-pipeline.yml` or nightly cron

**GAP-10: Secrets scan scripts unreferenced**
- `check_secrets_scan.py` and `check_sensitive_logs.py` exist but are wired nowhere
- Fix: Wire `check_secrets_scan.py` as pre-commit T0 gate (critical security)

**GAP-11: `zero_loss_refactor_verifier.py` not wired**
- Constitutional §10 requires zero-loss refactor verification. Script exists, no hook
- Fix: Wire as pre-commit T6.5 (after hollow-file-gate)

**GAP-12: `dead_production_import_gate.py` unreferenced**
- Dead import detection exists but wired nowhere
- Fix: Add to `structure-invariants.yml` CI workflow

**GAP-13: 136 scripts in `ops_scripts/ci/` — ~96 are dead**
- 73 underscore-prefixed scripts: only 2 actively referenced (`_adg_ci_gates.py`, `_validate_pytest_config.py`)
- ~25 non-underscore scripts unreferenced by any pre-commit or CI config
- Fix: Archive 96 scripts to `tools/archive/ops_scripts_ci_deprecated/`

**GAP-14: 13 pre-commit hooks use `cmd /c` Windows shell wrappers**
- Breaks cross-platform CI, violates spirit of Constitutional §0
- Fix: Each script should `sys.path.insert(0, str(Path(__file__).resolve().parents[N]))` internally

**GAP-15: Terminal zombie processes after Cascade chat ends (PP-9)**
- Constitutional §11 mandates terminal lifecycle management but enforcement is behavioral only
- Non-blocking `run_command` processes (dev servers, watchers, long tests) survive chat end
- Multiple chats accumulate orphaned processes → port conflicts, CPU waste, file locks
- Fix: `post_cascade_response` hook attempts best-effort cleanup of spawned processes per-response (not guaranteed at session end). `post_run_command` hook logs command + best-effort PID to `artifacts/windsurf/spawned_processes.jsonl`. PID not natively available in Windsurf `post_run_command` payload — requires OS process table lookup.

**GAP-16: ADG SQLite file lock contention during MCP pause/restart/debug (PP-10)**
- `adg_indexed_*.sqlite` is locked by ADG MCP server process
- Pausing, restarting, or debugging MCP causes: stale locks, read timeouts, "database is locked" errors
- Cascading failures: ADG queries fail → constitutional §2 blocks work → entire session stalls
- Current `adg_close_connections` tool exists but is manual and easy to forget
- Fix: (1) `pre_mcp_tool_use` hook checks SQLite lock state before ADG tool calls, blocks if locked; (2) `post_cascade_response` hook attempts `adg_close_connections` as response-tail cleanup (best-effort, not guaranteed session-end); (3) constitutional §15: "Before restarting any MCP server, call `mcp1_adg_close_connections`. After restart, call `mcp1_adg_reopen_connections` and verify with `mcp1_adg_health`."

**GAP-24: Plans lack phase-level summary table at the top (PP-18)**
- **Symptom**: When plans grow large (this one is 1000+ lines), it’s impossible to see the full scope at a glance. You have to scroll through hundreds of lines to understand what waves exist, what phases are in each wave, and what each phase does.
- **Current state**: The Wave Structure table shows waves but NOT individual phases. Phase details are buried deep in the execution plan sections.
- **What’s needed**: Every plan MUST open with a **phase-level summary table** immediately after the wave overview. This table should show:
  - **Wave** — which wave this phase belongs to
  - **Phase ID** — e.g., 1.1, 2.4, 3.2
  - **Phase Title** — short name
  - **Scope** — 1-sentence description
  - **Pain Points** — which PP-N items this addresses
  - **Est. Tokens** — per-phase estimate
  - **Status** — 🟢/🟡/🔴
- **Enforcement**: Update `.windsurf/templates/execution-plan-template.md` and `.windsurf/rules/plan-location.md` to mandate this table. A plan missing the phase-level summary is **invalid**.
- **Benefit**: Any reader (or Cascade in a new session) can understand the full plan scope in 30 seconds by reading the top table.

**GAP-22: Author-Gate ⭐ recommendations lack concrete quality calibration (PP-16)**
- **Symptom**: The Author-Gate rule says "⭐ RECOMMENDED — SVP priority: operational simplicity, dependency hygiene..." but these are abstract principles. Cascade (and the user) have no concrete picture of what "good" looks like.
- **Root cause**: The recommendation anchor is a list of priorities, not a tangible target state. We say "SVP Engineering" but don’t define what an SVP-quality repo at a frontier AI company actually looks like.
- **Proposed target state** — "OpenAI Agentic SVP Engineering" quality bar:
  - **Code architecture**: Clean layered architecture (L0-L6), zero circular dependencies, every module has a single clear responsibility, no god classes
  - **Testing**: 90%+ meaningful coverage (not line-count gaming), property-based tests for core logic, mutation testing for critical paths, zero flaky tests
  - **Dependency graph**: Fully automated static analysis, blast radius computed before every refactor, no orphaned modules, dependency direction enforced by tooling
  - **Error handling**: Column 5 Precise Exceptions everywhere, zero silent swallowers in production paths, structured error metadata
  - **Observability**: Every significant operation traceable, structured logging, performance baselines
  - **Documentation**: ADRs for every architectural decision, runbooks for operations, API contracts specified
  - **CI/CD**: <5 min full pipeline, zero manual gates, every merge provably safe
  - **Technical debt**: Tracked, ratcheted, never increasing without explicit Author-Gate approval
- **Enforcement**: Update Author-Gate rule §HITL-1 templates to replace abstract SVP priorities with concrete OpenAI Agentic SVP Engineering checklist. Every ⭐ recommendation must cite which target-state attribute it serves.
- **Research needed**: RAG pull from **primary sources first**: OpenAI engineering blog, Anthropic engineering practices, Google DeepMind/Meta monorepo tooling, Windsurf/Codeium official docs. **Secondary implementation references**: LangChain, CrewAI, AutoGen, OpenAI Swarm (ecosystem examples, not quality anchors). Primary-source governance and agent-eval guidance takes precedence.

**GAP-23: ADG static analysis underutilized for intelligent refactoring (PP-17)**
- **Symptom**: We use ADG to *find* antipatterns and *auto-fix* them with scripts. But the real value of a dependency graph is *understanding* the codebase architecture: blast radius, coupling hotspots, dependency clusters, architectural debt concentration. We spend more time running fixers than reading the graph.
- **Current ADG usage (script-heavy, analysis-light)**:
  - `adg_antipattern_fixer.py` — auto-fixes guardian comments (script)
  - `generate_full_adg.py` — generates burndown table (script)
  - `adg_unified_gate.py` — pre-commit gate (script)
  - `mcp1_adg_edge_fanout/fanin` — used for repair loops (analysis, but narrow)
- **Missing ADG analysis capabilities (what OpenAI/Neo4j best practices would add)**:
  - **Blast radius computation**: Before any refactor, compute the full transitive closure of affected files via `edge_fanin` + `edge_fanout`. Present this as a visual or tabular summary BEFORE editing.
  - **Coupling hotspot detection**: Which modules have the highest fan-in? Those are the riskiest to change. ADG can rank them.
  - **Dependency cluster analysis**: Are there tightly-coupled clusters that should be refactored together? Neo4j community detection algorithms (Louvain, Label Propagation) applied to ADG edges.
  - **Architectural debt scoring**: Weight each violation by blast radius — a P2 antipattern in a module with fan-in=50 is far more urgent than one with fan-in=1.
  - **Refactoring impact prediction**: Before moving a module between layers, compute how many imports break, which tests need updating, which downstream consumers are affected.
  - **Change risk scoring**: Combine fan-in, test coverage, antipattern density, and layer position into a per-module risk score. Prioritize remediation by risk, not just severity.
- **Research sources for best practices**:
  - **Neo4j graph algorithms**: Community detection, centrality, pathfinding applied to code dependency graphs
  - **OpenAI engineering blog**: How frontier AI companies manage large codebases, static analysis at scale
  - **Anthropic engineering**: Cascade codebase practices, dependency management
  - **Google/Meta monorepo tooling**: Bazel dependency graph analysis, Meta’s IDE-integrated dependency tools
  - **Academic**: "Architectural Smells" literature, coupling/cohesion metrics from software engineering research
- **Key principle**: **Spend more time intelligently analyzing the ADG static graph than running scripts to automatically fix things.** The graph tells you *where* to focus and *why*. The scripts are just the last mile.
- **Constitutional enhancement**: Add blast radius computation to §2.2 as a MANDATORY step before any T2/T3 refactoring:
  ```
  §2.2 Scope Determination (ENHANCED):
  1. mcp1_adg_health — confirm MCP healthy
  2. mcp1_adg_nodes_by_file — locate entry points
  3. mcp1_adg_edge_fanout — trace downstream blast radius
  4. mcp1_adg_edge_fanin — trace upstream dependents
  5. COMPUTE BLAST RADIUS: union of steps 3+4 = full affected file set
  6. RISK SCORE: fan-in × antipattern density × layer distance = change risk
  7. Declare exact file list with node IDs, blast radius, and risk score as evidence
  ```

**GAP-21: MCP configuration massively over-engineered — killing development velocity (PP-15)**
- **Symptom**: MCP config has become its own workstream. We have built 10+ custom scripts, gates, workflows, and plan phases around managing MCP server configs — something that should take minutes, not weeks.
- **Current overhead inventory (what we built that Windsurf customers almost certainly do NOT):**

| Item | What It Does | Needed? |
|------|-------------|--------|
| `config/mcp_servers.yaml` (797 lines) | YAML SSOT with tool defs, layer assignments, capabilities, env vars | **OVERKILL** — Windsurf only reads `mcp_config.json`. Our YAML has 700+ lines of metadata Windsurf ignores |
| `tools/adg/sync_yaml_to_global.py` | Custom sync YAML → JSON | **OVERKILL** — only needed because we created the YAML layer |
| `ops_scripts/ci/check_mcp_config_sovereignty.py` | Pre-commit gate checking MCP config structure | **QUESTIONABLE** — prevents direct JSON edits, but we created that problem |
| `ops_scripts/ci/check_mcp_npx_windows.py` | Pre-commit gate for npx platform | **KEEP** — catches real cross-platform bugs (but should be 1-liner) |
| Phase 1.5 `post_write_audit.py` MCP lint | Hook running JSON-native lint on MCP config writes | **REPLACED** — was drift detection, now schema/env-var/tool-count lint |
| Phase 2.4 `config/mcp_registry.yaml` | Separate registry artifact for MCP rationale/scope | **OVERKILL** — comments in `mcp_config.json` or a simple README section suffice |
| Phase 2.5 intensive RAG audit (8-point checklist) | Per-MCP upstream validation | **REDUCE** — a one-time version check, not a governance phase |
| `/mcp-config-sync` workflow | Workflow to run sync script | **OVERKILL** — only exists because of YAML layer |
| `/mcp-validate` workflow | Validate MCP config | **ALREADY MARKED ARCHIVE** |
| `mcp_health_check.py` | Health check all MCPs | **KEEP** — useful for diagnosing startup issues |

- **Root cause**: We treated MCP configuration as a governance problem when it is actually a **one-time setup problem**. Windsurf's `mcp_config.json` is the native format. We layered YAML SSOT, sync scripts, drift detection, and registry artifacts on top — creating a governance surface that doesn't exist in normal Windsurf usage.
- **What Windsurf actually expects** (✅ CONFIRMED by RAG pull 2026-04-07 from 4 sources):
  - Edit `~/.codeium/windsurf/mcp_config.json` directly (or use MCP Marketplace UI)
  - Three transport patterns: stdio (`command`/`args`/`env`), Streamable HTTP (`serverUrl`/`headers`), SSE (legacy)
  - Native env var interpolation: `${env:VAR_NAME}` in command, args, env, serverUrl, url, headers
  - **100 tool limit** across all MCPs — can toggle individual tools per MCP in UI
  - No YAML intermediary, no sync scripts, no drift detection — confirmed by all sources
  - Windsurf handles server lifecycle; health = red/green indicators only (no dashboard, no degraded state)
  - Red indicators = config error (bad JSON, missing command) or server crash (non-zero exit)
  - Admin whitelist: server ID must match `mcp_config.json` key case-sensitively
- **Confirmed simplification** (all assumptions validated by RAG):
  1. ~~Research Windsurf docs FIRST~~ → ✅ DONE. Research confirms all assumptions below.
  2. **Collapse YAML → direct JSON** — Windsurf only reads JSON. No other user maintains YAML→JSON pipeline. Our YAML layer is unique overhead.
  3. **Archive sync infrastructure** — `sync_yaml_to_global.py`, `check_mcp_config_sovereignty.py`, `/mcp-config-sync` workflow, Phase 1.3 drift detection → all confirmed unnecessary.
  4. **Merge registry into Markdown** — JSON doesn't support comments. `docs/guides/MCP_Registry.md` is the right format. Include transport type per MCP.
  5. **Reduce 8-point audit to version check** — Windsurf University confirms "periodically check for updates" as standard practice. `npm outdated` + GitHub pulse = sufficient.
  6. **Keep only**: `mcp_health_check.py` (Windsurf has NO native health monitoring — confirmed) + `npx` platform check (1-liner)
  7. **NEW**: Migrate env vars from `${VAR:-default}` to `${env:VAR_NAME}` (Windsurf native interpolation)
  8. **NEW**: Audit total tool count across 14 servers — disable unused tools to stay under 100 limit
- **Net reduction**: ~8 scripts/phases/workflows eliminated. MCP config returns to a **5-minute task** instead of a multi-wave governance workstream.
- **RESEARCH STATUS**: ✅ COMPLETED. RAG pulled from Windsurf docs, MCP best practices, Windsurf University, MCP protocol spec. All assumptions validated. See Phase 2.7 Step 1 for full findings.

**GAP-19: Syntax errors not caught before commit — `except as e:` class of bugs (PP-13)**
- 8 instances of `except as e:` (missing exception type) survived into codebase
- This is **invalid Python syntax** that should NEVER pass any gate
- Current state: `python-syntax-check` hook exists in pre-commit at T1 (`py -m py_compile`) but:
  - Only runs at commit time — Cascade can write syntax errors that persist through an entire session
  - `py_compile` catches `SyntaxError` but not all malformed exception handlers (some parse but fail at runtime)
  - No Tier 1 Windsurf hook validates syntax at write-time
- **Root cause**: `except as e:` is syntactically invalid (should be `except Exception as e:` or `except <SpecificError> as e:`)
- **Tier analysis for syntax checking**:
  - **Tier 1 (Hook)**: `pre_write_code` could AST-parse every `.py` write — catches errors BEFORE they land. **Best for prevention.** Concern: performance on large files
  - **Tier 4 (Pre-commit)**: `py_compile` already exists at T1 — catches at commit time. **Last-resort backstop.** Already working but too late
  - **Tier 3 (ADG)**: ADG generation would fail on syntax errors — but runs infrequently. Not a gate, just a side-effect
  - **RECOMMENDED**: **Tier 1 (Hook) as SSOT for syntax prevention** + Tier 4 as backstop
- Fix: (1) Add AST parse check to `pre_write_gate.py` Phase 1.2 for all `.py` file writes; (2) Harden `py_compile` pre-commit hook to also check for `except as` pattern specifically; (3) Add `ruff` rule E722 (bare except) enforcement at P0 severity in `ruff_severity_gate.py`

**GAP-20: Guardian comments corrupted at scale + unclear exception handling vocabulary (PP-14)**
- **590 files** had massively-duplicated `# guardian:` comments from a prior automated tool run
  - Tool ran without idempotency → comments duplicated on every run
  - Some files had 10+ copies of the same guardian comment
  - Required bulk cleanup pass to restore sanity
- **Root cause of duplication**: `guardian-comment-fixer` (pre-commit T4, `tools/adg/adg_antipattern_fixer.py`) lacked idempotency guard — it appended without checking if comment already existed
- **Exception handling vocabulary confusion**: Developers (and Cascade) conflate:
  - **Column 3 (Broad Swallow)**: `except Exception: pass` — catches everything, suppresses everything. The "silent swallower"
  - **Column 4 (Invalid Stub)**: Test doubles that always return success — masked errors
  - **Column 5 (Precise Exceptions)**: `except (ImportError, KeyError, FileNotFoundError):` — catches specific types with specific recovery. **THE TARGET PATTERN**
  - Reference: `docs/reference/Python/Error & Exception Handling.md`
- **Guardian comment quality**: Many `# guardian: allow-broad-exception` comments lack the specific justification required by Constitutional §8 — generic words ("needed", "required") used instead of explaining WHY broad catch is necessary here
- Fix: (1) Harden `adg_antipattern_fixer.py` with idempotency guard (check before append); (2) Add Column 5 reference to `constitutional.md` §8 guardian exemption section; (3) ADG anti-pattern scanner to flag guardian comments with generic justifications; (4) Add `global_rules.md` entry: "Exception handling MUST follow Column 5 Precise Exceptions pattern from `docs/reference/Python/Error & Exception Handling.md` — catch specific types, recover specifically"

**GAP-18: MCP configurations not validated against latest upstream documentation (PP-12)** — ✅ RESEARCH COMPLETED
- ~~No systematic process to validate MCP server configs against upstream source docs~~ → **RAG research completed 2026-04-07** (see Phase 2.7 Step 1 for full findings)
- **Precedent — sequential-thinking MCP disaster**: Was configured and active until research proved it was buggy, unstable, and deprecated by its maintainer. Wasted sessions debugging hangs that were MCP bugs, not our code. Only discovered via manual investigation, not a governance gate
- **Windsurf config format confirmed by RAG**: Three transport patterns (stdio, Streamable HTTP, SSE). Native `${env:VAR_NAME}` interpolation. 100 tool limit. No native drift detection, health dashboard, or version checking.
- **Descoped from 8-point per-MCP audit to lightweight checks**: Version freshness (`npm outdated`), deprecation status (GitHub pulse), config syntax, tool count under 100, green indicators on startup.
- **Remaining risk areas** (validated by research):
  - Env vars using `${VAR:-default}` shell syntax instead of Windsurf-native `${env:VAR_NAME}` — needs migration
  - Total tool count across 14 MCPs may be near 100 limit — needs audit
  - `npx`-based servers confirmed correct launch pattern (Windsurf docs show `npx` as standard)
- Fix: Lightweight version check (Phase 2.5 descoped) + env var migration + tool count audit (Phase 2.7 action items). Output: `docs/guides/MCP_Registry.md` with per-MCP validation metadata; ADR documenting simplification rationale

**GAP-17: No MCP registry — overlapping responsibilities, undocumented rationale (PP-11)**
- 13 MCP servers configured with no central registry documenting:
  - Rationale: WHY each MCP exists
  - Scope: WHAT each MCP is responsible for (and what it is NOT)
  - SSOT authority: which MCP owns which capability exclusively
  - Overlap: where two MCPs can answer the same query (e.g., `filesystem` vs `github` for file reads)
- Current state: `config/mcp_servers.yaml` defines connection config but not governance metadata
- Known overlaps: (a) `filesystem` vs `github` for file content, (b) `fetch` vs `enhanced_http` for HTTP, (c) `memory` vs `adg_sqlite` for project context, (d) `brave-search` vs `fetch` for web content
- Fix: Create `config/mcp_registry.yaml` as SSOT registry with per-MCP: name, rationale, scope, exclusive authorities, forbidden overlaps. Add constitutional §16: "Before adding a new MCP, consult `config/mcp_registry.yaml` to verify no overlap. Each capability has exactly ONE authoritative MCP."

---

## Five-Tier Governance Architecture (Target State)

### Core Principle: Clean Separation of Concerns

```
┌─────────────────────────────────────────────────────────────────────┐
│  ADG = Structural Truth Engine                                      │
│  ├── What is structurally true?                                     │
│  ├── What depends on this?                                          │
│  ├── Where are the natural seams?                                   │
│  ├── What is the blast radius?                                      │
│  └── What is the safest sequence for change?                        │
│                                                                     │
│  Refactor Accelerator = Change Planner (consumes ADG)               │
│  ├── Ranked refactor candidates                                     │
│  ├── Safe extraction boundaries                                     │
│  ├── Ordered migration sequence                                     │
│  ├── Impacted tests + regression surface                            │
│  └── Do-now vs do-later priority                                    │
│                                                                     │
│  Governance = Decision Authority (Tiers 1–5)                        │
│  ├── What is allowed?                                               │
│  ├── What requires approval?                                        │
│  └── What must pass before promotion?                               │
└─────────────────────────────────────────────────────────────────────┘
```

### Tier Layout

```
TIER 1: Windsurf Cascade Hooks (.windsurf/hooks.json)
  Platform interception at event time. ONLY what hooks can actually inspect and block.

  HARD GATES (pre-hooks — can BLOCK actions, exit 2, FAIL-CLOSED):
  ├── pre_run_command      → PowerShell ban, dangerous command patterns
  ├── pre_write_code       → Anti-pattern injection, syntax errors (ast.parse via edit reconstruction),
  │                          MCP config tiered validation (not blanket deny)
  └── pre_mcp_tool_use     → ADG SQLite lock check, health prerequisite

  ADVISORY PRE-HOOK (pre-hook — always exit 0, FAIL-OPEN):
  └── pre_user_prompt      → Tier classifier + context seeding (never blocks)

  ADVISORY / AUDIT / CLEANUP (post-hooks — exit 0 always, FAIL-OPEN):
  ├── post_write_code      → MCP JSON-native lint, write telemetry
  ├── post_run_command     → Command tracking, best-effort PID registry (audit)
  ├── post_mcp_tool_use    → Tool usage telemetry, response time tracking (audit)
  └── post_cascade_response→ Response-tail cleanup attempt (best-effort, not session-end)

  post_cascade_response fires per-response, NOT per-session.
  It is NOT a guaranteed session-end control plane.
  Any control that MUST prevent an action lives in a pre-hook.

TIER 2: Windsurf Policy Layer (Rules + Skills + Workflows)
  Policy semantics only. Not a second enforcement runtime.
  ├── Rules (always_on)       → Policy: allow/deny/require-approval, risk classes,
  │                              escalation paths, exception policy, scope/ownership
  ├── Rules (glob/model_decision) → File-specific policy constraints
  ├── Skills (5)              → Governed multi-step PROCEDURES with support files
  │                              (graph-analysis, boundary, testing, operational, artifacts)
  └── Workflows               → Manual operator playbooks ONLY (/mcp-failure-rca, etc.)
                                 NOT hidden governance logic.

  Valid trigger modes only: always_on, glob, model_decision, manual
  Invalid triggers (file_change, pre_commit) → remove immediately.

TIER 3: ADG Structural Truth Layer (Analysis-Time)
  Structural evidence only. No policy, no approval, no runtime control.

  IN SCOPE:
  ├── Dependency topology     → file and symbol relationships
  ├── Layer boundary violations → structural violations only
  ├── Cycles                  → circular dependency detection
  ├── Fan-in / fan-out        → centrality metrics
  ├── Blast radius            → transitive closure of affected files
  ├── Ownership / churn hotspots → git-informed structural analysis
  ├── Structural seam detection → candidate extraction boundaries
  ├── Change impact analysis  → likely affected tests
  └── Minimum safe cut sets   → safest refactoring sequence

  OUT OF SCOPE (moved to Tier 2 or Tier 5):
  ├── ✗ Approval semantics    → Tier 2 policy
  ├── ✗ Runtime allow/deny    → Tier 1 hooks
  ├── ✗ Author-Gate ownership        → Tier 2 policy
  ├── ✗ Workflow/runbook semantics → Tier 2 workflows
  ├── ✗ Prompt/chat behavior  → Tier 2 rules
  ├── ✗ Release/promotion authority → Tier 5
  └── ✗ Subjective labels without structural evidence → REMOVED

  REFACTOR ACCELERATOR (adjacent to ADG, not inside governance):
  ├── Inputs: ADG graph, AST/symbol metadata, git churn/ownership,
  │           lint/type/coverage signals, test mapping, architecture rules
  └── Outputs: Ranked refactor candidates, safe extraction boundaries,
               ordered migration sequence, impacted tests, regression surface,
               recommended cut points, do-now vs do-later priority

TIER 4: Pre-commit (Fast Local Quality Ratchet)
  Fast, local, evidence-driven. Consumes Tier 3 + RA outputs. <10s.
  ├── Fresh ADG check      → ADG artifact timestamp < 24h
  ├── P0 count = 0         → Burndown table shows zero P0
  ├── P1 no ratchet        → P1 count ≤ previous commit's P1 count
  ├── Syntax + format      → py_compile, ruff, trailing whitespace
  ├── Import validation    → All imports resolve
  └── Secret detection     → No API keys, no credentials

  Does NOT re-implement governance semantics or architecture policy.

TIER 5: Independent Assurance & Promotion Authority (GitHub CI)
  Cross-platform validation and FINAL promotion decisions.
  ├── Full eval suites     → Matrix test run (Python version compat)
  ├── Integration tests    → Cross-module, MCP backend parity
  ├── Regression testing   → Full ADG generation when evidence stale
  ├── Promotion criteria   → Explicit, measurable pass/fail (not subjective)
  ├── High-risk review     → Changes affecting: external actions, permissions,
  │                          policy logic, write paths, evaluation logic
  └── Approval classes     → ALLOW (auto-merge), DENY (block), REQUIRE_APPROVAL (human review)

  Does NOT duplicate Tier 1 interception or Tier 3 structural analysis.
```

---

## Hardening Requirements

### H-1: No Hardcoded Paths
All hook scripts resolve paths dynamically:
```python
import pathlib
REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]  # ops_scripts/hooks/windsurf/ → repo root
```
**FORBIDDEN**: Literal `C:\`, `C:/Git/`, `/Users/`, `~/.codeium/` in any hook script.

### H-2: Hook Scripts Must Be Tested
Each hook in `ops_scripts/hooks/windsurf/` has companion test in `tests/unit/ops_scripts/hooks/windsurf/`:
- Test stdin JSON parsing (valid + malformed)
- Test exit code 0 (allow) and exit code 2 (block) paths
- Test edge cases (empty edits, missing fields, unicode)

### H-3: hooks.json Uses Repo-Relative Paths
```json
{
  "hooks": {
    "pre_run_command": [{
      "command": "python ops_scripts/hooks/windsurf/pre_run_gate.py",
      "working_directory": ".",
      "show_output": true
    }]
  }
}
```
`working_directory: "."` = workspace root. No absolute paths anywhere.

### H-4: MCP Green Light Prerequisite
`constitutional.md` §13: Before T2/T3 work, call `mcp1_adg_health`. If unhealthy, run `/mcp-failure-rca`.
Reinforced by `pre_mcp_tool_use` hook that warns on stale health.

### H-5: One SSOT Per Concern
See `governance-enforcement-table.md` for full dedup. Each concern has exactly ONE authoritative gate.

### H-6: Risk-Based Fail-Open / Fail-Closed Policy

A blanket "exit 0 on all errors" weakens safety-critical pre-hooks. Failure policy is tiered by hook risk class:

| Hook Risk Class | Examples | Failure Policy | Rationale |
|----------------|---------|---------------|----------|
| **Critical pre-hooks** | `pre_run_gate` (dangerous commands), `pre_write_gate` (syntax, anti-patterns) | **FAIL-CLOSED** (exit 2) when required fields missing or checker integrity broken | A broken safety gate that silently allows everything is worse than temporarily blocking |
| **Non-critical classifier pre-hooks** | `pre_prompt_classifier` (tier classification) | **FAIL-OPEN** (exit 0) with telemetry | Classification failure should not block prompts |
| **Advisory post-hooks** | All `post_*` hooks | **FAIL-OPEN** (exit 0) always | Telemetry/cleanup failure must never break Cascade |
| **Conditional pre-hooks** | `pre_mcp_gate` (ADG lock check) | **FAIL-CLOSED** for ADG calls, **FAIL-OPEN** for non-ADG MCPs | ADG lock contention is a known destructive failure; other MCPs are low-risk |

**Implementation**: Each hook script declares its risk class in a module-level constant `FAIL_POLICY = "closed" | "open"`. The stdin JSON parser wraps all processing in a try/except that respects the declared policy:
- `FAIL_POLICY = "closed"`: malformed JSON or internal error → exit 2 with diagnostic stderr
- `FAIL_POLICY = "open"`: malformed JSON or internal error → exit 0, log to telemetry

---

## Execution Plan

### Wave 0 — MCP Green Light Prerequisite

#### Phase 0.1 — Constitutional §13: MCP Health Check ✅ DONE
**Scope**: Add MCP green-light requirement to `constitutional.md`.

**Changes**:
- UPDATE: `constitutional.md` — add §13: "MCP GREEN LIGHT. Before T2/T3 work, call `mcp1_adg_health`. If unhealthy, run `/mcp-failure-rca`. NEVER begin multi-file work with unhealthy MCPs."
- Behavioral only (T2 rule) — reinforced by T1 hook in Wave 1

**Acceptance**: Constitutional floor includes MCP health prerequisite. Visible every turn.

**COMPLETED**: Added to constitutional floor callout (item 13) and as formal `## §13` section with subsections 13.1–13.4 covering rule, scope table, runtime enforcement references, and recovery escalation steps.

---

### Wave 1 — Cascade Hooks: Hard Gates (pre) + Advisory (post)

**Design principle**: Pre-hooks can BLOCK (exit 2). Post-hooks are advisory/audit/cleanup ONLY (exit 0 always, `show_output: false` by default).

#### Phase 1.1 — Pre-Run Gate — HARD GATE (PP-4, PP-9)
**Scope**: `pre_run_command` hook blocks dangerous commands. No hardcoded paths.

**Files**:
- CREATE: `.windsurf/hooks.json` (repo-relative paths via `working_directory: "."`)
- CREATE: `ops_scripts/hooks/windsurf/pre_run_gate.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_pre_run_gate.py`

**Script behavior** (`pre_run_gate.py`):
- Reads JSON from stdin (`tool_info.command_line`)
- **BLOCKS** (exit 2): `powershell`, `pwsh`, `PowerShell` (case-insensitive)
- **BLOCKS** (exit 2): `pytest tests/unit` when `ADG_REPAIR_ACTIVE` env var set
- All paths via `pathlib.Path(__file__).resolve()` — zero hardcoded paths
- Graceful on malformed JSON: exit 0, log warning

**Supersedes**: Pre-commit T7.8 `powershell-ban-gate` → ARCHIVE

**Acceptance**: Tests green. PowerShell commands blocked. Exit 2 on violation.

#### Phase 1.2 — Pre-Write Gate — HARD GATE (PP-3, PP-13)
**Scope**: `pre_write_code` hook blocks anti-patterns and syntax errors.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/pre_write_gate.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_pre_write_gate.py`
- UPDATE: `.windsurf/hooks.json`

**Hook payload** (Windsurf-documented): `tool_info.file_path` + `tool_info.edits` (array of `{old_string, new_string}`). **Windsurf does NOT provide a full post-write file buffer.** The hook must reconstruct the projected file content by reading the current on-disk file and applying the edit list sequentially before running `ast.parse()`.

**Script behavior** (`pre_write_gate.py`):
- Reconstruct projected file: read on-disk file → apply `edits[].old_string → new_string` in order → produce projected content
- **BLOCKS** (exit 2) — Anti-pattern scan on `new_string` values:
  - `except Exception` without `# guardian: allow-` → EXIT 2
  - `except:` bare except → EXIT 2
  - `shell=True` in subprocess → EXIT 2
- **BLOCKS** (exit 2) — Syntax errors: `ast.parse(projected_content)` on `.py` writes
- **MCP config edits** — tiered response (see Fix 5 below):
  - Schema-valid edits to `mcp_config.json` → ALLOW with lint check
  - Risky edits (removing servers, changing transport type, altering env vars) → REQUIRE_APPROVAL (stderr warning + telemetry)
  - Deleting `mcp_config.json` entirely → EXIT 2 (DENY)
- **Plan format** → NOT enforced here. PP-6 ownership is Tier 2 (Phase 2.9 template/rule). Removed from this gate.

**Supersedes**: Pre-commit T5.5 `windsurf-plan-ci` + T7.5 `plan-location-gate` → ARCHIVE

**Acceptance**: Tests green. Anti-patterns and syntax errors blocked. MCP config tiered. Exit 2 on violation.

#### Phase 1.3 — Pre-MCP Gate — HARD GATE (PP-1, PP-10)
**Scope**: `pre_mcp_tool_use` hook checks ADG SQLite lock and health prerequisites.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/pre_mcp_gate.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_pre_mcp_gate.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior** (`pre_mcp_gate.py`):
- **SQLite lock check** (PP-10): If `mcp_server_name == "adg_sqlite"`, check if `adg_indexed_*.sqlite` has an active write lock. If locked → EXIT 2 with message: "ADG SQLite is locked — call `mcp1_adg_close_connections` before retrying"
- If ADG MCP health >30 min stale → EXIT 2 with message: "ADG health stale — run `mcp1_adg_health` first"
- Graceful on non-ADG MCPs: exit 0 immediately

**Acceptance**: Tests green. ADG calls blocked when SQLite locked or health stale.

#### Phase 1.4 — Pre-User-Prompt Classifier — ADVISORY PRE-HOOK (NEW)
**Scope**: `pre_user_prompt` hook for tier classification and context seeding. **NOT a hard gate** — this hook classifies and annotates, it does not block.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/pre_prompt_classifier.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_pre_prompt_classifier.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior** (`pre_prompt_classifier.py`):
- Classify prompt as T0/T1/T2/T3 based on keywords and context
- Inject tier tag into stderr output for Cascade context seeding
- If T2/T3 detected and no plan file exists → stderr warning (not block)
- If MCP health stale → stderr warning (not block)
- **Always exit 0** — this is a classifier, not a gate. It assists Cascade by pre-computing tier classification and surfacing warnings, but never prevents a prompt.

**PP-6 ownership**: Plan format enforcement is **Tier 2 only** (template + rule in Phase 2.9). This classifier may warn about missing plans for T2/T3 prompts, but the Tier 2 rule is SSOT for plan format requirements. No plan format blocking in Tier 1.

**Acceptance**: Tests green. Pre-prompt classification runs without UX degradation. Always exit 0.

#### Phase 1.5 — Post-Write Audit — ADVISORY (PP-2)
**Scope**: `post_write_code` hook for MCP config lint and general write telemetry. `show_output: false`.

**NOTE**: Once Wave 2.7 archives the YAML layer and makes `mcp_config.json` the native SSOT, "drift" is no longer the right concept (there is no second source to drift from). This hook performs **JSON-native lint** instead.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_write_audit.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_write_audit.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior**:
- If `file_path` matches `mcp_config.json` → run JSON-native lint checks:
  - **Schema validation**: required fields present (`mcpServers`, per-server `command` or `serverUrl`)
  - **Env var format**: flag `${VAR:-default}` shell syntax → suggest `${env:VAR_NAME}` (Windsurf native)
  - **Tool count audit**: count total enabled tools across all servers → warn if approaching 100 limit
  - **Risky edit notice**: flag server removals, transport type changes, or new servers added
- All other files: exit 0 immediately
- **Never blocks** (exit 0 always) — lint results logged to `artifacts/windsurf/mcp_lint_audit.jsonl`
- `show_output: false` — no user-visible output unless explicitly desired

**Acceptance**: Tests green. MCP config edits linted against JSON-native checks.

#### Phase 1.6 — Post-Run Audit — ADVISORY (PP-9)
**Scope**: `post_run_command` hook for PID tracking and command telemetry. `show_output: false`.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_run_audit.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_run_audit.py`
- UPDATE: `.windsurf/hooks.json`

**Hook payload** (Windsurf-documented): `tool_info.command_line` + `tool_info.cwd`. **Windsurf does NOT provide a native PID field** in the `post_run_command` basic payload. PID tracking requires either: (a) parsing command output for PID hints, (b) scanning OS process table for matching command, or (c) accepting command-line + timestamp as the tracking key without PID.

**Script behavior**:
- Append `{"command": <cmd>, "cwd": <cwd>, "timestamp": <iso8601>, "pid": <pid_or_null>}` to `artifacts/windsurf/spawned_processes.jsonl`
- PID: best-effort lookup via OS process table matching `command_line` + `cwd`. Logged as `null` if unavailable.
- **Never blocks** — audit only

**Acceptance**: Tests green. Non-blocking commands tracked. PID best-effort, not guaranteed.

#### Phase 1.7 — Post-MCP Audit — ADVISORY (PP-1)
**Scope**: `post_mcp_tool_use` hook for MCP usage telemetry. `show_output: false`.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_mcp_audit.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_mcp_audit.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior**:
- Logs `mcp_server_name` + `mcp_tool_name` + response time to `artifacts/windsurf/mcp_tool_audit.jsonl`
- **Never blocks** — telemetry only

**Acceptance**: Tests green. MCP tool usage tracked.

#### Phase 1.8 — Post-Cascade Cleanup — ADVISORY (PP-9, PP-10)
**Scope**: `post_cascade_response` hook for **response-tail cleanup attempt**. This fires after each Cascade response, NOT guaranteed at session end. Windsurf documents `post_cascade_response` as providing the response summary since last user input; for rich machine-readable telemetry, the `post_cascade_response_with_transcript` variant is documented separately.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_cascade_cleanup.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_cascade_cleanup.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior**:
- **Process cleanup** (PP-9): Read PID registry, attempt to kill orphaned processes, clear stale entries. **Best-effort** — processes may have already exited or may not have PIDs recorded.
- **ADG lock release** (PP-10): Attempt to release SQLite file locks. **Best-effort** — locks may already be released or held by external processes.
- **Response-tail telemetry**: Log tool call count and hook trigger count for the response just completed. NOT session-level aggregation (session boundaries are not reliably detectable).
- **Never blocks** — response-tail cleanup only. Graceful on missing files or dead PIDs.

**CAUTION**: This hook fires per-response, not per-session. Do NOT assume it runs exactly once at session end. Any control that MUST prevent an action belongs in a pre-hook, not here.

**Acceptance**: Tests green. Best-effort response-tail cleanup. ADG lock release attempted.

---

### Wave 2 — Policy Layer Cleanup (Tier 2 = Policy Only)

**Design principle**: Tier 2 defines WHAT is allowed/denied/requires-approval. It does NOT re-implement enforcement (that's Tier 1 hooks) or structural analysis (that's Tier 3 ADG).

#### Phase 2.1 — Fix 5 Rules, Delete 2 Duplicates (PP-8)
**Scope**: Fix invalid triggers. Delete rules that duplicate T1 hooks or T4 pre-commit.

| Rule | Action | New Trigger | Rationale |
|------|--------|-------------|----------|
| `mcp-config-ssot.md` | FIX + REWRITE | `glob` + `globs: config/mcp_servers.yaml` | Policy guidance only (enforcement in T1 hook) |
| `mcp-pytest-enforcement.md` | FIX | `glob` + `globs: **/test_*.py, **/conftest.py` | Policy: test quality standards |
| `security-hardening.md` | FIX | `model_decision` | Policy: security requirements |
| `anti-pattern-author-gate.md` | FIX | `model_decision` | Policy: exception handling standards |
| `adg-test-accelerator-enforcement.md` | FIX | `glob` + `globs: **/test_*_adg.py, tools/adg/**` | Policy: ADG test standards |
| `plan_ci_enforcement.md` | **DELETE** | — | Dup of T1 hook `pre_write_gate.py` + pre-commit |
| `pytest-config-ssot.md` | **DELETE** | — | Dup of pre-commit T11.3 `_validate_pytest_config.py` |

**Acceptance**: 11 rules remain. All use valid triggers. Zero duplication with T1 hooks.

#### Phase 2.2 — Policy Cleanup + Populate global_rules.md (PP-8)
**Scope**: Archive workflows that contain hidden governance logic. Populate `global_rules.md` with compact policy statements.

**Dedup**: ARCHIVE `mcp-validate.md` → `tools/archive/windsurf/` (dup of pre-commit T11)

**global_rules.md** — compact policy statements (<6,000 chars):
- MCP green light: T2/T3 work requires healthy MCPs
- ADG-first: dependency analysis via ADG, not grep
- Timeout: all subprocess calls require `timeout=`
- PowerShell: forbidden, use `subprocess.run(argv, shell=False)`
- Plans: T2/T3 plans must have wave table
- ADG SQLite lock: release before MCP restart
- MCP authority: one SSOT owner per capability

**Acceptance**: 14 workflows remain. `global_rules.md` populated with policy, not procedure.

#### Phase 2.3 — Constitutional §13/§14 (PP-5)
**Scope**: Add §13 (MCP green light) and §14 (timeout discipline) to `constitutional.md`.

**§13**: MCP GREEN LIGHT — Before T2/T3 work, call `mcp1_adg_health`. If unhealthy, `/mcp-failure-rca`.
**§14**: TIMEOUT DISCIPLINE — All subprocess calls require `timeout=`. Extends existing §11.

**Acceptance**: Both sections in constitutional floor. Visible every Cascade turn.

#### Phase 2.4 — MCP Registry SSOT (PP-11)
**Scope**: Create `docs/guides/MCP_Registry.md` — authoritative registry of all MCP servers with rationale, scope, and SSOT authority.

**Files**:
- CREATE: `docs/guides/MCP_Registry.md` — per-MCP: name, transport, version, rationale, scope, overlaps
- UPDATE: `constitutional.md` — add §16: MCP SSOT Registry

**Constitutional §16**: "MCP SSOT REGISTRY. `docs/guides/MCP_Registry.md` is the authoritative source for MCP responsibilities. Each capability has exactly ONE authoritative MCP. Overlaps documented with resolution."

**Acceptance**: Registry covers all 14 MCPs. Each capability has one SSOT owner. All overlaps documented.

#### Phase 2.5 — MCP Config Version Check (PP-12)
**Scope**: Lightweight version/deprecation check. Research ✅ COMPLETED.

| Check | Method | Frequency |
|-------|--------|-----------|
| Version freshness | `npm outdated` / GitHub pulse | One-time, then quarterly |
| Deprecation status | Upstream repo activity | One-time, then quarterly |
| Config syntax | `mcp_config.json` parses cleanly | Every edit |
| Tool count | Total enabled tools across MCPs | When adding MCPs |
| Red indicator | All 14 MCPs green on startup | Every session |

**Gate**: No MCP added/retained without: (1) version check, (2) deprecation check, (3) green on startup, (4) stability over 1 session.

**Acceptance**: All 14 MCPs green. Zero deprecated MCPs. Tool count under 100.

#### Phase 2.6 — Exception Vocabulary (PP-14)
**Scope**: Column 5 Precise Exceptions as codebase standard.

**Files**:
- UPDATE: `constitutional.md` §8 — add Column 5 reference
- UPDATE: `global_rules.md` — add exception handling policy
- UPDATE: `.windsurf/rules/anti-pattern-author-gate.md` — reference Column 5

**Policy**: Column 5 = REQUIRED pattern. Columns 2-4 = FORBIDDEN. Guardian exemptions only when Column 5 demonstrably impossible.

**Acceptance**: Column 5 vocabulary in constitutional + global_rules.

#### Phase 2.7 — MCP Config Simplification (PP-15)
**Scope**: Eliminate over-engineered MCP config infrastructure. Research ✅ COMPLETED.

| Current | Action | Rationale |
|---------|--------|-----------|
| `config/mcp_servers.yaml` | **ARCHIVE** | YAML layer is overhead |
| `sync_yaml_to_global.py` | **ARCHIVE** | Only exists for YAML layer |
| `check_mcp_config_sovereignty.py` | **ARCHIVE** | Prevents JSON edits — but JSON IS SSOT |
| Phase 1.5 MCP drift logic | **REPLACED** | Drift concept removed — Phase 1.5 now performs JSON-native lint (schema, env vars, tool count) |
| `/mcp-config-sync` workflow | **ARCHIVE** | No sync without YAML layer |
| `mcp_health_check.py` | **KEEP** | Windsurf has NO native health monitoring |
| `check_mcp_npx_windows.py` | **KEEP** | Real cross-platform bug catcher |

**New SSOT**: `~/.codeium/windsurf/mcp_config.json` (Windsurf native). Env vars: `${env:VAR_NAME}`.

**Acceptance**: YAML layer archived. ≤2 MCP governance scripts remain. Config changes <5 min.

#### Phase 2.8 — Author-Gate SVP Calibration (PP-16)
**Scope**: Ground ⭐ recommendations in measurable target state, not abstract principles.

**Problem**: "SVP priority: operational simplicity, dependency hygiene..." is abstract. Every recommendation must be measurable.

**Step 1 — Research**: RAG from **primary sources first**: OpenAI engineering blog, Anthropic engineering practices, Google DeepMind/Meta monorepo tooling, Windsurf/Codeium docs. **Secondary implementation references**: LangChain, CrewAI, AutoGen (ecosystem examples, not quality anchors). Primary-source governance and agent-eval guidance takes precedence over ecosystem framework conventions.

**Step 2 — Target state doc**: CREATE `docs/architecture/target-state-svp-engineering.md` with measurable attributes per category (Architecture, Testing, Dependencies, Error Handling, Observability, Docs, CI/CD, Tech Debt).

**Step 3 — Upgrade Author-Gate templates**: Replace abstract `⭐ RECOMMENDED — SVP priority: ...` with `⭐ RECOMMENDED — Target: <specific measurable attribute>. See target-state doc.` Add §Author-Gate-0.2: all ⭐ must cite specific target-state attribute.

**Step 4 — Update constitutional §9**: SVP persona calibrated to target state doc.

**Acceptance**: Target state doc published. Author-Gate templates cite measurable attributes. §9 updated.

#### Phase 2.9 — Plan Format Enforcement (PP-18)
**Scope**: Mandate phase-level summary table at top of all plans.

**Problem**: Plans grow 1000+ lines. Without a summary table, scope is invisible at a glance.

**Files**:
- UPDATE: `.windsurf/templates/execution-plan-template.md` — add Phase-Level Summary table after Wave Structure
- UPDATE: `.windsurf/rules/plan-location.md` — add format requirement: phase-level summary table mandatory

**Template addition** (insert after Wave Structure table):
```markdown
## Phase-Level Summary (all waves)

| Wave | Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|------|-------|-------|-------|-------------|-------------|--------|
| W1 | 1.1 | [Title] | [1-sentence scope] | PP-N | [tokens] | 🟢/🟡/🔴 |
| W1 | 1.2 | [Title] | [1-sentence scope] | PP-N | [tokens] | 🟢/🟡/🔴 |
| ... | ... | ... | ... | ... | ... | ... |
```

**Rule update** (add to `.windsurf/rules/plan-location.md` Format Requirements):
- 5. Include **phase-level summary table** immediately after the wave summary. Each row = one phase with: Wave, Phase ID, Title, 1-sentence Scope, Pain Points addressed, Token estimate, Status.
- A plan missing the phase-level summary table is **invalid and must not be saved**.

**Acceptance**: Template updated. Rule updated. This plan (as reference implementation) has the phase-level summary table at the top.

#### Phase 2.10 — Approval & Exception Policy (NEW)
**Scope**: Define approval classes, risk categories, and exception policy for Tier 2.

**Approval classes**: ALLOW (auto-proceed), DENY (blocked), REQUIRE_APPROVAL (Author-Gate), ESCALATE (senior review).

**Risk categories**: LOW (≤1 file, ≤20 lines → ALLOW), MEDIUM (2-5 files, single layer → ALLOW with evidence), HIGH (cross-layer, external actions → REQUIRE_APPROVAL), CRITICAL (agent deletion, security boundary → ESCALATE).

**Exception policy**: T1 hard gates cannot be overridden. T2 policy overridable via Author-Gate with rationale. T3 structural evidence informs but does not decide. T5 promotion criteria are absolute.

**Acceptance**: Approval classes and risk categories documented. Exception policy clear.

---

### Wave 2.5 — ADG Generator Modularization (PP-19)

**Rationale**: `tools/generate/generate_full_adg.py` is a 3,305-line / 37-function monolith. Wave 3 builds ADG scope boundaries, burndown formats, and Refactor Accelerator on top of this code. Modularizing first gives W3 clean module boundaries to document and build against. Executing after W2 means Tier 1 syntax gates and Tier 2 policy protect the refactor.

**Source**: `tools/generate/generate_full_adg.py` (3,305 lines, 37 functions)
**Compat wrapper**: `tools/generate_full_adg.py` (21-line shim — NEVER modified)
**Test file**: `tools/generate/test_generate_full_adg_failfast.py` (26 tests, 8 classes, 6 unique imported symbols)
**Pre-commit**: `adg-unified-gate` calls `generate_full_adg.py --strict` — entry point unchanged

#### Current Function Inventory (rebaselined)

| Subpackage | Functions | Lines | Risk |
|------------|----------|-------|------|
| **utils/** | `_is_file_locked` (67), `_perform_wal_checkpoint` (29), `_check_locked_files` (34), `_ratio` (6), `_stable_digest` (10), `_sqlite_table_digest` (14) | ~160 | LOW |
| **archiving/** | `_extract_timestamp` (35), `_parse_timestamp` (23), `_archive_old_artifacts` (182), `_archive_zip_files` (43), `_archive_individual_files` (43), `_create_zip_archive` (61) | ~387 | LOW |
| **validation/** | `_check_artifact_validity` (52), `_check_sqlite_integrity` (35), `_check_artifact_consistency` (41), `_check_p1_defects` (98), `_check_p2_antipatterns` (73), `_check_p3_ratchet` (56), `_check_dead_production_imports` (61) | ~416 | MEDIUM — 22 test imports |
| **reporting/** | `_print_defect_table` (389), `_generate_standardized_reports` (622), `_audit_semantic_surfaces` (55), `_semantic_precision_stats` (60), `_violation_surface_stats` (39), `_violation_propagation_stats` (84), `_artifact_determinism_probe` (64), `_cleanup_validation_files` (75) | ~1,388 | MEDIUM — largest extraction |
| **integration/** | `_auto_ingest_to_redis` (37), `_auto_commit_artifacts` (113), `_persist_adg_to_memory` (33), `_check_mcp_config_lint` (33), `_run_p1_p2_auto_fix` (37) | ~253 | LOW-MEDIUM — external deps |
| **core/** | `generate_full_adg` (455), `_infer_layer` (58), `_generate_timestamp` (7), `_json_dumps` + constants (~30), `main` (94), `_verify_artifacts` (34) | ~678 | MEDIUM — orchestrator |
| **Total** | **37 functions** | **~3,282** | |

#### Target Structure

```
tools/generate/
├── __init__.py                    (exists — re-export main for backward compat)
├── generate_full_adg.py           THIN SHIM: from tools.generate.core.generator import main; ...
├── core/
│   ├── __init__.py
│   ├── config.py                  ROOT, _json_dumps, _generate_timestamp, _infer_layer, constants
│   ├── generator.py               generate_full_adg() orchestrator
│   └── cli.py                     main(), _verify_artifacts, CLI arg parsing
├── utils/
│   ├── __init__.py
│   ├── file_utils.py              _is_file_locked, _perform_wal_checkpoint, _check_locked_files
│   └── digest_utils.py            _ratio, _stable_digest, _sqlite_table_digest
├── validation/
│   ├── __init__.py
│   ├── gates.py                   _check_p1_defects, _check_p2_antipatterns, _check_p3_ratchet, _check_dead_production_imports
│   └── integrity.py               _check_artifact_validity, _check_sqlite_integrity, _check_artifact_consistency
├── reporting/
│   ├── __init__.py
│   ├── defect_table.py            _print_defect_table
│   ├── reports.py                 _generate_standardized_reports
│   └── analysis.py                _audit_semantic_surfaces, _semantic_precision_stats, _violation_surface_stats, _violation_propagation_stats, _artifact_determinism_probe, _cleanup_validation_files
├── archiving/
│   ├── __init__.py
│   ├── archiver.py                _extract_timestamp, _parse_timestamp, _archive_old_artifacts
│   └── zipper.py                  _archive_zip_files, _archive_individual_files, _create_zip_archive
└── integration/
    ├── __init__.py
    ├── redis_ingest.py            _auto_ingest_to_redis
    ├── git_commit.py              _auto_commit_artifacts
    ├── memory_persist.py          _persist_adg_to_memory
    ├── mcp_lint.py                _check_mcp_config_lint
    └── repair_orchestrator.py     _run_p1_p2_auto_fix
```

**Dependency layering** (no cycles):
```
cli.py → core/generator.py
core/generator.py → validation/*, reporting/*, archiving/*, integration/*, utils/*
core/config.py → (stdlib only)
validation/* → utils/*
reporting/* → utils/*
archiving/* → utils/*
integration/* → (external: redis, git, memory MCP)
```

#### Phase M.1 — Extract utils/
**Scope**: Move 6 utility functions (160 lines) to `tools/generate/utils/`.
- `file_utils.py`: `_is_file_locked`, `_perform_wal_checkpoint`, `_check_locked_files`
- `digest_utils.py`: `_ratio`, `_stable_digest`, `_sqlite_table_digest`
- In monolith: replace bodies with `from tools.generate.utils.file_utils import ...`
- **No test import changes** — none of these 6 are directly imported by tests

**Verify**: `pytest tools/generate/test_generate_full_adg_failfast.py -q` green

#### Phase M.2 — Extract archiving/
**Scope**: Move 6 archive/zip functions (387 lines) to `tools/generate/archiving/`.
- `archiver.py`: `_extract_timestamp`, `_parse_timestamp`, `_archive_old_artifacts`
- `zipper.py`: `_archive_zip_files`, `_archive_individual_files`, `_create_zip_archive`
- **No test import changes**

**Verify**: `pytest tools/generate/test_generate_full_adg_failfast.py -q` green

#### Phase M.3 — Extract validation/ (⚠️ test imports change)
**Scope**: Move 7 validation functions (416 lines) to `tools/generate/validation/`.
- `gates.py`: `_check_p1_defects`, `_check_p2_antipatterns`, `_check_p3_ratchet`, `_check_dead_production_imports`
- `integrity.py`: `_check_artifact_validity`, `_check_sqlite_integrity`, `_check_artifact_consistency`
- **Rewrite 22 test import statements** across 8 test classes (6 unique symbols):
  - `from tools.generate.generate_full_adg import _check_artifact_validity` → `from tools.generate.validation.integrity import _check_artifact_validity`
  - `from tools.generate.generate_full_adg import _check_sqlite_integrity` → `from tools.generate.validation.integrity import _check_sqlite_integrity`
  - `from tools.generate.generate_full_adg import _check_artifact_consistency` → `from tools.generate.validation.integrity import _check_artifact_consistency`
  - `from tools.generate.generate_full_adg import _check_p1_defects` → `from tools.generate.validation.gates import _check_p1_defects`
  - `from tools.generate.generate_full_adg import _check_p2_antipatterns` → `from tools.generate.validation.gates import _check_p2_antipatterns`
  - `from tools.generate.generate_full_adg import _check_p3_ratchet` → `from tools.generate.validation.gates import _check_p3_ratchet`

**Risk**: MEDIUM — this is where test breakage is most likely. Run tests after every import change, not as a batch.

**Verify**: `pytest tools/generate/test_generate_full_adg_failfast.py -q` green (all 26 tests)

#### Phase M.4 — Extract reporting/
**Scope**: Move 8 reporting functions (1,388 lines — largest extraction) to `tools/generate/reporting/`.
- `defect_table.py`: `_print_defect_table` (389 lines)
- `reports.py`: `_generate_standardized_reports` (622 lines) + constants `_INFER_LAYER_MAP`, `_MISSING_CAPABILITY_PATHS`
- `analysis.py`: `_audit_semantic_surfaces`, `_semantic_precision_stats`, `_violation_surface_stats`, `_violation_propagation_stats`, `_artifact_determinism_probe`, `_cleanup_validation_files`
- **No test import changes** — none of these are directly imported by tests

**Verify**: `pytest tools/generate/test_generate_full_adg_failfast.py -q` green + manual smoke: `python tools/generate_full_adg.py --help`

#### Phase M.5 — Extract integration/
**Scope**: Move 5 integration functions (253 lines) to `tools/generate/integration/`.
- Each is self-contained with its own subprocess/import chain
- `redis_ingest.py`, `git_commit.py`, `memory_persist.py`, `mcp_drift.py`, `repair_orchestrator.py`
- **No test import changes**

**Verify**: `pytest tools/generate/test_generate_full_adg_failfast.py -q` green

#### Phase M.6 — Extract core/ + slim monolith to shim
**Scope**: Move orchestrator + CLI to `tools/generate/core/`, slim monolith to thin delegator.
- `config.py`: `ROOT`, `_json_dumps` (orjson/json), `_generate_timestamp`, `_infer_layer`, constants
- `generator.py`: `generate_full_adg()` orchestrator (455 lines) — imports from all subpackages
- `cli.py`: `main()` (94 lines), `_verify_artifacts` (34 lines), CLI arg parsing
- Slim `generate_full_adg.py` to:
  ```python
  """ADG generation — delegates to tools.generate.core.cli"""
  from tools.generate.core.cli import main
  if __name__ == "__main__":
      main()
  ```
- `tools/generate/__init__.py`: re-export `main` and `generate_full_adg` for backward compat

**Risk**: MEDIUM — this is the last extraction and changes the import topology

**Verify**: `pytest tools/generate/test_generate_full_adg_failfast.py -q` green

#### Phase M.7 — Modularization Verification
**Scope**: Full end-to-end verification after all extractions.

| # | Test | Expected |
|---|------|----------|
| 1 | `python tools/generate_full_adg.py --help` | CLI help prints (compat wrapper) |
| 2 | `python tools/generate/generate_full_adg.py --help` | CLI help prints (slim delegator) |
| 3 | `pytest tools/generate/test_generate_full_adg_failfast.py -q` | 26 tests pass |
| 4 | `pre-commit run adg-unified-gate --all-files` | Gate runs successfully |
| 5 | Full ADG generation (manual) | 5 artifacts produced |
| 6 | `from tools.generate.generate_full_adg import generate_full_adg` | Import succeeds (backward compat) |
| 7 | No `guardian: allow-*` comments added | `git diff` shows zero new guardian comments |

**Invariants** (must hold after every phase):
1. `python tools/generate_full_adg.py` (root shim) still works end-to-end
2. `pytest tools/generate/test_generate_full_adg_failfast.py -q` passes
3. `tools/generate_full_adg.py` (the 21-line compat wrapper) is NEVER modified
4. All `guardian:` exemption comments preserved verbatim in moved code
5. No new `guardian: allow-*` comments added during refactor
6. Pre-commit `adg-unified-gate` passes

**Acceptance**: Monolith reduced from 3,305 → ~30 lines (shim). 7 subpackages with clear boundaries. All tests + pre-commit green.

---

### Wave 3 — ADG Structural Truth + Refactor Accelerator + Syntax/Guardian Hardening

**Design principle**: ADG = structural evidence ONLY. Refactor Accelerator = change planner consuming ADG. Neither makes governance decisions.

#### Phase 3.1 — ADG Scope Clarification
**Scope**: Formally document ADG in-scope / out-of-scope boundary.

**Files**: UPDATE `constitutional.md` §2, CREATE `docs/reference/ADG_Scope_Boundary.md`

**ADG IN SCOPE** (structural truth only):
- Dependency topology (file + symbol), layer boundary violations, circular deps
- Fan-in / fan-out centrality, blast radius (transitive closure)
- Ownership / churn hotspots (git-informed), structural seam detection
- Change impact analysis, minimum safe cut sets, anti-pattern detection
- Burndown counts (P0/P1/P2 with ratchet tracking)

**ADG OUT OF SCOPE** (explicitly removed):
- ✗ Approval/deny semantics → Tier 2 policy
- ✗ Runtime interception → Tier 1 hooks
- ✗ Author-Gate prompting → Tier 2 rules
- ✗ Promotion/release authority → Tier 5 CI

**Acceptance**: Boundary doc published. §2 references it. No governance logic in ADG outputs.

#### Phase 3.2 — ADG Structural Outputs (PP-17)
**Scope**: ADG produces burndown table with structural metrics + blast radius.

**Burndown table** (`artifacts/adg/adg_burndown_table.json`):
```json
{
  "generated_at": "ISO8601",
  "adg_snapshot_id": "...",
  "counts": { "P0_layer_violations": 0, "P1_anti_patterns": 42, "P1_previous": 45 },
  "p0_clean": true,
  "p1_no_ratchet": true,
  "structural_metrics": { "total_nodes": 0, "max_fan_in": 0, "cycle_count": 0 }
}
```

**Enhanced §2.2** (blast radius mandatory for T2/T3):
1. `adg_health` → 2. `nodes_by_file` → 3. `edge_fanout` (downstream) → 4. `edge_fanin` (upstream)
5. BLAST RADIUS = union(fanout ∪ fanin) → 6. RISK: fan-in, density, coverage, layer span → 7. Declare evidence

**ADG Analysis Playbook** (`docs/reference/ADG_Analysis_Playbook.md`): 6 patterns (blast radius, coupling hotspot, dependency cluster, orphan detection, layer violations, weighted debt).

**Acceptance**: Burndown with structural metrics. Blast radius in §2.2. Playbook published.

#### Phase 3.3 — Refactor Accelerator Design (NEW)
**Scope**: Design the Refactor Accelerator as change planner adjacent to ADG.

**RA inputs**: ADG graph, AST/symbol metadata, git churn/ownership, lint/type/coverage signals, test mapping, architecture rules.

**RA outputs**:
- Ranked refactor candidates: modules sorted by (fan-in × churn × antipattern density)
- Safe extraction boundaries: seams with minimal blast radius
- Ordered migration sequence: leaf → root dependency ordering
- Impacted tests per candidate, regression surface estimate
- Do-now vs do-later priority based on risk × value × effort

**Key distinction**: RA RECOMMENDS. It does not DECIDE. Governance decisions = Tier 2 + Tier 5.

**Acceptance**: RA design doc published. Input/output contract defined.

#### Phase 3.4 — Refactor Accelerator MVP (NEW)
**Scope**: MVP producing ranked refactor list from ADG.

**Files**: CREATE `tools/refactor_accelerator/ra_core.py`, `ra_ranking.py`, tests.

**MVP**: Read ADG burndown + metrics → compute per-module risk score → sort → output `artifacts/refactor_accelerator/ra_candidates.json`.

**Acceptance**: RA produces ranked candidates from real ADG data.

#### Phase 3.5 — Write-time Syntax Gate (PP-13)
**Scope**: `ast.parse()` in `pre_write_gate.py` blocks syntax errors at write-time.

**Changes**:
- UPDATE: `pre_write_gate.py` — AST parse on `.py` writes → EXIT 2 on SyntaxError
- UPDATE: `ruff_severity_gate.py` — E722 (bare except) at P0 severity
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_syntax_gate.py`

**Historical context**: 8 `except as e:` instances survived all gates — no gate checked at write-time.

**Acceptance**: Zero syntax errors pass write-time gate. Pre-commit backstop catches remainders.

#### Phase 3.6 — Guardian Idempotency (PP-14)
**Scope**: Harden `adg_antipattern_fixer.py` — check before append. 590 files corrupted historically.

**Changes**:
- UPDATE: `adg_antipattern_fixer.py` — idempotency check before guardian append
- UPDATE: tests — idempotency cases (run 2x = identical)
- UPDATE: `guardian_exemption_gate.py` — block duplicate guardians

**Acceptance**: Fixer idempotent. Zero duplicates.

#### Phase 3.7 — Guardian Quality Scanner (PP-14)
**Scope**: ADG flags weak guardian justifications ("needed", "required", "temporary" = FORBIDDEN).

**Changes**: ADG detection flags generic justifications. Burndown adds `P1_weak_guardian_justifications`. P1 ratchet prevents increase.

**Acceptance**: Weak justifications flagged. Burndown tracks count.

---

### Wave 4 — Local Quality Ratchet + CI Promotion Authority + Verification

**Design principle**: Tier 4 = fast local checks consuming upstream evidence. Tier 5 = independent assurance with explicit, measurable promotion criteria.

#### Phase 4.1 — Pre-commit Slim-down (Fast Local Quality Ratchet)
**Scope**: Reduce pre-commit to evidence checks + syntax + format. <10s.

**KEEP**: Normalization, syntax (`py_compile`), Ruff, import validation, ADG freshness, burndown evidence, secret detection.

**ARCHIVE** (moved upstream): `check-anti-patterns` → T1 hook, `check-dedup-violations` → T3 ADG, `check-script-sprawl` → T3 ADG, `check-shim-discipline` → T3 ADG, `check-rollback-checkpoints` → T2 rule, `check-c0-sovereignty` → T3 ADG.

**Acceptance**: Pre-commit <10s. Evidence-based only.

#### Phase 4.2 — Dead Script Archival (GAP-13)
**Scope**: Archive ~96 dead scripts from `ops_scripts/ci/`.

**Archive target**: `tools/archive/ops_scripts_ci_deprecated/`

**Underscore scripts (71 → archive all except 2)**:
- KEEP: `_adg_ci_gates.py` (pre-commit T5), `_validate_pytest_config.py` (pre-commit T11.3)
- ARCHIVE: All other 71 underscore-prefixed scripts (one-shot fixers, abandoned gates, debug tools)

**Non-underscore scripts (~25 → archive unreferenced)**:
- See `governance-enforcement-table.md` "UNREFERENCED by any active config" table for full list
- Key archive candidates: `adg_burndown_gate.py` (disabled T13), `adg_layer_violation_gate.py` (disabled T13.5), `adg_p1_defect_gate.py` (disabled T13.6), 6 `adg_*_ban_gate.py` (subsumed by T14 compliance gate)

**Acceptance**: `ops_scripts/ci/` reduced from 136 → ~40 active scripts. All archived scripts in `tools/archive/`.

#### Phase 4.3 — Wire Missing Gates (GAP-7, GAP-9, GAP-10, GAP-11, GAP-12)
**Scope**: Connect 5 existing-but-unwired enforcement scripts.

| Script | Wire To | Gate |
|--------|---------|------|
| `check_no_archives_imports.py` | `.pre-commit-config.yaml` | Archives import ban |
| `check_secrets_scan.py` | `.pre-commit-config.yaml` | Secret detection |
| `zero_loss_refactor_verifier.py` | `.pre-commit-config.yaml` | Hollow file detection |
| `dead_production_import_gate.py` | `structure-invariants.yml` | Dead import detection |
| `check_memory_health.py` | `adg-pipeline.yml` | Memory graph health |

**Acceptance**: All 5 scripts wired.

#### Phase 4.4 — Eliminate `cmd /c` Wrappers (GAP-14)
**Scope**: Remove 13 Windows shell wrappers from `.pre-commit-config.yaml`. Each script adds PYTHONPATH internally.

**Acceptance**: Zero `cmd /c` in `.pre-commit-config.yaml`. Cross-platform.

#### Phase 4.5 — CI Promotion Authority (Tier 5 = Independent Assurance)
**Scope**: Define explicit, measurable promotion criteria. Tier 5 = SOLE promotion authority.

**Promotion criteria** (ALL must pass for merge):

| Criterion | Measurable Target | Verification |
|-----------|------------------|-------------|
| Unit tests | 100% pass, zero skip | `pytest tests/unit -q` exit 0 |
| Integration tests | 100% pass | `pytest tests/integration -q` exit 0 |
| ADG evidence | P0=0, P1 no ratchet | Burndown table check |
| Cross-platform | Windows + Linux green | CI matrix |
| Import resolution | All imports resolve | `test-import-contracts.yml` |
| Architecture | Zero layer violations | `structure-invariants.yml` |

**High-risk review path** (REQUIRE_APPROVAL):
- External actions (API calls, network requests)
- Permission/authentication logic
- Policy/governance config files
- Agent deletion (constitutional §1.6)

**CI workflow reduction** (~36 → ~8):
- KEEP: `main_ci_pipeline.yml`, `adg-pipeline.yml`, `adg-mcp-ci.yml`, `structure-invariants.yml`, `test-import-contracts.yml`, `environment-contract.yml`, `agent-sprawl-check.yml`, `safe-remediation-gate.yml`
- ARCHIVE: ~15 workflows duplicated by upstream tiers

**Acceptance**: Promotion criteria explicit. High-risk review defined. ~8 CI workflows. CI <5min.

#### Phase 4.6 — End-to-End Verification
**Scope**: Measurable verification across all 5 tiers.

| # | Test | Expected | Tier |
|---|------|----------|------|
| 1 | Run `pwsh` | BLOCKED (exit 2) | T1 hard |
| 2 | Write `except Exception:` | BLOCKED (exit 2) | T1 hard |
| 3 | Write to MCP config | BLOCKED (exit 2) | T1 hard |
| 4 | ADG call with locked SQLite | BLOCKED (exit 2) | T1 hard |
| 5 | Edit MCP config file | Drift warning logged | T1 advisory |
| 6 | Run non-blocking command | PID tracked | T1 advisory |
| 7 | MCP tool call | Telemetry logged | T1 advisory |
| 8 | 11 rules in Customizations | Visible | T2 policy |
| 9 | Approval classes documented | ALLOW/DENY/REQUIRE_APPROVAL | T2 policy |
| 10 | Generate ADG | Burndown + structural metrics | T3 structural |
| 11 | RA produces candidates | Ranked list | T3 adjacent |
| 12 | Commit with P0=0 | Pre-commit passes | T4 ratchet |
| 13 | Commit with P0>0 | Pre-commit BLOCKS | T4 ratchet |
| 14 | Push to CI | Promotion criteria checked | T5 promotion |
| 15 | High-risk change | Review required | T5 promotion |

**Acceptance**: All 15 verification steps pass.

---

### Wave 5 — Post-Plan Technical Debt Cleanup (Fast Follow)

**Design principle**: After Waves 1–4 establish the five-tier architecture, Wave 5 is a pure cleanup wave that archives everything the new architecture supersedes. Zero new functionality — only removal, archival, and one rewiring (RepairOrchestrator).

**Prerequisite**: Waves 1–4 must be complete. Tier 1 write-time hooks, Tier 3 ADG burndown evidence, and Tier 4 evidence-based ratchet must all be live before removing the pre-commit hooks they replace.

#### Phase 5.1 — Archive ADG Severity Hooks (pre-commit → Tier 1/3/4)
**Scope**: Remove 3 pre-commit ADG severity hooks superseded by the five-tier architecture + remove 7 commented-out dead entries.

**ARCHIVE** (scripts → `tools/archive/ops_scripts_hooks/`):
- `ops_scripts/hooks/adg_autofix_hook.py` (T4.5) — AUTO_FIX MEDIUM/LOW → superseded by Tier 1 `pre_write_gate.py` + `ruff`
- `ops_scripts/hooks/adg_unified_gate.py` (T10.6) — CRITICAL BLOCK → superseded by ADG generation `_check_p1_defects()` + Tier 4 burndown evidence
- `ops_scripts/hooks/adg_suggest_hook.py` (T10.7) — HIGH SUGGEST → superseded by Tier 3 ADG + Refactor Accelerator

**REMOVE from `.pre-commit-config.yaml`**:
- Active: `adg-autofix` (T4.5), `adg-unified-gate` (T10.6), `adg-suggest-report` (T10.7)
- Commented-out dead entries: `auto-stage` (T0), `adg-burndown-gate` (T13), `adg-layer-violation-gate` (T13.5), `adg-p1-defect-gate` (T13.6), `eager-import-lint` (T10.5), `adg-skip-file-ratchet` (T15), `purge-cache` (T20)

**Rationale**: Every concern these hooks address is handled earlier (Tier 1 write-time, Tier 3 ADG build-time) or faster (Tier 4 burndown JSON read). Live SQLite queries + code mutation at commit time violates Tier 4's evidence-only, <10s mandate.

**Acceptance**: 3 hook scripts archived. 10 entries removed from `.pre-commit-config.yaml`. Zero SQLite queries at commit time.

#### Phase 5.2 — Archive MCP YAML Infrastructure (Phase 2.7 Residuals)
**Scope**: After Phase 2.7 makes `.windsurf/mcp_config.json` the SSOT, the YAML sync pipeline is dead weight.

**ARCHIVE** (→ `tools/archive/mcp_yaml/`):
- `config/mcp_servers.yaml` — former YAML SSOT, replaced by JSON SSOT
- `tools/adg/sync_yaml_to_global.py` — YAML→global sync script
- `ops_scripts/ci/check_mcp_config_sovereignty.py` — sovereignty gate for old YAML config

**REMOVE from `.pre-commit-config.yaml`**:
- `mcp-config-sovereignty` (T11) — triggers on `^mcp_config\.json$` but script checks YAML SSOT
- `mcp-config-drift-check` (T11.2) — calls `sync_yaml_to_global.py --check`

**Acceptance**: Zero YAML MCP infrastructure. 2 pre-commit entries removed.

#### Phase 5.3 — Archive Orphan Hook Scripts (ops_scripts/hooks/)
**Scope**: 13 scripts + 4 baseline files in `ops_scripts/hooks/` not referenced by any active `.pre-commit-config.yaml` entry.

**ARCHIVE** (→ `tools/archive/ops_scripts_hooks/`):

| Script | Reason |
|--------|--------|
| `auto_stage.py` | Commented out in pre-commit (T0) |
| `auto_stage_hook_fixes.py` | Helper for `auto_stage.py` |
| `auto_stage_untracked.py` | Helper for `auto_stage.py` |
| `check_compound_suffix.py` | Not referenced by any config |
| `check_import_resolution.py` | Not referenced by any config |
| `guard_apps_shared_instructional_layer.py` | Not referenced by any config |
| `validate_governance_policy.py` | Not referenced by any config |
| `validate_paths.py` | Not referenced by any config |
| `validate_plan_format.py` | Not referenced (plan_location_gate.py is the active gate) |
| `landmine_baseline.txt.bak` | Backup file |
| `spine_bypass_baseline.txt` | Baseline for removed check |
| `write_bypass_baseline.txt` | Baseline for removed check |
| `import_dep_baseline.txt` | Baseline for removed check |

**KEEP**: `windsurf_plan_ci.py`, `validate_report_location.py`, `reject_tracked_generated_artifacts.py`, `burndown_budget.json`, `guardian_exemption_budget.json`, `skip_file_budget.json`, `post-commit`.

**Verify**: `grep -rn` all archived filenames across active configs → 0 hits.

**Acceptance**: `ops_scripts/hooks/` reduced from 25 → 12 active files. Zero orphans.

#### Phase 5.4 — Archive One-Shot MCP Scripts (tools/mcp/)
**Scope**: 8 deprecated/one-shot scripts in `tools/mcp/` that are no longer used.

**ARCHIVE** (→ `tools/archive/tools_mcp/`):

| Script | Reason |
|--------|--------|
| `expand_mcp_config.py` | Deprecated sync script (superseded by sync_yaml_to_global.py, itself now deprecated) |
| `yaml_to_json_config.py` | Deprecated sync script |
| `fix_hardcoded_paths.py` | One-shot fixer, already applied |
| `mcp_gitkraken_fix.py` | One-shot fix for GitKraken config |
| `mcp_redis_fix.py` | One-shot fix for Redis config |
| `mcp_redis_fix_v2.py` | One-shot fix v2 for Redis config |
| `mcp_redis_wrapper.py` | Superseded by native Redis MCP server |
| `mcp_git_wrapper.py` | Superseded by GitKraken MCP server |

**KEEP**: `pytest_server.py`, `redis_mcp_server.py`, `enhanced_http_server.py`, `terminal_server.py`, `vector_db_server.py` (active MCP servers), `probe_mcps.py`, `e2e_test_all_mcps.py`, `smoke_test_all_mcps.py`, `performance_test_all_mcps.py`, `integration_validation.py` (testing/health).

**Acceptance**: `tools/mcp/` reduced from 18 → 10 active files. Zero deprecated scripts.

#### Phase 5.5 — Rewire RepairOrchestrator into ADG Generation
**Scope**: Move P1 auto-fix from pre-commit time to ADG generation time.

**Current flow**:
```
ADG generation → scan → _check_p1_defects() → sys.exit(1) if P1 > 0
Pre-commit hook → RepairOrchestrator AUTO_FIX (MEDIUM/LOW only)
```

**Target flow**:
```
ADG generation → scan → P1 found? → RepairOrchestrator.attempt_p1_fix() → re-scan → _check_p1_defects() → sys.exit(1) if STILL P1 > 0
```

**Changes**:
- UPDATE: `tools/generate/validation/gates.py` (post-modularization path) — add `_attempt_p1_repair()` before `_check_p1_defects()` halt
- UPDATE: `tools/adg/repair/orchestrator.py` — add `attempt_p1_fix(db_path, defects)` entry point
- CREATE: test coverage for P1 repair → re-scan → halt-if-still-failing flow

**Risk**: MEDIUM — changes ADG generation flow. Must not mask real P1 defects.

**Safety**: P1 auto-fix is best-effort. If `attempt_p1_fix()` throws or the re-scan still shows P1 > 0, generation still halts with `sys.exit(1)`. The RepairOrchestrator never suppresses a real P1.

**Acceptance**: P1 auto-fix runs during ADG generation. Pre-commit no longer invokes RepairOrchestrator. ADG generation still halts on unfixable P1.

#### Phase 5.6 — Archive Deprecated Windsurf Workflows
**Scope**: Archive 3 Windsurf workflows superseded by the five-tier architecture.

**ARCHIVE** (→ `tools/archive/windsurf_workflows/`):

| Workflow | Reason |
|----------|--------|
| `mcp-config-sync.md` | No YAML SSOT → no sync needed (Phase 2.7 + 5.2) |
| `mcp-validate.md` | Superseded by Tier 4 MCP health check (Phase 2.2) |
| `preprocess-rules.md` | One-time setup, no longer needed |

**KEEP**: `adg-redis-refresh.md`, `adg-repair-loop.md`, `adg-test-triage-gate.md`, `adg-timeout-recovery.md`, `agent-deletion-gate.md`, `antipattern-author-gate.md`, `author-gate-decision-gate.md`, `mcp-failure-rca.md`, `memory-purge-sync.md`, `adg-accelerator-optimization.md`, `progress-display-enforcement.md`, `timeout-progress-enforcement.md`.

**UPDATE**: `.windsurf/RULES_INDEX.md` — remove entries for archived workflows.

**Acceptance**: 3 workflows archived. RULES_INDEX updated. `/mcp-config-sync` and `/mcp-validate` slash commands no longer active.

#### Phase 5.7 — Archive Deprecated CI Workflows
**Scope**: Archive ~28 GitHub Actions workflows superseded by Tier 4/5 consolidation (Phase 4.5 execution).

**KEEP** (8 essential — the Phase 4.5 list):
- `main_ci_pipeline.yml` — main test + gate pipeline
- `adg-pipeline.yml` — ADG generation
- `adg-mcp-ci.yml` — MCP health in CI
- `structure-invariants.yml` — architecture enforcement
- `test-import-contracts.yml` — import resolution
- `environment-contract.yml` — environment consistency
- `agent-sprawl-check.yml` — agent creation governance
- `safe-remediation-gate.yml` — safe auto-fix gating

**ARCHIVE** (→ `tools/archive/github_workflows/`) — 28 workflows:
`adg-antipattern-ci.yml`, `adg-ci-gates.yml`, `adg-grep-ban-ci.yml`, `adg-invariant-gates.yml`, `adg-invariant-scan.yml`, `adg-proof-artifact-truthfulness.yml`, `adg-schema-field-names.yml`, `agent-deletion-guard.yml`, `ci-integrity-gate.yml`, `guardian-tests.yml`, `import-resolution-guardian.yml`, `layer-sovereignty-enforcement.yml`, `multi_environment_testing.yml`, `performance_testing.yml`, `plan-validation-ci.yml`, `policy-drift-classification.yml`, `prompt-taxonomy-enforcement.yml`, `pytest-config-ssot.yml`, `release_pipeline.yml`, `security_and_quality.yml`, `skip-registry-convergence.yml`, `spine-determinism-guard.yml`, `ssot-kernel-guardrail.yml`, `ssot_verify.yml`, `system-learning-ci.yml`, `test_suite_validation.yml`, `timeout-progress-enforcement.yml`, `windsurf-governance-health.yml`

**ALSO ARCHIVE**: `_deleted/` subfolder (4 already-dead workflows) → flatten into archive.

**Acceptance**: `.github/workflows/` reduced from 36 active + 4 deleted → 8 active. Zero `_deleted/` folder.

#### Phase 5.8 — Clean Pre-Commit Config
**Scope**: Final cleanup pass on `.pre-commit-config.yaml` after all archival phases complete.

**Actions**:
1. Remove all entries for archived hooks (from Phases 5.1, 5.2)
2. Remove all commented-out dead entries (7 from Phase 5.1)
3. Remove stale comments referencing archived scripts/workflows
4. Verify `cmd /c` elimination complete (Phase 4.4 should have handled, verify zero remaining)
5. Re-number hook tier IDs to close gaps (T4.5, T10.6, T10.7, T11, T11.2, T13–T15 all removed)
6. Consolidate manual-stage hooks: evaluate `check-c0-sovereignty`, `check-dedup-violations`, `check-script-sprawl`, `check-shim-discipline` — if all 4 are subsumed by Tier 3 ADG (per Phase 4.1 ARCHIVE list), remove their manual-stage entries too

**Acceptance**: `.pre-commit-config.yaml` contains only active hooks. Zero commented-out entries. Zero `cmd /c`. Hook IDs are contiguous.

#### Phase 5.9 — Dangling Reference Sweep + Final Verification
**Scope**: Grep-based verification that no active code references any archived script.

**Sweep targets**:
```
grep -rn "adg_autofix_hook\|adg_unified_gate\|adg_suggest_hook" .
grep -rn "sync_yaml_to_global\|check_mcp_config_sovereignty\|mcp_servers\.yaml" .
grep -rn "auto_stage\|check_compound_suffix\|validate_governance_policy" .
grep -rn "expand_mcp_config\|yaml_to_json_config\|mcp_redis_fix" .
grep -rn "mcp-config-sync\|mcp-validate\|preprocess-rules" .windsurf/
```

**Verification matrix**:

| # | Test | Expected |
|---|------|----------|
| 1 | `pre-commit run --all-files` | All active hooks pass, <10s |
| 2 | `python tools/generate_full_adg.py --help` | ADG generation works |
| 3 | `pytest tests/unit -q` | Full suite green |
| 4 | Grep archived filenames in active configs | 0 hits |
| 5 | `.pre-commit-config.yaml` has zero `cmd /c` | Verified |
| 6 | `.pre-commit-config.yaml` has zero commented-out hook entries | Verified |
| 7 | `.github/workflows/` contains ≤8 files | Verified |
| 8 | `ops_scripts/hooks/` contains ≤12 files | Verified |
| 9 | `tools/mcp/` contains ≤10 files | Verified |
| 10 | `ls tools/archive/` shows all archive subdirs | Verified |

**Acceptance**: All 10 verification steps pass. Zero dangling references.

#### Phase 5.10 — Archive ADG Root One-Shot Scripts (~148 files)
**Scope**: `tools/adg/` contains 248 items but only ~30 are live infrastructure. The remaining ~148 are one-shot fixers, debug scripts, ad-hoc queries, and completed validation passes.

**ARCHIVE** (→ `tools/archive/adg_oneshot/`):

| Category | Count | Examples |
|----------|-------|---------|
| `__dbg_*` debug harnesses | 6 | `__dbg_classes.py`, `__dbg_methods.py`, `__dbg_routing_matrix.py`, `__dbg_scripts.py`, `__dbg_scripts2.py`, `__dbg_ssot.py` |
| Ticket-numbered fixers | 8 | `adg_1608_final_fix.py`, `adg_1608_hardening_wire.py`, `adg_1653_*.py` (6 files, one is hollow — calls undefined `main()`) |
| Timestamped/status reports | 4 | `adg_regen_status_03292026_2240.py`, `adg_p3_status.py`, `adg_p4_status.py`, `adg_p4_final_status.py` |
| Underscore ad-hoc scripts | 22 | `_adg_ap_*.py` (5), `_adg_gap_*.py` (2), `_adg_heal_*.py` (2), `_adg_gov_peek.py`, `_adg_query.py`, `_adg_rationalization_query.py`, `_adg_resolve_conflicts.py`, `_adg_size_rca.py`, `_adg_sovereign_territories_analysis.py`, `_adg_inspect_nodes.py`, `_exec_ssot_violations.py`, `_gv_violates_*.py` (2), `_multi_file_violations.py`, `_violates_lines.py`, `_violations_survey.py` |
| One-shot wirers/patchers | 21 | `mega_wire_adg.py`, `micro_wave_wirer.py` (34KB), `p0_batch_wirer.py`, `p0_fallback_wirer.py`, `p0_gap_analyzer.py`, `p0_microwave_wirer.py`, `p0_runtime_deficit.py`, `p1_docstring_repair.py`, `p1_fallback_wirer.py`, `l4_*.py` (6), `wave_packer.py`, `add_execution_trace.py`, `adg_add_determinism_edges.py`, `adg_add_mutation_edges.py`, `adg_layer_annotation_fix.py`, `patch_orphan_imports.py` |
| One-shot validation/gap scripts | 15 | `adg_validation_final.py`, `adg_final_gap_validation.py` (27KB), `adg_rigorous_gap_closure_0617.py` (32KB), `adg_execution_grade_validation.py` (36KB), `adg_static_validation.py`, `adg_static_validation_real.py` (35KB), `adg_precision_pass.py`, `semantic_gap_analyzer.py` (94KB!), `closure_gap_analysis.py`, `precision_hardening_engine.py`, etc. |
| Dead code/cleanup tools | 10 | `bulk_delete_dead_code.py`, `bulk_uwg_migrator.py`, `delete_functions.py`, `delete_redundant_stubs.py`, `delete_test_functions.py`, `remove_unused_imports.py`, `strip_boilerplate.py`, `hollow_file_cleanup.py`, `adg_cleanup_directory.py`, `phase_script_archiver.py` |
| Coverage/query/report scripts | 33 | `coverage_*.py` (3), `final_coverage_report.py`, `query_dead_*.py` (2), `query_execution_trace_coverage.py`, `query_guardrail_coverage.py`, `query_writes_through_*.py` (2), `find_*.py` (4), `generate_missing_stubs.py`, `identify_*.py` (3), `check_*.py` (6), `denominator_*.py` (4), `debug_new_stub_coverage.py`, `filter_*.py` (2), `adg_update_reports.py`, `adg_violation_histogram.py`, `adg_archive_analysis.py`, `ingest_*.py` (4), `react_chunking_graph_audit.py`, `repo_hygiene_classifier.py`, `edge_signal_analysis.py`, `boilerplate_ratio_report.py`, `capability_extractor.py`, `antipattern_detection.py`, `identity_normalizer.py`, `runtime_acceleration.py` |
| Hollow `__main__.py` | 1 | 154 lines of `_emit_*` boilerplate calls with zero behavioral logic (Constitutional §10 violation) |

**KEEP** (core infrastructure — ~30 files):
- `core/` (4 files) — `__init__.py`, `models.py`, `service.py`, `sqlite_backend.py`
- `mcp/server.py` + `mcp/health.py` + `mcp/__init__.py`
- `cache/` (2 files) — `__init__.py`, `redis_cache.py`
- `repair/` (11 files) — orchestrator, rules, engine, types, git integration
- `report_parsers/` (10 files) — base + 8 concrete parsers
- `accelerators/` (3 files) — `__init__.py`, `__main__.py`, `orchestrator.py`
- `services/` (3 files) — `__init__.py`, `adg_invariant_runner.py`, `adg_query_service.py`
- Key scripts: `adg_mcp_entry.py`, `adg_antipattern_analyzer.py`, `adg_antipattern_fixer.py`, `adg_redis_ingest.py`, `adg_redis_query.py`, `adg_redis_validation.py`, `adg_stale_guard.py`, `adg_harden.py`, `adg_insight_cli.py`, `adg_intelligent_burndown.py`, `dep_graph_db.py`, `adg_semantic_builder.py`, `adg_layer_boundary_checker.py`, `adg_import_validator.py`, `adg_type_check.py`, `adg_test_accelerator.py`, `adg_test_classifier.py`, `adg_test_selector.py`, `adg_test_triage.py`, `adg_timeout_scanner.py`, `adg_scanner_audit.py`, `adg_incremental_update.py`, `adg_ci_gate.py`, `adg_ci_lane_gate.py`, `adg_lifecycle.py`, `detect_tombstone_modules.py`, `drift_lifecycle.py`, `drift_score.py`, `redis_health_check.py`, `adg_namespaced_ingest.py`, `adg_layer_overrides.yaml`
- Evaluate: `adg_cli.py` (63KB — may need refactoring), `adg_debug_cli.py`, `adg_direct.py`, `adg_query_bridge.py`

**Acceptance**: `tools/adg/` reduced from 248 → ~100 items (core + subdirs). Zero hollow files. Zero ticket-numbered scripts.

#### Phase 5.11 — Archive ADG MCP Duplicates + shared_modules/ + queries/ (~26 files)
**Scope**: Three categories of internal ADG debt.

**ARCHIVE MCP duplicates** (→ `tools/archive/adg_mcp_deprecated/`):

| File | Reason |
|------|--------|
| `adg_mcp_server.py` (38KB) | Old custom Redis MCP server, superseded by `tools/mcp/redis_mcp_server.py` |
| `mcp/server_clean.py` | Duplicate launcher with hardcoded `C:\Git\Agentic-Workflow` path |
| `mcp/server_debug.py` | Duplicate launcher with hardcoded path |
| `mcp/server_launcher.py` | Duplicate launcher with hardcoded path |
| `mcp/run_server.bat` | Batch file launcher (Constitutional §0 — no shell scripts) |
| `configure_mcp.py` | One-shot config script with hardcoded `C:\Users\amita\` path |
| `enhanced_redis_mcp_client.py` | Explicitly marked `DEPRECATED` in docstring |

**ARCHIVE shared_modules/** (→ `tools/archive/adg_shared_modules/`):

| File | Size | Reason |
|------|------|--------|
| `file_operations.py` | 49KB | Extracted stub from `UniversalWriteGateway.py` (2026-03-27) |
| `string_processing.py` | 33KB | Extracted stub from test file |
| `extracted_training_pipeline.py` | 59KB | Extracted stub from `system_learning` |
| `extracted_test_template_rendering_e2e.py` | 46KB | Extracted stub from test |
| `extracted_capability_extractor.py` | 21KB | Extracted stub |
| `extracted_capability_registry.py` | 25KB | Extracted stub |
| `validation.py` | 24KB | Extracted validation |
| `path_resolver.py` | 2KB | Path resolver |

Total: 257KB of dead extracted stubs, not imported by anything.

**ARCHIVE queries/** (→ `tools/archive/adg_queries/`):
- `adg_align_query.py` through `adg_align_query7.py` (7 numbered iterations!)
- `adg_redis_live_query.py`
- `adg_rlhf_sft_query.py`, `adg_rlhf_sft_query2.py`
- `__init__.py`

**ARCHIVE archives/** (→ flatten into `tools/archive/adg_oneshot/`):
- `archives/auto_fix_p1_p2.py` — already in an archives subfolder inside adg

**Acceptance**: Zero MCP duplicate launchers. Zero `shared_modules/`. Zero `queries/`. Zero `archives/` subfolder.

#### Phase 5.12 — Archive tools/ One-Shot Graveyard (~600 files)
**Scope**: Six directories under `tools/` are entirely comprised of completed one-shot scripts.

| Directory | Files | Total Size | Contents | Archive Target |
|-----------|-------|------------|----------|----------------|
| `tools/fix/` | 134 | ~780KB | One-shot fixers (`fix_*.py`, `batch_fix_*.py`, `ast_*.py`) — all already applied | `tools/archive/tools_fix/` |
| `tools/analysis/` | 122 | ~440KB | Ad-hoc analysis scripts (`check_*.py`, `analyze_*.py`, `categorize_*.py`) | `tools/archive/tools_analysis/` |
| `tools/evidence/` | 163 | ~1.2MB | Phase evidence runners (`phase*_evidence_runner.py`, `wave*_runner.py`, `qwen_migration_*.py`) | `tools/archive/tools_evidence/` |
| `tools/waves/` | 36 | ~100KB | Completed wave scripts (`convert_wave_*.py`, `_apply_wave_*.py`) | `tools/archive/tools_waves/` |
| `tools/testing/` | 60 | ~570KB | Ad-hoc test scripts not in `tests/` suite (sequential thinking tests, MCP tests, wave tests) | `tools/archive/tools_testing/` |
| `tools/debug/` | 13 | ~60KB | Debug scripts (`debug_*.py`) | `tools/archive/tools_debug/` |
| `tools/diagnose/` | 22 | ~50KB | Diagnostic scripts (`diagnose_*.py`) | `tools/archive/tools_diagnose/` |
| `tools/scripts/` | 45 | ~270KB | Misc scripts (demos, shell scripts, helpers) | `tools/archive/tools_scripts/` |

**Also archive**:
- `tools/silent_swallower_report.json` (1.1MB!) — generated report in tools root
- Root-level `silent_swallower_report.json` (1.1MB!) — duplicate in repo root
- `tools/cleanup/` (5 files) — cleanup scripts

**KEEP under tools/**:
- `tools/adg/` (post-Phase 5.10 cleanup)
- `tools/generate/` (ADG generation pipeline)
- `tools/mcp/` (post-Phase 5.4 cleanup)
- `tools/archive/` (archival target)
- `tools/utils/` (active utilities)
- `tools/memory/` (memory MCP server)
- `tools/guardian/` (guardian enforcement)
- `tools/ingestion/` (data ingestion — evaluate)
- `tools/otel/` (OpenTelemetry — evaluate)
- `tools/ci/` (CI tools — evaluate)
- `tools/governance/` (governance — evaluate)
- `tools/profiling/` (profiling — evaluate)
- `tools/repair/` (repair — evaluate)
- `tools/migrate/` (migration — evaluate)
- `tools/test_enforcement/` (test enforcement — evaluate)
- `tools/learning/` (learning — evaluate)
- `tools/windsurf/` (windsurf config)
- `tools/__init__.py`, `tools/generate_full_adg.py`

**Acceptance**: `tools/` reduced from ~1,200 items to ~200 active items. Zero one-shot scripts outside `tools/archive/`.

#### Phase 5.13 — Fix Hardcoded Paths in ADG MCP Entry
**Scope**: `adg_mcp_entry.py` has hardcoded `C:\Git\Agentic-Workflow` — must use `Path(__file__).resolve()` or environment variable.

**Files to fix**:
- `tools/adg/adg_mcp_entry.py` — lines 8-9: `sys.path.insert(0, r"C:\Git\Agentic-Workflow")` and `os.chdir(r"C:\Git\Agentic-Workflow")`

**Target**: Replace with:
```python
_REPO = str(Path(__file__).resolve().parents[3])
sys.path.insert(0, _REPO)
os.chdir(_REPO)
```

**Acceptance**: Zero hardcoded `C:\Git\Agentic-Workflow` in any non-archived Python file. Verified with `grep -rn "C:\\\\Git\\\\Agentic" tools/adg/ --include="*.py"`.

#### Phase 5.14 — tools/ Directory Consolidation + Expanded Verification
**Scope**: After Phases 5.10–5.13, update Phase 5.9 verification matrix with expanded checks.

**Additional verification steps**:

| # | Test | Expected |
|---|------|----------|
| 11 | `tools/adg/` item count | ≤100 |
| 12 | `tools/fix/` exists | NO (archived) |
| 13 | `tools/analysis/` exists | NO (archived) |
| 14 | `tools/evidence/` exists | NO (archived) |
| 15 | `tools/waves/` exists | NO (archived) |
| 16 | `tools/testing/` exists | NO (archived) |
| 17 | `tools/debug/` exists | NO (archived) |
| 18 | `tools/diagnose/` exists | NO (archived) |
| 19 | `tools/scripts/` exists | NO (archived) |
| 20 | `grep -rn "C:\\\\Git\\\\Agentic" tools/ --include="*.py"` outside archive | 0 hits |
| 21 | `silent_swallower_report.json` in repo root or tools/ | NO (archived) |
| 22 | `tools/adg/shared_modules/` exists | NO (archived) |
| 23 | `tools/adg/queries/` exists | NO (archived) |
| 24 | ADG MCP server starts clean | `mcp1_adg_health` returns OK |

**Acceptance**: All 24 verification steps pass (original 10 + 14 new). `tools/` is a clean, navigable directory.

---

## Rules

- Each wave is independently deliverable — Wave 1 is highest value
- Hook scripts must be Python (no PowerShell, no bash on Windows)
- Pre-hooks must be fast (<2s) to avoid UX degradation
- Post-hooks are advisory only — exit 0 always, `show_output: false` default
- ADG produces structural evidence only — no governance decisions
- Refactor Accelerator recommends — governance layers decide
- Pre-commit hooks being archived go to `tools/archive/pre-commit/`
- All changes require existing tests to continue passing

---

## Success Criteria

**Wave 1 — Hooks (3 Hard Gates + 1 Advisory Pre-Hook + 4 Advisory Post-Hooks)**:
- [ ] `.windsurf/hooks.json` with 4 pre-hooks (3 hard gate + 1 classifier) + 4 post-hooks
- [ ] Hard gate pre-hooks BLOCK (exit 2, fail-closed). Classifier pre-hook always exit 0. Post-hooks always exit 0.
- [ ] Every hook script has companion unit test
- [ ] Zero hardcoded paths. Risk-based fail-open/fail-closed per H-6.
- [ ] PowerShell blocked, syntax errors blocked (via edit reconstruction), MCP config tiered (not blanket deny)
- [ ] Best-effort PID tracking, MCP telemetry, response-tail cleanup (not session-end)

**Wave 2 — Policy Layer**:
- [ ] 11 rules remain, valid triggers, zero duplication with T1 hooks
- [ ] `global_rules.md` populated with policy (not procedure)
- [ ] YAML layer archived, JSON is SSOT
- [ ] MCP Registry.md published, all 14 MCPs documented
- [ ] Target state doc published, Author-Gate ⭐ calibrated to measurable attributes
- [ ] Plan format enforcement in template + rule
- [ ] Approval classes (ALLOW/DENY/REQUIRE_APPROVAL/ESCALATE) documented
- [ ] Column 5 Precise Exceptions in constitutional + global_rules

**Wave 2.5 — ADG Generator Modularization**:
- [ ] Monolith reduced from 3,305 → ~30 lines (thin shim)
- [ ] 7 subpackages created (utils, archiving, validation, reporting, integration, core)
- [ ] 22 test imports rewritten, all 26 tests green
- [ ] `adg-unified-gate` pre-commit passes
- [ ] Full ADG generation produces 5 artifacts
- [ ] Backward compat: `from tools.generate.generate_full_adg import generate_full_adg` works
- [ ] Zero new `guardian: allow-*` comments

**Wave 3 — ADG Structural Truth + Refactor Accelerator**:
- [ ] ADG scope boundary documented (in/out explicit, no governance logic)
- [ ] Burndown table with structural metrics produced
- [ ] Blast radius mandatory in constitutional §2.2
- [ ] ADG Analysis Playbook published (6 patterns)
- [ ] Refactor Accelerator design doc published
- [ ] RA MVP produces ranked candidates from real ADG data
- [ ] Syntax gate at write-time (`ast.parse`)
- [ ] Guardian fixer idempotent, quality scanner active

**Wave 4 — Local Ratchet + CI Promotion**:
- [ ] Pre-commit <10s, evidence-based only
- [ ] ~96 dead scripts archived (136 → ~40)
- [ ] 5 missing gates wired, 13 `cmd /c` wrappers eliminated
- [ ] CI promotion criteria explicit and measurable
- [ ] High-risk review path defined
- [ ] ~8 CI workflows remain, <5min
- [ ] All 15 E2E verification steps pass

**Wave 5 — Post-Plan Tech Debt Cleanup**:
- [ ] 3 ADG severity hooks archived, 10 pre-commit entries removed (3 active + 7 dead)
- [ ] MCP YAML infrastructure archived (config, sync script, sovereignty gate)
- [ ] 13 orphan hook scripts + 4 baselines archived from `ops_scripts/hooks/`
- [ ] 8 one-shot MCP scripts archived from `tools/mcp/`
- [ ] RepairOrchestrator rewired into ADG generation (P1 auto-fix at build time)
- [ ] 3 deprecated Windsurf workflows archived
- [ ] ~28 deprecated CI workflows archived (36 → 8)
- [ ] `.pre-commit-config.yaml` clean: zero dead entries, zero `cmd /c`, contiguous IDs
- [ ] Dangling reference sweep: zero hits across all configs/rules/docs
- [ ] ~148 ADG root one-shot scripts archived (tools/adg/ from 248 → ~100 items)
- [ ] 7 ADG MCP duplicates + 8 shared_modules (257KB) + 11 queries archived
- [ ] ~600 one-shot scripts archived from tools/fix/, analysis/, evidence/, waves/, testing/, debug/, diagnose/, scripts/
- [ ] 2× silent_swallower_report.json (2.2MB) archived
- [ ] Zero hardcoded `C:\Git\Agentic-Workflow` paths in non-archived code
- [ ] `tools/` consolidated from ~1,200 → ~200 active items
- [ ] All 24 Wave 5 verification steps pass

---

## Rollback Strategy

1. **Wave 1**: Delete `.windsurf/hooks.json` → all hooks disabled instantly
2. **Wave 2**: Revert rule frontmatter changes via git
3. **Wave 2.5**: Revert `tools/generate/` to monolith from git history (`git checkout HEAD~N -- tools/generate/`)
4. **Wave 3**: ADG scope changes are doc-only (revert docs). RA is additive (delete `tools/refactor_accelerator/`)
5. **Wave 4**: Restore archived pre-commit hooks + CI workflows from git history
6. **Wave 5**: Restore archived scripts from `tools/archive/` subdirs via `git checkout HEAD~N`. RepairOrchestrator rewiring reverts with `tools/generate/` revert. Pre-commit config restores from git history.

Each wave is independently rollbackable.

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|-------------|
| **Tier 1 — Hard Gates (3 pre-hooks)** | | |
| Pre-hook blocks PowerShell | 100% blocked (exit 2) | `pytest test_pre_run_gate.py -q` |
| Pre-hook blocks syntax errors | 100% blocked via edit reconstruction (exit 2) | `pytest test_pre_write_gate.py -q` |
| MCP config tiered validation | Schema-valid → ALLOW, risky → REQUIRE_APPROVAL, delete → DENY | `pytest test_pre_write_gate.py -q` |
| Pre-hook blocks locked SQLite | ADG calls blocked (exit 2) | `pytest test_pre_mcp_gate.py -q` |
| **Tier 1 — Advisory Pre-Hook (1)** | | |
| Prompt classifier never blocks | Always exit 0, tier tag in stderr | `pytest test_pre_prompt_classifier.py -q` |
| **Tier 1 — Advisory Post-Hooks (4)** | | |
| Post-hooks never block | All exit 0 | `pytest test_post_*_audit.py -q` |
| Post-hook telemetry | MCP calls + commands logged, PID best-effort | Audit log files exist |
| Fail-open/fail-closed per H-6 | Critical → fail-closed, advisory → fail-open | Test cases per FAIL_POLICY |
| Response-tail cleanup | Best-effort per-response, not session-end | `pytest test_post_cascade_cleanup.py -q` |
| No hardcoded paths | 0 literal paths | `grep -rn "C:\\\|/Users/" ops_scripts/hooks/windsurf/` = 0 |
| **Tier 2 — Policy** | | |
| Rules valid triggers | 11/11 valid modes | Cascade Customizations panel |
| SSOT dedup | 0 enforcement duplicates | governance-enforcement-table.md audit |
| Approval classes | ALLOW/DENY/REQUIRE_APPROVAL/ESCALATE | Policy doc review |
| MCP Registry | 14 MCPs documented | `docs/guides/MCP_Registry.md` exists |
| Author-Gate ⭐ calibration | All cite target-state attributes | `grep "target-state" author-gate-enforcement.md` |
| Column 5 vocabulary | In constitutional §8 | `grep "Column 5" constitutional.md` |
| **Wave 2.5 — ADG Modularization** | | |
| Monolith → shim | 3,305 → ~30 lines | `wc -l tools/generate/generate_full_adg.py` |
| Subpackages | 7 packages created | `ls tools/generate/*/` |
| Test stability | 26/26 tests green | `pytest tools/generate/test_*.py -q` |
| Pre-commit compat | adg-unified-gate passes | `pre-commit run adg-unified-gate` |
| Backward compat | Old imports still work | `python -c "from tools.generate.generate_full_adg import generate_full_adg"` |
| No guardian creep | 0 new guardian comments | `git diff --stat` |
| **Tier 3 — Structural Truth** | | |
| ADG scope boundary | In/out-of-scope explicit | `docs/reference/ADG_Scope_Boundary.md` exists |
| ADG blast radius | Mandatory in §2.2 | `grep "BLAST RADIUS" constitutional.md` |
| ADG burndown table | Produced with structural metrics | `artifacts/adg/adg_burndown_table.json` schema |
| ADG Analysis Playbook | 6 patterns documented | `docs/reference/ADG_Analysis_Playbook.md` exists |
| RA design | Input/output contract defined | Design doc published |
| RA MVP | Ranked candidates from ADG | `artifacts/refactor_accelerator/ra_candidates.json` |
| Syntax gate (write-time) | 0 syntax errors pass | `test_syntax_gate.py` |
| Guardian idempotency | Fixer 2x = identical | `test_adg_antipattern_fixer.py` |
| Guardian quality | 0 generic justifications | Burndown `P1_weak_guardian_justifications` = 0 |
| **Tier 4 — Local Ratchet** | | |
| Pre-commit speed | <10s | `time pre-commit run --all-files` |
| P0 gate | Blocked if P0 > 0 | Burndown evidence check |
| P1 ratchet | Blocked if P1 increased | Burndown evidence check |
| Dead scripts archived | ~96 moved | `ls tools/archive/ops_scripts_ci_deprecated/` |
| cmd /c wrappers | 0 in pre-commit | `grep "cmd /c" .pre-commit-config.yaml` = 0 |
| **Tier 5 — Promotion** | | |
| CI workflows | ≤8 essential | Count active .yml files |
| CI speed | <5min | CI run time |
| Promotion criteria | Explicit and measurable | CI config review |
| High-risk review | Path defined | CI config includes review gates |
| E2E verification | 15/15 steps pass | Phase 4.6 matrix |
| **Wave 5 — Tech Debt Cleanup** | | |
| ADG severity hooks archived | 3 scripts in `tools/archive/ops_scripts_hooks/` | `ls tools/archive/ops_scripts_hooks/adg_*` |
| Pre-commit dead entries removed | 0 commented-out hook entries | `grep "^#.*id:" .pre-commit-config.yaml` = 0 |
| MCP YAML infrastructure archived | 3 files in `tools/archive/mcp_yaml/` | `ls tools/archive/mcp_yaml/` |
| Orphan hook scripts archived | 13 scripts + 4 baselines archived | `ops_scripts/hooks/` ≤12 files |
| One-shot MCP scripts archived | 8 scripts archived | `tools/mcp/` ≤10 files |
| RepairOrchestrator rewired | P1 auto-fix at ADG build time | `grep "attempt_p1" tools/generate/validation/gates.py` |
| Windsurf workflows archived | 3 workflows archived | `.windsurf/workflows/` has 12 files |
| CI workflows archived | 28 workflows archived | `.github/workflows/` ≤8 active files |
| Pre-commit config clean | Zero `cmd /c`, zero dead entries, contiguous IDs | Manual audit |
| Dangling references | 0 hits for archived filenames | Phase 5.9 grep sweep |
| ADG root one-shot archived | `tools/adg/` ≤100 items | `ls tools/adg/ | wc -l` |
| ADG MCP duplicates archived | Zero `server_clean.py`, `server_debug.py`, `run_server.bat` | `ls tools/adg/mcp/` |
| ADG shared_modules archived | `tools/adg/shared_modules/` does not exist | `test -d` check |
| ADG queries archived | `tools/adg/queries/` does not exist | `test -d` check |
| tools/fix/ archived | Directory does not exist | `test -d` check |
| tools/analysis/ archived | Directory does not exist | `test -d` check |
| tools/evidence/ archived | Directory does not exist | `test -d` check |
| tools/waves/ archived | Directory does not exist | `test -d` check |
| tools/testing/ archived | Directory does not exist | `test -d` check |
| tools/ total items | ≤200 active items | Item count excluding archive/ |
| Hardcoded paths | 0 `C:\Git\Agentic` in non-archived .py | `grep -rn` sweep |
| silent_swallower_report.json | Not in repo root or tools/ root | `ls` check |
| ADG MCP health post-cleanup | `mcp1_adg_health` returns OK | MCP tool call |
| Wave 5 verification | 24/24 steps pass | Phase 5.14 matrix |
