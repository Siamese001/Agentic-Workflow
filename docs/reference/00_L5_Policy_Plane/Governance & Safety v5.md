========================================================================================================================================================================================
[ ABOVE GOVERNANCE & SAFETY CONTEXT | governed packet enters from routing/orchestration ]
[ Library analogy: Patron arrives at the Commandant's desk with a routed reading request, a plan slip, and requested powers ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INVARIANT: no execution, mutation, external model call, tool invocation, connector access, HITL modification, or durable write proceeds without L5 certification.
INVARIANT: L5 governs authority and safety. It does not retrieve evidence, assemble prompts, execute tools, write state, or promote learning.
INVARIANT: every certification binds active policy, structure blueprint, registry digests, origin-trust labels, principal chain, capability_token, sandbox envelope, and replay envelope.
INVARIANT: hard_constraint breaches are not remediable. They terminate as REJECT unless a new upstream packet is created and re-entered through L5.
INVARIANT: every human modification is treated as untrusted data until re-cleared by L5.
INVARIANT: every out-of-band calibration, red-team, audit, or learning signal affects future policy versions only. It cannot mutate the current certified run.
INVARIANT: no silent fallback. If a provider, tool, connector, model, policy, or registry target changes, L5 must re-certify the new lane.
========================================================================================================================================================================================
                                                                    │
                                                               [ walks in ]
                                                                    ▼
========================================================================================================================================================================================
[ GOVERNANCE & SAFETY | L5 ENFORCEMENT PLANE | v5 ]
[ v5 = v4 preserved + gross-detail expansion for runtime gates, regression protection, identity/capability scope, HITL, egress, audit, and replay ]
========================================================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G0: GOVERNANCE ENTRY CONTRACT | "What exactly is being submitted to the Commandant?"                                                                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ INPUT PACKET TYPES                                                                                                                                                           │
│ - RequestEnvelope from Intake: normalized user/task artifact, request_id, tenant, trace_root, caller_scope_baseline.                                                          │
│ - L1PlanContract: task_spec, query_spec, proposed_route, confidence, assumptions, constraints, unresolved gaps.                                                               │
│ - L0RouteContract: route_id, execution_form, risk_tier_hint, fallback_chain, freshness_class, cache_policy, SLO, telemetry_keys, HMAC signature.                              │
│ - L3StepContract: current bounded workflow node, dependencies satisfied, retry budget, current step inputs, policy_hash, blueprint_hash.                                      │
│ - L2ExecutionRequest: tool/model/action spec, arguments, capability request, sandbox request, expected artifact.                                                              │
│ - HITLReentryPacket: bounded human review packet, human proposed diff, reason_code, evidence bundle, prior decision trace.                                                    │
│ - ExitDispositionRequest: sealed L2/L3 artifact, execution trace, state diff proposal, commit request, deny/reroute/escalate candidate.                                      │
│                                                                                                                                                                              │
│ REQUIRED FIELDS                                                                                                                                                              │
│ - request_id, trace_id, run_id, tenant_id, caller_id or service principal.                                                                                                    │
│ - origin_trust_manifest for all inbound text, retrieved content, tool output, human input, and prior artifacts.                                                               │
│ - policy_hash, blueprint_hash, registry_digest_set, route_contract_hmac, and replay_key candidate.                                                                            │
│ - declared side_effect_class: NONE | READ | MODEL_CALL | TOOL_CALL | NETWORK | MEMORY | WRITE_PROPOSAL | EXTERNAL_COMMIT.                                                    │
│ - requested authority: read_scope, tool_scope, model_scope, connector_scope, network_scope, write_scope, human_review_scope.                                                  │
│                                                                                                                                                                              │
│ FAST REJECT CONDITIONS                                                                                                                                                       │
│ - missing route contract when authority is requested.                                                                                                                        │
│ - missing origin labels for content entering prompt assembly or L2.                                                                                                           │
│ - missing principal chain for any delegated agent, tool, model, connector, or human re-entry.                                                                                 │
│ - missing or stale registry digest for an agent/tool/model/connector/prompt referenced by the packet.                                                                         │
│ - action claims read-only but contains write intent, external call intent, memory mutation intent, or broad filesystem/network access.                                        │
│                                                                                                                                                                              │
│ OUTPUT                                                                                                                                                                       │
│ - GovernanceReviewRequest = normalized, typed, bounded review packet ready for G1 triage.                                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                                    │ [ review packet ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G1: GOVERNANCE INVOCATION | Front Desk Triage                                                                                                                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                                                                      │
│ - Decide which enforcement lane applies before any power is granted.                                                                                                         │
│ - Establish the minimum governance depth required for this packet.                                                                                                           │
│ - Detect obvious bypass, injection, spoofing, or mismatch before deeper review.                                                                                              │
│                                                                                                                                                                              │
│ MODE SELECTION                                                                                                                                                               │
│ - STATIC_CHECK: repo/code/doc structure, policy package, registry update, prompt template, connector config, CI candidate.                                                    │
│ - RUNTIME_CHECK: live route, model/tool invocation, L2 execution, external egress, current-run exit.                                                                          │
│ - HUMAN_REENTRY: human approval, human modification, SME review, operator override, customer-provided correction.                                                            │
│ - COMMIT_REVIEW: durable state mutation proposal, memory update, policy promotion, catalog change, workflow checkpoint write.                                                │
│ - INCIDENT_REVIEW: anomaly, injection hit, sandbox breach, replay failure, suspicious cost spike, provider drift, audit reconstruction.                                      │
│                                                                                                                                                                              │
│ RISK TIER BAND ASSIGNMENT                                                                                                                                                    │
│ - LOW: read-only, no sensitive data, no external action, no durable write, stable cached answer, reversible and low blast radius.                                             │
│ - MODERATE: tool/model call, internal network, sensitive-ish context, workflow step, grounded answer with citations, bounded connector access.                               │
│ - HIGH: irreversible action, financial/legal/medical/employment impact, privileged connector, customer-facing policy change, PII/secret exposure risk, broad write scope.     │
│ - CRITICAL: credential access, cross-tenant risk, production mutation, policy bypass attempt, jailbreak success path, unbounded autonomous workflow, incident containment.     │
│                                                                                                                                                                              │
│ TRIAGE CHECKS                                                                                                                                                                │
│ - declared mode matches actual packet content.                                                                                                                               │
│ - route_id and execution_form match requested power.                                                                                                                         │
│ - risk_tier_hint from L0 does not understate actual authority requested.                                                                                                      │
│ - side_effect_class matches arguments and tool/model/connector registry metadata.                                                                                             │
│ - presence of prompt injection patterns, role override attempts, hidden instructions, suspicious URLs, secrets, or credential-like strings.                                  │
│ - shadow_discovery_probe detects attempts to evade governance through alternate tools, "just do it", hidden text, markdown injection, or connector smuggling.               │
│                                                                                                                                                                              │
│ OUTPUT                                                                                                                                                                       │
│ - governance_mode: STATIC_CHECK | RUNTIME_CHECK | HUMAN_REENTRY | COMMIT_REVIEW | INCIDENT_REVIEW.                                                                           │
│ - risk_tier_band: LOW | MODERATE | HIGH | CRITICAL.                                                                                                                          │
│ - review_depth: FAST_PATH | STANDARD | ENHANCED | LOCKDOWN.                                                                                                                  │
│ - triage_flags: injection_suspected, scope_mismatch, identity_gap, registry_gap, side_effect_mismatch, hard_constraint_candidate.                                            │
│ - next_lane: STATIC_LANE | RUNTIME_LANE | BOTH_LANES | DECISION_RAIL_REJECT.                                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ hands slip ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2: AUTHORITY CONTEXT RESOLUTION | The Master Charter Desk                                                                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                                                                      │
│ - Resolve the official rulebook before judging anything.                                                                                                                     │
│ - Prevent ad-hoc policy, stale config, hidden tool assumptions, or implied authority from entering runtime.                                                                   │
│                                                                                                                                                                              │
│ ACTIVE POLICY SET                                                                                                                                                            │
│ - policy_bundle_id and policy_hash.                                                                                                                                          │
│ - policy_version_current and policy_effective_time.                                                                                                                          │
│ - refusal taxonomy and exception taxonomy.                                                                                                                                   │
│ - hard_constraint tags: true | false.                                                                                                                                        │
│ - remediable tags: true | false.                                                                                                                                             │
│ - risk tier mapping table.                                                                                                                                                   │
│ - HITL requirements and approval thresholds.                                                                                                                                 │
│ - sector overlays: financial, healthcare, legal, HR, education, government, regulated data, customer-facing action.                                                          │
│ - standards_fingerprint: NIST_AI_RMF | ISO_42001 | CoSAI_baselines | SOC2_controls | internal overlays.                                                                     │
│                                                                                                                                                                              │
│ STRUCTURE BLUEPRINT                                                                                                                                                          │
│ - allowed layer boundaries: U0, L1, L0, C0, PA, L3, L2, L5, Exit, HITL, UWG, L4, L6.                                                                                          │
│ - layer authority matrix: who can read, propose, execute, approve, commit, observe.                                                                                           │
│ - route topology: R1A exact cache, R1B semantic cache, R3 grounded read, R4 action, managed workflow, R5 fallback.                                                           │
│ - invariant map: no L2 direct write, no L6 current-run mutation, no C0 answer generation, no PA retrieval, no HITL bypass.                                                   │
│                                                                                                                                                                              │
│ FOUR SIBLING REGISTRIES                                                                                                                                                      │
│ - Agent Registry                                                                                                                                                             │
│   • agent_id, owner, allowed_models, tool roster, connector roster, execution_mode, risk ceiling, registry_digest.                                                           │
│   • max delegation depth, allowed specialist handoffs, allowed memory surfaces, allowed policy posture.                                                                       │
│                                                                                                                                                                              │
│ - Tool Registry                                                                                                                                                              │
│   • tool_id, schema, auth scopes, side-effect class, risk tier, approval authority, argument constraints, timeout, cost guard.                                                │
│   • allowed callers, sandbox requirements, reversible vs irreversible, read/write class, audit fields required.                                                              │
│                                                                                                                                                                              │
│ - Prompt Registry                                                                                                                                                            │
│   • prompt_id, version, lineage, rollback policy, stable prefix, slot map, exemplar eligibility, schema binding, policy compatibility.                                       │
│   • allowed model families, allowed task classes, prompt injection posture, disallowed dynamic fields.                                                                        │
│                                                                                                                                                                              │
│ - MCP Connector Registry                                                                                                                                                     │
│   • connector_id, enterprise allowlist, one-time vs durable grant, tenant/data sensitivity, network egress class, scopes, expiration.                                        │
│   • connector owner, audit requirement, allowed target domains, credential handling policy, data retention class.                                                            │
│                                                                                                                                                                              │
│ DATA AUTHORITY RESOLUTION                                                                                                                                                    │
│ - supply_chain_digest for retrieved, uploaded, generated, human-authored, and tool-returned content.                                                                          │
│ - RAG-source vetting fingerprint: source authority, freshness, provenance, ACL, tenant, region, document version.                                                            │
│ - origin-trust posture: system > policy > registry > developer/admin > retrieved/tool output/human input > user task text as intent only.                                    │
│ - quarantine status for any content that includes instructions, hidden text, scripts, URLs, macros, or suspicious formatting.                                                │
│                                                                                                                                                                              │
│ IDENTITY PROPAGATION                                                                                                                                                         │
│ - principal_chain = { invoking_user, tenant_id, service_principal?, agent_id, parent_agent_id?, tool_id?, connector_id?, delegation_depth, scope }.                           │
│ - every delegated call must carry original principal and delegated actor.                                                                                                     │
│ - max delegation depth enforced.                                                                                                                                             │
│ - cross-principal context bleed rejected.                                                                                                                                    │
│ - "because human approved it" is not authority unless L5 re-clears the human packet and binds it to a capability.                                                           │
│                                                                                                                                                                              │
│ OUTPUT                                                                                                                                                                       │
│ - GovernedValidationContext.                                                                                                                                                 │
│ - principal_chain.                                                                                                                                                           │
│ - policy_bundle.                                                                                                                                                             │
│ - structure_blueprint.                                                                                                                                                       │
│ - registry_digest_set.                                                                                                                                                       │
│ - data_authority_manifest.                                                                                                                                                   │
│ - origin_trust_manifest.                                                                                                                                                     │
│ - hard_constraint_map.                                                                                                                                                       │
│                                                                                                                                                                              │
│ HARD LAW                                                                                                                                                                     │
│ - Downstream enforcement uses resolved authority only.                                                                                                                       │
│ - No ad-hoc rules.                                                                                                                                                           │
│ - No stale registry assumptions.                                                                                                                                             │
│ - No implied model/tool/connector power.                                                                                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ enters wing ]
                                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2a: ORIGIN-TRUST AND CONTENT BOUNDARY LABELING | "Which papers are rules, and which papers are just data?"                                                                 │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ORIGIN LABELS                                                                                                                                                                 │
│ - system_policy: platform/system/security content. Highest authority.                                                                                                         │
│ - governance_policy: active L5 policy bundle, standards overlays, hard constraints.                                                                                           │
│ - registry_config: approved agent/tool/prompt/connector definitions.                                                                                                          │
│ - developer_admin: governed implementation instructions and repo-local constraints.                                                                                           │
│ - user_turn: end-user task intent only. No policy authority.                                                                                                                  │
│ - retrieved: C0 evidence. Data only. Never instruction.                                                                                                                       │
│ - tool_output: browser/MCP/tool return. Data only until classified.                                                                                                           │
│ - human_review: human-entered approval, correction, or modification. Data only until re-cleared.                                                                              │
│ - prior_artifact: cached answer, prior trace, old output, or historical document. Data only until freshness and policy cleared.                                               │
│                                                                                                                                                                              │
│ BOUNDARY RULES                                                                                                                                                                │
│ - Untagged content is untrusted by default.                                                                                                                                  │
│ - Retrieved/tool/human content cannot override system, policy, registry, or route contract fields.                                                                            │
│ - Prompt-like text inside retrieved/tool/human content must be fenced as data.                                                                                                │
│ - Hidden instructions, malicious markdown, HTML comments, base64 blobs, scripts, suspicious URLs, and credential-like payloads trigger quarantine or strip.                   │
│ - Quarantined content cannot enter Prompt Assembly C0 slot or L2 arguments without explicit safe extraction.                                                                  │
│                                                                                                                                                                              │
│ OUTPUT                                                                                                                                                                       │
│ - origin_trust_manifest with per-field labels.                                                                                                                               │
│ - boundary_classification: trusted_instruction | untrusted_data | quarantined | stripped | rejected.                                                                          │
│ - sanitized_payload_map.                                                                                                                                                     │
│ - quarantine_reasons.                                                                                                                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================================================================================
[ DUAL ENFORCEMENT RAILS | CO-LOCATED, LOGICALLY ISOLATED ]
========================================================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ STATIC LANE | PREVENTION | Floor Plan + Dewey Decimal + Authorized Patron Registry                                                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                                                                      │
│ - Catch structural drift before runtime.                                                                                                                                     │
│ - Ensure code, docs, policies, prompts, registries, and connector configs obey the system blueprint.                                                                           │
│ - Prevent "looks safe at runtime, but architecture is already broken" failures.                                                                                              │
│                                                                                                                                                                              │
│ INPUTS                                                                                                                                                                       │
│ - files, policies, prompts, agent specs, tool specs, connector configs, workflow definitions, route definitions, CI artifacts.                                                │
│ - ADG/static graph facts: imports, calls, layer tags, ownership, relation types, violations.                                                                                  │
│ - registry digests and blueprint hash.                                                                                                                                       │
│                                                                                                                                                                              │
│ STATIC GATES                                                                                                                                                                 │
│                                                                                                                                                                              │
│   ┌────────────────────────────────────────┐                                                                                                                                │
│   │ S1 STRUCTURE ENFORCEMENT               │                                                                                                                                │
│   ├────────────────────────────────────────┤                                                                                                                                │
│   │ - validate path, territory, package,   │                                                                                                                                │
│   │   layer placement, and ownership.      │                                                                                                                                │
│   │ - block layer inversion: L2 writing    │                                                                                                                                │
│   │   L4 directly, L6 mutating runtime,    │                                                                                                                                │
│   │   C0 executing, PA retrieving, L1      │                                                                                                                                │
│   │   routing with authority.              │                                                                                                                                │
│   │ - verify allowed dependencies and      │                                                                                                                                │
│   │   forbidden imports.                   │                                                                                                                                │
│   │ - detect hidden egress paths and       │                                                                                                                                │
│   │   bypass wrappers.                     │                                                                                                                                │
│   │ - output: structure_violation_report.  │                                                                                                                                │
│   └────────────────────┬───────────────────┘                                                                                                                                │
│                        │ [ structural metadata ]                                                                                                                            │
│                        ▼                                                                                                                                                     │
│   ┌────────────────────────────────────────┐                                                                                                                                │
│   │ S2 CLASSIFICATION KERNEL               │                                                                                                                                │
│   ├────────────────────────────────────────┤                                                                                                                                │
│   │ - AST type classification.             │                                                                                                                                │
│   │ - dual-tag conflict detection.         │                                                                                                                                │
│   │ - classify file/function/symbol as     │                                                                                                                                │
│   │   planner, router, retriever, assembler│                                                                                                                                │
│   │   executor, evaluator, writer, policy. │                                                                                                                                │
│   │ - detect "hybrid authority" smells:    │                                                                                                                                │
│   │   one symbol that both executes and     │                                                                                                                                │
│   │   commits, retrieves and answers,       │                                                                                                                                │
│   │   observes and mutates.                 │                                                                                                                                │
│   │ - output: type_ssot_report.             │                                                                                                                                │
│   └────────────────────┬───────────────────┘                                                                                                                                │
│                        │ [ classified artifacts ]                                                                                                                           │
│                        ▼                                                                                                                                                     │
│   ┌────────────────────────────────────────┐                                                                                                                                │
│   │ S3 REGISTRY VALIDATION x4              │                                                                                                                                │
│   ├────────────────────────────────────────┤                                                                                                                                │
│   │ - Agent Registry digest match.         │                                                                                                                                │
│   │ - Tool Registry schema/scope match.    │                                                                                                                                │
│   │ - Prompt Registry slot/order match.    │                                                                                                                                │
│   │ - MCP Connector Registry allowlist.    │                                                                                                                                │
│   │ - detect orphan tools, shadow prompts, │                                                                                                                                │
│   │   unregistered agents, broad scopes,   │                                                                                                                                │
│   │   stale connector grants.              │                                                                                                                                │
│   │ - output: registry_validation_report.  │                                                                                                                                │
│   └────────────────────┬───────────────────┘                                                                                                                                │
│                        │ [ registry consistency ]                                                                                                                           │
│                        ▼                                                                                                                                                     │
│   ┌────────────────────────────────────────┐                                                                                                                                │
│   │ S4 POLICY PACKAGE INTEGRITY            │                                                                                                                                │
│   ├────────────────────────────────────────┤                                                                                                                                │
│   │ - verify policy bundle hashes.         │                                                                                                                                │
│   │ - verify hard_constraint flags.        │                                                                                                                                │
│   │ - verify refusal taxonomy and sector   │                                                                                                                                │
│   │   overlays resolve.                    │                                                                                                                                │
│   │ - detect dangling policy refs, stale   │                                                                                                                                │
│   │   risk tiers, missing escalation paths.│                                                                                                                                │
│   │ - output: policy_integrity_report.     │                                                                                                                                │
│   └────────────────────┬───────────────────┘                                                                                                                                │
│                        │ [ policy consistency ]                                                                                                                             │
│                        ▼                                                                                                                                                     │
│   ┌────────────────────────────────────────┐                                                                                                                                │
│   │ S5 STATIC REGRESSION PROTECTION        │                                                                                                                                │
│   ├────────────────────────────────────────┤                                                                                                                                │
│   │ - compare against golden architecture  │                                                                                                                                │
│   │   snapshots.                           │                                                                                                                                │
│   │ - detect newly introduced bypasses.    │                                                                                                                                │
│   │ - detect deleted gates, weakened       │                                                                                                                                │
│   │   defaults, relaxed scopes, missing    │                                                                                                                                │
│   │   replay metadata, missing audit.      │                                                                                                                                │
│   │ - require explicit ADR/waiver for      │                                                                                                                                │
│   │   policy weakening.                    │                                                                                                                                │
│   │ - output: static_regression_report.    │                                                                                                                                │
│   └────────────────────┬───────────────────┘                                                                                                                                │
│                        │                                                                                                                                                     │
│                        ▼                                                                                                                                                     │
│   STATIC OUTPUTS                                                                                                                                                             │
│   - PASS: structure and registry posture certified.                                                                                                                          │
│   - REJECT: hard structural violation, missing registry authority, hidden egress, direct write path, policy weakening without approval.                                      │
│   - REMEDIATE: safe fix suggestion only when no hard_constraint is breached.                                                                                                  │
│                                                                                                                                                                              │
│ STATIC HARD LAW                                                                                                                                                              │
│ - The static lane can prevent unsafe runtime packets from existing.                                                                                                          │
│ - It cannot approve live execution by itself. Runtime packets still traverse runtime gates.                                                                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                                                                    │
                                                              [ drops down ]
                                                                    ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ RUNTIME LANE | CONTAINMENT | Layered Guardrails + Handoff Validation + Restricted Section + Interlibrary Loan Exit                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ PURPOSE                                                                                                                                                                      │
│ - Gate the live packet before it reaches L2, a provider, a tool, a connector, a human reviewer, or UWG.                                                                       │
│ - Constrain blast radius even if planning, retrieval, prompt assembly, tool output, or a human packet is compromised.                                                        │
│ - Ensure every action is authorized, scoped, logged, replayable, and reversible where required.                                                                               │
│                                                                                                                                                                              │
│ RUNTIME PIPELINE                                                                                                                                                             │
│                                                                                                                                                                              │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R1 CLIENT-LEVEL UNIVERSAL GUARDRAIL BANK                                                                                                                         │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Runs for every call, regardless of agent, task, model, route, or tool.                                                                                             │     │
│     │                                                                                                                                                                  │     │
│     │ Checks:                                                                                                                                                          │     │
│     │ - moderation and high-harm content.                                                                                                                              │     │
│     │ - secrets, API keys, passwords, tokens, private keys, credentials, connection strings.                                                                            │     │
│     │ - URL/domain allowlist and suspicious link detection.                                                                                                             │     │
│     │ - jailbreak and role-override patterns.                                                                                                                          │     │
│     │ - prompt injection patterns in user text, retrieved content, tool output, and human review text.                                                                  │     │
│     │ - NSFW, hate/harassment, violence, self-harm, regulated goods, cyber-abuse, privacy leak categories.                                                              │     │
│     │ - custom enterprise prompt checks.                                                                                                                               │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: pass | refine | strip | quarantine | reject | escalate.                                                                                                │     │
│     │ Output: universal_guardrail_report with matched_patterns, severity, and recommended disposition.                                                                  │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R2 AGENT-LEVEL DOMAIN GUARDRAIL BANK                                                                                                                          │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Bound to agent spec and task domain.                                                                                                                            │     │
│     │                                                                                                                                                                  │     │
│     │ Checks:                                                                                                                                                          │     │
│     │ - PII detection and handling policy.                                                                                                                            │     │
│     │ - hallucination and unsupported-claim risk for factual outputs.                                                                                                  │     │
│     │ - off-topic detection against agent charter.                                                                                                                     │     │
│     │ - competitor/IP/data leakage constraints.                                                                                                                        │     │
│     │ - domain-specific keyword filters.                                                                                                                              │     │
│     │ - sector constraints: financial advice, credit, healthcare, legal, HR, insurance, regulated operations.                                                          │     │
│     │ - citation requirement and groundedness requirement for factual claims.                                                                                           │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: pass | require_grounding | require_HITL | shrink_scope | reject.                                                                                       │     │
│     │ Output: agent_guardrail_report.                                                                                                                                  │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R3 ROUTE AND PLAN ALIGNMENT CHECK                                                                                                                              │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Verifies that the chosen route is allowed for the actual request.                                                                                                │     │
│     │                                                                                                                                                                  │     │
│     │ Checks:                                                                                                                                                          │     │
│     │ - R1 cache route cannot satisfy fresh, high-stakes, or user-specific tasks without freshness and policy proof.                                                   │     │
│     │ - R3 grounded read must include C0 EvidenceContract or safe weak-support disposition.                                                                             │     │
│     │ - R4 action must include exact action, capability token request, sandbox request, and reversible/irreversible classification.                                    │     │
│     │ - Managed workflow must include L3 bounded step contract, not open-ended autonomy.                                                                                │     │
│     │ - R5 fallback must include reason_code and cannot silently become an answer.                                                                                      │     │
│     │ - HITL/high-risk route cannot be downgraded after human approval without re-clearance.                                                                            │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: pass | reroute_required | reject | escalate.                                                                                                           │     │
│     │ Output: route_alignment_report.                                                                                                                                  │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R4 HANDOFF VALIDATION | A2A / specialist to specialist                                                                                                          │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Prevents cross-agent context bleed and delegation laundering.                                                                                                    │     │
│     │                                                                                                                                                                  │     │
│     │ Checks:                                                                                                                                                          │     │
│     │ - handoff_description present.                                                                                                                                   │     │
│     │ - source_agent and target_agent registry entries exist.                                                                                                          │     │
│     │ - target_agent allowed for this route, task class, data class, model lane, and connector scope.                                                                  │     │
│     │ - principal_chain propagated unchanged.                                                                                                                          │     │
│     │ - delegation_depth <= max.                                                                                                                                       │     │
│     │ - target receives minimum necessary context only.                                                                                                                │     │
│     │ - hidden memory, stale scratchpad, or prior user context not leaked across task/principal boundary.                                                              │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: pass | shrink_context | require_HITL | reject.                                                                                                         │     │
│     │ Output: handoff_validation_report.                                                                                                                              │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R5 CONTEXT BOUNDARY ENFORCEMENT                                                                                                                               │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Prevents accidental or malicious mixing of principals, tasks, tenants, contexts, and memory.                                                                      │     │
│     │                                                                                                                                                                  │     │
│     │ Checks:                                                                                                                                                          │     │
│     │ - cross-task information bleed.                                                                                                                                 │     │
│     │ - cross-principal memory bleed.                                                                                                                                 │     │
│     │ - cross-tenant retrieval/tool output leak.                                                                                                                       │     │
│     │ - retrieved content with instruction-like text crossing into instruction slots.                                                                                  │     │
│     │ - human review packet adding new facts outside the bounded evidence packet.                                                                                      │     │
│     │ - stale cached content entering fresh task.                                                                                                                       │     │
│     │                                                                                                                                                                  │     │
│     │ Token binding:                                                                                                                                                    │     │
│     │ - capability_token.context_scope = task_id + tenant_id + principal_chain + route_id + evidence_contract_id.                                                     │     │
│     │ - context_scope cannot be broadened downstream without re-certification.                                                                                          │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: pass | strip | quarantine | require_retrieval_refresh | reject.                                                                                        │     │
│     │ Output: context_boundary_report.                                                                                                                                │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R6 POLICY VALIDATION CHOKEPOINT | risk-tier proportionate                                                                                                       │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ This is the main live authority gate.                                                                                                                            │     │
│     │                                                                                                                                                                  │     │
│     │ Risk depth:                                                                                                                                                       │     │
│     │ - LOW      -> fast-track policy check, minimal log, no HITL unless registry requires it.                                                                          │     │
│     │ - MODERATE -> standard guardrails, tool schema validation, replay binding, audit trace.                                                                           │     │
│     │ - HIGH     -> enhanced log, scoped sandbox, HITL if action high-impact, egress review, stricter evidence support.                                                 │     │
│     │ - CRITICAL -> lockdown posture, no autonomous execution, human/security review, isolate packet, forensic record.                                                 │     │
│     │                                                                                                                                                                  │     │
│     │ Validates:                                                                                                                                                        │     │
│     │ - requested action against policy.                                                                                                                               │     │
│     │ - tool/model/connector authority against registries.                                                                                                             │     │
│     │ - argument shape and schema.                                                                                                                                     │     │
│     │ - side-effect class and write intent.                                                                                                                            │     │
│     │ - sandbox envelope sufficiency.                                                                                                                                  │     │
│     │ - citation/grounding requirement.                                                                                                                                │     │
│     │ - human approval requirement.                                                                                                                                    │     │
│     │ - data sensitivity and export controls.                                                                                                                          │     │
│     │ - max retries, max cost, max tokens, max tool calls, max delegation depth.                                                                                        │     │
│     │                                                                                                                                                                  │     │
│     │ Hard stops:                                                                                                                                                       │     │
│     │ - hard_constraint breach.                                                                                                                                        │     │
│     │ - unregistered tool/model/connector.                                                                                                                             │     │
│     │ - broad credential, filesystem, memory, or network access without explicit scope.                                                                                 │     │
│     │ - irreversible action without required HITL.                                                                                                                     │     │
│     │ - cross-tenant or cross-principal leak.                                                                                                                          │     │
│     │ - prompt injection not neutralized.                                                                                                                              │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: reject | remediate | certify | escalate | shrink_scope | require_HITL.                                                                                  │     │
│     │ Output: policy_validation_report.                                                                                                                               │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R7 CAPABILITY TOKEN AND SANDBOX ENVELOPE BUILDER                                                                                                               │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Builds the actual runtime permit.                                                                                                                               │     │
│     │                                                                                                                                                                  │     │
│     │ capability_token fields:                                                                                                                                         │     │
│     │ - token_id.                                                                                                                                                       │     │
│     │ - principal_chain.                                                                                                                                               │     │
│     │ - scope: exact tool/model/connector/action/read/write class.                                                                                                     │     │
│     │ - ttl and expiration policy.                                                                                                                                     │     │
│     │ - single_use or bounded_multi_use with max_invocations.                                                                                                          │     │
│     │ - connector_allowlist.                                                                                                                                           │     │
│     │ - plan_digest and route_contract_digest.                                                                                                                         │     │
│     │ - evidence_contract_id if grounded.                                                                                                                              │     │
│     │ - permission_ladder: read < model < tool < network < memory < write_proposal < commit_request.                                                                   │     │
│     │ - allowed_args_hash or schema constraints.                                                                                                                       │     │
│     │ - revocation reason support.                                                                                                                                     │     │
│     │                                                                                                                                                                  │     │
│     │ sandbox_envelope fields:                                                                                                                                         │     │
│     │ - fs_scope: allowed paths, read/write mode, temp dirs, denied paths.                                                                                              │     │
│     │ - net_scope: allowed domains/IPs, methods, ports, egress class.                                                                                                   │     │
│     │ - syscall_scope: allowed commands/capabilities.                                                                                                                  │     │
│     │ - env_scope: allowed env vars, secrets policy, redaction policy.                                                                                                  │     │
│     │ - timeouts, memory limits, CPU/GPU limits, token/cost budget, retry budget.                                                                                      │     │
│     │ - artifact scope and output sealing location.                                                                                                                    │     │
│     │                                                                                                                                                                  │     │
│     │ Output: signed capability_token + sandbox_envelope.                                                                                                               │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R8 LLM GATEWAY | SOVEREIGN MODEL EGRESS                                                                                                                        │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Only approved path to external or internal model providers.                                                                                                      │     │
│     │                                                                                                                                                                  │     │
│     │ Provider resolution:                                                                                                                                             │     │
│     │ - symbolic model_id -> approved provider/model/version.                                                                                                          │     │
│     │ - registry confirms model allowed for agent, task class, risk tier, and data sensitivity.                                                                         │     │
│     │ - no silent fallback. Provider outage returns controlled error or certified fallback route only.                                                                  │     │
│     │                                                                                                                                                                  │     │
│     │ Ingress inspection:                                                                                                                                              │     │
│     │ - assembled prompt envelope scanned before model call.                                                                                                           │     │
│     │ - origin labels re-checked.                                                                                                                                      │     │
│     │ - retrieved content and tool output fenced as data.                                                                                                              │     │
│     │ - prompt injection detection.                                                                                                                                   │     │
│     │ - secret and PII scan.                                                                                                                                           │     │
│     │ - schema/tool field separation verified.                                                                                                                         │     │
│     │                                                                                                                                                                  │     │
│     │ Egress inspection:                                                                                                                                               │     │
│     │ - PII leak detection.                                                                                                                                            │     │
│     │ - secret leak detection.                                                                                                                                         │     │
│     │ - unsafe URL or credential exfiltration detection.                                                                                                               │     │
│     │ - hallucination/groundedness check when factual.                                                                                                                 │     │
│     │ - sensitive-data classifier.                                                                                                                                     │     │
│     │ - schema compliance.                                                                                                                                             │     │
│     │ - refusal/abstention correctness.                                                                                                                               │     │
│     │ - tool-call proposal validation before any tool is invoked.                                                                                                      │     │
│     │                                                                                                                                                                  │     │
│     │ Optional high-risk guard-model review:                                                                                                                           │     │
│     │ - second-model or deterministic verifier checks policy, leakage, groundedness, and action safety.                                                                 │     │
│     │ - disagreement escalates, not auto-allow.                                                                                                                        │     │
│     │                                                                                                                                                                  │     │
│     │ Outputs: model_gateway_receipt, ingress_report, egress_report, provider_receipt, replay envelope event.                                                          │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R9 TOOL / CONNECTOR / NETWORK EGRESS                                                                                                                           │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Intercepts every non-model power use.                                                                                                                           │     │
│     │                                                                                                                                                                  │     │
│     │ Checks before invocation:                                                                                                                                        │     │
│     │ - token valid, unexpired, correct principal, correct route, correct tool/connector.                                                                               │     │
│     │ - arguments match schema and allowed_args_hash.                                                                                                                  │     │
│     │ - no path traversal, command injection, SQL injection, prompt injection into tool fields, SSRF, broad wildcard.                                                   │     │
│     │ - network destination allowed.                                                                                                                                  │     │
│     │ - action side-effect class matches token.                                                                                                                        │     │
│     │ - irreversible or high-impact action paused for HITL if required.                                                                                                │     │
│     │                                                                                                                                                                  │     │
│     │ Checks after invocation:                                                                                                                                         │     │
│     │ - tool output classified as untrusted data.                                                                                                                      │     │
│     │ - output scanned for secrets, PII, instructions, hidden payloads, and malformed data.                                                                             │     │
│     │ - state diff captured as proposal only.                                                                                                                          │     │
│     │ - replay receipt sealed.                                                                                                                                         │     │
│     │                                                                                                                                                                  │     │
│     │ Outputs: invocation_record, tool_output_classification, state_diff_proposal, replay_event.                                                                        │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R10 HITL ACTION GATE AND HUMAN RE-ENTRY                                                                                                                        │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Human review is allowed only as a bounded control step. It is not a bypass.                                                                                      │     │
│     │                                                                                                                                                                  │     │
│     │ Trigger conditions:                                                                                                                                              │     │
│     │ - high-impact action.                                                                                                                                            │     │
│     │ - irreversible write or external commit.                                                                                                                         │     │
│     │ - critical uncertainty.                                                                                                                                          │     │
│     │ - policy ambiguity.                                                                                                                                              │     │
│     │ - suspicious injection pattern with possible benign intent.                                                                                                      │     │
│     │ - material customer/financial/legal/health/HR consequence.                                                                                                      │     │
│     │                                                                                                                                                                  │     │
│     │ Human packet rules:                                                                                                                                              │     │
│     │ - freeze current authority.                                                                                                                                      │     │
│     │ - present bounded packet only: reason, evidence, proposed action, risk, alternatives, required decision.                                                         │     │
│     │ - human can APPROVE, MODIFY_DIFF, REJECT, REQUEST_MORE_INFO.                                                                                                     │     │
│     │ - human cannot directly mutate L4, bypass L5, broaden scope, or call tools.                                                                                       │     │
│     │ - any human modification becomes human_review origin data and re-enters G2a, R1, R5, and R6.                                                                     │     │
│     │                                                                                                                                                                  │     │
│     │ Output: HITLDispositionPacket + re_clearance_required = true.                                                                                                    │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R11 RUNTIME REGRESSION AND DRIFT PROTECTION                                                                                                                    │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Protects against current-run behavior drifting away from certified assumptions.                                                                                  │     │
│     │                                                                                                                                                                  │     │
│     │ Checks:                                                                                                                                                          │     │
│     │ - policy_hash still current for this run.                                                                                                                        │     │
│     │ - registry_digest_set unchanged.                                                                                                                                 │     │
│     │ - provider/model version matches certified symbolic mapping.                                                                                                     │     │
│     │ - prompt template stable prefix unchanged.                                                                                                                       │     │
│     │ - tool schema version unchanged.                                                                                                                                 │     │
│     │ - connector grant unchanged.                                                                                                                                     │     │
│     │ - sandbox envelope not broadened.                                                                                                                                │     │
│     │ - retry loop not thrashing.                                                                                                                                      │     │
│     │ - cost/token/tool-call budget not exceeded.                                                                                                                      │     │
│     │ - evidence support not degraded below required threshold.                                                                                                        │     │
│     │ - route contract not silently reinterpreted by L2/L3.                                                                                                           │     │
│     │                                                                                                                                                                  │     │
│     │ Outcomes: pass | deny | reroute | escalate | freeze_incident.                                                                                                   │     │
│     │ Output: runtime_regression_report.                                                                                                                              │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│     ┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐     │
│     │ R12 REPLAY AND AUDIT SEALING                                                                                                                                    │     │
│     ├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤     │
│     │ Seals enough evidence for deterministic replay and forensic reconstruction.                                                                                      │     │
│     │                                                                                                                                                                  │     │
│     │ Captures:                                                                                                                                                        │     │
│     │ - request_id, run_id, trace_id, span_id, route_id.                                                                                                                │     │
│     │ - policy_hash, blueprint_hash, registry_digest_set.                                                                                                              │     │
│     │ - capability_token hash and sandbox_envelope hash.                                                                                                               │     │
│     │ - prompt artifact hash, evidence contract hash, output schema hash.                                                                                              │     │
│     │ - tool/model invocation records.                                                                                                                                │     │
│     │ - state diff proposal.                                                                                                                                           │     │
│     │ - human disposition packet if any.                                                                                                                              │     │
│     │ - decision rail verdict.                                                                                                                                         │     │
│     │ - standards_fingerprint and compliance_hash.                                                                                                                     │     │
│     │                                                                                                                                                                  │     │
│     │ Output: replay_envelope + audit_log_event + L6 evidence hooks.                                                                                                   │     │
│     └──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────┘     │
│                                                            ▼                                                                                                                 │
│                                              [ send to decision rail ]                                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

========================================================================================================================================================================================
[ DECISION RAIL | EXPLICIT TERMINAL AUTHORITY | The Head Librarian's Desk ]
========================================================================================================================================================================================

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ DECISION RAIL INPUTS                                                                                                                                                         │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ - GovernedValidationContext.                                                                                                                                                 │
│ - static reports if applicable.                                                                                                                                              │
│ - runtime guardrail reports.                                                                                                                                                 │
│ - route alignment report.                                                                                                                                                    │
│ - context boundary report.                                                                                                                                                   │
│ - policy validation report.                                                                                                                                                  │
│ - capability/sandbox draft.                                                                                                                                                  │
│ - LLM/tool/connector egress reports if invocation occurred.                                                                                                                   │
│ - HITLDispositionPacket if applicable.                                                                                                                                       │
│ - runtime regression report.                                                                                                                                                 │
│ - replay and audit sealing report.                                                                                                                                           │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                    ┌────────────────────────────────────┬────────────────────────────────────┬────────────────────────────────────┬────────────────────────────────────┐
                    │ ❌ REJECT                          │ 🩹 REMEDIATE                        │ 👥 ESCALATE / HUMAN REVIEW          │ ✅ CERTIFY                          │
                    │ Revoke Card                         │ Suggest Safe Edits                  │ Secure Reading Room                 │ Stamp of Approval                   │
                    ├────────────────────────────────────┼────────────────────────────────────┼────────────────────────────────────┼────────────────────────────────────┤
                    │ WHEN                                │ WHEN                                │ WHEN                                │ WHEN                                │
                    │ - hard_constraint breach            │ - no hard_constraint breach         │ - policy ambiguity                  │ - all required gates passed         │
                    │ - unregistered authority            │ - safe sanitization possible        │ - high-impact action                │ - scope is bounded                  │
                    │ - cross-tenant/principal leak       │ - narrow scope can fix risk         │ - irreversible effect               │ - replay material complete          │
                    │ - injection not neutralized         │ - missing field can be repaired     │ - sensitive uncertain judgment      │ - capability token is scoped        │
                    │ - hidden egress/write path          │ - output schema fix possible        │ - operator/SME signoff required     │ - sandbox is sufficient             │
                    │ - provider/tool mismatch            │ - safe re-entry through L5          │ - incident posture needed           │ - audit record sealed               │
                    │                                    │                                    │                                    │                                    │
                    │ ACTIONS                             │ ACTIONS                             │ ACTIONS                             │ ACTIONS                             │
                    │ - stop execution                    │ - sanitize or narrow                │ - freeze authority                  │ - attach compliance_hash            │
                    │ - revoke token if issued            │ - produce remediation patch         │ - materialize bounded review packet │ - attach standards_fingerprint      │
                    │ - record failure reason             │ - return to upstream layer          │ - block direct mutation             │ - bind capability_token             │
                    │ - send fault telemetry              │ - require full re-validation        │ - require L5 re-clearance after     │ - bind sandbox_envelope             │
                    │ - no fallback unless certified      │ - preserve original audit trail     │   human response                    │ - emit replay_envelope              │
                    │                                    │                                    │ - record HITL latency/verdict       │ - emit audit_log                    │
                    │                                    │                                    │                                    │ - allow governed execution only     │
                    │                                    │                                    │                                    │                                    │
                    │ OUTPUT                              │ OUTPUT                              │ OUTPUT                              │ OUTPUT                              │
                    │ - GovernanceResult.REJECT           │ - GovernanceResult.REMEDIATE        │ - GovernanceResult.ESCALATE         │ - GovernanceResult.CERTIFY          │
                    │ - reason_code                       │ - remediation_instructions          │ - HITLReviewPacket                  │ - compliance_hash                   │
                    │ - hard_stop                         │ - revalidate_required = true        │ - authority_frozen = true           │ - capability_token                  │
                    │ - no execution authority            │ - no execution authority yet        │ - re_clearance_required = true      │ - sandbox_envelope                  │
                    │                                    │                                    │                                    │ - replay_envelope                   │
                    └────────────────────┬───────────────┴────────────────────┬───────────────┴────────────────────┬───────────────┴────────────────────┘
                                         │                                    │                                    │
                                    [ tears up ]                        [ hands back ]                       [ stamps approved ]
                                         ▼                                    ▼                                    ▼
                              [ FAIL / RETURN ]                    [ RE-VALIDATE LOOP ]              [ GOVERNED EXECUTION CONTINUES ]

DECISION RAIL INVARIANTS
- Every human modification, plan change, tool call, model request, connector call, or write proposal must traverse this rail before gaining execution authority.
- REMEDIATE is forbidden when breached_rule.hard_constraint = true.
- ESCALATE freezes authority. It does not grant authority.
- CERTIFY is scoped to the exact packet, token, route, plan_digest, sandbox, principal_chain, and policy_hash.
- CERTIFY does not imply durable write authority. Durable writes still require Exit Control and UWG.
- A certified model/tool call cannot be reused for a different task, principal, tenant, route, or scope.
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                    │
                                                              [ walks out ]
                                                                    ▼
========================================================================================================================================================================================
[ OUTPUT CONTRACT | GovernanceResult ]
========================================================================================================================================================================================

GovernanceResult
  - decision:
      REJECT | REMEDIATE | ESCALATE | CERTIFY

  - reason_codes:
      policy_violation
      hard_constraint_breach
      missing_authority
      registry_mismatch
      route_mismatch
      injection_detected
      context_bleed
      cross_tenant_risk
      data_sensitivity_risk
      evidence_weak
      groundedness_required
      HITL_required
      sandbox_insufficient
      replay_incomplete
      provider_mismatch
      tool_schema_mismatch
      connector_scope_mismatch
      budget_exceeded
      drift_detected

  - compliance_hash:
      hash over policy_bundle + blueprint + registry_digest_set + decision reports + standards_fingerprint

  - standards_fingerprint:
      NIST_AI_RMF
      ISO_42001
      CoSAI_baselines
      SOC2_controls
      sector overlays
      internal policy overlays

  - audit_log:
      append-only governance decision record
      includes who/what/when/why/how
      includes rejected/remediated/escalated/certified path

  - replay_envelope:
      schema-versioned
      binds run_id, trace_id, route_contract, policy_hash, blueprint_hash, registry digests, prompt/evidence/tool/model hashes
      sufficient for L6 forensic replay and independent reconstruction

  - capability_token:
      scope
      ttl
      single_use or bounded_multi_use
      principal_chain
      connector_allowlist
      plan_digest
      route_contract_digest
      evidence_contract_id
      permission_ladder
      allowed_args_hash
      revocation posture

  - sandbox_envelope:
      fs_scope
      net_scope
      syscall_scope
      env_scope
      timeout
      resource limits
      artifact scope
      retry bounds
      output sealing path

  - origin_trust_manifest:
      labels for system_policy, governance_policy, registry_config, developer_admin, user_turn, retrieved, tool_output, human_review, prior_artifact

  - governance_reports:
      triage_report
      authority_context_report
      origin_boundary_report
      static_report
      runtime_guardrail_report
      route_alignment_report
      handoff_report
      context_boundary_report
      policy_validation_report
      token_sandbox_report
      egress_report
      HITL_report
      runtime_regression_report
      audit_seal_report

  - downstream_disposition:
      allow_l2_execution
      allow_model_call
      allow_tool_call
      allow_connector_call
      require_HITL
      deny
      reroute
      require_UWG_commit_review
      incident_lockdown

========================================================================================================================================================================================
[ OUT-OF-BAND PLANES | feed policy versions; NEVER alter current certified run ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────────┐  ┌──────────────────────────────────────────────┐
│ CALIBRATION PLANE                             │  │ ASSURANCE PLANE                               │  │ AUDIT / FORENSIC PLANE                       │
│ Golden, adversarial, and regression corpus    │  │ Continuous red-team and threat intel          │  │ Replay verifier and independent reconstruction│
├──────────────────────────────────────────────┤  ├──────────────────────────────────────────────┤  ├──────────────────────────────────────────────┤
│ - guardrail threshold tuning                  │  │ - prompt injection suites                      │  │ - replay envelope validation                  │
│ - groundedness threshold tuning               │  │ - jailbreak and bypass discovery               │  │ - hash-chain audit verification               │
│ - risk-tier calibration                       │  │ - connector/tool abuse tests                    │  │ - policy/version reconstruction               │
│ - cache reuse threshold tuning                │  │ - model/provider drift tests                    │  │ - human review reconstruction                 │
│ - HITL sampling rate calibration              │  │ - policy weakening regression tests             │  │ - incident timeline reconstruction            │
│ - false positive/negative review              │  │ - sector overlay tests                          │  │ - retention and compliance attestation        │
│ - approved promotion only                     │  │ - CI/promptfoo-style enforcement                │  │ - tamper evidence and gap reports             │
└───────────────────────┬──────────────────────┘  └───────────────────────┬──────────────────────┘  └───────────────────────┬──────────────────────┘
                        └──────────────────────────────┬───────────────────┴──────────────────────────────┬─────────────────┘
                                                       ▼                                                  ▼
                                          [ policy_version_next candidate ]                    [ forensic replay / compliance attestation ]
                                          enters G2 on next packet only                         no retroactive mutation

OUT-OF-BAND INVARIANTS
- Learning signals inform future thresholds, policies, registries, rubrics, prompts, and guardrail rules only after promotion.
- No out-of-band plane can rescue, mutate, approve, or reinterpret a completed current run.
- Promotion requires regression pack, rollback plan, owner approval, and UWG commit if durable state changes.
- Policy_version_next is not policy_version_current until the Universal Write Gateway commits it into L4.
========================================================================================================================================================================================

========================================================================================================================================================================================
[ BELOW GOVERNANCE & SAFETY CONTEXT | certified outputs propagate to execution / exit / observability ]
[ Library analogy: Patron leaves with stamped books, bounded permits, receipt trail, and no secret side doors ]
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
CERTIFIED OUTPUTS PROPAGATE TO:
- L2 Execute:
    receives capability_token, sandbox_envelope, replay_envelope, governed PromptEnvelope or action packet.
    may execute only the current bounded step.
    cannot route, broaden scope, ask humans directly, or commit durable state.

- L3 Orchestration:
    receives governed step contracts and policy limits.
    may sequence only within certified workflow bounds.
    cannot re-decide route or expand authority.

- Exit Eval & Control:
    receives sealed artifacts and governance receipts.
    decides allow, deny, reroute, escalate, or commit request.
    cannot let a write bypass UWG.

- HITL:
    receives bounded review packet only.
    human response re-enters L5 as untrusted human_review data.

- UWG:
    receives commit request only after Exit Control and L5 clearance.
    sole durable write path into L4.

- L6:
    receives telemetry, replay envelope, audit log, decision reports, guardrail hits, HITL outcomes, and drift signals.
    observes, evaluates, and proposes future learning only.

FINAL INVARIANT SET
- L5 is the Commandant: policy, safety, authority, and egress certification.
- C0 retrieves only.
- Prompt Assembly packages only.
- L0 routes only.
- L3 orchestrates bounded workflows only.
- L2 executes bounded current steps only.
- HITL reviews only, and human input is not sovereign authority.
- UWG writes only.
- L4 stores canonical durable state.
- L6 observes, evaluates, and promotes future-run learning only.
- No hidden state mutation.
- No silent fallback.
- No unregistered authority.
- No cross-principal context bleed.
- No direct write outside UWG.
- No current-run mutation from learning signals.
========================================================================================================================================================================================

Cross-references:
  - docs/reference/00_L5_Policy_Plane/Governance & Safety v4.md
  - docs/reference/00_L5_Policy_Plane/guardrail_families.md
  - docs/reference/00_L5_Policy_Plane/risk_tier_bands.md
  - docs/reference/00_L5_Policy_Plane/capability_token.schema.md
  - docs/contracts/identity_propagation.md
  - docs/reference/00_L5_Policy_Plane/calibration_assurance_planes.md
  - docs/architecture/adr/ADR-049-l5-v4-governance-plane.md
  - docs/reference/agentic_system_process_map_exec.md
  - docs/reference/C0_Governance_Safety_Enforcement.md
  - docs/reference/C1_Deterministic_Replay_Execution_Integrity.md
  - docs/reference/C2_Observability_Telemetry_Control_Signals.md
  - docs/reference/C3_Healing_Remediation_Escalation.md
  - docs/reference/C4_State_Sovereignty_Universal_Write_Governance.md
  - docs/reference/C6_Evaluation_Learning_Promotion_System.md
========================================================================================================================================================================================