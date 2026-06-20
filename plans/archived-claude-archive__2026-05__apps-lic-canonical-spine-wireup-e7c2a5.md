---
status: Archived
do_not_execute: true
memorialized: true
source_surface: claude_legacy_plans
source_key: claude
original_path: 'C:\\Git\\Agentic-Workflow-FRESH\\.codex\\plans\\_archive\\2026-05\\apps-lic-canonical-spine-wireup-e7c2a5.md'
original_relative_path: '_archive\\2026-05\\apps-lic-canonical-spine-wireup-e7c2a5.md'
source_sha256: 0db827630c6f9ffa7048364227c8ade1b3bda648c480b7fafaac59f58fdf123a
recovered_status: LEGACY_EXISTING
last_commit: ''
last_commit_date: ''
created_date: ''
archived_reason: historical consolidation for review, lessons learned, and anti-pattern analysis
---

> ARCHIVED MEMORIAL RECORD: This file is preserved for review and lessons learned. Do not execute it as an active plan.

---
# apps_lic Canonical Spine Wireup

**Slug:** `apps-lic-canonical-spine-wireup`
**ID:** `e7c2a5`
**Status:** Not Started
**Started:** 2026-05-04
**Owner:** Cascade
**Pattern Source:** `apps-rg-canonical-wireup-c8a4f2.md` — adapted for outreach domain

**Goal:** Make `apps_lic` a thin app overlay on `agentic_core` for governed professional outreach drafts. Briefing is a prerequisite artifact (same as apps_rg). R4 when briefing exists and fresh. R3R4_MANAGED_WORKFLOW when briefing is missing/stale (L3 orchestrates apps_research). apps_research failure = apps_lic fail-closed through Exit V6. R3_SIMPLE_GROUNDED_READ is briefing-only; never produces outreach drafts. L0 is decision-only.

> **Feedback revision 2026-05-04:** Full architectural correction applied. Key changes: (1) briefing treated as prerequisite artifact not optional enrichment; (2) R3R4 is the governed path for missing/stale briefings; (3) signal controls (anti-pattern detector, ask engine, recipient triggers, proof modes) are contextual and scoped by recipient class — not universally mandatory; (4) wave structure reordered to W1–W8 matching feedback implementation order; (5) sentinel test list updated to full 24 from feedback; (6) L0 forbidden list extended; (7) R5 reason codes extended; (8) Exit rubric corrected with proper fail-closed scoping; (9) outreach schema extended with send_mode, omitted_claims; (10) manifest extended with claim_permission_map, proof_mode, personalization_mode, omission_policy.
>
> **Tightening patch 2026-05-04:** (1) BRIEFING_MISSING_NO_AUTO_RESEARCH renamed to BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED — only fires when policy explicitly disables research for the run; (2) R3_SIMPLE_GROUNDED_READ flow clarified to include C0/apps_research evidence path and optional PA synthesis before Exit; (3) L0 file-write prohibition tightened to write-mode operations only (read-mode config loads explicitly allowed); (4) anti-pattern count resolved to 15 default hard-fail + configurable extension list; (5) BriefingReady success criteria added with 8 required fields; (6) 5 new sentinel tests added (29 total).

---

## Hard Invariants

1. `apps_lic` is a thin app overlay on `agentic_core`.
2. L0 emits exactly one deterministic `RouteContract`.
3. L0 is decision-only. Never executes subprocesses.
4. L0 must not call, import, or reference `apps_research` directly.
5. L0 must not call providers (OpenAI, Anthropic, Gemini, Bedrock, or local model).
6. L0 must not write files or generate fallback outreach.
7. L3 or L2 may use a governed `apps_research` bridge only when policy, registry, capability, sandbox, and trace evidence are bound.
8. Every R5 or fail-closed terminal path MUST go through Exit V6.
9. Exit emits exactly one X3 disposition per run.
10. L2 generates proposed artifacts only — never writes directly to L4.
11. Durable writes flow only `Exit → UWG → L4`.
12. L6 learns from completed-run exhaust only; cannot rescue or mutate the current run.
13. Sending messages is forbidden. `apps_lic` generates drafts or send-ready candidates only.
14. No generic fallback outreach draft when briefing is absent or research fails.
15. `R3_SIMPLE_GROUNDED_READ` produces briefing artifacts only — never outreach drafts.

---

## Files In Scope

```
# Core entrypoint and adapters
apps_lic/__main__.py                                           # rewrite: canonical entrypoint + R5 helpers
apps_lic/spine_manifest.yaml                                   # rewrite: R4_SINGLE_ACTION + R3R4_MANAGED_WORKFLOW claims
apps_lic/integrations/spine_handoff.py                         # NEW: direct R3 contract surface
apps_lic/integrations/preloaded_outreach_context_manifest.py   # NEW: deterministic context contract
apps_lic/integrations/lic_identity_resolver.py                 # NEW: CLI-local identity resolver
apps_lic/integrations/lic_r5_policy.py                         # NEW: decision-only R5 policy
apps_lic/integrations/apps_research_bridge.py                  # NEW: L3-governed bridge (no L0 usage)
apps_lic/integrations/managed_workflow_dispatcher.py           # NEW: L3-orchestrated dispatch

# Config and schemas
apps_lic/config/apps_lic_static_dag.yaml                       # NEW: L2 static recipe for R4 path
apps_lic/config/apps_lic_managed_dag.yaml                      # NEW: L3-managed recipe for R3R4 path
apps_lic/config/intake_policy.yaml                             # NEW: U0 E1-E4 policy
apps_lic/config/outreach_schema.json                           # NEW: E4 validation schema
apps_lic/config/lic_plan_rules.yaml                            # NEW: L1 planning rules
apps_lic/config/l0_policy.yaml                                 # NEW: L0 route decision policy
apps_lic/config/exit_rubric.yaml                               # NEW: Exit V6 rubric for outreach

# Prompt assembly and L1
apps_lic/prompt_assembly/lic_pa_compiler.py                    # NEW: outreach-specific prompt compiler
apps_lic/L1_cognition/message_planner.py                       # refactor: wire to canonical L1 bridge

# Governance tests
tests/governance/test_apps_lic_*.py                            # 24 sentinel tests + category tests
```

**Out of scope (will NOT touch):**
- `apps_lic/engines/*Agent.py` files unless a direct failing import or adapter boundary requires it
- `apps_research/` internals — integrate via public API only
- `agentic_core/` internals unless a clearly bounded extension to an existing entrypoint is required
- Message sending, campaign batching, auto-promotion of raw drafts

---

## Wave Structure

