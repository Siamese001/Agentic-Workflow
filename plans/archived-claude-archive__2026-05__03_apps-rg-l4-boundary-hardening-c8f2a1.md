---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.claude\\plans\\_archive\\2026-05\\03_apps-rg-l4-boundary-hardening-c8f2a1.md'
original_relative_path: '_archive\\2026-05\\03_apps-rg-l4-boundary-hardening-c8f2a1.md'
source_sha256: 3d9ef4081813fced936146c80af05de0b95af0181cb571e1baf1f3e00244ad08
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
---
plan_id: apps-rg-l4-boundary-hardening-c8f2a1
plan_type: governance
touches_agentic_core: false
touches_governance_ci: true
touches_windsurf_rules: false
touches_plan_templates: false
core_addition_author_gate_required: false
author_gate_receipt_ref: ""
dod_exempt: false
---

> [!IMPORTANT]
> PORTFOLIO_STATUS: CONSOLIDATED_UNDER_MASTER
> MASTER_PLAN_REF: .cursor/plans/01_apps-rg-master-governed-runtime-hardening.md
> DISPOSITION: MERGED_INTO_MASTER
> SUPERSEDED_BY_PHASES: Phase 0, Phase 1, Phase 2, Phase 3, Phase 13
> RETAINED_SCOPE:
> - apps_rg-local direct cache write removal
> - app-owned L4 namespace manifest
> - filesystem and Chroma write guards
> - CI non-contamination proof
> MOVED_SCOPE:
> - Generic L4 namespace parser remains in Core G29 plan
> DEFERRED_SCOPE:
> - None by default
> CONFLICTS_RESOLVED:
> - This plan is the backbone for apps_rg-local L4/write boundary work

## Portfolio Consolidation Notes
This plan has been merged into the master consolidation. The original wave detail is preserved below for reference. Implementation ownership has been transferred to the master plan phases listed above.

---

# apps_rg L4 Boundary Hardening — UWG Compliance & CI Gate Enforcement (apps_rg-local ONLY)

Close apps_rg-local gaps from L4 end-to-end audit: eliminate direct semantic cache writes (P0 blocker), quarantine dead L6 engine, add app-owned L4 namespace manifest, enforce filesystem write discipline, and harden CI gate coverage for durable surface mutations. Core contract evolution (G29, FutureRunPromotionRequest proofs, generic L4 namespace parser) split to separate core-enabling plan.

---

## Plan State Markers

FORMAT_VERSION: simplified-plan-format-v1
PLAN_STATUS: TODO
CURRENT_WAVE: W0
LAST_COMPLETED_WAVE: NONE
LAST_UPDATED: 2026-05-13

---

## Context (SCQA)

- **Situation** — apps_rg runtime has evolved with multiple bindings (U0, L1, L0, C0, PA, L2, Exit) and semantic cache for section-level resume generation. The codebase has direct filesystem writes, dead L6 shadow learning code, and lacks explicit app-owned L4 namespace contracts. CI gates exist for some boundaries but gaps remain.

- **Complication** — GAP audit revealed: (G2) Direct semantic cache writes bypass UWG entirely; (G1) Dead L6 engine creates architectural confusion; (G3) No app-owned L4 namespace manifest for read surfaces; (G4) No CI gate scanning for direct filesystem writes; (G5) Exit may write artifacts directly without X3C/UWG mediation; (G6) C0 Chroma lacks readonly CI guard; (G7) Cache entries lack full L4 provenance; (G8) G29 gate identifier missing (split to core plan); (G9) Promotion request lacks proof fields (split to core plan); (G10) Print-based span emission instead of OTel.

- **Question** — How do we harden apps_rg L4 boundaries to ensure all durable writes are UWG-mediated, all read surfaces are namespaced and ACL-bound in app-owned config, and CI gates enforce these invariants without modifying agentic_core?

- **Answer** — Implement 6 waves of apps_rg-local changes only: W1 removes P0 blocker (direct cache write→inert proposals with full provenance schema), W2 quarantines dead code and fixes span labels with inertness proof, W3 adds app-owned L4 namespace manifest and Exit X3C proposal-only path (no core changes), W4 tests expect core fields (no core mods), W5 adds comprehensive CI gates with allowlist semantics, W6 verifies full compliance and non-contamination. Core contract evolution split to companion plan `core-l6-g29-promotion-proof-hardening`.

