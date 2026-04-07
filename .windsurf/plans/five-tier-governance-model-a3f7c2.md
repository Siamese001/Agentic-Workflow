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
| Wave 0 | 0.1 | MCP green light prerequisite | Z: constitutional §13 MCP health check | ~2K | 🟢 READY |
| Wave 1 | 1.1–1.8 | Cascade Hooks: pre-hooks = hard gates, post-hooks = advisory/audit only | A: hooks block pwsh, anti-patterns; audit hooks log; zombie cleanup | ~16K | 🟢 READY |
| Wave 2 | 2.1–2.10 | Policy layer cleanup + MCP simplification + HITL calibration + plan format | B: all rules loading, MCP simplified, HITL calibrated, plan template updated | ~15K | 🟢 READY |
| **Wave 2.5** | **M.1–M.7** | **ADG Generator Modularization** (3,305-line monolith → 7 subpackages) | **B2: `generate_full_adg.py` → package, tests green, pre-commit green** | **~18K** | **🟡 AFTER W2** |
| Wave 3 | 3.1–3.7 | ADG structural truth + Refactor Accelerator + syntax/guardian hardening | C: ADG scoped to structure, RA created, syntax gate, guardian idempotent | ~16K | 🟡 DEPENDS ON W2.5 |
| Wave 4 | 4.1–4.6 | Local quality ratchet + CI promotion authority + verification | D: fast pre-commit, explicit promotion criteria, full pipeline green | ~10K | 🟢 READY |

**Total: ~77K tokens across 6 waves (Wave 0, 1, 2, 2.5, 3, 4)**

Token estimator UNRESOLVED — `token_budget_loader.py` has path bug (uses parent of repo root). Estimates are manual.

---

## Phase-Level Summary (all waves)

