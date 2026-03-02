# Agentic Workflow — Production-Grade Sovereign AI Architecture

> A layered, self-healing agentic system engineered for correctness, auditability, and production safety.  
> Built to prove that AI agents can be deterministic, observable, and architecturally governed — not just functional.

---

## Why This Exists

Most AI agent frameworks hand you primitives and leave correctness as an exercise. This system starts from the opposite premise: **every mutation is gated, every validation is deterministic, every failure is auditable**.

This repository demonstrates a complete, production-ready agentic architecture — designed by an engineer who has built and operated AI systems end-to-end, from LLM inference routing to sovereign write gateways to self-healing orchestration loops.

---

## What It Does

Two real-world AI-powered applications run on top of this framework:

| App | Domain | What It Automates |
|-----|--------|-------------------|
| **`apps_lic`** | LinkedIn Content | Multi-agent pipeline for drafting, scoring, and publishing professional content |
| **`apps_rg`** | Resume Generation | Structured resume assembly with schema-validated output and quality scoring |

Both apps are driven by the same underlying `agentic_core` — a shared, layer-enforced execution substrate.

---

## Architecture: L0–L6 Layered Execution

The system is organized into seven enforced layers. No layer may import from a higher layer. Violations are caught at test time by AST-based cycle detection.

```
┌────────────────────────────────────────────────────────────────────┐
│  L0  Routing       — Sovereign entry point, allowlist-gated        │
│  L1  Cognition     — Deterministic orchestration & LLM arbitration │
│  L2  Execution     — Universal Write Gateway (all mutations here)  │
│  L3  Orchestration — Healing loops, arbitration, change packages   │
│  L4  State         — Indexed knowledge artifacts, embedding store  │
│  L5  Safety        — 100+ enforcement guards, human review queue   │
│  L6  Observability — Immutable audit ledger, mutation records      │
└────────────────────────────────────────────────────────────────────┘
```

Execution flows **down**. Validation signals flow **up**. No layer bypasses contract enforcement.

---

## Key Engineering Decisions

### Universal Write Gateway (L2)
Every filesystem, database, and vector write in the system passes through a single authority — `UniversalWriteGateway`. It enforces path allowlists, blocks executable extensions, records every mutation as an immutable `MutationRecord`, and supports **replay mode** for deterministic simulation with zero side-effects.

```python
# All writes gated — no back-channel mutations anywhere in the system
gateway.write_file("artifacts/output.json", data)   # permitted
gateway.write_file("src/agent.py", data)             # raises ToolNotAllowedError
```

### Validator ↔ Healer Symmetry
Validators and healers share a single SSOT (`structure_blueprint`). Both read the identical canonical export surface at runtime — no drift possible. Healing is versioned: each fix creates a `ChangePackage` with a parent pointer, forming a DAG that prevents temporal skew between detect and repair cycles.

```
V0 (baseline) → V1 (validator detects 47 violations) → V2 (healer applies fixes) → V3 (validator: 0 violations)
```

### Self-Healing with Confidence Routing
The orchestration layer routes healing decisions through a three-tier confidence model:
- **High confidence** → autonomous healing, no human required
- **Medium confidence** → Qwen 2.5 14B AWQ (local vLLM) arbitrates
- **Low confidence** → Human Review Queue, gated approval before any mutation

### AST-Based Enforcement Throughout
Zero regex for structural analysis. Every architectural invariant — layer boundary checks, import cycle detection, shim structure validation, SSOT compliance — uses AST parsing. Heuristics are explicitly forbidden by constitutional rules baked into the CI pipeline.

### Deterministic Test Suite
2,300+ tests across unit, integration, governance, and sovereign hardening suites. Markers include `constitutional`, `ssot`, `sovereignty`, `negative_control`, `determinism`, and `guardian`. The test suite is self-auditing: it verifies its own collection count vs execution count to detect silent deselection.

---

## What's Inside

```
agentic_core/
  L0_routing/          # 276 files — entry routing, legacy allowlist
  L1_cognition/        # LLM orchestration, shadow routers
  L2_execution/        # UniversalWriteGateway, instruction packets, CID registry
  L3_orchestration/    # Healing arbitration, change packages
  L4_state/            # Embedding store, knowledge artifacts
  L5_safety/           # 100+ guards: circuit breakers, PII vault, SSOT scanner,
                       #   canary token defense, sovereign fence, mutation prohibition
  L6_observability/    # Immutable audit ledger, telemetry
  base_agents/         # Canonical base classes — one file per agent archetype
  prompt_governance/   # Deterministic prompt assembly, orphan detection

system_learning/       # Meta-learning, healing pattern advisor, delta enforcer
tests/                 # 2,300+ tests: unit, integration, governance, architecture
.github/workflows/     # 17 CI gates: SSOT guardrail, agent sprawl check,
                       #   guardian tests, dashboard freshness, prompt governance
```

---

## Production Safety Properties

| Property | Mechanism |
|----------|-----------|
| **No silent failures** | Every rejected write raises `ToolNotAllowedError` with reason |
| **No heuristic routing** | All decisions use bounded contracts or AST enforcement |
| **No orphan prompts** | CI gate rejects any prompt file not referenced by an engine |
| **No layer inversions** | AST cycle detector runs on every PR |
| **No non-determinism** | SHA-256 hash verification on all embedding artifacts before healer reads |
| **No unchecked mutations** | `MutationRecord` written for every permitted and blocked operation |
| **No stale healing** | Versioned `ChangePackage` DAG prevents validator/healer temporal drift |

---

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **LLM Inference** | Google Gemini, Qwen 2.5 14B AWQ via local vLLM |
| **Embeddings** | Pinecone, BMG GPU embeddings, ChromaDB |
| **Data / State** | Redis, DuckDB, Pandas |
| **AST / Code Analysis** | libcst (deterministic CST), Python `ast` stdlib |
| **Observability** | Custom immutable ledger, structured logging, Plotly Dash |
| **CI** | GitHub Actions (17 workflow gates), pre-commit hooks |
| **Testing** | pytest with 25 registered marker types, pytest-asyncio, Playwright |

---

## For Technical Recruiters & Hiring Managers

This repository demonstrates engineering at the intersection of **AI systems design**, **software architecture**, and **production reliability**:

- **Systems thinking**: Every component is designed around explicit contracts, not convenience. The architecture forces correctness rather than hoping for it.
- **Production discipline**: Self-healing loops, human-in-the-loop gating, immutable audit trails, and replay-mode simulation — the same concerns that matter in real production AI systems.
- **Depth of craft**: 2,300+ tests, 17 CI gates, AST-enforced architectural invariants, and a coherent seven-layer execution model — built to a standard that holds up under scrutiny.
- **AI-native engineering**: Not a wrapper around an API. A complete substrate for running multi-agent workflows safely: routing, arbitration, healing, observability, and governance in one coherent system.

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/<your-handle>/Agentic-Workflow
cd Agentic-Workflow
pip install -e ".[dev]"

# Run the full test suite
python -m pytest -q --color=no

# Explore the architecture
cat docs/technical/Healer-Validator\ Resolution\ Symmetry\ in\ Architecture.md
```



