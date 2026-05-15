# Repository Governance Architecture

This repository is governed as a production engineering system, not just a codebase with tests.

The control model has two primary governance layers:

1. **Windsurf rules and hooks**: AI-time controls that shape how work is planned, edited, verified, and audited while the agent is operating.
2. **ADG CI**: repo-wide structural governance that converts the codebase into a queryable architecture graph and fails the build when architecture, routing, write authority, evidence, or safety contracts regress.

Tests remain important, but they are not asked to carry architectural governance. In this repo, tests prove runtime behavior; ADG CI proves whether the system is still structurally governable.

---

## Executive summary

Most repositories rely on tests as the primary quality layer. That works for product behavior, but it does not reliably catch architecture drift, illegal dependency paths, gate bypasses, silent exception swallowing, missing runtime witnesses, stale shims, config drift, or agent/tool boundary violations.

This repo uses a stronger pattern:

```text
AI-time discipline    -> Windsurf rules, skills, workflows, and hooks
Commit-time hygiene   -> pre-commit and focused local gates
Repo-wide governance  -> ADG CI graph generation, ratchets, structural checks
Runtime proof         -> tests, coverage, replay evidence, and OTel-derived witnesses
```

The result is a layered control system where the agent is guided before it acts, commits are checked before they land, and the full repository is continuously audited as a graph.

---

## Why this matters to an engineering reviewer

An SVP Engineering reviewer should care about three things:

1. **Can the system keep scaling without becoming ungovernable?**
2. **Can engineering leadership see architecture drift before it becomes delivery drag?**
3. **Can autonomous or AI-assisted coding be allowed without turning the repo into a pile of local exceptions?**

This governance model answers those directly.

The repo does not rely only on developer intent or local unit tests. It encodes architectural expectations as machine-checkable gates and turns the repository itself into an auditable system of record.

---

## Layer 1: Windsurf rules and hooks

Windsurf is the AI-time control layer. It governs how the coding agent behaves before, during, and after changes.

### What it does

Windsurf provides the repo's active operating discipline:

- Keeps always-on rules lean and constitutional.
- Routes deeper procedures into skills and workflows only when needed.
- Separates analyze, plan, edit, and verify modes.
- Forces evidence-first behavior instead of guesswork.
- Adds hook-based enforcement around reads, writes, MCP calls, prompts, command execution, and cascade completion.
- Captures plans, deferred scope, author-gate decisions, next steps, and audit trails.

### Evidence in this repo

The `.windsurf` control surface enforces discipline at three points: **before** an action, **during** it, and **after** it. Counts move week-to-week as rules are consolidated, demoted to skills, or promoted to hooks; the *shape* is the signal.

| Surface | Role | SSOT |
|---|---|---|
| Constitutional rules | Always-on invariants the agent reads every turn | `.windsurf/rules/constitutional.md`, `global_rules.md` |
| Conditional rules | Loaded on demand by trigger phrase | frontmatter `trigger: model_decision` |
| Skills | Procedural how-to, on-demand (third-person, deterministic) | `.windsurf/skills/<name>/SKILL.md` |
| Workflows | Slash-command runbooks for repeatable sequences | `.windsurf/workflows/*.md` |
| Hook scripts | Deterministic Python at pre/post action moments | `.windsurf/scripts/*.py` |
| Schemas | Machine-validated contracts for ledgers, manifests, certs | `.windsurf/schemas/*.{sql,json,yaml}` |
| Plans | Per-task SSOT with wave/phase decomposition | `.windsurf/plans/<slug>-<6hex>.md` |

The two-tier model is deliberate. **Rules state invariants; skills carry procedure; hooks enforce.** Adding rules without a hook is advisory; adding hooks without a rule is brittle. Every load-bearing invariant lives in one SSOT and is enforced by all three layers, so drift is structurally hard.

Key files to inspect:

```text
.windsurf/RULES_INDEX.md
.windsurf/hooks.json
.windsurf/rules/constitutional.md
.windsurf/rules/global_rules.md
.windsurf/rules/adg-canonical-invariants.md
.windsurf/rules/author-gate-enforcement.md
.windsurf/rules/ssot-folder-enforcement.md
.windsurf/skills/*/SKILL.md
.windsurf/workflows/*.md
.windsurf/scripts/*.py
```

### Hook coverage

The configured hook model covers both pre-action and post-action moments. The current `hooks.json` registers **48 hook entries across 10 phases**:

