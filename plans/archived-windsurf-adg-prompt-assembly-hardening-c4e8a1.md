---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\adg-prompt-assembly-hardening-c4e8a1.md'
original_relative_path: 'adg-prompt-assembly-hardening-c4e8a1.md'
source_sha256: b7a0dcb86437b2b5d30e3a6d83904c74525a2102eb06c186fc29f3a799bd1692
recovered_status: LOST_RECOVERED
last_commit: '6477883502e'
last_commit_date: '2026-04-27 08:55:24 -0400'
created_date: '2026-04-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ADG Prompt Assembly Hardening — Stage 1 Design Package

**Plan ID**: `adg-prompt-assembly-hardening-c4e8a1`
**Tier**: T3 — Architectural (new subsystem, cross-layer, >10 files)
**Status**: STAGE 1 — AWAITING APPROVAL

---

## 1. Executive Summary

This design introduces a **prompt assembly layer for ADG results** — a structured subsystem that converts raw ADG canonical outputs (SQLite, JSON reports, graph DB queries, infra wiring findings, P0–P3 gate outputs) into **grounded, deterministic, contradiction-aware, token-budgeted PromptEnvelope packets**.

The layer is strictly separated from C0 retrieval (which fetches/shapes evidence) and from L0–L2 execution (which consumes packets). It lives in `tools/adg/prompt_assembly/` as a tooling-layer subsystem that:

- Consumes shaped evidence from retrieval adapters (C0-side)
- Assembles typed prompt packets using shared templates and contracts
- Preserves contradictions, gaps, and weak support explicitly
- Budgets tokens deterministically
- Emits bounded `PromptEnvelope` artifacts (JSON/Markdown)
- Never retrieves, routes, or executes

### Wave Summary

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|-----------------|
| W1 | P1-P3 | Contracts + Core Types | ~8K | Schema stable | PLANNED | Types compile, tests pass |
| W2 | P4-P5 | Retrieval Adapters + Evidence Shaping | ~12K | SQLite/JSON accessible | PLANNED | All 6 artifact types loadable |
| W3 | P6-P7 | Packet Builders + Token Budgeter | ~15K | Contracts from W1 | PLANNED | 8 packet families build correctly |
| W4 | P8-P9 | CLI + Triggers + Tests | ~10K | Builders from W3 | PLANNED | CLI runs, 100% contract coverage |
| W5 | P10 | Docs + Integration Verification | ~5K | All waves green | PLANNED | No regressions, docs complete |

### Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| P1 | Evidence Contract types | 1 file | None | 2K | PLANNED |
| P2 | PromptEnvelope + Status types | 1 file | None | 2K | PLANNED |
| P3 | Packet Registry + Template types | 2 files | Template slot ordering | 4K | PLANNED |
| P4 | Retrieval Adapters (6 sources) | 1 file | SQLite schema drift | 5K | PLANNED |
| P5 | Evidence Shaper | 1 file | Contradiction logic | 7K | PLANNED |
| P6 | Packet Builders (8 families) | 1 file | Must-use vs optional rules | 10K | PLANNED |
| P7 | Token Budgeter | 1 file | Overflow strategies | 5K | PLANNED |
| P8 | CLI entrypoint | 1 file | Arg parsing | 4K | PLANNED |
| P9 | Tests | 1 file | Determinism assertions | 6K | PLANNED |
| P10 | Docs + Integration | 2 files | None | 5K | PLANNED |

---

## 2. Current-State Analysis

### 2.1 Canonical ADG Artifact Surfaces

The ADG generation pipeline (`tools/generate/generate_full_adg.py`) produces a 5-file canonical output set per run:

| Artifact | Path Pattern | Format | Content |
|----------|-------------|--------|---------|
| **Snapshot** | `artifacts/adg/adg_snapshot_<ts>.json` | JSON | Metrics, graph_plane_counts, by_layer, blind_spots, commit_sha, counts |
| **SQLite DB** | `artifacts/adg/adg_indexed_<ts>.sqlite` | SQLite | Full queryable store: nodes, edges, violations tables; 18 edge types |
| **Provenance Report** | `artifacts/adg/provenance_report_<ts>.json` | JSON | Digests, reconciliation (db_nodes vs report_nodes), validation flags |
| **Closure Report** | `artifacts/adg/closure_validation_report_<ts>.json` | JSON | 12+ closure rows: structural coverage, governance visibility, determinism, edge precision |
| **Edge Density Report** | `artifacts/adg/edge_density_report_<ts>.json` | JSON | Edge distribution counts, critical edge coverage |
| **Layer Coverage Report** | `artifacts/adg/layer_coverage_report_<ts>.json` | JSON | Layer distribution, unknown modules list, coverage percentage |
| **Burndown Table** | `artifacts/adg/adg_burndown_table.json` | JSON | P0-P3 counts by class (hygiene, structural, agentic) |
| **P1/P2 Ratchets** | `artifacts/adg/p1_ratchet.json`, `p2_ratchet.json` | JSON | Ceiling values for ratchet enforcement |
| **Repair Log** | `artifacts/adg/repair_log_<ts>.json` | JSON | Repair orchestrator event trail |
| **SC/AP Config** | `artifacts/adg/sc_ap_config.json` | JSON | Structural conformance + anti-pattern rule enable/audit states |
| **Graph Snap** | `artifacts/adg/adg_graphsnap_<ts>.json` | JSON | Previous-run snapshot for E7 drift detection |

### 2.2 Post-Generation Augmentation Surfaces

| Surface | Location | Purpose |
|---------|----------|---------|
| **Structural Outputs** | `tools/adg/structural_outputs.py` | Burndown, blast radius, seam detection, centrality (reads SQLite) |
| **Refactor Accelerator** | `tools/adg/refactor_accelerator.py` | Ranked refactoring candidates by composite score (reads SQLite + git churn) |
| **Infra Wiring Views** | `tools/generate/infra_wiring_views.py` | Materializes SQL views detecting infra wiring violations |
| **Infra Wiring Scan** | `ops_scripts/ci/infra_wiring_scan.py` | Scans forbidden direct imports in production layers |
| **Infra Wiring Postprocess** | `ops_scripts/ci/infra_wiring_postprocess.py` | Filters false positives from infra wiring view results |
| **Graph DB** | `tools/graphdb/` | NetworkX projection: analyst queries, blast radius, historical diff, structural queries |
| **ADG MCP Server** | `tools/adg/mcp/server.py` | MCP interface for ADG queries (node, edge fanout/fanin, nodes by layer/file) |

### 2.3 P0–P3 Gating and Ratchet Surfaces

| Gate | Location | What It Checks |
|------|----------|---------------|
| **P0 Violations** | `tools/generate/validation/gates.py::_check_p0_violations` | Layer violations (hard fail) |
| **P0 Structural** | `tools/generate/validation/gates.py::_check_structural_conformance` | Structural conformance rules SC-1 through SC-8 |
| **P0 Anti-patterns** | `tools/generate/validation/gates.py::_check_agentic_antipatterns` | Agentic anti-patterns AP-1 through AP-17 |
| **P1 Ratchet** | `tools/generate/validation/gates.py::_check_p1_ratchet` | High-severity ceiling enforcement |
| **P2 Ratchet** | `tools/generate/validation/gates.py::_check_p2_ratchet` | Medium-severity ceiling enforcement |
| **CI Delta Gates** | `ops_scripts/ci/_adg_ci_gates.py` | M1–M6 delta enforcement (determinism, dispatch, mutation, guardrail, trace, replay) |
| **CI Lane Gate** | `tools/adg/adg_ci_lane_gate.py` | Test bucket contracts (unit_strict, degraded_path, integration_infra) |

### 2.4 Existing Prompt/Template Surfaces

