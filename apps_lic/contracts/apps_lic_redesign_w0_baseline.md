# apps_lic Redesign W0 Baseline And Contract Freeze

Source plan: apps-lic-redesign-refactor-plan-v2-consolidated, Notion page `37927693f55c8125bd57cdf3fc395b13`.

Date: 2026-06-08

Scope: Wave 0 only. This artifact documents the current runtime baseline and freezes the target contracts for later waves. It intentionally makes no runtime behavior changes.

## W0 Acceptance Mapping

| Acceptance item | W0 result |
| --- | --- |
| Current vector state and policy gaps documented | Covered in Vector State, Live Runtime Inventory, and Gap Summary. |
| Contracts explicit before code changes | Frozen in `apps_lic/config/domain_contract/apps_lic_redesign_w0_contracts.yaml`. |
| No runtime behavior changes | Only contract/docs/test artifacts were added. No runtime module or existing config behavior was changed. |

## Vector State Baseline

Current canonical apps_lic C0 behavior is inline-evidence only.

| Area | Current state | Gap against v2 design |
| --- | --- | --- |
| Canonical C0 binding | `apps_lic/runtime/bindings/c0_binding.py` builds `FinalEvidenceContract` from `ValidatedRequest.app_payload` only. | Does not retrieve public profile snippets, LinkedIn/about/background, public role descriptions, JD facts, or Chroma-backed fact vectors. |
| Chroma delegate | `apps_lic/integrations/chroma_delegate.py` exposes the sanctioned import site for `SovereignChromaClient`. | Delegate exists, but canonical C0 does not call it and there is no apps_lic vector readiness contract. |
| Vector evidence status | C0 explicitly marks dense/vector fields as not applicable. | W1+ must distinguish missing, stale, blocked, conflicted, and ready fact vectors. |
| C0.3 graph skills | `apps_lic/integrations/c0_graph_adapter.py` is a stub that returns unresolved anchors and empty neighbors. | Needs live proof graph traversal for approved sender proof points. |
| Retrieval profiles | `apps_lic/config/domain_contract/retrieval_profiles.yaml` defines allowed/prohibited sources and lineage expectations. | Profiles are not yet the source of a C0 readiness decision for apps_lic public-contact evidence. |

ADG note: the `adg_sqlite` MCP health check was unavailable in this Codex session because the transport was closed. W0 used local repository inspection as the fallback and records that limitation here.

## Live Runtime Inventory

| Layer | Current behavior | W0 gap |
| --- | --- | --- |
| U0 | `apps_lic/runtime/u0/adapter.py` validates `AppsLicIngressContractV1`, enforces read-only mode, blocks forbidden send actions, and passes app payload into the canonical contract. | U0 does not yet expose the v2 seed contract for public evidence URLs, manual brief mode, user asserted facts, JD facts, send mode, or recipient-class hints as non-authoritative hints. |
| Ingress contract | `apps_lic/contracts/apps_lic_ingress_contract_v1.py` supports request types `outreach_draft`, `campaign_batch`, and `dry_run`; channels include `linkedin`; outreach modes are `cold`, `warm`, and `reengagement`. | No canonical v2 message type taxonomy, application status, JD requirement gate, relationship/referral/prior thread contract, or derived recipient class contract. |
| L1 | `apps_lic/runtime/bindings/l1_binding.py` produces advisory route hints and support expectations from app payload. | L1 may estimate ambiguity/risk later, but currently does not emit v2 risk/reasoning signals or recipient-class derivation requirements. |
| L0 | `apps_lic/runtime/bindings/l0_binding.py` chooses R4/R3R4/R5 using the outreach route profile and Qwen vLLM constraints. | No v2 `sc_level`, `reasoning_intensity`, judge profile, recipient-class route, JD gate, or message-type policy matrix. |
| C0 | C0 creates data-only evidence from inline app payload and can return EMPTY/WEAK/PASS support. | C0 does not own public evidence retrieval, vector readiness, source lineage confidence for public contact snippets, recipient class derivation, or JD facts. |
| PA | `apps_lic/runtime/bindings/pa_binding.py` compiles model prompts for Qwen/vLLM with temperature `0.5`, JSON output, subject/body/qa_notes fields, and email-first defaults. | V2 needs whole-message LinkedIn/InMail candidates, higher temperature by risk band, approved proof IDs, and no prompt authority for unapproved claims. |
| L2 | `apps_lic/runtime/bindings/l2_binding.py` runs the HOP executor as one bounded L2 step. | V2 needs explicit SC-0 through SC-3 whole-message candidate paths and bounded repair that cannot add missing facts. |
| X2 / Exit | `apps_lic/runtime/bindings/exit_binding.py` uses shared Exit v6 X1/X2/X3Disposition with the outreach exit profile. | V2 needs apps_lic dispositions `clear_draft`, `review_required`, `blocked`, and `abstain`, while still preserving shared Exit authority. |
| X1D / judges | Existing judge and rubric files are not wired as a v2 risk-scaled LLM-as-judge panel for apps_lic. | V2 needs Claude Sonnet 4.6 as default independent LLM judge, and two independent LLM judge passes for CEO/C-level clear-draft decisions. |

## Message Type And Input Audit

V2 freezes five canonical message types for later implementation:

1. `general_intro`
2. `role_specific`
3. `trigger_based_insight`
4. `referral_ask`
5. `follow_up`

Current support is incomplete:

