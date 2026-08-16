# apps_rg standalone simplification

Status: BLOCKED in W1D; source refreeze SR0 is separately authorized

Plan ID: apps-rg-standalone-simplification-7d9190

## Authority amendment (2026-07-19)

The user superseded the prior ADG preflight blocker. The standalone migration
must neither repair nor consume ADG. The frozen source can retain historical ADG
governance language, but that language is not inherited by the target and does
not authorize a migration dependency.

```text
ADG_POLICY: DEPRECATED_AND_FORBIDDEN
ADG_RECOVERY_AUTHORIZED: false
ADG_TARGET_DEPENDENCY: false
ADG_MIGRATION_PREREQUISITE: false
W0R_STATUS: CANCELLED
PLAN_STATUS: BLOCKED
CURRENT_WAVE: W1D
BLOCKED_WAVE: W1
BLOCKER: W1D_SOURCE_REFREEZE_REQUIRED
SOURCE_SHA: fc7039821148151e08459f8473cc8428df39bc8b
SOURCE_TREE: 8e3fa68878aef4224f781335850a9eab7ff2c6c9
TARGET_STATE: ABSENT
SOURCE_REFREEZE_REQUIRED: true
SOURCE_REMEDIATION_AUTHORIZED: SR0_ONLY
GRAPH_COMPLETION_REQUIRED_BEFORE_MIGRATION: true
GRAPH_SKILL_EMBEDDINGS_MANDATORY: true
EMBEDDING_UNIT: ATOMIC_SKILL_ASSERTION
NO_EMBEDDING_PROMOTION_IS_SUCCESS: false
RUNTIME_TRACE_CONTINUATION_AUTHORIZED: false
TARGET_CREATION_AUTHORIZED: false
W1_FALLBACK_AUTHORITY: deterministic_non_adg_source_closure_v1
```

Wave 1 evidence will be written only under
`artifacts/apps_rg_standalone/w1/` in an isolated source worktree. The target
`C:\\Git\\apps_rg` remains absent until the existing Wave 2 initialization
precondition is satisfied.

## Objective

Produce a materially simpler, independently installable `apps_rg` repository at
`C:\Git\apps_rg` while preserving the frozen Agentic-Workflow `apps_rg`
behavior, authority boundaries, provider behavior, replayability, evidence
receipts, fail-closed controls, and auditability.

This is an extraction and consolidation program. It is not a redesign of the
agentic architecture and must not create a generic agent platform.

## Baseline

Source repository: `C:\Git\Agentic-Workflow-FRESH`

Authoritative branch: `origin/main`

Frozen source commit:

```text
fc7039821148151e08459f8473cc8428df39bc8b
```

Pre-plan checks performed on 2026-07-19:

```text
HEAD        fc7039821148151e08459f8473cc8428df39bc8b
origin/main fc7039821148151e08459f8473cc8428df39bc8b
FETCH_HEAD  fc7039821148151e08459f8473cc8428df39bc8b
```

Fetch command:

```text
git fetch origin main
```

Dirty worktree status is accepted as pre-existing Wave 0 work, per user
clarification. This plan does not modify, validate, stage, publish, or combine
those Wave 0 changes with standalone simplification implementation.

Known pre-existing Wave 0 dirty paths at plan creation:

```text
 D .codex/automations/adg-p0-blocker-burndown/automation.toml
 D .codex/automations/adg-p1-ratchet-burndown/automation.toml
 M scripts/governance/verify_codex_enforcement_home.py
 M scripts/governance/verify_codex_primary.py
 D tests/unit/codex/test_adg_p0_burndown_automation_contract.py
 M tests/unit/scripts/governance/test_verify_codex_enforcement_home.py
 M tests/unit/scripts/governance/test_verify_codex_primary.py
 M tests/unit/tools_adg/test_prepare_p0_burndown.py
?? plans/apps-rg-simple-end-to-end-spine-e6a41d.md
?? plans/codex-adg-enforcement-decoupling-4d7a1c.md
```

ADG health at plan creation:

```text
status=critical
mode=unavailable
sqlite=unavailable
redis=healthy
adg_snapshot_id=unavailable:canonical-4.0.0
reason=certified snapshot pointer is missing; active snapshot is not certified;
       certified snapshot digest was not verified; required materialization
       status=UNKNOWN; projection status response malformed
```

The preceding ADG status is historical source-environment evidence only. It is
not migration authority, a target dependency, or a Wave 1 precondition.

## Constraints

- No implementation edits before this plan is approved.
- Do not push, merge, tag, or rewrite history without explicit authorization.
- Do not reimplement C0.3, change graph schema semantics, weaken read purity,
  auto-repair graph data from a read path, or normalize NOT_READY or UNKNOWN to
  PASS.
- Do not mix graph-data remediation, Wave 0 lock fixes, provider upgrades,
  embedding introduction, or DAG enablement into simplification commits.