```text
Before work:
  pre_user_prompt        (10 entries — classifier, reminders, queue surfacing)
  pre_read_code          ( 1)
  pre_run_command        ( 1)
  pre_write_code         ( 4 — author-gate, write-gate, scope-gate, fortknox-guard)
  pre_mcp_tool_use       ( 1)

After work:
  post_write_code        ( 4)
  post_run_command       ( 1)
  post_mcp_tool_use      ( 1)
  post_cursor_agent_response  (24 — capture markers, audits, ledger writebacks)
  post_setup_worktree    ( 1)
```

This matters because many AI-coding failures happen before a traditional test ever runs. Examples include scope drift, wrong tool use, unsafe write paths, missing plan registration, MCP misuse, or unrecorded deferred work.

Windsurf hooks catch those process failures at the moment they happen.

### Operating discipline (visible signals)

Every Cursor Agent response in this repo emits structured markers that the post-action hooks parse and route into ledgers and Notion databases:

```text
SR_PLAN / SR_APPROVAL / SR_EXECUTE / SR_VERIFY     -> reasoning packet (T2/T3)
DECISION_CAPTURED:                                 -> Author-Gate ledger
DEFERRED_SCOPE: P1..P5                             -> backlog row in Notion
NEXT_STEP:                                         -> out-of-scope idea capture
ROUTER_DECISION: layer=<L> route=<r>               -> router ledger event
ADG Provenance: backend=<...> snapshot=<...>       -> evidence stamp
SCOPE_RESET: from=<...> to=<...>                   -> topic transition signal
PLAN_CREATED: slug=<...>                           -> Notion Plans DB registration
AG_QUEUE_SEED: id=<...> depends_on=<...>           -> Author-Gate queue plan-time seed
```

The point is not the markers. The point is that **agent behavior produces inspectable, queryable artifacts by default** — which is the precondition for trusting autonomous coding inside an SDLC.

---

## Layer 2: ADG CI

ADG CI is the repo-wide architecture governance layer.

It does not ask only, "do the tests pass?" It asks, "is the system still structurally legal?"

### What ADG CI generates

The ADG pipeline produces a non-redundant artifact set centered on a queryable SQLite graph:

```text
adg_snapshot_<timestamp>.json         metrics snapshot
adg_indexed_<timestamp>.sqlite        primary queryable architecture store
adg_file_graph_<timestamp>.json       file-level graph
adg_symbol_graph_<timestamp>.json     symbol-level graph
adg_governance_graph_<timestamp>.json governance graph
```

The current ADG snapshot (`adg_indexed_05052026_0722.sqlite`) contains:

| ADG signal | Count |
|---|---:|
| Nodes | 140,743 |
| Edges | 863,353 |
| Canonical violations | 12,819 |
| Overlay violations | 120,577 |
| `imports` edges | 187,442 |
| `reads_from` edges | 175,088 |
| `flows_to` edges | 124,543 |
| `resolves_callsite` edges | 91,393 |
| `controls_flow` edges | 80,778 |
| `emits_side_effect` edges | 47,032 |
| `covers` edges (test coverage relations) | 18,218 |
| `writes_to` edges | 3,132 |

Edge authority is also typed:

| Authority status | Edges |
|---|---:|
| `external` | 405,530 |
| `test_only` | 217,655 |
| `verified` | 217,459 |
| `unresolved` | 22,602 |
| `dynamic` | 107 |

This gives reviewers something concrete: the repo is not being governed by informal diagrams. It is being converted into an inspectable graph with hundreds of thousands of *typed* relationships, and every edge carries an authority status that says how much trust to place in it.

### What ADG CI checks

ADG CI enforces several classes of engineering control:

| Control class | What it protects |
|---|---|
| Structural conformance | Layering, routing discipline, spine alignment, boundary integrity |
| P0/P1/P2/P3 ratchets | Prevents known debt classes from worsening silently |
| Dead production imports | Prevents stale or misleading dependency surfaces |
| Agentic anti-patterns | Catches broad catches, silent swallows, unsafe dynamic behavior, and related failure modes |
| Write sovereignty | Detects durable writes that bypass required gateways |
| Registry lift | Connects declared capabilities, MCP config, policy packs, and agent specs into the graph |
| Edge authority backfill | Classifies graph edges by authority status such as verified, unresolved, external, test-only, or dynamic |
| Witness-tier gates | Separates plumbing evidence, test evidence, and live runtime evidence |
| Post-ADG gates | Runs focused subprocess gates for wiring, config references, lifecycle pairing, exception contracts, and test-harness coverage |
| Drift and provenance | Captures commit SHA, repo tree hash, graph hash, artifact digest, and end-of-run state checks |

### What failure modes this intercepts

AI-assisted development introduces a new class of defect that traditional CI does not catch: **architecturally plausible code that violates structural intent**. A model can produce a file that compiles, type-checks, passes unit tests, and quietly:

