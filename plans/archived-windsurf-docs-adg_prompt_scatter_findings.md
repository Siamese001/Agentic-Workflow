---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\adg_prompt_scatter_findings.md'
original_relative_path: 'adg_prompt_scatter_findings.md'
source_sha256: 0a2c393125f6784e465eb64c3812b71bee77ba29d244326c0c281dcabbc928d6
recovered_status: LOST_RECOVERED
last_commit: 'fd8afcb3494'
last_commit_date: '2026-04-11 11:10:04 -0400'
created_date: '2026-04-11'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Prompt Scatter Findings
**Stage 1 Discovery — Scan-only, no code changes**
**Date:** 2026-04-11 | **ADG Snapshot:** `04102026_1817`

---

## 1. Definition: Prompt Scatter

**Prompt scatter** is any occurrence where a module constructs, assembles, or dispatches a prompt string, prompt dict, or prompt slot **outside** the canonical `tools/adg/prompt_assembly` pipeline and its `PacketRegistry`. This includes:

- Hard-coded prompt strings in non-PA modules
- Ad hoc `build_prompt()` / `format_prompt()` / `system_message=` patterns outside L_PG
- Direct LLM calls with inline system/user blocks not routed through a `PromptEnvelope`
- Modules generating `S0`/`D0`/`I0`/`C0`/`U0` slots without going through the `PacketRegistry`

---

## 2. Confirmed: No Scatter Within the PA Package Itself

The `tools/adg/prompt_assembly/` package enforces the no-scatter invariant correctly:

- **All 8 packet types are registered in `packets/registry.py`** — no inline template strings found outside registry
- **`cli.py` dispatches exclusively via `build_packet(packet_type)`** — no ad hoc packet construction
- **Shared policy block (`_SHARED_POLICY`)** is defined once in `registry.py` and referenced by all 8 templates — no per-template policy drift found
- **README explicitly states:** "No prompt scatter: all packet types go through a central `PacketRegistry`. Ad hoc prompt construction in calling code is a violation."
- **`evidence_shaper.py`** never appends raw strings to a prompt — operates only on typed `EvidenceItem` / `EvidenceBundle`

**CONFIRMED CLEAN — within PA package boundary.**

---

## 3. Prompt Scatter Findings: ADG Governance Plane

### Finding 1: `generates_prompt` — 39 Edges Across 39+ Modules

The ADG snapshot (04102026_1817) shows **39 `generates_prompt` edges** and **41 `consumes_prompt` edges** across the `L_PG` layer (122 modules) and other layers.

These edges are **tracked in the governance graph** (`adg_governance_graph_<ts>.json`) and are scanned by `agentic_core/adg/extraction/visitors/lifecycle_advanced.py` (E20 — `_PromptSlotVisitor`).

**Known scatter risk:** Any module outside `L_PG` that calls a `PromptAssembler` or `get_prompt()` function emits a `generates_prompt` or `consumes_prompt` edge. The ADG graph **tracks but does not block** these.

**Status:** TRACKED, not blocked at CI level. `prompt_authority.py` (E21) detects violations but its output is a report, not a hard exit gate.

---

### Finding 2: Two Disconnected Prompt Assembly Subsystems

This is the most significant structural scatter finding:

| Subsystem | Location | Purpose | Connected? |
|-----------|----------|---------|------------|
| **Tool-layer PA** | `tools/adg/prompt_assembly/` | ADG-output packet building for analyst use | CLI only |
| **Runtime PA** | `agentic_core/L3_orchestration/types/c0_evidence_contract_types.py` + `agentic_core/prompt_governance/` | Live C0→PA→L2 pipeline | Not wired to tool-layer PA |

The `C0EvidenceContract` exists in L3 as the mandatory contract between C0 retrieval and a prompt assembler. The `tools/adg/prompt_assembly` adapters fetch directly from ADG artifact files (SQLite, JSON). **There is no bridge**. Any runtime prompt construction in `agentic_core/` is functionally invisible to the `PacketRegistry` and vice versa.

**Status:** ARCHITECTURAL GAP — two distinct prompt assembly surfaces with no shared contract.

---

### Finding 3: `prompt_governance` Layer (L_PG) Has 122 Modules — No Inventory Reviewed

The snapshot reports `L_PG: 122` modules. These are the canonical location for prompt governance code. None of these modules were fully inventoried in this scan. They may contain:

- Additional `PromptAssembler` implementations
- Slot type registrations
- Additional packet templates outside `PacketRegistry`

**Status:** UNCONFIRMED — requires follow-up scan of all L_PG module paths.

---

### Finding 4: `phase_b_capability_tool_task.py` References `generates_prompt` Edges

`tools/generate/materialized_views/phase_b_capability_tool_task.py` (5 references) consumes `generates_prompt` edges as part of its materialized view. This module processes prompt governance data but produces a structured view — not an ad hoc prompt. It does not construct any `PromptEnvelope`.

**Status:** FALSE POSITIVE — structural consumer of graph edges, not scatter.

---

### Finding 5: `adg_redis_live_query.py` Queries `generates_prompt` / `consumes_prompt` via Redis

