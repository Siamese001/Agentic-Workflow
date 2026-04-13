# Architectural Gap Register — Agentic Best Practices vs. Implementation

**Date:** 2026-04-13  
**Scope:** Cross-layer gap analysis comparing documentation specs, 10C-REQ requirements, and UWG_ISOLATION_SPEC against actual implementation stubs, dead paths, and open-by-default guards.  
**Trigger:** UWG `WriteGateway` was unimplemented (`raise RuntimeError("Write gateway not configured")`); this register identifies all analogous gaps.

---

## Severity Key

| Severity | Meaning |
|---|---|
| **CRITICAL** | Core enforcement pipeline bypassed; doc contract unmet in production write path |
| **HIGH** | Named architectural component exists in code but is hollow; spec requirement unfulfilled |
| **MEDIUM** | Component implemented but not wired into calling pipeline; dead at runtime |
| **LOW** | Spec describes future capability; no enforcement gap in current scope |

---

## GAP-01 — UWGClerk._process_request Bypasses Entire UWG Pipeline

| Field | Value |
|---|---|
| **Severity** | CRITICAL |
| **File** | `agentic_core/L4_state/enforcement/uwg_clerk.py:88-100` |
| **Spec ref** | 10C-REQ-122; UWG_ISOLATION_SPEC §IPC Protocol; UWG doc §2.0–§4.0 |
| **Status** | ❌ Stub — comment confirms: _"actual implementation calls verifier, catalog, locker, committer"_ |

**Doc says:** Every write request flows U1 → U2 (verify) → U3 (catalog/blast-radius) → U4 (lock) → U5 (commit) → U6 (refresh). The Clerk is the *orchestrator* of that pipeline.

**Code does:** `_process_request` increments a counter and generates a synthetic `commit_hash` directly. Stages U2–U6 are never called.

**Impact:** The newly implemented `PromotionWriteGateway` plumbs into `UWGClerk.submit()`, which routes into this stub. All downstream guards (RBAC, blast radius, write lock, alias swap) are silently bypassed. The durable ledger write (`UWGCommitter.commit()`) is called correctly by `PromotionWriteGateway` — but only because it circumvents the Clerk. Any other caller going through the Clerk gets no enforcement.

**Closure action:** Wire `_process_request` to call `UWGVerifier` → `UWGCatalogChecker` → `UWGLocker.acquire()` → `UWGCommitter.commit()` → `UWGLocker.release()` → `UWGRefresher.refresh()` in sequence. Return `None` (rejected) on any stage failure.

---

## GAP-02 — UWGCatalogChecker Blast Radius Always Returns 0.1 (ADG Not Called)

| Field | Value |
|---|---|
| **Severity** | HIGH |
| **File** | `agentic_core/L4_state/enforcement/uwg_catalog_checker.py:114-122` |
| **Spec ref** | 10C-REQ-124; UWG doc §2.3 "Blast Radius Check" |
| **Status** | ❌ Stub — always returns `BlastRadius(file_count=1, risk_score=0.1)` |

**Doc says:** "The Commandant verifies the Restorer isn't trying to rewrite too many books at once." Blast radius must query the ADG dependency graph to count affected files, downstream dependencies, and layer crossings.

**Code does:** Hardcodes `file_count=1, risk_score=0.1` regardless of write target. Threshold check (`risk_score <= 0.5`) always passes.

**Closure action:** Call `mcp1_adg_edge_fanout` / `mcp1_adg_edge_fanin` on `request.path` to count real downstream dependents. Populate `BlastRadius.downstream_dependencies`, `layer_crossings`, and compute `risk_score` proportional to dependent count and layer crossing count.

---

## GAP-03 — UWGCatalogChecker Structure Check Always Returns True

| Field | Value |
|---|---|
| **Severity** | HIGH |
| **File** | `agentic_core/L4_state/enforcement/uwg_catalog_checker.py:143-146` |
| **Spec ref** | 10C-REQ-124; UWG doc §2.1 "Target Resolution" + §2.2 "RBAC Verification" |
| **Status** | ❌ Stub — `return True` unconditionally |

**Doc says:** Structure check must verify layer gravity (L0→L6 ordering), import boundaries, and structural constraints before approving a write.

**Code does:** Always approves.

