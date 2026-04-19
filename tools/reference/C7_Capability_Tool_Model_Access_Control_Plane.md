==============================================================================================================================
[C7] 🔑 CAPABILITY / TOOL / MODEL ACCESS CONTROL PLANE
     Library Persona: 🎟️ Permit Clerk + 🧰 Tool Librarian + 🌐 Interlibrary Loan Booth
     Operational Span: Request classification -> Permissioning -> Ticketing -> Gated invocation -> Audit trail
==============================================================================================================================

                                              [ REQUEST NEEDS POWER ]
                                                         │
                                                         │
                                                 [ resource intent ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ ⚡ G1: WHAT KIND OF POWER? (Permit Clerk)                                                                                  │
│ - Classifies access type: read / tool / model / network / memory / write                                                   │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Resource Archetype ]
                                                         │
                                                         │
                                                  [ resource class ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 📚 G2: REGISTRY + ALLOWED SET (Tool Librarian)                                                                             │
│ - Validates identity and enforces allowed_models / execution_mode locks                                         │
│ - Performs registry digest integrity match and access control list (ACL) verification                                      │
└──────────────────────────┬──────────────────────────────────────────────────────────────────┬──────────────────────────────┘
                           │                                                                  │
                           │ [ verified on roster ]                                           │ [ ❌ NOT ON ROSTER ]
                           ▼                                                                  ▼
                                                                                          [ BLOCK ]
                                                         │
                                                         │
                                                  [ verified identity ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🧭 G3: CHOOSE THE LANE                                                                                                     │
│ - Routes request to local tool, external model, memory, network, or Universal Write Gate (UWG)                             │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Lane Routing Policy ]
                                                         │
                                                         │
                                                  [ execution lane ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🎟️ G4: BUILD ACCESS TICKET                                                                                                 │
│ - Generates capability_token and sandbox_envelope for the specific runtime                                       │
│ - Binds bounded scope, expiration metadata, and strict timeout parameters                                                  │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Auth & Sandbox State ]
                                                         │
                                                         │
                                               [ signed access ticket ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🚪 G5: INTERCEPT THE CALL                                                                                                  │
│ - Validates argument shape, route, and target; performs injection checks                                         │
│ - Assesses risk tiering for the requested operation against current policy                                              │
└──────────────────────────┬──────────────────────────────────────────────────────────────────┬──────────────────────────────┘
                           │                                                                  │
                           │ [ safe call profile ]                                            │ [ ⚠️ TOO BROAD / RISK ]
                           ▼                                                                  ▼
                                                                                          [ DENY / SHRINK ]
                                                         │
                                                         │
                                                  [ intercepted call ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🌐 G6: SOVEREIGN EGRESS / GATE (Interlibrary Loan Booth)                                                                   │
│ - Maps symbolic request to specific provider; enforces "No silent fallback" policy                                         │
│ - Ensures exactly one approved path out of the library environment                                                         │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Provider Mapping ]
                                                         │
                                                         │
                                               [ executed invocation ]
                                                         │
                                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 🧾 G7: INVOCATION RECORD                                                                                                   │
│ - Records usage: who used what, provider, tool, and compute cost                                                │
│ - Appends to audit log and seals the replay envelope for L6 verification                                                   │
└────────────────────────────────────────────────────────┬─────────────► [ Dependency: Execution Telemetry ]
                                                         │
                                                         │
                                               [ audit log + receipts ]
                                                         │
                                                         ▼
                                                [ HAND BACK TO 🛠️ L2 ]

==============================================================================================================================
[!] GOVERNED LANES: [📖 Read] [🧰 Tool] [🤖 Model] [🌐 Network] [🧠 Memory] [🖋️ Write] [👥 Human Review]
[!] LOGIC: Need Power -> Check Roster -> Issue Ticket -> Guard the Call -> Approved Lane Only -> Record It.
==============================================================================================================================