| Dimension | Current support | Gap |
| --- | --- | --- |
| `request_type` | `outreach_draft`, `campaign_batch`, `dry_run`. | These are execution/request shapes, not message-intent types. |
| `outreach_mode` | `cold`, `warm`, `reengagement`. | Missing explicit `referral` and `followup`; warm context is not enough to prove relationship. |
| `recipient_class` | User can supply `seniority_class`; separate archetype enum has only `C_LEVEL`, `EXECUTIVE`, `SENIOR_TA`, `RECRUITER`. | Recipient class must be mandatory but derived by C0 from evidence. U0 can seed title/headline/company/profile details only as evidence inputs or hints. |
| `application_status` | No first-class field in ingress contract. | Required before mentioning applied, referred, interviewing, or prior process status. |
| JD fields | No first-class JD facts contract with title and requisition number. | JD becomes mandatory after classification for role-specific recruiter/Senior TA/hiring-manager/applied/referral/follow-up-with-role cases. Recruiter and Senior TA role-specific messages require `position_name` and `requisition_number`. |
| Relationship/referral/prior thread | No first-class evidence contract for these contexts. | Warm/referral/follow-up language must fail closed or require review if support is missing. |

## LinkedIn Length Policy Audit

Current LinkedIn enforcement has useful broad caps but is too coarse for the v2 scope.

| Source | Current policy | Gap |
| --- | --- | --- |
| `apps_lic/engines/channel_length_enforcer.py` | LinkedIn caps are broadly `60` words for cold and `80` words for warm/referral/follow-up, independent of recipient class and message type. | V2 needs sentence, word, and character budgets by message type and recipient class. |
| `apps_lic/types/recipient_archetype_types.py` | Archetype templates are email-like: recruiter 140-170 words, senior TA 150-190, executive 160-220, C-level 190-230. | These conflict with LinkedIn/InMail copy and should not govern v2 LinkedIn messages. |

Frozen W0 target budgets are in the YAML contract. They favor concise LinkedIn/InMail drafts while allowing slightly more room for executive insight and role-specific context.

## Reasoning Intensity And Judge Audit

Current apps_lic behavior does not have a complete v2 reasoning intensity implementation.

| Area | Current state | Gap |
| --- | --- | --- |
| Reasoning intensity module | No active `apps_lic.policy.reasoning_intensity` module is present in this worktree baseline. | W1+ must add a policy that scales reasoning by risk rather than by default. |
| SC paths | Current L2 runs the HOP pipeline, not explicit SC-0 to SC-3 whole-message candidate paths. | Need SC path selection based on message type, evidence strength, and recipient class. |
| Generator temperature | PA uses temperature `0.5`. | V2 needs higher temperature for candidate generation, bounded by evidence and risk. |
| Deterministic gates | Exit v6 supplies shared gating, but v2 apps_lic hard-gate definitions are not explicit. | Need X2 gates for schema, length, JD facts, evidence support, relationship claims, no-send, and prompt-injection neutralization. |
| LLM judge | No risk-scaled Claude Sonnet 4.6 judge contract exists for apps_lic. | Need X1D as advisory after X2, with Claude Sonnet 4.6 and extra depth for CEO/C-level. |

## Frozen V2 Design Rules

These rules are contractually frozen for later waves:

- C0 owns public evidence, source lineage, fact-vector readiness, recipient-class derivation, and public role ownership signals.
- Ingestion is separate from inference. C0 may request governed ingestion when evidence is missing or stale, but it must not silently browse the web or write vectors during generation.
- C0.3 owns approved sender proof graph traversal and returns only approved proof points with IDs, source lineage, and permission decisions.
- JD is optional globally but required after classification for role-specific recruiter, Senior TA, hiring manager, applied-role, referral-with-role, or follow-up-with-role messages.
- Recruiter and Senior TA role-specific LinkedIn messages require `position_name` and `requisition_number` from JD facts.
- L2 generates whole-message candidates only; it does not assemble header/body fragments as separate generation products.
- More reasoning can improve wording and selection, but cannot override missing C0 evidence, L0 route authority, X2 gates, no-send policy, or Exit clearance.
- X2 gates run before X1D. X1D cannot clear a draft that X2 blocked.
- Claude Sonnet 4.6 is the default independent LLM-as-judge for X1D. CEO/C-level clear-draft decisions require two LLM judge passes.
- Auto-send remains disabled. Exit may clear a draft for review/use, require review, block, or abstain; it may not send.

## W0 Gap Summary

1. No apps_lic Chroma/vector readiness baseline is wired into canonical C0.
2. No governed on-demand opportunity ingestion path exists for contact/company/JD facts.
3. No live C0.3 proof graph selection exists for sender proof points.
4. Recipient class is not mandatory-derived from C0 public evidence.
5. Message type taxonomy is not represented in ingress, routing, generation, or tests.
6. JD fields are not first-class and no post-classification JD gate exists.
7. LinkedIn length policy is broad by outreach mode and not optimized by message type/recipient class.
8. L2 uses a HOP pipeline instead of explicit SC whole-message candidate paths.
9. PA temperature and prompt shape are conservative and email-oriented relative to the v2 LinkedIn design.
10. X1D judge policy is not risk-scaled and does not use Claude Sonnet 4.6 as the frozen default.

## W0 Verification Boundary

W0 verification is limited to artifact presence and contract parseability. Runtime behavior is intentionally unchanged and should not be asserted as implemented until later waves.
