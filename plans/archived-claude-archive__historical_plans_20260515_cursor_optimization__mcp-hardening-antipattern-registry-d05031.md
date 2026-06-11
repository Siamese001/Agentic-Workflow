---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\mcp-hardening-antipattern-registry-d05031.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\mcp-hardening-antipattern-registry-d05031.md'
source_sha256: 32d1008d326227b0bad95639a03b5e928257ed2f2815f231a16725ddce030f5b
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# MCP Config + Antipattern Registry Hardening

Harden the Windsurf MCP global config (secret extraction, profile tagging, `enabled` gating) and rewrite `antipattern_registry.py` into a clean 3-file split with a forensic record model and deterministic IDs, then update affected tests.

---

## Exposed Secrets — Rotate Before Anything Else (P0, your action)

The following credentials are **live** in `~/.codeium/windsurf/mcp_config.json` and must be rotated **now**, before any other work:

| Secret | Location | Action |
|---|---|---|
| `BSAr2wedArAn5uzkoHBpQegHvaEfPxZ` | `brave-search.env.BRAVE_API_KEY` | Rotate at brave.com |
| `github_pat_11BP7NBKQ07p…` | `github.env.GITHUB_PERSONAL_ACCESS_TOKEN` | Revoke at github.com/settings/tokens |
| `figd_ilNTaaCNfcZvO_LzBUgWOaRowYqTcgBzjUj2e-XG` | `figma.args[3]` | Revoke at figma.com/settings |
| `postgresql://postgres:postgres@localhost:5432/mcp_db` | `postgres_memory.args[2]` | Rotate local DB password |

Note: `.env` also contains live OpenAI, Anthropic, Pinecone, GitHub keys — confirm `.env` is in `.gitignore` and not committed.

---

## Wave 1 — MCP Config Hardening

**Scope:** `~/.codeium/windsurf/mcp_config.json` (global Windsurf config)
**Tier:** T1 — single file, config-only

### Changes

1. **All secrets → `${ENV_VAR}` references**
   - `BRAVE_API_KEY` → `${BRAVE_API_KEY}`
   - `GITHUB_PERSONAL_ACCESS_TOKEN` → `${GITHUB_PERSONAL_ACCESS_TOKEN}`
   - Figma key → move from `args` into `env.FIGMA_API_KEY` → `${FIGMA_API_KEY}`
   - Postgres DSN → `${POSTGRES_MCP_URL}`

2. **Profile tagging + `disabled` gate on high-risk servers**
   Each server gains a `"profile"` field:

   | Profile | Servers | Default |
   |---|---|---|
   | `core` | gitkraken, filesystem, memory, redis | enabled |
   | `network` | brave_search, deepwiki, fetch | disabled |
   | `browser` | playwright | disabled |
   | `repo_admin` | github | disabled |
   | `design` | figma | disabled |
   | `state` | postgres_memory | disabled |

3. **Structural fixes**
   - `deepwiki`: remove empty `"command": ""` — keep `url` only (remote MCP mode)
   - `FIGMA_TEAM_ID` placeholder → `${FIGMA_TEAM_ID}` with explicit comment
   - `playwright`: add comment noting overlap with `browser`; only one per session
   - `gitkraken`: add `# host-specific path` comment

4. **Pin `npx` package versions**
   - `@modelcontextprotocol/server-brave-search` → `@0.6.2`
   - `@modelcontextprotocol/server-filesystem` → `@0.6.2`
   - `@modelcontextprotocol/server-github` → `@0.6.2`
   - `@modelcontextprotocol/server-fetch` → `@0.6.2`
   - `@executeautomation/playwright-mcp-server` → `@1.0.5`
   - Others: pin at implementation time via npm; mark `# TODO: pin` if unavailable

**File edited:** `~/.codeium/windsurf/mcp_config.json`

---

## Wave 2 — Antipattern Registry 3-File Split

**Scope:** `agentic_core/adg/runtime/`
**Tier:** T2 — 2-3 files, single layer

### File 1: `antipattern_types.py` (new)

Pure data — zero side effects, zero `lifecycle_trace_contract` imports.

- `AntipatternSeverity` enum (moved from registry)
- `AntipatternCategory` enum (existing 14 + 17 new MCP-specific categories)
- `_SEVERITY_MAP` dict (existing + new entries)
- `SuppressionRecord` dataclass: `reason`, `reviewer`, `ticket`, `suppressed_at`
- `AntipatternRecord` dataclass — hardened fields:
  - `schema_version: str = "2.0"`
  - `fingerprint: str` — stable SHA-256 of `(run_id, source_file, line_start, symbol, category)`
  - `record_id: str` — derived from fingerprint prefix (no `uuid4()`)
  - `category`, `severity`, `source_file`, `line_start`, `line_end`, `column_start`
  - `symbol`, `rule_id`, `scanner`, `evidence_hash`
  - `suppression: SuppressionRecord | None = None`
  - `remediation_status: str = "open"`
  - `agent_id`, `run_id`, `description`
  - `to_dict()` (pure)