| Surface | Location | Relevance |
|---------|----------|-----------|
| **Prompt Template Manager** | `agentic_core/L1_cognition/reasoning/prompt_template_manager.py` | RAG prompt templates — **NOT** ADG result packetization. L1-scoped. |
| **Prompt Authority DAG** | `agentic_core/adg/analysis/prompt_authority.py` | Detects prompt slot authority violations (S0>D0>I0>C0>U0). Analysis tool, not assembly. |
| **Prompt Drift Detector** | `agentic_core/adg/analysis/prompt_drift_config.py` | Detects prompt governance changes across snapshots. Analysis tool. |
| **Prompt Impact Analyzer** | `agentic_core/adg/applications/prompt_impact.py` | Blast radius for prompt template changes. Analysis tool. |
| **ADG Schema** | `agentic_core/adg/contracts/schema.py` | Defines `prompt_slot`, `prompt_template`, `prompt_assembly` entity types |
| **SC-7 Config** | `artifacts/adg/sc_ap_config.json` | "SC-7: Grounding contract / C0-PA separation" — already recognized as a conformance rule |

### 2.5 Key Finding: No PromptEnvelope or Packet System Exists

**There is no `PromptEnvelope`, `PromptPacket`, or structured ADG result packet type anywhere in the repo.** The ADG analysis tools (prompt_authority, prompt_drift, prompt_impact) analyze prompt *governance* edges in the graph — they do not assemble ADG *results* into bounded prompt packets.

The existing `PromptTemplate` in L1 is a RAG-focused template for generation tasks, not an ADG result packetization system.

### 2.6 Ad Hoc Prompt Scatter Assessment

**AP-12 ("Prompt scatter")** is already a recognized anti-pattern in `sc_ap_config.json`. Currently in `audit_mode: true`. No formal packetization contracts enforce it for ADG results.

Current ADG result presentation is:
- Raw JSON reports printed to terminal (`_print_defect_table`)
- Raw SQLite queries via MCP or manual tools
- Unstructured markdown in evidence files
- No shared packet contracts between consumers

### 2.7 ADG Result Consumers Inventory

| Consumer | Access Pattern | Current Format |
|----------|---------------|---------------|
| **CLI user** (developer) | `python tools/generate/generate_full_adg.py` | Terminal print, raw JSON files |
| **Analyst** (Cascade/agent) | MCP tools (`mcp1_adg_*`) | Raw SQLite rows, node/edge dicts |
| **PR review** | CI gates (`_adg_ci_gates.py`) | Exit codes, stderr messages |
| **Repair workflow** | `tools/adg/repair/repair_orchestrator.py` | Repair log JSON |
| **Ratchet review** | `_check_p1_ratchet`, `_check_p2_ratchet` | Pass/fail with ceiling delta |
| **Graph investigation** | `tools/graphdb/queries/analyst.py` | NetworkX dicts |
| **Infra wiring review** | `infra_wiring_views.py`, `infra_wiring_postprocess.py` | SQL view results |
| **Structural analysis** | `tools/adg/structural_outputs.py` | JSON dicts (burndown, blast radius, seams, centrality) |

---

## 3. Retrieval and Evidence Shaping Design

### 3.1 Retrieval Adapter Design

Retrieval adapters live on the C0 side — they fetch raw data from canonical sources and return typed `EvidenceBundle` objects. Prompt assembly **never** calls SQLite/JSON/graph DB directly.

```
tools/adg/prompt_assembly/
    retrieval/
        __init__.py
        adapters.py          # All retrieval adapters
    ...
```

**Six retrieval adapters**:

| Adapter | Source | Returns |
|---------|--------|---------|
| `SQLiteAdapter` | `adg_indexed_<ts>.sqlite` | Node/edge/violation rows by query |
| `ReportAdapter` | `*_report_<ts>.json`, `adg_snapshot_<ts>.json` | Parsed report dicts with provenance |
| `RatchetAdapter` | `p1_ratchet.json`, `p2_ratchet.json`, `adg_burndown_table.json` | Ratchet ceilings, burndown data |
| `GraphDBAdapter` | `tools/graphdb/` NetworkX queries | Blast radius, paths, neighborhoods (tagged as derived) |
| `InfraWiringAdapter` | Infra wiring SQL views in SQLite | Violation rows, approved/miswired surfaces |
| `StructuralAdapter` | `tools/adg/structural_outputs.py` functions | Burndown, blast radius, seams, centrality dicts |

Each adapter returns an `EvidenceBundle`:

```python
@dataclass
class EvidenceItem:
    source_artifact: str          # e.g. "adg_indexed_04082026_1914.sqlite"
    source_type: str              # "sqlite" | "json_report" | "graph_db" | "infra_view"
    snapshot_id: str              # timestamp
    commit_sha: str
    artifact_digest: str
    row_references: list[str]     # row IDs, paths, or line numbers
    support_score: float          # 0.0–1.0
    is_derived: bool              # True for graph DB results
    data: dict                    # the actual evidence payload

@dataclass
class EvidenceBundle:
    items: list[EvidenceItem]
    coverage_score: float
    contradiction_status: str     # "none" | "minor" | "major"
    contradictions: list[dict]    # explicit disagreements
    gaps: list[str]               # missing data descriptions
    freshness: str                # ISO timestamp
    weak_support: bool            # True if coverage_score < 0.5
```

### 3.2 Evidence Shaping Pipeline

Before evidence reaches packet builders, the shaper applies these steps:

1. **Dedupe** — remove duplicate rows/findings across sources
2. **Normalize** — unify field names (e.g. `source_file` vs `file_path`)
3. **Reconcile** — cross-check DB counts vs report counts (tag mismatches)
4. **Contradiction Retain** — if DB says 65708 nodes but report says 65682, preserve both with a `ContradictionFlag`
5. **Provenance Preserve** — every evidence item carries its source artifact, digest, and row reference
6. **Citation** — annotate with `cited_span` (file:line) or `row_ref` (table:rowid)
7. **Support/Coverage/Gap** — compute coverage score, identify gaps, flag weak support

### 3.3 Contradiction Handling Rules

| Contradiction Type | Example | Handling |
|-------------------|---------|----------|
| Node count mismatch | DB 65708 ≠ report 65682 | Preserve both; `contradiction_status: "major"`; flag in packet |
| Digest mismatch | artifact_digest changed between runs | Preserve both digests; note in provenance |
| Critical edge coverage mismatch | Report says 14.28% but graph shows richer coverage | Preserve disagreement; annotate source authority |
| Report schema vs graph richness | Report covers 7 closure rows; graph has 60+ edge types | Note as `gap: "report_schema_narrower_than_graph"` |
| Validation `false` fields | `has_artifact_digest: false` in provenance report | Preserve as weakness; `weak_support: true` |

### 3.4 Abstain/Refine Behavior

When evidence is insufficient:
- `coverage_score < 0.3` → packet builder emits `abstain: true` with `refine_suggestion`
- Missing canonical artifact → adapter returns empty bundle with `gap: "artifact_missing"`
- Graph DB unavailable → proceed without derived evidence; note `augmentation_available: false`

---

## 4. Prompt Contract Design

### 4.1 PromptEnvelope Contract

```python
@dataclass
class PromptEnvelope:
    # Header
    packet_type: str              # e.g. "determinism_rca", "p0_failure", "ratchet_review"
    packet_id: str                # deterministic UUID from inputs
    schema_version: str           # "1.0.0"

    # Blocks (ordered — canonical evidence precedes interpretation)
    system_block: str             # Operator mode / system instructions
    policy_block: str             # Invariants, rules, constraints
    task_block: str               # What the consumer should do
    must_use_evidence: list[dict] # Evidence that MUST be cited in response
    optional_evidence: list[dict] # Evidence that MAY be cited

    # Integrity
    contradiction_flags: list[dict]  # Explicit disagreements
    abstain_instructions: str     # When/how to abstain
    refine_instructions: str      # What to request if evidence is insufficient

    # Output
    output_schema: dict           # Expected response structure
    replay_metadata: dict         # snapshot_id, commit_sha, digests, timestamp

    # Status
    assembly_status: PromptAssemblyStatus
```