- Do not copy all of `agentic_core` or `apps_shared`.
- The target must not contain `tools/adg`, `agentic_core/adg`, `artifacts/adg`,
  `adg_sqlite`, an ADG MCP configuration, snapshots, manifests, repair
  handoffs, certification receipts, CI workflows, ratchets, package/build/test
  dependencies, runtime imports, source-path fallbacks, or ADG-derived
  authority claims. Target independence tests scan case-insensitively for the
  prohibited dependency stems. Only a historical exclusion note and test
  deny-lists may mention them textually.
- Do not introduce Agentic-Workflow as a runtime, package, Git, submodule,
  symlink, source-tree path, or dynamic import fallback dependency.
- Graph grounding remains mandatory. Graph-skill embeddings remain conditional
  and must not become a standalone v1 prerequisite unless the frozen
  qualification returns `QUALIFIED_GO`.
- Serial execution remains the production default until standalone serial
  parity and later DAG certification pass.
- Exact graph, candidate facts, source lineage, ACL, freshness, allocation,
  gates, Exit/X3, UWG, L6, L7, and provider evidence remain authority
  boundaries.

## Assumptions

- The dirty source paths listed above are Wave 0 work owned outside this
  standalone simplification plan.
- The frozen commit is the behavior authority for migration even while the local
  checkout contains explained Wave 0 dirty files.
- `C:\Git\apps_rg` is the target repository location. If it already exists, its
  state must be inspected before Wave 2 and must not be overwritten silently.
- The target excludes ADG code, assets, package dependencies, MCP wiring,
  snapshots, manifests, CI, tests, runtime imports, and source-path fallbacks.
- Product-domain graph grounding remains mandatory but is not ADG. Use names
  such as `GraphSnapshot`, `SkillEvidenceGraph`, `GraphReadAdapter`, and
  `GraphSelectionReceipt`.

## Tier

T3: multi-repository extraction, architecture consolidation, dependency
closure, provider boundary migration, replay parity, packaging, and
certification.

## Touched surfaces

Planned source reads:

- `apps_rg/**`
- `apps_research/**`
- `apps_eval/**`
- `agentic_core/**` only for reachable behavior inventory and ports
- `apps_shared/**` only for reachable behavior inventory and ports
- `config/**`
- `data/**`
- `tests/**`
- `scripts/**`
- `pyproject.toml`
- packaging/configuration files required by frozen production entry points

Planned target writes after Wave 1 acceptance:

- `C:\Git\apps_rg\pyproject.toml`
- `C:\Git\apps_rg\README.md`
- `C:\Git\apps_rg\AGENTS.md`
- `C:\Git\apps_rg\src\apps_rg\**`
- `C:\Git\apps_rg\src\apps_research\**`
- `C:\Git\apps_rg\src\apps_eval\**`
- `C:\Git\apps_rg\config\**`
- `C:\Git\apps_rg\data\**`
- `C:\Git\apps_rg\tests\**`
- `C:\Git\apps_rg\artifacts\**`

Planned Wave 1 source-worktree evidence writes:

- `artifacts/apps_rg_standalone/w1/**`
- `tools/apps_rg_standalone/**` only for deterministic, non-ADG closure
  generation and validation
- `tests/unit/tools/apps_rg_standalone/**` for the closure tool's import,
  dynamic-import, and asset-resolution behavior

## Plan

### 1. Evidence and preflight

1. Reconfirm source branch and full SHA:
   - `git status --short`
   - `git fetch origin main`
   - `git rev-parse HEAD`
   - `git rev-parse origin/main`
   - `git rev-parse FETCH_HEAD`
   - `git rev-parse HEAD^{tree}`
2. Record Wave 0 dirty paths as excluded pre-existing work. Stop if new
   unexplained dirty paths appear.
3. Inspect `C:\Git\apps_rg` if present:
   - repository existence;
   - Git status;
   - remotes;
   - HEAD commit;
   - whether files may be reused or must be initialized.
4. Record the ADG deprecation boundary as a target deny-list and confirm that
   no ADG status, pointer, digest, graph artifact, MCP route, or recovery step
   is used as migration authority.
5. Run source readiness checks required for long Codex-primary work:
   - `python scripts/governance/codex_readiness.py --json`
   - `python scripts/governance/verify_codex_enforcement_home.py --json`
   - use stricter flags only when Wave 0 dirty-state handling is resolved.

Stop if the frozen SHA changes, dirty source paths are not explained, the
target repository contains unexplained work, a non-ADG closure arm is
incomplete, or any reachable object remains UNKNOWN.

### 2. Wave 1: freeze, reachability, and differential baseline

1. Emit `source_freeze.json` with full commit SHA, tree SHA, and digests for
   reachable configuration, schemas, providers, prompts, rubrics, fixtures,
   graph data, candidate facts, and canonical artifacts.