| Wave | Phase IDs | Focus | Est. Tokens | Status | Success Criteria |
|------|-----------|-------|-------------|--------|------------------|
| **W1** | P1, P2, P3 | Remove L0 subprocess execution; enforce all R5/fail-closed through Exit V6 | ~15k | Not Started | Zero `subprocess.run` / direct `apps_research` imports in L0 path; every early-exit calls `_emit_r5_terminal_via_exit`; L0 never calls providers |
| **W2** | P4, P5, P6 | R4_SINGLE_ACTION with fresh briefing; PreloadedOutreachContextManifest; static DAG | ~25k | Not Started | Fresh briefing → R4 → L2 → Exit; manifest has all 35 fields including claim_permission_map, proof_mode, omission_policy; 6 core sentinel tests pass |
| **W3** | P7, P8, P9 | R3R4_MANAGED_WORKFLOW; L3 dispatcher; apps_research bridge; fail-closed on research failure | ~30k | Not Started | Missing briefing → R3R4 → L3 → apps_research → manifest build → R4 resume → Exit; research failure → fail-closed through Exit |
| **W4** | P10, P11, P12, P13, P14 | Config externalization; lic_pa_compiler; message_planner wiring; spine_manifest correction | ~25k | Not Started | All 5 config YAMLs valid; PA compiler composes only; manifest claims both route types; message_planner uses canonical contracts |
| **W5** | P15, P16, P17 | Exit rubric + outreach schema validation; unsupported claim omission policy; send_mode restrictions | ~20k | Not Started | Exit rubric correctly scoped fail-closed dims; omit_unsupported path works; send_now/auto_send/connector_send blocked at schema + Exit |
| **W6** | SE-P0a, SE-P0b, SE-P0c | P0 signal controls: anti-pattern detector (20 patterns); channel-length enforcement; scope-calibrated ask engine | ~20k | Not Started | Anti-pattern detector hard-fails on all 20 patterns; channel ceilings enforced; ask_friction_score computed and bound-fails >0.5 |
| **W7** | SE-P1a, SE-P1b, SE-P1c, SE-P1d | P1 contextual signal controls: recipient-trigger engine (scoped); sender credibility card; proof appropriateness (scoped); asymmetric insight (config-gated) | ~25k | Not Started | Recipient trigger scoped by recipient_class; repo proof not required for simple recruiter follow-up; asymmetric insight only when configured; 8 new tests pass |
| **W8** | T-suite, V1 | Full governance suite (24 sentinel tests); ADG no-bypass proof; Notion writeback | ~20k | Not Started | All 24 sentinel tests pass; existing governance suite green; ADG scans clean; Notion Plans row updated |

**Total est tokens:** ~180k.

---

## Phase-Level Summary

| Phase ID | Title | Scope (files) | Pain Points | Est. Tokens | Status |
|----------|-------|---------------|-------------|-------------|--------|
| **P1** | Remove L0 subprocess + direct research calls | `apps_lic/__main__.py` | Remove `subprocess.run`, `subprocess.Popen`, `os.system`; remove any direct `apps_research` import or call from L0 decision path | 5k | Not Started |
| **P2** | Route all R5/fail-closed through Exit V6 | `apps_lic/__main__.py:_emit_r5_terminal_via_exit` (new) | Every early-return and terminal path must call `_emit_r5_terminal_via_exit` before process exit | 5k | Not Started |
| **P3** | L0 decision-only enforcement | `apps_lic/__main__.py` | Add explicit guard: L0 emits `RouteContract` only; create `lic_r5_policy.py` stub for decision logic | 5k | Not Started |
| **P4** | R4 entrypoint module | `agentic_core/runtime/entrypoints/integrated_r4_lic_pipeline_run.py` (NEW) | Thin wrapper over canonical R4 entrypoint with apps_lic identity binding | 10k | Not Started |
| **P5** | PreloadedOutreachContextManifest | `apps_lic/integrations/preloaded_outreach_context_manifest.py` (NEW) | All 35 fields; frozen dataclass; deterministic `manifest_hash`; includes `claim_permission_map`, `proof_mode`, `personalization_mode`, `omission_policy` | 12k | Not Started |
| **P6** | Static DAG YAML | `apps_lic/config/apps_lic_static_dag.yaml` (NEW) | 5-stage recipe: `load_manifest → validate_context → plan_message → compose_draft → seal_output` | 3k | Not Started |
| **P7** | Managed workflow dispatcher | `apps_lic/integrations/managed_workflow_dispatcher.py` (NEW) | L3-orchestrated apps_research dispatch; `RequestForBriefing` → `BriefingReady` or failure; fail-closed on failure | 12k | Not Started |
| **P8** | Managed DAG YAML + apps_research bridge | `apps_lic/config/apps_lic_managed_dag.yaml` (NEW); `apps_lic/integrations/apps_research_bridge.py` (NEW) | 8-stage recipe; bridge emits trace + audit refs; bridge uses registered public interface only | 13k | Not Started |
| **P9** | Research-failure fail-closed path | `apps_lic/integrations/managed_workflow_dispatcher.py` | `APPS_RESEARCH_FAILED`, `APPS_RESEARCH_EMPTY`, `APPS_RESEARCH_BLOCKED`, `APPS_RESEARCH_STALE`, `APPS_RESEARCH_WEAK_SUPPORT` → Exit V6 terminal | 5k | Not Started |
| **P10** | Fix spine_manifest route claims | `apps_lic/spine_manifest.yaml` | Must claim `R4_SINGLE_ACTION` and `R3R4_MANAGED_WORKFLOW`; remove `R3_grounded_read` for outreach path | 3k | Not Started |
| **P11** | Config files: intake_policy + l0_policy | `apps_lic/config/intake_policy.yaml`, `apps_lic/config/l0_policy.yaml` | U0 E1-E4 policy; L0 route matrix with invalid-schema-rejection path (exit code 2, not R5) | 5k | Not Started |
| **P12** | Config files: plan_rules + outreach schema | `apps_lic/config/lic_plan_rules.yaml`, `apps_lic/config/outreach_schema.json` | Schema includes `send_mode`, `omitted_claims`, `omission_policy`; plan rules include channel-specific arch config | 4k | Not Started |
| **P13** | lic_identity_resolver + lic_r5_policy | `apps_lic/integrations/lic_identity_resolver.py`, `apps_lic/integrations/lic_r5_policy.py` | Identity resolver: sender identity, not recipient; R5 policy: decision-only, all 14 reason codes | 6k | Not Started |
| **P14** | PA compiler wiring | `apps_lic/prompt_assembly/lic_pa_compiler.py` (NEW); refactor `message_planner.py` | Compiler: compose-only, 8 prompt slots (S0/I0/C0/U0/D0/E0/Y0/R0); includes `claim_permission_map` and `omission_policy`; never calls providers | 8k | Not Started |
| **P15** | Exit rubric YAML (corrected) | `apps_lic/config/exit_rubric.yaml` | Correct fail-closed scoping per feedback; add `ask_friction_score`, `antipattern_clean`, `proof_appropriate_for_recipient`, `personalization_mode_appropriate`, `asymmetric_insight_present` | 5k | Not Started |
| **P16** | Unsupported claim omission policy | `apps_lic/integrations/preloaded_outreach_context_manifest.py`; `apps_lic/config/exit_rubric.yaml` | `omit_unsupported` allows claim omission; `hitl_required` escalates; `fail_closed` blocks draft; omitted claims tracked in `OutreachDraft.omitted_claims` | 6k | Not Started |
| **P17** | send_mode restrictions | `apps_lic/config/outreach_schema.json`; `apps_lic/config/exit_rubric.yaml` | Allowed: `draft_only`, `review_required`, `send_ready_candidate`; Forbidden: `send_now`, `auto_send`, `connector_send`; Exit blocks forbidden modes | 4k | Not Started |
| **SE-P0a** | Anti-pattern detector (20 patterns) | `apps_lic/engines/outreach_antipattern_detector.py` (NEW); wire into pre-Exit path | Hard-fail on all 20 patterns; produces evidence refs and reason codes; fail-closed; does not rewrite content | 8k | Not Started |
| **SE-P0b** | Channel-length enforcement (configurable) | `apps_lic/config/lic_plan_rules.yaml` (extend); `apps_lic/L1_cognition/message_planner.py` | `channel_length_fit` fail-closed when word count > ceiling × tolerance (default 1.10); ceilings configurable per (channel, recipient_class, outreach_mode) | 5k | Not Started |
| **SE-P0c** | Scope-calibrated ask engine | `apps_lic/engines/scope_calibrated_ask_engine.py` (NEW) | Ask derived from (seniority × relationship_distance × hiring_posture × channel); `ask_friction_score` 0.0–1.0; bound-fail >0.5 unless override configured; reciprocity-front pattern | 7k | Not Started |
| **SE-P1a** | Recipient-trigger engine (scoped by recipient_class) | `apps_lic/engines/recipient_trigger_engine.py` (NEW) | EXEC/C_LEVEL/VP_ENG: require 1-2 person-level or company-strategy triggers where available; RECRUITER/SENIOR_TA: allow role/company/hiring-priority triggers; REFERRAL: allow relationship triggers; missing triggers → downgrade or omit, not hard-fail (unless policy says fail_closed) | 10k | Not Started |
| **SE-P1b** | Sender credibility card | `apps_lic/engines/sender_credibility_engine.py` (NEW); integrate into `HOP3SenderGroundingAgent.py` | `SenderCredibilityCard` with hash-bound claims; source_ref bound to `master_resume.json`; `factual_support` rejects unsourced claims | 8k | Not Started |
| **SE-P1c** | Proof appropriateness (scoped) | `apps_lic/engines/repo_proof_linker.py` (NEW) | Verifiable proof required for EXEC/C_LEVEL/CTO/VP_ENG/HIRING_MANAGER where technical claim depth is high; proof optional for RECRUITER/SENIOR_TA unless strong technical claim present; no proof requirement if no technical claims; proof formats: GitHub link, LinkedIn project, resume metric, public artifact, briefing/deck reference; do NOT force repo links into short LinkedIn messages | 7k | Not Started |
| **SE-P1d** | Asymmetric insight (config-gated) | `apps_lic/engines/asymmetric_insight_engine.py` (NEW) | `AsymmetricInsight` required ONLY when `asymmetric_insight_required: true` configured for that recipient_class and outreach_mode combination; simple recruiter follow-up does not require it | 7k | Not Started |
| **T-suite** | 24 sentinel tests + category tests | `tests/governance/test_apps_lic_*.py` | All 24 listed sentinel tests; existing governance suite stays green | 15k | Not Started |
| **V1** | Final verification + Notion writeback | governance suite + Notion | ADG no-bypass proof; Notion Plans row updated; SR_SUMMARY emitted | 5k | Not Started |

