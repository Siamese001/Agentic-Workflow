╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                            ADG SQLITE HOTSPOT CHEAT SHEET                                                    ║
║                   (didactic • zero-loss • high-signal • repo-native)                                         ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ BOTTOM LINE                                                                                                  ║
║ Your ADG SQLite = what code IS + what it DOES + rules it MUST OBEY + boundaries it CROSSES.                  ║
║ A HOTSPOT = bad catch site sitting on a structurally important path with meaningful blast radius.            ║
║ ADG = Observed + enforced truth. When conflict exists, ADG wins. If a node lies, the graph is invalid.       ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ ADG SQLITE – THE TOPOLOGICAL MENTAL MODEL                                                                    ║
║                                                                                                              ║
║ ┌─────────────────────────────────────────────────────────────────────┐                                      ║
║ │                           ADG SQLITE                                │                                      ║
║ ├─────────────────────────────────────────────────────────────────────┤                                      ║
║ │ META       "What build is this?" (commit_sha, stats, exemptions)    │                                      ║
║ ├─────────────────────────────────────────────────────────────────────┤                                      ║
║ │ NODES      "What things exist?" (Modules, Symbols, Layers)          │                                      ║
║ │ SURFACES   "Where is the risk?" (Execution, Write, Security limits) │                                      ║
║ ├─────────────────────────────────────────────────────────────────────┤                                      ║
║ │ EDGES      "How do they relate?" (Extracted from underlying AST)    │                                      ║
║ │   • Static: imports, extends, owns (The Bridge: Module owns Symbol) │                                      ║
║ │   • Flow: calls, flows_to, reads_from, writes_to                    │                                      ║
║ ├─────────────────────────────────────────────────────────────────────┤                                      ║
║ │ VIOLATIONS "Where is a rule broken?" (category, severity, line)     │                                      ║
║ └─────────────────────────────────────────────────────────────────────┘                                      ║
║                                                                                                              ║
║ Nouns = Nodes • Verbs = Edges • Red flags = Violations • Label = Meta                                        ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ THE ZERO-LOSS PROPAGATION PIPELINE & HOTSPOT DIAGNOSIS                                                       ║
║                                                                                                              ║
║ [ 1. catch site at file:line ]                                                                               ║
║           │                                                                                                  ║
║           ▼                                                                                                  ║
║ [ 2. antipattern edge ] (broad_catch, log_and_swallow, silent_swallow, return_none)                          ║
║           │                                                                                                  ║
║           ▼                                                                                                  ║
║ [ 3. ownership bridge ] (Map the catching Symbol back to its governing Module/Layer to cross the Type Gap)   ║
║           │                                                                                                  ║
║   ├─────► How bad is the pattern itself?                                                                     ║
║   ├─────► What layer is it in? (L0/L3/L4/L5 matters more)                                                    ║
║   ├─────► How many things depend on it? (Reverse Walk -> Blast Radius / Fan-In)                              ║
║   ├─────► How many things does it touch? (Forward Walk -> Dependency / Fan-Out)                              ║
║   └─────► Does the flow intersect one of the FIVE ADG SURFACES?                                              ║
║           │                                                                                                  ║
║           ▼                                                                                                  ║
║      [ HOTSPOT ]                                                                                             ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ THE DIRECTIONAL RULE: FAN-IN vs FAN-OUT                                                                      ║
║                                                                                                              ║
║      REVERSE WALK ("Who do I break?")                 FORWARD WALK ("What do I need to run?")                ║
║      (Blast-Radius View)                              (Dependency View)                                      ║
║                                                                                                              ║
║                     FAN-IN                                                                                   ║
║      A ───────┐                                                                                              ║
║      B ───────┼──────► [ FILE X ] ──────► Y                                                                  ║
║      C ───────┤                         ├────► Z                                                             ║
║      D ───────┘                         └────► Q                                                             ║
║                                           FAN-OUT                                                            ║
║                                                                                                              ║
║ High fan-in = central dependency (if it lies → many callers get poisoned)                                    ║
║ High fan-out = orchestrator/coordinator (if it swallows → hides downstream damage)                           ║
║ High flow/control density = operational hotspot                                                              ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ THE 5 ADG SURFACES (Risk Boundaries) & THE 4 DEADLY ANTIPATTERNS                                             ║
║ Surfaces are semantic boundaries where untrusted inputs flow. Swallowing errors here causes system lies.     ║
║                                                                                                              ║
║ 1. EXECUTION SURFACE   (calls/eval)      → Masks Arbitrary Code Execution (ACE) risks.                       ║
║    └─ Vulnerable to: broad_exception_catch (The System Hijacker - loops on dead state)                       ║
║ 2. WRITE SURFACE       (writes_to)       → Masks state mutation and data corruption.                         ║
║    └─ Vulnerable to: silent_exception_swallow (The State Corrupter - caches a void)                          ║
║ 3. GOVERNANCE SURFACE  (guardrails)      → Masks autonomous policy bypasses.                                 ║
║    └─ Vulnerable to: log_and_swallow (The False Sentinel - observes violation but proceeds)                  ║
║ 4. DETERMINISM SURFACE (wall_clock/rng)  → Masks reproducibility and replay failures.                        ║
║ 5. SECURITY SURFACE    (reads_secret)    → Masks data exfiltration and trust breaches.                       ║
║    └─ Vulnerable to: return_none_swallow (The Stack Destroyer - completely drops audit trace)                ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ THE FOUR HOTSPOT ARCHETYPES                                                                                  ║
║ 1. CENTRAL DEPENDENCY      ← many inbound, bad swallow poisons callers                                       ║
║ 2. ORCHESTRATOR            ← huge outbound/flow, swallow hides chain failures                                ║
║ 3. STATE / MEMORY NODE     ← swallow creates silent inconsistency                                            ║
║ 4. SAFETY / GATEKEEPER     ← swallow suppresses controls                                                     ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ HOTSPOT SCORE FORMULA (the one-liner you keep in your head)                                                  ║
║                                                                                                              ║
║ HOTSPOT SCORE ≈ local_antipattern_severity × structural_centrality × blast_radius × surface_intersection ×   ║
║                 layer_criticality × observability_weakness                                                   ║
║                                                                                                              ║
║ • local severity: silent_exception_swallow > broad_exception_catch > logged narrow catch                     ║
║ • centrality: fan-in / import concentration                                                                  ║
║ • blast radius: fan-out / flows_to / controls_flow / emits_side_effect                                       ║
║ • surface risk: Security/Execution limits > Determinism > standard internal flow                             ║
║ • layer criticality: L0 routing > L3 orchestration > L4 state > L5 safety                                    ║
║ • observability weakness: return_None / silent / no structured outcome                                       ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ WHAT YOUR SQLITE WILL TELL YOU ABOUT TOP ROWS (structural signals 101)                                       ║
║                                                                                                              ║
║ A) Highest direct inbound (central dependencies)                                                             ║
║    • [Core / Routing Services]        → High inbound file count                                              ║
║    • [Security / Gatekeepers]         → High inbound file count                                              ║
║    • [State / Cache Managers]         → High inbound file count                                              ║
║                                                                                                              ║
║ B) Highest outward blast radius (controllers/orchestrators)                                                  ║
║    • [Primary Orchestrator Agents]    → Massive outbound, heavy flow/control edges                           ║
║    • [State / Checkpoint Managers]    → Massive outbound, heavy flow edges                                   ║
║    • [Action Plane Controllers]       → High outbound, execution flow edges                                  ║
║                                                                                                              ║
║ C) Biggest violation clusters                                                                                ║
║    • [Code Hygiene / Utilities]       → High concentration of structural violations                          ║
║    • [Legacy Integration Modules]     → High concentration of structural violations                          ║
║                                                                                                              ║
║ Plain-English translations:                                                                                  ║
║ • Orchestrator Agents           → controllers hiding chain failures                                          ║
║ • Core Routing Services         → classic central-dependency hotspots                                        ║
║ • Gatekeeper Modules            → safety-layer choke points                                                  ║
║ • Cache Managers                → state/cache paths with real inbound dependencies                           ║
║ • Hygiene / Legacy Modules      → code-health concentration points                                           ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ GUARDIAN vs REAL FIX (fastest decision guide)                                                                ║
║ guardian     = "we know this looks bad, but we are explicitly allowing it"                                   ║
║ narrow catch = "make the failure surface smaller and more truthful"                                          ║
║ add logging  = "do not hide the failure, at least make it observable"                                        ║
║ inspect      = "we are not yet sure if this is intentional or laziness"                                      ║
║                                                                                                              ║
║ Rule of thumb:                                                                                               ║
║ • High fan-in + swallow      → guardian only with VERY strong reason                                         ║
║ • High fan-out + broad catch → usually narrow it                                                             ║
║ • L4/L5 silent swallow       → highest skepticism                                                            ║
║ • return_none_swallow in shared path → often worse than it looks                                             ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ THE SINGLE BEST ASCII TO KEEP IN YOUR HEAD                                                                   ║
║                                                                                                              ║
║                    ┌──────────────────────────────┐                                                          ║
║                    │       BAD CATCH SITE         │                                                          ║
║                    │ broad / silent / swallow     │                                                          ║
║                    └──────────────┬───────────────┘                                                          ║
║                                   │                                                                          ║
║                 ┌─────────────────┼─────────────────┐                                                        ║
║                 │                 │                 │                                                        ║
║                 ▼                 ▼                 ▼                                                        ║
║         ┌────────────────┐ ┌────────────────┐ ┌────────────────┐                                             ║
║         │    FAN-IN      │ │    FAN-OUT     │ │   LAYER RISK   │                                             ║
║         │ who needs me?  │ │ what I touch?  │ │ L0/L3/L4/L5 ?  │                                             ║
║         └──────┬─────────┘ └──────┬─────────┘ └──────┬─────────┘                                             ║
║                │                  │                  │                                                       ║
║                └──────────────────┼──────────────────┘                                                       ║
║                                   ▼                                                                          ║
║                     ┌──────────────────────────┐                                                             ║
║                     │        HOTSPOT RANK      │                                                             ║
║                     │ centrality + blast radius│                                                             ║
║                     │ + hidden failure risk    │                                                             ║
║                     └──────────────────────────┘                                                             ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ USEFUL SQL PATTERNS (copy-paste ready)                                                                       ║
║ 1. Structural summary          SELECT key, value FROM meta ORDER BY key;                                     ║
║ 2. Top edge families           SELECT relation_type, COUNT(*) FROM edges GROUP BY relation_type ORDER BY c DESC;║
║ 3. File-level fan-in/fan-out   (see full query in original – uses src_id/dst_id joins)                       ║
║ 4. Hotspots by file            SELECT v.file_path, COUNT(*), SUM(exception_antipatterns) FROM violations...  ║
║ 5. One file blast radius       SELECT relation_type, edge_kind, COUNT(*) FROM edges WHERE resolved_path=...  ║
╟──────────────────────────────────────────────────────────────────────────────────────────────────────────────╢
║ EXAMPLE REPO STATS (what to look for in your build)                                                          ║
║ • [X] nodes • [Y] edges • [Z] violations • [N] guardian exemptions                                           ║
║ Tracks: imports + runtime-ish behavior (flows, controls, side effects, antipatterns)                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