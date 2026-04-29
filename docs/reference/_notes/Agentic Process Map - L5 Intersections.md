================================================================================================================
                         AGENTIC PROCESS MAP WITH L5 INTERSECTIONS — v38 ALIGNED
================================================================================================================

================================================================================================================
                         MENTAL MODEL FIRST
================================================================================================================

Think of the system like a governed library:

  U0 Intake       = Front Desk / Guard
                   Checks the person, form, identity, quota, and envelope.

  L1 Plan         = Senior Librarian
                   Understands the ask and drafts the bounded plan, but cannot route or act.

  L0 Route        = Hallway Director / Dispatcher
                   Chooses exactly one path through the building.

  L3 Orchestrate  = Floor Manager
                   Breaks an approved managed workflow into bounded step cards.

  C0 Context      = Reference Desk
                   Finds evidence, checks lineage, ACL, freshness, contradictions, and support.

  Prompt Assembly = Packet Builder
                   Packs trusted instructions, verified evidence, user task, schema, and provider metadata.

  L2 Execute      = Assistant in the Stacks
                   Does one approved bounded work order, may repair locally, then seals the folder.

  Exit            = Checkout Desk / Commandant
                   Decides whether the sealed folder can leave, reroute, escalate, abstain, or request real ink.

  UWG             = Master Clerk
                   The only place that can put real ink into the permanent archive.

  L4              = Permanent Archive
                   Durable system of record, registries, policies, memory, cache, replay, and audit.

  L6              = Night Board
                   Reviews completed runs after the runtime boundary and proposes future improvements only.

  99              = Proof Auditor
                   Proves the whole process actually happened through traces, receipts, replay, and no-bypass checks.

  L5              = Safety Officer / Certification Spine
                   Certifies whether every packet has valid authority, policy, registry, origin trust,
                   capability, sandbox, egress, HITL, replay, audit, and static governance evidence.

Core mental model:

  L5 is not a traffic light.
  L5 is not the checkout desk.
  L5 is not the master clerk.
  L5 is not the assistant doing the work.

  L5 is the certification spine that proves:
    "This packet is governed under the right policy, authority, registry, origin labels,
     capability, sandbox, egress lane, HITL status, replay envelope, and audit chain."

  Then:
    00C Runtime Gates decide live proceed / stop.
    Exit emits exactly one X3 disposition.
    UWG commits durable state.
    L4 stores durable state.
    L6 learns only for future runs.

Cheat rule:

  L2 proposes -> Exit clears -> UWG commits -> L4 stores

Control split:

  L5 certifies evidence.
  00C gates live steps.
  Exit decides final current-run outcome.
  UWG admits durable writes.
  99 proves the chain ran.

================================================================================================================
                         L5 GOVERNANCE / CERTIFICATION SPINE
================================================================================================================

 [ L5 GOVERNANCE / CERTIFICATION SPINE ]
   Certifies evidence for:
   policy | authority | registry | origin trust | capability | sandbox | egress | HITL | replay/audit | static drift
   Binds:
   request_id | run_id | trace_id | policy_hash | blueprint_hash | registry_digest_set |
   principal_chain | capability_token | sandbox_envelope | origin_trust_manifest |
   egress lane | replay envelope | audit refs | L5GovernanceContext digest
   Does NOT:
   route | retrieve | assemble prompt | execute | emit live disposition | commit durable state | learn into current run

        │
        │ emits / binds L5 certification evidence consumed by live gates and Exit
        │
        ▼

 [ 00C RUNTIME GATES ]
   Live question: "Can this current packet / step / call / output / write proposal proceed right now?"
   Uses L5 evidence, but owns live GateVerdict.
   UNKNOWN is never PASS. NOT_APPLICABLE requires reason.
        │
        ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. U0 INTAKE                                                                                                  │
