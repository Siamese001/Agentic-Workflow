# THREAT MODEL — apps_underwriting_ai

> **Threat-model methodology:** STRIDE per asset; data-classification-driven controls.
> **Scope:** apps_underwriting_ai only. Cross-app threats live in repo-root SECURITY.md (TODO).
> **Last reviewed:** 2026-04-29
> **Owner:** see `CODEOWNERS`

## Why This App Needs a Threat Model

apps_underwriting_ai produces **regulated, binding decisions** affecting borrowers. The threat model is not optional — it is a regulatory expectation in any jurisdiction with fair-lending or anti-discrimination rules.

This document is the security-posture companion to `RUNBOOK.md` (operational) and `SLO.md` (performance/cost). All three together form the operational charter.

## Asset Inventory

| Asset | Class | Sensitivity | Where it lives |
|---|---|---|---|
| Borrower PII (SSN, DOB, address) | **PII-Sensitive** | High — regulated retention | Ingested via document store; held in memory during decision; persisted to immutable evidence ledger |
| Borrower contact (name, email) | **PII-Standard** | Medium | Same as above |
| Decision rationale + features | **Decision artifact** | High — auditable, immutable | `evidence_register_engine.py` output → audit ledger |
| Authority-limit policy | **Compliance config** | High — must be tamper-evident | `apps_underwriting_ai/config/`, version-pinned |
| Forbidden-feature list | **Compliance config** | High | `apps_underwriting_ai/config/forbidden_features.yaml` (TODO if not present) |
| Model weights / prompts | **IP + risk** | High — version-pinned, not editable in prod | `agentic_core/L3_orchestration/inference/` |
| Aggregate metrics | Non-PII | Low | Standard observability |

## Trust Boundaries

```
[ External requester ]
       │  (REST/RPC ingress, authenticated)
       ▼
[ apps_underwriting_ai/integrations/* ]   ← Boundary 1: external → app
       │
       ▼
[ Document ingestion + parse ]            ← Boundary 2: parsed payload becomes typed PII
       │
       ▼
[ Feature derivation ]                    ← Boundary 3: PII → derived numeric features
       │
       ▼
[ Forbidden-feature checker + Authority validator + Compliance + Stale-data + Contradiction + Completeness ]
       │
       ▼
[ Decision packet assembly ]              ← Boundary 4: features → immutable artifact
       │
       ▼
[ Evidence register (append-only ledger) ] ← Boundary 5: to audit/compliance
```

## STRIDE Analysis (per boundary)

### Boundary 1: External → App ingress

| Threat (STRIDE) | Description | Control |
|---|---|---|
| **S**poofing | Attacker submits a request claiming to be an authorized requester | mTLS + signed JWT; identity propagated end-to-end (see `docs/contracts/identity_propagation.md`) |
| **T**ampering | Request modified in transit | TLS + integrity hash on request envelope |
| **R**epudiation | Requester later claims they didn't submit a decision request | Append-only request log with cryptographic chain (see `appends_hash_chain` ADG edge) |
| **I**nfo disclosure | Decision request leaks via error message | Structured errors only; never include PII in error strings |
| **D**oS | Resource exhaustion via large doc upload | Per-requester rate limit + max doc size; ingestion engine bounds in `document_ingestion.py` |
| **E**OP | Requester escalates to invoke higher-authority decisions | Authority limit validator runs PER REQUEST, not per session |

### Boundary 2: PII Ingestion

| Threat | Description | Control |
|---|---|---|
| **Tampering** | Document content altered between parse and feature derivation | All parsed docs hashed; hash propagated through evidence register; replay parity verifies match |
| **Info disclosure** | PII leaked to logs / OTEL spans | OTEL spans MUST NOT include PII fields. Only feature IDs + derived numeric values. CI gate (TODO) — `check_pii_in_telemetry.py` |
| **Repudiation** | Document later claimed never received | Document hash + ingestion timestamp written to evidence register on receipt, before any processing |

### Boundary 3: Feature Derivation

| Threat | Description | Control |
|---|---|---|
| **Tampering** | Forbidden feature smuggled into derived feature set | `forbidden_feature_checker.py` runs after derivation, blocks decision packet creation |
| **Info disclosure** | Derived feature implicitly encodes a forbidden attribute (proxy) | **GAP** — proxy-detection requires offline analysis; current checker only catches explicit features. Document in compliance audit. |
| **Repudiation** | Feature value later claimed different | `feature_derivation_engine.py` writes feature provenance — input doc, derivation function, version |

### Boundary 4: Decision Assembly

| Threat | Description | Control |
|---|---|---|
| **Tampering** | Decision packet altered post-assembly | Packet is hashed; hash signed (see `_emit_signs_execution_trace` ADG edge); verifiable downstream |
| **Repudiation** | Decision later claimed not issued / different | Packet committed to append-only ledger before return to requester |
| **EOP** | Decision exceeds approver's authority | `authority_limit_validator.py` blocks before assembly completes |

### Boundary 5: Evidence Register

| Threat | Description | Control |
|---|---|---|
| **Tampering** | Audit ledger entry mutated post-write | Hash-chain over consecutive entries (see `appends_hash_chain` ADG edge); any mutation breaks the chain |
| **Repudiation** | Whole ledger claimed missing | Periodic external attestation (TODO — out of scope; cite as gap) |

## Compliance Gates (mapped to validators)

| Regulatory concern | Enforcing validator | Hard gate? |
|---|---|---|
| Fair lending — no protected-class influence | `forbidden_feature_checker.py` | YES — blocks decision |
| Authority limits — decision within approver's scope | `authority_limit_validator.py` | YES |
| Data freshness — no stale data in regulated decision | `stale_data_validator.py` | YES |
| Evidence consistency — no contradictory evidence accepted | `contradiction_validator.py` | YES |
| Document completeness — required docs present | `document_completeness_validator.py` | YES |
| Overall compliance posture | `compliance_validator.py` | YES |

All six validators run before decision packet emission. Any failure halts the decision.

## Known Gaps & Mitigations

| Gap | Severity | Mitigation Plan |
|---|---|---|
| Proxy-feature detection (Boundary 3) | High | Offline statistical fairness audit; tracked in DEFERRED_SCOPE |
| External ledger attestation (Boundary 5) | Medium | Track in NEXT_STEP; integrate with regulatory attestation provider |
| PII-in-telemetry CI gate not yet present | High | NEXT_STEP — `ops_scripts/ci/check_pii_in_telemetry.py` |
| Forbidden-feature list not present in repo | Critical | Author-Gate decision required to author this list (legal review) |
| No automated red-team / adversarial test suite | Medium | NEXT_STEP — `ops_scripts/assurance/red_team_runner.py` exists; not wired to underwriting fixtures |
| No documented incident-response procedure for compliance hits | High | Capture in compliance officer onboarding (when role exists) |

## Threat-Model Review Cadence

- **Quarterly review** by app owner + compliance officer.
- **Triggered review** on: validator change, new feature class, regulator interaction, security incident.
- **Annual external review** (when in production) by an external SOC2 / fair-lending auditor.

## Why This Document Matters for the SVP+ Narrative

A senior hiring panel for a fintech / regulated-AI engineering role will probe this exact area: "you built an AI underwriting decision engine — walk me through the threat model." This document is the answer. The depth of the validator chain (6 dedicated validators, vs. 1-2 in peer apps) is the architectural answer to a regulated-domain problem, and a defensible portfolio narrative.
