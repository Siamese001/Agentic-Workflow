---
status: Archived
do_not_execute: true
memorialized: true
source_surface: recovered_docs_reports_plans
source_key: windsurf-docs
original_path: 'C:\\Git\\windsurf-plans-recovered\\docs_reports_plans\\infra_wiring_findings.md'
original_relative_path: 'infra_wiring_findings.md'
source_sha256: 6fa228057958dfa58de58bb3b6d5d8187eeeea845432655c22bebd43a8506778
recovered_status: LOST_RECOVERED
last_commit: 'e941e3e9e0e'
last_commit_date: '2026-04-11 22:12:51 -0400'
created_date: '2026-04-08'
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# Infrastructure Wiring Findings — Phase 3

**Generated:** 2026-04-11
**ADG Snapshot:** `adg_indexed_04112026_1604.sqlite`
**Rebuild:** `python tools/generate_full_adg.py` — exit 0, all 4 CI gates PASS
**Scorecard:** `artifacts/infra_wiring_scorecard.json`
**Methodology:** Conservative and evidence-based. Every finding tagged:
- **PROVEN_SCAN** — confirmed by `infra_wiring_scan.py` file-level pattern scan
- **PROVEN_ADG** — confirmed by ADG structural view after rebuild
- **FILE_ONLY** — confirmed by direct file read; ADG view blind (reason noted)
- **EXPECTED_ABSENT** — Phase 2 predicted; did not surface; visibility limitation documented

---

## A. Executive Summary

Phase 3 rebuild with the Phase 2 detection layer surfaced **10 distinct findings** across 3 severity levels:

| Severity | Count | Status |
|---|---|---|
| P1 Hardening | 7 | 3 PROVEN_SCAN + 4 PROVEN_ADG |
| P2 Warning | 5 | 2 PROVEN_ADG + 3 FILE_ONLY |
| P3 Watch | 2 | PROVEN_ADG |

**Compliance score dropped from 100% → 96%** — expected; the drop reflects newly visible detections, not regressions.

**Reconciliation note (2026-04-11):** Waves A, B, C (partial), vLLM Path A, OTel bypass, and retrieval_layers fixes are complete. Current scan: P0=0 P1=0. Compliance restored to 100%. See repair plan for per-item resolution status.

Three ratchets now show **BLOCK** status:
- `apps_* direct infra access` — 3 google-import violations in `agentic_core/` (scan-ratchet label mismatch, findings real)
- `zero-caller infra` — 2 adapters registered but never called
- `not on L0-L6 spine` — same 2 adapters absent from execution path

Two high-value visibility limitations remain (§E):
- Raw aiohttp in `optimized_vllm_client.py` — **file-proven but ADG-invisible**
- `neo4j_store.py` zero-caller — **expected but absent from ADG views** (indexing gap)

No P0 hard failures. No UWG write bypasses. No apps_* direct infra access (`v_p0_apps_direct_infra = 0`).

---

## B. Rebuild Validation and Current Scorecard Snapshot

### Rebuild result
```
generate_full_adg.py — exit 0
All 4 CI gates: PASS (G1 executor_reachability, G2 claim_to_execution, G3 import_only_capability, G4 production_classif.)
ADG rebuild timestamp: 04112026_1604
Redis hot cache: HOT
```

### Scorecard delta

| Metric | Phase 1 (pre-Phase 2) | Phase 3 (post-rebuild) | Delta |
|---|---|---|---|
| `total_infra_surfaces` | 10 | 13 | +3 |
| `compliance_score` | 100% | 96% | -4 |
| `violations.p0` | 0 | 0 | — |
| `violations.p1` | 0 | 4 | +4 |
| `violations.p2` | 5 | 5 | — |
| `violations.p3` | 5 | 6 | +1 |
| `v_p1_zero_caller_infra` | 0 | 2 | +2 |
| `v_p1_not_on_spine` | 0 | 2 | +2 |
| `v_p1_raw_http_outside_seam` | N/A | 0 | ADG blind |
| `v_p0_provider_bypass` | 0 | 0 | ADG blind (3 file-scan) |
| `v_p3_isolated_experimental` | 5 | 6 | +1 |
| Ratchets BLOCKING | 0 | 3 | +3 |

