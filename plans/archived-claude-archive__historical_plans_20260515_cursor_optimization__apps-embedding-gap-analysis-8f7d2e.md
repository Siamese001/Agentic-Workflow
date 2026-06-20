---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\historical_plans_20260515_cursor_optimization\\apps-embedding-gap-analysis-8f7d2e.md'
original_relative_path: '_archive\\historical_plans_20260515_cursor_optimization\\apps-embedding-gap-analysis-8f7d2e.md'
source_sha256: e0d46cbf9dee95f46d5277f54b25e387f21115af4a5047022c68e8e7197b9f9d
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-embedding-gap-analysis-8f7d2e
plan_type: audit
dod_exempt: false
---

# Apps Embedding Gap Analysis — ADG-Driven Inventory vs ChromaDB

Inspect all apps_* overlays via ADG to determine runtime embedding requirements, inventory current ChromaDB collections, and produce a read-only gap analysis without mutating any data.

---

## Context (SCQA)

- **Situation** — The system uses one governed agentic spine with apps_* overlays. Embeddings power L1/L0 intent routing, C0 retrieval/evidence, R1B semantic cache, graph signatures, and Exit quality checks. Current state of which apps use which embedding signals via which spine stages is not centrally inventoried.

- **Complication** — apps_* may have invented independent embedding paths, or may lack required collections. ChromaDB collections may be orphaned, stale, or duplicative. Without a gap analysis, we cannot distinguish runtime-critical needs from eval-only or future-run-only needs.

- **Question** — What embeddings does each apps_* overlay actually require per ADG evidence, and how does that map to existing ChromaDB collections?

- **Answer** — A read-only gap analysis producing requirements inventory, ChromaDB inventory, and gap matrix distinguishing intent_vec vs fact_vec vs graph_sig, with P0/P1/P2 remediation grouping.

---

## Evidence Sources

| Source | Why needed | Status |
|---|---|---|
| ADG artifacts (adg_indexed_*.sqlite, mv_*, v_p*) | Structural dependency evidence | 🔲 |
| apps_* config/domain_contract/ | Registry declarations, rubrics, thresholds | 🔲 |
| apps_* source code imports/calls | Runtime embedding consumer/producer paths | 🔲 |
| ChromaDB persistent directory metadata | Collection inventory, dimensionality, counts | 🔲 |
| agentic_core spine contracts | FinalEvidenceContract, PromptEnvelope, ExitReviewPacket refs | 🔲 |

---

## Wave Structure

| Wave | Focus | Scope | Checkpoint | Tokens |
|------|-------|-------|------------|--------|
| W0 | Baseline repo and ADG inputs | Locate ADG generator, artifacts, apps_* directories, spine routing | ADG artifacts located, safe gen command identified | ~8K 🟢 |
| W1 | Build apps_* embedding requirement map from ADG | Per-app requirement extraction (8 requirement categories) | apps_embedding_requirements_from_adg.json complete | ~15K 🟢 |
| W2 | Inventory current ChromaDB state | Collection metadata, dimensionality, ownership, staleness | chromadb_embedding_inventory.json complete | ~6K 🟢 |
| W3 | Compare required vs actual embeddings | Gap matrix 11 status types, per-surface classification | apps_embedding_gap_matrix.json complete | ~8K 🟢 |
| W4 | Contract alignment cross-check | R1B, FinalEvidenceContract, PromptEnvelope, ExitReviewPacket, L6 | Contract gaps documented | ~5K 🟢 |
| W5 | Output artifacts and reports | 5 JSON/MD files under artifacts/apps_embedding_gap_analysis/ | All files created, no ChromaDB mutation | ~4K 🟢 |
| W6 | Acceptance verification | 10 criteria verification, final summary | Criteria met, read-only verified | ~2K 🟢 |

**Total: ~48K tokens across 6 waves, all GREEN**

---

## Out Of Scope

