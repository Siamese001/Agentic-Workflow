# Evidence Standards

## Required Sections (in order)

1. `# <Phase Title>`
2. `## Scope` — with graph justification
3. `## INSPECTED_FILES`
4. `## FACT_CLASSIFICATION` — three tiers below
5. Command output sections
6. `## DEPENDENCY_GRAPH` — roots, impacted nodes, upstream/downstream sets, edge classes, boundary findings, per-file scope justification
7. `## BRANCH_INVENTORY`
8. `## ROBUSTNESS_MATRIX` — success / edge / failure / recovery / determinism / side-effect per changed surface
9. `## DEFECT_MODEL`

## Conditional Sections

Add when applicable:

| Section | When |
|---|---|
| `## TIMEOUT_RECOVERY` | Any timeout occurred |
| `## CLUSTER_ANALYSIS` | Every repair session |
| `## FAILURE_CAPTURE` | Before any repair edit |
| `## PROOF_ARTIFACT_TRUTHFULNESS` | ADG proof artifact referenced |
| `## POLICY_DRIFT` | Policy regression classified |
| `## CONTRACT_CONFLICT` | Contract conflict identified |
| `## ENVIRONMENT_CONTRACT` | Environment dependency involved |

## Three-Tier Fact Classification

| Tier | Label | Rule |
|---|---|---|
| 1 | `DIRECTLY OBSERVED` | Read from raw artifact / command stdout — no inference |
| 2 | `DERIVED` | Computed from secondary command — source command MUST be named |
| 3 | `UNRESOLVED` | Not yet proven — MUST be listed explicitly, never omitted |

## Artifact Citation Format

Every artifact path in a response MUST use backtick citation: `` `@<absolute_path>` ``.  
Plain text paths = CONSTITUTIONAL VIOLATION.

## Evidence Contract

- One evidence file per phase under `docs/reports/` or `artifacts/`; active plans live under `plans/`
- Commands via `subprocess.run(argv, shell=False, encoding="utf-8", errors="replace")`
- PowerShell invocation FORBIDDEN
- ASCII-only output with ANSI escape sequences stripped