### ADG view counts (post-rebuild)

```
v_p0_apps_direct_infra:     0
v_p0_provider_bypass:       0   <- ADG blind to lazy method-body imports
v_p0_write_bypass_uwg:      0
v_p0_l1_direct_infra:       0
v_p0_l6_mutation:           0
v_p0_l0_raw_execution:      0
v_p1_zero_caller_infra:     2   <- NEW: blob_storage_provider + cache/core/redis
v_p1_not_on_spine:          2   <- NEW: same 2 files
v_p1_ad_hoc_imports:        0
v_p1_mis_layered_infra:     0
v_p1_raw_http_outside_seam: 0   <- ADG blind to external package nodes
v_p2_mixed_usage:           3
v_p2_duplicated_adapters:   2
v_p2_dormant_ambiguous:     0
v_p3_isolated_experimental: 6
```

File scan violations (separate from ADG views): **3 google-import violations** in `agentic_core/` paths.

---

## C. Findings by Severity

---

### P1 — HARDENING FAIL

---

#### F-P1-001 — Provider Bypass: GeminiJudge (llm_judge.py)
**Evidence:** PROVEN_SCAN + FILE_ONLY
**infra_surface:** `google.generativeai`
**File/symbol:** `agentic_core/evaluation/judges/llm_judge.py:264`
```python
import google.generativeai as genai   # inside GeminiJudge._get_client() method body
```
**Violated law:** Provider imports must route through `infrastructure/sdks_mcps/__init__.py` or the
sanctioned Google adapter `apps_shared/utils/providers_google_genai_client_util.py`.
`agentic_core/evaluation/` is NOT in `_PROVIDER_EXEMPT_PREFIXES`.
**Why it matters:** `GeminiJudge` creates live Gemini API connections inside the evaluation harness
without going through the provider control plane. This bypasses rate limiting, key rotation, and
audit logging enforced by the sanctioned adapter. The lazy-import pattern hides the coupling from
static analysis and the ADG.
**Confidence:** HIGH — direct file evidence, line 264 confirmed.
**ADG visibility:** `v_p0_provider_bypass = 0` — ADG cannot capture method-body lazy imports as
static `imports` edges. Scanner catches it via `.strip()` of raw line text.
**Remediation:** Replace `import google.generativeai` with an injected `gemini_client` parameter
(already supported: `__init__(self, gemini_client=None, ...)`). Callers pass a client created via
`create_vertex_client()` from `infrastructure/sdks_mcps`.
**Repair type:** Code repair (Phase 4). Can be batched with F-P1-002.

---

#### F-P1-002 — Provider Bypass: GeminiJudgeProvider (provider_registry.py)
**Evidence:** PROVEN_SCAN + FILE_ONLY
**infra_surface:** `google.generativeai`
**File/symbol:** `agentic_core/evaluation/judges/provider_registry.py:92`
```python
import google.generativeai as genai   # inside GeminiJudgeProvider._get_client() method body
```
**Violated law:** Same as F-P1-001. Duplicate provider bypass in the same module tree.
**Why it matters:** Two files in `agentic_core/evaluation/judges/` independently bypass the Google
provider control plane. Neither file injects the SDK client; both self-provision on first call.
API key management changes require patching both files independently.
**Confidence:** HIGH — direct file evidence, line 92 confirmed.
**ADG visibility:** Same as F-P1-001 — ADG blind to lazy method-body imports.
**Remediation:** Accept `gemini_client` at construction time. `create_default_registry()` should
create the client via `infrastructure/sdks_mcps` and inject it.
**Repair type:** Code repair (Phase 4). Same PR as F-P1-001.

---