**Closure action:** Implement layer-gravity check: resolve `request.path` to an ADG node, check that the write actor's layer (from `actor_id` prefix) does not violate L0→L6 flow direction. Check `self._structure_rules` against the path.

---

## GAP-04 — UWGVerifier is Open-by-Default (All Guards Vacuous When Registries Empty)

| Field | Value |
|---|---|
| **Severity** | HIGH |
| **File** | `agentic_core/L4_state/enforcement/uwg_verifier.py:81-115` |
| **Spec ref** | UWG_ISOLATION_SPEC §Stale Policy Hash Rejection; §Signed ExecutionTrace; 10C-REQ-123 |
| **Status** | ⚠️ Implemented but open-by-default — empty registries → all checks pass |

**Doc says:** All writes require: valid actor authorization, current-epoch policy hash, valid compliance hash, and HMAC-SHA256 signature. A write with an unsigned or stale-policy request must be rejected.

**Code does:**
- `_verify_actor`: `if not self._allowed_actors: return True` — no registry configured at startup → every actor passes
- `_verify_compliance`: same pattern — empty registry → pass
- `_verify_policy`: same pattern — empty registry → pass; **no epoch tracking**
- `_verify_signature`: `if not request.signature: return True` — unsigned requests pass

**Closure action:** `UWGVerifier.__init__` should reject writes when registries are empty unless an explicit `allow_open=True` flag is set (off by default). Policy hash verification must compare against a current-epoch hash computed from an active `PolicyStore`, not a static dict.

---

## GAP-05 — UWGLocker Not Called from Write Pipeline

| Field | Value |
|---|---|
| **Severity** | MEDIUM |
| **File** | `agentic_core/L4_state/enforcement/uwg_locker.py` (correct) vs `uwg_clerk.py:88-100` (stub) |
| **Spec ref** | 10C-REQ-125: "Prevent ghost writes overlapping mutations claim exclusive write-access" |
| **Status** | ⚠️ Component implemented; never wired |

**Doc says:** Stage U4 must acquire an exclusive write lock before the commit. If lock fails → request rejected. Lock released after commit.

**Code does:** `UWGLocker` is correctly implemented (mutex, timeout, per-path locking). `UWGClerk._process_request` never instantiates or calls it.

**Closure action:** Resolved by GAP-01 closure — wire `UWGLocker.acquire()` before `UWGCommitter.commit()`, release in `finally`.

---

## GAP-06 — UWGRefresher Not Called After Commit (Alias Swap Never Happens)

| Field | Value |
|---|---|
| **Severity** | MEDIUM |
| **File** | `agentic_core/L4_state/enforcement/uwg_refresher.py` (correct) vs `uwg_clerk.py:88-100` (stub) |
| **Spec ref** | 10C-REQ-127: "Execute alias swap clear retrieval caches ensure very next request sees updated state"; UWG doc §5.0–§5.4 |
| **Status** | ⚠️ Component implemented; never wired |

**Doc says:** After commit, the Clerk must: atomically swap the read alias, clear retrieval caches, and force vector index recalculation. "This guarantees the Senior Research Librarian (L1) never pulls stale context."

**Code does:** `UWGRefresher` is correctly implemented (alias swap, cache clear handlers, read surface refresh handlers). Never called.

**Closure action:** Resolved by GAP-01 closure — call `UWGRefresher.refresh(request)` after successful `UWGCommitter.commit()`.

---

## GAP-07 — TieredVectorStore Warm Storage Fallback Not Implemented

| Field | Value |
|---|---|
| **Severity** | MEDIUM |
| **File** | `agentic_core/L4_state/utils/memory/in_memory_vector_cache.py:396` |
| **Spec ref** | `TieredVectorStore` docstring: "Two-tier vector storage: hot in-memory cache + warm disk storage. Automatically promotes frequently accessed items to hot cache." |
| **Status** | ❌ Stub — `Logger.warning("Warm storage fallback not yet implemented"); return empty` |

**Doc says:** On hot cache miss, fall through to warm storage (Qdrant at `warm_store_url`). Results should be promoted to hot cache for next access.

**Code does:** Returns `{"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}` on every hot cache miss.

**Impact:** Any search that misses the in-memory cache silently returns no results. Callers receive empty results with no error, making this an invisible data loss.

