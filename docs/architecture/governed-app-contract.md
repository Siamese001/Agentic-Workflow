# Governed-App Contract

> **Status:** Active  
> **Enforced by:** `ops_scripts/ci/check_governed_app_conformance.py`  
> **Registry:** `apps_shared/integrations/app_registry.py`  
> **Shared base:** `apps_shared/integrations/governed_app_runner.py`

---

## 1. Purpose

This contract defines the minimum requirements for an `apps_*` package to be considered
**governed** — that is, fully integrated with the repo's shared agentic substrate
(L1 → L0 → C0 → L2 → L5 + L6).

Apps that cannot yet adopt the pattern must declare an **explicit bounded exception** rather
than silently bypassing the governed substrate.

---

## 2. Governed-App Onboarding Contract

An app is considered **governed** when it satisfies all five requirements:

### 2.1 App Identity

The app must supply:

| Field | Type | Example |
|---|---|---|
| `app_name` | `str` | `"apps_research"` |
| `capability_token` | `str` (stable, versioned) | `"apps_research.governed_e2e.v1"` |
| `proof_prefix` | `str` (2–5 chars) | `"APP"` |

### 2.2 Capability Token

A stable dotted-string token unique to this app's governed capability.  
Format: `{app_name}.governed_e2e.{version}`  
Used by `authorize_and_execute()` as the policy anchor.

### 2.3 Routing Target and Keywords

The app must register one L0 routing target and at least three intent keywords:

| Field | Type | Example |
|---|---|---|
| `routing_target` | `str` | `"research_assembly"` |
| `ROUTING_KEYWORDS` | `list[str]` (≥3 entries) | `["research", "analysis", "study"]` |

### 2.4 GovernedAppRunner Subclass

The app must provide a class that:
- Subclasses `apps_shared.integrations.governed_app_runner.GovernedAppRunner`
- Sets `APP_NAME`, `CAPABILITY_TOKEN`, `ROUTING_TARGET`, `ROUTING_KEYWORDS` as class attributes
- Implements `run_governed_e2e(request, *, inject_chunks=None)` returning a frozen dataclass
- Maps the generic `GovernedAppRunRecord` into an app-specific frozen record type

File location convention: `{app_name}/integrations/governed_{short_name}_run.py`

### 2.5 Result Record

The app-specific result record must be a `frozen=True` dataclass and must expose at minimum:

| Field | Purpose |
|---|---|
| `run_id` | Correlation key |
| `error` | `""` on success; exception message on failure |
| `disposition` | Gate disposition string |
| `grounded` | Bool — grounded_replayable from exit gate |
| `l2_executed` | Bool — authorize_and_execute() ran |
| `l6_ingested` | Bool — L6 eval packet queued |

### 2.6 Registry Entry

The app must be listed in `APP_REGISTRY` in `apps_shared/integrations/app_registry.py`
as a `GovernedAppEntry` with all required fields populated.

---

## 3. Exception / Candidate Schema

An app that **cannot yet** adopt GovernedAppRunner must declare an explicit `ExceptionAppEntry`
in `APP_REGISTRY`. Silent bypass (absent from registry entirely) is a conformance violation.

### 3.1 Required Fields

| Field | Type | Valid values |
|---|---|---|
| `app_name` | `str` | importable package name |
| `status` | `GovernanceStatus` | `CANDIDATE` or `EXCEPTION` |
| `exception_category` | `str` | `"pending_migration"` \| `"circular_dependency"` \| `"regulatory_domain"` |
| `exception_reason` | `str` (≥20 chars) | one-sentence specific justification |
| `owner` | `str` | responsible team or person |
| `target_phase` | `str` | `"Phase N"` or `"N/A — permanent exception"` |

### 3.2 Categories

| Category | Meaning |
|---|---|
| `pending_migration` | Structurally compatible; migration not yet done; bounded by `target_phase` |
| `circular_dependency` | Adopting GovernedAppRunner would create a semantic circular dependency |
| `regulatory_domain` | App makes legally-binding or safety-critical decisions incompatible with the generic substrate |

### 3.3 Permanent vs. Bounded

- `status=EXCEPTION` → permanent; `target_phase` must be `"N/A — permanent exception"`
- `status=CANDIDATE` → bounded; `target_phase` must name a delivery phase (e.g. `"Phase 3"`)

---

## 4. Full `apps_*` Classification Table

| App | Status | Category | Reason | Target |
|---|---|---|---|---|
| `apps_research` | **GOVERNED** | — | GovernedResearchRun; proof APP01–APP15 pass | done |
| `apps_exec` | **GOVERNED** | — | GovernedExecRun; proof EXE01–EXE12 pass | done |
| `apps_rfp` | **GOVERNED** | — | GovernedRfpRun; proof RFP01–RFP12 pass | done |
| `apps_rg` | CANDIDATE | pending_migration | trace_id present; 45+ engines need query mapping | Phase 4 |
| `apps_lic` | CANDIDATE | pending_migration | trace_id present; multi-hop engine needs care | Phase 4 |
| `apps_eval` | EXCEPTION | circular_dependency | IS the evaluation framework; would evaluate itself | permanent |
| `apps_underwriting_ai` | EXCEPTION | regulatory_domain | Legally-binding credit decisions; own governance protocol | permanent |

---

## 5. Conformance Gate

Run at any time:

```bash
python ops_scripts/ci/check_governed_app_conformance.py
```

Integrated into the proof harness:

```bash
python tools/eval/retrieval_benchmark.py --conformance-gate-proof
```

The gate checks:
1. All governed apps have an importable `GovernedAppRunner` subclass
2. All exception/candidate apps have a valid `ExceptionAppEntry` with all required fields
3. No `apps_*` package is absent from the registry (silent bypass check)
4. Both migrated apps pass their E2E checks

Exit 0 = PASS. Exit 1 = FAIL with table.

---

## 6. Adding a New App

1. Create `{app_name}/integrations/governed_{short}_run.py` subclassing `GovernedAppRunner`
2. Add a `GovernedAppEntry` to `APP_REGISTRY` in `apps_shared/integrations/app_registry.py`
3. Update this contract's classification table (section 4)
4. Run `python ops_scripts/ci/check_governed_app_conformance.py` — must exit 0
5. Add proof checks to `tools/eval/retrieval_benchmark.py` with the app's `proof_prefix`

If the app cannot adopt the runner yet, add an `ExceptionAppEntry` with `status=CANDIDATE`
and a concrete `target_phase`.