### 4.2 PromptAssemblyStatus

```python
@dataclass
class PromptAssemblyStatus:
    packet_type: str
    packet_id: str
    input_artifacts: list[str]
    evidence_contract_status: str  # "complete" | "partial" | "empty"
    contradiction_status: str      # "none" | "minor" | "major"
    token_budget_status: str       # "within_budget" | "trimmed" | "split"
    overflow_action: str           # "none" | "summarized" | "narrowed" | "split" | "abstained"
    assembly_result: str           # "pass" | "fail" | "partial"
    replay_metadata: dict
```

### 4.3 Authority Slot Ordering

Every packet follows this strict block order:

1. **system_block** — operator mode, role definition
2. **policy_block** — invariants, non-negotiable constraints
3. **task_block** — what to do, what question to answer
4. **must_use_evidence** — canonical ADG evidence (source-of-truth)
5. **optional_evidence** — graph DB augmentation (marked as derived)
6. **contradiction_flags** — explicit disagreements (NEVER hidden)
7. **abstain_instructions** — when/how to refuse to answer
8. **output_schema** — expected response format
9. **replay_metadata** — provenance for deterministic replay

This ensures canonical evidence precedes interpretation, contradictions are explicit, and graph DB outputs are clearly tagged as augmenting.

### 4.4 Shared Templates

Templates are static YAML/dict blocks stored in a central registry:

```python
PACKET_TEMPLATES: dict[str, PacketTemplate] = {
    "determinism_rca": PacketTemplate(
        system_block="You are an ADG determinism analyst...",
        policy_block="Canonical ADG artifacts are the source of truth...",
        output_schema={...},
        must_use_sources=["provenance_report", "closure_report", "sqlite"],
        optional_sources=["graph_db"],
    ),
    "p0_failure": PacketTemplate(...),
    "ratchet_review": PacketTemplate(...),
    # ... 8 total
}
```

### 4.5 Packet Registry

A central `PacketRegistry` prevents prompt scatter:

- All packet types are registered with their builder, template, and evidence requirements
- No packet can be built without going through the registry
- Adding a new packet type requires registering it here (single place)

---

## 5. Packet Family Design

### 5.1 Eight Packet Families

| ID | Packet Family | Must-Use Evidence | Optional Evidence |
|----|--------------|-------------------|-------------------|
| **A** | Determinism/Provenance RCA | provenance_report, closure_report (row 3), SQLite digests | graph_db snapshot diff |
| **B** | P0 Failure | SQLite `violates` edges, closure_report, SC/AP config | graph path explanation |
| **C** | P1/P2 Ratchet Review | p1_ratchet, p2_ratchet, burndown_table, SQLite violations by severity | structural outputs (centrality) |
| **D** | Unknown/Unresolved Triage | layer_coverage_report (unknown_modules), SQLite unresolved imports | graph_db layer analysis |
| **E** | Hotspot Investigation | SQLite fan-in/fan-out top-N, structural_outputs centrality | graph_db blast radius |
| **F** | Infrastructure Boundary | infra wiring SQL views, infra_wiring_scan results, approved adapters | graph_db path traces |
| **G** | Graph Path Explanation | graph_db exact violating path, first illegal hop, blast radius | historical diff context |
| **H** | Executive Summary | adg_snapshot, burndown_table, closure_report summary rows, p1/p2 ratchets | all optional for depth |

### 5.2 Per-Packet Evidence Rules

