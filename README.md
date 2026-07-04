# Agentic Workflow — A Deterministic AI Control Plane

> **A governed runtime around the agent — not another agent framework.**
> Route authority, verified context, bounded execution, runtime gates, single-door writes, exact replay, and shadow learning. Built as a reference design for enterprise-grade agentic systems.

**Author:** [Amit Ayer](https://github.com/Siamese001) — SVP-level Agentic Engineer · platform architecture for governed enterprise AI.

---

## The Thesis

Most public discourse about "agents" is about **frameworks, prompts, and demos**. That framing is the reason enterprise AI projects stall the moment they hit a regulated runtime boundary.

The argument this repo makes — and demonstrates in code — is the opposite:

> **The agent is not the product. The governed runtime around the agent is the product.**

Production AI in regulated environments tends to fail on five predictable edges:

1. **No route authority** — the model decides what to do next, instead of a typed, contract-bound dispatcher.
2. **No context guarantees** — retrieval quietly routes and executes, instead of grounding against canonical state.
3. **No exit evaluation** — outputs commit without a current-run disposition (allow / deny / reroute / escalate).
4. **No write controls** — state mutates through any code path that can reach a database.
5. **No replay** — incidents cannot be reconstructed, so nothing can be audited, regressed, or learned from safely.

Those failure modes are **system engineering problems**, not prompt-engineering problems. This repository is the engineering substrate behind the positioning: **AI that behaves like software, not experiments.**

---

## What this is *not*

- Not an agent framework. Not another CrewAI / LangGraph / AutoGen wrapper.
- Not a model fine-tune. Not a prompt library.
- Not a finished product. It is a **public reference design** for what governed enterprise agentic AI looks like when it has to clear an enterprise control boundary — written so that an SVP Engineering, a CISO, or a Head of Platform can reason about it without trusting screenshots.

The argument the repository makes — and the argument my career makes — is the same one: AI moves into production by becoming **system engineering**, not by becoming a bigger model.

---

## Why This Matters for SVP Engineering Hiring

This repository is meant to be reviewed as a public proof asset for senior engineering leadership. It demonstrates the judgment required to move AI from prototype to governed platform: clear authority boundaries, deterministic execution, audit-ready evidence, controlled write paths, operational proof commands, and a documented model for letting AI-assisted development move quickly without losing architectural control.

For a hiring manager or CTO, the signal is not just "can build AI software." The signal is **can design the operating system around AI teams and AI runtimes so they can scale safely.**

---

## Best-in-Class Design Patterns Implemented

This is the centerpiece. Each pattern below is a load-bearing structural decision in this codebase — named, isolated, and verifiable in source.

### 1. Layered Control Plane (L0–L7) — Separation of Authority

A 7-layer plane in which each layer has a clear accountability and cross-layer calls are expected to use typed contracts. The intended shape is a directed, auditable structure rather than an "everything talks to everything" mesh.

| Layer | Persona | Single accountability | Authority |
|-------|---------|------------------------|-----------|
| L0 | Dispatcher | Route selection (cache → RAG → action → fallback) | Routing only |
| L1 | Librarian | Bounded LLM reasoning → execution plan | Plan formulation |
| L2 | Execution | Sandboxed tool / action calls | Sandboxed exec |
| L3 | Orchestrator | Multi-step coordination of L2 chains | Optional, on demand |
| L4 | Archivist | Durable state — single-door writes via UWG | Read-broad / write-strict |
| L5 | Safety Officer | Cross-cutting policy plane | **Veto authority everywhere** |
| L6 | Observer | Shadow evaluation, telemetry, replay | Read-only — no runtime mutation |
| L7 | Auditability | Compiled certification + signed proof bundles | Read-only audit surface |

> Code: `agentic_core/L0_routing/` · `L1_cognition/` · `L2_execution/` · `L3_orchestration/` · `L4_state/` · `L5_safety/` · `L6_observability/` · `L7_auditability/`.

### 2. Universal Write Gateway (UWG) — Single-Door State Mutation

Durable writes are designed to pass through one validated, signed, recorded gateway, with bypass checks carried by ADG and CI gates. The goal is to make state integrity a **structural** property, not a code-review property.

```
ANY STATE CHANGE → UWG (validate · authorize · sign · record) → L4
```

### 3. Deterministic Replay — Trace + Digest + Replay Key

Replayable paths emit a **determinism digest** and a **replay key** so incidents and regressions can be reconstructed from recorded evidence. Wall-clock and randomness controls are treated as proof obligations rather than after-the-fact debugging notes.

### 4. Programmatic Tool Calling (PTC) — Schema-Enforced Action Surface

Tool usage is **schema-driven and contract-enforced**, not free-text JSON the model invents. Calls that do not conform to the contract are blocked before L2 by the programmatic action surface.

### 5. AST Dependency Graph (ADG) — Source-of-Truth for the Codebase Itself

A SQLite-backed dependency graph (~264K nodes / ~929K edges) with **graph-DB semantics over a relational store**: materialized views, semantic edges (`flows_to`, `reads_from`, `writes_to`, `emits_side_effect`, `controls_flow`, `resolves_callsite`), and pre-classified P-views (`v_p0_*` … `v_p3_*`). Refactor blast-radius, hotspot ranking, and layer-violation detection are queries — not guesses.

> Code: `tools/adg/` · `agentic_core/adg/` · canonical snapshot at `artifacts/adg/adg_indexed_<ts>.sqlite`.

### 6. Closed-Loop Routers + Intelligence Ledgers

Ten routers across L0–L6 (bandit / r5 / c0 / cascade / shape / reroute / uwg / hitl / promo / regret) each emit a `ROUTER_DECISION:` marker plus an append-only ledger event in the same code path. The ledgers feed back into Wilson-CI promotion gates and Thompson-sampling bandits. **Decisions become evidence become the next decision** — a closed loop, not an open hope.

> Code: `agentic_core/L0_routing/reasoning/namespace_bandit.py` · `agentic_core/L6_observability/promotion_gates.py` · `tools/ledgers/`.

### 7. Author-Gate Decision Pattern — Scored Options with Dominance Rule

Ambiguous decisions are surfaced as **scored options on [0.00–1.00]** with explicit confidence, gap-to-next, and a dominance rule (top >= 0.85 and gap >= 0.12 -> surface alone, recommended). The current Codex-primary flow preserves the pattern as a decision-ledger and choice-surface discipline; historical Notion mirroring is not the active governance source of truth.

### 8. Codex Rules + Hooks + CI Gates — Three-Tier Enforcement

Discipline is encoded at three layers:

- **Tier 1 — always-on rules** (`.codex/rules/*.md`) — prose invariants the agent reads during governed work.
- **Tier 2 — pre/post hooks** (`.codex/hooks.json`, `.codex/hooks/**`, `.codex/governance/scripts/**`) — deterministic checks around write, tool-use, and response time.
- **Tier 3 — pre-commit + CI gates** (`ops_scripts/ci/check_*.py`) — fail-closed at commit and pipeline.

High-signal invariants are assigned to one source of truth and then checked at the layer where enforcement is strongest, so drift is visible instead of buried in duplicated guidance.

### 9. Fort Knox Certification — Two-Arm Signed Runtime Proof

Runtime certification is **compiler-only** (no hand-written claims): `compile_requirement_signoff.py` consumes a JSONL of evidence assertions and emits a Merkle-rooted, signed bundle (SHA-256 + signature). A **canary requirement** (`RTC-REQ-001` for `agentic_core`, `APPS-REQ-001` for apps) plus a **mutation-rejection report** prove the verifier rejects regressions. Doctrine: SLSA L3 / in-toto / Sigstore / Critic-Agent.

> Code: `scripts/compile_requirement_signoff.py` · `scripts/compile_apps_e2e_signoff.py` · `tools/cert/`.

### 10. HOP Pipeline Pattern — Declarative Multi-Stage Orchestration

Multi-stage app workflows are expressed as **typed HOP topologies** (e.g. underwriting's 5-stage `initialize → reconcile → derive → collect → assemble`). A shared `HopPipelineExecutor` walks the topology with replay support; an imperative driver mirrors it 1:1 for direct use. The same shape ships in `apps_lic`, `apps_rg`, `apps_underwriting_ai`.

### 11. Final Evidence Contract (FEC) — Per-Claim Provenance

Grounded app outputs use a versioned `final_evidence_contract` (schema_version=1.0) with `producer`, `grounded`, `retrieval_sources`, `template_ids`, `route_id`, `evidence_sufficiency`. The evaluator and HITL-policy router consume it; the Exit pipeline records provenance before commit.

### 12. Spine Manifest + Boundary Adapters — Static Route Claim per App

Each app ships a `spine_manifest.yaml` declaring the canonical route it serves on the runtime spine. Boundary-leak tests assert the claim. Cross-app imports route through PEP-562 lazy facades in `apps_shared/integrations/adapters/` — `apps_eval` cannot reach into `apps_rg` even by accident.

### 13. Ledger Family — Append-Only Decision Substrate

Thirty-plus append-only ledgers and the Memory MCP knowledge graph give routers, gates, and promotions durable consult-and-record surfaces. Schema-versioned, fail-soft writers, weekly Wilson-CI rollups. The substrate that makes pattern #6 (closed-loop routers) actually closed.

### 14. Skill + Rule + Workflow Trinity (Development Harness)

The development harness follows the same separation it imposes on the runtime: **skills** (procedural how-to, on-demand) · **rules** (durable invariants, always-on) · **workflows** (slash commands for repeatable runs). The agent that builds the system is governed by the same discipline as the system it builds.

---

## System Guarantees (Enforced Invariants)

```
DETERMINISM         · Same input → same output → same digest
REPLAYABILITY       · Replayable paths bind execution evidence to digest keys
ENTROPY CONTROL     · Wall-clock and randomness use are explicit proof obligations
CONTROLLED MUTATION · Durable writes route through the UWG contract
FULL PROVENANCE     · Decisions tie back to state, policy hash, and evidence
EXECUTION ISOLATION · L2 actions occur in sandboxed environments
GOVERNANCE FIRST    · Nothing executes without policy validation
LAYERED SCALING     · Single-accountability layers enable safe growth
```

These are not features — they are **structural invariants** with hooks, gates, and tests behind each one.

---

## Architecture at a Glance

```
                          User / API Request
                                  ↓
             ┌────────────────────────────────────────┐
             │ L1 Cognition · Librarian               │   bounded LLM → plan
             └───────────────────┬────────────────────┘
                                 ↓
             ┌────────────────────────────────────────┐
             │ L0 Routing · Dispatcher                │   route authority
             │ R1 cache · R3 RAG · R4 action · R5 fallback │
             └───┬───────────────┬───────────────┬────┘
                 ↓               ↓               ↓
          [cache hit]      C0 Context        L2 Execution
                            (grounding)         │
                                                ↓
                                         L3 Orchestrator
                                         (when complex)
                                                ↓
             ┌────────────────────────────────────────┐
             │ L5 Safety · cross-cutting veto         │   policy plane
             └───────────────────┬────────────────────┘
                                 ↓
             ┌────────────────────────────────────────┐
             │ Exit Spine · allow / deny / reroute    │
             │ COMMIT → UWG → L4 (only mutation path) │
             └───────────────────┬────────────────────┘
                                 ↓
             ┌────────────────────────────────────────┐
             │ L6 Observer · shadow eval, replay, telemetry │
             │ L7 Auditability · signed proof bundles       │
             └────────────────────────────────────────┘
```

**Primary runtime path:** L1 → L0 → [L3] → L2 → Exit → UWG → L4
**State mutation path:** L2 output → L5 validation → UWG → L4 (sole write authority)
**Learning path:** L6 reads ledgers + telemetry → shadow eval → promotion via L6/promo gate (no current-run mutation)

---

## How This Repository Is Governed

This repository is itself an example of the discipline it argues for. It is governed at four control planes, with each plane catching a different class of failure:

| Control plane | What it catches | SSOT |
|---|---|---|
| **AI-time discipline** — Codex rules, hooks, skills, and automation contracts | Scope drift, unauthorized edits, missing plan registration, MCP misuse, deferred scope going unrecorded | `.codex/` |
| **Commit-time hygiene** — pre-commit + focused gates | Lint, syntax, plan/report SSOT routing, schema validity | `.pre-commit-config.yaml`, `ops_scripts/ci/check_*.py` |
| **Repo-wide governance** — ADG CI graph + ratchets | Layer violations, write-sovereignty bypasses, dead imports, anti-pattern regressions, exception-handling drift, registry/policy drift | `tools/generate/generate_full_adg.py`, `artifacts/adg/` |
| **Runtime evidence** — tests, coverage, OTel-derived witness | Behavioral correctness, replay determinism, runtime trace attestation | `tests/`, `tools/cert/`, `certification/` |

Each plane is **independent of the others**. A test cannot replace a graph gate; a hook cannot replace a test; CI cannot replace AI-time discipline. The layered model is deliberate: **autonomous coding inside an SDLC requires more than one kind of evidence**, because no single evidence kind is honest about all of the failure modes that AI assistance introduces.

For a deeper walk-through of the governance model and the SQL queries a reviewer can run against the ADG snapshot, see [`docs/SVP_ENGINEERING_GOVERNANCE_README.md`](docs/SVP_ENGINEERING_GOVERNANCE_README.md).

---

## Application Portfolio

The GitHub-facing app portfolio below is a navigation map for active app and shared-library surfaces. Runtime-governance classification is separately anchored in [`apps_shared/integrations/app_registry.py`](apps_shared/integrations/app_registry.py), which is the authoritative source for governed vs. formal-exception status.

| App | What it does | README | Runbook | SLO | SVP Review | Threat Model |
|---|---|:-:|:-:|:-:|:-:|:-:|
| [`apps_architect`](apps_architect/) | Pattern Collection & Repo Hardening Engine — deterministic pattern scan and hardening-rule emission | — | — | — | — | — |
| [`apps_eval`](apps_eval/) | Evaluation Lab — benchmarks `agentic_core` and app workloads against deterministic scenarios | [→](apps_eval/README.md) | — | — | — | — |
| [`apps_exec`](apps_exec/) | Executive Brief Generator — governed registry surface with historical product docs | — | — | — | [→](docs/reports/apps_exec/PRODUCT_SPEC.md) | — |
| [`apps_lic`](apps_lic/) | Lifecycle Intelligence & Communication — multi-hop profile + research + grounded outbound authoring | [→](apps_lic/README.md) | [→](apps_lic/RUNBOOK.md) | [→](apps_lic/SLO.md) | [→](apps_lic/SVP_ENGINEERING_REVIEW.md) | [→](apps_lic/THREAT_MODEL.md) |
| [`apps_qna`](apps_qna/) | Interview Q&A Card-Pack Builder — parameterized interview-prep packs with routed retrieval | [→](apps_qna/README.md) | [→](apps_qna/RUNBOOK.md) | [→](apps_qna/SLO.md) | [→](apps_qna/SVP_ENGINEERING_REVIEW.md) | — *(see [`PATHOLOGY_TAXONOMY.md`](apps_qna/PATHOLOGY_TAXONOMY.md))* |
| [`apps_research`](apps_research/) | Autonomous Research Engine — structured research artifacts from topic + mode, plus compact downstream briefs for `apps_rg` and `apps_lic` | [→](apps_research/README.md) | [→](apps_research/RUNBOOK.md) | [→](apps_research/SLO.md) | [→](apps_research/SVP_ENGINEERING_REVIEW.md) | — |
| [`apps_rg`](apps_rg/) | AI Résumé Generator — grounded résumé synthesis with ATS-coverage gates | — | — | — | [→](docs/reports/apps_rg/SVP_ENGINEERING_REVIEW.md) | — |
| [`apps_underwriting_ai`](apps_underwriting_ai/) | Commercial credit underwriting decision support — zero-authority surface over `agentic_core` | [→](apps_underwriting_ai/README.md) | [→](apps_underwriting_ai/RUNBOOK.md) | [→](apps_underwriting_ai/SLO.md) | [→](apps_underwriting_ai/SVP_ENGINEERING_REVIEW.md) | [→](apps_underwriting_ai/THREAT_MODEL.md) |
| [`apps_shared`](apps_shared/) | Shared adapters, validators, HOP executor, proof harness — library-only | [→](apps_shared/README.md) | [→](apps_shared/RUNBOOK.md) | [→](apps_shared/SLO.md) | [→](apps_shared/SVP_ENGINEERING_REVIEW.md) | [→](apps_shared/validators/proof/THREAT_MODEL.md) |

> Historical `apps_exec` product snapshots remain under `archives/apps_exec_20260505/`; the current registry surface is the governed adapter named in `apps_shared/integrations/app_registry.py`.

`apps_research` also exposes compact downstream consumer briefs:
- `apps_rg` uses `downstream_research_substrate_v1`
- `apps_lic` uses `apps_lic_research_substrate_v1`

Consolidated SVP Engineering reviews live under [`docs/reports/`](docs/reports/) — see the per-app subfolders for the latest certification status.

---

## Quickstart

```bash
git clone https://github.com/Siamese001/Agentic-Workflow.git
cd Agentic-Workflow

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e .

# Optional caching/telemetry stack
docker compose -f docker-compose.redis.yml up -d
docker compose -f docker-compose.otel.yml up -d

# Run any app
python -m apps_eval --all
python -m apps_research --topic "agentic governance" --mode brief
python -m apps_underwriting_ai --demo

# Architecture proof pack (exit 0 = green; inspect current output)
python ops_scripts/ci/run_architecture_proof.py
```

---

## Governed Architecture Proof Pack

Current registry snapshot: three governed entries and five formal exceptions, with one release gate. The direct conformance gate below is authoritative for registry counts; the top-level proof command is the suite entrypoint for current pass/fail status.

```bash
python ops_scripts/ci/check_governed_app_conformance.py
python ops_scripts/ci/run_architecture_proof.py
```

| Suite | Validates |
|---|---|
| S1 — Conformance Gate | Registry + imports: CONF01-08 + EXCF01-08 (52 checks) |
| S2 — Exception Framework | Behavioral E2E across governed apps + eval/uw exception controls |
| S3 — Regression Check | Evidence governance regression baseline (RC01-12) |

Registry status as of the committed docs snapshot:

| Status | Apps |
|---|---|
| Governed | `apps_exec`, `apps_research`, `apps_rg` |
| Formal exception | `apps_architect`, `apps_eval`, `apps_lic`, `apps_qna`, `apps_underwriting_ai` |

**Reviewer journey:**

1. [`docs/architecture/REVIEWER_GUIDE.md`](docs/architecture/REVIEWER_GUIDE.md) — executive walkthrough + engineer quickstart
2. [`docs/architecture/architecture-proof-pack.md`](docs/architecture/architecture-proof-pack.md) — proof command map + gap maps
3. `python ops_scripts/ci/run_architecture_proof.py` — run the proofs yourself
4. [`docs/architecture/ROLLOUT_CLOSEOUT.md`](docs/architecture/ROLLOUT_CLOSEOUT.md) — final status + known-gap register

---

## Tech Stack

- **Python** — core orchestration · Pydantic contracts · pytest harness
- **SQLite** — deterministic state · ADG canonical snapshot · 30+ append-only ledgers
- **Redis** — L1 retrieval cache · ADG hot projection · coordination fabric
- **FAISS / ChromaDB** — vector retrieval · semantic search MCP
- **OpenTelemetry** — runtime ADG ingest · trace correlation · anomaly detection
- **OpenAI + local LLMs (vLLM on WSL2 GPU)** — multi-model routing
- **Notion + GitKraken + DeepWiki + Tavily MCP servers** — governance, code review, research surfaces
- **Containerized** — Docker Compose for Redis + OTel collectors

---

## Public Positioning Index

- [`docs/THOUGHT_LEADERSHIP_INDEX.md`](docs/THOUGHT_LEADERSHIP_INDEX.md) — themes this repository argues for publicly
- [`docs/EXECUTIVE_OVERVIEW.md`](docs/EXECUTIVE_OVERVIEW.md) — bottom-line positioning for CTO / SVP Engineering readers
- [`docs/RECRUITER_GUIDE.md`](docs/RECRUITER_GUIDE.md) — plain-English explanation for hiring and leadership audiences

> **Note.** This repository is a **public proof asset and reference design**, not a confidential client implementation. Client-specific work is kept private; what is published here is the architecture and the reasoning behind it.

---

## Start Here (by Audience)

| Audience | Start with | Why |
|----------|------------|-----|
| Recruiter / hiring manager | [`docs/RECRUITER_GUIDE.md`](docs/RECRUITER_GUIDE.md) | Plain-English explanation of what this repo demonstrates and the roles it supports |
| CTO / SVP Engineering | [`docs/EXECUTIVE_OVERVIEW.md`](docs/EXECUTIVE_OVERVIEW.md) | Bottom-line positioning, runtime control model, and platform-leadership signal |
| AI platform engineer | [`docs/RUNTIME_CONTROL_PLANE.md`](docs/RUNTIME_CONTROL_PLANE.md) | Technical narrative of the control plane: layers, separation of duties, write model, replay |
| Governance / risk / compliance | [`docs/RUNTIME_CONTROL_PLANE.md`](docs/RUNTIME_CONTROL_PLANE.md) + [`docs/EXECUTIVE_OVERVIEW.md`](docs/EXECUTIVE_OVERVIEW.md) | Read-broad/write-strict model, UWG single-door commit, replay and audit evidence |
| Deep technical reviewer | [`docs/architecture/REVIEWER_GUIDE.md`](docs/architecture/REVIEWER_GUIDE.md) + this README | Executive walkthrough plus the full architecture, proof pack, and ADRs |
| CTO / SVP Engineering — governance lens | [`docs/SVP_ENGINEERING_GOVERNANCE_README.md`](docs/SVP_ENGINEERING_GOVERNANCE_README.md) | Why this repo treats AI-time discipline, commit hygiene, ADG CI, and runtime evidence as four independent control planes |

---

## Documentation Map

### Architecture & governance
- **Reviewer Guide:** [`docs/architecture/REVIEWER_GUIDE.md`](docs/architecture/REVIEWER_GUIDE.md)
- **Architecture Proof Pack:** [`docs/architecture/architecture-proof-pack.md`](docs/architecture/architecture-proof-pack.md)
- **Rollout Closeout:** [`docs/architecture/ROLLOUT_CLOSEOUT.md`](docs/architecture/ROLLOUT_CLOSEOUT.md)
- **Release Readiness:** [`docs/architecture/RELEASE_READINESS.md`](docs/architecture/RELEASE_READINESS.md)
- **Governed-App Contract:** [`docs/architecture/governed-app-contract.md`](docs/architecture/governed-app-contract.md)
- **Architecture ADRs:** [`docs/architecture/adr/`](docs/architecture/adr/)
- **Standards:** [`docs/STANDARDS.md`](docs/STANDARDS.md)

### Subsystem & tooling
- **ADG prompt-assembly subsystem:** [`tools/adg/prompt_assembly/README.md`](tools/adg/prompt_assembly/README.md)
- **Calibration (Wilson-CI weekly reports, ledger binders):** [`tools/calibration/README.md`](tools/calibration/README.md)
- **Local LLM (vLLM on WSL2 GPU):** [`tools/vllm/README.md`](tools/vllm/README.md)
- **OpenTelemetry refactor notes:** [`tools/otel/README_REFACTOR.md`](tools/otel/README_REFACTOR.md)
- **MCP servers & SDK wrappers:** [`infrastructure/sdks_mcps/README.md`](infrastructure/sdks_mcps/README.md)
- **Reference docs root:** [`docs/reference/README.md`](docs/reference/README.md)
- **SVP Engineering reviewer hub:** [`docs/svp/README.md`](docs/svp/README.md)
- **Author-Gate reports:** [`docs/reports/author-gate/README.md`](docs/reports/author-gate/README.md)
- **Calibration reports:** [`docs/reports/calibration/README.md`](docs/reports/calibration/README.md)

### By app
See the [Application Portfolio](#application-portfolio) table above.

---

## Community Health And Public Scope

This repository is published as a public proof asset and reference design. At this docs snapshot, the repo does not yet include root-level `LICENSE`, `SECURITY`, `SUPPORT`, `CONTRIBUTING`, or `CODE_OF_CONDUCT` files. Treat those as explicit community-health gaps rather than implied policy, support, licensing, or disclosure commitments.

For currently supported reviewer evidence, use the proof commands and architecture documents above; for governance process, use `AGENTS.md`, `docs/codex-primary-execution.md`, and `.codex/**`.

---

## The Public Engineering Arguments

This repository is the evidence behind a small set of public arguments:

1. **The agent is not the product.** The governed runtime around it is. Models are interchangeable; the runtime is the moat.
2. **Tests prove behavior; the graph proves governability.** Most repos try to make tests carry both jobs. They cannot.
3. **Lowest viable agency.** Give the agent the smallest amount of autonomy that still solves the problem; prove it; expand only with evidence.
4. **Decisions are scored, not voted.** Author-Gate scoring (`[0.00–1.00]`, confidence, gap-to-next, dominance rule) replaces "the model picked one".
5. **Known debt is ratcheted, not normalized.** P0/P1/P2/P3 ratchets fail builds when known debt classes worsen.
6. **Certification is compiler-only.** No human writes `SIGNED_OFF`. Evidence compiles into a signed Merkle bundle, or it does not exist.
7. **Runtime governance ≠ static AI policy.** Policy documents do not survive contact with a live agent; runtime gates do.

See [`docs/THOUGHT_LEADERSHIP_INDEX.md`](docs/THOUGHT_LEADERSHIP_INDEX.md) for the long-form series.

---

## Final Positioning

This is not another agent framework. It is a **deterministic AI control plane** — the engineering substrate for reproducibility, auditability, and safe autonomous execution in regulated environments.

- **For platform leaders:** the reference architecture for what "governed agentic AI" actually looks like when it has to clear an enterprise control boundary.
- **For engineers:** a working implementation of route authority, verified context, bounded execution, exit evaluation, write control, replay, and shadow learning.
- **For the field:** a counter-argument to the prevailing "bigger model + more tools = agent" framing.

**AI that behaves like software, not experiments.**

— [Amit Ayer](https://github.com/Siamese001), SVP-level Agentic Engineer

---

*Last updated: July 2026 — maintained by [Amit Ayer](https://github.com/Siamese001).*