- ❌ Mutating ChromaDB (adding/removing collections, updating metadata)
- ❌ Generating new embeddings
- ❌ Deleting or rewriting any production files
- ❌ "Fixing" gaps — this plan is inspection-only
- ❌ Code refactoring or path consolidation
- ❌ LLM inference or embedding model training
- ❌ Real-time runtime telemetry capture (use existing OTel artifacts only)

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| W0.P1 | Locate ADG generator and artifacts | tools/adg/, artifacts/adg/ | ADG may be stale; unclear if safe to regenerate | ~3K | 🔲 TODO |
| W0.P2 | Identify apps_* directories and spine routing | apps_*/ directories | Distinguish spine-routed vs legacy paths | ~2K | 🔲 TODO |
| W0.P3 | Capture exact paths and commands | docs, READMEs, scripts | Documentation may not match reality | ~3K | 🔲 TODO |
| W1.P1 | L1/L0 intent support requirements | apps_* L1_cognition/, L0_routing/ | R1B semantic cache routing | ~4K | 🔲 TODO |
| W1.P2 | C0 grounded retrieval requirements | apps_* c0/, retrieval configs | fact_vec vs intent_vec distinction | ~4K | 🔲 TODO |
| W1.P3 | Prompt Assembly evidence packing | apps_* PA configs | Evidence contract embedding refs | ~3K | 🔲 TODO |
| W1.P4 | L2 model/tool execution using evidence | apps_* L2_execution/ | Evidence consumption patterns | ~2K | 🔲 TODO |
| W1.P5 | Exit quality/groundedness checks | Exit eval configs | citation, faithfulness, cache compatibility | ~2K | 🔲 TODO |
| W2.P1 | Locate ChromaDB configuration | config/, .env, docker-compose | Multiple possible persist directories | ~2K | 🔲 TODO |
| W2.P2 | Inspect collection metadata | ChromaDB client read-only | Authentication/permission limits | ~2K | 🔲 TODO |
| W2.P3 | Classify collection state | metadata analysis | Stale vs active vs orphaned judgment | ~2K | 🔲 TODO |
| W3.P1 | Build gap matrix | JSON comparison logic | 11 status types, edge cases | ~4K | 🔲 TODO |
| W3.P2 | Per-app gap rollup | Aggregation logic | Unknown_NEEDS_MANUAL_REVIEW handling | ~2K | 🔲 TODO |
| W3.P3 | Critical gaps identification | Scoring/ranking | P0/P1/P2 classification | ~2K | 🔲 TODO |
| W4.P1 | R1B semantic cache contract check | R1B configs | request_intent_embedding_ref, cache_embedding_ref | ~2K | 🔲 TODO |
| W4.P2 | FinalEvidenceContract check | Exit eval contracts | query_vec_ref, fact_vec_ref, evidence_items | ~2K | 🔲 TODO |
| W4.P3 | PromptEnvelope/SealedL2Artifact check | L2 contracts | evidence_refs preservation | ~1K | 🔲 TODO |
| W5.P1 | Create JSON artifacts | 3 JSON files | Schema validation | ~2K | 🔲 TODO |
| W5.P2 | Create markdown reports | 2 MD files | Executive summary, gap details | ~2K | 🔲 TODO |
| W6.P1 | Acceptance criteria verification | Verification scripts | Read-only verification | ~2K | 🔲 TODO |

**Status legend**: 🔲 TODO · 🔄 IN PROGRESS · ✅ DONE · ❌ BLOCKED

---

## Gap Register

**GAP-1: ADG staleness risk**
- Existing ADG artifacts may not reflect current code state
- Impact: Requirements map may be based on stale structural evidence
- Mitigation: Document timestamp, note limitation, optionally regenerate if safe

**GAP-2: ChromaDB location multiplicity**
- Config files, docker-compose, and .env may reference different persist directories
- Impact: May miss collections if inspecting wrong path
- Mitigation: Search all candidate paths, document which were inspected

**GAP-3: apps_* local embedding paths**
- Some apps may have invented independent embedding paths outside spine
- Impact: Spine governance violated, duplicate collections possible
- Mitigation: ADG edge analysis for imports outside agentic_core

**GAP-4: Contract field vs runtime mismatch**
- Contracts may declare embedding refs that runtime does not populate
- Impact: False confidence in evidence chain
- Mitigation: Cross-reference ADG flows_to/reads_from edges

---

## Execution Plan

### W0 — Baseline repo and ADG inputs

**Scope**: Establish foundation for analysis by locating ADG artifacts, apps_* directories, and identifying spine vs legacy routing.

**Commands**:
```bash
# Locate ADG generator and latest artifacts
find . -name "generate_full_adg.py" -type f 2>/dev/null
find . -name "adg_indexed_*.sqlite" -type f 2>/dev/null | head -5
find . -name "three_bucket_gap_report*.md" -type f 2>/dev/null | head -5

# Identify apps_* directories
ls -d apps_*/ 2>/dev/null

# Check for safe ADG regeneration command
python tools/generate_full_adg.py --help 2>/dev/null || echo "No --help available"

# Verify ADG health if MCP available
python -c "from mcp1_adg_health import main; main()" 2>/dev/null || echo "MCP not available via CLI"
```