│ Owns: request envelope, identity/session/tenant baseline, schema, quota, origin labels                         │
│                                                                                                                │
│ L5 intersects:                                                                                                │
│ - Requires initial origin/data-boundary labels on inbound content                                               │
│ - Binds request_id / session_id / trace_root / caller / tenant / principal baseline                             │
│ - Marks user text as intent only, not policy, registry, route, tool, model, or write authority                  │
│ - Surfaces malformed, unlabeled, oversized, duplicate, or obvious injection evidence for later certification    │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - reason, route, retrieve, execute, approve, deny, or write                                                     │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ ValidatedRequest
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2. L1 INTERPRET / PLAN                                                                                        │
│ Owns: intent, task_spec, query_spec, ambiguity register, advisory plan, L1PlanContract                          │
│                                                                                                                │
│ L5 intersects:                                                                                                │
│ - Separates user intent from system / governance / registry authority                                           │
│ - Reads L4-approved policy, schemas, route priors, examples, and patterns as governed planning context          │
│ - Carries policy_hash / blueprint_hash / registry refs into the plan contract when available                    │
│ - Marks assumptions and unresolved gaps so L5/Exit can later verify no hidden authority was invented            │
│ - Declares grounding_required, action expectation, side-effect hint, HITL hint, UWG hint                        │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - turn advisory plan into route authority                                                                       │
│ - let model output widen authority                                                                             │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ L1PlanContract
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3. L0 ROUTING / L3 ORCHESTRATION                                                                              │
│ Owns: exactly one RouteContract; L3 only when managed workflow is selected                                      │
│                                                                                                                │
│ L5 intersects at L0:                                                                                           │
│ - Certifies route posture against policy, risk tier, registry, capability ceiling, sandbox, replay envelope     │
│ - Checks route cannot silently widen read/tool/model/network/filesystem/write scope                             │
│ - Binds selected route to policy_hash, blueprint_hash, registry_digest_set, replay_key, side_effect_class       │
│ - Treats cache reuse as governed reuse, not truth by similarity alone                                           │
│ - Requires provider/model/tool/connector substitution to be re-certified                                        │
│                                                                                                                │
│ L5 intersects at L3:                                                                                           │
│ - Ensures workflow expansion preserves RouteContract bounds                                                     │
│ - Ensures each L3StepContract carries same authority context or explicit recertification need                   │
│ - Prevents workflow step from expanding scope, tools, providers, side effects, or durable mutation authority     │
│ - Requires HITL pause/resume packets to remain frozen, bounded, and re-clearable                                │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - choose the route                                                                                             │
│ - expand the workflow                                                                                          │
│ - execute steps                                                                                                │
│                                                                                                                │
│ Route options:                                                                                                │
│   R1A Exact Cache -----------------------> [RET] -> Exit                                                       │
│   R1B Semantic Cache --------------------> [RET] -> Exit                                                       │
│   R5 Fallback ---------------------------> [RET] -> Exit                                                       │
│   R3 Grounded Read ----------------------> C0 -> PA -> L2 -> Exit                                              │
│   R4 Single Action ----------------------> L2 -> Exit                                                          │
│   R3/R4 Managed Workflow ----------------> L3 -> L2 step loop -> Exit                                          │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ RouteContract / L3StepContract if managed
                                               ▼

        ┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
        │ L4 READ SURFACES                                                                                   │
        │ Owns: durable policy, blueprint, registry, memory, cache, retrieval surfaces, replay/audit records  │
        │                                                                                                    │
        │ L5 intersects:                                                                                    │
        │ - Reads active policy bundle, blueprint, registry snapshots, capability and sandbox records         │
        │ - Uses point-in-time reconstructable state for certification                                       │
        │ - Requires stale, missing, mismatched, deprecated, or substituted registry entries to fail closed    │
        │ - Provides policy_hash / blueprint_hash / registry_digest_set / replay snapshot to L5 consumers     │
        │                                                                                                    │
        │ L5 must not:                                                                                      │
        │ - write L4 directly                                                                                │
        └───────────────────────────────────────────────────────────────────────────────────────────────────┘

                                               │
                              grounded path only
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ C0 CONTEXT ENGINE                                                                                            │
│ Owns: retrieval planning, fetch, hydration, graph expansion, evidence shaping, verification, support status    │
│                                                                                                                │
│ L5 intersects:                                                                                                │
│ - Enforces retrieved text as data only, never instruction                                                       │
│ - Requires origin_trust_manifest and source lineage for retrieved/user/tool/human/prior/model content           │
│ - Checks ACL, tenant, region, data class, freshness, source authority, citation anchors, and contradiction      │
│ - Requires exact/BM25/metadata support for names, IDs, paths, dates, policy labels, code symbols                │
│ - Preserves source_id, version, retrieval lane, graph lineage, support status, and gaps                         │
│ - Blocks quarantined content unless safe extraction preserves lineage and does not invent authority             │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - retrieve missing evidence                                                                                    │
│ - score support as C0                                                                                          │
│ - answer                                                                                                       │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ FinalEvidenceContract
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PROMPT ASSEMBLY                                                                                              │
│ Owns: signed prompt packet from verified evidence, user task, schema, governance refs, provider metadata       │
│                                                                                                                │
│ L5 intersects:                                                                                                │
│ - Consumes L5/governance refs, origin labels, authority classes, policy refs, provider lane, replay metadata   │
│ - Preserves trusted instruction vs untrusted data boundary                                                     │
│ - Fences user/retrieved/tool/model/human/prior content by authority class                                      │
│ - Blocks prompt-like untrusted content from becoming system/developer/governance instruction                    │
│ - Requires signed PromptEnvelope / CompiledPromptArtifact with manifest/hash/HMAC discipline                    │
│ - Requires provider/model/tool lane to match registry and egress certification refs                            │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - assemble the prompt                                                                                          │
│ - call provider                                                                                                │
│ - approve output                                                                                               │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ CompiledPromptArtifact
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 4. L2 EXECUTE                                                                                                │
│ Owns: E1 Prep -> E2 Valid -> E3 Exec -> E4 Heal -> E5 Seal                                                     │
│                                                                                                                │
│ L5 intersects at E1 Prep:                                                                                      │
│ - Binds packet to same policy_hash / blueprint_hash / registry_digest_set / replay_key                          │
│ - Freezes capability_token, sandbox_envelope, provider lane, input hash, prompt hash, attempt seed              │
│ - Confirms L2 receives authority and cannot create authority                                                    │
│                                                                                                                │
│ L5 intersects at E2 Valid:                                                                                     │
│ - Validates authority context, capability scope, sandbox scope, side-effect class, ACL, route match             │
│ - Fails before execution on missing authority, stale policy, blocked ACL, sandbox gap, route mismatch           │
│ - Confirms tool/model/connector/provider target is registry-bound and certified                                 │
│                                                                                                                │
│ L5 intersects at E3 Exec:                                                                                      │
│ - Requires all model/tool/network/provider egress through governed gateway path                                 │
│ - Prevents direct SDK bypass, silent fallback, hardcoded model/provider substitution, broad credential use       │
│ - Captures model/tool/provider receipts, trace refs, cost/budget counters, replay/audit refs                    │
│                                                                                                                │
│ L5 intersects at E4 Heal:                                                                                      │
│ - Healing must stay same-authority, same route, same policy, same blueprint, same sandbox                       │
│ - Cannot heal missing authority, blocked ACL, policy conflict, stale registry, sandbox gap, HITL need           │
│ - Heal repository is approved repair menu; heal function is live same-authority repair governor                 │
│                                                                                                                │
│ L5 intersects at E5 Seal:                                                                                      │
│ - SealedL2Artifact must include certification refs, terminal class, traces, counters, lineage, replay receipts  │
│ - proposed_state_diff remains inert until Exit/UWG                                                             │
│ - Any mutation intent must remain a proposal, never a durable write                                             │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - execute, repair, approve output, request commit, or commit durable state                                      │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ SealedL2Artifact / ProposedStateDiff
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 5. EXIT EVAL & CONTROL                                                                                       │
│ Owns: X1 checks, X2 aggregation, exactly one X3 current-run disposition                                         │
│                                                                                                                │
│ L5 intersects at Exit input normalization:                                                                     │
│ - ExitReviewPacket must bind route, policy_hash, blueprint_hash, prompt_hash, replay_key                       │
│ - Requires sandbox_envelope, capability_token, provider receipts, evidence contract if grounded                 │
│ - Immediate fail if required authority, replay, route, terminal class, sandbox, capability, or evidence missing │
│                                                                                                                │
│ L5 intersects at X1 gates:                                                                                     │
│ - X1A Today's Rules: policy manifest, threshold profile, grader roster                                          │
│ - X1C Safe to Leave: sandbox, mutation authority, side effect, egress                                           │
│ - X1D Answer Good: groundedness, faithfulness, citations, support                                               │
│ - X1G Replay Eligible: replay guard, idempotency, manifest integrity                                            │
│ - X1H Observable: OTEL span tree, counters, audit trail completeness                                            │
│ - X1J Write Eligibility: pre-UWG readiness when mutation requested                                              │
│                                                                                                                │
│ L5 intersects at HITL:                                                                                         │
│ - Human input is data until re-cleared                                                                         │
│ - Human modification cannot widen authority, policy, registry, scope, provider lane, or write authority         │
│ - Resume requires bounded HumanReviewEvidencePacket, HumanModificationDiff, and L5 re-clearance evidence        │
│                                                                                                                │
│ L5 intersects at X3:                                                                                           │
│ - Exit owns exactly one disposition: DENY/REROUTE | ESCALATE_HITL | COMMIT_REQUEST_TO_UWG | ALLOW | ABSTAIN     │
│ - L5 certification evidence informs Exit, but L5 does not emit the X3                                           │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - emit final X3                                                                                                │
│ - allow output, deny output, reroute, escalate, or request commit                                               │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ CommitRequest only if Exit clears
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ UWG / L4 COMMIT                                                                                              │
│ Owns: durable write admission and atomic mutation into L4                                                      │
│                                                                                                                │
│ L5 intersects:                                                                                                │
│ - UWG may require L5 certification refs for durable mutation admission                                         │
│ - Checks CommitRequest against authority scope, StateDiff, schema, policy, replay, audit, lock, rollback       │
│ - Confirms mutation does not bypass Exit or widen beyond capability/sandbox/write_scope                        │
│ - Emits durable write receipts, audit append, rollback refs, read-surface refresh receipts                     │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - write durable state directly                                                                                 │
│ - approve UWG commit as L5                                                                                     │
└──────────────────────────────────────────────┬───────────────────────────────────────────────────────────────┘
                                               │ RuntimeExhaustBundle after runtime boundary
                                               ▼

┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 6. L6 SHADOW EVALUATION / FUTURE-RUN LEARNING                                                                │
│ Owns: completed-run ingest, evaluation, calibration, RCA, proposals, gauntlet, future-run promotion attempt    │
│                                                                                                                │
│ L5 intersects:                                                                                                │
│ - L6 reads sealed L5 evidence after runtime boundary only                                                       │
│ - Evaluates governance failures: policy/auth/registry/origin/egress/HITL/replay/audit/static drift             │
│ - May draft future-run policy/prompt/rubric/config proposals                                                    │
│ - Promotion must pass gauntlet and UWG before becoming durable L4 state                                         │
│                                                                                                                │
│ L5 must not:                                                                                                  │
│ - retroactively certify the completed run                                                                      │
│ - let L6 rescue or mutate the current run                                                                      │
│ - let L6 write L4 directly                                                                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘


================================================================================================================
                         L5 CROSS-CHILD CERTIFICATION SPINE
================================================================================================================

Every L5 child must certify the SAME governed object through the same L5GovernanceContext digest:

   Safety Enforcement digest
        =
   Authority / Registry digest
        =
   Origin Trust digest
        =
   HITL Reclearance digest when applicable
        =
   Egress Certification digest when applicable
        =
   Replay / Audit digest
        =
   Static Governance digest
        =
   Runtime Certification Binding digest