2. Discover production entry points:
   - CLIs and module entry points;
   - whole-run, section-only, patch-run, replay, and live paths;
   - Apps Research handoff;
   - cache read and promotion paths;
   - Apps Eval, L5, Exit/X3, UWG, L6, and L7 paths.
3. Build the static Python import closure with the standard-library `ast`
   module. Resolve absolute and relative imports, package facades, `__all__`,
   PEP-562 lazy imports, and module-level registries. Classify every unresolved
   import explicitly; no reachable import may remain UNKNOWN.
4. Independently inventory dynamic imports and module selection through
   `importlib`, `__import__`, entry points, provider/section/adapter registries,
   environment-selected modules, module-name strings, and subprocess module
   invocations. Classify each finding as concrete reachable, optional,
   test-only, or justified deletion.
5. Capture deterministic stub/replay traces for all 11 lanes, serial whole run,
   Apps Research, product-graph grounding, R1A, disabled R1B, patch run, Apps
   Eval, L5, Exit, UWG, L7, and L6. Record local modules loaded at runtime and
   reconcile them against the static closure.
6. Build the non-Python asset closure for all reachable prompts, configuration,
   schemas, provider and judge profiles, gate profiles, product graph data,
   candidate facts, templates, rendering and DOCX assets, fixtures, and
   validation or migration scripts. Resolve file access through code paths,
   resources, configuration, environment variables, loaders, and subprocesses.
7. Cross-check the closure using focused non-ADG tests for provider routing,
   section registry completeness, write sovereignty, product graph read purity,
   root X3 uniqueness, L6, package boundaries, app-to-core boundaries, and
   artifact production. Tests corroborate but do not replace closure evidence.
8. Reconcile every discovered object with the 11-lane registry, provider and
   Apps Research contracts, product graph schemas, cache and patch contracts,
   Apps Eval, L5, Exit, UWG, L7, L6, and product-output contracts. Classify
   every object exactly once:
   - `KEEP`
   - `MOVE`
   - `MERGE`
   - `REWRITE_BEHIND_PORT`
   - `EXTERNALIZE_AS_DATA`
   - `DELETE_AFTER_PARITY`
9. Produce the required non-ADG migration manifests:
   - `source_freeze.json`
   - `static_import_closure.json`
   - `dynamic_import_inventory.json`
   - `runtime_module_trace.json`
   - `non_python_asset_closure.json`
   - `behavior_contract.json`
   - `artifact_contract.json`
   - `provider_pin_manifest.json`
   - `section_registry_reconciliation.json`
   - `legacy_surface_inventory.json`
   - `product_graph_baseline.json`
   - `migration_risk_register.json`
10. Identify duplicate section lifecycle code, duplicate X3/exit logic,
   duplicate contracts, duplicate provider selection, duplicate section
   identifiers, stale docs, review-only manifests, unreachable production-like
   modules, and hidden source-path assumptions.
11. Capture deterministic golden runs for all required lane, full-run, handoff,
   graph, cache, patch, judge, Exit/X3, UWG, L7, and L6 cases.
12. Run the source repository's current required tests and record actual
   commands, exit codes, and artifact paths.
13. Run or add the narrow W0 stale-lock recovery guard. If it fails, stop
    extraction and isolate the W0 lock fix; do not combine with simplification.

Acceptance marker: `W1_FROZEN_REACHABLE_CLOSURE_PASS` only when all non-ADG
closure arms reconcile, every reachable object is classified, no UNKNOWN entry
remains, the product graph remains authoritative and read-pure, and the target
still has no ADG dependency.

#### Wave 1 checkpoint (2026-07-19)

The isolated source worktree emitted the first deterministic closure bundle at
`artifacts/apps_rg_standalone/w1/static-import-reconciliation-0008/` from
source commit `fc7039821148151e08459f8473cc8428df39bc8b` and tree
`8e3fa68878aef4224f781335850a9eab7ff2c6c9`. `source_freeze.json` passed.
The static scanner resolved 1,074 local modules without parse errors or a
module-limit breach, while preserving seven runtime unresolved local references
and eleven separately classified optional or type-only references for manual
disposition. The dynamic inventory contains 16 direct records and 189 literal
module references extracted from named registries; 15 records require
reconciliation. The non-Python asset inventory contains 522 dynamic file-access
records requiring runtime or manual reconciliation.

This is a `W1_INCOMPLETE` evidence checkpoint, not an acceptance marker. The
runtime 11-lane trace, non-Python asset closure, behavior and artifact
contracts, provider pins, section-registry reconciliation, product-graph
baseline, and risk register remain required. The legacy-surface inventory
passes with the frozen bootstrap in `apps_research.__main__` explicitly marked
`DO_NOT_INHERIT`; it creates no target dependency and does not authorize any
ADG recovery or use.

#### Wave 1 continuation authorization (2026-07-19)