---

## Wave Overview

**Waves**: 6 total (W1–W6)
**Total Estimate**: ~18K tokens
**Current**: W0 (pre-flight)

**Wave Manifest**:
- **W1** — Remove P0 Blocker: Direct Cache Write → Inert Proposals (provenance-ready) | ~3K tokens | Checkpoint A | STATUS: TODO
- **W2** — Quarantine Dead Code & Fix Observability (inertness proof) | ~2K tokens | Checkpoint B | STATUS: TODO
- **W3** — App-owned L4 Namespace Manifest & Exit Proposal-Only Path | ~4K tokens | Checkpoint C | STATUS: TODO
- **W4** — Test Core Field Expectations (no core mods) | ~1K tokens | Checkpoint D | STATUS: TODO
- **W5** — CI Gate Enforcement (filesystem/Chroma/L4 import allowlists) | ~5K tokens | Checkpoint E | STATUS: TODO
- **W6** — Compliance Verification & Non-Contamination Proof | ~3K tokens | Checkpoint F | STATUS: TODO

**Pre-flight Baseline (W0)**:
- Run `python ops_scripts/ci/run_contract_gates.py` to capture current failing baseline
- Document known G2 violation (direct cache write) as accepted pre-existing
- Document any direct filesystem writes in Exit binding (file/line evidence)
- Establish allowlist template for runtime filesystem writes
- **W0 Baseline Receipt**: `artifacts/governance/apps_rg_l4_boundary_w0_baseline_receipt.json`
  - Current run_contract_gates result
  - Known G2 direct cache write evidence
  - G4 filesystem write classification
  - Allowlist seed state
  - Confirmation that no implementation changes were made during W0

---

## Wave 1 — Remove P0 Blocker: Direct Cache Write → Inert Proposals (Provenance-Ready)

WAVE_ID: W1
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: A

**Authorization**: NOT_REQUIRED — No shared surface modifications; apps_rg-local changes only.

**Phases**:
- **W1.1** — Create SectionCacheWriteProposal dataclass (full provenance schema) | ~1.2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.2** — Add cache_write_proposals to ExitBindingResult | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.3** — Refactor section pipeline to emit proposals only | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W1.4** — Add negative control test (AST/imports ban) | ~0.2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**SectionCacheWriteProposal Schema (W1.1)** — Provenance-ready from day one:
```python
@dataclass(frozen=True)
class SectionCacheWriteProposal:
    proposal_id: str                          # UUID
    section_id: str                         # headline, executive_summary, etc.
    cache_key: str                            # 32-char hash
    content_digest: str                     # SHA256 of content
    payload_digest: str                     # SHA256 of source payload
    metadata_ref: str                       # ref to metadata blob
    compatibility_proof_ref: str              # ref to compatibility validation
    request_intent_embedding_ref: str       # ref to intent embedding
    cache_embedding_ref: str                # ref to cache embedding
    evidence_lineage_digest: str            # digest of source evidence chain
    source_evidence_refs: tuple[str, ...]   # tuple of evidence refs
    policy_hash: str                        # policy version hash
    blueprint_hash: str                     # blueprint version hash
    registry_digest_set: tuple[str, ...]    # registry digests
    prompt_profile_refs: tuple[str, ...]   # prompt/profile refs used
    replay_key: str                         # deterministic replay key
    audit_manifest_ref: str                 # ref to audit manifest
    target_l4_namespace: str                 # "apps_rg/semantic_cache"
    mutation_type: str = "CACHE_WRITE"      # enum value
    proposal_status: str = "PENDING_UWG"    # PENDING_UWG | ADMITTED | REJECTED
    mutation_candidate_inert: bool = True   # explicit inert flag
```

**Acceptance**:
- `python ops_scripts/ci/check_no_direct_semantic_cache_write.py` passes (zero violations)
- `write_section_to_semantic_cache` no longer imported in `section_agentic_pipeline.py`
- Test proves section pipeline cannot call cache writer (AST scan fails if import present)
- `SectionCacheWriteProposal` dataclass exists with `frozen=True`, `mutation_candidate_inert=True`
- All 18 provenance fields present (may be empty strings pending UWG admission, but schema complete)
- `ExitBindingResult` has `cache_write_proposals: tuple[SectionCacheWriteProposal, ...]` field
- Runtime section generation returns proposals only (no actual cache mutation)

---