- writes to durable state outside the Universal Write Gateway;
- imports across a layer boundary that was supposed to be one-way;
- catches `Exception` and swallows the recovery path;
- adds a new provider call outside the approved seam;
- reuses a deprecated shim instead of the canonical surface;
- introduces a tool surface that nobody routes to;
- creates a config reference to a key that was retired three plans ago.

None of those fail a unit test. All of them fail an architecture graph. That is why this repo treats the graph as a **first-class CI artifact**, not as a diagram on a wiki.

### Why this is different from tests

Tests are scenario-based.

```text
Input -> execution -> expected output
```

ADG CI is system-contract-based.

```text
Repo -> graph -> invariants -> gates -> ratchets -> evidence -> decision
```

That makes it better at catching issues like:

- Direct writes that bypass the Universal Write Gateway.
- Cross-layer dependency violations.
- Provider calls outside approved seams.
- Dead imports that make the repo appear more connected than it is.
- Missing lifecycle closures.
- Exception handling mismatches.
- Test files that import production code in misleading or incomplete ways.
- Shims that preserve compatibility but need retirement discipline.
- Runtime witness gaps where static structure exists but live proof is absent.

---

## How the layers work together

```text
+--------------------------------------------------------------+
|                    Engineering Intent                         |
|       architecture, safety policy, delivery discipline        |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
| Layer 1: Windsurf AI-time governance                          |
| rules, hooks, skills, workflows, author gates, scope capture  |
|                                                               |
| Purpose: guide and constrain the agent while work is happening|
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
| Layer 2: Commit and local verification                        |
| pre-commit, lint, syntax, focused tests, local gates          |
|                                                               |
| Purpose: stop obvious defects before they enter the repo      |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
| Layer 3: ADG CI architecture governance                       |
| static graph, registry graph, runtime proof view, ratchets    |
|                                                               |
| Purpose: prove the repo is still structurally governable      |
+-------------------------------+------------------------------+
                                |
                                v
+--------------------------------------------------------------+
| Layer 4: Runtime evidence                                     |
| tests, coverage, replay, OTel-derived runtime witnesses       |
|                                                               |
| Purpose: prove important paths actually execute correctly     |
+--------------------------------------------------------------+
```

The important point is that no single layer is pretending to do everything.

Windsurf prevents many bad actions before they happen. Pre-commit catches local hygiene and obvious failures. Tests prove behavior. ADG CI audits the whole repository against architectural contracts.

---

## Reviewer inspection path

A reviewer can inspect the governance model in this order.

### 1. Start with the operating model

```text
.windsurf/RULES_INDEX.md
```

Look for:

- Two-tier rule model.
- Always-on constitutional floor.
- Load-on-demand skills and workflows.
- Evidence-first discipline.
- Clear split between advisory rules and deterministic hooks or CI gates.

### 2. Inspect active hook enforcement

```text
.windsurf/hooks.json
.windsurf/scripts/
```

Look for:

- Pre-write gates.
- Post-write audits.
- MCP tool-use gates.
- Cursor Agent response audits.
- Scope drift and deferred-scope capture.
- Author-gate capture and miss detection.

### 3. Inspect ADG generation

```text
tools/generate/generate_full_adg.py
```

Look for:

- Static scan and artifact generation.
- Temp artifact write followed by validity checks before production commit.
- SQLite integrity checks.
- P0/P1/P2 ratchets.
- Structural conformance gates.
- Anti-pattern gates.
- Runtime proof view construction.
- Registry bucket lift.
- Edge authority backfill.
- Parallel post-ADG gates.
- Deferred failure aggregation.

### 4. Inspect the graph artifact

```bash
# Resolve the latest snapshot deterministically
SNAPSHOT=$(ls -t artifacts/adg/adg_indexed_*.sqlite | head -1)
sqlite3 "$SNAPSHOT"
```

```sql
-- Edge taxonomy: structural vs semantic vs governance
SELECT relation_type, COUNT(*) AS edges
FROM edges
GROUP BY relation_type
ORDER BY edges DESC;

-- Edge authority distribution: verified / external / test_only / unresolved / dynamic
SELECT COALESCE(authority, '<NULL>') AS authority, COUNT(*) AS edges
FROM edges
GROUP BY authority
ORDER BY edges DESC;

-- Write-path sovereignty: any rows here are durable writes that bypass the UWG
SELECT * FROM mv_gateway_bypass_paths LIMIT 25;

-- Cross-layer authority breaches (e.g. L6 mutating, L1 calling raw infra)
SELECT * FROM mv_authority_boundary_breaches LIMIT 25;

-- Top hotspots ranked by coverage gap and structural centrality
SELECT * FROM mv_hotspot_coverage_risk
ORDER BY combined_risk_score DESC
LIMIT 25;

-- P-views: pre-classified architectural concerns (P0 = blocking, P3 = isolated)
SELECT name FROM sqlite_master
WHERE type = 'view' AND name LIKE 'v_p%'
ORDER BY name;
```

