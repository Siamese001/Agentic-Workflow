TUNNEL (FLOW PATH)                     SEAM (BOUNDARY CONTRACT)

"How the request moves"                "Where rules are enforced"


     ┌──────────────┐                  ┌──────────────┐
     │   L5 SAFETY  │                  │   L5 SAFETY  │
     │ governance   │                  │ governance   │
     └──────┬───────┘                  └──────┬───────┘
            │                                 │
            ▼                                 ▼
   ┌─────────────────────┐        ┌────────────────────────┐
   │                     │        │          SEAM           │
   │     TUNNEL PATH     │        │   contract interface    │
   │                     │        │                         │
   │  validation flow    │        │  validate(packet)      │
   │  execution routing  │        │  authorize(token)      │
   │  command pipeline   │        │  enforce schema        │
   │                     │        │                         │
   └──────────┬──────────┘        └──────────┬─────────────┘
              │                              │
              ▼                              ▼
        ┌──────────────┐               ┌──────────────┐
        │  L2 EXECUTE  │               │  L2 EXECUTE  │
        │  run agents  │               │  run agents  │
        └──────────────┘               └──────────────┘
