# L5 Out-of-Band Planes — Calibration, Assurance, Audit/Forensic

**Scope**: Specifies the three out-of-band planes that feed L5 policy versions but **never alter the current certified run**.

**Covers gaps**: G-10 (eval-driven threshold calibration), G-11 (continuous red-team + threat intel), G-18 (replay envelope downstream contract).

**Sources**:
- OpenAI *Governed Agents Cookbook* → automated feedback loop for threshold tuning; Promptfoo red-team CI integration
- Anthropic *Framework* → Threat Intelligence monitoring loop; agentic-misalignment evals; RSP v3 external review
- Google *SAIF* → Assurance Controls (red team + vuln mgmt); CoSAI baselines
- Internal: `apps_eval/`, `tools/calibration/`, `config/judges/`, `config/retrieval/calibration_manifest.yaml`

---

## 1. The V4 Invariant

> **Out-of-band planes feed `policy_version_next`. The current run is immutable post-CERTIFY.**

This extends the v3 invariant (*"learning signals may inform future thresholds but cannot alter the current certified run"*) with an explicit mechanism: three planes operating *outside* the request path, producing a candidate `policy_version` that is promoted (or rejected) via a gate and then becomes the next G2 policy set.

---

## 2. Calibration Plane (G-10)

### 2.1 Purpose
Tune guardrail thresholds and policy parameters against golden + adversarial corpora; produce candidate policy versions.

### 2.2 Inputs
- **Golden corpus** (`data/eval/golden/`): known-good request/response pairs that should pass.
- **Adversarial corpus** (`data/eval/adversarial/`): known-bad / edge-case pairs that should be blocked.
- **Judge calibration data** (`data/judge_calibration/`): human-labeled anchors; see `judge-calibration-cadence.md`.
- **Production telemetry digests** (from Audit Plane, anonymized): distribution of real traffic patterns.

### 2.3 Cadence by risk_tier_band
| Band | Cadence |
|---|---|
| LOW | Weekly |
| MODERATE | Daily |
| HIGH | Continuous (every policy-affecting PR) |

### 2.4 Process
1. Load candidate threshold / rule set.
2. Run evaluation harness (`apps_eval/engines/evaluation_retrieval_engine.py` + equivalents).
3. Score against golden (precision) and adversarial (recall) corpora.
4. Compute family-level metrics (per `guardrail_families.md` §1).
5. Emit `CalibrationReport` artifact with: current vs. candidate metrics, coverage, regressions.

### 2.5 Promotion Gate (per `evaluation-promotion-gate.md`)
A candidate `policy_version` is promoted only when:
- No family regresses below its locked floor.
- No guardrail with `hard_constraint: true` exhibits any false-negative on adversarial corpus.
- Judge calibration within unknown-budget watchdog (see `judge-calibration-cadence.md`).
- Human promoter sign-off (ADR-style) for HIGH-band families.

Promotion → `policy_version_next`; enters G2 on next packet. Current in-flight packets continue on their issued `policy_version`.

### 2.6 Artifact paths (current repo)
- `config/retrieval/calibration_manifest.yaml` — existing calibration SSOT
- `config/judges/rubrics.yaml`, `config/judges/trace_rubric.yaml`, `config/judges/budget.yaml`
- `tools/calibration/` — calibration entry points
- `ops_scripts/calibration/weekly_refresh.py` — existing weekly cadence

---

## 3. Assurance Plane (G-11)

### 3.1 Purpose
Continuous adversarial pressure on the governance plane itself. Produce signed attestations that the current policy set resists known attack classes.

### 3.2 Components

#### 3.2.1 Red-Team CI Harness
- **Tooling**: Promptfoo-style target + config + report (OpenAI cookbook pattern).
- **Coverage**: per-family adversarial cases from `data/eval/adversarial/`.
- **Cadence**: gates every policy-version promotion; ad-hoc on demand.
- **Output**: `AssuranceReport` with pass/fail per family, regression diff vs previous version.

#### 3.2.2 Threat Intelligence Loop (Anthropic pattern)
- External signal ingestion: published jailbreaks, new injection patterns, sector-specific attack variants.
- Feeds F-18 (Threat-Intel Signature) guardrail with new signatures.
- Triggers out-of-cycle Calibration run when high-severity signal lands.

#### 3.2.3 Agentic Misalignment Eval Suite (Anthropic)
- Scenario-based evals probing for misaligned goal pursuit, specification gaming, reward-hacking.
- Run pre-deployment for any HIGH-band-eligible agent.
- Failure = block registry entry from granting HIGH-band tokens.

#### 3.2.4 Vulnerability Management (SAIF Assurance control)
- Standard vuln scanning on tool registry entries (dependency CVEs, MCP connector security advisories).
- Quarterly full-sweep; continuous dependency watch.

### 3.3 Promotion Gate Interlock
Assurance Plane has **veto** on Calibration Plane promotions:
- If red-team report shows regression on any hard_constraint family → block.
- If threat-intel loop flagged a new signature not yet covered → block or require explicit acceptance.
- If misalignment eval suite regresses → block HIGH-band promotions specifically.

### 3.4 Artifact paths (proposed additions)
- `data/eval/adversarial/` (exists) + `data/eval/red_team/` (new)
- `ops_scripts/assurance/` (new — red-team runners, threat-intel ingest)
- `docs/reports/assurance/<YYYY-Www>.md` (new — weekly assurance reports)