The checkpoint tooling is accepted as an intermediate source-analysis result:

```text
W1_NON_ADG_CLOSURE_TOOLING_PASS
W1_FROZEN_REACHABLE_CLOSURE_STATUS=INCOMPLETE
```

These markers do not advance Wave 1, authorize target creation, or imply
runtime, asset, provider, section, or product-graph closure. The source branch
`codex-apps-rg-standalone` remains a migration-analysis branch only.

W1.1 has an initial source-classification baseline at
`artifacts/apps_rg_standalone/w1/static-import-reconciliation-0009/`. Its
seven-import classification was superseded by the independent reachability and
migration-disposition reconciliation at
`artifacts/apps_rg_standalone/w1/static-import-reconciliation-0019/`.
The current record includes defect ID, source site, missing target, exact
trigger, static and runtime reachability, standalone-scope decision, frozen
behavior impact, test coverage, target owner, and parity/negative test. It has
`static_unresolved_import_count = 0`, no unknown reachability or disposition,
and two conditionally reachable, unmitigated source defects. W1.1 therefore
remains blocked rather than complete; an import-only trace is not evidence that
any lazy source defect is unreachable.

W1.2 static reconciliation is recorded at
`artifacts/apps_rg_standalone/w1/static-import-reconciliation-0019/`.
All 16 dynamic sites have an explicit migration disposition (eight
`REWRITE_BEHIND_PORT`, six `LEGACY_DO_NOT_INHERIT`, one `OPTIONAL_EXPLICIT`,
and one `TEST_ONLY`), with no unknown or pending dynamic policy. The six source
registry owners and 21 references have no unknown entry. The source's
eight-module `LANE_DISPATCH_MODULES` remains `DUPLICATE_TO_MERGE`; the single
intended 11-lane target registry is the declarative
`apps_rg.runtime.section_execution_plan.SECTION_EXECUTION_POLICIES` mapping.
This is a static W1.2 result, not a Wave 1 completion marker or generic plugin
authorization.

W1.3 has an intermediate asset-normalization inventory at
`artifacts/apps_rg_standalone/w1/static-import-reconciliation-0019/`. It
preserves the original 522 frozen access call sites by digest and source
artifact, separately records 840 expanded read/write call sites, and groups
them into 639 normalized expressions. No canonical migration asset is inferred
from the dynamic expressions (`canonical_migration_asset_count = 0`), and no
ADG path is promoted into target scope (`adg_path_count = 0`). This remains an
incomplete asset arm because all 639 expressions require runtime binding.

W1.4 has a first bounded import-smoke trace at
`artifacts/apps_rg_standalone/w1/runtime-import-smoke-0001/`. The original
minimal child environment caused `OSError [WinError 10106]` while `redis`
imported `asyncio.windows_events`, before a source write, subprocess launch,
network connection, or legacy import. This attempt remains attempted but not
completed; it did not authorize a source behavior change or a Wave 1 marker.

#### Checkpoint 0015 conditional continuation (2026-07-19)

```text
W1_STATIC_IMPORT_ANALYSIS_COMPLETE=true
W1_STATIC_IMPORT_MIGRATION_DISPOSITION_COMPLETE=false
W1_RUNTIME_TRACE_STATUS=BLOCKED
W1_RUNTIME_TRACE_BLOCKER=TRACE_ENVIRONMENT_PREFLIGHT_FAILED
W1_RUNTIME_REQUIRED_SCENARIOS=17
W1_RUNTIME_ATTEMPTED_SCENARIOS=1
W1_RUNTIME_COMPLETED_SCENARIOS=0
W1_RUNTIME_PASSED_SCENARIOS=0
W1_RUNTIME_BLOCKED_SCENARIOS=1
W1_RUNTIME_PENDING_SCENARIOS=16
TARGET_REPOSITORY_STATE=ABSENT
W1_CHECKPOINT_0015_CONDITIONAL_CONTINUE
```

The failed import-smoke attempt remains an attempted but not completed runtime
scenario. Wave 1 continues only through migration-analysis tooling, with the
trace environment preflight and independent reachability/disposition evidence
required before any target work.

#### Checkpoint 0015 environment recovery (2026-07-19)

The hardened harness copies the inherited Windows environment, scrubs only
credential and live-provider selection keys, and preserves the Windows bootstrap
keys required by Python and WinSock. All three child-process probes now import
`socket`, `asyncio`, and `redis` successfully on Python 3.12.10
(`C:\Users\amita\AppData\Local\Programs\Python\Python312\python.exe`),
Windows 11 10.0.26200, AMD64. The original failure is classified as an
environment-sanitization defect, not a host/Python or trace-guard defect.

Focused harness tests passed: `20 passed in 1.52s`. They prove inherited and
sanitized imports, Windows bootstrap preservation, no secret-value evidence,
operation-boundary denial of outbound sockets, subprocesses, and unauthorized
writes, allowed trace-directory writes, and Redis import without a connection.

