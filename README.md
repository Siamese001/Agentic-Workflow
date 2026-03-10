# Agentic Workflow

Enterprise agentic AI platform for deterministic multi-agent execution, bounded side effects, auditable recovery, and governed deployment.

**Executive Summary**

This repository demonstrates how to build agentic systems that are reliable enough for enterprise environments rather than just impressive in demos.

Most agent frameworks focus on agent composition and prompt orchestration. This system instead focuses on the **control plane required to make multi-agent systems trustworthy, inspectable, and operationally safe.**

The platform treats routing, execution, mutation control, safety enforcement, replayability, and recovery as **first-class engineering primitives** rather than application glue.

The result is a layered agentic execution substrate that enables complex workflows to run with explicit control over side effects, deterministic decision boundaries, and auditable system behavior.

**What This System Demonstrates**

This repository is not a collection of agents. It is a platform that demonstrates how governed agentic systems can be engineered.

Key properties include:

* **Deterministic routing**
  Critical routing and orchestration decisions generate stable digests tied to exact inputs so behavior can be inspected and compared across runs.

* **Bounded side effects**
  Filesystem writes, model calls, and embedding generation pass through explicit gateways instead of being scattered throughout the codebase.

* **Architectural enforcement**
  AST analysis verifies architectural rules such as layer boundaries and dependency direction.

* **Fail-closed behavior**
  Integrity failures stop execution rather than silently degrading into partial results.

* **Auditable recovery**
  Validation and healing components repair failures in ways that are observable and testable.

* **Reusable multi-app architecture**
  Multiple applications run on the same shared platform rather than embedding logic into one-off scripts.

**Working Applications**

Two applications run on top of the same shared agentic core.

1. **apps_lic**

   Governed LinkedIn outreach generation system.

   Capabilities:

   * Profile analysis
   * Research and context enrichment
   * Persona routing
   * Message generation
   * Validation and QA
   * Recovery loops for output quality

2. **apps_rg**

   Resume generation system.

   Capabilities:

   * Persona-driven resume construction
   * Evidence-aware bullet generation
   * Company-specific tailoring
   * Validation and healing loops

These applications demonstrate that the platform is **reusable infrastructure** rather than a single-purpose agent pipeline.

**Why This Architecture Exists**

Most agentic repos demonstrate that agents can call tools and coordinate tasks.

Very few demonstrate how those systems remain stable in real production environments.

Common failure modes in typical agent frameworks include:

* Hidden side effects scattered across the codebase
* Non-repeatable model behavior
* Silent fallbacks masking infrastructure failures
* Architectural drift over time
* Retry loops that hide errors instead of repairing them

This repository explores a different engineering model where agentic systems are treated as **infrastructure platforms with enforceable control surfaces.**

**Platform Architecture**

The system is organized into a layered architecture.

Execution flows downward through controlled interfaces while validation and observability flow upward.

1. **L0 Routing**

   * Entry policies
   * Reasoning policies
   * Envelope formation
   * Deterministic routing decisions

2. **L1 Cognition**

   * Perception modules
   * Reasoning systems
   * Action planning
   * Coordinator logic

3. **L2 Execution**

   * Execution pipelines
   * Sovereign gateways
   * Healing-tier routing
   * Execution cycle management

4. **L3 Orchestration**

   * Multi-step workflow coordination
   * Tool handshake protocols
   * Contract enforcement

5. **L4 State**

   * Retrieval systems
   * Vector store interaction
   * State inspection
   * Mutation monitoring

6. **L5 Safety**

   * Classification
   * Validation policies
   * Structural rule enforcement
   * SSOT governance

7. **L6 Observability**

   * Execution digests
   * Telemetry signals
   * Drift detection
   * Audit traces

**Sovereign Gateways**

Side effects are not allowed to occur directly inside arbitrary agents.

They pass through explicit gateways designed for policy enforcement and auditability.

* **Write Gateway**

  * Controls filesystem mutations
  * Verifies allowed write paths

* **LLM Gateway**

  * Centralizes model invocation
  * Routes between Gemini and local Qwen models

* **Embedding Gateway**

  * Generates embeddings
  * Verifies embedding artifact integrity

Separating these gateways ensures that mutation control, model governance, and embedding integrity remain independent and enforceable.

**Determinism and Replay**

Certain decision boundaries generate deterministic digests tied to exact inputs.

These digests allow:

* Run-to-run comparison
* Drift detection
* Execution audit trails
* Debuggable reasoning paths

The system does not attempt to make every component deterministic. Instead it ensures that **critical trust boundaries emit reproducible signals.**

**Architecture Dependency Graph**

The repository includes an AST-derived Architecture Dependency Graph.

The ADG is used to analyze the structure of the codebase and enforce architectural rules.

Capabilities include:

* Detecting layer boundary violations
* Identifying gateway bypass attempts
* Detecting dependency cycles
* Surfacing orphan modules
* Tracking structural drift

Using AST analysis turns architectural governance into **executable verification rather than documentation.**

**Failure Philosophy**

The platform is intentionally designed to make failures visible.

Examples include:

* Write attempts outside approved paths are rejected
* Embedding integrity mismatches stop execution
* Layer inversions trigger structural failures
* Prompt contract violations block dispatch
* Routing paths outside allowlists cause hard failure

The goal is not to eliminate failure.
The goal is to make failures **bounded, inspectable, and recoverable.**

**Testing and CI**

Continuous integration enforces architectural integrity in addition to running tests.

Checks include:

* Dependency graph enforcement
* Layer sovereignty validation
* Prompt governance verification
* Determinism guards
* Import correctness checks
* Application scope isolation
* Infrastructure boundary validation

Architectural drift therefore appears as a **CI failure** rather than an unnoticed design regression.

**Technology Stack**

Model inference

* Gemini APIs
* Qwen models via local vLLM

Embeddings

* FAISS
* multilingual-e5-large

Data and state

* Redis
* DuckDB
* SQLite
* Pandas

Structural analysis

* Python AST
* libcst

Prompt assembly

* XML semantic fencing
* Jinja2 StrictUndefined

Testing

* pytest
* pytest-asyncio
* Playwright

Continuous integration

* GitHub Actions

**How to Read This Repository**

Recommended reading order:

1. README
2. docs/technical/agentic_process_mapping_detailed.md
3. agentic_core/adg
4. agentic_core/L2_execution
5. agentic_core/L3_orchestration
6. agentic_core/L5_safety
7. apps_lic and apps_rg
8. tests

This order reveals the system from architecture through enforcement to application.
