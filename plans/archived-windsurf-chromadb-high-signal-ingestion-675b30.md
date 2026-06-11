---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_windsurf_plans
source_key: windsurf
original_path: 'C:\\Git\\windsurf-plans-recovered\\windsurf_plans\\chromadb-high-signal-ingestion-675b30.md'
original_relative_path: 'chromadb-high-signal-ingestion-675b30.md'
source_sha256: 3c36000ae92612ee35e6d77044c5d6c1434a23d11ee7a35f44120a56631728ca
recovered_status: LOST_RECOVERED
last_commit: '41dafddcfc7'
last_commit_date: '2026-04-04 07:19:10 -0400'
created_date: '2026-04-04'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# ChromaDB High-Signal Content Ingestion Plan with Micro-Waves

Wire BGE-M3 embeddings into ingestion pipeline and ingest priority architectural documentation into ChromaDB using micro-wave execution (≤15 files per batch) for incremental validation and rollback safety.

---

## Wave & Micro-Wave Structure

| Wave | Micro-Wave | Phase ID | Files | Focus | Est. Tokens | Status | Success Criteria |
|------|------------|----------|-------|-------|-------------|--------|------------------|
| **Wave 0** | M0.0 | P0 | 1 | **BGE-M3 Wiring** — Modify `ingest_docs.py` to use embedding factory | ~500 | 🟡 In Progress | `--embedding-provider bge-m3` flag works |
| **Wave 1** | M1.1 | P1a | 12 | **Hardening Specs** — docs/specs/hardening/*.md | 51,055 | 🔵 Planned | `specs` collection created, 12 files ingested |
| **Wave 2** | M2.1 | P2a | 2 | **ADRs** — docs/architecture/adr/*.md | 3,500 | 🔵 Planned | ADR metadata preserved |
| | M2.2 | P2b | 3 | **Architecture Docs** — docs/architecture/*.md (non-ADR) | 3,773 | 🔵 Planned | Architecture patterns ingested |
| **Wave 3** | M3.1 | P3a | 2 | **Docs Rules** — docs/rules/*.md | 6,196 | 🔵 Planned | Governance rules ingested |
| | M3.2 | P3b | 8 | **Constitutional Rules** — .windsurf/rules/*.md | 9,779 | 🔵 Planned | Constitutional rules ingested |
| **Wave 4** | M4.1 | P4a | 8 | **App Specs Batch A** — apps_eval + apps_exec specs | 8,500 | 🔵 Planned | App specs A ingested |
| | M4.2 | P4b | 8 | **App Specs Batch B** — apps_research + apps_rfp + apps_shared specs | 8,645 | 🔵 Planned | App specs B ingested |
| **Wave 5** | M5.1 | P5a | 2 | **Audits** — docs/audits/*.md | 8,842 | 🔵 Planned | Gap audits ingested |
| | M5.2 | P5b | 1 | **Contracts** — docs/contracts/*.md | 556 | 🔵 Planned | Guardian contracts ingested |
| **Wave 6** | M6.1 | P6a | 3 | **Testing Guides** — docs/testing/*.md | 2,757 | 🔵 Planned | Test contracts ingested |
| | M6.2 | P6b | 3 | **SVP Docs** — docs/svp/*.md | 6,352 | 🔵 Planned | SVP retrieval docs ingested |
| | M6.3 | P6c | 1 | **Implementation Guide** — docs/guides/*.md | 1,555 | 🔵 Planned | ADG migration guide ingested |

**Total: ~12 micro-waves, ~112,010 tokens, 63 files, all GREEN**

---

## Micro-Wave Execution Order

### Wave 0 — BGE-M3 Wiring (Prerequisite)
**M0.0: Embedding Provider Wiring**
- **Files**: `tools/ingestion/ingest_docs.py` (1 file modified)
- **Scope**: Add `--embedding-provider` CLI arg, wire BGE-M3 factory
- **Command**:
```bash
# After code modification:
python tools/ingestion/ingest_docs.py --help | grep -i embedding
python tools/ingestion/ingest_docs.py --source-dir docs/specs --dry-run --embedding-provider bge-m3 --limit 3
```
- **Checkpoint**: BGE-M3 option appears in help, dry-run succeeds
- **Rollback**: `git checkout tools/ingestion/ingest_docs.py`

---

### Wave 1 — Hardening Specs
**M1.1: Hardening Specifications Ingestion**
- **Files**: 12 files from `docs/specs/hardening/`
  - `AUTHORITY_HIERARCHY_INVARIANTS.md`
  - `DEGRADATION_MATRIX.md`
  - `HEALER_RETRY_HARDENING_SPEC.md`
  - `L0_DECOMPOSITION_SPEC.md`
  - `L6_DRIFT_SAFEGUARDS_SPEC.md`
  - `LATENCY_BUDGET_SLA_SPEC.md`
  - `POLICY_EPOCH_SPEC.md`
  - `PTC_SCOPE_LOCK_SPEC.md`
  - `README.md`
  - `REPLAY_DETERMINISM_RULES.md`
  - `UWG_ISOLATION_SPEC.md`
  - `ssot_equivalence_spec.md`
- **Collection**: `specs`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/specs \
  --collection-name specs \
  --embedding-provider bge-m3 \
  --exclude-glob "**/generated/**"
```
- **Checkpoint**: Collection `specs` exists with 12 documents
- **Verification**:
```bash
python -c "from agentic_core.L4_state.client.chroma_client import SovereignChromaClient; c = SovereignChromaClient(); print(c.get_collection_stats('specs'))"
```

---

### Wave 2 — Architecture & ADRs
**M2.1: Architecture Decision Records**
- **Files**: 2 files from `docs/architecture/adr/`
  - `2026-03-29-chromadb-as-canonical-vector-store.md`
  - `adr-0042-skills-consolidation.md`
- **Collection**: `architecture`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/architecture/adr \
  --collection-name architecture \
  --embedding-provider bge-m3
```
- **Checkpoint**: 2 ADRs ingested with decision metadata

**M2.2: Architecture Documentation**
- **Files**: 3 files from `docs/architecture/`
  - `AI_CHECKING_AI_REMEDIATION_COMPLETE.md`
  - `hardening_addendum.md`
  - `PascalSovereignty_vs_PreCommit.md`
- **Collection**: `architecture` (same as M2.1)
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/architecture \
  --collection-name architecture \
  --embedding-provider bge-m3 \
  --exclude-glob "**/adr/**"
```
- **Checkpoint**: Total 5 files in `architecture` collection
- **Verification**:
```bash
python tools/ingestion/test_retrieval.py --collection architecture --query "chromadb ADR"
```

---

### Wave 3 — Governance Rules
**M3.1: Documentation Rules**
- **Files**: 2 files from `docs/rules/`
  - `enforcement_architecture.md`
  - `governance.md`
- **Collection**: `rules`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/rules \
  --collection-name rules \
  --embedding-provider bge-m3
```
- **Checkpoint**: 2 governance docs ingested

**M3.2: Constitutional Rules**
- **Files**: 8 files from `.windsurf/rules/`
  - `.windsurfrules`
  - `.windsurfrules.consolidated`
  - `adg-repair-discipline.md`
  - `embedding-lifecycle-gaps.md`
  - `mcp-config-ssot.md`
  - `p0-tactical-gaps.md`
  - `plan_ci_enforcement.md`
  - `test_sovereignty_rules.md`
- **Collection**: `constitutional_rules`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir .windsurf/rules \
  --collection-name constitutional_rules \
  --embedding-provider bge-m3
```
- **Checkpoint**: 8 constitutional rules ingested
- **Verification**:
```bash
python -c "from agentic_core.L4_state.client.chroma_client import SovereignChromaClient; c = SovereignChromaClient(); print('Rules:', c.get_collection_stats('rules')); print('Constitutional:', c.get_collection_stats('constitutional_rules'))"
```

---

### Wave 4 — App Specifications
**M4.1: App Specs Batch A (apps_eval + apps_exec)**
- **Files**: 8 files
  - `apps_eval/PRODUCT_SPEC.md`
  - `apps_eval/CLI_SPEC.md`
  - `apps_eval/OUTPUT_CONTRACTS.md`
  - `apps_eval/README.md`
  - `apps_exec/PRODUCT_SPEC.md`
  - `apps_exec/CLI_SPEC.md`
  - `apps_exec/OUTPUT_CONTRACTS.md`
  - `apps_exec/README.md`
- **Collection**: `apps`
- **Command**:
```bash
# Run separately for each app to ensure metadata
for app in apps_eval apps_exec; do
  python tools/ingestion/ingest_docs.py \
    --source-dir $app \
    --collection-name apps \
    --embedding-provider bge-m3
done
```
- **Checkpoint**: 8 app spec files ingested with app_id metadata

**M4.2: App Specs Batch B (apps_research + apps_rfp + apps_shared)**
- **Files**: 8 files
  - `apps_research/PRODUCT_SPEC.md`
  - `apps_research/CLI_SPEC.md`
  - `apps_research/OUTPUT_CONTRACTS.md`
  - `apps_research/README.md`
  - `apps_rfp/PRODUCT_SPEC.md`
  - `apps_rfp/CLI_SPEC.md`
  - `apps_rfp/OUTPUT_CONTRACTS.md`
  - `apps_rfp/README.md`
- **Collection**: `apps` (same as M4.1)
- **Command**:
```bash
for app in apps_research apps_rfp; do
  python tools/ingestion/ingest_docs.py \
    --source-dir $app \
    --collection-name apps \
    --embedding-provider bge-m3
done
```
- **Checkpoint**: Total 16 app spec files in `apps` collection
- **Verification**:
```bash
python tools/ingestion/test_retrieval.py --collection apps --query "evaluation engine"
```

---

### Wave 5 — Audits & Contracts
**M5.1: Architecture Audits**
- **Files**: 2 files from `docs/audits/`
  - `architecture_gap_audit.md`
  - `architecture_remediation_plan.md`
- **Collection**: `audits`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/audits \
  --collection-name audits \
  --embedding-provider bge-m3
```
- **Checkpoint**: Gap audit and remediation plan ingested

**M5.2: Guardian Contracts**
- **Files**: 1 file from `docs/contracts/`
  - `guardian_to_L6.md`
- **Collection**: `contracts`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/contracts \
  --collection-name contracts \
  --embedding-provider bge-m3
```
- **Checkpoint**: Guardian→L6 contract ingested
- **Verification**:
```bash
python -c "from agentic_core.L4_state.client.chroma_client import SovereignChromaClient; c = SovereignChromaClient(); print('Audits:', c.get_collection_stats('audits')); print('Contracts:', c.get_collection_stats('contracts'))"
```

---

### Wave 6 — Testing & SVP
**M6.1: Testing Guides**
- **Files**: 3 files from `docs/testing/`
  - `maintenance_procedures.md`
  - `TEST_CONTRACT.md`
  - `test_suite_guide.md`
- **Collection**: `testing`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/testing \
  --collection-name testing \
  --embedding-provider bge-m3
```
- **Checkpoint**: 3 test docs ingested

**M6.2: SVP Documentation**
- **Files**: 3 files from `docs/svp/`
  - `README.md`
  - `Retrieval_System_SVP.md`
  - `Technical_Implementation_Guide.md`
- **Collection**: `svp`
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/svp \
  --collection-name svp \
  --embedding-provider bge-m3
```
- **Checkpoint**: 3 SVP docs ingested

**M6.3: Implementation Guides**
- **Files**: 1 file from `docs/guides/`
  - `ADG_MCP_MIGRATION.md`
- **Collection**: `guides` (or merge into `svp`)
- **Command**:
```bash
python tools/ingestion/ingest_docs.py \
  --source-dir docs/guides \
  --collection-name guides \
  --embedding-provider bge-m3
```
- **Checkpoint**: Migration guide ingested
- **Verification**:
```bash
python tools/ingestion/test_retrieval.py --collection testing --query "test contract"
python tools/ingestion/test_retrieval.py --collection svp --query "retrieval system"
```

---

## Micro-Wave Loop (Per-Wave Execution Pattern)

Each micro-wave follows this loop:

```
┌─────────────────────────────────────────────────────────────┐
│  MICRO-WAVE EXECUTION LOOP                                  │
├─────────────────────────────────────────────────────────────┤
│  1. PRE-FLIGHT                                              │
│     └── Verify BGE-M3: python -c "from agentic_core...      │
│                                                             │
│  2. INGESTION                                               │
│     └── Run micro-wave command                              │
│                                                             │
│  3. CHECKPOINT                                              │
│     └── Verify collection count increased                   │
│                                                             │
│  4. DIVERGENCE CHECK                                        │
│     └── If collection count unchanged → STOP, investigate    │
│                                                             │
│  5. RETRIEVAL TEST                                          │
│     └── Query sample from micro-wave files                  │
│                                                             │
│  6. PROCEED                                                 │
│     └── Continue to next micro-wave                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Gap Register

**GAP-1: Embedding Provider Selection** → **BEING ADDRESSED IN M0.0**
- Current: `ingest_docs.py` uses OpenAI or mock embeddings
- Required: Wire BGE-M3 embedding factory
- Resolution: Add `--embedding-provider` CLI arg, import factory, replace OpenAI client

**GAP-2: Collection Naming Strategy**
- Current: Single collection per run
- Required: Domain-separated collections (specs, architecture, rules, apps, audits, testing, svp, guides)
- Impact: 8 collections total

**GAP-3: Content Deduplication**
- Risk: Some specs may overlap with generated API docs (excluded)
- Mitigation: Use content hash deduplication in metadata

---

## Rules

- **EXCLUDE** `docs/generated/api/` — auto-generated, high redundancy
- **EXCLUDE** `docs/evidence/` — runtime logs, not reference material
- **EXCLUDE** `docs/store/` — tool call storage, not documentation
- **MICRO-WAVE LIMIT**: ≤15 files per micro-wave (all waves compliant)
- **CHECKPOINT AFTER EACH MICRO-WAVE**: Verify collection count before proceeding
- **USE** BGE-M3 embeddings via `embedding_factory.create_embedding_client("bge-m3")`
- **PRESERVE** directory structure in metadata for traceability
- **DEFER** Waves 1-6 execution to next session per user request
- **EXECUTE** Wave 0 (wiring) now if approved

---

## Success Criteria

| Wave | Micro-Waves | Files | Collection | Success Criteria |
|------|-------------|-------|------------|------------------|
| 0 | M0.0 | 1 (modified) | — | `--embedding-provider bge-m3` flag works |
| 1 | M1.1 | 12 | `specs` | Hardening specs queryable |
| 2 | M2.1, M2.2 | 5 | `architecture` | ADRs + arch docs queryable |
| 3 | M3.1, M3.2 | 10 | `rules`, `constitutional_rules` | Governance rules queryable |
| 4 | M4.1, M4.2 | 16 | `apps` | App specs queryable |
| 5 | M5.1, M5.2 | 3 | `audits`, `contracts` | Audits + contracts queryable |
| 6 | M6.1, M6.2, M6.3 | 7 | `testing`, `svp`, `guides` | Testing + SVP docs queryable |

**Total**: 12 micro-waves, 8 collections, 54 files ingested

---

## Rollback Strategy (Per Micro-Wave)

**If micro-wave fails:**
1. **Log failure**: Note which files failed in micro-wave manifest
2. **Delete partial collection**: `client.delete_collection("<name>")` (if first micro-wave of wave)
3. **Fix issue**: Address code/config problem
4. **Re-run micro-wave**: Execute single micro-wave command
5. **Verify**: Checkpoint before proceeding

**If Wave 0 (wiring) fails:**
1. Revert `ingest_docs.py`: `git checkout tools/ingestion/ingest_docs.py`
2. Verify fallback works: `python tools/ingestion/ingest_docs.py --mock-embeddings --dry-run`

**Full reset if needed:**
```bash
# Delete all ChromaDB data
rm -rf artifacts/chromadb/*

# Re-run from Wave 0
```

---

## Acceptance Criteria Matrix

| Wave | Micro-Wave | Metric | Target | Verification |
|------|------------|--------|--------|--------------|
| 0 | M0.0 | BGE-M3 wired | 100% | `--embedding-provider bge-m3` works, 1024-dim |
| 1 | M1.1 | Specs ingested | 12 files | `specs` collection count = 12 |
| 2 | M2.1 | ADRs ingested | 2 files | `architecture` count = 2 |
| 2 | M2.2 | Arch docs ingested | 3 files | `architecture` count = 5 |
| 3 | M3.1 | Docs rules ingested | 2 files | `rules` count = 2 |
| 3 | M3.2 | Const. rules ingested | 8 files | `constitutional_rules` count = 8 |
| 4 | M4.1 | App specs A ingested | 8 files | `apps` count = 8 |
| 4 | M4.2 | App specs B ingested | 8 files | `apps` count = 16 |
| 5 | M5.1 | Audits ingested | 2 files | `audits` count = 2 |
| 5 | M5.2 | Contracts ingested | 1 file | `contracts` count = 1 |
| 6 | M6.1 | Testing docs ingested | 3 files | `testing` count = 3 |
| 6 | M6.2 | SVP docs ingested | 3 files | `svp` count = 3 |
| 6 | M6.3 | Guides ingested | 1 file | `guides` count = 1 |

---

## Quick Reference: All Micro-Wave Commands

```bash
# ===== WAVE 0: BGE-M3 Wiring =====
# (Code modification required, then test)
python tools/ingestion/ingest_docs.py --help | grep -i embedding

# ===== WAVE 1: Hardening Specs =====
python tools/ingestion/ingest_docs.py --source-dir docs/specs --collection-name specs --embedding-provider bge-m3

# ===== WAVE 2: Architecture =====
python tools/ingestion/ingest_docs.py --source-dir docs/architecture/adr --collection-name architecture --embedding-provider bge-m3
python tools/ingestion/ingest_docs.py --source-dir docs/architecture --collection-name architecture --embedding-provider bge-m3 --exclude-glob "**/adr/**"

# ===== WAVE 3: Governance Rules =====
python tools/ingestion/ingest_docs.py --source-dir docs/rules --collection-name rules --embedding-provider bge-m3
python tools/ingestion/ingest_docs.py --source-dir .windsurf/rules --collection-name constitutional_rules --embedding-provider bge-m3

# ===== WAVE 4: App Specifications =====
for app in apps_eval apps_exec apps_research apps_rfp; do
  python tools/ingestion/ingest_docs.py --source-dir $app --collection-name apps --embedding-provider bge-m3
done

# ===== WAVE 5: Audits & Contracts =====
python tools/ingestion/ingest_docs.py --source-dir docs/audits --collection-name audits --embedding-provider bge-m3
python tools/ingestion/ingest_docs.py --source-dir docs/contracts --collection-name contracts --embedding-provider bge-m3

# ===== WAVE 6: Testing & SVP =====
python tools/ingestion/ingest_docs.py --source-dir docs/testing --collection-name testing --embedding-provider bge-m3
python tools/ingestion/ingest_docs.py --source-dir docs/svp --collection-name svp --embedding-provider bge-m3
python tools/ingestion/ingest_docs.py --source-dir docs/guides --collection-name guides --embedding-provider bge-m3

# ===== VERIFICATION =====
python -c "from agentic_core.L4_state.client.chroma_client import SovereignChromaClient; c = SovereignChromaClient(); print(c.list_collections())"
```