## Wave 2 — Quarantine Dead Code & Fix Observability (Inertness Proof)

WAVE_ID: W2
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: B

**Phases**:
- **W2.1** — Quarantine `l6_shadow_learning.py` to `_quarantine/` with header | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.2** — Fix span emission labels (Exit_observe, SECTION-OBSERVE) | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.3** — Add docstring clarifying telemetry-only purpose | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W2.4** — Prove inertness (AST scan, no dispatch refs, no tests) | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Acceptance**:
- File moved to `apps_rg/_quarantine/l6_shadow_learning.py` with header:
  ```python
  # QUARANTINED — NOT RUNTIME — DO NOT IMPORT
  # Moved 2026-05-13 per plan apps-rg-l4-boundary-hardening-c8f2a1 W2.1
  # Use canonical agentic_core/L6_learning/package_driven_l6_binding.py instead
  ```
- AST scan proves zero external importers (not just grep)
- No dispatch registry references
- No package `__init__.py` exports the quarantined module
- No tests import or rely on quarantined module
- Quarantined path excluded from runtime discovery
- Span labels changed from `"[L6-SHADOW]"` to `"[SECTION-OBSERVE]"`
- `_emit_section_span` has docstring: "Telemetry-only observation span. NOT real L6 learning execution."

---

## Wave 3 — App-Owned L4 Namespace Manifest & Exit Proposal-Only Path

WAVE_ID: W3
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: C

**Phases**:
- **W3.1** — Create `apps_rg/config/l4_namespace_manifest.yaml` (app-owned) | ~1.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.2** — Create optional `apps_rg/config/l4_namespace_manifest.schema.json` | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.3** — Add apps_rg tests validating manifest shape | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.4** — Refactor Exit binding to produce inert CommitRequest candidates only | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W3.5** — Add `x3c_commit_requests` to ExitBindingResult | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**apps_rg/config/l4_namespace_manifest.yaml (W3.1)**:
```yaml
l4_namespace:
  app_id: apps_rg
  version: "2026-05-13"
  surfaces:
    - surface_id: semantic_cache
      surface_type: cache
      schema_version: W5C
      acl_profile: apps_rg_runtime_only
      replay_key_pattern: "{section_id}:{cache_key}:{timestamp}"
      audit_manifest_ref: artifacts/apps_rg/audit/semantic_cache_manifest.jsonl
      retention_policy: 90d
    - surface_id: chroma_retrieval
      surface_type: vector_index
      schema_version: W4
      acl_profile: apps_rg_readonly
      replay_key_pattern: "{query_hash}:{source_class}:{n_results}"
      audit_manifest_ref: artifacts/apps_rg/audit/chroma_retrieval_manifest.jsonl
      retention_policy: derived_from_source
    # ... 8 more surfaces per GAP audit
```

**Exit X3C Semantics (Hardened W3.4-3.5)**:
- Exit may only produce **inert CommitRequest candidates** when X3C route selected
- Exit must not write files, mutate cache, mutate vectors, refresh indexes, or call L4 writers
- X3C is **not** a durable write — proposals only
- UWG is the **only** writer
- Rename `_write_artifact` → `_build_artifact_commit_candidate` (eliminate "write" verb)
- Add explicit comment: "Constructs inert commit candidate only. Does not write durable state."

**Acceptance**:
- `apps_rg/config/l4_namespace_manifest.yaml` exists with 10 surface definitions
- Optional JSON schema validates manifest shape
- Tests prove manifest valid against schema
- `exit_binding.py` has no:
  - `write_text`
  - `write_bytes`
  - `open(..., "w")`
  - `json.dump`
  - `pickle.dump`
  - `shutil.copy`
  - Chroma mutation calls
  - direct L4 writer imports
  - cache writer imports
- Only inert proposal or CommitRequest candidate construction is allowed 

---

## Wave 4 — Test Core Field Expectations (No Core Modifications)

WAVE_ID: W4
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: D

**Dependency**: apps_rg W4 may run before core plan completion only as xfail expectation tests. It may not be marked PASS until `core-l6-g29-promotion-proof-hardening` W1 is complete.

**Phases**:
- **W4.1** — Add tests expecting `PromotionGauntlet.GATE_ID == "G29"` | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.2** — Add tests expecting `L6GauntletResult.gate_id` field | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W4.3** — Add tests expecting FutureRunPromotionRequest proof fields | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Important**: This wave tests **expectations only** — no modifications to `agentic_core`. Core enabling work split to companion plan `core-l6-g29-promotion-proof-hardening`.