#### F-P1-003 — Provider Bypass with Wrong Guardian Exemption (dependencygraph_validator.py)
**Evidence:** PROVEN_SCAN + FILE_ONLY
**infra_surface:** `google.generativeai`
**File/symbol:** `agentic_core/L5_safety/validators/dependencygraph_validator.py:179-182`
```python
try:
    from google import genai
except ImportError:  # guardian: allow-silent-swallow
    genai = None
```
**Violated law:** (1) Provider import outside sanctioned adapter. (2) Guardian exemption type
mismatch — `allow-silent-swallow` exempts silent exception swallowing, NOT provider imports.
`allow-provider-bypass` would be required, and that itself requires HITL approval (constitutional §8).
**Why it matters:** L5 Safety is the policy enforcement layer. A misguarded provider import appears
exempted but isn't — `guardian_exemption_gate.py` looks at the type string and will not flag it,
creating a false sense of compliance.
**Confidence:** HIGH — direct file evidence, lines 179-182 confirmed.
**ADG visibility:** ADG blind (try/except module-level import; captured by file scanner).
**Remediation:** Either (a) remove Google dependency from L5 validator entirely, or (b) route
through `infrastructure/sdks_mcps` and obtain `# guardian: allow-provider-bypass -- <HITL justification>`.
**Repair type:** Code repair + policy decision. Requires HITL for exemption type change.

---

#### F-P1-004 — Zero-Caller Infra Adapter: blob_storage_provider.py
**Evidence:** PROVEN_ADG (`v_p1_zero_caller_infra`, `v_p1_not_on_spine`)
**infra_surface:** `boto3` / S3
**File/symbol:** `agentic_core/L4_state/utils/memory/blob_storage_provider.py`
ADG query: `adapter_id=685, caller_count=0, adapter_layer=L4`
**Violated law:** P1-7 (critical infra adapter with no approved runtime caller). The adapter is in
`SANCTIONED_ADAPTER_FILES` and `_APPROVED_ADAPTER_PATHS`, but `canonical_store.py` (declared
consumer) only imports `botocore.exceptions` for error handling — it does NOT import `blob_storage_provider`.
**Why it matters:** `blob_storage_provider.py` is the declared S3/Boto3 seam but has no actual
consumers. If S3 operations exist, they reach boto3 via a path invisible to this adapter.
The Boto3 surface may be uncontrolled.
**Confidence:** HIGH — ADG structural evidence confirmed.
**Remediation:** (a) If S3 genuinely unused: remove from SANCTIONED, reclassify as DORMANT.
(b) If S3 is used: trace the actual boto3 consumer and route it through `blob_storage_provider`.
**Repair type:** Investigation first → registry fix or code repair.

---

#### F-P1-005 — Zero-Caller Infra Adapter: cache/core/redis_cache_client.py
**Evidence:** PROVEN_ADG (`v_p1_zero_caller_infra`, `v_p1_not_on_spine`)
**infra_surface:** `redis`
**File/symbol:** `agentic_core/cache/core/redis_cache_client.py`
ADG query: `adapter_id=1492, caller_count=0, adapter_layer=L_SHARED`
**Violated law:** P1-7 (zero-caller infra) + P1-8 (not on spine). Dead duplicate of the canonical
Redis adapter at `agentic_core/cache/redis_cache_client.py` (without `/core/`), which IS called.
**Why it matters:** Two Redis adapters exist with nearly identical paths. The `/core/` variant is
dead code. Having a dead sanctioned adapter creates confusion about the canonical path and inflates
the approved-adapter registry.
**Confidence:** HIGH — ADG confirms 0 callers; `v_p2_duplicated_adapters=2` confirms the duplicate.
**Remediation:** Deprecate `cache/core/redis_cache_client.py` and remove from SANCTIONED +
APPROVED after confirming no active callers. Document `cache/redis_cache_client.py` as sole
canonical Redis path.
**Repair type:** Registry fix — no runtime code change needed.

