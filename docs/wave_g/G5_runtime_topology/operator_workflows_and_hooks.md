# G5 — Operator Workflows, Hooks, and Runtime Posture Gates

wave: G5
produced_at: 2026-04-18
adg_snapshot: artifacts/adg/adg_indexed_04182026_0814.sqlite
upstream_artefacts:
  - .windsurf/hooks.json
  - .windsurf/workflows/*.md
  - .github/workflows/*.yml
  - .pre-commit-config.yaml

ADG snapshot timestamp used: `04182026_0814`.

## 1) Windsurf hooks that directly alter runtime posture

From `.windsurf/hooks.json`:

- `pre_run_command` → `.windsurf/scripts/pre_run_gate.py`
  - blocks PowerShell invocation and full-suite misuse in repair mode.
- `pre_write_code` → `.windsurf/scripts/pre_write_gate.py`
  - write-time governance gate.
- `pre_mcp_tool_use` → `.windsurf/scripts/pre_mcp_gate.py`
  - MCP invocation policy gate.
- `pre_user_prompt` → `.windsurf/scripts/pre_prompt_classifier.py`
  - tier classification and routing guardrails.
- `post_write_code` → `.windsurf/scripts/post_write_audit.py`, `.windsurf/scripts/post_write_mcp_config_sync.py`
  - write audit + MCP config propagation.
- `post_run_command` / `post_mcp_tool_use` / `post_cursor_agent_response`
  - audit/cleanup and ADG-first retroactive detection (`post_cursor_agent_adg_audit.py`).

## 2) Operator workflows with runtime impact

High runtime-impact workflows in `.windsurf/workflows/`:

- `/adg-redis-refresh`
  - canonical ADG refresh pipeline (staleness check, regenerate, Redis ingest, verify hot).
- `/adg-repair-loop`
  - ADG-scoped repair loop with strict staged testing semantics.
- `/mcp-failure-rca`
  - MCP failure-domain diagnosis and recovery workflow.
- `/adg-timeout-recovery`
  - timeout-aware recovery path for ADG-related operations.
- `/memory-purge-sync`
  - memory lifecycle cleanup + re-import path affecting persistent memory runtime context.
- `/progress-display-enforcement` and `/timeout-progress-enforcement`
  - operator/runtime execution ergonomics and bounded execution safeguards.

## 3) CI workflows affecting live/runtime posture assumptions

From `.github/workflows/`:

- `adg-ci-gates.yml`
  - provisions Redis service container, ingests ADG, runs staleness guard and MCP contract tests.
- `guardian-tests.yml`
  - enforces guardian contract and sovereignty boundaries.
- `infra_wiring_check.yml`
  - requires infra wiring compliance score at 100%.
- `pytest-config-ssot.yml`
  - prevents pytest configuration drift from SSOT.

These are CI-trigger surfaces (not always-on local daemons) but materially shape what runtime states are admissible.

## 4) Pre-commit/runtime-adjacent gate surfaces

From `.pre-commit-config.yaml`:

- Python syntax validation gate (`py_compile`).
- Formatting + guardian auto-fix stage.
- Pytest SSOT strict validation stage.
- Manual-only gates: ADG staleness guard and C0 sovereignty.

These do not run as runtime daemons, but gate the deployable state that reaches runtime.

## 5) Bootstrap and launcher scripts with runtime effects

- `.windsurf/scripts/filesystem_mcp_launcher.js`
  - Node wrapper for filesystem MCP with startup watchdog and deterministic cleanup.
- `.windsurf/scripts/sync_mcp_config.py`
  - config sync path that can change global MCP launch behavior.
- `ops_scripts/dev_tools/start_metrics_sidecar.py`
  - optional observability sidecar (`:8000/metrics`) for live monitoring.

## 6) Operator-managed versus repo-managed boundaries

- Repo-managed surfaces:
  - Python MCP server entrypoints under `tools/mcp/`, `tools/adg/mcp/`, `tools/memory/`, `tools/otel/`.
  - workflows/hooks/scripts in `.windsurf/` and `ops_scripts/`.
- Operator-managed surfaces:
  - local Redis daemon lifecycle,
  - external endpoint availability (DeepWiki, Notion API, provider APIs),
  - GitKraken binary auth and process behavior.

## 7) Highest-impact operator actions

1. Running `/adg-redis-refresh` after structural changes.
2. Verifying snapshot alignment (`adg_status` vs Redis hot sentinel timestamp).
3. Checking `otel_server_info.source_is_stale` before restarting otel MCP.
4. Treating high-risk per-call kill-switches from G4b as controlled operations.
5. Avoiding silent fallback pathways in dependency analysis (ADG-first enforcement chain).