---

## Domain-Specific Architecture

apps_lic is an **outreach engine** for governed professional communication. Briefing is a prerequisite — same pattern as apps_rg's resume requiring a company brief.

| Dimension | apps_rg | apps_lic |
|-----------|---------|----------|
| **Prerequisite artifact** | Company brief | Recipient/company briefing (`PreloadedOutreachContextManifest`) |
| **Output** | Resume document (DOCX, JSON) | Message draft (plain text — `send_mode: draft_only` by default) |
| **Route if prerequisite present** | `R4_SINGLE_ACTION` | `R4_SINGLE_ACTION` |
| **Route if prerequisite missing** | `R5_FALLBACK` or `R3R4` for brief | `R3R4_MANAGED_WORKFLOW` (L3 runs apps_research) |
| **If prerequisite producer fails** | Fail closed through Exit | Fail closed through Exit — no generic draft |
| **R5 trigger** | Missing/stale company brief | Missing/stale briefing, apps_research failure, unsupported mandatory claims, high-friction ask, forbidden send_mode |
| **HITL posture** | Document release approval | Tone risk, senior exec low confidence, unsupported claims, proof appropriateness review |

### Canonical Briefing Prerequisite Rule

```
1. apps_lic receives request.
2. If PreloadedOutreachContextManifest with fresh briefing exists:
   → R4_SINGLE_ACTION → L2 drafts → Exit V6
3. If briefing is missing or stale:
   → R3R4_MANAGED_WORKFLOW → L3 dispatches apps_research
   → apps_research returns BriefingReady artifact
4. If apps_research succeeds:
   → convert to PreloadedOutreachContextManifest → resume R4_SINGLE_ACTION
5. If apps_research fails:
   → apps_lic fail-closed → no draft generated
   → terminal path through Exit V6 → exactly one X3 disposition
6. If request is for briefing only:
   → R3_SIMPLE_GROUNDED_READ → briefing artifact output only
   → no outreach draft generated
7. If request is structurally invalid:
   → U0 schema rejection (exit code 2)
   → NOT R5 — U0 rejection is not a routing failure
```

---

## Required Route Behavior (7 scenarios)

| Scenario | Route | Output | Exit Disposition |
|----------|-------|--------|-----------------|
| 1. Invalid request schema | U0 rejection (exit 2) | none | N/A — pre-routing |
| 2. Briefing-only request | `R3_SIMPLE_GROUNDED_READ` → C0/apps_research evidence path → optional PA/L2 synthesis → Exit | briefing artifact only (never outreach draft) | `ALLOW_FINISH` |
| 3. Outreach + fresh briefing | `R4_SINGLE_ACTION` | outreach draft | `ALLOW_FINISH` or `ESCALATE_HITL` |
| 4. Outreach + missing/stale briefing | `R3R4_MANAGED_WORKFLOW` | outreach draft (after research) | `ALLOW_FINISH` or `ESCALATE_HITL` |
| 5. apps_research fails | fail-closed via Exit V6 | none | `SAFE_ABSTAIN` |
| 6. Unsupported claim (omittable) | `R4_SINGLE_ACTION` with omission | outreach draft minus omitted claim | `ALLOW_FINISH` or `ESCALATE_HITL` |
| 7. Unsupported mandatory claim / high-friction ask / forbidden send_mode | R5 via Exit V6 | none | `SAFE_ABSTAIN` or `DENY` |
| 8. Research capability unavailable / policy disables research | R5 via Exit V6 | none | `SAFE_ABSTAIN` (reason: BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED) |

---

## PreloadedOutreachContextManifest (35 fields)

