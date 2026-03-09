# Agentic Workflow — Cryptographically Governed Sovereign AI Architecture

> A cryptographically governed, self-healing agentic substrate where every LLM call,
> filesystem write, and embedding operation routes through a dedicated sovereign gateway —
> auditable, replayable, and deterministic by construction.

---

## Why This Exists

Most AI agent frameworks hand you primitives and leave correctness as an exercise. This system starts from the opposite premise: **every mutation is gated, every decision is cryptographically bound, every failure is auditable**.

Not a wrapper around an API. A complete substrate for running multi-agent workflows with the same reliability guarantees you'd demand from financial or safety-critical software — routing, arbitration, healing, observability, and governance in one coherent system.

---

## System at a Glance

| Metric | Value |
|--------|-------|
| **Architectural layers** | 7 (L0–L6), enforced by ADG on every commit |
| **Sovereign gateways** | 3 independent authorities (write, LLM, embedding) |
| **CI enforcement workflows** | 17 GitHub Actions gates |
| **Test suite** | 2,300+ tests, 31 registered marker types, self-auditing collection guard |
| **Determinism digests** | P5 · W6 · LOCKDOWN · W5 — SHA-256 bound to exact inputs |
| **Healing tiers** | 3 (LOCAL\_AGENT · QWEN\_VLLM · GEMINI\_2\_5\_PRO), mathematically routed |
| **Meta-learning pipeline** | 9 immutable stages (AUDIT → TELEMETRY → … → COMMIT) |

---

## What It Does

Two production AI applications run on this framework:

| App | What It Actually Solves |
|-----|------------------------|
| **`apps_lic`** | LinkedIn outreach via a 9-hop pipeline (Profile → Research → Persona → Routing → Generation → Validation → Gate Decision → QA → Integration). `GovernanceShieldAgent` detects and replaces naive AI claims ("zero hallucinations", "100% accurate") with risk-mature language. `OutreachSignalRouterAgent` selects surgical or full-diagnostic healing strategies and executes automatic rollback on critical signal detection. |
| **`apps_rg`** | Resume generation with persona routing, competitive intelligence (target company recon), evidence injection into bullet points, and a convergence-loop orchestrator (`RgHealingOrchestrator`) that caches successful healing patterns via meta-learning for future cycles. |

Both run on the same `agentic_core` substrate. Domain logic is encapsulated in Strategy classes; infrastructure sovereignty is non-negotiable and cannot be bypassed by application code.

---

## Architecture: L0–L6 Layered Execution

