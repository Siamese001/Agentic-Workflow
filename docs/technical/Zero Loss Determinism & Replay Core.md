# Zero Loss Determinism & Replay Core

## Overview

Zero-loss determinism means that any execution sequence in the system is fully reproducible from its inputs alone — no wall-clock timestamps in replay keys, no environment variable access during scoring, no random seeds, no external data lookups during confidence calculations. The replay core captures the full execution surface (provider, model, embedder, config hash, semantic clock) in a sealed envelope so that any future replay produces byte-for-byte identical routing decisions.

---

## Architecture

```
Execution Request
     │
     ▼
ProviderBindingContext     ← pins provider_id, model_id, gateway_version, semantic_clock_vector
     │
     ▼
ReplayEnvelope             ← seals full RAG + embedding + policy surface
     │
     ▼
ExecutionGateway           ← execute_with_trace → ExecutionTrace
     │
     ▼
HashChainAuditLog          ← append(tier, action, payload) → chained AuditEntry
     │
     ▼
DeterminismDigestEmitter   ← emit_once() → single sealed digest per execution
     │
     ▼
ReplayGuard (context mgr)  ← patches socket, subprocess, filesystem, threading, random
     │
     ▼
DeterministicReplayEngine  ← replay(cases) → ReplayResult with changed_cases count
     │
     ▼
ReplayValidator            ← validate_seed_pack + validate_embedding_artifact
```

---

## Replay Envelope — Full Surface Seal

**File:** `agentic_core/L2_execution/types/replay_envelope_types.py`

`ReplayEnvelope` (frozen dataclass) captures the complete configuration surface that must be identical for a replay to be valid.

| Field | Type | Description |
|---|---|---|
| `routing_hash` | `str` | Hash of the routing decision inputs |
| `manifest_hash` | `str` | Hash of the agent manifest at execution time |
| `model_id` | `str` | LLM model identifier |
| `model_version` | `str` | LLM model version string |
| `temperature` | `float` | Sampling temperature (must be 0.0 for determinism) |
| `allowed_model_policy_version` | `str` | Policy version governing allowed models |
| `policy_version` | `str` | Full policy config version |
| `gateway_version` | `str` | `SovereignLLMGateway` version |
| `embedder_provider` | `str` | Embedding provider identifier |
| `embedder_model` | `str` | Embedding model identifier |
| `embedder_dim` | `int` | Embedding dimension |
| `normalization_policy` | `str` | L2 / none |
| `chunking_policy` | `str` | Chunking strategy identifier |
| `distance_metric` | `str` | cosine / l2 |
| `retrieval_top_k` | `int` | Top-K retrieval parameter |
| `retrieval_similarity_cutoff` | `float` | Minimum similarity threshold |
| `agent_registry_hash` | `str` | Hash of `agent_discovery_full.json` at execution time |
| `deterministic_engine_version` | `str` | Version of the determinism engine |
| `code_commit_hash` | `str | None` | Git commit SHA at execution time |

---

## Replay Key Components

**File:** `agentic_core/L6_observability/engines/replay_key_computer.py`

`ReplayKeyComponents` (dataclass) enumerates every input dimension that contributes to a replay key:

| Field | Type | Description |
|---|---|---|
| `tier_selection` | `str` | Healing tier selected (LOCAL_AGENT / QWEN_VLLM / GEMINI_2_5_PRO) |
| `retry_count` | `int` | Retry count at decision time |
| `threshold_config` | `dict[str, float]` | X/Y thresholds in effect |
| `tool_budget_caps` | `dict[str, int]` | Tool budget per tool name |
| `freshness_windows` | `dict[str, int]` | Retrieval freshness windows |
| `config_surface_hash` | `str` | Hash of full config surface |
| `embedding_pack_hash` | `str` | Hash of FAISS index packs |
| `embedding_model_version` | `str` | Embedding model version |
| `c0_context_hash` | `str` | Hash of C0 context (initial system context) |

Any change to any field produces a different replay key, making configuration drift detectable at replay time.

---

## Healing Tier Router — Deterministic Scoring

**File:** `agentic_core/L2_execution/healers/healing_tier_router.py`

The router is the primary determinism boundary for healing decisions. See [Healing & Escalation Loop](Healing%20%26%20Escalation%20Loop.md) for full details.

Determinism guarantees:
- All weights are local variables — no config loading
- `FAILURE_CLASS_PRIORS` and `HISTORICAL_SUCCESS_RATES` are compile-time frozen dicts
- `tool_readiness` is a fixed constant (0.8)
- Timestamp is **excluded** from the replay key
- `HISTORICAL_DATA_VERSION = "v1.0.0"` versioned into every replay key
- Score rounded to 6 decimal places via `round(max(0.0, min(1.0, raw)), 6)`

`_compute_replay_key(healing_input, decision)` — SHA-256 over 9 components, returns first 16 hex chars.

---

## ReplayGuard — Side-Effect Patcher

