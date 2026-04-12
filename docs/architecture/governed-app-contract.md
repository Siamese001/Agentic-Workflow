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

### 3.1 Candidate Apps (transient — use `ExceptionAppEntry`)

An app that **cannot yet** adopt GovernedAppRunner but is targeted for migration
must declare an explicit `ExceptionAppEntry` in `APP_REGISTRY`.
Silent bypass (absent from registry entirely) is a conformance violation.

| Field | Type | Valid values |
|---|---|---|
| `app_name` | `str` | importable package name |
| `status` | `GovernanceStatus` | `CANDIDATE` |
| `exception_category` | `str` | `"pending_migration"` |
| `exception_reason` | `str` (≥20 chars) | one-sentence specific justification |
| `owner` | `str` | responsible team or person |
| `target_phase` | `str` | `"Phase N"` (concrete delivery phase) |

### 3.2 Permanent Exceptions — Formal Exception Framework

All `status=EXCEPTION` apps **MUST** use `FormalExceptionEntry`. Plain `ExceptionAppEntry`
for a permanent exception is a conformance violation (EXCF01 fails).

The formal exception framework enforces that exceptions are:
- **Explicit** — canonical `ExceptionReasonCode` enum, not a free-text string
- **Bounded** — declared blocked layers and safe adoption surfaces
- **Compensated** — ≥2 compensating controls verified by the gate
- **Auditable** — machine-readable `ExceptionRecord` via `get_exception_record()`
- **Reviewable** — declared `review_cadence` (annual/semi-annual/quarterly)

#### 3.2.1 `FormalExceptionEntry` Schema

| Field | Type | Requirement |
|---|---|---|
| `app_name` | `str` | importable package name |
| `status` | `GovernanceStatus` | always `EXCEPTION` |
| `exception_reason_code` | `ExceptionReasonCode` | `CIRCULAR_DEPENDENCY` \| `REGULATORY_DOMAIN` |
| `exception_reason` | `str` | full human-readable justification |
| `blocked_layers` | `tuple[str, ...]` | governed layers that cannot be adopted (≥1) |
| `safe_layers` | `tuple[str, ...]` | substrate surfaces safely adopted (≥1) |
| `compensating_controls` | `tuple[str, ...]` | CC-XXX-NN descriptions (≥2) |
| `review_cadence` | `str` | `"annual"` \| `"semi-annual"` \| `"quarterly"` |
| `owner` | `str` | responsible team or person |
| `target_phase` | `str` | `"N/A — permanent exception"` |
| `partial_adoption_module` | `str` | dotted module path of the safe-adoption handler |
| `partial_adoption_class` | `str` | class name; must implement `check_compensating_controls()` |
| `proof_prefix` | `str` | 2–5 char prefix for proof-harness check IDs |

#### 3.2.2 `ExceptionReasonCode` Values

| Code | Meaning |
|---|---|
| `CIRCULAR_DEPENDENCY` | Adopting GovernedAppRunner creates a semantic circular dependency |
| `REGULATORY_DOMAIN` | App makes legally-binding or safety-critical decisions incompatible with the generic substrate |
| `PENDING_MIGRATION` | Reserved for future use in structured migration tracking |

#### 3.2.3 Partial Adoption Module Contract

Each permanent exception must provide a handler class (at `partial_adoption_module`) that:
- Implements `get_exception_record()` returning a machine-readable record
- Implements `check_compensating_controls()` returning `list[tuple[str, bool, str]]`
- Does NOT subclass `GovernedAppRunner`
- Adopts only the safe substrate surfaces declared in `safe_layers`

File location convention: `{app_name}/integrations/governed_{short}_exception.py`

#### 3.2.4 Compensating Controls (CC-XXX-NN)

Each compensating control must have a unique identifier (`CC-APPSHORT-NN`).
Controls are verified at gate time by `check_compensating_controls()`. All controls must pass.

#### 3.2.5 Permanent vs. Bounded