`runtime-import-smoke-0004/` passed with 392 local modules, 2,521 third-party
modules, 16 captured source dynamic imports, 413 file reads, zero source writes,
zero network connection attempts, and zero subprocess launches. Redis is
recorded only as a source-runtime transitive import:
`apps_rg.__main__ -> agentic_core.L2_execution.utils.write_gateway ->
agentic_core.__init__ -> agentic_core.cache.redis_cache_client -> redis`.
Its target-dependency disposition remains undecided pending an approved product
scenario. The failed historical attempt plus the passing fresh import smoke
produce 2 attempts, 1 completed, 1 passed, 1 blocked, and 16 pending scenarios.

`unresolved_import_reconciliation.json` at
`static-import-reconciliation-0019/` contains seven completed dispositions:
two `BLOCKED_SOURCE_DEFECT` rows (`W1-IMPORT-001` local retrieval bootstrap and
`W1-IMPORT-002` manifest integrity), four `LEGACY_DO_NOT_INHERIT` rows, and one
`OPTIONAL_EXPLICIT` OpenAI-provider row. The two in-scope defects yield
`reachable_unmitigated_source_defect_count = 2` and
`W1_BLOCKED_ON_REACHABLE_SOURCE_DEFECT`; no target repository may be created.
W1.2 reconciles all 16 observed dynamic sites, with no generic plugin target
mechanism. W1.3 preserves the 522 baseline, with 840 expanded calls, 659
normalized expressions, and zero canonical migration assets. No production source file changed, and
`C:\Git\apps_rg` remains absent.

```text
W1_STATIC_IMPORT_ANALYSIS_COMPLETE=true
W1_STATIC_IMPORT_MIGRATION_DISPOSITION_COMPLETE=true
W1_RUNTIME_TRACE_STATUS=PARTIALLY_COMPLETE
W1_RUNTIME_TRACE_BLOCKER=NONE
W1_RUNTIME_REQUIRED_SCENARIOS=17
W1_RUNTIME_ATTEMPTED_SCENARIOS=2
W1_RUNTIME_COMPLETED_SCENARIOS=1
W1_RUNTIME_PASSED_SCENARIOS=1
W1_RUNTIME_BLOCKED_SCENARIOS=1
W1_RUNTIME_PENDING_SCENARIOS=16
W1_TRACE_HARNESS_PREFLIGHT_PASS
W1_RUNTIME_IMPORT_SMOKE_PASS
W1_BLOCKED_ON_REACHABLE_SOURCE_DEFECT
TARGET_REPOSITORY_STATE=ABSENT
W1_CHECKPOINT_0015_CONDITIONAL_CONTINUE
```

#### W1D reachable source-defect adjudication (2026-07-19)

W1D adjudicated exactly the two reachable, in-scope frozen-source defects in
`source-defect-adjudication-w1d-0020/`. `W1-IMPORT-001` is the uncharacterized
local retrieval cache-miss rebuild path; `W1-IMPORT-002` is the absent active
L4 configuration provider used by the hash-bearing manifest integrity gate.
Both require `SOURCE_REFREEZE_REQUIRED`: the first lacks an independent
retrieval/candidate-fact behavior oracle, while the second would require
inventing deterministic configuration-hash authority. No source remediation,
migration rewrite, trace shim, target creation, or remaining runtime scenario
is authorized.

The packet preserves the frozen source commit/tree, records zero source
production changes, normalizes 2,521 raw third-party modules into 71 package
roots without converting source bootstrap imports into target dependencies, and
records Redis as `UNDECIDED_PENDING_BEHAVIORAL_REACHABILITY`. The corrected
asset reconciliation identifies 213 source-controlled candidates with zero
unknown, missing-digest, or unowned records; it does not treat the prior call
expression statistic as a zero-asset migration scope.

```text
PLAN_STATUS: BLOCKED
CURRENT_WAVE: W1D
BLOCKED_WAVE: W1
BLOCKER: W1_BLOCKED_ON_REACHABLE_SOURCE_DEFECT
TARGET_STATE: ABSENT
SOURCE_REPAIR_AUTHORIZED: false
MIGRATION_REWRITE_AUTHORIZED: false
RUNTIME_TRACE_CONTINUATION_AUTHORIZED: false
W1D_SOURCE_REFREEZE_REQUIRED
```

#### Source-refreeze amendment (2026-07-19)

The W1D decision packet remains immutable historical diagnostic evidence. The
only authorized follow-on is SR0 source-contract repair in the separate
`codex-apps-rg-source-refreeze` worktree and plan
`apps-rg-source-refreeze-c03-assertion-embeddings-c03a5e`. The remaining 16
standalone runtime scenarios remain unauthorized. SR1 through SR6, including
C0.3 graph authority/data remediation and atomic skill-assertion BGE-M3
embeddings, require their stated future checkpoints before migration can
restart. ADG remains deprecated and forbidden for all source and target work.