**File:** `agentic_core/L2_execution/determinism/replay_guard.py`

`ReplayGuard` is a context manager that patches all non-deterministic stdlib surfaces for the duration of a replay execution.

| Method | Description |
|---|---|
| `__enter__` | Saves original state, applies all patches |
| `__exit__` | Restores all original state via `_restore_all` |
| `_patch_socket()` | Blocks outbound socket connections |
| `_patch_subprocess()` | Intercepts subprocess calls |
| `_patch_filesystem_writes()` | Blocks filesystem writes outside declared write set |
| `_patch_threading()` | Serializes threading for deterministic ordering |
| `_patch_random()` | Seeds `random` module with fixed seed |
| `_save()` / `_restore(name)` | Per-surface save/restore |
| `_restore_all()` | Full restoration of all patched surfaces |

`ReplayViolation(RuntimeError)` — raised when a patched surface is accessed in a way that would introduce non-determinism.

---

## Deterministic Providers

**File:** `agentic_core/L2_execution/deterministic_providers.py`

Three deterministic provider classes replace stdlib non-determinism sources during replay:

### `FixedTimeProvider`

| Method | Description |
|---|---|
| `time()` | Returns current fixed timestamp |
| `sleep(seconds)` | Advances internal clock without blocking |
| `advance(delta)` | Manually advances the clock by `delta` seconds |
| `current_offset` | Elapsed time since construction |

### `DeterministicRandomSource`

| Method | Description |
|---|---|
| `random()` | Returns next value from seeded sequence |
| `randint(a, b)` | Seeded integer in range |
| `choice(seq)` | Seeded sequence choice |
| `shuffle(seq)` | In-place seeded shuffle |

### `DeterministicUUIDProvider`

| Method | Description |
|---|---|
| `uuid4()` | Returns next UUID from seeded counter |

`DeterministicPatchError(Exception)` — raised when an unpatchable stdlib call is attempted.

---

## DigestCalculator

**File:** `agentic_core/L2_execution/determinism/digest_calculator.py`

`DigestCalculator` — stateless digest helper.

- `compute(data)` — returns SHA-256 hex digest of `data` (bytes or str)
- `zero_hash()` — returns a fixed all-zeros hash for unset/null inputs

Used to canonicalize inputs before hashing in `ReplayEnvelope`, `ExecutionTrace`, and `HashChainAuditLog`.

---

## DependencyLocker

**File:** `agentic_core/L2_execution/determinism/dependency_locker.py`

`DependencyLocker` pins the Python dependency surface for reproducible execution environments.

| Method | Description |
|---|---|
| `generate_lock_hash()` | SHA-256 over `requirements.txt` + `pyproject.toml` |
| `save_lock_file(path)` | Writes lock hash to a file |
| `load_lock_hash(path)` | Reads a previously saved lock hash |
| `validate()` | Compares current environment hash against saved lock |

Replays that detect a dependency lock mismatch fail immediately with the mismatch detail in evidence.

---

## DeterminismDigestEmitter — Once-Per-Execution Digest

**File:** `agentic_core/L6_observability/engines/determinism_digest_emitter.py`

`DeterminismDigestEmitter` ensures exactly one determinism digest is emitted per logical execution.

| Method | Description |
|---|---|
| `compute(replay_envelope, execution_trace)` | Computes the determinism digest from sealed artifacts |
| `emit_once(digest)` | Emits the digest; raises `DuplicateEmissionError` if called twice |
| `reset_for_testing()` | Test isolation — resets emission state |

`DuplicateEmissionError(RuntimeError)` — raised on any second emission attempt. This is a hard invariant: duplicate emission indicates a non-deterministic execution path.

`_Encoder(json.JSONEncoder)` — custom encoder that handles `bytes`, `frozenset`, and `tuple` types in artifact payloads.

---

## Semantic Clock Validator

**File:** `agentic_core/L6_observability/engines/semantic_clock_validator.py`

`SemanticClockValidationResult` dataclass:

| Field | Type | Description |
|---|---|---|
| `valid` | `bool` | Whether the stored and computed hashes match |
| `stored_hash` | `str` | Hash stored in the `CapabilityTokenArtifact` |
| `computed_hash` | `str` | Hash re-computed from current vector |
| `advancement_id` | `str` | Identifier of the clock advancement event |

`SemanticClockHashMismatch(ValueError)` — raised when `stored_hash != computed_hash`. This means the semantic clock was advanced after the capability token was issued, invalidating the token.

---

## Deterministic Replay Engine

**File:** `system_learning/engines/deterministic_replay_engine.py`

`DeterministicReplayEngine` executes a set of replay cases against base and candidate configurations and computes a replay digest.

| Method | Description |
|---|---|
| `replay(cases, base_config, candidate_config)` | Full replay execution, returns `ReplayResult` |
| `_run_replay_cases(cases, config)` | Per-case execution under `ReplayGuard` |
| `_compute_replay_digest(base_outputs, candidate_outputs)` | SHA-256 over sorted output diffs |