Seven enforced layers. No layer may import from a higher layer. Import direction is enforced by an AST-based **Architecture Dependency Graph (ADG)** that runs on every push, verifies all edges against a compile-time `ALLOWED_LAYER_EDGES` schema, and uploads a commit-scoped edge-list artifact. Any violation fails the build.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  L0  Routing        — ReasoningPolicyEngine stamps a SignedExecutionEnvelope  │
│                       with a cryptographic determinism digest. Pure function: │
│                       same inputs → byte-for-byte identical output.           │
│  L1  Cognition      — Coordinator pattern: Perception → Reasoning → Action   │
│                       with parallel/async execution, lazy eval, output cache. │
│  L2  Execution      — Three Sovereign Gateways (write · LLM · embedding),    │
│                       HealingTierRouter (single choke point), CIDRegistry.    │
│  L3  Orchestration  — DeterministicOrchestrator (W5-DETERMINISM-DIGEST),     │
│                       PTC immutable tool contracts, HandshakeStateMachine.    │
│  L4  State          — Read-only retrieval with GhostMutationDetector;        │
│                       FAISS IndexFlatIP with manifest integrity verification. │
│  L5  Safety         — Classification kernel (20 FileTypes, AST, LRU-cached), │
│                       structure blueprint, SSOT folder check, canary defense. │
│  L6  Observability  — DeterminismDigestEmitter (emit-once guarantee),        │
│                       EntropyTelemetryEngine, drift registry, audit ledger.   │
└──────────────────────────────────────────────────────────────────────────────┘
```

Execution flows **down**. Validation signals flow **up**. No layer bypasses contract enforcement.

---

## Key Engineering Decisions

### Three Sovereign Gateways (L2) — Not One Monolith

All external side-effects are channelled through three distinct, independently audited authorities — separated by side-effect class because each has different replay, policy, and audit requirements:

- **`UniversalWriteGateway`** — Every filesystem, database, and vector write passes through here. Enforces path allowlists, blocks executable extensions (`.py`, `.exe`, `.so`, …), records every operation as an immutable `MutationRecord`, supports **replay mode** for zero-side-effect simulation. Any non-gateway write raises `ToolNotAllowedError` immediately.
- **`SovereignLLMGateway`** — Every LLM call routes through 13 enforced guarantees (G1–G13): per-agent model allowlists, prompt injection detection before dispatch, hash-chained immutable audit log, `ReplayEnvelope` wrapping for deterministic replayability, provider health monitoring with graceful degradation. No agent calls a provider SDK directly.
- **`EmbeddingSovereignAgent`** — All embedding operations are gated, fingerprinted (`SHA-256` manifest), and verified at boot. Mismatched manifest hash raises `ManifestIntegrityError` immediately — fail-closed, no best-effort fallback.

```python
# All writes gated — no back-channel mutations anywhere in the system
gateway.write_file("artifacts/output.json", data)   # permitted
gateway.write_file("src/agent.py", data)             # raises ToolNotAllowedError
```

### Cryptographic Determinism Spine

Every critical decision point emits a SHA-256 digest bound to its exact inputs. Identical inputs across any two runs produce byte-for-byte identical digests — testable, falsifiable, auditable:

- **`ReasoningPolicyEngine` (L0)** — stamps `profile_hash` + `envelope_hash` into `SignedExecutionEnvelope`. No time signals, no mutable runtime state, no stochastic weighting.
- **`DeterministicOrchestrator` (L3)** — computes `W5-DETERMINISM-DIGEST` over plan hash, agent registry hash, tool key hash, and full handshake sequence on every orchestration run.
- **`DeterminismDigestEmitter` (L6)** — thread-locked emit-once guarantee per instance. Any second call raises `DuplicateEmissionError`. Verified by the **Spine Determinism Guard** CI workflow on every push.
- **`execute_ssot` pipeline** — emits `EXECUTE_SSOT_PIPELINE_DIGEST` from pipeline order + adapter keys + territory. A negative-control test injects a tamper token and verifies the digest changes — proving the digest covers the actual execution surface.

### Mathematically Deterministic Confidence Routing

`HealingTierRouter` is the **single choke point** for all model selection. It computes a weighted confidence score from six fixed-precision components with no environment variable access, no external I/O, and compile-time frozen historical data:

| Component | Weight |
|-----------|--------|
| Failure class prior | 0.25 |
| Blast radius | 0.20 |
| Failure entropy class | 0.15 |
| Historical success rate | 0.15 |
| Tool readiness | 0.15 |
| Retry decay | 0.10 |

Three routing tiers — and the routing itself is a `SovereigntyViolation` hard-fail if the agent isn't in the compile-time frozen `TIERING_ALLOWLIST`:

- **≥ 0.75** → `LOCAL_AGENT` — autonomous healing, no human required
- **0.40 – 0.75** → `QWEN_VLLM` — Qwen 2.5 14B AWQ (on-device vLLM) arbitrates
- **< 0.40 or retry ≥ 3** → `GEMINI_2_5_PRO` — escalated to frontier model; Human Review Queue gated before any mutation

`EntropyTelemetryEngine` (L6) tracks tier variance, flip rate, and Path D (human-in-the-loop) intervention rate in rolling windows — the system monitors its own routing health continuously.

### Validator ↔ Healer Symmetry

Validators and healers share a single SSOT (`structure_blueprint`). Both read the identical canonical export surface at runtime — drift is structurally impossible. Healing is versioned: each fix creates a `ChangePackage` with a parent pointer, forming a DAG that prevents temporal skew between detect and repair cycles.

```
V0 (baseline) → V1 (violations detected) → V2 (healer applies fixes) → V3 (zero violations)
```

### Self-Healing with Meta-Learning Feedback

The `system_learning` substrate closes the loop: `PatternAnalysisEngine` clusters historical healing outcomes (deterministic FAISS + cosine distance, L2-normalised), feeds findings to `HealingConfigOptimizer`, and `L0ThresholdTuner` / `L3EfficiencyTuner` / `L5PolicyProposer` propose refined configuration as versioned `ChangePackage`s. The default is `proposal_only=True` — no auto-commit without explicit dual injection of `version_store` + `approval_gate`.

### Architecture Dependency Graph (ADG)

Commit-scoped static analysis that builds the full import graph, verifies it against `ALLOWED_LAYER_EDGES`, detects sovereign gateway violations, and emits a SHA-256 digest. CLI: `python -m agentic_core.adg.cli --repo-root . --commit <sha> scan`. Edge lists are uploaded as GitHub Actions artifacts on every push.

### Programmatic Tool Contracts (PTC)

All tool calls in L3 are typed as immutable frozen dataclasses (`ToolSpec` / `ToolCall` / `ToolCallResult`) with deterministic SHA-256 `call_id` generation, canonical JSON serialisation, and a `side_effect_class` taxonomy (`PURE` / `READONLY` / `WRITE_FS` / `SUBPROCESS`). No untyped tool dispatch anywhere in the system.

### Prompt Governance

Every prompt assembled via five-slot XML semantic fence (S0→D0→I0→C0→U0). Slot ordering enforced by contract at assembly time. `SovereignPromptRenderer` uses Jinja2 `StrictUndefined` — any undefined variable is a hard failure, not a silent empty string. A CI gate (`prompt-governance.yml`) rejects any prompt file unreferenced by an active engine.

### AST-Based Enforcement Throughout

Zero regex for structural analysis. Every invariant — layer boundary checks, import cycle detection, spine bypass detection, MRO diamond contracts, agent sprawl, shim structure, SSOT compliance — uses Python `ast` parsing. Heuristics are constitutionally forbidden and enforced in CI.

---

## Failure Modes — How the System Fails Safely

Production-grade systems are defined as much by how they fail as how they succeed:

| Failure | Response |
|---------|----------|
| Non-gateway filesystem write | `ToolNotAllowedError` raised immediately — no partial writes |
| FAISS manifest hash mismatch | `ManifestIntegrityError` — fail-closed at boot, no fallback |
| Qwen vLLM unavailable | `qwen_circuit_breaker` trips; escalates to `GEMINI_2_5_PRO` tier automatically |
| Unregistered agent invocation | `KeyError` hard-fail with available agents listed — no silent routing |
| Ghost mutation detected | `GhostMutationViolation` raised with full before/after diff |
| Layer import inversion | ADG build failure — merge blocked |
| Determinism digest mismatch | `DuplicateEmissionError` or digest delta — CI fails, run is not replayable |
| Prompt injection detected | Blocked at `SovereignLLMGateway` before provider dispatch |
| Non-allowlisted agent in healing | `SovereigntyViolation` — hard-fail, no tier selection attempted |

---

## What's Inside

```
agentic_core/
  L0_routing/          # ReasoningPolicyEngine, ShadowRouterClassifier,
                       #   AirlockAssembler (S0→D0→I0→C0→U0), ExecutionOrchestrator
  L1_cognition/        # CognitiveNode (Perception → Reasoning → Action),
                       #   lazy eval for simple intents, hash-based output cache
  L2_execution/        # Three Sovereign Gateways, HealingTierRouter (choke point),
                       #   determinism.py (P5/W6/LOCKDOWN digests), L2AgentProtocol,
                       #   CIDRegistry (immutable ExecutionCycle), ReEntryLoop (bounded)
  L3_orchestration/    # DeterministicOrchestrator (W5 digest + HandshakeStateMachine),
                       #   OrchestratorFacade (strategy pattern), PTC tool contracts
  L4_state/            # GhostMutationDetector, ReadonlyRetrievalOrchestrator,
                       #   LocalFAISSStore (IndexFlatIP + pure-Python fallback)
  L5_safety/           # ClassificationKernel (20 FileTypes, 19-priority AST queue,
                       #   LRU-cached), StructureBlueprint (sovereign territories),
                       #   circuit breakers, canary token defense, SSOT folder check
  L6_observability/    # DeterminismDigestEmitter (emit-once, thread-locked),
                       #   EntropyTelemetryEngine (tier variance, flip rate, Path D rate),
                       #   drift registry, provider binding fingerprint
  base_agents/         # SovereignBaseAgent — CoreIntegrityVerifier on every boot,
                       #   V15ExecutionGateway, 10 capability mixins
  prompt_governance/   # PromptAssembler (XML fencing, airlock, healer re-entry gate),
                       #   SovereignPromptRenderer (Jinja2 StrictUndefined)
  adg/                 # Architecture Dependency Graph — schema, CLI, commit-scoped scan