```python
@dataclass(frozen=True)
class PreloadedOutreachContextManifest:
    # Identity
    manifest_id: str
    request_id: str
    run_id: str
    trace_id: str
    
    # Policy/Blueprint binding
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    
    # Source references (hashes for lineage)
    user_profile_ref: str           # hash of user profile
    resume_ref: str                 # hash of resume snapshot
    target_role_ref: str            # hash of JD
    job_description_ref: str        # URI + hash of JD
    application_status: str         # "applied", "referred", "interviewing", "offer", "none"
    company_brief_ref: str          # hash of company briefing
    recipient_brief_ref: str        # hash of recipient research briefing
    relationship_context_ref: str   # hash of relationship context
    
    # Channel/mode selection
    channel: str                    # "email", "linkedin", "text"
    outreach_mode: str              # "cold", "warm", "referral", "followup"
    recipient_class: str            # RECRUITER, SENIOR_TA, HIRING_MANAGER, EXECUTIVE, C_LEVEL, VP_ENG, CTO, REFERRAL_CONTACT
    recipient_seniority: str        # IC, MANAGER, DIRECTOR, VP, C_LEVEL
    relationship_distance: str      # cold, warm, referral, known
    
    # Content governance
    source_items: List[SourceItem]          # citations for claims used
    origin_label_map: Dict[str, str]        # field → source label
    content_hashes: Dict[str, str]          # field → hash
    freshness_status: str                   # "fresh", "stale", "missing"
    unsupported_fact_flags: List[str]       # claims needing HITL review
    
    # Claim governance
    claim_permission_map: Dict[str, str]    # claim → "allowed"|"omit_unsupported"|"hitl_required"|"fail_closed"
    proof_mode: str                         # "none"|"resume_metric"|"repo_link"|"public_artifact"|"referral_context"|"company_brief"|"recipient_brief"
    personalization_mode: str               # "none"|"company"|"role"|"recipient"|"relationship"|"asymmetric"
    omission_policy: str                    # "omit_unsupported"|"hitl_required"|"fail_closed"
    
    # HITL gating
    personalization_confidence: float       # 0.0-1.0
    required_hitl_flags: List[str]          # e.g., ["senior_exec_recipient", "low_confidence"]
    
    # Audit
    manifest_hash: str                      # sha256 of serialized manifest
    audit_refs: List[str]                   # trace IDs for upstream evidence
```

### Manifest freshness semantics
- `fresh`: briefing produced within configured TTL (default: 7 days for executives, 30 days for recruiters)
- `stale`: briefing exists but past TTL → triggers R3R4_MANAGED_WORKFLOW
- `missing`: no briefing → triggers R3R4_MANAGED_WORKFLOW

---

## OutreachDraft Schema (L2 Output)

```python
@dataclass(frozen=True)
class OutreachDraft:
    # Content
    subject: str
    message_body: str
    
    # Routing metadata
    channel: str
    recipient_class: str
    relationship_posture: str           # cold, warm, referral, followup
    intended_next_step: str
    
    # Grounding
    claims_used: List[str]              # claims present in draft, all sourced
    unsupported_claims: List[str]       # claims NOT included (surfaced for HITL)
    omitted_claims: List[str]           # claims omitted per omission_policy
    personalization_confidence: float
    
    # Risk / HITL
    tone_risk_flags: List[str]
    hitl_questions: List[str]
    
    # Output governance
    signature_block: str
    metadata: Dict[str, Any]
    send_mode: str                      # "draft_only" | "review_required" | "send_ready_candidate"
    # FORBIDDEN send_mode values: "send_now", "auto_send", "connector_send"
```

---

## L0 Route Policy

L0 emits **exactly one** `RouteContract` from this decision matrix:

| Condition | RouteContract | Notes |
|-----------|---------------|-------|
| Structurally invalid request | U0 rejection (exit 2) | NOT R5 |
| Explicit briefing-only request | `R3_SIMPLE_GROUNDED_READ` | no outreach draft generated |
| `manifest.fresh == True` | `R4_SINGLE_ACTION` | standard outreach path |
| `manifest.stale == True` OR `manifest.missing == True` | `R3R4_MANAGED_WORKFLOW` | L3 runs apps_research first |
| `manifest.missing == True` AND outreach-type request AND research authorized | `R3R4_MANAGED_WORKFLOW` | governed path; auto-research authorized for valid outreach requests |
| `manifest.missing == True` AND research NOT authorized (policy/capability/registry failure) | R5 via Exit V6 | reason: BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED |
| `apps_research` fails (from R3R4) | R5 via Exit V6 | reason codes: APPS_RESEARCH_FAILED / EMPTY / BLOCKED / STALE / WEAK_SUPPORT |
| `personalization_confidence < 0.3` | R5 via Exit V6 | reason: LOW_CONFIDENCE |
| `senior_exec AND confidence < 0.5` AND no safe generic note | R5 via Exit V6 | reason: LOW_CONFIDENCE_SENIOR_EXEC |
| Forbidden `send_mode` in request | R5 via Exit V6 | reason: SEND_MODE_FORBIDDEN |
| `HIGH_FRICTION_ASK` detected pre-generation | R5 via Exit V6 | avoids wasting generation tokens |

### Forbidden in L0 (hard enforcement)

L0 may read config and manifests through approved read surfaces (e.g., `open(path, "r")`, `yaml.safe_load`, `json.load`). L0 must not perform write-mode file operations or durable state mutations.

```python
FORBIDDEN_IN_L0 = [
    # subprocess / OS execution
    "subprocess.run",
    "subprocess.Popen",
    "os.system",
    # direct research / provider access
    "apps_research",           # no direct import or call
    "openai",                  # no provider calls
    "anthropic",
    "google.generativeai",
    "boto3",                   # no bedrock
    "llama",                   # no local models
    # write-mode file operations (read-only config loads are allowed)
    'open(.*mode.*["\'].*[wax+]',  # open() with write/append/exclusive/update mode
    "Path.write_text",
    "Path.write_bytes",
    "json.dump.*durable",       # json.dump to durable path
    "yaml.dump.*durable",       # yaml.dump to durable path
    "shutil.copy",              # copy into durable or artifact paths
    "shutil.move",              # move into durable or artifact paths
    # direct L4 / durable state
    "l4_write",                 # direct L4 write APIs
    "durable_state_mutation",
    # fallback drafts
    "generic_fallback_draft",  # no best-effort drafts without briefing
]

# NOTE: AST scanner must distinguish write-mode open() from read-mode open().
# Tests must verify read-only config loads (e.g., open(path, "r")) do NOT trigger the gate.
```

---

## R5 Policy — All Reason Codes

`apps_lic/integrations/lic_r5_policy.py` is **decision-only** (no subprocess, no provider calls).

```python
class R5ReasonCode(str, Enum):
    BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED = "BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED"
    # ^ Only fires when: (a) tenant/run policy explicitly disables governed apps_research,
    #   (b) required research capability is unavailable, (c) registry/capability/sandbox
    #   binding for apps_research fails, or (d) run explicitly forbids research.
    #   Normal missing/stale briefing routes to R3R4_MANAGED_WORKFLOW — NOT this code.
    APPS_RESEARCH_FAILED                = "APPS_RESEARCH_FAILED"
    APPS_RESEARCH_EMPTY                 = "APPS_RESEARCH_EMPTY"
    APPS_RESEARCH_BLOCKED               = "APPS_RESEARCH_BLOCKED"
    APPS_RESEARCH_STALE                 = "APPS_RESEARCH_STALE"
    APPS_RESEARCH_WEAK_SUPPORT          = "APPS_RESEARCH_WEAK_SUPPORT"
    CONTEXT_MANIFEST_MISSING            = "CONTEXT_MANIFEST_MISSING"
    CONTEXT_MANIFEST_STALE              = "CONTEXT_MANIFEST_STALE"
    LOW_CONFIDENCE                      = "LOW_CONFIDENCE"
    LOW_CONFIDENCE_SENIOR_EXEC          = "LOW_CONFIDENCE_SENIOR_EXEC"
    UNSUPPORTED_MANDATORY_CLAIMS        = "UNSUPPORTED_MANDATORY_CLAIMS"
    INVALID_RECIPIENT_CLASS             = "INVALID_RECIPIENT_CLASS"
    HIGH_FRICTION_ASK                   = "HIGH_FRICTION_ASK"
    SEND_MODE_FORBIDDEN                 = "SEND_MODE_FORBIDDEN"
```