| Wave | Phase | Title | Scope | Pain Points | Est. Tokens | Status |
|------|-------|-------|-------|-------------|-------------|--------|
| W0 | 0.1 | MCP Green Light | Add §13 MCP health prerequisite to constitutional floor | PP-1 | ~2K | 🟢 |
| W1 | 1.1 | Pre-Run Gate (HARD) | Block PowerShell, dangerous commands, PID tracking | PP-4, PP-9 | ~2K | 🟢 |
| W1 | 1.2 | Pre-Write Gate (HARD) | Block anti-patterns, syntax errors, MCP config protection | PP-3, PP-6, PP-13 | ~3K | 🟢 |
| W1 | 1.3 | Pre-MCP Gate (HARD) | ADG-first enforcement, SQLite lock check, health prerequisite | PP-1, PP-10 | ~2K | 🟢 |
| W1 | 1.4 | Pre-User-Prompt Gate (HARD) | Scope enforcement, tier classification, plan prerequisite | — | ~2K | 🟢 |
| W1 | 1.5 | Post-Write Audit (ADVISORY) | MCP config drift detection, lint suggestions | PP-2 | ~1K | 🟢 |
| W1 | 1.6 | Post-Run Audit (ADVISORY) | PID registry for zombie tracking, command telemetry | PP-9 | ~1K | 🟢 |
| W1 | 1.7 | Post-MCP Audit (ADVISORY) | MCP tool usage telemetry, response time tracking | PP-1 | ~1K | 🟢 |
| W1 | 1.8 | Post-Cascade Cleanup (ADVISORY) | Kill zombie processes, release ADG locks, session telemetry | PP-9, PP-10 | ~2K | 🟢 |
| W2 | 2.1 | Fix Rules (Policy) | Fix 5 broken rule triggers, delete 2 duplicates | PP-8 | ~1K | 🟢 |
| W2 | 2.2 | Policy Cleanup | Archive workflow-as-governance, populate global_rules.md | PP-8 | ~1K | 🟢 |
| W2 | 2.3 | Constitutional §13/§14 | Add MCP green light + timeout discipline to constitutional | PP-5 | ~1K | 🟢 |
| W2 | 2.4 | MCP Registry SSOT | Create MCP registry with rationale/scope/overlaps | PP-11 | ~2K | 🟢 |
| W2 | 2.5 | MCP Config Version Check | Lightweight version/deprecation check (research ✅) | PP-12 | ~1K | 🟢 |
| W2 | 2.6 | Exception Vocabulary | Column 5 Precise Exceptions in constitutional §8 | PP-14 | ~1K | 🟢 |
| W2 | 2.7 | MCP Config Simplification | Archive YAML layer, collapse to native JSON (research ✅) | PP-15 | ~2K | 🟢 |
| W2 | 2.8 | HITL SVP Calibration | Ground ⭐ recommendations in measurable target state | PP-16 | ~2K | 🟢 |
| W2 | 2.9 | Plan Format Enforcement | Mandate phase-level summary table at top of all plans | PP-18 | ~1K | 🟢 |
| W2 | 2.10 | Approval & Exception Policy | Define allow/deny/require-approval classes, escalation paths, risk classes | — | ~2K | 🟢 |
| **W2.5** | **M.1** | **Extract utils/** | Move 6 utility functions (file_utils, digest_utils) to subpackage | PP-19 | ~2K | 🟡 |
| **W2.5** | **M.2** | **Extract archiving/** | Move 6 archive/zip functions to subpackage | PP-19 | ~2K | 🟡 |
| **W2.5** | **M.3** | **Extract validation/** | Move 6 validation/gate functions + rewrite 22 test imports | PP-19 | ~3K | 🟡 |
| **W2.5** | **M.4** | **Extract reporting/** | Move defect table (389 lines) + reports (622 lines) to subpackage | PP-19 | ~3K | 🟡 |
| **W2.5** | **M.5** | **Extract integration/** | Move 5 integration functions (redis, git, memory, mcp, repair) | PP-19 | ~2K | 🟡 |
| **W2.5** | **M.6** | **Extract core/ + main.py** | Move orchestrator + CLI + config to core package, slim monolith to shim | PP-19 | ~3K | 🟡 |
| **W2.5** | **M.7** | **Modularization Verification** | Full E2E: generate ADG, tests green, pre-commit green, no import breakage | PP-19 | ~3K | 🟡 |
| W3 | 3.1 | ADG Scope Clarification | Explicit in-scope / out-of-scope boundary for ADG | — | ~1K | 🟡 |
| W3 | 3.2 | ADG Structural Outputs | Burndown table, blast radius, seam detection, centrality | PP-17 | ~3K | 🟡 |
| W3 | 3.3 | Refactor Accelerator Design | RA spec: inputs (ADG + git + lint + test), outputs (ranked candidates, safe cuts) | — | ~3K | 🟡 |
| W3 | 3.4 | Refactor Accelerator MVP | RA produces ranked refactor list, impacted tests, migration order | — | ~3K | 🟡 |
| W3 | 3.5 | Write-time Syntax Gate | AST parse in pre_write_gate blocks syntax errors | PP-13 | ~2K | 🟡 |
| W3 | 3.6 | Guardian Idempotency | Harden antipattern fixer, block duplicate guardians | PP-14 | ~2K | 🟡 |
| W3 | 3.7 | Guardian Quality Scanner | ADG flags weak justifications, P1 ratchet | PP-14 | ~1K | 🟡 |
| W4 | 4.1 | Pre-commit Slim-down | Fast local quality ratchet — evidence checks + syntax + format only | — | ~2K | 🟢 |
| W4 | 4.2 | Dead Script Archival | Archive ~96 dead scripts from ops_scripts/ci/ | GAP-13 | ~2K | 🟢 |
| W4 | 4.3 | Wire Missing Gates | Connect 5 existing-but-unwired enforcement scripts | GAP-7,9,10,11,12 | ~2K | 🟢 |
| W4 | 4.4 | Eliminate cmd /c | Remove 13 Windows shell wrappers from pre-commit | GAP-14 | ~1K | 🟢 |
| W4 | 4.5 | CI Promotion Authority | Explicit promotion criteria, high-risk review path, approval classes | — | ~3K | 🟢 |
| W4 | 4.6 | End-to-End Verification | Measurable verification across all 5 tiers | — | ~1K | 🟢 |

---

## Priority Map (User Pain Points → Gates)

**Key distinction**: Pre-hooks (`pre_*`) = **hard gates** that can BLOCK actions. Post-hooks (`post_*`) = **advisory/audit/cleanup** only.

| ID | Pain Point | Severity | Gate Tier | Hook Type | Hook Event | Wave |
|----|-----------|----------|-----------|-----------|------------|------|
| PP-1 | MCP servers silently failing | **P0** | T1 (advisory) + T2 (policy) | Post | `post_mcp_tool_use` telemetry + `post_cascade_response` health summary | W1 |
| PP-2 | MCP config drift | **P0** | T1 (advisory) | Post | `post_write_code` drift warning | W1 |
| PP-3 | Silent swallowers / antipatterns | **P0** | T1 (hard) + T3 (structural) | Pre | `pre_write_code` pattern scan | W1 |
| PP-4 | PowerShell causes hangs | **P1** | T1 (hard) | Pre | `pre_run_command` blocks pwsh | W1 |
| PP-5 | Timeouts not implemented | **P1** | T2 (policy) | — | `always_on` rule | W2 |
| PP-6 | Plans missing waves | **P1** | T1 (hard) | Pre | `pre_write_code` plan format check | W1 |
| PP-7 | ADG not used as primary tool | **P2** | T2 (policy) | — | `always_on` rule | W2 |
| PP-8 | Rules using invalid triggers | **P2** | T2 (policy) | — | Fix frontmatter triggers | W2 |
| PP-9 | Zombie processes accumulate | **P0** | T1 (advisory) | Post | `post_run_command` PID registry + `post_cascade_response` cleanup | W1 |
| PP-10 | ADG SQLite lock contention | **P0** | T1 (hard + advisory) | Pre+Post | `pre_mcp_tool_use` lock check + `post_cascade_response` lock release | W1 |
| PP-11 | No MCP registry | **P1** | T2 (policy) | — | MCP registry doc | W2 |
| PP-12 | MCP configs not validated | **P1** | T2 (policy) | — | Lightweight version check (research ✅) | W2 |
| PP-13 | Syntax errors in codebase | **P0** | T1 (hard) + T4 (backstop) | Pre | `pre_write_code` AST parse | W1+W3 |
| PP-14 | Guardian comments corrupted | **P0** | T3 (structural) + T4 (backstop) | — | Guardian idempotency + quality scanner | W3 |
| PP-15 | MCP config over-engineered | **P1** | T2 (policy) | — | Simplify to native JSON | W2 |
| PP-16 | HITL ⭐ not calibrated | **P0** | T2 (policy) | — | Measurable target state | W2 |
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
- Fix: `post_cascade_response` hook tracks spawned PIDs and kills them on chat end. Also add `pre_run_command` hook that logs PID for tracking. New process registry at `artifacts/windsurf/spawned_processes.jsonl`

**GAP-16: ADG SQLite file lock contention during MCP pause/restart/debug (PP-10)**
- `adg_indexed_*.sqlite` is locked by ADG MCP server process
- Pausing, restarting, or debugging MCP causes: stale locks, read timeouts, "database is locked" errors
- Cascading failures: ADG queries fail → constitutional §2 blocks work → entire session stalls
- Current `adg_close_connections` tool exists but is manual and easy to forget
- Fix: (1) `pre_mcp_tool_use` hook checks SQLite lock state before ADG tool calls, warns if locked; (2) `post_cascade_response` hook calls `adg_close_connections` automatically on chat end; (3) constitutional §15: "Before restarting any MCP server, call `mcp1_adg_close_connections`. After restart, call `mcp1_adg_reopen_connections` and verify with `mcp1_adg_health`."

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

**GAP-22: HITL ⭐ recommendations lack concrete quality calibration (PP-16)**
- **Symptom**: The HITL rule says "⭐ RECOMMENDED — SVP priority: operational simplicity, dependency hygiene..." but these are abstract principles. Cascade (and the user) have no concrete picture of what "good" looks like.
- **Root cause**: The recommendation anchor is a list of priorities, not a tangible target state. We say "SVP Engineering" but don’t define what an SVP-quality repo at a frontier AI company actually looks like.
- **Proposed target state** — "OpenAI Agentic SVP Engineering" quality bar:
  - **Code architecture**: Clean layered architecture (L0-L6), zero circular dependencies, every module has a single clear responsibility, no god classes
  - **Testing**: 90%+ meaningful coverage (not line-count gaming), property-based tests for core logic, mutation testing for critical paths, zero flaky tests
  - **Dependency graph**: Fully automated static analysis, blast radius computed before every refactor, no orphaned modules, dependency direction enforced by tooling
  - **Error handling**: Column 5 Precise Exceptions everywhere, zero silent swallowers in production paths, structured error metadata
  - **Observability**: Every significant operation traceable, structured logging, performance baselines
  - **Documentation**: ADRs for every architectural decision, runbooks for operations, API contracts specified
  - **CI/CD**: <5 min full pipeline, zero manual gates, every merge provably safe
  - **Technical debt**: Tracked, ratcheted, never increasing without explicit HITL approval
- **Enforcement**: Update HITL rule §HITL-1 templates to replace abstract SVP priorities with concrete OpenAI Agentic SVP Engineering checklist. Every ⭐ recommendation must cite which target-state attribute it serves.
- **Research needed**: RAG pull from OpenAI engineering blog, Anthropic engineering practices, frontier AI company open-source repos (OpenAI Swarm, LangChain, CrewAI) to validate and refine target state.

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
  - **Anthropic engineering**: Claude codebase practices, dependency management
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
| Phase 1.3 `post_write_gate.py` MCP drift | Hook running `sync --check` on every write | **OVERKILL** — if we edit JSON directly, no drift possible |
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
  4. **Merge registry into Markdown** — JSON doesn't support comments. `docs/reference/MCP_Registry.md` is the right format. Include transport type per MCP.
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
- Fix: Lightweight version check (Phase 2.5 descoped) + env var migration + tool count audit (Phase 2.7 action items). Output: `docs/reference/MCP_Registry.md` with per-MCP validation metadata; ADR documenting simplification rationale

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

  HARD GATES (pre-hooks — can BLOCK actions, exit 2):
  ├── pre_run_command      → PowerShell ban, dangerous command patterns
  ├── pre_write_code       → Anti-pattern injection, syntax errors (ast.parse), MCP config protection
  ├── pre_mcp_tool_use     → ADG SQLite lock check, health prerequisite
  └── pre_user_prompt      → Scope enforcement, tier classification, plan prerequisite

  ADVISORY / AUDIT / CLEANUP (post-hooks — exit 0 always, show_output off by default):
  ├── post_write_code      → MCP drift warning, lint suggestions (telemetry)
  ├── post_run_command     → PID registry for zombie tracking (audit)
  ├── post_mcp_tool_use    → Tool usage telemetry, response time tracking (audit)
  └── post_cascade_response→ Kill zombie processes, release ADG locks (cleanup)

  post_cascade_response is NOT a guaranteed session-end control plane.
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
  ├── ✗ HITL ownership        → Tier 2 policy
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

### H-6: Graceful Degradation
Hook scripts exit 0 on malformed stdin JSON or internal errors. Never break Cascade on hook bugs.

---

## Execution Plan

### Wave 0 — MCP Green Light Prerequisite

#### Phase 0.1 — Constitutional §13: MCP Health Check
**Scope**: Add MCP green-light requirement to `constitutional.md`.

**Changes**:
- UPDATE: `constitutional.md` — add §13: "MCP GREEN LIGHT. Before T2/T3 work, call `mcp1_adg_health`. If unhealthy, run `/mcp-failure-rca`. NEVER begin multi-file work with unhealthy MCPs."
- Behavioral only (T2 rule) — reinforced by T1 hook in Wave 1

**Acceptance**: Constitutional floor includes MCP health prerequisite. Visible every turn.

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

#### Phase 1.2 — Pre-Write Gate — HARD GATE (PP-3, PP-6, PP-13)
**Scope**: `pre_write_code` hook blocks anti-patterns, syntax errors, MCP config writes.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/pre_write_gate.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_pre_write_gate.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior** (`pre_write_gate.py`):
- Receives `tool_info.file_path` + `tool_info.edits`
- **BLOCKS** (exit 2) — Anti-pattern scan on `new_string`:
  - `except Exception` without `# guardian: allow-` → EXIT 2
  - `except:` bare except → EXIT 2
  - `shell=True` in subprocess → EXIT 2
- **BLOCKS** (exit 2) — Syntax errors: `ast.parse(file_content)` on `.py` writes
- **BLOCKS** (exit 2) — MCP config protection: writes to `*/mcp_config*.json`
- **WARNS** (stderr, no block) — Plan format: `*/plans/*.md` without wave table

**Supersedes**: Pre-commit T5.5 `windsurf-plan-ci` + T7.5 `plan-location-gate` → ARCHIVE

**Acceptance**: Tests green. Anti-patterns and syntax errors blocked. Exit 2 on violation.

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

#### Phase 1.4 — Pre-User-Prompt Gate — HARD GATE (NEW)
**Scope**: `pre_user_prompt` hook for scope enforcement and tier classification.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/pre_user_prompt_gate.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_pre_user_prompt_gate.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior** (`pre_user_prompt_gate.py`):
- Lightweight checks on prompt context before Cascade processes it
- Verify plan file exists if T2/T3 work is in progress
- Verify MCP health state is current (advisory, not blocking for T0/T1)
- Graceful: exit 0 on all edge cases — this gate assists, not blocks

**Acceptance**: Tests green. Pre-prompt checks run without UX degradation.

#### Phase 1.5 — Post-Write Audit — ADVISORY (PP-2)
**Scope**: `post_write_code` hook for MCP drift detection and telemetry. `show_output: false`.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_write_audit.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_write_audit.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior**:
- If `file_path` matches MCP config files → log drift warning to telemetry
- All other files: exit 0 immediately
- **Never blocks** (exit 0 always) — telemetry and warning only
- `show_output: false` — no user-visible output unless explicitly desired

**Acceptance**: Tests green. MCP config edits logged.

#### Phase 1.6 — Post-Run Audit — ADVISORY (PP-9)
**Scope**: `post_run_command` hook for PID tracking and command telemetry. `show_output: false`.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_run_audit.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_run_audit.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior**:
- Append `{"pid": <pid>, "command": <cmd>, "timestamp": <iso8601>}` to `artifacts/windsurf/spawned_processes.jsonl`
- PID extracted from Windsurf hook context (if available) or logged as "unknown"
- **Never blocks** — audit only

**Acceptance**: Tests green. Non-blocking commands tracked in PID registry.

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
**Scope**: `post_cascade_response` hook for cleanup. NOT a guaranteed session-end control plane.

**Files**:
- CREATE: `ops_scripts/hooks/windsurf/post_cascade_cleanup.py`
- CREATE: `tests/unit/ops_scripts/hooks/windsurf/test_post_cascade_cleanup.py`
- UPDATE: `.windsurf/hooks.json`

**Script behavior**:
- **Process cleanup** (PP-9): Read PID registry, kill orphaned processes, clear registry
- **ADG lock release** (PP-10): Release SQLite file locks for clean next session
- **Session telemetry**: Log session duration, tool call count, hook trigger count
- **Never blocks** — cleanup only. Graceful on missing files or dead PIDs.

**Acceptance**: Tests green. Best-effort zombie cleanup. ADG locks released.

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
| `anti-pattern-hitl-gate.md` | FIX | `model_decision` | Policy: exception handling standards |
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
**Scope**: Create `docs/reference/MCP_Registry.md` — authoritative registry of all MCP servers with rationale, scope, and SSOT authority.

**Files**:
- CREATE: `docs/reference/MCP_Registry.md` — per-MCP: name, transport, version, rationale, scope, overlaps
- UPDATE: `constitutional.md` — add §16: MCP SSOT Registry

**Constitutional §16**: "MCP SSOT REGISTRY. `docs/reference/MCP_Registry.md` is the authoritative source for MCP responsibilities. Each capability has exactly ONE authoritative MCP. Overlaps documented with resolution."

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
- UPDATE: `.windsurf/rules/anti-pattern-hitl-gate.md` — reference Column 5

**Policy**: Column 5 = REQUIRED pattern. Columns 2-4 = FORBIDDEN. Guardian exemptions only when Column 5 demonstrably impossible.

**Acceptance**: Column 5 vocabulary in constitutional + global_rules.

#### Phase 2.7 — MCP Config Simplification (PP-15)
**Scope**: Eliminate over-engineered MCP config infrastructure. Research ✅ COMPLETED.

| Current | Action | Rationale |
|---------|--------|-----------|
| `config/mcp_servers.yaml` | **ARCHIVE** | YAML layer is overhead |
| `sync_yaml_to_global.py` | **ARCHIVE** | Only exists for YAML layer |
| `check_mcp_config_sovereignty.py` | **ARCHIVE** | Prevents JSON edits — but JSON IS SSOT |
| Phase 1.5 MCP drift logic | **SIMPLIFY** | If JSON is SSOT, drift = non-problem |
| `/mcp-config-sync` workflow | **ARCHIVE** | No sync without YAML layer |
| `mcp_health_check.py` | **KEEP** | Windsurf has NO native health monitoring |
| `check_mcp_npx_windows.py` | **KEEP** | Real cross-platform bug catcher |

**New SSOT**: `~/.codeium/windsurf/mcp_config.json` (Windsurf native). Env vars: `${env:VAR_NAME}`.

**Acceptance**: YAML layer archived. ≤2 MCP governance scripts remain. Config changes <5 min.

#### Phase 2.8 — HITL SVP Calibration (PP-16)
**Scope**: Ground ⭐ recommendations in measurable target state, not abstract principles.

**Problem**: "SVP priority: operational simplicity, dependency hygiene..." is abstract. Every recommendation must be measurable.

**Step 1 — Research**: RAG from OpenAI, Anthropic, LangChain/CrewAI/AutoGen engineering practices.

**Step 2 — Target state doc**: CREATE `docs/architecture/target-state-svp-engineering.md` with measurable attributes per category (Architecture, Testing, Dependencies, Error Handling, Observability, Docs, CI/CD, Tech Debt).

**Step 3 — Upgrade HITL templates**: Replace abstract `⭐ RECOMMENDED — SVP priority: ...` with `⭐ RECOMMENDED — Target: <specific measurable attribute>. See target-state doc.` Add §HITL-0.2: all ⭐ must cite specific target-state attribute.

**Step 4 — Update constitutional §9**: SVP persona calibrated to target state doc.

**Acceptance**: Target state doc published. HITL templates cite measurable attributes. §9 updated.

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

**Approval classes**: ALLOW (auto-proceed), DENY (blocked), REQUIRE_APPROVAL (HITL), ESCALATE (senior review).

**Risk categories**: LOW (≤1 file, ≤20 lines → ALLOW), MEDIUM (2-5 files, single layer → ALLOW with evidence), HIGH (cross-layer, external actions → REQUIRE_APPROVAL), CRITICAL (agent deletion, security boundary → ESCALATE).

**Exception policy**: T1 hard gates cannot be overridden. T2 policy overridable via HITL with rationale. T3 structural evidence informs but does not decide. T5 promotion criteria are absolute.

**Acceptance**: Approval classes and risk categories documented. Exception policy clear.

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
- ✗ HITL prompting → Tier 2 rules
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

**Wave 1 — Hooks (4 Hard Gates + 4 Advisory)**:
- [ ] `.windsurf/hooks.json` with 4 pre-hooks + 4 post-hooks
- [ ] Pre-hooks can BLOCK (exit 2). Post-hooks always exit 0.
- [ ] Every hook script has companion unit test
- [ ] Zero hardcoded paths. Graceful degradation on malformed JSON.
- [ ] PowerShell blocked, syntax errors blocked, MCP config protected, scope enforced
- [ ] PID tracking, MCP telemetry, cleanup on session end

**Wave 2 — Policy Layer**:
- [ ] 11 rules remain, valid triggers, zero duplication with T1 hooks
- [ ] `global_rules.md` populated with policy (not procedure)
- [ ] YAML layer archived, JSON is SSOT
- [ ] MCP Registry.md published, all 14 MCPs documented
- [ ] Target state doc published, HITL ⭐ calibrated to measurable attributes
- [ ] Plan format enforcement in template + rule
- [ ] Approval classes (ALLOW/DENY/REQUIRE_APPROVAL/ESCALATE) documented
- [ ] Column 5 Precise Exceptions in constitutional + global_rules

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

---

## Rollback Strategy

1. **Wave 1**: Delete `.windsurf/hooks.json` → all hooks disabled instantly
2. **Wave 2**: Revert rule frontmatter changes via git
3. **Wave 3**: ADG scope changes are doc-only (revert docs). RA is additive (delete `tools/refactor_accelerator/`)
4. **Wave 4**: Restore archived pre-commit hooks + CI workflows from git history

Each wave is independently rollbackable.

---

## Acceptance Criteria

| Metric | Target | Verification |
|--------|--------|-------------|
| **Tier 1 — Hard Gates** | | |
| Pre-hook blocks PowerShell | 100% blocked (exit 2) | `pytest test_pre_run_gate.py -q` |
| Pre-hook blocks syntax errors | 100% blocked (exit 2) | `pytest test_pre_write_gate.py -q` |
| Pre-hook blocks MCP config edits | Protected files exit 2 | `pytest test_pre_write_gate.py -q` |
| Pre-hook blocks locked SQLite | ADG calls blocked | `pytest test_pre_mcp_gate.py -q` |
| **Tier 1 — Advisory** | | |
| Post-hooks never block | All exit 0 | `pytest test_post_*_audit.py -q` |
| Post-hook telemetry | MCP calls + PIDs logged | Audit log files exist |
| Graceful degradation | Malformed JSON → exit 0 | Test cases in all hook tests |
| No hardcoded paths | 0 literal paths | `grep -rn "C:\\\|/Users/" ops_scripts/hooks/windsurf/` = 0 |
| **Tier 2 — Policy** | | |
| Rules valid triggers | 11/11 valid modes | Cascade Customizations panel |
| SSOT dedup | 0 enforcement duplicates | governance-enforcement-table.md audit |
| Approval classes | ALLOW/DENY/REQUIRE_APPROVAL/ESCALATE | Policy doc review |
| MCP Registry | 14 MCPs documented | `docs/reference/MCP_Registry.md` exists |
| HITL ⭐ calibration | All cite target-state attributes | `grep "target-state" hitl-enforcement.md` |
| Column 5 vocabulary | In constitutional §8 | `grep "Column 5" constitutional.md` |
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
