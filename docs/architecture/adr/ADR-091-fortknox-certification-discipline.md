# ADR-091 — Fort Knox Certification Discipline

**Status**: Accepted
**Date**: 2026-05-01
**Plan**: `.claude/plans/fortknox-certification-discipline-fb2a9e.md`
**Pairs with**: ADR-080 (Phase D Runtime Certification design anchor), ADR-050 (intelligence-ledger family)
**Constitutional rule**: §32

## Context

The runtime-certification stack (`scripts/compile_requirement_signoff.py`,
`scripts/verify_final_requirement_signoff_bundle.py`,
`scripts/generate_mutation_rejection_report.py`,
`certification/schemas/evidence_assertion.schema.json`) shipped in Phase D
without harness-side enforcement. Codex had three latent failure modes:

1. **Hand-edited reports.** Codex could open
   `artifacts/certification/final_requirement_signoff_report.json` and
   "fix" a row instead of regenerating from atomic assertions — bypassing
   the hostile verifier doctrine.
2. **Prose certification claims.** Codex could narrate "RTC-REQ-042 is
   now SIGNED_OFF" without ever invoking the compiler, leaving auditors
   unable to distinguish a real signoff from a prose hallucination.
3. **Silently-broken compiler.** A compiler that rejects every assertion
   would look identical to a rigorous one with no green rows. Without a
   positive-control canary, monotone failure is undetectable.

These are the same three classes that SLSA L3 / in-toto / Sigstore /
Critic-Agent doctrine address through (a) producer allowlists, (b)
attestation envelopes, (c) adversarial review. This ADR codifies the
mapping for the legacy editor harness layer.

## Decision

Adopt the **hostile-verifier doctrine** as a constitutional rule (§32)
with five enforcement layers:

| Layer | Artifact | Behavior |
|---|---|---|
| Advisory rule | `.claude/rules/fortknox-certification-discipline.md` | Always-on; shapes Codex composition |
| Pre-write hook | `.claude/governance/scripts/pre_write_fortknox_guard.py` | Blocks direct edits to `final_requirement_signoff_report.{json,sha256,merkle.json,signature.json}` and `certification/*.xlsx` (exit 2) |
| Post-cursor-agent audit | `.claude/governance/scripts/post_cursor_agent_fortknox_integrity_audit.py` | Fail-open detection of prose signoff claims without compiler invocation; logs to `artifacts/windsurf/fortknox_integrity_violations.jsonl` |
| Pre-commit triplet | `ops_scripts/ci/check_fortknox_{clean_bundle,mutation_rejection,positive_control}.py` | T7s.1/.2/.3 — separation-of-duties: compiler+verifier agree, all mutations rejected, RTC-REQ-001 canary remains SIGNED_OFF |
| Nightly regression | `.github/workflows/fortknox-nightly.yml` | Diffs trust_level + signed_off count + merkle_root vs prior committed bundle; opens `cert-regression`-tagged issue on regression |
| Author-Gate trigger | `.claude/rules/author-gate-decision-points.md` §1.11 | `certification_claim` — Codex must run compiler+verifier before claiming SIGNED_OFF / FINAL_SIGNED_CERTIFICATION |
| Skill | `.claude/skills/fortknox-evidence/SKILL.md` | Procedural recipe + forbidden-pattern checklist |

Producer-allowlist (per §32): atomic assertions emitters MUST live under
`tools/cert/*.py`, `scripts/verify_*_gate.py`, or `scripts/verify_rtc_*.py`.
Runtime code paths (`agentic_core/*`, `apps_*/*`, `system_learning/*`)
MAY NOT emit assertions.

The signature envelope writer (`tools/cert/sign_requirement_signoff_envelope.py`)
populates the SLSA-pattern envelope at
`artifacts/certification/final_requirement_signoff_report.signature.json`
with the deterministic claims (report sha256, sidecar diff, merkle root,
trust level, row count) and pins
`signature_verification_status: UNSIGNED_BLOCKED` until the signer-identity
follow-up Author-Gate (see Deferred decisions).

## Consequences

**Positive**:

- Compiler is the single status authority. XLSX and Markdown exporters
  become read-only views.
- Hand-edits to compiler outputs are physically blocked at write time.
- Prose certification claims without compiler invocation are detected
  retroactively and surfaced in a violation log.
- Positive control (`RTC-REQ-001`) provides a known-good canary; a
  silently-broken compiler regresses the canary first.
- Mutation rejection runner (Critic Agent counterpart) is wired
  independently of the compiler — separation of duties enforced.

**Negative**:

- Three new pre-commit gates increase commit latency (~6–10s typical, up
  to 600s if mutation runner is heavy).
- Positive-control gate runs in **advisory mode** until RTC-REQ-001 is
  actually built and verified `SIGNED_OFF`. Operator must flip
  `POSITIVE_CONTROL_STRICT=1` in CI when the canary is established.
- The signature envelope is structurally complete but
  cryptographically unsigned — `trust_level` cannot promote to
  `SIGNED_PROOF` or `FINAL_SIGNED_CERTIFICATION` until the signer-identity
  follow-up Author-Gate lands.

**Neutral**:

- No new MCP server. Fort Knox integrity comes from deterministic
  scripts + schemas + hashes, not from a trusted intermediary — adding
  a Fort Knox MCP would itself become a single point of trust,
  contradicting the hostile-verifier doctrine.

## Deferred decisions

### P5 — Signer identity (separate Author-Gate, target ADR-NNN)

The cryptographic-signing layer is structurally scaffolded but not
wired. The follow-up Author-Gate (`decision_type=architecture_choice`,
trigger `signer_identity_for_runtime_cert_envelope`) must pick among:

| Option | Pros | Cons |
|---|---|---|
| **cosign keyless via GitHub OIDC** (recommended) | Industry-standard SLSA reference; no key custody; native GH Actions support; Sigstore transparency log entry | Ties signer identity to GitHub OIDC infra; requires GH Actions for signing |
| GPG | Broad compatibility; offline signing possible | Manual key custody; rotation/revocation overhead; not SLSA-default |
| In-house HMAC/RSA | Full control over key material | Build + audit a custom signing infra; no Sigstore transparency benefit |

The pending-signer marker
`cosign-keyless-via-github-oidc-pending-adr-091-p5b` is the deterministic
default in the envelope until that decision lands.

### Notion auto-routing receipts

When the compiler fires and `trust_level` upgrades, AGENTS.md
auto-routing rule "Trust level changes in Fort Knox bundle" posts a row
to ADR Registry. Until §32 fires for the first time on a real upgrade,
no Notion writeback occurs from this ADR — the writeback is event-driven,
not migration-driven.

## References

- Schema: `certification/schemas/evidence_assertion.schema.json`
- Compiler: `scripts/compile_requirement_signoff.py`
- Bundle verifier: `scripts/verify_final_requirement_signoff_bundle.py`
- Mutation runner: `scripts/generate_mutation_rejection_report.py`
- Envelope writer: `tools/cert/sign_requirement_signoff_envelope.py`
- Rule: `.claude/rules/fortknox-certification-discipline.md`
- Skill: `.claude/skills/fortknox-evidence/SKILL.md`
- Plan: `.claude/plans/fortknox-certification-discipline-fb2a9e.md`
- Pairs: ADR-080 (Phase D anchor), ADR-050 (intelligence-ledger family)

Web-research grounding: SLSA L3 build-provenance verifiability,
in-toto predicate-per-subject attestations, Sigstore non-repudiation
+ transparency log, Critic-Agent / Adversarial Code Review.
