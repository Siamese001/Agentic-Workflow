TUNNEL (THE FLOW PATH)                                  SEAM (THE BOUNDARY CONTRACT)
"How the request moves through the system"              "Where rules are enforced between domains"
==========================================              ==========================================

        ┌──────────────────────┐                                ┌──────────────────────┐
        │      L5 SAFETY       │                                │      L5 SAFETY       │
        │      governance      │                                │      governance      │
        └──────────┬───────────┘                                └──────────┬───────────┘
                   │                                                       │
                   ▼ (Request enters)                                      ▼ (Request hits boundary)
        ┌──────────────────────┐                         ══════════════════╪═══════════════════ (Hard Barrier)
        │ │   TUNNEL PATH    │ │                         │                 ▼                  │
        │ │                  │ │                         │               SEAM                 │
        │ │ ↓ validation flow│ │                         │        contract interface          │
        │ │ ↓ execution rout │ │                         │                                    │
        │ │ ↓ command pipelin│ │                         │     [x] validate(packet)           │
        │ │                  │ │                         │     [x] authorize(token)           │
        │ │  (orchestration) │ │                         │     [x] enforce schema             │
        │ │                  │ │                         │                                    │
        └──────────┬───────────┘                         ══════════════════╪═══════════════════ (Hard Barrier)
                   │ (Request exits)                                       │ (Permitted payload)
                   ▼                                                       ▼
        ┌──────────────────────┐                                ┌──────────────────────┐
        │      L2 EXECUTE      │                                │      L2 EXECUTE      │
        │      run agents      │                                │      run agents      │
        └──────────────────────┘                                └──────────────────────┘
