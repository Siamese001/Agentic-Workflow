================================================================================
#2 RUNTIME GATES vs L5 vs EXIT
================================================================================

                   CROSS-CUTTING CONTROL SURFACES
                   -------------------------------

        ┌──────────────────────────────────────────────────────────┐
        │ 00A / L5 GOVERNANCE                                      │
        │                                                          │
        │ Question:                                                │
        │   "Is the authority / policy / registry / origin /       │
        │    sandbox / egress / replay evidence certified?"        │
        │                                                          │
        │ Emits:                                                   │
        │   L5_CERTIFIED / L5_NOT_CERTIFIED / gap evidence         │
        │                                                          │
        │ Does NOT emit:                                           │
        │   ALLOW / DENY / REROUTE / COMMIT_REQUEST                │
        └──────────────────────────────────────────────────────────┘
                                  │ evidence
                                  ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│   U0     │-->|   L1     │-->|   L0     │-->| C0 / PA  │-->|   L2     │
│ Intake   │   │ Plan     │   │ Route    │   │ Evidence │   │ Execute  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
      ▲              ▲              ▲              ▲              ▲
      │              │              │              │              │
      └──────────────┴──────────────┴──────────────┴──────────────┘
                         00C RUNTIME GATES
                         -----------------
                         Question:
                           "May this live packet, route,
                            retrieval, prompt, tool call,
                            model call, output, escalation,
                            or write proposal proceed now?"

                         Emits:
                           GateVerdict + bounded disposition hint

                         Does NOT:
                           route, retrieve, execute, assemble,
                           approve final output, commit L4,
                           or certify L5 evidence

                                  │ gate verdict evidence
                                  ▼
        ┌──────────────────────────────────────────────────────────┐
        │ 05 EXIT                                                  │
        │                                                          │
        │ Question:                                                │
        │   "Can the sealed result leave, deny, reroute, escalate, │
        │    abstain, or request commit?"                          │
        │                                                          │
        │ Emits:                                                   │
        │   exactly one X3 disposition                              │
        └──────────────────────────────────────────────────────────┘