**Acceptance**:
- [ ] ADG generator path identified
- [ ] Latest ADG sqlite path identified (or "none found" documented)
- [ ] All apps_* directories listed
- [ ] Safe regeneration command verified or documented as unsafe/unclear

---

### W1 — Build apps_* embedding requirement map from ADG

**Scope**: For each apps_* package, analyze ADG to determine embedding requirements across 8 categories.

**Commands**:
```bash
# Query ADG for embedding-related nodes
# (Use adg_sqlite MCP or direct sqlite3 if MCP unavailable)

# Example direct SQLite queries if needed:
sqlite3 artifacts/adg/adg_indexed_<TS>.sqlite "
SELECT DISTINCT layer, adg_name, resolved_path 
FROM nodes 
WHERE adg_name LIKE '%embed%' OR adg_name LIKE '%intent%' OR adg_name LIKE '%fact%' OR adg_name LIKE '%cache%'
ORDER BY layer, adg_name;
"

# Query for apps_* imports of embedding-related modules
sqlite3 artifacts/adg/adg_indexed_<TS>.sqlite "
SELECT src.resolved_path, tgt.resolved_path, e.relation_type
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes tgt ON e.tgt_id = tgt.id
WHERE tgt.adg_name LIKE '%embedding%' OR tgt.adg_name LIKE '%chroma%' OR tgt.adg_name LIKE '%vector%'
ORDER BY src.layer, src.adg_name;
"
```

**Acceptance**:
- [ ] Every apps_* package has requirement rows in apps_embedding_requirements_from_adg.json
- [ ] 8 requirement categories addressed per app where applicable
- [ ] confidence (high/medium/low) assigned per row
- [ ] evidence_paths cite specific ADG nodes/edges or config files

---

### W2 — Inventory current ChromaDB state

**Scope**: Read-only inspection of ChromaDB collections without mutation.

**Commands**:
```bash
# Find ChromaDB configuration
find . -name "chroma*" -type f 2>/dev/null | grep -E "\.(yaml|yml|json|py)$"
grep -r "chromadb" --include="*.py" --include="*.yaml" --include="*.yml" -l 2>/dev/null | head -10
grep -r "ChromaClient\|PersistentClient" --include="*.py" -l 2>/dev/null | head -10

# Inspect via Python (read-only)
python -c "
import chromadb
from pathlib import Path

# Try common persist directories
persist_dirs = [
    './chroma_db',
    './.chroma',
    './data/chroma',
    './vector_db',
]

for pd in persist_dirs:
    if Path(pd).exists():
        print(f'Found persist directory: {pd}')
        try:
            client = chromadb.PersistentClient(path=pd)
            collections = client.list_collections()
            print(f'  Collections: {[c.name for c in collections]}')
        except Exception as e:
            print(f'  Error accessing {pd}: {e}')
"
```

**Acceptance**:
- [ ] All ChromaDB persist directories identified
- [ ] Every collection has metadata row in chromadb_embedding_inventory.json
- [ ] Collection state classified (active/stale/orphaned/test-only/unknown)
- [ ] No ChromaDB mutation occurred (verified by timestamp checks)

---

### W3 — Compare required vs actual embeddings

**Scope**: Build gap matrix with 11 status types.

**Commands**:
```bash
# Analysis performed via Python script (no external commands)
# Script: tools/analysis/apps_embedding_gap_analysis.py (created in W5)

# Verification that no mutations occurred
find artifacts/apps_embedding_gap_analysis/ -type f -name "*.json" -newer .windsurf/plans/apps-embedding-gap-analysis-8f7d2e.md 2>/dev/null | wc -l
```

**Acceptance**:
- [ ] apps_embedding_gap_matrix.json exists with all 11 status types represented
- [ ] Every required embedding surface has gap status assigned
- [ ] UNKNOWN_NEEDS_MANUAL_REVIEW used where evidence insufficient
- [ ] intent_vec vs fact_vec vs graph_sig distinguished

---

### W4 — Contract alignment cross-check

**Scope**: Verify embedding-related contract expectations.