---

#### F-P1-006 — Not on L0-L6 Spine (same files as F-P1-004 and F-P1-005)
**Evidence:** PROVEN_ADG (`v_p1_not_on_spine`)
**Note:** `blob_storage_provider.py` (L4) and `cache/core/redis_cache_client.py` (L_SHARED) each
produce one `v_p1_not_on_spine` row. These are the P1-8 counterpart violations to F-P1-004/005.
Both rows counted in scorecard `violations.p1 = 4`.

---

### P2 — WARNING

---

#### F-P2-001 — Mixed Raw/Wrapped Usage: retrieval_layers.py
**Status: PARTIALLY RESOLVED (2026-04-11)**
**Evidence:** PROVEN_ADG (`v_p2_mixed_usage` = 3) + FILE_ONLY
**infra_surface:** `chromadb`, `openai`
**File/symbol:** `agentic_core/L4_state/reasoning/retrieval_layers.py:20-21`

**OpenAI bypass: RESOLVED** — `from openai import OpenAI` replaced with `create_openai_sync_client()` from `infrastructure.sdks_mcps`. Guardian comment added. Both `L2SemanticCache.__init__` and `L3SemanticRAG.__init__` now use the sanctioned seam.

**ChromaDB raw import: REMAINS** — `import chromadb` at line 20 is the remaining mixed-usage item (at accepted P2 ceiling of 3). `v_p2_mixed_usage` count unchanged — ADG counts chromadb edges, not openai.
**Remediation:** ChromaDB injection deferred — accepted ceiling, no regression.

---

#### F-P2-002 — Lazy Provider Import: semantic_enricher.py
**Status: RESOLVED (2026-04-11)**
**Evidence:** FILE_ONLY
**infra_surface:** `openai`

**Resolution (R-B3):** `from openai import OpenAI` inside `_init_default_client()` replaced with `create_openai_sync_client()` from `infrastructure.sdks_mcps`. Guardian comment added. `try/except (ImportError, ValueError)` preserves mock fallback on missing key or missing package.

---

#### F-P2-003 — OTel Bypass: apps_tracing_mixin.py
**Status: RESOLVED (2026-04-11)**
**Evidence:** FILE_ONLY
**infra_surface:** `opentelemetry`

**Resolution:** `apps_shared/mixins/apps_tracing_mixin.py` now imports `OTEL_AVAILABLE` from `apps_shared/utils/open_telemetry_tracing_adapter_util` (canonical adapter) and conditionally imports raw `trace`/`Status`/`StatusCode` only when the adapter confirms availability. The independent `try/except ImportError` bypass is eliminated. Runtime graceful degradation preserved.

---

#### F-P2-004 — Duplicated Adapters: Redis (two canonical paths)
**Evidence:** PROVEN_ADG (`v_p2_duplicated_adapters` = 2)
**infra_surface:** redis
**Files:** `agentic_core/cache/redis_cache_client.py` (active, called) vs
`agentic_core/cache/core/redis_cache_client.py` (dead, zero callers — see F-P1-005).
Multi-adapter pattern; accepted at ceiling=2. Ceiling must not regress.

---

#### F-P2-005 — Duplicated Adapters: SQLite (multi-registry pattern)
**Evidence:** PROVEN_ADG (`v_p2_duplicated_adapters` = 2)
**infra_surface:** sqlite3
**Why it matters:** Multiple SQLite adapter files independently open connections without a unified
write coordinator. Accepted by design; ceiling=2 enforces no regression.

---

### P3 — WATCH

---

#### F-P3-001 — Isolated Experimental: L2 Sandbox Files (4 files)
**Evidence:** PROVEN_ADG (`v_p3_isolated_experimental`)
**Files:**
- `agentic_core/L2_execution/enforcement/docker_sandbox.py` (node 288)
- `agentic_core/L2_execution/enforcement/preventative_sandbox.py` (node 300)
- `agentic_core/L2_execution/enforcement/sovereign_sandbox_isolation.py` (node 306)
- `agentic_core/L2_execution/types/sandbox_envelope_types.py` (node 377)