Every R5/fail-closed terminal path:
1. Builds a minimal `ExitReviewPacket` or terminal return packet
2. Calls Exit V6
3. Produces exactly one X3 disposition
4. Returns configured process exit code
5. Produces **no outreach draft**

---

## Managed Workflow Behavior (R3R4 Path)

```
U0 → L1 → L0 (emits R3R4_MANAGED_WORKFLOW)
    ↓
L3 Orchestrator receives RouteContract
    ↓
L3 dispatches RequestForBriefing to apps_research bridge
  (bridge uses registered public apps_research interface — never from L0)
    ↓
apps_research produces BriefingReady (with source lineage, hashes, freshness, confidence, gaps)
  OR apps_research failure
    ↓
[SUCCESS] Validate BriefingReady (see BriefingReady success criteria below)
          → Convert BriefingReady → PreloadedOutreachContextManifest
          → Resume apps_lic R4_SINGLE_ACTION → L2 → Exit V6
[FAILURE / INVALID] apps_lic fail-closed → Exit V6 → exactly one X3 disposition (SAFE_ABSTAIN)
          No generic draft, no fallback personalization
```

### BriefingReady Success Criteria

`apps_research` success does NOT mean "returned any object." `BriefingReady` is valid **only if all** of the following pass:

| Criterion | Failure → R5 Reason Code |
|-----------|---------------------------|
| `confidence_score >= configured threshold` (default 0.5) | `APPS_RESEARCH_WEAK_SUPPORT` |
| `freshness` is `"fresh"` or accepted by freshness policy | `APPS_RESEARCH_STALE` |
| All `required_fields` in `coverage` pass minimum coverage | `APPS_RESEARCH_EMPTY` |
| `sources` is non-empty | `APPS_RESEARCH_EMPTY` |
| `audit_refs` is non-empty | `APPS_RESEARCH_BLOCKED` |
| `content_hashes` is non-empty (present for briefing fields) | `APPS_RESEARCH_BLOCKED` |
| `origin_label_map` is present and non-empty | `APPS_RESEARCH_BLOCKED` |
| All entries in `unsupported_gaps` are classified under `claim_permission_map` as `omit_unsupported`, `hitl_required`, or `fail_closed` | `APPS_RESEARCH_WEAK_SUPPORT` |

If `BriefingReady` fails any criterion: map to the appropriate R5 reason code above and fail-closed through Exit V6. No outreach draft is generated.

### RequestForBriefing fields

```python
@dataclass(frozen=True)
class RequestForBriefing:
    request_id: str
    run_id: str
    trace_id: str
    recipient_id: str
    recipient_class: str
    company_id: str
    target_role_id: str
    briefing_depth: str             # "standard" | "deep" (for executives)
    required_fields: List[str]
    policy_hash: str
    blueprint_hash: str
    replay_key: str
    source_scope: str               # "recipient" | "company" | "both"
    freshness_requirement: str      # "fresh" | "any"
```

### BriefingReady fields

```python
@dataclass(frozen=True)
class BriefingReady:
    request_id: str
    run_id: str
    trace_id: str
    briefing_ref: str
    confidence_score: float
    coverage: Dict[str, bool]       # which required fields were found
    freshness: str                  # "fresh" | "stale" | "partial"
    sources: List[str]
    unsupported_gaps: List[str]     # fields not findable
    content_hashes: Dict[str, str]
    origin_label_map: Dict[str, str]
    audit_refs: List[str]
```

---

## Required Config Files

### A. l0_policy.yaml (L0)

```yaml
schema_version: "1.0"
app: apps_lic

route_decision:
  routes:
    - id: U0_REJECTION
      condition: "structurally_invalid_request"
      exit_code: 2
      note: "Schema validation failure — NOT R5"

    - id: R3_SIMPLE_GROUNDED_READ
      condition: "explicit_briefing_only_request"
      flow: "C0 or apps_research evidence path -> optional PA/L2 synthesis if needed -> Exit"
      note: "Produces governed briefing artifact only — NEVER an outreach draft"

    - id: R4_SINGLE_ACTION
      condition: "manifest.fresh"
      priority: 1

    - id: R3R4_MANAGED_WORKFLOW
      condition: "manifest.missing OR manifest.stale"
      priority: 2
      note: "L3 orchestrates apps_research; resume R4 on success"

    - id: R5_FALLBACK
      condition: "apps_research_failed OR send_mode_forbidden OR high_friction_ask OR unsupported_mandatory_claims"
      terminal: true
      routes_through_exit: true

forbidden_in_l0:
  - subprocess_execution          # subprocess.run, subprocess.Popen, os.system
  - apps_research_direct_import
  - apps_research_direct_call
  - provider_api_call             # openai, anthropic, gemini, bedrock, local model
  - file_write
  - generic_fallback_draft_generation
  - durable_state_mutation
```

### B. exit_rubric.yaml (V6 — corrected scoping)

```yaml
schema_version: "1.0"
app: apps_lic

dimensions:
  # ALWAYS fail-closed (no scoping)
  - id: no_fabricated_relationship
    weight: 2.0
    fail_closed: always

  - id: no_fabricated_application_status
    weight: 2.0
    fail_closed: always

  - id: no_confidential_leakage
    weight: 2.0
    fail_closed: always

  - id: antipattern_clean
    weight: 2.0
    fail_closed: always
    note: "hard-fail on any of the 20 forbidden patterns; produces evidence refs + reason codes"

  # Fail-closed for REMAINING claims in draft (unsupported claims may be omitted per omission_policy)
  - id: factual_support
    weight: 2.0
    fail_closed: remaining_claims_in_draft
    note: "claims omitted via omit_unsupported do NOT trigger factual_support failure"

  - id: no_unsupported_company_facts
    weight: 1.5
    fail_closed: remaining_claims_in_draft

  - id: no_unsupported_recipient_facts
    weight: 1.5
    fail_closed: remaining_claims_in_draft

  # Fail-closed for hard voice rules; contextual for soft rules
  - id: voice_compliance
    weight: 1.0
    hard_rules_fail_closed:
      - no_em_dash
      - plain_text_links_only
      - signature_rules_where_applicable
    soft_rules_contextual: true

  # Fail-closed when above ceiling × tolerance; contextual below
  - id: channel_length_fit
    weight: 1.0
    fail_closed_when: "word_count > ceiling * tolerance"
    tolerance: 1.10
    ceilings:
      email_executive_cold: 100
      email_executive_warm_referral: 120
      email_recruiter_hiring_manager_cold: 150
      email_recruiter_hiring_manager_warm: 200
      linkedin_any_cold: 60
      linkedin_any_warm_referral: 80
      referral_intro: 80

  # Contextual (not universally fail-closed)
  - id: tone_fit_seniority
    weight: 1.5
    contextual: true

  - id: clear_cta
    weight: 1.0
    contextual: true

  # ask_friction_score: contextual + fail-closed only above bound
  - id: ask_friction_score
    weight: 1.5
    fail_closed_when: "score > 0.5 AND NOT override_configured"
    contextual: true

  # Scoped by recipient_class + outreach_mode
  - id: proof_appropriate_for_recipient
    weight: 1.0
    contextual: true
    required_when:
      - recipient_class: [EXECUTIVE, C_LEVEL, CTO, VP_ENG, HIRING_MANAGER]
        AND: technical_claim_depth_high
        proof_formats: [github_link, linkedin_project, resume_metric, public_artifact, briefing_deck_ref]
    not_required_when:
      - recipient_class: [RECRUITER, SENIOR_TA]
        UNLESS: strong_technical_claim_present
      - no_technical_claims_in_draft

  - id: personalization_mode_appropriate
    weight: 1.0
    contextual: true

  # Required ONLY when configured for recipient_class + outreach_mode
  - id: asymmetric_insight_present
    weight: 1.5
    required_when: "asymmetric_insight_required == true in config for this (recipient_class, outreach_mode)"
    note: "simple recruiter follow-up does NOT require asymmetric insight"

x3_dispositions:
  - ALLOW_FINISH         # safe draft-only output
  - ESCALATE_HITL        # review-needed drafts
  - SAFE_ABSTAIN         # no safe output (research failure, mandatory claim failure)
  - REROUTE              # upstream remediation valid
  - DENY                 # unsafe or fabricated output
  - COMMIT_REQUEST       # approved reusable templates/patterns ONLY — never raw outreach drafts

hitl_policy:
  hard_substring_triggers: ["fabricated", "confidential", "send_now", "auto_send"]
  escalate_on_dim_fail: ["no_fabricated_relationship", "no_fabricated_application_status", "no_confidential_leakage"]
  escalate_on_low_score: ["factual_support"]
  executive_escalation: "recipient_class in [EXECUTIVE, C_LEVEL, CTO, VP_ENG] AND any_bound_fail"
```