```text
PLAN_STATUS: BLOCKED
CURRENT_WAVE: W1D
BLOCKED_WAVE: W1
BLOCKER: W1D_SOURCE_REFREEZE_REQUIRED
SOURCE_SHA: fc7039821148151e08459f8473cc8428df39bc8b
SOURCE_TREE: 8e3fa68878aef4224f781335850a9eab7ff2c6c9
TARGET_STATE: ABSENT
SOURCE_REFREEZE_REQUIRED: true
SOURCE_REMEDIATION_AUTHORIZED: SR0_ONLY
GRAPH_COMPLETION_REQUIRED_BEFORE_MIGRATION: true
GRAPH_SKILL_EMBEDDINGS_MANDATORY: true
EMBEDDING_UNIT: ATOMIC_SKILL_ASSERTION
NO_EMBEDDING_PROMOTION_IS_SUCCESS: false
ADG_POLICY: DEPRECATED_AND_FORBIDDEN
RUNTIME_TRACE_CONTINUATION_AUTHORIZED: false
TARGET_CREATION_AUTHORIZED: false
```

### 3. Wave 2: standalone skeleton and contract collapse

Precondition: `W1_FROZEN_REACHABLE_CLOSURE_PASS`.

1. Initialize or normalize `C:\Git\apps_rg` as an independent Git repository.
2. Create reproducible packaging and dependency policy.
3. Copy canonical data/config/schema inputs by verified digest only.
4. Define the minimum stable contract set:
   - `RunRequest`
   - `ResearchHandoff`
   - `ResearchValidationReceipt`
   - `GraphSnapshotRef`
   - `AllocationPlan`
   - `SectionWorkOrder`
   - `SectionResult`
   - `ClaimBinding`
   - `GateReceipt`
   - `JudgeAttemptReceipt`
   - `JudgePanelReceipt`
   - `AppsEvalReceipt`
   - `L5Certification`
   - `X3Disposition`
   - `CommitRequest`
   - `UwgCommitReceipt`
   - `PromotionReceipt`
   - `TraceReconciliation`
   - `L7AuditReceipt`
   - `L6ShadowReceipt`
   - `RunReceipt`
5. Build one canonical 11-lane registry:
   - `competencies`
   - `unify_bullets`
   - `ibm_bullets`
   - `insurtech_bullets`
   - `ey_bullets`
   - `unify_narrative`
   - `ibm_narrative`
   - `insurtech_narrative`
   - `ey_narrative`
   - `executive_summary`
   - `headline`
6. Add static architecture tests proving no old-repo runtime dependency, no
   provider SDK import outside adapters, no graph DB import outside graph
   adapter, no durable-state access outside UWG, no domain-to-runtime
   inversion, and no second section registry.
7. Keep any migration-only differential harness external to production
   packaging and non-importing from source modules.

Acceptance marker: `W2_CONTRACT_COLLAPSE_PASS`.

### 4. Wave 3: providers, research, and graph authority boundaries

Precondition: `W2_CONTRACT_COLLAPSE_PASS`.

1. Derive provider/model pins from frozen reachable configuration.
2. Port reachable provider behavior behind one `ProviderGateway`:
   aliases, endpoints, environment variable names, payloads, schemas,
   streaming, reasoning controls, timeouts, retry/backoff, truncation, JSON
   parsing, locks, availability fallback, independence rules, proof eligibility,
   forbidden fallback, raw artifacts, and spans.
3. Keep deterministic/stub providers for replay.
4. Explicitly reject Qwen/vLLM routes and aliases.
5. Port Apps Research boundary once. It may receive company, role, JD, and
   authorized research config only.
6. Port graph read adapter once. Reads must not create, repair, promote, or
   mutate graph state.
7. Add positive and negative tests for provider parity, research fail-closed
   behavior, graph authority, unauthorized selection, stale source rejection,
   and read purity.

Acceptance markers:

- `PROVIDER_TRANSPORT_PARITY_PASS`
- `APPS_RESEARCH_BOUNDARY_PASS`
- `GRAPH_AUTHORITY_BOUNDARY_PASS`

### 5. Wave 4: SectionRunner, serial E2E, Exit/X3, UWG, L7, and L6

Precondition: Wave 3 markers pass.

1. Implement one bounded `SectionRunner` used by every generated lane.
2. Implement one serial whole-run coordinator.
3. Preserve whole-resume allocation before generation.
4. Enforce lane work orders, allowlists, deterministic gates, judge panel
   receipts, repair policy, claim binding, output schema, and artifact lineage.
5. Preserve Apps Eval and L5 certification behavior.
6. Emit exactly one root X3 disposition; only `X3D_ALLOW_FINISH` is success.
7. Route all durable write/promotion through UWG.
8. Preserve OTel/L7 reconciliation and L6 post-run shadow boundary.