All 4 have 0 incoming callers. L2 enforcement layer. WATCH for accidental adoption without
architecture review.

---

#### F-P3-002 — Isolated Experimental: ADG Sandbox Airlock (2 files)
**Evidence:** PROVEN_ADG (`v_p3_isolated_experimental`)
**Files:**
- `agentic_core/adg/_compat/sandbox_airlock.py` (node 1287, L_TOOLS)
- `agentic_core/adg/runtime/sandbox_airlock.py` (node 1463, L_TOOLS)

0 incoming callers; tooling layer. One of these is the +1 new entry (was 5, now 6).

---

## D. Highest-Leverage First Patch Candidates

Ranked by: severity × caller-count-at-risk × ease of fix.

| Rank | Finding | Fix Type | Risk | Batch-able? |
|---|---|---|---|---|
| 1 | F-P1-001 + F-P1-002 (Gemini judge bypasses) | Code: inject client at construction | Medium — 2 files, same pattern | YES — same PR |
| 2 | F-P1-005 (dead `cache/core/redis_cache_client.py`) | Registry: remove from SANCTIONED + APPROVED | Low — 0 callers | YES — with #4 |
| 3 | F-P1-003 (dependencygraph_validator wrong guardian) | Code + policy: fix guard or remove Google dep | Low — L5 validator only | Solo PR + HITL |
| 4 | F-P1-004 (blob_storage_provider zero callers) | Investigation → registry fix or DORMANT | Medium — confirm S3 usage first | After investigation |
| 5 | F-P2-003 (apps_tracing_mixin OTel bypass) | Code: use canonical OTel adapter | Low — graceful degradation in place | YES — tracing refactor |

---

## E. False-Negative / Visibility Limitations Still Remaining

### E-1 — Raw aiohttp in optimized_vllm_client.py: RESOLVED (2026-04-11)
**Evidence:** FILE_ONLY (proven by direct read)
**Location:** `agentic_core/L3_orchestration/inference/qwen_vllm/engines/optimized_vllm_client.py:21-22`

**Resolution:** vLLM Path A approved via `docs/reports/plans/vllm_http_decision_packet.md` (2026-04-11). `optimized_vllm_client.py` added to `_APPROVED_ADAPTER_PATHS` in `tools/generate/infra_wiring_views.py` and reclassified from `UNDER_REVIEW` to `APPROVED` in `ops_scripts/ci/infra_wiring_scan.py`. Sanctioned seam contract comment block added to file. `v_p1_raw_http_outside_seam = 0` (ADG-blind by design — external PyPI packages not in ADG nodes; file-scan exclusion clause added to `_VIEW_P1_RAW_HTTP_OUTSIDE_SEAM` SQL). ADG visibility limitation documented as permanent — no further action required.

### E-2 — neo4j_store.py Absent from v_p1_zero_caller_infra
**Expected:** Phase 2 predicted neo4j_store.py would appear with 0 callers after rebuild.
**Actual:** `v_p1_zero_caller_infra` shows only `blob_storage_provider` and `cache/core/redis`.
`neo4j_store.py` is absent from all ADG views.
**Root cause (hypothesis):** `neo4j_store.py` has 130+ `_emit_` module-level calls before any class
definition, plus an unusual try-block at lines 88-93 with a bare string literal, followed by the
import. The ADG static scanner may have failed to fully resolve this file's `resolved_path`, or
it may be excluded by a path pattern. The `raise ImportError(...)` before `GraphDatabase = None`
also makes the fallback dead code — a broken guard that may have caused parse-time issues.
**Manual confirmation:** File is at `agentic_core/L4_state/enforcement/neo4j_store.py`. Direct
read confirms `from neo4j import GraphDatabase` at line 90 and zero callers by Phase 1 analysis.
The zero-caller state is real even if ADG views don't surface it.
**Severity (file-proven):** P3 Watch — EXPERIMENTAL_ISOLATED.

