╔══════════════════════════════════════════════════════════════════════════════╗
║                WHY ADG MISSES HARDCODED STRING ANTI-PATTERNS                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────┐  ┌─────────────────────────────────────┐
│         ADG SEES: STRUCTURE         │  │   ADG MISSES: CONTENT SEMANTICS     │
├─────────────────────────────────────┤  ├─────────────────────────────────────┤
│ file_a.py                           │  │ file_a.py                           │
│  ├─ imports -> utils.py             │  │  api_key = "sk_live_abc123"         │
│  ├─ calls   -> send_request()       │  │  sql     = "SELECT * FROM users"    │
│  ├─ writes  -> state_store          │  │  prompt  = "Ignore prior rules"     │
│  └─ reads   -> config_loader        │  │  route   = "admin_override"         │
├─────────────────────────────────────┤  ├─────────────────────────────────────┤
│ • graph relations & edges           │  │ • string meaning & intent           │
│ • layer boundaries & calls          │  │ • sensitivity & policy risk         │
│ • ownership & write paths           │  │ • business semantics                │
├─────────────────────────────────────┤  ├─────────────────────────────────────┤
│         "WHO TALKS TO WHOM?"        │  │       "WHAT EXACTLY WAS SAID?"      │
└─────────────────────────────────────┘  └─────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                     WHAT ADG IS ACTUALLY BUILT TO MODEL                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ request.py ──calls──> planner.py ──calls──> router.py ──calls──> executor.py ║
║      │                     │                    │                    │       ║
║      └────reads_policy─────┴────routes_path─────┴────writes_to──────> UWG    ║
╠═════════════════════════════════════╦════════════════════════════════════════╣
║            EXCELLENT AT:            ║               WEAK AT:                 ║
║ ─────────────────────────────────── ║ ────────────────────────────────────── ║
║ • layer inversion                   ║ • "is this literal a secret?"          ║
║ • unauthorized write paths          ║ • "is this prompt text dangerous?"     ║
║ • missing governance edges          ║ • "is this SQL string unsafe?"         ║
║ • broken orchestration links        ║ • "is this rule hardcoded vs config?"  ║
║ • dependency & authority drift      ║ • "is this phrase a policy bypass?"    ║
╚═════════════════════════════════════╩════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                WHY HARDCODED STRINGS FALL THROUGH THE CRACKS                 │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [ SOURCE FILE ]                                                             │
│         │                                                                    │
│         ▼                                                                    │
│  [ EXTRACTORS ] ─── function call / import graph / symbol relations          │
│         │                                                                    │
│         ▼                                                                    │
│  [ ADG NODE ]   ─── function: make_request() | class: ApiClient | client.py  │
│         │                                                                    │
│         ▼                                                                    │
│  [ ADG EDGE ]   ─── make_request() ────calls────> http_post()                │
│                                                                              │
│  THE PROBLEM:                                                                │
│  The literal string stays TRAPPED inside the AST of the node body.           │
│  It does not natively map to a first-class graph edge.                       │
│                                                                              │
│  EXAMPLE:                                                                    │
│  http_post(url="https://prod-secret-endpoint")                               │
│                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                │
│                Dangerous payload, but treated as inert text by ADG.          │
└──────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                             THE LIBRARY ANALOGY                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ADG = The Library Floor Map         ║ String Anti-Pattern = The Note's Text  ║
║ • room connections                  ║                                        ║
║ • allowed note-passing paths        ║ "use admin password 123"               ║
║ • master ledger write-access        ║                                        ║
║                                     ║                                        ║
║ FLOOR MAP CAN PROVE:                ║ FLOOR MAP CANNOT PROVE:                ║
║ "Clerk A passed a note to Vault"    ║ "The note contained a password."       ║
╠═════════════════════════════════════╬════════════════════════════════════════╣
║          FLOOR MAP PROBLEM          ║         NOTE CONTENT PROBLEM           ║
║ ─────────────────────────────────── ║ ────────────────────────────────────── ║
║ • structural compliance             ║ • literal content inspection           ║
║ • graph / edge analysis             ║ • lexical / pattern analysis           ║
╚═════════════════════════════════════╩════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│                        WHY THIS IS NOT AN ADG FAILURE                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ ADG is designed for structural truth (routing, authority, replay, write).    │
│ It is NOT a semantic auditor, secret scanner, config linter, or regex tool.  │
│                                                                              │
│ "Asking ADG to catch hardcoded strings is like asking a subway map           │
│  to detect profanity written inside a passenger's text message."             │
├──────────────────────────────────────────────────────────────────────────────┤
│                          WHAT YOU NEED IN ADDITION                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────┐   ┌─────────────────────┐   ┌──────────────────┐   │
│   │ ADG / AST STRUCTURE │ + │ LEXICAL STRING SCAN │ + │ POLICY ENGINE    │   │
│   ├─────────────────────┤   ├─────────────────────┤   ├──────────────────┤   │
│   │ "where is it wired?"│   │ regex / heuristics  │   │ "is this legal?" │   │
│   │                     │   │ entropy / SQL rules │   │                  │   │
│   └──────────┬──────────┘   └──────────┬──────────┘   └────────┬─────────┘   │
│              │                         │                       │             │
│              ▼                         ▼                       ▼             │
│   [ 1. WHERE IT LIVES ]       [ 2. WHAT IT IS ]       [ 3. WHY IT FAILS ]    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════════════════╗
║                        SIMPLE EXAMPLE & MENTAL MODEL                         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CODE:                                                                        ║
║ def route():                                                                 ║
║     mode = "admin_override"  <────── Forbidden control string                ║
║     return execute(mode)                                                     ║
║                                                                              ║
║ ADG SEES:         route() ──calls──> execute()                               ║
║ ADG MISSES:       "admin_override" is a hardcoded control value.             ║
║ REQUIRED FIX:     Literal extraction + Gov. Rules + Taint/Policy Analysis    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                            THE RIGHT MENTAL MODEL                            ║
║ ──────────────────────────────────────────────────────────────────────────── ║
║ TOOL                QUESTION                             ROLE                ║
║ ─────────────────   ────────────────────────────────   ───────────────────── ║
║ ADG                 "What is connected?"               Architecture MRI      ║
║ String Scanner      "What exact text is embedded?"     Microscope            ║
║ Policy Engine       "Should that text be there?"       Compliance Judge      ║
╚══════════════════════════════════════════════════════════════════════════════╝