### C. outreach_schema.json (E4 — extended)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OutreachRequest",
  "type": "object",
  "required": ["recipient_id", "channel", "outreach_mode"],
  "properties": {
    "recipient_id": {"type": "string", "minLength": 1},
    "channel": {"enum": ["email", "linkedin", "text"]},
    "outreach_mode": {"enum": ["cold", "warm", "referral", "followup"]},
    "recipient_class": {"enum": ["RECRUITER", "SENIOR_TA", "HIRING_MANAGER", "EXECUTIVE", "C_LEVEL", "VP_ENG", "CTO", "REFERRAL_CONTACT"]},
    "target_role_id": {"type": "string"},
    "company_id": {"type": "string"},
    "application_status": {"enum": ["applied", "referred", "interviewing", "offer", "none"]},
    "preloaded_context_manifest_path": {"type": "string"},
    "send_mode": {"enum": ["draft_only", "review_required", "send_ready_candidate"]},
    "omission_policy": {"enum": ["omit_unsupported", "hitl_required", "fail_closed"]},
    "personalization_claims": {"type": "array", "items": {"type": "string"}},
    "briefing_only": {"type": "boolean", "default": false}
  },
  "not": {
    "properties": {
      "send_mode": {"enum": ["send_now", "auto_send", "connector_send"]}
    }
  }
}
```

### D. Prompt Assembly Slots (lic_pa_compiler.py)

```python
PROMPT_SLOTS = {
    "S0": "system_and_governance",          # spine identity, constitutional constraints
    "I0": "outreach_rules",                 # channel rules, length ceilings, anti-patterns
    "C0": "verified_briefing_context",      # recipient/company brief — fenced as DATA
    "U0": "user_ask",                       # outreach request
    "D0": "origin_and_injection_fences",    # label all external text as data
    "E0": "approved_examples",              # approved prior messages (optional)
    "Y0": "approved_writing_preferences",   # voice/style preferences (optional)
    "R0": "output_schema",                  # OutreachDraft schema + send_mode restrictions
}