- `status=EXCEPTION` + `FormalExceptionEntry` → permanent; gate runs EXCF01–EXCF08
- `status=CANDIDATE` + `ExceptionAppEntry` → bounded; gate runs CONF04–CONF07

---

## 4. Full `apps_*` Classification Table

| App | Status | Type | Proof | Owner |
|---|---|---|---|---|
| `apps_research` | **GOVERNED** | GovernedResearchRun | APP01–APP15 | research team |
| `apps_exec` | **GOVERNED** | GovernedExecRun | EXE01–EXE12 | exec team |
| `apps_rfp` | **GOVERNED** | GovernedRfpRun | RFP01–RFP12 | rfp team |
| `apps_rg` | **GOVERNED** | GovernedRgRun | RG01–RG12 | rg team |
| `apps_lic` | **GOVERNED** | GovernedLicRun | LIC01–LIC12 | lic team |
| `apps_eval` | **FORMAL EXCEPTION** | GovernedEvalException | EVAL01–EVAL10 + EXCF01–EXCF08 | eval-platform team |
| `apps_underwriting_ai` | **FORMAL EXCEPTION** | GovernedUwException | UW01–UW10 + EXCF01–EXCF08 | underwriting-ai team |

### 4.1 Exception Gap Maps

**apps_eval** (`CIRCULAR_DEPENDENCY`)

| Layer | Status | Domain equivalent |
|---|---|---|
| L0 routing | BLOCKED | apps_eval has no generic routing target |
| L1 query decomp | BLOCKED | evaluation runs are structured, not free-text |
| C0 evidence retrieval | BLOCKED | apps_eval retrieves evidence OF other apps, not for itself |
| L2 authorize_and_execute | BLOCKED | would need to authorize the authorizer |
| L5 exit gate | BLOCKED | calls evaluate_and_emit → circular |
| L6 shadow eval | BLOCKED | IS the shadow eval system |
| BUS T telemetry | **SAFE** | `GovernedEvalException.emit_run_telemetry()` (no evaluate_and_emit) |
| conformance metadata | **SAFE** | `GovernedEvalException.get_exception_record()` |

**apps_underwriting_ai** (`REGULATORY_DOMAIN`)

| Layer | Status | Domain equivalent |
|---|---|---|
| L0 generic routing | BLOCKED | product_type + decision_type routing via CoreAdapter |
| L1 query decomp | BLOCKED | structured UnderwritingRequest (no free-text query) |
| C0 evidence retrieval | BLOCKED | `retrieval_adapter.py` with typed DocumentSet |
| L2 authorize_and_execute | BLOCKED | `policy_adapter.py` + domain validators |
| L5 safety exit gate | BLOCKED | `human_review_reason` + `review_required` (domain gate) |
| BUS T telemetry | **SAFE** | `GovernedUwException.emit_decision_telemetry()` |
| conformance metadata | **SAFE** | `GovernedUwException.get_exception_record()` |

---

## 5. Conformance Gate

Run at any time:

```bash
python ops_scripts/ci/check_governed_app_conformance.py
```

Integrated into the proof harness:

```bash
python tools/eval/retrieval_benchmark.py --exception-framework-proof
python tools/eval/retrieval_benchmark.py --conformance-gate-proof
```

The gate checks:
1. **CONF01–CONF03**: All governed apps have an importable `GovernedAppRunner` subclass with versioned capability token
2. **CONF04–CONF07**: All candidate apps have valid `ExceptionAppEntry` fields
3. **CONF08**: No `apps_*` package is absent from the registry (silent bypass check)
4. **EXCF01**: All `status=EXCEPTION` apps use `FormalExceptionEntry` (no ad hoc exceptions)
5. **EXCF02–EXCF06**: Formal exception schema fields are valid and non-empty
6. **EXCF07**: Partial adoption module is importable
7. **EXCF08**: All compensating controls pass at gate time

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