---

## 4. Audit / Forensic Plane (G-18)

### 4.1 Purpose
Emit, index, and independently verify `replay_envelope` artifacts so any certified run can be reconstructed after the fact.

### 4.2 `replay_envelope` Schema (descriptive)

```yaml
replay_envelope:
  schema_version: semver
  token_id: str                      # from capability_token
  compliance_hash: sha256
  policy_version: semver
  registry_digest: sha256

  request:
    packet_hash: sha256
    risk_tier_band: LOW|MODERATE|HIGH
    principal_chain: { ... }         # verbatim from capability_token

  enforcement_trace:                 # ordered list
    - stage: CLIENT_GUARDRAILS | AGENT_GUARDRAILS | HANDOFF | CONTEXT | CHOKEPOINT | LLM_INGRESS | LLM_EGRESS
      family_results: [ { family_id, verdict, score, threshold } ]
      duration_ms: int

  decision:
    verdict: REJECT | REMEDIATE | CERTIFY
    remediation_diff: str | null
    rejection_reason: str | null

  outputs:
    response_hash: sha256
    side_effects: [ { kind, target, principal_chain, at } ]

  retention:
    band: LOW|MODERATE|HIGH
    retain_until: iso8601
    forensic_index_ref: str
```

### 4.3 Retention by band
| Band | Retention |
|---|---|
| LOW | 30 days |
| MODERATE | 1 year |
| HIGH | 7 years + forensic index |

### 4.4 Independent Verifier
A separate process (runs out-of-band) that:
1. Samples `replay_envelope`s (all for HIGH; statistical for LOW/MODERATE).
2. Re-runs the enforcement trace against the pinned `policy_version` + `registry_digest`.
3. Asserts: same family verdicts, same decision, same compliance_hash.
4. Any divergence → forensic alert to Assurance Plane.

### 4.5 Compliance Attestation
Audit Plane produces periodic attestations mapping samples to:
- NIST AI RMF functions (Govern / Map / Measure / Manage)
- ISO/IEC 42001 controls
- CoSAI baselines
- Sector overlays (HIPAA / SOX / GDPR) where tagged by `sector_overlays` in capability_token

### 4.6 Artifact paths (proposed)
- `artifacts/l5/replay_envelopes/<YYYY>/<MM>/<DD>/` (new)
- `artifacts/l5/attestations/<YYYY-Ww>.md` (new)
- `tools/l5/replay_verifier.py` (new)

---

## 5. Plane Interaction Diagram

```
        ┌───────────────────────────┐
        │ L5 Runtime (in-band)      │───── emits ─────┐
        │ G1/G2/Static/Runtime/Dec. │                 │
        └─────────────┬─────────────┘                 │
                      │                               ▼
                      │                    ┌──────────────────────┐
                      │                    │ AUDIT / FORENSIC     │  [G-18]
                      │                    │  - replay_envelope   │
                      │                    │  - verifier          │
                      │                    │  - attestation       │
                      │                    └─────────┬────────────┘
                      │                              │
                      │                              │ (digests, anomaly signals)
                      │                              ▼
                      │                    ┌──────────────────────┐
                      │                    │ ASSURANCE            │  [G-11]
                      │                    │  - red-team CI       │
                      │                    │  - threat intel      │
                      │                    │  - misalignment evals│
                      │                    │  - vuln mgmt         │
                      │                    └─────────┬────────────┘
                      │                              │
                      │                              │ (veto / ack)
                      │                              ▼
                      │                    ┌──────────────────────┐
                      │                    │ CALIBRATION          │  [G-10]
                      │                    │  - threshold tuning  │
                      │                    │  - golden+adversarial│
                      │                    │  - promotion gate    │
                      │                    └─────────┬────────────┘
                      │                              │
                      │      policy_version_next ◄───┘
                      │
                      └── on next packet, G2 loads promoted policy
```

---

## 6. Governance of the Planes Themselves

Each plane has:
- **Owner** (human): accountable for its health and promotion decisions.
- **Cadence**: defined in §2.3, §3.2, §4.3.
- **Success criteria**: metric floors checked weekly; degradation triggers remediation plan.
- **ADR requirement**: any change to plane mechanics requires an ADR (per ADR Registry).

---

## 7. Existing Infrastructure Reuse

| New plane component | Existing artifact | Status |
|---|---|---|
| Calibration runner | `apps_eval/engines/evaluation_retrieval_engine.py`, `ops_scripts/calibration/weekly_refresh.py` | Exists; needs plane framing |
| Judge calibration | `config/judges/*.yaml`, `judge-calibration-cadence.md` | Exists; aligned |
| Promotion gate | `evaluation-promotion-gate.md` | Exists; aligned |
| Golden / adversarial corpora | `data/eval/golden/`, `data/eval/adversarial/` | Exist; extend |
| Red-team harness | — | **New** (adopt Promptfoo or equivalent) |
| Threat-intel loop | — | **New** |
| Replay verifier | — | **New** (spec → per-gap plan) |
| Attestation generator | — | **New** |

---

## 8. Out of Scope

- Choice of specific red-team tooling (Promptfoo vs alternative).
- CoSAI baseline mapping table (separate plan; cross-ref from ADR).
- Implementation — spawned by per-gap plans.