Acceptance markers:

- `SECTION_RUNNER_CONSOLIDATION_PASS`
- `SERIAL_11_OF_11_E2E_PASS`
- `APPS_EVAL_L5_PASS`
- `ROOT_X3_UWG_PASS`
- `OTEL_L7_L6_PASS`

No DAG implementation or certification may begin before all Wave 4 markers
pass.

### 6. Wave 5: CLI, output, and documentation collapse

Precondition: Wave 4 markers pass.

1. Expose one thin CLI:
   - `python -m apps_rg run ...`
   - `python -m apps_rg section ...`
   - `python -m apps_rg patch-run ...`
   - `python -m apps_rg research ...`
   - `python -m apps_rg doctor ...`
2. Keep CLI limited to parsing, normalization, application service calls,
   terminal rendering, and documented exit codes.
3. Use one output publisher and one output manifest.
4. Preserve required product/evidence outputs.
5. Prove forbidden legacy outputs are absent.
6. Replace stale architecture docs only after runtime parity.

Acceptance markers:

- `THIN_CLI_PASS`
- `SINGLE_OUTPUT_AUTHORITY_PASS`
- `LEGACY_OUTPUTS_ABSENT`
- `DOCUMENTATION_PARITY_PASS`

### 7. Wave 6: R1A, R1B, and patch-run consolidation

Precondition: Wave 5 markers pass.

1. Preserve exact-digest R1A cache as default.
2. Keep R1B disabled by default and separate from C0 fact vectors and optional
   graph-skill embeddings.
3. Require mandatory fresh Apps Research before cache admission.
4. Revalidate provenance, freshness, policy, graph digest, allocation, provider,
   prompt, schema, and final authority for cache proposals.
5. Preserve patch-run immutability, dependency expansion, compatibility
   rejection, rerun requirements, new root X3 linkage, and prior-disposition
   immutability.

Acceptance marker: `R1A_R1B_PATCH_RUN_PASS`.

### 8. Wave 7: independence, cutover, and legacy-surface removal

Precondition: Wave 4, Wave 5, and Wave 6 markers pass.

1. Remove migration duplication from the target repository only after parity.
2. Do not delete the original source repository's `apps_rg` implementation.
3. Build wheel and sdist.
4. Install into a clean temporary environment where Agentic-Workflow is not
   installed, source checkout is unavailable, no repo-root `PYTHONPATH` exists,
   and no developer editable installs exist.
5. Run import smoke, CLI help, doctor, unit, contract, deterministic replay,
   serial 11-lane stub E2E, and output presence/absence checks.
6. Scan source, wheel, metadata, lockfiles, and runtime strings for old-repo
   dependencies, Git URLs, submodules, symlinks, dynamic import fallback,
   absolute source paths, and undeclared data reads.
7. Validate package-data completeness and fresh-checkout rebuildability.

Acceptance markers:

- `ZERO_AGENTIC_WORKFLOW_DEPENDENCY`
- `CLEAN_WHEEL_INSTALL_PASS`
- `LEGACY_RUNTIME_SURFACE_REMOVED`
- `PORT_SCOPE_ACCOUNTED`

### 9. Wave 8: conditional graph-embedding decision

Precondition: exact graph path, serial standalone E2E, and source/control
readiness are certified.

1. Run frozen qualification benchmark and negative controls.
2. Compare exact graph retrieval baseline, existing fact-vector behavior, and
   candidate graph-skill assertion embeddings.
3. Emit exactly one decision:
   - `QUALIFIED_GO`
   - `NO_EMBEDDING_PROMOTION`
4. For `QUALIFIED_GO`, embed only eligible evidence-bearing skill assertions
   and use vectors only to propose existing skill IDs.
5. For `NO_EMBEDDING_PROMOTION`, record the decision, retain exact graph
   retrieval, and create no production graph-embedding store.

Mandatory acceptance marker: `GRAPH_EMBEDDING_DECISION_RECORDED`.

Conditional marker: `GRAPH_EMBEDDINGS_QUALIFIED`.

### 10. Wave 9: existing DAG semantics port and certification

Preconditions:

- `SERIAL_11_OF_11_E2E_PASS`
- `ZERO_AGENTIC_WORKFLOW_DEPENDENCY`
- `R1A_R1B_PATCH_RUN_PASS`

1. Port existing bounded DAG behavior to call the same `SectionRunner`.
2. Preserve frozen DAG waves:
   - wave 0: five proof-bearing lanes;
   - wave 1: four narrative lanes;
   - wave 2: `executive_summary`;
   - wave 3: `headline`;
   - terminal: aggregation, gates, judging, Apps Eval, L5, Exit/X3, UWG,
     promotion, reconciliation/L7, current-run closure, and L6.
