==============================================================================================================================
[C0] 🛡️ GOVERNANCE & SAFETY ENFORCEMENT
     Library Personas: 👮 Commandant + 🚪 Front Desk Guard + 📋 Rule Librarian
     Operational Span: 👤 apps -> 🧠 L1 -> 🧭 L0/L3 -> 🛠️ L2 -> 🚪 Exit -> 👥 HITL -> 🏛️ UWG
==============================================================================================================================

                                              👤 REQUEST / PLAN / ACTION
                                                         │
                                                         │
                                                 [ inbound ask ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G1 🚪 GOVERNANCE INVOCATION (Front Desk Triage)                                                                            │
│ - Triage Mode Selection: Static check (pre-flight), Runtime check (active), or Human re-entry                    │
│ - Initial integrity verification and ingress categorization                                                      │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
                                                         │
                                                         │
                                                  [ hands slip ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ G2 📋 AUTHORITY CONTEXT (Master Charter Desk)                                                                              │
│ - Loads active policy sets, structure maps, and registry rules for the specific tenant                           │
│ - Binds the governing "Charter" to the request folder for downstream enforcement                                 │
└────────────────────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┘
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
                 │ [ structure metadata ]                                              │ [ runtime context ]
                 ▼                                                                               ▼
┌────────────────────────────────────────┐       ┌───────────────────────────────────────────────────────────────────────────┐
│ 🗺️ G3 STRUCTURE CHECK                  │       │ 📚 G4 REGISTRY VALIDATION                                                 │
│ - Layer isolation & depth verification │───────│ - Identity check & allowed model verification                  │
│ - placement & connectivity audit     │ - Execution mode & digest integrity check                       │
└────────────────┬───────────────────────┘       └──────────────────────────────┬────────────────────────────────────────────┘
                 │                                                              │
                 │ [ structural signals ]                              │ [ registry status ]
                 └───────────────────────────────┬──────────────────────────────┘
                                                 │
                                                 │ [ safety signals ]
                                                 ▼
                              ┌──────────────────────────────────────────────────┐
                              │ 🏷️ G5 CLASSIFY SHAPE                              │
                              │ - Execution type check & dual-tag clash detection│
                              │ - Resource intent vs. capability alignment
                              └──────────────────┬───────────────────────────────┘
                                                 │
                                                 │ [ risk report ]
                                                 ▼
                              ┌──────────────────────────────────────────────────┐
                              │ 🚪 G6 POLICY CHOKEPOINT                          │
                              │ - Risk tiering & explicit tool validation        │
                              │ - Plan-to-Action alignment check       │
                              └──────────────────┬───────────────────────────────┘
                                                 │
                                                 │ [ asks exit ]
                                                 ▼
                              ┌──────────────────────────────────────────────────┐
                              │ 🌐 G7 SOVEREIGN EGRESS                           │
                              │ - Symbolic to provider mapping & audit           │
                              │ - Prompt injection detection & replay sealing    │
                              │ - Policy: Fail-Closed Only             │
                              └──────────────────┬───────────────────────────────┘
                                                 │
                                                 │ [ security audit ]
                                                 ▼
==============================================================================================================================
                                              👮 THE DECISION RAIL
==============================================================================================================================
          ┌──────────────────────────────┬──────────────────────────────┬────────────────────────────────────────┐
          │ ❌ REJECT                    │ 🩹 REMEDIATE                 │ ✅ CERTIFY                             │
          │ - Immediate stop & return    │ - Sanitize & re-inject       │ - Bind compliance & capability tokens  │
          │ - Record failure logs - Trigger re-validate - Seal in sandbox envelope      │
          └──────────────┬───────────────┴──────────────┬───────────────┴────────────────┬───────────────────────┘
                         │                              │                                │
                         │ [ tears up ]       │ [ hands back ]       │ [ stamps approved ]
                         ▼                              ▼                                ▼
                 [ fail / return ]              [ re-validate loop ]            [ governed execution continues ]
                                                                                         │
                                                                                         │ [ final tokens ]
                                                                                         ▼
                  OUTPUTS: compliance_hash + audit_log + replay_envelope + capability_token + sandbox_envelope