**Closure action:** Implement `_query_warm_store(query_embeddings, top_k)` using the `enhanced_http` MCP to POST to Qdrant's `/collections/{name}/points/search` endpoint. On successful warm result, promote to hot cache via `self.hot_cache.add(...)`.

---

## GAP-08 — L5 Agents: heal() Universally Unimplemented (15+ Agents)

| Field | Value |
|---|---|
| **Severity** | HIGH (systemic) |
| **Files** | `L5_safety/reasoning/GospelSyncAgent.py`, `GovernanceAgent.py`, `IntegrityGateExecutorAgent.py`, `InterfaceBoundaryAgent.py`, `L5SafetyExerciserAgent.py`, `NeuralAutoImmuneAgent.py`, `PolicyNeuralAutoImmuneAgent.py`, `PreCommitSovereignAgent.py`, `PredictiveCostAuditorAgent.py`, `RegressionOracleAgent.py`, `SprawlInspectorAgent.py`, `EmbeddingSovereignAgent.py`, `RedisSovereignAgent.py`, `SubAtomicRegistryAgent.py` + others |
| **Spec ref** | `C3_Healing_Remediation_Escalation.md §LOCAL HEAL FIRST` |
| **Status** | ❌ All return `{"status": "skipped", "details": "... heal() not yet implemented"}` |

**Doc says:** C3 specifies a full three-tier healing router: (1) **high confidence** → deterministic local rule fix, (2) **medium confidence** → Qwen_vLLM structured repair, (3) **low confidence** → Gemini_2.5_Pro deep reasoning. "Attempt deterministic rule fix (e.g., schema repair, known type casting)" at LOCAL HEAL FIRST. Unhealed violations escalate up Path D to human review.

**Code does:** Every `heal()` returns `skipped` regardless of violation type. The entire C3 healing loop is architecturally specified but produces zero concrete repair actions.

**Closure action (by priority):**
1. Implement deterministic local heal for the agents most frequently triggered: `InterfaceBoundaryAgent` (import boundary violations → auto-fix import path), `SprawlInspectorAgent` (unused file → move to archive), `PreCommitSovereignAgent` (pre-commit hook failures → retry with corrected path).
2. Wire remaining agents to the `HealingTierRouter` (if it exists) or implement it.

---

## GAP-09 — GitHub MCP Healing Integration Missing (Commit + PR Creation)

| Field | Value |
|---|---|
| **Severity** | MEDIUM |
| **File** | `agentic_core/L5_safety/enforcement/git_kraken_healing_strategy.py:297-328` |
| **Spec ref** | L0 healing flow; GitKraken MCP is available (`mcp0_git_add_or_commit`, `mcp0_pull_request_create`) |
| **Status** | ❌ Logs warning "not yet implemented" and returns `None`/`False` |

**Doc says:** L0 healing should commit repaired files and open PRs through the GitHub MCP integration.

**Code does:** Warnings only. No commit, no PR.

**Closure action:** Replace placeholders with calls to `mcp0_git_add_or_commit(action="commit", ...)` and `mcp0_pull_request_create(...)` using the GitKraken MCP already registered in `mcp_config.json`. Note: the tool names in the comments (`mcp10_push_files`) are stale — the correct MCP prefix is `mcp0_`.

---

## GAP-10 — UWG Policy Hash Has No Epoch Tracking (Stale Hash Not Detected)

| Field | Value |
|---|---|
| **Severity** | MEDIUM |
| **File** | `agentic_core/L4_state/enforcement/uwg_verifier.py:93-97` |
| **Spec ref** | UWG_ISOLATION_SPEC §Stale Policy Hash Rejection: "Hash must match current epoch. Stale hashes rejected." |
| **Status** | ❌ `_policy_registry` is a static dict with no epoch/timestamp |

**Doc says:** Policy hash must be compared against a rolling "current epoch hash" that rotates when policy is updated. Stale hashes are rejected and logged.

**Code does:** Compares against a static dict of named hashes. No epoch rotation, no staleness window, no rejection logging.

**Closure action:** Add `_current_epoch_hash: str` and `_epoch_updated_at: float` to `UWGVerifier`. Expose `rotate_policy_epoch(new_hash)`. In `_verify_policy`, reject if `policy_hash != self._current_epoch_hash` and log the mismatch with timestamp.

---

## GAP-11 — Monotonic Trace ID Chaining Not Enforced (Replay Attack Vector)