system_learning/       # LocalFAISSStore, PatternAnalysisEngine (deterministic clustering),
                       #   HealingConfigOptimizer, RLHF optimizer, ShadowDriftAnalyzer,
                       #   MetaLearningReplayBinding, L0ThresholdTuner, L3EfficiencyTuner,
                       #   L5PolicyProposer, 9-stage immutable meta-learning pipeline

apps_lic/              # 9-hop outreach pipeline, GovernanceShieldAgent (naive-claim
                       #   detection + senior replacement), OutreachSignalRouterAgent
                       #   (strategy selection + automatic rollback on critical signals)

apps_rg/               # Persona routing, competitive recon, evidence injection,
                       #   RgHealingOrchestrator (meta-learning cycle cache + convergence)

tests/                 # Unit, integration, governance, architecture, guardian, sovereign
                       #   hardening, e2e, evaluation, stress, ssot_equivalence suites.
                       #   Self-auditing: conftest verifies collection count = execution
                       #   count on every run — silent test deselection is impossible.

.github/workflows/     # 17 CI enforcement gates (see table below)
```

---

## CI Gates — 17 Enforced Workflows

| Workflow | What It Enforces |
|----------|-----------------|
| `adg-invariant-scan` | Full ADG import-graph scan; uploads commit-scoped edge-list artifact |
| `layer-sovereignty-enforcement` | AST cross-layer import matrix; L4/L1/L3 forbidden-import checks |
| `agent-sprawl-check` | Agent count cap, MRO diamond contracts, dedup similarity ≤ 0.85, active-set drift |
| `spine-determinism-guard` | AST spine-bypass detection, adapter contract, evidence contract v2 |
| `mcp-sovereignty` | No hardcoded credentials, `MCPHardenedMixin` presence, SSL/TLS + Neo4j encryption |
| `ssot-enforcement` | Sovereign folder structure, hierarchy depth rules, no orphaned files |
| `prompt-governance` | No unreferenced prompt files; assembly validation |
| `guardian-tests` | All `@pytest.mark.guardian` tests |
| `scope-separation-enforcement` | Cross-app import separation |
| `sovereignty-hardening` | Full hardening suite |
| `ssot-kernel-guardrail` | Core kernel SSOT contracts |
| `structure-invariants` | File/folder structural invariants |
| `import-resolution-guardian` | Import resolution correctness |
| `dashboard-freshness` | Observability dashboard currency |
| `qwen-sovereignty-audits` | Local model sovereignty |
| `redis-integration` | Redis MCP integration |
| `ssot_verify` | Full SSOT verification run |

---

## Production Safety Properties

| Property | Mechanism |
|----------|-----------|
| **No silent failures** | Every rejected write raises `ToolNotAllowedError`; every LLM rejection emits an audit entry |
| **No heuristic routing** | All routing uses bounded contracts, deterministic fixed-precision scoring, or AST enforcement |
| **No orphan prompts** | CI gate rejects any prompt file not referenced by an active engine |
| **No layer inversions** | ADG + AST cycle detector on every PR; `ALLOWED_LAYER_EDGES` is the sole authority |
| **No non-determinism** | SHA-256 manifest verification on all embedding artifacts; `DeterminismDigestEmitter` emit-once guarantee |
| **No unchecked mutations** | `MutationRecord` written for every permitted and blocked operation |
| **No stale healing** | Versioned `ChangePackage` DAG prevents validator/healer temporal drift |
| **No ghost mutations** | `GhostMutationDetector` diffs before/after state against execution transcript |
| **No credential leakage** | `mcp-sovereignty` CI gate scans for hardcoded API keys and passwords on every push |
| **No unbounded retries** | `ReEntryLoop` bounded; `CIDRegistry` tracks immutable `ExecutionCycle` records — no infinite loops |

---

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **LLM Inference** | Google Gemini 2.5 Pro, Qwen 2.5 14B AWQ via local vLLM |
| **Embeddings** | FAISS (IndexFlatIP + L2 normalisation), multilingual-e5-large, Pinecone |
| **Data / State** | Redis (hot-path cache), DuckDB, SQLite (dep graph), Pandas |
| **AST / Code Analysis** | Python `ast` stdlib (all structural enforcement), libcst |
| **Observability** | Custom immutable ledger, `EntropyTelemetryEngine`, structured logging, Plotly Dash |
| **Prompt Engineering** | XML semantic fencing (S0–U0 slots), Jinja2 `StrictUndefined`, injection detection |
| **CI** | GitHub Actions (17 workflow gates), pre-commit hooks |
| **Testing** | pytest (31 registered marker types), pytest-asyncio, Playwright |

---

## Design Philosophy

Sovereignty over convenience. Cryptographic accountability over trust. Enforcement at the boundary, not the convention.

Every component is designed around an explicit contract. The architecture forces correctness rather than assuming it. The 17 CI workflows aren't a testing strategy — they're a machine that makes architectural drift physically impossible to merge.

The interesting engineering problems here are not "which LLM to call" but "how do you make an autonomous system that fails loudly, heals deterministically, and produces the same output given the same inputs — provably, across any run, on any machine."

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/<your-handle>/Agentic-Workflow
cd Agentic-Workflow
pip install -e ".[dev]"

# Run the full test suite
python -m pytest -q --color=no

# Run the ADG invariant scan
python -m agentic_core.adg.cli --repo-root . scan

# Read the full zero-loss architecture map
cat docs/technical/agentic_process_mapping_detailed.md
```