**Commands**:
```bash
# Inspect contract files
grep -r "request_intent_embedding_ref\|cache_embedding_ref" --include="*.yaml" --include="*.py" -l 2>/dev/null
grep -r "query_vec_ref\|fact_vec_ref\|dense_search_refs" --include="*.yaml" --include="*.py" -l 2>/dev/null
grep -r "FinalEvidenceContract\|PromptEnvelope\|ExitReviewPacket" --include="*.py" -l 2>/dev/null | head -10

# ADG semantic edge check for flows_to/reads_from on evidence paths
sqlite3 artifacts/adg/adg_indexed_<TS>.sqlite "
SELECT src.adg_name, tgt.adg_name, e.relation_type
FROM edges e
JOIN nodes src ON e.src_id = src.id
JOIN nodes tgt ON e.tgt_id = tgt.id
WHERE e.relation_type IN ('flows_to', 'reads_from', 'writes_to')
AND (src.adg_name LIKE '%evidence%' OR tgt.adg_name LIKE '%evidence%')
ORDER BY src.layer;
"
```

**Acceptance**:
- [ ] R1B semantic cache contract requirements documented
- [ ] FinalEvidenceContract field requirements documented
- [ ] PromptEnvelope/SealedL2Artifact evidence ref requirements documented
- [ ] ExitReviewPacket/X1 evidence ref requirements documented

---

### W5 — Output artifacts

**Scope**: Create 5 deliverable files under artifacts/apps_embedding_gap_analysis/.

**Commands**:
```bash
# Create output directory
mkdir -p artifacts/apps_embedding_gap_analysis

# Generate artifacts via analysis script
python tools/analysis/apps_embedding_gap_analysis.py \
  --adg-path artifacts/adg/adg_indexed_<TS>.sqlite \
  --apps-glob "apps_*/" \
  --chroma-persist-dir <DISCOVERED_PATH> \
  --out-dir artifacts/apps_embedding_gap_analysis/

# Verify files created
ls -la artifacts/apps_embedding_gap_analysis/
wc -l artifacts/apps_embedding_gap_analysis/*.json artifacts/apps_embedding_gap_analysis/*.md
```

**Acceptance**:
- [ ] apps_embedding_requirements_from_adg.json created
- [ ] chromadb_embedding_inventory.json created
- [ ] apps_embedding_gap_matrix.json created
- [ ] apps_embedding_gap_report.md created
- [ ] apps_embedding_gap_summary_for_exec.md created

---

### W6 — Acceptance verification

**Scope**: Verify all 10 acceptance criteria met.

**Commands**:
```bash
# Criteria 1: Every apps_* has row in requirements file
python -c "
import json
reqs = json.load(open('artifacts/apps_embedding_gap_analysis/apps_embedding_requirements_from_adg.json'))
apps = set(r['app_name'] for r in reqs)
print(f'Apps in requirements: {sorted(apps)}')
"

# Criteria 2: Every ChromaDB collection has row in inventory
python -c "
import json
inv = json.load(open('artifacts/apps_embedding_gap_analysis/chromadb_embedding_inventory.json'))
print(f'Collections inventoried: {len(inv.get(\"collections\", []))}')
"

# Criteria 3: Every required embedding has gap status
python -c "
import json
matrix = json.load(open('artifacts/apps_embedding_gap_analysis/apps_embedding_gap_matrix.json'))
unclassified = [m for m in matrix if m.get('gap_status') == 'UNKNOWN_NEEDS_MANUAL_REVIEW']
print(f'Unclassified surfaces: {len(unclassified)}')
"

# Criteria 4-5: intent_vec vs fact_vec vs graph_sig distinguished
python -c "
import json
reqs = json.load(open('artifacts/apps_embedding_gap_analysis/apps_embedding_requirements_from_adg.json'))
signal_types = set(r.get('embedding_signal_type') for r in reqs)
print(f'Signal types found: {signal_types}')
"

# Criteria 6-7: No ChromaDB mutation, no embeddings generated
# Verified by file timestamps and content inspection
stat artifacts/apps_embedding_gap_analysis/*.json

# Criteria 8: No code fixes made
git diff --stat 2>/dev/null | grep -v "artifacts/apps_embedding_gap_analysis" || echo "No code changes outside artifacts/"

# Criteria 9-10: Evidence paths present, unknowns marked
python -c "
import json
matrix = json.load(open('artifacts/apps_embedding_gap_analysis/apps_embedding_gap_matrix.json'))
missing_evidence = [m for m in matrix if not m.get('evidence_paths')]
print(f'Surfaces missing evidence_paths: {len(missing_evidence)}')
"
```

**Acceptance**:
- [ ] All 10 criteria verified
- [ ] Final summary with file counts, app counts, collection counts, critical gaps

---

## Rules