# PA Compiler contract:
# - compose only (no retrieval, no provider calls, no state mutation, no execution)
# - preserve origin labels from claim_permission_map
# - fence retrieved/company/recipient/user-provided text as DATA
# - include claim_permission_map and omission_policy in context
# - include channel length ceiling
# - include send_mode restrictions
```

---

## Signal Controls (W6 P0 + W7 P1)

### Anti-Pattern Detector (SE-P0a) — 15 default hard-fail patterns + configurable extension

**15 default hard-fail patterns (always enforced):**

1. `"I would love to learn more"` — passive seeker tone
2. `"I think I'd be a great fit"` — un-evidenced self-assessment
3. `"looking for new opportunities"` / `"open to new opportunities"` — status-deflating
4. `"quick question"` / `"picking your brain"` — low-status framing
5. `"I saw your company"` — scraper-tagged opener
6. `"I noticed you"` — scraper-tagged flattery
7. `"thought leader"` / `"luminary"` / `"stalwart"` — buzzword filler
8. `"would love to connect"` — generic LinkedIn cliché
9. Any em dash (`—` / `–`) — brand voice violation
10. `"I admire your work"` without specific artifact reference
11. `"I'm passionate about"` — filler
12. Compensation/salary/visa/relocation mention before first reply
13. >120 words before CTA (three-paragraph intro)
14. `"Please let me know if you have any questions"` — passive close
15. `"Hope this finds you well"` / `"Hope you're doing well"` — noise opener

**Configurable extension patterns:** added via `apps_lic/config/exit_rubric.yaml` `antipattern_extension_patterns` list. Extension patterns have the same hard-fail semantics as defaults.

**Detector behavior:** hard-fail on any matched pattern (default or extension); produces evidence refs + reason codes; does NOT rewrite content; explicit test fixtures supported.

### Channel-Length Enforcement (SE-P0b) — Configurable ceilings

| Channel | Recipient Class | Outreach Mode | Max Words |
|---------|----------------|---------------|-----------|
| email | EXECUTIVE, C_LEVEL | cold | 100 |
| email | EXECUTIVE, C_LEVEL | warm / referral | 120 |
| email | RECRUITER, HIRING_MANAGER | cold | 150 |
| email | RECRUITER, HIRING_MANAGER | warm | 200 |
| linkedin | any | cold | 60 |
| linkedin | any | warm / referral | 80 |
| referral_intro | — | — | 80 |

`channel_length_fit` fail-closed when word count > ceiling × 1.10 (configurable).

### Scope-Calibrated Ask Engine (SE-P0c)

- Ask calibrated to: recipient seniority, relationship distance, hiring posture, channel, outreach mode
- Executives cold → low-friction, reciprocity-front (offer perspective before asking)
- Recruiters → more direct ask acceptable
- Referral → make forwarding easy
- Avoid "discuss opportunities" as default CTA
- `ask_friction_score` 0.0–1.0; bound-fail if > 0.5 (unless override configured)

### Recipient Trigger Engine (SE-P1a) — Scoped requirements

**NOT universally mandatory.** Requirements by recipient_class:
- `EXECUTIVE, C_LEVEL, VP_ENG, CTO, HIRING_MANAGER` (cold): require 1-2 high-quality recipient-level or company-strategy triggers *where available*; if missing → downgrade `personalization_mode` or require HITL
- `RECRUITER, SENIOR_TA`: allow role, company, application-context, or hiring-priority triggers; do NOT fail because person-level triggers unavailable
- `REFERRAL_CONTACT`: allow relationship-context triggers
- If all triggers missing → omit unsupported personalization; fall back to role/company/value-led message per omission_policy; OR fail-closed if policy says `fail_closed`
- NEVER invent triggers

### Sender Credibility Card (SE-P1b)

Hash-bound claims from `master_resume.json`. `factual_support` rejects claims without `source_ref`. `SenderCredibilityCard` with `top_claims` (top-3 by `fit_score_for_recipient`) + `all_claims` for HITL review.

### Proof Appropriateness (SE-P1c) — Scoped requirements

**NOT universally mandatory.** Requirements:
- Required: EXEC/C_LEVEL/CTO/VP_ENG/HIRING_MANAGER + technical claim depth high + channel allows it
- Optional: RECRUITER/SENIOR_TA unless strong technical claim present
- Not applicable: no technical claims in draft, or short LinkedIn message where it hurts channel fit
- Proof formats: GitHub link, LinkedIn project link, resume metric, public artifact, briefing/deck reference

### Asymmetric Insight Generator (SE-P1d) — Config-gated

`asymmetric_insight_present` required **only when** `asymmetric_insight_required: true` in config for the `(recipient_class, outreach_mode)` combination. A simple recruiter follow-up is correct, short, and high-converting without asymmetric insight.

---

## L2 Bounded Artifact Set

L2 generates exactly one bounded artifact set:
- candidate outreach draft
- metadata
- `claims_used`
- `unsupported_claims`
- `omitted_claims`
- risk flags
- HITL questions
- sealed artifact receipt

**L2 must NOT:**
- Send messages
- Write durable state
- Invent relationships, application status, recipient facts, or company facts
- Include unsupported claims in the draft (must omit per `omission_policy`)
- Fail closed only when unsupported mandatory claims remain after omission attempt

---

## L4 / UWG — Durable Learning Policy

No raw outreach drafts automatically committed to memory.

**Approved durable learning (Exit → UWG → L4):**
- Approved outreach patterns
- Approved recipient-class rubric refinements
- Reusable templates
- Successful CTA patterns
- Sender proof cards
- Channel length policy updates
- User-approved voice rules

**Do NOT commit:**
- Raw generated drafts
- Raw recipient research
- Unsupported claims
- Transient HITL comments
- Failed outputs

---

## L6 Shadow Evaluation

L6 consumes completed-run exhaust only. L6 may evaluate: reply outcome (when provided), HITL decision quality, anti-pattern failure frequency, omitted claim patterns, successful proof modes, ask friction outcomes, recipient trigger effectiveness.

**L6 must NOT:** mutate current run, directly write L4, change L0 route behavior live, rescue failed research, or auto-promote learning without UWG approval.

---

## Test Categories and Sentinel Tests

### 24 Hard Sentinel Tests

```python
# Category 1: L0 architecture integrity
def test_apps_lic_l0_emits_exactly_one_route_contract(): ...
def test_apps_lic_l0_does_not_execute_apps_research(): ...
def test_apps_lic_l0_does_not_import_apps_research(): ...
def test_apps_lic_l0_does_not_call_providers(): ...
def test_apps_lic_l0_allows_read_only_config_open_but_blocks_write_mode_open(): ...
# ^ Verifies open(path, "r") / yaml.safe_load / json.load pass the AST gate;
#   open(path, "w"), Path.write_text, shutil.copy, json.dump-to-durable all fail.

# Category 2: Route behavior
def test_apps_lic_complete_briefing_routes_r4_single_action(): ...
def test_apps_lic_missing_briefing_routes_r3r4_managed_workflow(): ...
def test_apps_lic_apps_research_success_resumes_r4_single_action(): ...
def test_apps_lic_apps_research_failure_fails_closed_through_exit(): ...
def test_apps_lic_invalid_outreach_request_rejected_by_u0_not_r5(): ...
def test_apps_lic_briefing_missing_research_not_authorized_only_when_policy_blocks_research(): ...
# ^ BRIEFING_MISSING_RESEARCH_NOT_AUTHORIZED fires only when policy/capability/registry
#   blocks research; normal missing briefing → R3R4_MANAGED_WORKFLOW, NOT this code.
def test_apps_lic_r3_simple_grounded_read_briefing_only_no_outreach_draft(): ...
# ^ R3_SIMPLE_GROUNDED_READ with explicit briefing_only=True produces briefing artifact,
#   never an OutreachDraft; verifies output type at Exit.

# Category 3: Manifest integrity
def test_apps_lic_preloaded_outreach_context_manifest_has_hash_lineage_policy_blueprint_replay(): ...
def test_apps_lic_manifest_has_claim_permission_map_and_personalization_mode(): ...

# Category 4: Exit rubric behavior
def test_apps_lic_exit_blocks_unsupported_mandatory_personalization_claim(): ...
def test_apps_lic_exit_omits_unsupported_optional_claim(): ...
def test_apps_lic_exit_escalates_hitl_for_senior_exec_low_confidence(): ...

# Category 5: Write discipline
def test_apps_lic_no_direct_l4_write(): ...
def test_apps_lic_send_now_forbidden(): ...

# Category 6: Anti-pattern + channel
def test_antipattern_detector_default_15_patterns_and_config_extension(): ...
# ^ All 15 default patterns fail-closed; a configurable extension pattern added via
#   exit_rubric.yaml antipattern_extension_patterns also fails closed.
def test_channel_length_hard_ceiling_executive_cold_email(): ...
def test_scope_calibrated_ask_executive_cold_produces_low_friction_cta(): ...

# Category 7: Scoped signal controls
def test_recipient_trigger_requirements_scoped_by_recipient_class(): ...
def test_repo_proof_not_required_for_simple_recruiter_followup(): ...
def test_repo_proof_required_for_high_depth_exec_technical_claim(): ...
def test_asymmetric_insight_required_only_when_configured(): ...
def test_verifiable_proof_density_not_applicable_without_technical_claims(): ...