### E-3 — v_p0_provider_bypass = 0 Despite 3 Confirmed Google Imports
**Root cause:** `v_p0_provider_bypass` detects `imports` edges from non-exempt nodes to provider
SDK module nodes. Lazy imports inside method bodies (`def _get_client(self): import google...`)
create no static `imports` edge in the ADG. All lazy-import provider bypasses are permanently
invisible to ADG structural views.
**Impact:** The file scanner is the only defense for this pattern class. Phase 2 correctly added
`"import google"` / `"from google"` to `FORBIDDEN_IMPORTS` — the scanner detects all 3 violations.
But the ADG cannot enforce them at scale without AST-level support for deferred imports.

---

## F. Open Ambiguities That Block Repair or CI Decisions

### §FA — agentic_core/evaluation/ Provider Exemption Policy
**Question:** Should `agentic_core/evaluation/` be added to `_PROVIDER_EXEMPT_PREFIXES`?
**Against:** Sanctioned path exists; client injection is already supported — no technical need.
**Decision rule:** Conservative. Do not add exemption. Prefer client injection fix (F-P1-001/002).
**Blocks:** CI ratchet ceiling for provider bypass.

### §FB — blob_storage_provider.py S3 Usage Confirmation
**Question:** Is S3/Boto3 actively used anywhere in production paths?
**Evidence against usage:** `blob_storage_provider.py` has 0 ADG callers. `canonical_store.py`
only imports `botocore.exceptions` (error handling), not `blob_storage_provider`.
**Decision needed:** Confirm whether any production path uses S3. If not, reclassify as DORMANT
and remove from approved/sanctioned lists.
**Blocks:** F-P1-004 remediation strategy.

### §FC — optimized_vllm_client.py Architecture Decision — RESOLVED (2026-04-11)
**Decision: Path A approved.** `optimized_vllm_client.py` added to `_APPROVED_ADAPTER_PATHS` and reclassified APPROVED in `SANCTIONED_ADAPTER_FILES`. Seam contract comment block added. `v_p1_raw_http_outside_seam = 0`. ADG-blind by design (external PyPI). CI ratchet question closed — ceiling is 0 with file-scan exclusion clause in SQL.

### §FD — dependencygraph_validator.py Google Dependency Purpose — RESOLVED (2026-04-11)
**Decision: R-C1 executed.** `from google import genai` removed; `ValidationContext._init_intelligence()` now calls `create_vertex_client()` via sanctioned seam. Graceful no-op preserved when `GOOGLE_API_KEY` absent. File-scan violation cleared.

### §FE — neo4j_store.py: Deprecate or Formalize? — CONFIRMED EXPERIMENTAL_ISOLATED (2026-04-11)
**Question:** Should Neo4j remain in P3 Watch or escalate?
**Evidence:** Broken guard pattern (dead fallback), zero ADG callers confirmed, EXPERIMENTAL_ISOLATED.

**Audit result (2026-04-11):** Zero-caller classification confirmed via ADG fan-in (node 613, 0 import edges) and direct file analysis. The only caller candidate (`apps_shared/utils/rank_observability_components_util.py` line 187) has a broken guard catching `(ValueError, TypeError, RuntimeError)` but NOT `ImportError` — meaning when neo4j is absent, both files fail to import. Effective live caller count: 0. Classification EXPERIMENTAL_ISOLATED is correct and internally consistent across all enforcement surfaces (scan.py, views.py, ownership matrix).

**Decision deferred:** Deprecate-vs-formalize remains open. P3 Watch status retained. No escalation to P1 — zero-caller state is expected and documented. No action required in Phase 4 repairs.

---

*Phase 3 findings complete. Repair wave (Phase 4) may proceed starting with Rank-1 candidates from §D.
CI ratchets should not be tightened until Phase 4 repairs are committed.*