Each packet builder enforces:
- **Must-use**: sources that MUST be present and cited; if missing → `evidence_contract_status: "partial"`
- **Optional**: sources that enrich but are not required; absence is noted but not a failure
- **Derived tag**: all graph DB evidence carries `is_derived: true`

---

## 6. Token Budgeting Design

### 6.1 Budget Allocation per Packet Type

| Packet Type | Target Tokens | System+Policy | Task | Must-Use Evidence | Optional | Contradiction+Meta |
|-------------|--------------|---------------|------|-------------------|----------|-------------------|
| **Executive Summary** | 4K | 400 | 300 | 2500 | 500 | 300 |
| **Determinism RCA** | 8K | 500 | 500 | 5000 | 1200 | 800 |
| **P0 Failure** | 6K | 400 | 400 | 4000 | 800 | 400 |
| **Ratchet Review** | 6K | 400 | 400 | 4000 | 800 | 400 |
| **Unknown/Unresolved** | 6K | 400 | 400 | 4000 | 800 | 400 |
| **Hotspot Investigation** | 8K | 500 | 500 | 5000 | 1200 | 800 |
| **Infra Boundary** | 6K | 400 | 400 | 4000 | 800 | 400 |
| **Graph Path** | 6K | 400 | 400 | 4000 | 800 | 400 |

### 6.2 Stratification Rules

When evidence exceeds budget:

1. **High-signal first** — critical-severity violations before medium/low
2. **Modified-area focus** — violations in recently changed files first
3. **Critical-path first** — nodes on known critical paths prioritized
4. **Representative sampling** — for large sets (e.g. 563 unresolved imports), include top-10 representative clusters, not all rows
5. **Hotspot neighborhoods** — top-5 neighborhoods, not full graph flood

### 6.3 Overflow Actions

| Action | When | Effect |
|--------|------|--------|
| **Summarize** | Evidence slightly over budget | Condense low-priority items into summary counts |
| **Narrow** | Evidence significantly over budget | Restrict to top-N by severity or fan-in |
| **Split** | Evidence far over budget | Emit follow-on packet with remaining evidence |
| **Abstain** | Cannot meaningfully present in budget | Emit abstain with scope refinement suggestion |

### 6.4 Instruction Preservation

Token trimming NEVER removes:
- system_block
- policy_block
- task_block
- contradiction_flags
- abstain_instructions
- output_schema

Only evidence blocks are trimmed. Must-use evidence is trimmed last (after optional).

---

## 7. Integration Plan

### 7.1 Directory Structure

```
tools/adg/prompt_assembly/
    __init__.py                  # Public API
    contracts.py                 # EvidenceItem, EvidenceBundle, PromptEnvelope, PromptAssemblyStatus
    retrieval/
        __init__.py
        adapters.py              # SQLiteAdapter, ReportAdapter, RatchetAdapter, GraphDBAdapter, InfraWiringAdapter, StructuralAdapter
    shaping/
        __init__.py
        evidence_shaper.py       # Dedupe, normalize, reconcile, contradiction retain, gap compute
    packets/
        __init__.py
        registry.py              # PacketRegistry, PacketTemplate
        builders.py              # 8 packet builders (one function each)
    budgeting/
        __init__.py
        token_budgeter.py        # Budget allocation, stratification, overflow
    cli.py                       # CLI entrypoint: python -m tools.adg.prompt_assembly
```

### 7.2 Trigger Points

| Trigger | When | Packet(s) Generated |
|---------|------|-------------------|
| Post-ADG run | After `generate_full_adg.py` completes | Executive Summary (H) |
| Post-P0 failure | When P0 gate fails (exit 1) | P0 Failure (B) |
| Post-ratchet | After P1/P2 ratchet check | Ratchet Review (C) |
| Analyst query | Manual CLI invocation | Any packet type by name |
| Graph investigation | Manual CLI for path/hotspot | Graph Path (G), Hotspot (E) |
| Provenance mismatch detected | When closure report row 3 fails | Determinism RCA (A) |