- **Read-only invariant**: No ChromaDB mutation, no embedding generation, no file rewrites
- **Evidence-based**: Every claim cites ADG nodes/edges, config files, or code paths
- **Confidence grading**: high (direct ADG edge), medium (config reference), low (inference/grep)
- **Unknown marking**: UNKNOWN_NEEDS_MANUAL_REVIEW for insufficient evidence, not silent pass
- **Signal type discipline**: intent_vec (L1/L0), fact_vec (C0), graph_sig (graph/lineage)
- **Runtime classification**: runtime-critical vs eval-only vs future-run-only must be explicit

---

## Success Criteria

| Metric | Target | Verification |
|---|---|---|
| apps_* packages inspected | 8+ (all apps_*) | Count rows in requirements JSON |
| ChromaDB collections found | All discovered | Count rows in inventory JSON |
| Required embedding surfaces classified | 100% | Gap matrix coverage check |
| Signal types distinguished | intent_vec/fact_vec/graph_sig | Field presence in requirements |
| Runtime vs eval vs future-run classified | Per-row | Classification field presence |
| ChromaDB mutations | 0 | Timestamp/content verification |
| Embeddings generated | 0 | No new vector files |
| Code fixes made | 0 | git diff limited to artifacts/ |
| Evidence paths present | Per-row | JSON field verification |
| Unknowns explicitly marked | All insufficient evidence | UNKNOWN_NEEDS_MANUAL_REVIEW count |

---

## Implementation Commands

```bash
# Full wave execution sequence (run waves sequentially)

# W0: Baseline
find . -name "adg_indexed_*.sqlite" -type f 2>/dev/null | sort -r | head -1
ls -d apps_*/

# W1: Requirements (ADG analysis - use MCP or direct SQLite)
# python tools/analysis/extract_embedding_requirements.py --adg-path <PATH>

# W2: ChromaDB inventory (read-only)
# python tools/analysis/inventory_chromadb.py --persist-dir <PATH>

# W3-W5: Analysis and report generation
# python tools/analysis/apps_embedding_gap_analysis.py --adg-path <PATH> --out-dir artifacts/apps_embedding_gap_analysis/

# W6: Verification
python ops_scripts/ci/check_apps_embedding_gap_analysis.py --artifacts-dir artifacts/apps_embedding_gap_analysis/
```

---

## Rollback Strategy

This is a read-only observational plan. No rollback needed.
- All outputs go to `artifacts/apps_embedding_gap_analysis/` (disposable)
- No production files modified
- No databases mutated
- To "undo": `rm -rf artifacts/apps_embedding_gap_analysis/`

---

## Definition of Done

| # | Criterion | Verification command / evidence | Status |
|---|---|---|---|
| DoD-1 | All apps_* packages have requirement rows | `python -c "import json; r=json.load(open('artifacts/apps_embedding_gap_analysis/apps_embedding_requirements_from_adg.json')); apps=set(x['app_name'] for x in r); print(f'{len(apps)} apps: {sorted(apps)}')"` | 🔲 |
| DoD-2 | All ChromaDB collections inventoried | `python -c "import json; i=json.load(open('artifacts/apps_embedding_gap_analysis/chromadb_embedding_inventory.json')); print(f'{len(i.get(\"collections\",[]))} collections')"` | 🔲 |
| DoD-3 | Gap matrix covers all required surfaces | `python -c "import json; m=json.load(open('artifacts/apps_embedding_gap_analysis/apps_embedding_gap_matrix.json')); print(f'{len(m)} surfaces classified')"` | 🔲 |
| DoD-4 | No ChromaDB mutation verified | `ls -la artifacts/apps_embedding_gap_analysis/*.json` created only | 🔲 |
| DoD-5 | Documentation complete (5 output files) | `ls artifacts/apps_embedding_gap_analysis/` shows 5 files | 🔲 |

**Verification-vs-Deferral table**:

| Item | Why deferred | Tracked in |
|---|---|---|
| Remediation implementation | Out of scope — this plan is inspection only | Future plan: apps-embedding-remediation-<hex> |
| Real-time telemetry capture | Use existing OTel artifacts only | W0 limitation documented |
| ADG regeneration | Only if safe; may use existing artifacts | W0.P1 determination |

---

## Cascade Alignment Checks

- ADG-first retrieval for dependency analysis (no grep for imports)
- Evidence paths required for every claim
- Confidence grading: high/medium/low
- Unknown_NEEDS_MANUAL_REVIEW for insufficient evidence
- Read-only invariant enforced throughout