`tools/adg/queries/adg_redis_live_query.py` scans Redis for `generates_prompt` and `consumes_prompt` edges. This is a read-only analysis query — it does not construct prompts.

**Status:** FALSE POSITIVE — analysis query, not scatter.

---

### Finding 6: `ops_scripts/archives/orphaned/graphdb_p2p3_watch.py` — Orphaned Reference

One match for `generates_prompt` found in an archived/orphaned file. Not in production code path.

**Status:** ARCHIVED — not a scatter risk.

---

## 4. Prompt Scatter Risk Register

| Risk | Location | Severity | Confirmed? |
|------|----------|---------|------------|
| Two disconnected PA subsystems (tool-layer vs. runtime) | `tools/adg/prompt_assembly/` vs `agentic_core/L3_orchestration/` | **HIGH** | Confirmed |
| 122 `L_PG` modules not fully inventoried | `agentic_core/prompt_governance/` (inferred) | **MEDIUM** | Partially confirmed |
| `generates_prompt` / `consumes_prompt` violations not hard-blocked at CI | `prompt_authority.py` E21 output is a report only | **MEDIUM** | Confirmed |
| No `PromptEnvelope` ever written to `artifacts/adg/packets/` | Directory exists but is empty | **LOW** | Confirmed |
| `adg_align_query*.py` ad hoc SQL queries against L_PG nodes | Multiple query scripts in `tools/adg/queries/` | **LOW** | Confirmed — dev use only |

---

## 5. Where a Prompt Assembly Hook Should Connect

Based on the above findings, the following integration points are where a prompt assembly layer should hook in to close the scatter gap:

### Hook Point 1: C0 → PA Bridge

**Location:** Between `C0EvidenceContract` (at `agentic_core/L3_orchestration/types/`) and the `PromptEnvelope` builder in `tools/adg/prompt_assembly/packets/builders.py`.

**What is missing:** A translation adapter that:
- Accepts `C0EvidenceContract.cited_spans` as input
- Maps them to `EvidenceItem` objects (matching `SourceType` from `contracts.py`)
- Feeds them into the evidence shaper → packet builder pipeline

**Boundary rule (from `README.md`):** "C0 retrieves only, prompt assembly packages only" — this bridge must live at the L3/tool boundary, not inside either subsystem.

### Hook Point 2: PacketRegistry → Runtime Dispatch

**Location:** Between `packets/builders.py:build_packet()` and the L2 execution agent receiving a signed packet.

**What is missing:** A serialization/dispatch path that:
- Writes `PromptEnvelope` (already structured with `replay_metadata`) to a known artifact or message channel
- Is consumed by L2 rather than discarded after CLI run

**Note:** The `replay_metadata` block in `PromptEnvelope` is already designed for deterministic re-execution — it expects `snapshot_id`, `commit_sha`, `artifact_digests`. This infrastructure is ready; the dispatch call is not.

### Hook Point 3: Prompt Authority Gate → CI Hard Block

**Location:** `prompt_authority.py` (E21) output → `ops_scripts/ci/_adg_ci_gates.py` or `gate_p0_*.py`

**What is missing:** A gate that reads `PromptAuthorityReport.violation_count > 0` and fails the CI run (analogous to how `_check_p0_violations` exits 1 on layer violations). Currently E21 only reports; it does not block.

---

## 6. No Prompt Scatter Found in These Areas

| Area | Evidence |
|------|---------|
| `L0_routing/` | No `generates_prompt` imports found; routes to PA rather than building prompts |
| `L2_execution/` | No `PromptEnvelope` or `build_packet` imports confirmed |
| `L5_safety/` | No prompt construction found — consumes sealed work, not raw prompts |
| `L6_shadow/` | Ingests traces, not prompts |
| `ops_scripts/ci/adg_gates/` | Gate modules read ADG artifacts, do not construct prompts |
| `tools/generate/reporting/` | Produces JSON reports and burndown tables, not prompts |

---

## 7. Summary: What Is Clean, What Is Not

### CLEAN (confirmed no scatter)
- `tools/adg/prompt_assembly/` internal package — all 8 types through `PacketRegistry`
- All CI gate modules in `ops_scripts/ci/adg_gates/`
- All report-generation modules in `tools/generate/reporting/`
- `tools/generate/validation/gates.py` — consumes ADG, does not build prompts

### NOT CLEAN (scatter or gap found)
- **Two disconnected prompt assembly subsystems** — tool-layer PA vs. runtime C0→PA — no integration bridge
- **`L_PG` layer (122 modules) not fully audited** — potential hidden scatter
- **`prompt_authority.py` E21** — reports authority violations but does not hard-block at CI
- **`artifacts/adg/packets/`** — empty; no `PromptEnvelope` ever emitted to disk at generation time, meaning no packet is available for L2 runtime pickup

### INFERRED RISK (not confirmed, requires deeper scan)
- Any module in `agentic_core/prompt_governance/` that builds prompt strings without routing through `PacketRegistry`
- Any agent in `L3_orchestration/` that calls LLM APIs with inline system messages not tracked by E20 visitor