**Acceptance**:
- Tests assert `hasattr(PromotionGauntlet, 'GATE_ID')` and value equals `"G29"`
- Tests assert `L6GauntletResult` has `gate_id` field and is populated post-gauntlet
- Tests assert `FutureRunPromotionRequest` has proof fields: `completed_eval_record_ref`, `rca_packet_ref`, `audit_manifest_ref`
- Tests skip gracefully if core fields absent (xfail with clear message)
- No `agentic_core` file modifications in this plan
- W4 marked PASS only after companion core plan W1 completes

---

## Wave 5 — CI Gate Enforcement (Filesystem/Chroma/L4 Import Allowlists)

WAVE_ID: W5
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: E

**Phases**:
- **W5.1** — Create `check_no_direct_filesystem_durable_writes.py` with allowlist | ~2K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.2** — Create `apps_rg_runtime_filesystem_write_allowlist.yaml` | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.3** — Create `check_c0_chroma_readonly_runtime.py` (full runtime scan) | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.4** — Create `check_no_direct_l4_writer_imports.py` | ~1K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.5** — Create `check_l4_namespace_manifest_present.py` | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.6** — Register gates in `run_contract_gates.py` | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W5.7** — Add tests for each gate | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**Allowlist Semantics (W5.1-5.2)**:
- Gate distinguishes: forbidden durable runtime writes vs allowed sandbox/temp writes vs allowed test fixture writes vs allowed UWG implementation writes
- Allowlist at: `ops_scripts/ci/allowlists/apps_rg_runtime_filesystem_write_allowlist.yaml`
- Categories: `sandbox_temp`, `test_fixtures`, `ci_output`, `uwg_implementation`, `docs_plans`
- Fail closed when write found outside allowlist

**C0 Chroma Gate Scope (W5.3)**:
- Scans: `apps_rg/runtime/**`, `apps_rg/cache/**`, `apps_rg/tools/**`, `apps_rg/providers/**`, `apps_rg/runtime/bindings/**`
- Blocks mutations: `add`, `upsert`, `delete`, `update`, `get_or_create_collection` (with side effects), `persist`, `reset`, `create_collection`
- Allowed live: `query`, `get`, `peek` (read-only)

**L4 Import Gate (W5.4)**:
- Blocks direct import from core L4 write modules: `StateStore`, `DurableWriteGateway.commit`, archive writers, cache/vector writers
- Allowed: proposal types, `CommitRequest`, contracts, typed exceptions
- apps_rg may construct proposals or CommitRequest candidates only

**CI Bypass Discipline**:
- Bypass env vars allowed only in local developer mode
- CI strict mode ignores bypass env vars
- Any bypass emits visible receipt: `BYPASS_RECEIPT: gate=<name> reason=<env_var> actor=<user>`
- Protected branches fail on bypass (bypass-receipt=BLOCK)

**Acceptance**:
- Filesystem gate fails if `write_text`, `write_bytes`, `json.dump`, `pickle.dump`, `shutil.copy`, `sqlite3.connect` with non-temp paths found outside allowlist
- Chroma gate fails if mutations found in live runtime paths
- L4 import gate fails if direct writer imports found
- All gates registered with `*_FAIL_CLOSED=1` strict mode for CI
- `pytest tests/unit/ops_scripts/ci/test_check_*_writes.py -v` passes

---

## Wave 6 — Compliance Verification & Non-Contamination Proof

WAVE_ID: W6
WAVE_STATUS: TODO
WAVE_COMPLETE: NO
AUTHORIZATION_STATUS: NOT_REQUIRED
CHECKPOINT: F

**Phases**:
- **W6.1** — Add apps_rg tests asserting UWG receipt refs present when returned | ~0.8K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.2** — Full compliance verification run | ~0.7K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.3** — Produce non-contamination proof (agentic_core purity) | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO
- **W6.4** — Final documentation & memory writeback | ~0.5K tokens | PHASE_STATUS: TODO | PHASE_COMPLETE: NO

**W6.1 Clarification**: Tests only — no UWG modifications. Tests assert that when UWG returns `StateCommitReceipt`, the admitted cache entries carry UWG receipt refs. Tests mock UWG response; do not modify UWG implementation.

