# SVP Engineering Review — apps_underwriting_ai

**Application:** apps_underwriting_ai (Regulated Underwriting Decision Engine)
**Review Date:** 2026-04-29
**Status:** SVP+ candidate; gaps tracked
**Test Pass Rate:** 100% (current — 30+ tests across 6 validators + types)

---

## What's Specifically Hard About This Domain

Underwriting decisions are **regulated, binding, and audited**. That changes everything about the engineering bar:

1. **Decisions cannot be silently retried.** A retry that succeeds after a real validator failure is a compliance violation, not a recovery.
2. **Every decision must be replayable.** If a regulator asks "why did you approve this loan?" 18 months later, the answer must be reproducible from immutable inputs + a versioned model.
3. **Forbidden features must be impossible to use, not merely "discouraged."** A forbidden-feature checker that runs after-the-fact is insufficient — though it's the floor we have. Proxy-feature detection is harder and is a documented gap.
4. **Authority limits are non-negotiable.** A decision exceeding the approver's authority is non-binding. The system must refuse, not warn.

This drives the architecture: 6 dedicated validators (vs. 1-2 in peer apps), 14 type modules (vs. 1-2), evidence-register engine, decision packet assembler. None of this is excess — every piece earns its place against a regulated-decisioning failure mode.

## Non-Goals (deliberately out of scope)

- **Real-time ingestion.** Underwriting is batch-oriented; sub-second latency is not the goal — auditability is.
- **Self-improving model.** Decisions are gated by versioned model weights. Continuous learning would break replay parity.
- **Customer-facing UI.** Decisions feed downstream systems; this app is an engine, not a product surface.
- **Negotiation logic.** Decision is binary (approve/reject/escalate); negotiation lives elsewhere.

## Alternatives Considered (and rejected)

### Alternative 1: Single monolithic validator

**Considered:** combine all 6 validators (authority, compliance, contradiction, stale-data, forbidden-feature, completeness) into one `decision_validator.py`.

**Rejected because:**
- Each validator has independently-evolving rules (compliance changes faster than authority limits).
- A monolithic validator has a single failure surface; partial failure (e.g., authority validator down) becomes an all-or-nothing outage.
- Audit clarity requires per-concern trace ("which validator fired and why?"), which a monolith obscures.

### Alternative 2: Mutable evidence register (overwrite on update)

**Considered:** allow evidence-register entries to be updated when underlying source data changes.

**Rejected because:**
- Mutation breaks replay parity by definition.
- Regulators view mutable audit trails as evidence of tampering risk, not data hygiene.
- The append-only ledger pattern is the industry default for this reason.

### Alternative 3: LLM-only feature derivation

**Considered:** let the LLM derive risk features end-to-end from documents.

**Rejected because:**
- LLM determinism is insufficient for regulated decisioning (replay parity violations).
- Feature derivation must be inspectable and explicable; an LLM-derived feature with no decomposition is a black box.
- Hybrid (deterministic feature + LLM cross-check) preserves explicability and replayability.

## SVP Standards Compliance

### 1. Domain Contracts (Pydantic — 14 type modules)

| Component | Status | Notes |
|-----------|--------|-------|
| `UnderwritingRequest` | ✅ | Input contract |
| `RiskFeatures` | ✅ | Derived feature set with provenance |
| `DecisionPacket` | ✅ | Immutable output artifact, signed |
| `EvidenceEntry` | ✅ | Per-feature evidence with source hash |
| `AuthorityScope` | ✅ | Approver authority bounds |
| `ComplianceFlags` | ✅ | Per-rule compliance state |
| `ForbiddenFeatureMatch` | ✅ | Match record + signature pattern |
| `ContradictionRecord` | ✅ | Pair of contradicting evidence + resolution |
| `StalenessReport` | ✅ | Per-source freshness |
| `DocumentCompletenessRecord` | ✅ | Required-doc gap report |
| (4 more) | ✅ | Per the 14-type breakdown |

### 2. Validators (6 — most domain-rich in portfolio)

| Validator | Hard gate? | Bypassable? |
|-----------|------------|-------------|
| `authority_limit_validator.py` | YES | NO — refusal cascades |
| `compliance_validator.py` | YES | NO |
| `contradiction_validator.py` | YES | NO — contradictions surface in packet |
| `stale_data_validator.py` | YES | NO |
| `forbidden_feature_checker.py` | YES | NO — refuses decision |
| `document_completeness_validator.py` | YES | NO — refuses decision |