3. Enforce isolated lane artifacts, immutable work orders, no shared mutable
   generation state, centralized provider concurrency/rate limits,
   deterministic merge order, dependency failure blocking, sibling failure
   isolation, cache-hit receipts, reduced DAG patch construction, bounded
   cancellation, and no hidden retries.
4. Prove deterministic serial/DAG equivalence for work-order identities,
   allocations, prompts, provider routes, gates, judges, claim ledger,
   artifacts, root authority, and disposition.

Acceptance marker: `L3_DAG_11_OF_11_E2E_PASS`.

## Verification matrix

Each wave must produce a machine-readable receipt with:

- wave ID;
- source full SHA;
- target full SHA;
- timestamp;
- input manifest digests;
- changed files;
- deleted files;
- contract changes;
- tests/checks and exit codes;
- produced artifact paths and digests;
- authority-boundary assertions;
- dependency scan result;
- unresolved risks;
- readiness status;
- exact acceptance marker;
- `PASS`, `BLOCKED`, or `FAIL`.

Required suites across the program:

- formatting, lint, type, and static architecture;
- contract/schema units;
- Wave 0 graph regression and read purity;
- stale-lock recovery negative controls;
- provider transport fixtures;
- Apps Research positive and fail-closed cases;
- graph allocation and unauthorized-claim negatives;
- per-lane `SectionRunner` contracts;
- serial 11-lane replay;
- live proof behind explicit gates;
- judge quorum/outage/retry/fallback cases;
- Apps Eval and L5 positives/negatives;
- root X3 uniqueness;
- direct-write/UWG bypass rejection;
- promotion authorization and rejection;
- R1A/R1B compatibility;
- patch-run dependency and immutability;
- required and forbidden outputs;
- OTel/local receipt reconciliation;
- L7 lineage;
- L6 current-run firewall;
- clean-wheel independence;
- DAG dependency/concurrency/isolation/parity after Wave 9.

## Tools needed

- `git`: source/target branch, SHA, tree, dirty-state, worktree, and artifact
  provenance.
- Standard-library AST tooling plus deterministic replay tracing: static import,
  dynamic-import, runtime-module, and asset-closure evidence with explicit
  unresolved-item classification.
- `python scripts/governance/codex_readiness.py --json`: Codex-primary
  readiness.
- `python scripts/governance/verify_codex_enforcement_home.py --json`:
  Codex-only enforcement home validation.
- `python scripts/governance/verify_codex_primary.py`: governance validation
  after any Codex execution-surface changes.
- `pytest`: source and target regression proof.
- `python -m build`, `pip install`, and clean environment tooling: package
  independence proof.
- Hashing scripts or small Python utilities using bounded subprocess timeouts:
  digest manifests and artifact receipts.

## Missing information

- Whether `C:\Git\apps_rg` already exists and whether any target dirty state is
  explained.
- The Wave 1 evidence location is
  `artifacts/apps_rg_standalone/w1/` in the isolated source worktree. The
  target remains absent until Wave 2.
- Exact source test command set for Wave 1, to be derived from frozen repo
  configuration rather than historical counts.

## Stop conditions

- Source baseline SHA differs from
  `fc7039821148151e08459f8473cc8428df39bc8b`.
- New unexplained source dirty paths appear.
- Existing Wave 0 dirty paths need semantic changes before this plan can run.
- Target repository has unexplained work or would be overwritten.
- Any source or target path introduces a prohibited ADG dependency, fallback,
  artifact, or authority claim.
- Static import, dynamic-import, runtime-trace, or non-Python asset closure is
  incomplete or leaves a reachable object UNKNOWN.
- Reachable dependency closure contains `UNKNOWN` entries.
- A source behavior cannot be characterized.
- A provider/model pin cannot be established.
- Graph reads mutate state or graph snapshot identity cannot be verified.
- NOT_READY or UNKNOWN is coerced to PASS.
- Claims lose fact or graph lineage.
- A lane selects outside its allocation.
- Judge or repair code gains authority.
- More than one root X3 is possible.
- Success can occur without `X3D_ALLOW_FINISH`.
- Durable writes can bypass UWG.
- L6 can affect the current run.
- Cache admission can bypass research.
- R1B becomes enabled by default.
- Patch run mutates a prior disposition.
- Target imports or reads the old repository.
- Clean-wheel proof requires the source checkout.
- Forbidden legacy outputs reappear.
- Embeddings add evidence or claim authority.
- DAG changes prompts, allocation, provider policy, gates, judges, or Exit.
- Required regression tests fail.

## Approval

The original approval plus the 2026-07-19 authority amendment authorize the
non-ADG Wave 1 closure tool, its focused tests, source-worktree evidence, and
the required manifests only. Later implementation waves remain gated by their
stated preconditions and acceptance receipts. Push, merge, tag, history
rewrite, provider upgrades, product-graph remediation, embedding promotion,
and source decommissioning require separate explicit authorization.