### 7.3 CLI Interface

```bash
# Generate specific packet
python -m tools.adg.prompt_assembly --packet determinism_rca
python -m tools.adg.prompt_assembly --packet p0_failure
python -m tools.adg.prompt_assembly --packet executive_summary

# Generate all packets for latest run
python -m tools.adg.prompt_assembly --all

# Custom SQLite path
python -m tools.adg.prompt_assembly --packet hotspot --sqlite artifacts/adg/adg_indexed_<ts>.sqlite

# Output format
python -m tools.adg.prompt_assembly --packet ratchet_review --format json
python -m tools.adg.prompt_assembly --packet ratchet_review --format markdown

# Write to file
python -m tools.adg.prompt_assembly --packet executive_summary --output artifacts/adg/packets/
```

### 7.4 Emission Formats

- **JSON**: Machine-readable `PromptEnvelope` dict
- **Markdown**: Human-readable formatted packet with sections
- **Both**: Default emits JSON; `--format markdown` for analyst consumption

### 7.5 What Is NOT Changed

- `generate_full_adg.py` — not modified; packets are generated optionally post-run
- Canonical artifact schemas — unchanged
- CI gates — unchanged; packet generation is additive
- Graph DB — unchanged; read-only consumption
- MCP server — unchanged; packets can be generated separately

---

## 8. File-by-File Implementation Plan

### Wave 1: Contracts + Core Types (P1–P3)

| File | Action | Content |
|------|--------|---------|
| `tools/adg/prompt_assembly/__init__.py` | CREATE | Public API exports |
| `tools/adg/prompt_assembly/contracts.py` | CREATE | `EvidenceItem`, `EvidenceBundle`, `PromptEnvelope`, `PromptAssemblyStatus` dataclasses |
| `tools/adg/prompt_assembly/packets/__init__.py` | CREATE | Packet subpackage init |
| `tools/adg/prompt_assembly/packets/registry.py` | CREATE | `PacketTemplate`, `PacketRegistry`, 8 template definitions |

### Wave 2: Retrieval Adapters + Evidence Shaping (P4–P5)

| File | Action | Content |
|------|--------|---------|
| `tools/adg/prompt_assembly/retrieval/__init__.py` | CREATE | Retrieval subpackage init |
| `tools/adg/prompt_assembly/retrieval/adapters.py` | CREATE | 6 retrieval adapters |
| `tools/adg/prompt_assembly/shaping/__init__.py` | CREATE | Shaping subpackage init |
| `tools/adg/prompt_assembly/shaping/evidence_shaper.py` | CREATE | Evidence shaping pipeline |

### Wave 3: Packet Builders + Token Budgeter (P6–P7)

| File | Action | Content |
|------|--------|---------|
| `tools/adg/prompt_assembly/packets/builders.py` | CREATE | 8 builder functions |
| `tools/adg/prompt_assembly/budgeting/__init__.py` | CREATE | Budgeting subpackage init |
| `tools/adg/prompt_assembly/budgeting/token_budgeter.py` | CREATE | Token budget allocation + overflow |

### Wave 4: CLI + Tests (P8–P9)

| File | Action | Content |
|------|--------|---------|
| `tools/adg/prompt_assembly/cli.py` | CREATE | CLI entrypoint |
| `tools/adg/prompt_assembly/__main__.py` | CREATE | `python -m` support |
| `tests/unit/tools/adg/prompt_assembly/test_contracts.py` | CREATE | Contract type tests |
| `tests/unit/tools/adg/prompt_assembly/test_adapters.py` | CREATE | Retrieval adapter tests |
| `tests/unit/tools/adg/prompt_assembly/test_shaper.py` | CREATE | Evidence shaper tests |
| `tests/unit/tools/adg/prompt_assembly/test_builders.py` | CREATE | Packet builder tests |
| `tests/unit/tools/adg/prompt_assembly/test_budgeter.py` | CREATE | Token budgeter tests |
| `tests/unit/tools/adg/prompt_assembly/test_cli.py` | CREATE | CLI tests |