# Category 8: BriefingReady validation
def test_apps_lic_briefing_ready_requires_confidence_freshness_sources_hashes_and_audit_refs(): ...
# ^ BriefingReady with low confidence_score -> APPS_RESEARCH_WEAK_SUPPORT;
#   missing sources -> APPS_RESEARCH_EMPTY; missing audit_refs -> APPS_RESEARCH_BLOCKED;
#   stale freshness -> APPS_RESEARCH_STALE; unclassified gap -> APPS_RESEARCH_WEAK_SUPPORT.
```

### Test Category Summary

| Category | Count | File | What It Proves |
|----------|-------|------|----------------|
| L0 architecture | 5 | `test_apps_lic_l0_policy.py` | L0 decision-only; no subprocess; no research import; no providers; write-mode blocked, read-mode allowed |
| Route behavior | 7 | `test_apps_lic_route_behavior.py` | R4/R3R4/research-failure/U0-rejection/R3-briefing-only/research-not-authorized paths |
| Manifest integrity | 2 | `test_apps_lic_manifest.py` | 35-field contract; claim_permission_map; hash lineage |
| Exit rubric | 3 | `test_apps_lic_exit_rubric.py` | Mandatory claim block; optional omission; HITL escalation |
| Write discipline | 2 | `test_apps_lic_no_direct_l4_write.py` | No L4 write; send_now forbidden |
| Anti-pattern + channel | 3 | `test_apps_lic_signal_p0.py` | 15-default + extension detector; channel ceiling; ask friction |
| Scoped signal controls | 5 | `test_apps_lic_signal_p1.py` | Recipient trigger scoped; proof scoped; asymmetric insight config-gated |
| BriefingReady validation | 1 | `test_apps_lic_briefing_ready.py` | All 8 BriefingReady criteria; each failure maps to correct R5 code |

---

## ADG Hotspot Report

| Node | Layer | Fan-in | Archetype | Surface(s) | Impact |
|------|-------|--------|-----------|------------|--------|
| `apps_lic.__main__.main` | App-overlay | 4 | ORCHESTRATOR | Execution + Write | HIGH — single chokepoint for all W1 fixes |
| `GovernedLicRun.run_governed_e2e` | App-overlay | 2 | ORCHESTRATOR | Execution | HIGH — substrate integration point |
| `managed_workflow_dispatcher.dispatch` | App-overlay | 1 | ORCHESTRATOR | Execution + State | HIGH — R3R4 chokepoint; research failure exit |
| `preloaded_outreach_context_manifest.build_manifest` | App-overlay | 3 | STATE_NODE | State | MEDIUM — manifest lineage correctness |
| `message_planner.MessagePlanner.plan` | App-overlay (L1) | 1 | CENTRAL_DEPENDENCY | Execution | MEDIUM — planning surface feeds all L2 |
| `lic_r5_policy.evaluate` | App-overlay | 3 | SAFETY_GATEKEEPER | Security + Execution | HIGH — all 14 reason codes surface here |

---

## ADG Graph Layer Evidence

| Primitive | Use |
|-----------|-----|
| `mv_hotspot_centrality` | Confirm `__main__.main` and `GovernedLicRun` are centrality nodes before W1 edits |
| `mv_graph_chokepoint_bridges` | `governed_lic_run` is the chokepoint between apps_lic and spine |
| `mv_graph_reverse_dependency_hotspots` | `apps_research` reverse-deps from apps_lic — confirm only via L3 bridge |
| `flows_to` | `__main__.main` → `GovernedLicRun` → `GovernedAppRunner` |
| `emits_side_effect` | Pre-W1: check for `subprocess_spawn_apps_research` — must be REMOVED |
| `controls_flow` | `managed_workflow_dispatcher` → `apps_research_bridge` → `BriefingReady` path |
| `v_p1_layer_break_app_to_app` | apps_lic → apps_research direct edge must be L3-orchestrated only |
| `v_p2_silent_swallow` | Audit existing broad-except sites; no new ones in this plan |

---

## Gap Register

| Gap | Severity | Mitigation |
|-----|----------|------------|
| `apps_research` public API may not expose `BriefingReady` shape | HIGH | P8 discovery phase verifies API; if missing, extend apps_research as bounded public contract first |
| L3 `integrated_managed_workflow_real_run.py` unverified | HIGH | W3 blocked until apps_rg R4 entrypoint works end-to-end |
| `SpineRuntimeAdapter` may be insufficient for W2 | MEDIUM | P4 uses adapter; if stub insufficient, bypass with direct entrypoint call |
| apps_lic eval harness has 3 stub dims | LOW | W4 must wire real graders or keep `intentional_zero_dims` annotation |
| Scoped signal control config per (recipient_class, outreach_mode) | MEDIUM | P15 defines the config schema; SE-P1a/P1d implement the dispatch logic |

---

## Deferred Scope

```
DEFERRED_SCOPE: Real LLM-judge implementations for Exit rubric dims — stubs exist per apps-eval-harness-deferred-e4a1b7
DEFERRED_SCOPE: HITL freeze/review/re-clearance mechanism — design in W8; implementation in follow-up plan
DEFERRED_SCOPE: Production apps_research briefing quality validation — research quality gates out of scope
DEFERRED_SCOPE: Multi-recipient campaign batching — single-recipient only in this plan
DEFERRED_SCOPE: A/B test framework for message variants — L6 shadow eval in follow-up plan
DEFERRED_SCOPE: P2+P3 signal enhancements (narrative arc, archetype tone, multi-touch, resurfacing, mutual network) — tracked in apps-lic-signal-enhancements-p2p3-f4b8d1
```

---

## Author-Gate Queue Seed

```
AG_QUEUE_SEED: plan=apps-lic-canonical-spine-wireup-e7c2a5 id=ag-lic-research-auth title="R3R4 auth model: always-authorized vs policy-gated"
AG_QUEUE_SEED: plan=apps-lic-canonical-spine-wireup-e7c2a5 id=ag-lic-omission-default title="Default omission_policy: omit_unsupported vs hitl_required"
AG_QUEUE_SEED: plan=apps-lic-canonical-spine-wireup-e7c2a5 id=ag-lic-proof-scope title="Proof appropriateness gate: strict vs contextual-only"
```

---

## Verification Plan

1. Pre-W1: `adg_health` green; `mv_hotspot_centrality` confirms top-5 nodes
2. W1 complete: AST scan — zero `subprocess.run` in L0 path; zero direct `apps_research` imports from L0 files
3. W2 complete: manifest has all 35 fields; `manifest_hash` is deterministic (same inputs = same hash); R4 path executes static DAG
4. W3 complete: research-success → manifest built → R4 resumes; research-failure → fail-closed; terminal paths all call `_emit_r5_terminal_via_exit`
5. W4 complete: all config YAMLs pass schema validation; PA compiler does not call providers
6. W5 complete: omit_unsupported path works; send_now blocked at schema; Exit rubric has correct fail-closed scoping
7. W6 complete: 15 default patterns hard-fail; configurable extension pattern hard-fails when added to config; channel ceilings enforced; ask friction computed
8. W7 complete: recipient triggers scoped by recipient_class; simple recruiter test passes without asymmetric insight; proof not required when no technical claims
9. W8 complete: all 29 sentinel tests pass; existing governance suite green; ADG scans clean

---

## Acceptance Criteria Summary

- `apps_lic` rides canonical `U0 → L1 → L0 → L3 (optional) → L2 → Exit → UWG/L4 (optional) → L6`
- L0 is decision-only; forbidden list enforced by AST scan
- Briefing is a prerequisite artifact; no outreach draft without fresh briefing
- `R4_SINGLE_ACTION` if briefing present and fresh
- `R3R4_MANAGED_WORKFLOW` if briefing missing or stale; L3 runs apps_research
- apps_research failure → apps_lic fail-closed through Exit V6; no generic draft
- `R3_SIMPLE_GROUNDED_READ` produces briefing artifacts only — never outreach drafts
- No messages sent; `send_now` / `auto_send` / `connector_send` blocked at schema and Exit
- Exit emits exactly one X3 disposition; `COMMIT_REQUEST` never for raw outreach drafts
- Durable writes only through `Exit → UWG → L4`
- L6 learns from completed-run exhaust only
- All 29 sentinel tests pass; existing governance tests remain green
- Signal controls (anti-pattern, ask friction, recipient trigger, proof, asymmetric insight) are correctly scoped — not universally mandatory
- No unrelated broad refactors; no decorative abstractions

---

## PLAN_CREATED: apps-lic-canonical-spine-wireup-e7c2a5