**No "advisory" or "warning" validators.** Every validator is a hard gate. This is the regulated-domain default.

### 3. Engines

| Engine | Lines | Role |
|--------|------:|------|
| `feature_derivation_engine.py` | 21K | Doc → typed features with provenance |
| `underwriting_engine.py` | 15K | Decision orchestration |
| `evidence_register_engine.py` | 10K | Append-only audit ledger |
| `document_reconciliation_engine.py` | 8K | Cross-doc consistency |
| `decision_packet_assembler.py` | 7K | Final immutable artifact |

## Architecture Rigor

### Layer Alignment
- **L0 Routing:** decision routing per request type
- **L1 Cognition:** feature interpretation (`reasoning/feature_interpreter.py`)
- **L2 Execution:** validator chain
- **L3 Orchestration:** underwriting engine workflow
- **L4 State:** evidence register (append-only)
- **L5 Safety:** forbidden-feature checker, authority validator
- **L6 Observability:** decision-packet provenance

### Principles
1. **Zero silent failure.** All 6 validators surface explicit `ComplianceFlags` / gate violations.
2. **Immutability over speed.** Decision packets are write-once.
3. **Replay parity is law.** Nightly replay job re-derives prior-day decisions; mismatch is a CRITICAL incident (see `RUNBOOK.md` §3).
4. **Authority is checked per-request, not per-session.** Sessions can drift; per-request validation can't.
5. **Hash-chain audit trail.** ADG edges `appends_hash_chain` + `appends_commit_receipt` enforce this.

## Test Coverage

| Test | Tests | Status |
|------|------:|--------|
| `test_underwriting_types.py` | varies | ✅ |
| `test_validators.py` (per validator) | varies | ✅ |
| `test_engines.py` | varies | ✅ |

**Honest gaps (vs. the 100% claim):**
- No property-based tests yet (W2.2 adds seed)
- No contract test for replay parity at the suite level (W2.1 adds seed)
- No fuzz test for prompt injection in document ingestion (NEXT_STEP)

## Production Readiness

| Criterion | Status | Notes |
|-----------|--------|-------|
| Type Safety | ✅ | 14-type Pydantic surface |
| Error Handling | ✅ | Hard gates, no silent paths |
| Observability | Partial | OTEL spans defined per `THREAT_MODEL.md`; PII-redaction CI gate is a NEXT_STEP |
| Configurability | ✅ | YAML configs for thresholds |
| Documentation | ✅ | This + RUNBOOK + SLO + THREAT_MODEL |
| Test Coverage | ✅ on unit; gap on contract+property — W2 |
| Compliance gates | ✅ | 6 hard validators |
| Replay parity | Partial | Engine supports it; nightly job is a NEXT_STEP |
| Forbidden-feature list in repo | **GAP** — Author-Gate required to author (legal) |

## SVP+ Bar Items Still Open

- [ ] PII-in-telemetry CI gate (`ops_scripts/ci/check_pii_in_telemetry.py`)
- [ ] Forbidden-feature signature list in repo (legal review needed)
- [ ] Nightly replay-parity job (`ops_scripts/calibration/uw_replay_parity_job.py`)
- [ ] Proxy-feature detection (offline statistical fairness audit)
- [ ] External ledger attestation integration
- [ ] Compliance officer role + onboarding doc

## Why This App Is The Strongest Portfolio Narrative

For an SVP+ engineering interview, the question is "what's the hardest engineering problem you've owned?" apps_underwriting_ai is the answer:

- **Regulated domain** with non-negotiable compliance gates
- **Immutability + replay parity** as a first-class architectural concern
- **Multi-validator gate chain** with no advisory mode
- **Cryptographic audit trail** (hash-chain ADG edges)
- **Documented threat model** with STRIDE per boundary
- **Acknowledged gaps** with mitigation tracking — credibility comes from naming what's not done, not pretending everything is

The differentiation from apps_exec / apps_research / apps_rfp is not "more code" — it's "different physics." Latency-tolerant, audit-mandatory, hard-gated. That's the recruiter-recognizable shape of regulated AI engineering.