### Wave 5: Docs + Integration (P10)

| File | Action | Content |
|------|--------|---------|
| `tools/adg/prompt_assembly/README.md` | CREATE | Architecture, usage, packet families |
| `docs/architecture/adr/adr-prompt-assembly-layer.md` | CREATE | ADR documenting design decisions |

---

## 9. Acceptance Criteria

1. ✅ C0 retrieval adapters and prompt assembly builders are in separate modules
2. ✅ ADG result packets use formal `EvidenceItem`/`EvidenceBundle` contracts
3. ✅ Contradictions, gaps, and weak support are preserved in `PromptEnvelope`
4. ✅ All packet builders use shared `PacketRegistry` and `PacketTemplate` — no scatter
5. ✅ Packet builders consume shaped evidence only — never call SQLite/JSON directly
6. ✅ Graph DB evidence is tagged `is_derived: true` in every `EvidenceItem`
7. ✅ Token budgeting is explicit with defined overflow actions
8. ✅ All 8 packet families have working builders
9. ✅ `PromptEnvelope` output is bounded, replayable, and deterministic from canonical inputs
10. ✅ Implementation is additive — no existing ADG generation or CI gate is modified
11. ✅ Tests verify retrieval/assembly boundary, packet correctness, contradiction preservation, token budget behavior

---

## 10. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Prompt scatter** — builders bypass registry | Medium | High | Registry is the only entry point; tests enforce |
| **Graph-only truth drift** — graph DB results treated as canonical | Low | High | `is_derived` tag on all graph evidence; tests enforce |
| **Contradiction suppression** — shaper hides disagreements | Low | Critical | Shaper MUST preserve; tests verify contradiction count |
| **Token overflow** — packets too large | Medium | Medium | Explicit budget + 4 overflow strategies |
| **Stale graph DB** — augmentation from old snapshot | Medium | Low | Freshness check in adapter; warn if stale |
| **SQLite schema drift** — ADG schema changes break adapters | Low | Medium | Schema version check in SQLiteAdapter |
| **Over-broad packets** — too much evidence hides signal | Medium | Medium | Must-use vs optional; stratification rules |
| **Mixing canonical and derived** — evidence sources confused | Low | High | `source_type` and `is_derived` on every item |

---

## 11. Assumptions and Uncertainties

### Assumptions

1. ADG SQLite schema (nodes/edges/violations tables) is stable and will not change during implementation
2. All canonical JSON report schemas are stable
3. `tools/graphdb/` NetworkX queries are functional and return expected dict structures
4. `config/token_budget.yaml` provides the model's context window limits
5. The repo's existing `tools/` directory is the correct home for this subsystem (not `agentic_core/`)
6. No runtime imports into `agentic_core/` are needed — this is a tooling-only subsystem

### Uncertainties

| Area | Uncertainty | Resolution Plan |
|------|-------------|----------------|
| **Graph DB availability** | NetworkX graph may not always be materialized | Adapter returns empty bundle; packet proceeds without derived evidence |
| **Token estimation accuracy** | Character-based estimation may differ from actual tokenization | Use `config/token_budget.yaml` rates; provide `--estimate-tokens` CLI flag |
| **Infra wiring view stability** | SQL views may change as infra wiring hardening continues | Adapter wraps view queries; schema check on load |
| **Packet type boundaries** | Some findings may span multiple packet types | Allow CLI to generate multiple packets per invocation; each packet is self-contained |
| **Repair log format** | Repair log structure may vary between runs | Adapter handles missing fields gracefully |

---

## STOP — Awaiting Approval

This is the end of Stage 1. No code has been written. The design package is complete.

**To proceed to Stage 2 (Implementation)**: Approve this plan and I will implement in the wave order described above.

**To modify**: Specify which sections need revision before approval.