- `AntipatternRegistryReport` dataclass — all `@property` accessors pure (no emit calls)

### New MCP-specific categories

```
SECRET_IN_EDITOR_CONFIG       (critical)
UNPINNED_MCP_PACKAGE          (high)
DEFAULT_LOCAL_DB_CREDENTIALS  (critical)
OVERBROAD_FILESYSTEM_ROOT     (high)
REDUNDANT_CAPABILITY_OVERLAP  (medium)
REMOTE_MCP_WITHOUT_EXPLICIT_MODE (medium)
MACHINE_SPECIFIC_ABSOLUTE_EXECUTABLE_PATH (medium)
PLACEHOLDER_VALUE_IN_LIVE_CONFIG (low)
NETWORK_TOOL_WITHOUT_EGRESS_POLICY (high)
MIXED_MUTATION_AND_EXFILTRATION_SURFACE (critical)
IMPORT_TIME_SIDE_EFFECT       (critical)
READ_ACCESSOR_WITH_SIDE_EFFECT (high)
NONDETERMINISTIC_ID_GENERATION (critical)
DOMAIN_MODEL_COUPLED_TO_TELEMETRY (high)
SUPPRESSION_WITHOUT_REASON    (medium)
UNBOUNDED_REGISTRY_GROWTH     (medium)
EXACT_MATCH_ONLY_CLASSIFIER   (low)
```

### File 2: `antipattern_registry.py` (rewrite in-place)

Pure registry — no `lifecycle_trace_contract` imports.

- Imports only `antipattern_types` + stdlib (`threading`, `hashlib`)
- `AntipatternRegistry`:
  - `threading.Lock` for append safety
  - `register()` — computes deterministic fingerprint, deduplicates by fingerprint
  - `suppress(record, reason, reviewer="", ticket="")` — populates `SuppressionRecord`
  - `classify()` — exact match + normalized alias fallback
  - `register_from_edge_kind()`
  - `snapshot()` — returns thread-safe copy of report
- Re-exports `AntipatternRecord`, `AntipatternCategory`, `AntipatternSeverity`, `AntipatternRegistryReport` for backward compatibility

### File 3: `antipattern_telemetry.py` (new)

Optional adapter — all `lifecycle_trace_contract` imports live here only; never called on import.

- `AntipatternTelemetryAdapter` class
- `emit_registration(record)` — wraps `_emit_records_execution_trace`
- `emit_report(report)` — wraps metric emitters
- Zero module-level side-effecting calls

**Files created/edited:**
- `agentic_core/adg/runtime/antipattern_types.py` (new)
- `agentic_core/adg/runtime/antipattern_registry.py` (rewrite)
- `agentic_core/adg/runtime/antipattern_telemetry.py` (new)

---

## Wave 3 — Test Updates

**Scope:** `tests/unit/agentic_core/adg/runtime/`
**Tier:** T1-T2

### Updates

1. **`test_antipattern_registry_adg.py`** — verify proxy re-exports from `agentic_core.__init__` still resolve after split (no logic changes expected)

2. **New: `test_antipattern_registry_hardened.py`**

   | Test | Assertion |
   |---|---|
   | `test_fingerprint_is_deterministic` | Same inputs → identical fingerprint |
   | `test_fingerprint_no_uuid4` | Fingerprint is hex, not UUID format |
   | `test_register_deduplicates` | Same pattern registered twice → 1 record |
   | `test_by_category_is_pure` | `by_category` called N times → no state growth |
   | `test_suppress_requires_reason` | `suppress(record)` without reason raises `ValueError` |
   | `test_registry_thread_safe` | 50 concurrent `register()` calls → correct count |
   | `test_no_lifecycle_trace_on_import` | Import `antipattern_registry` → `lifecycle_trace_contract` absent from `sys.modules` |
   | `test_mcp_categories_in_severity_map` | All 17 new MCP categories present in `_SEVERITY_MAP` |

---

## Out of Scope

- Secret rotation itself (manual — see table above)
- `config/mcp_servers.yaml` YAML SSOT sync (separate `/mcp-config-sync` workflow)
- Guardian exemption ratchet updates
- ADG regeneration

## Assumptions

- `.env` is gitignored (verify manually)
- `agentic_core/__init__.py` re-exports `AntipatternRegistry` — will update re-export to point at new file (same public API)
- The existing `_emit_*` calls are pure `logger.debug()` — removing them has zero behavioral effect
- Windsurf reads `~/.codeium/windsurf/mcp_config.json` for `${ENV_VAR}` substitution from the OS environment