The `v_p0_*` … `v_p3_*` family is the punchline of the graph layer: defects are not surfaced as a heap, they are *pre-classified by severity band*, and CI ratchets guard each band independently. New P0s fail the build; existing P0s have a published burndown.

### 5. Inspect governance maturity honestly

A mature reviewer will not only ask what the system catches. They will ask where proof is still thin.

In the current snapshot, the architecture graph is strong, but runtime attestation should continue to mature:

| Area | Current observation | Engineering implication |
|---|---|---|
| Static graph | Strong | Large typed graph with broad repo coverage |
| Registry graph | Present | Declarative configs and policy surfaces are lifted into graph form |
| Runtime proof view (`v_runtime_proof`) | Empty in inspected snapshot | Continue wiring OTel-derived runtime proof into ADG views |
| Coverage table (`coverage_by_path`) | Empty in inspected snapshot | Ensure `.coverage` is produced before ADG generation when coverage-linked hotspot analysis is required |
| Gateway bypass view (`mv_gateway_bypass_paths`) | Zero rows in inspected snapshot | Good signal, continue enforcing as hard gate |
| Authority boundary breach view (`mv_authority_boundary_breaches`) | Zero rows in inspected snapshot | Good signal, continue enforcing as hard gate |

This is the right maturity posture: strong graph governance today, with runtime witness depth as the next hardening frontier — named, not hidden.

---

## What this is not

This governance model is not a substitute for tests.

Tests are still required for:

- User-visible behavior.
- Unit-level correctness.
- End-to-end flows.
- Regression proof.
- Runtime edge cases.
- Replay determinism.
- Contract behavior.

ADG CI should not replace tests. It should decide whether the codebase remains architecturally safe enough for tests to be meaningful.

The clean split is:

```text
Tests prove behavior.
ADG CI proves governability.
Windsurf controls the AI-time work process.
```

---

## Why this is a serious engineering pattern

This repo is moving from "test-driven quality" to "governed-runtime quality."

That matters because AI-assisted development increases both speed and risk. A coding agent can generate correct local behavior while still introducing architectural debt, control-plane bypasses, duplicated surfaces, stale compatibility shims, or unsafe exception handling.

The governance layers here reduce that risk by making the repo inspectable at multiple levels:

```text
Behavioral correctness      -> tests
Local change hygiene        -> pre-commit
Agent behavior discipline   -> Windsurf rules and hooks
Architecture correctness    -> ADG CI
Runtime evidence            -> coverage, replay, OTel witnesses
Decision traceability       -> plans, author gates, ledgers, manifests
```

That is the core engineering claim: this repo is designed so that autonomous code generation is not trusted blindly. It is guided, constrained, audited, and ratcheted through machine-checkable controls.

---

## Reviewer takeaway

The impressive part is not the count of rules or the size of the graph. It is the small set of engineering arguments this repository commits to and proves:

1. **Tests prove behavior; the graph proves governability.**
   Two different evidence kinds, two different tools. Tests cannot catch a layer violation any more than a graph can catch a wrong answer.

2. **Decisions are scored, not voted.**
   Every ambiguous author-time decision is surfaced as scored options on `[0.00–1.00]` with explicit confidence, gap-to-next, and a dominance rule (top ≥ 0.85 AND gap ≥ 0.12 → recommended alone). Decisions land in an append-only ledger; the ledger feeds the next decision.

3. **Known debt is ratcheted, not normalized.**
   P0/P1/P2/P3 violation classes have ratchets in CI. New debt fails the build; existing debt has a published burndown. Nothing rots silently.

4. **Certification is compiler-only.**
   No human writes `SIGNED_OFF` prose. A compiler consumes evidence assertions and emits a Merkle-rooted, signed bundle. A canary requirement and a mutation-rejection canary prove the verifier is not asleep. Doctrine: SLSA L3 / in-toto / Sigstore.

5. **Runtime witness is the next frontier — and the repo says so.**
   Static graph and registry graph are strong. `v_runtime_proof` and `coverage_by_path` are deliberately empty in the inspected snapshot — runtime attestation depth is the next hardening wave, and it is named, not hidden.

For a senior engineering reviewer, the strongest signal is this:

```text
The repository is not asking, "does the code work?"
It is asking, "can this system keep changing safely
while autonomous coding agents are turned on?"
```