If digests mismatch:
   -> emit L5_NOT_CERTIFIED evidence
   -> 00C Runtime Gates / Exit decide live consequence
   -> L5 still does NOT emit ALLOW / DENY / REROUTE / COMMIT


================================================================================================================
                         L5 CHILD COVERAGE MAP
================================================================================================================

 00A.1 Safety Enforcement
 - classification kernel, structure blueprint, agent execution profile registry, sovereign gateway substrate
 - catches unregistered agents, direct SDK bypass, model substitution, unsafe structure, registry drift

 00A.2 Authority Context + Registry Binding
 - GovernedValidationContext, policy/blueprint/registry/principal/capability/sandbox/replay binding
 - catches no-implied-authority, stale registry, cross-principal bleed, cross-tenant bleed, scope widening

 00A.3 Origin Trust + Content Boundary
 - OriginTrustManifest, trusted instruction vs untrusted data, quarantine, safe extraction
 - catches prompt injection, retrieved-text-as-instruction, human-input-as-authority, model-output-as-authority

 00A.4 HITL Reclearance
 - HITLFreezePacket, HumanReviewEvidencePacket, HumanModificationDiff, ResumeAuthorityReceipt
 - catches human override expansion, unbounded review, modification without re-clearance

 00A.5 Egress + Provider Governance
 - EgressCertificationRequest/Receipt, provider/model/tool/connector/network/credential/fallback evidence
 - catches silent fallback, provider substitution, hidden egress, direct SDK bypass, credential leakage

 00A.6 Replay / Audit / Certification Evidence
 - L5CertificationPacket/Result, audit manifest, receipt chain, hash/trace/reconstruction reports
 - catches non-replayable certification, missing audit refs, broken hash chain, reconstruction gaps

 00A.7 Static Governance + Structure Drift
 - static drift reports for architecture, policy, registry, prompt, connector, route, bypass, write paths
 - catches governance weakening before runtime

 00A.7a Governance Context Invariant
 - canonical L5GovernanceContext, deterministic digest equality across children
 - catches sibling certifiers proving different realities

 00A.8 Runtime Certification Binding
 - runtime packet binding to L5 certification evidence
 - connects L5 evidence to U0/L1/L0/C0/PA/L3/L2/Exit/UWG/L6 without giving L5 live disposition authority

 00A.8a Cross-Child Certification Tests
 - mutation matrix, OTEL assertions, digest equality tests
 - proves L5 children cannot drift or certify inconsistent contexts


================================================================================================================
                         L5 PROOF REQUIREMENTS IN 99
================================================================================================================

99 must prove the L5 spine actually ran, not merely that the answer looked correct.

Minimum L5 proof bundle:
- l5_certification_result
- l5_governance_context_digest
- policy_hash
- blueprint_hash
- registry_digest_set
- origin_trust_manifest_ref
- capability_token_ref
- sandbox_envelope_ref
- egress_certification_receipt when provider/tool/connector/network used
- HITL re-clearance receipt when human review modified or resumed work
- replay_envelope_ref
- audit_manifest_ref
- OTEL spans for l5.certify / l5.governance.context / l5.runtime.binding
- no-bypass assertion for model/tool/provider/network/direct-write paths
- negative control showing mismatch -> L5_NOT_CERTIFIED
- proof that L5 did not emit GateVerdict, X3 disposition, or durable commit
================================================================================================================