| Field | Value |
|---|---|
| **Severity** | MEDIUM |
| **File** | No implementation exists |
| **Spec ref** | UWG_ISOLATION_SPEC §Monotonic Trace ID Chaining; §Replay Mode Bypass Prevention |
| **Status** | ❌ Not implemented — `WriteRequest.replay_key` is present but never validated for monotonicity |

**Doc says:** Trace IDs must be UUIDv7 (RFC 9562, time-ordered). Each new ID must be strictly greater than the last. Duplicate IDs indicate replay attack — must be rejected and logged.

**Code does:** `replay_key` field exists on `WriteRequest` and is set by `PromotionWriteGateway`, but `UWGClerk` never validates it for ordering or collision.

**Closure action:** Implement `TraceIDChainValidator` per spec (already fully specified in `UWG_ISOLATION_SPEC.md:240-362`). Wire into `UWGClerk._process_request` before stage U2.

---

## GAP-12 — UWG Daemon Independence Not Implemented (In-Process Only)

| Field | Value |
|---|---|
| **Severity** | LOW (design phase) |
| **Spec ref** | UWG_ISOLATION_SPEC §Independent Daemon Requirements: "Runs as independent process. Listens on Unix socket. Maintains own PID file." |
| **Status** | ⚠️ Architecture gap — UWG runs as a Python class in the main process, not as an independent daemon |

**Doc says:** UWG must run as an independent host-level daemon on port 9000 / Unix socket, with independent versioning from L2 and a PID file.

**Code does:** `UWGClerk` is a Python singleton in-process. L2 code can call it directly without IPC boundary enforcement.

**Closure action:** Out of scope for current sprint. Document as ADR: current implementation is "embedded mode" UWG with in-process enforcement. True daemon isolation requires `tools/uwg_daemon.py` + Unix socket IPC layer.

---

## Priority Matrix

| Gap | Severity | Closure effort | Blocks production? |
|---|---|---|---|
| GAP-01 UWGClerk stub | CRITICAL | Medium — wire 5 existing stages | Yes — all write enforcement bypassed |
| GAP-04 Verifier open-by-default | HIGH | Low — add fail-closed default | Yes — no actor/policy/signature enforcement |
| GAP-02 Blast radius stub | HIGH | Medium — ADG fanin/fanout query | Partial — risk gating absent |
| GAP-03 Structure check stub | HIGH | Low-Medium — layer gravity check | Partial — layer boundary not enforced |
| GAP-08 heal() universal skip | HIGH | High — per-agent impl needed | Yes — C3 healing loop dead |
| GAP-07 Warm storage missing | MEDIUM | Medium — Qdrant HTTP call | Partial — silent empty results |
| GAP-05 Locker unwired | MEDIUM | Trivial — resolved by GAP-01 | Resolved by GAP-01 |
| GAP-06 Refresher unwired | MEDIUM | Trivial — resolved by GAP-01 | Resolved by GAP-01 |
| GAP-10 Policy epoch missing | MEDIUM | Low | No — open-by-default is the bigger risk |
| GAP-11 Trace chain missing | MEDIUM | Medium — spec is complete in docs | No — replay attack vector only |
| GAP-09 GitHub MCP missing | MEDIUM | Low — MCP tools available | No — healing degrades gracefully |
| GAP-12 UWG daemon | LOW | High — full IPC layer | No — in-process is acceptable now |

---

## Execution Order (Recommended)

**Sprint 1 — Close the write pipeline (GAP-01, GAP-04):**
Wire `UWGClerk._process_request` to call all 5 stages in sequence. Simultaneously make `UWGVerifier` fail-closed when registries are empty.

**Sprint 2 — Real enforcement in the pipeline (GAP-02, GAP-03, GAP-10, GAP-11):**
ADG-backed blast radius, layer gravity structure check, epoch policy hash, trace ID chain validator.

**Sprint 3 — Healing loop activation (GAP-08, GAP-09):**
Implement deterministic `heal()` for the 3 highest-frequency L5 agents. Wire GitHub MCP commit/PR.

**Sprint 4 — Data path completeness (GAP-07):**
Qdrant warm-storage fallback with hot-cache promotion.

**Sprint 5 — Architecture hardening (GAP-12):**
UWG daemon isolation — separate process, Unix socket IPC. ADR required first.
