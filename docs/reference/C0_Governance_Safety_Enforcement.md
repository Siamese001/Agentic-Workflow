==============================================================================================================================
[C0] 🛡️ GOVERNANCE & SAFETY ENFORCEMENT
     Library Personas: 👮 Commandant + 🚪 Front Desk Guard + 📋 Rule Librarian
     Operational Span: 👤 apps -> 🧠 L1 -> 🧭 L0/L3 -> 🛠️ L2 -> 🚪 Exit -> 👥 HITL -> 🏛️ UWG
==============================================================================================================================

┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ INVARIANTS (normative - C0 governs; does not retrieve, package, or execute)                                            │
│ J1. C0 governs only. It does not retrieve evidence, package prompts, or dispatch tools.                                    │
│ J2. Every ingress artifact is labeled with origin-trust before downstream use.                                              │
│ J3. Untrusted content MUST pass boundary classification before reaching prompt assembly or L2.                              │
│ J4. Injection detection runs at BOTH ingress and egress. Fail-closed on either side.                                       │
│ J5. PromptEnvelope postures are policy-bound here; PA encodes, C0 enforces.                                                │
│ J6. High-impact actions traverse HITL and explicit sandbox scope before sovereign egress.                                  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                                              👤 REQUEST / PLAN / ACTION
                                                         │
                                                         │
                                                 [ inbound ask ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G1 🚪 GOVERNANCE INVOCATION (Front Desk Triage)                                                                               │
│ - Triage mode selection: static check, runtime check, or human re-entry                                                      │
│ - Initial integrity verification and ingress categorization                                                                   │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G1a 🧪 HARMLESSNESS PRE-SCREEN (lightweight ingress classifier)                                                               │
│ - Runs before charter binding using a cheap classifier or rules pass                                                         │
│ - Scans prompt text, uploads, and referenced URLs                                                                            │
│ - Matches jailbreak, coercion, role-play escape, and system-override patterns                                                │
│ - Outputs: allow | refine | deny + risk_tier + matched_patterns[]                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
                                                  [ hands slip ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2 📋 AUTHORITY CONTEXT (Master Charter Desk)                                                                                 │
│ - Loads active policy sets, structure maps, tenant rules, and refusal taxonomy                                               │
│ - Binds the governing Charter to the folder for downstream enforcement                                                       │
│ - Charter includes citation defaults, tool-use defaults, and escalation posture                                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2a 🏷️ ORIGIN-TRUST LABELING (content provenance)                                                                            │
│ - user_system  = platform-authored system or policy content                                                                  │
│ - user_turn    = end-user input                                                                                              │
│ - retrieved    = C0 evidence from shelves                                                                                    │
│ - tool_output  = browser, MCP, or tool returns                                                                              │
│ - human_review = HITL-authored correction                                                                                    │
│ - Untagged artifacts default to untrusted until explicitly cleared                                                           │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                [ stamped folder ]
                                                         │
                                                         ▼
==============================================================================================================================
                      DUAL ENFORCEMENT RAILS   [ Parallel Validation of the Governed Folder ]
==============================================================================================================================

      STATIC LANE 🧱 (Prevention)                                                 RUNTIME LANE 🚧 (Containment)
      ───────────────────────────                                                 ─────────────────────────────
                 │                                                                               │
                 │ [ structure metadata ]                                                        │ [ runtime context ]
                 ▼                                                                               ▼
┌───────────────────────────────────────────────────────────────────────┐       ┌───────────────────────────────────────────────────────────────────────────┐
│ 🗺️ G3 STRUCTURE CHECK                                                 │       │ 📚 G4 REGISTRY VALIDATION                                                  │
│ - Layer isolation and depth verification                              │       │ - Identity check and allowed model verification                            │
│ - Placement, connectivity, and boundary audit                         │       │ - Execution mode, digest integrity, and capability roster check            │
└──────────────────────────────────────────────┬────────────────────────┘       └──────────────────────────────────┬────────────────────────────────────────┘
                                               │                                                           │
                                               │ [ structural signals ]                                     ▼
                                               │                            ┌────────────────────────────────────────────────────────────────────────────┐
                                               │                            │ 🔍 G4a RETRIEVED-CONTENT CLASSIFIER (C0 -> PA boundary)                    │
                                               │                            │ - Applies to origin=retrieved and origin=tool_output artifacts            │
                                               │                            │ - Scans for embedded instructions, hidden text, and coercive UI payloads  │
                                               │                            │ - Outcomes: pass | quarantine | strip | reject                            │
                                               │                            │ - Quarantined content MUST NOT enter <documents>                          │
                                               │                            └────────────────────────────────────────────────────────────────────────────┘
                                               │                                                           │
                                               └───────────────────────────────┬───────────────────────────┘
                                                                               │
                                                                               │ [ safety signals ]
                                                                               ▼
                              ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
                              │ 🏷️ G5 CLASSIFY SHAPE                                                                         │
                              │ - Execution type check and dual-tag clash detection                                          │
                              │ - Resource intent vs capability alignment                                                     │
                              │ - Read-only vs mutate intent vs external egress intent                                        │
                              └──────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                     │
                                                                     │ [ risk report ]
                                                                     ▼
                              ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
                              │ 🚪 G6 POLICY CHOKEPOINT                                                                       │
                              │ - Risk tiering and explicit tool validation                                                   │
                              │ - Plan-to-action alignment check                                                              │
                              │ - Binds citation_mode and tool_use posture on the governed packet                             │
                              └──────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
                              ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
                              │ 👥 G6a HITL ACTION-GATE + 🔒 SANDBOX SCOPE                                                   │
                              │ - High-impact actions must traverse HITL before sovereign egress                             │
                              │ - Sandbox envelope declares fs_scope, net_scope, syscall_scope, and ttl explicitly           │
                              │ - Even a successful injection remains bounded by declared scope                               │
                              └──────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                     │
                                                                     │ [ asks exit ]
                                                                     ▼
                              ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
                              │ 🚧 G7a INGRESS INJECTION VALIDATOR                                                            │
                              │ - Final scan of the assembled PromptEnvelope before handoff to L2                            │
                              │ - Re-checks origin labels, G4a quarantine outcomes, and document-content cleanliness         │
                              │ - Fail-closed only                                                                            │
                              └──────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                     │
                                                                     ▼
                              ┌────────────────────────────────────────────────────────────────────────────────────────────────┐
                              │ 🌐 G7 SOVEREIGN EGRESS                                                                        │
                              │ - Symbolic-to-provider mapping and audit                                                     │
                              │ - Egress injection detection and replay sealing                                              │
                              │ - Policy: fail-closed only                                                                    │
                              └──────────────────────────────────────┬─────────────────────────────────────────────────────────┘
                                                                     │
                                                                     │ [ security audit ]
                                                                     ▼
==============================================================================================================================
                                              👮 THE DECISION RAIL
==============================================================================================================================
          ┌──────────────────────────────┬──────────────────────────────┬────────────────────────────────────────┐
          │ ❌ REJECT                    │ 🩹 REMEDIATE                 │ ✅ CERTIFY                             │
          │ - Immediate stop and return  │ - Sanitize and re-inject     │ - Bind compliance and capability tokens│
          │ - Record failure logs        │ - Trigger re-validate loop   │ - Seal replay and sandbox envelopes    │
          └──────────────┬───────────────┴──────────────┬───────────────┴────────────────┬───────────────────────┘
                         │                              │                                │
                         │ [ tears up ]                 │ [ hands back ]                 │ [ stamps approved ]
                         ▼                              ▼                                ▼
                 [ fail / return ]              [ re-validate loop ]            [ governed execution continues ]
                                                                                         │
                                                                                         │ [ final tokens ]
                                                                                         ▼
  OUTPUTS: compliance_hash + audit_log + replay_envelope + capability_token + sandbox_envelope + origin_trust_manifest

==============================================================================================================================
                                     📈 G8 MONITORING & THROTTLE LOOP (closed-loop)
==============================================================================================================================
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ - Aggregates refusals, G1a/G4a/G7/G7a hits, HITL approvals/denies, and sandbox breaches                                       │
│ - Telemetry: refusal_rate, injection_detect_rate, HITL_latency, sandbox_exit_rate                                             │
│ - Repeat-offender policy: throttle | temp-ban | escalate_to_human                                                             │
│ - Drift watch: downstream tool failures and audit anomalies feed new patterns back into G1a and G4a                          │
│ - Red-team findings are ingested here as new prevention patterns                                                               │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