**W6.3 Non-Contamination Proof**:
- AST/grep proof that `agentic_core` has no apps_rg literals introduced by this plan
- No resume section names in `agentic_core`
- No apps_rg namespace constants in `agentic_core`
- No app-owned L4 manifest embedded in core
- Diff review: zero changes under `agentic_core/` except via separate core-enabling plan

**Acceptance**:
- `python ops_scripts/ci/run_contract_gates.py` exits 0
- No apps_rg L4 violations
- No direct cache writes
- No direct Chroma runtime writes
- No direct filesystem durable writes outside allowlist
- No Exit writer paths
- No quarantined L6 importers
- AST proof: `grep -r "apps_rg" agentic_core/` returns only pre-existing legitimate references (none added by this plan)

**No Cache Read Regression (W1/W6)**:
- Semantic cache read path still works if cache records already exist
- Read path is governed/read-only
- No write occurs on cache miss
- Cache miss returns proposal candidate only after Exit path, not during retrieval/routing

---

## Generated Artifact Policy

apps_rg creates resume artifacts. This plan explicitly governs artifact durability:

**Allowed** (no UWG required):
- Final user-visible artifact generation as response payload
- Staged temp artifacts for immediate user download (with retention, path scope, non-L4 classification)

**Requires CommitRequest/UWG**:
- Durable artifact metadata storage
- Durable artifact body storage (unless user download temp)
- Any write to `artifacts/apps_rg/runs/<ts>/` with persistence > 24h

**Temp Download Artifacts**:
- Retention: ≤ 24 hours or user session bound
- Path scope: `temp/` or `staging/` subdirectory (not `artifacts/`)
- Non-L4 classification: explicitly marked non-durable, non-replay

## Out Of Scope

- Implementing real L6 shadow learning engine (apps_rg should use canonical `agentic_core/L6_learning/package_driven_l6_binding.py`)
- Real LLM-judge implementations for eval harness (covered in deferred plan)
- Chroma ingestion/index refresh offline pipeline (separate ingestion plan)
- OTel span emitter bridge implementation (telemetry infrastructure, not boundary hardening)
- UWG implementation itself (assumes UWG exists in `agentic_core/L4_state/uwg/`)
- Changes to `agentic_core` generic contracts. Generic L4 namespace parser work belongs only to companion plan `core-l6-g29-promotion-proof-hardening-d9e3b2`.

---

## Gap Register

**GAP-1: G2 Direct Semantic Cache Write (P0 BLOCKER)**
- Location: `apps_rg/runtime/section_agentic_pipeline.py:72,246`
- Violation: Direct import and call to `write_section_to_semantic_cache` bypasses UWG
- Impact: Current run mutates durable state without admission control; violates L4 boundary
- Close criteria: Inert proposal pattern implemented, CI gate passes

**GAP-2: G1 Dead L6 Shadow Learning Engine (HIGH)**
- Location: `apps_rg/runtime/l6_shadow_learning.py`
- Violation: Duplicate of canonical core types, zero external importers
- Impact: Architectural confusion, code bloat, potential future misuse
- Close criteria: File quarantined, no imports break

**GAP-3: G3 Missing L4 Namespace Manifest (HIGH)**
- Location: `apps_rg/config/` (missing)
- Violation: No typed, versioned, ACL-bound manifest for read surfaces
- Impact: Read surfaces not governed, replay/audit bindings undefined
- Close criteria: Manifest exists with 10 surface definitions and validates against apps_rg-local schema. If generic core validator is absent, tests xfail gracefully until companion core plan lands.

**GAP-4: G4 Direct Filesystem Writes (HIGH — PENDING W0 CLASSIFICATION)**
- Location: `apps_rg/runtime/bindings/exit_binding.py:120`, `apps_rg/cache/r1b_semantic.py:55,62`
- Violation: Direct filesystem write patterns found
- W0 Classification Required: Before implementation, verify whether each is: (a) live runtime durable write, (b) sandbox/temp write, (c) test fixture write, (d) artifact staging for user download, (e) dead code
- Evidence: `@exit_binding.py:108-121` (`_write_artifact` with `path.write_text`); `@r1b_semantic.py:54-68` (direct `write_text` and `open(..., "a")`)
- Close criteria: All live runtime durable writes removed or UWG-mediated; sandbox/temp/downloads properly classified in allowlist 
