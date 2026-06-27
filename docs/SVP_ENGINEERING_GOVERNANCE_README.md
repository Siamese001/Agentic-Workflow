# Repository Governance Architecture

This repository is governed as a production engineering system, not just a
codebase with tests.

The current governance model is Codex-primary:

1. **Codex execution discipline**: repo-owned rules, skills, hooks, automation
   contracts, and verification receipts under `.codex/`.
2. **Commit-time hygiene**: pre-commit and focused local gates.
3. **ADG CI**: repo-wide structural governance that converts the codebase into
   a queryable architecture graph and fails when routing, write authority,
   evidence, dependency, or safety contracts regress.
4. **Runtime proof**: tests, replay, certification, and OpenTelemetry-derived
   witnesses where available.

Tests remain important, but they are not asked to carry architectural
governance. In this repo, tests prove runtime behavior; ADG CI proves whether
the system is still structurally governable; Codex-primary enforcement governs
how AI-assisted work is planned, edited, verified, and published.

---

## Executive Summary

Most repositories rely on tests as the primary quality layer. That works for
product behavior, but it does not reliably catch architecture drift, illegal
dependency paths, gate bypasses, silent exception swallowing, stale shims,
config drift, or agent/tool boundary violations.

This repo uses a stronger pattern:

```text
Codex execution discipline -> rules, skills, hooks, automation contracts
Commit-time hygiene        -> pre-commit and focused local gates
Repo-wide governance       -> ADG graph generation, ratchets, structural checks
Runtime proof              -> tests, replay, certification, OTel witnesses
```

The result is a layered control system where the agent is guided before it
acts, commits are checked before they land, and the full repository is
continuously audited as a graph.

---

## Why This Matters to an SVP Engineering Reviewer

An SVP Engineering reviewer should care about three questions:

1. **Can the system keep scaling without becoming ungovernable?**
2. **Can leadership see architecture drift before it becomes delivery drag?**
3. **Can AI-assisted coding be allowed without turning the repo into local
   exceptions and hidden bypasses?**

This repository answers those questions by making architectural expectations
machine-checkable. It does not rely only on developer intent, prose policy, or
local unit tests. It turns the repository itself into an auditable system of
record.

---

## Layer 1: Codex Execution Discipline

Codex is the primary local execution surface for readiness, run evidence, and
verification receipts. Repo-owned governance files remain versioned in this
repository.

| Surface | Role | SSOT |
|---|---|---|
| Root adapter | Codex-facing operating contract | `AGENTS.md` |
| Primary execution contract | Readiness, evidence, closeout, publication rules | `docs/codex-primary-execution.md` |
| Rules | Durable invariants and task gates | `.codex/rules/` |
| Skills | Procedure loaded by task surface | `.codex/skills/` |
| Hooks | Native Codex hook registration and entrypoints | `.codex/hooks.json`, `.codex/hooks/**` |
| Governance scripts | Deterministic checks and verifiers | `.codex/governance/`, `scripts/governance/` |
| Automation contracts | Repo-owned scheduled/on-demand automation prompts | `.codex/automations/*/automation.toml` |
| State and schemas | Local governed state and validation contracts | `.codex/state/`, `.codex/schemas/` |

The enforcement-home guard is:

```bash
python scripts/governance/verify_codex_enforcement_home.py --json
```

The primary Codex contract guard is:

```bash
python scripts/governance/verify_codex_primary.py
```

These checks matter because they prevent this repo from drifting back into
parallel governance trees. `.codex` is the active repo governance home.

---

## Layer 2: Commit and Local Verification

Commit-time checks catch local hygiene issues before changes become review
surface:

- syntax and import failures;
- schema validity;
- focused contract gates;
- policy and config reference drift;
- documentation-only scope enforcement when a run is documentation-only.

This layer is intentionally narrower than ADG CI. It catches obvious local
defects and keeps commits reviewable.

---

## Layer 3: ADG CI

ADG CI is the repo-wide architecture governance layer.

It does not ask only, "do the tests pass?" It asks, "is the system still
structurally legal?"

The ADG pipeline produces a queryable SQLite architecture graph and companion
artifacts. The graph lets reviewers inspect:

- layer boundaries;
- write-sovereignty paths;
- routing and dispatcher authority;
- dependency hotspots;
- dead imports and stale shims;
- P0/P1/P2/P3 ratchet movement;
- registry and policy surface drift;
- runtime witness gaps when proof views are thin.

Representative inspection queries:

```sql
-- Edge taxonomy: structural vs semantic vs governance
SELECT relation_type, COUNT(*) AS edges
FROM edges
GROUP BY relation_type
ORDER BY edges DESC;

-- Edge authority distribution
SELECT COALESCE(authority, '<NULL>') AS authority, COUNT(*) AS edges
FROM edges
GROUP BY authority
ORDER BY edges DESC;

-- Write-path sovereignty: rows here are durable writes that bypass the gateway
SELECT * FROM mv_gateway_bypass_paths LIMIT 25;

-- Cross-layer authority breaches
SELECT * FROM mv_authority_boundary_breaches LIMIT 25;

-- P-views: pre-classified architectural concerns
SELECT name FROM sqlite_master
WHERE type = 'view' AND name LIKE 'v_p%'
ORDER BY name;
```

The important pattern is not any one query. The important pattern is that
architecture review becomes executable.

---

## Layer 4: Runtime Proof

Runtime evidence proves important paths actually execute correctly:

- unit, smoke, regression, and end-to-end tests;
- replay determinism checks;
- certification compilers and signed proof bundles;
- OpenTelemetry-derived runtime witnesses where available;
- application-specific proof packs and SLO/runbook evidence.

This layer is deliberately distinct from static graph governance. Tests prove
behavior. ADG proves governability. Runtime witnesses prove that important paths
were actually exercised.

---

## Reviewer Inspection Path

Use this path for a fast senior-review pass:

1. Read `README.md` for the product thesis and differentiators.
2. Read `docs/EXECUTIVE_OVERVIEW.md` for the leadership narrative.
3. Read `docs/RUNTIME_CONTROL_PLANE.md` for the runtime model.
4. Read `docs/architecture/REVIEWER_GUIDE.md` for proof commands.
5. Run:

```bash
python scripts/governance/verify_codex_primary.py
python scripts/governance/verify_codex_enforcement_home.py --json
python ops_scripts/ci/run_architecture_proof.py
```

6. Inspect the latest ADG SQLite snapshot when structural proof is needed.

---

## What This Is Not

This governance model is not a substitute for tests.

Tests are still required for:

- user-visible behavior;
- unit-level correctness;
- end-to-end flows;
- regression proof;
- runtime edge cases;
- replay determinism;
- contract behavior.

The clean split is:

```text
Tests prove behavior.
ADG CI proves governability.
Codex governs the AI-time work process.
```

---

## Reviewer Takeaway

The strongest signal is not the size of the graph or the number of gates. It is
the engineering posture:

1. **Tests prove behavior; the graph proves governability.**
2. **Known debt is ratcheted, not normalized.**
3. **Runtime governance is executable, not just documented.**
4. **AI-assisted development is guided, constrained, audited, and published
   through Codex-primary evidence.**

For a senior engineering reviewer, the repo is asking a higher-order question:

```text
Can this system keep changing safely while AI-assisted development is turned on?
```

That is the governance claim this repository is built to prove.
