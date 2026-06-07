# Fort Knox Certification Discipline — P1–P4 Rollout

Status: Active
Decision date: 2026-05-01
Author-Gate: APPROVED (option: P1–P4 now, P5 scaffolded unsigned) — decision_id captured via post-hook
Plan slug: `fortknox-certification-discipline-fb2a9e`

## 1. Intent

Ship the hostile-verifier / attestation / mutation-rejection discipline for runtime certification into Windsurf enforcement layers. Grounded in SLSA L3 "verifiable by third party", in-toto predicate-per-subject, Sigstore non-repudiation, and Critic Agent adversarial review. Maps each Fort Knox criterion to a concrete Windsurf layer (rule, constitutional §, CI gate, hook, skill, workflow).

User packet (authoritative source): Cascade conversation 2026-05-01 — the packet lists 12 sections; this plan implements P1–P4 (§1–§4, §6, §7, §8, §10, §11). P5 (signature envelope implementation) is deferred to a separate Author-Gate on signer identity (cosign vs GPG).

## 2. Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|---|---|---|---|---|---|---|
| W1 Foundation | P1.1–P1.5 | Rule + constitutional §32 + 3 CI gates | ~14k | compile + verifier + mutation scripts unchanged | Todo | rule lints; §32 parses; 3 gates import-clean |
| W2 Hooks | P2.1–P2.3 | pre_write + post_cascade audit + hooks.json wire-up | ~6k | hooks.json schema purity (§27) | Todo | both hooks exit 0 on no-op response |
| W3 Procedural | P3.1–P3.2 | Skill + Author-Gate §1.11 | ~5k | skill-creator template | Todo | skill frontmatter valid; AG §1.11 parses |
| W4 Automation | P4.1–P4.2 | Nightly workflow + AGENTS.md auto-routing rows | ~3k | GH Actions OIDC not required (no signing yet) | Todo | workflow YAML lints; AGENTS.md autogen block still in sync |
| W5 Envelope scaffold | P5.1 | Unsigned envelope writer at `tools/cert/sign_requirement_signoff_envelope.py` (SSOT-compliant per §31) + ADR-091 codifying the doctrine | ~4k | scripts/ would have violated §31 → moved to tools/cert/ | Done | scaffold rewrites envelope; status=UNSIGNED_BLOCKED; --enforce returns 2 |

## 3. Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|---|---|---|---|---|---|
| P1.1 | Advisory rule | `.windsurf/rules/fortknox-certification-discipline.md` | House-style consistency | 4k | Todo |
| P1.2 | Constitutional §32 | `.windsurf/rules/constitutional.md` | One-line entry matching §28–§31 shape | 1k | Todo |
| P1.3 | `check_fortknox_clean_bundle.py` | `ops_scripts/ci/` | Subprocess timeout + bundle JSON parse | 3k | Todo |
| P1.4 | `check_fortknox_mutation_rejection.py` | `ops_scripts/ci/` | Mutation runner may be slow — cap via `--quick` | 3k | Todo |
| P1.5 | `check_fortknox_positive_control.py` | `ops_scripts/ci/` | RTC-REQ-001 canary | 2k | Todo |
| P1.6 | pre-commit wiring | `.pre-commit-config.yaml` | Correct stage placement | 1k | Todo |
| P2.1 | `pre_write_fortknox_guard.py` | `.windsurf/scripts/` | Emitter-signature header check regex | 2.5k | Todo |
| P2.2 | `post_cascade_fortknox_integrity_audit.py` | `.windsurf/scripts/` | Fail-open; append-only JSONL | 2.5k | Todo |
| P2.3 | hooks.json wiring | `.windsurf/hooks.json` | Schema purity (§27) | 1k | Todo |
| P3.1 | Skill | `.windsurf/skills/fortknox-evidence/SKILL.md` | Frontmatter validator | 3k | Todo |
| P3.2 | Author-Gate §1.11 | `.windsurf/rules/author-gate-decision-points.md` | `certification_claim` trigger | 2k | Todo |
| P4.1 | Nightly workflow | `.github/workflows/fortknox-nightly.yml` | Artifact upload sizing | 2k | Todo |
| P4.2 | AGENTS.md auto-routing | `AGENTS.md` | Autogen block preservation (3 rows) | 1k | Todo |

## 4. Files In Scope (exactly these — scope-containment §)

Created: 9 (rule, 3 CI gates, 2 hooks, skill, workflow, plan)
Modified: 4 (constitutional.md, .pre-commit-config.yaml, hooks.json, author-gate-decision-points.md, AGENTS.md)

## 5. Gap Register

| Gap | Resolution |
|---|---|
| No sign_requirement_signoff.py | Deferred to separate Author-Gate (signer identity decision) — see P5 deferred-scope marker at plan tail |
| Notion auto-routing triggers fire only when events occur | No writeback now — triggers documented in AGENTS.md |
| Memory MCP entity writes (P3 §6) | Deferred to a single follow-up MCP call per serialization §25 — NEXT_STEP marker at plan tail |

## 6. Success Criteria

- Constitutional §32 parses; rule lints in house-style.
- Each CI gate runs in <30s on a clean repo; all three exit 0 today on the committed report state.
- `pre_write_fortknox_guard.py` exits 2 on a simulated direct report edit; exit 0 otherwise.
- `post_cascade_fortknox_integrity_audit.py` appends zero rows for this plan's own response (no violations introduced).
- Nightly workflow passes syntax on `actionlint` (or equivalent).
- AGENTS.md autogen blocks remain in sync (existing gate `agents-md-autogen-sync` passes).

## 7. Deferred / Next Steps

P5.1 envelope scaffold landed at `tools/cert/sign_requirement_signoff_envelope.py` (SSOT-routed per §31; the user packet's `scripts/` path would have violated the legacy-allowlist gate). Scaffold validates report shape, populates the SLSA-pattern envelope deterministic claims, and pins `signature_verification_status: UNSIGNED_BLOCKED`. ADR-091 codifies the doctrine and names the deferred signer-identity decision.

Remaining deferrals — captured as durable markers below:

DEFERRED_SCOPE: plan=fortknox-certification-discipline-fb2a9e wave=W6 phase=P5.2 layer=L6 fan_in=0 surface=Security coverage_gap_pct=100.0 est_tokens=8000 reason=Cosign keyless via GitHub OIDC implementation Author-Gate pending ADR-091 successor

NEXT_STEP: plan=fortknox-certification-discipline-fb2a9e title=Notion ADR Registry post for ADR-091 priority=P3 est_tokens=2000 reason=Auto-routing per AGENTS.md fires on ADR creation; query data_source schema then API-post-page next session

NEXT_STEP: plan=fortknox-certification-discipline-fb2a9e title=Notion Constitutional Rules Registry post for §32 priority=P3 est_tokens=2000 reason=Track rule status next to §28-§31 siblings; query schema then post next session