`ReplayResult` dataclass:

| Field | Type | Description |
|---|---|---|
| `case_count` | `int` | Total replay cases executed |
| `base_outputs` | `dict[str, list[str]]` | Output lines per case for base config |
| `candidate_outputs` | `dict[str, list[str]]` | Output lines per case for candidate config |
| `changed_cases` | `int` | Count of cases where output differed |
| `replay_digest` | `str` | Deterministic digest over all outputs |

---

## Meta-Learning Replay Binding

**File:** `system_learning/engines/meta_learning_replay_binding.py`

`MetaLearningReplayBinding` (dataclass) — seals the meta-learning surface inputs into the replay key:

| Field | Type | Description |
|---|---|---|
| `faiss_index_digests` | `dict[str, str]` | Per-index SHA-256 digests |
| `strategy_weights_digest` | `str` | Digest of current strategy weights |
| `embedding_model_version` | `str` | Embedding model version string |

Changes to any FAISS index, strategy weights, or embedding model version produce a new replay key, making meta-learning drift visible in replay comparisons.

---

## Replay Validator

**File:** `system_learning/engines/replay_validator.py`

`ReplayValidator` — validates that seed packs and embedding artifacts are internally consistent before replay execution.

| Method | Description |
|---|---|
| `validate_seed_pack(pack)` | Validates seed pack schema, hash integrity, and version |
| `validate_embedding_artifact(artifact)` | Validates embedding artifact dimensions and model version |

`DeterminismViolationError(Exception)` — raised when validation detects an inconsistency that would make replay non-deterministic.

---

## Deterministic Replay Record

**File:** `agentic_core/L3_orchestration/replay/deterministic_replay.py`

`ReplayRecord` (dataclass) — the serializable execution record used for offline replay:

| Field | Type | Description |
|---|---|---|
| `version` | `int` | Record schema version |
| `created_utc` | `str` | ISO 8601 creation timestamp |
| `commands` | `list[ReplayCommand]` | Ordered command list |
| `results` | `list[ReplayResult]` | Per-command results |
| `hashes` | `dict[str, str]` | Per-command output hashes |
| `metrics` | `ReplayMetrics | None` | Byte counts for stdout/stderr |

`ReplayCommand` dataclass:

| Field | Type | Description |
|---|---|---|
| `argv` | `list[str]` | Command argument vector (`shell=False`) |
| `cwd` | `str` | Working directory |
| `env_allowlist` | `dict[str, str]` | Allowed environment variables only |
| `timeout_s` | `int` | Command timeout |
| `max_stdout_bytes` | `int` | Stdout truncation limit |
| `max_stderr_bytes` | `int` | Stderr truncation limit |

`ReplayMetrics` dataclass: `per_command_bytes_out`, `per_command_bytes_err`, `total_bytes_out`, `total_bytes_err`.

`ComparisonResult` dataclass: `is_match: bool`, `mismatches: list[str]`, `first_diff_summary: str`.

---

## LLM Replay Strategy

**File:** `agentic_core/L2_execution/types/llm_replay_types.py`

`ReplayBundle` (dataclass) — captures raw LLM I/O for replay verification:

| Field | Type | Description |
|---|---|---|
| `model_version` | `str` | Model version string |
| `tokenizer_version` | `str` | Tokenizer version string |
| `raw_prompt_bytes` | `bytes` | Exact bytes sent to LLM |
| `raw_response_bytes` | `bytes` | Exact bytes received from LLM |
| `provider_checksum` | `str` | Provider-computed response checksum |
| `replay_hash` | `str` | SHA-256 over prompt + response |
| `integrity_verified` | `bool` | Whether provider checksum matches |

`LLMReplayStrategy` dataclass: `bundle: ReplayBundle`, `mode: ReplayMode`.

`ReplayMode(enum.Enum)` — values control replay behavior: `STRICT` (exact byte match), `SEMANTIC` (embedding distance match), `SKIP` (replay disabled).

---

## Execution Trace — Sealed Evidence

**File:** `agentic_core/L2_execution/types/execution_trace_types.py`

`ExecutionTrace` is the sealed, immutable record of a single execution. Every field is content-addressed.

Key determinism fields:
- `governed_payload_hash` — hash of governed LLM input
- `llm_response_hash` — hash of raw LLM output
- `hash_chain_root` — root of `HashChainAuditLog`
- `policy_hash` — hash of active policy config (must be stable across replays)
- `prev_hash` — links to previous `ExecutionTrace` (chain integrity)
- `replay_key` — deterministic replay identifier

`ExecutionTraceBuilder` fluent API: `set_governed_payload`, `add_sandbox_envelope`, `set_llm_response`, `set_transcript`, `set_policy_hash`, `set_prev_hash`, `set_validation_decision`, `set_hash_chain_root`, `set_timing`, `seal()`.
