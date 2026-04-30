# RUNBOOK — apps_underwriting_ai

> **When to use this:** a regulated decision is wrong, blocked, or its audit trail is incomplete.
> **Companion docs:** `SLO.md` · `THREAT_MODEL.md` · (SVP review at W1.6)
> **Owner:** see `CODEOWNERS`

## CRITICAL: Read This First

apps_underwriting_ai produces **regulated, binding decisions**. Every operational response must preserve:

1. **Audit trail integrity** — never lose a decision packet, never silently mutate evidence
2. **Authority-limit enforcement** — never produce a decision that exceeds the approver's authority
3. **Forbidden-feature isolation** — never let a regulated feature influence a decision

When in doubt, **freeze and escalate**, never auto-recover.

## On-Call Decision Tree

```
apps_underwriting_ai is misbehaving
├── Did the authority-limit validator fail or trip?
│   ├── YES → §1 Authority Failure (CRITICAL)
│   └── NO  → continue
├── Did the forbidden-feature checker emit a hit?
│   ├── YES → §2 Forbidden Feature (CRITICAL)
│   └── NO  → continue
├── Did replay parity mismatch?
│   ├── YES → §3 Replay Mismatch (CRITICAL)
│   └── NO  → continue
├── Is document completeness failing?
│   ├── YES → §4 Document Completeness
│   └── NO  → §5 Generic
```

## §1 Authority Limit Failure / Bypass (CRITICAL)

**Symptom:** `authority_limit_validator.py` is unavailable, OR a decision is rendered with `authority_validated=False`.

**Why critical:** decisions without authority validation are **non-binding** and create regulatory exposure.

**Triage:**
1. **REFUSE all new decisions** while authority validator is down. Engage kill switch in `apps_underwriting_ai/config/`.
2. Identify any decisions issued in the unvalidated window (audit query).
3. Mark those decisions as `pending_authority_review`; flag for manual re-approval.

**Mitigation:**
- Restore validator service.
- Replay every flagged decision; verify authority compliance.
- Log full incident to compliance audit ledger.

**This is paged 24/7.**

## §2 Forbidden Feature Hit (CRITICAL)

**Symptom:** `forbidden_feature_checker.py` flags a decision as having used a regulated feature.

**Why critical:** regulated features (race, gender, protected class proxies, etc.) MUST NOT influence underwriting decisions. A hit means either the feature leaked into the model OR the checker's signature pattern fired falsely.

**Triage:**
1. Freeze the request immediately: `python -m apps_underwriting_ai --freeze --request-id=<id>`.
2. Inspect the feature provenance: which features did the decision touch? Which one matched the forbidden pattern?
3. Determine: real leak vs. false positive.

**Mitigation:**
- **Real leak:** halt the model; notify compliance; re-train without the feature; ADR documenting the incident.
- **False positive:** Author-Gate review of the forbidden-pattern signature; tighten if needed.

**This is paged 24/7.**

## §3 Replay Mismatch (CRITICAL)

**Symptom:** nightly replay job re-derives a prior decision and the digest does not match.

**Why critical:** replay parity is the foundation of audit-trail credibility. A mismatch means either the model is non-deterministic OR a feature input was mutated after-the-fact.

**Triage:**
1. **Freeze the model** — block all new decisions on this codepath.
2. Capture full state of the original decision and the replay attempt.
3. Diff: features, evidence, model version, judge version.

**Common causes:**
1. Model version drift (most common)
2. Evidence-store mutation (data integrity issue — INVESTIGATE FIRST)
3. Non-deterministic feature derivation (e.g., `datetime.now()` in a feature)
4. External lookup that returned different data

**Mitigation:**
- Identify cause.
- Either fix determinism OR document via ADR that this codepath is no longer replayable (which has compliance implications).
- Never relax the digest assertion silently.

**This is paged 24/7.**

## §4 Document Completeness Failure

**Symptom:** `gate_violations=["INCOMPLETE_DOCUMENTS:<doc>"]`.

**Triage:**
1. Identify the missing document type.
2. Check ingestion engine: `python -m apps_underwriting_ai --inspect-ingest --request-id=<id>`.
3. Determine: missing in source, lost in parsing, or rejected by validator?

**Mitigation:**
- Reject the request back to the upstream system with explicit gap notice.
- Never auto-substitute "best-effort" documents. The decision must wait for completeness.

## §5 Generic Investigation

If §1-§4 don't apply:
1. Replay: `python -m apps_underwriting_ai --replay --request-id=<id>`.
2. Inspect feature derivation: `python -m apps_underwriting_ai --feature-trace --request-id=<id>`.
3. Compare against last-known-good fixture in `examples/`.

## Rollback Procedure

apps_underwriting_ai rollback is **never** routine — every rollback must be:
1. Author-Gate approved (it changes regulated decision logic)
2. Replay-tested against ≥100 historical decisions
3. Documented in an ADR

**Procedure:**
1. Open Author-Gate decision.
2. `git revert <commit>` only after gate approval.
3. Run nightly replay parity job manually; require 100% pass before resuming new decisions.
4. Notify compliance.

## Top-3 Failure Modes

1. **Replay mismatch** → §3 (CRITICAL — data integrity)
2. **Forbidden-feature hit** → §2 (CRITICAL — regulatory)
3. **Authority-limit validator unavailability** → §1 (CRITICAL — non-binding decision risk)

All three are paged 24/7.

## Key Files

- `engines/underwriting_engine.py` — main decision engine (15KB)
- `engines/feature_derivation_engine.py` — features (21KB) — **PII flow per THREAT_MODEL.md**
- `engines/decision_packet_assembler.py` — final packet
- `engines/evidence_register_engine.py` — evidence trail
- `validators/authority_limit_validator.py` — § 1
- `validators/forbidden_feature_checker.py` — § 2
- `validators/contradiction_validator.py` — evidence consistency
- `validators/stale_data_validator.py` — freshness gate
- `validators/document_completeness_validator.py` — § 4
- `validators/compliance_validator.py` — overall compliance gate
- `reasoning/feature_interpreter.py` — risk interpretation (highest ADG edge density: 42 emits)

## Escalation Contacts

- **Primary on-call:** see `CODEOWNERS`
- **Compliance officer:** TBD (REQUIRED — this app cannot operate without one in production)
- **Model risk owner:** TBD
- **Audit / regulatory:** TBD
