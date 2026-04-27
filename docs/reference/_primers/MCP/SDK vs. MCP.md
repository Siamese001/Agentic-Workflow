Bottom line: pip install = local dependency install, SDK = developer interface to a service, MCP = runtime control plane + governed tool access layer.

                                      [ USER / APP REQUEST ]
                                                │
                                                ▼
════════════════════════════════════════════════════════════════════════════════════════════════════
║                         THREE WAYS TO ACCESS CAPABILITIES (STACKED BY POWER)                     ║
════════════════════════════════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1) PIP INSTALL (LOCAL LIBRARY INSTALL)                                                           │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Dev pulls code into local runtime                                                               │
│                                                                                                  │
│   pip install openai                                                                             │
│          │                                                                                       │
│          ▼                                                                                       │
│   [ LOCAL ENV / PYTHON RUNTIME ]                                                                 │
│   - Library runs inside your process                                                             │
│   - You manage deps, versions, execution                                                         │
│                                                                                                  │
│   (Library analogy: You bought the book and keep it on your desk for immediate, local use)       │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2) SDK (API WRAPPER / CLIENT INTERFACE)                                                          │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Code → SDK → External Service                                                                   │
│                                                                                                  │
│   your_code.py                                                                                   │
│        │                                                                                         │
│        ▼                                                                                         │
│   OpenAI SDK / AWS SDK                                                                           │
│        │                                                                                         │
│        ▼                                                                                         │
│   HTTPS API CALL                                                                                 │
│        │                                                                                         │
│        ▼                                                                                         │
│   [ REMOTE SERVICE (LLM / DB / API) ]                                                            │
│                                                                                                  │
│   - Hardcoded 1:1 integration: Dev must write custom glue code for every endpoint                │
│   - Stateless request/response pipeline                                                          │
│   - Blind to agents: Agent requires strict, custom upfront prompting on the specific API shape   │
│                                                                                                  │
│   (Library analogy: You query a retrieval persona to fetch a specific text from the stacks)      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 3) MCP (MODEL CONTEXT PROTOCOL — CONTROL + TOOL BUS)                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  Model ↔ MCP Server ↔ Tools / Systems                                                            │
│                                                                                                  │
│   [ LLM / AGENT ]                                                                                │
│        │                                                                                         │
│        ▼                                                                                         │
│   MCP CLIENT (protocol layer)                                                                    │
│        │                                                                                         │
│        ▼                                                                                         │
│   MCP SERVER (governed gateway / system bus persona)                                             │
│        │                                                                                         │
│   ┌───────────────┬───────────────┬────────────────┐                                             │
│   ▼               ▼               ▼                ▼                                             │
│ Filesystem     Database       APIs          Internal Tools                                       │
│                                                                                                  │
│   - Agent-Native: Dynamic runtime discovery (Agent asks the server "What tools do I have?")      │
│   - Universal 1:Many Integration: Standardized context injection and semantic routing            │
│   - Stateful capability exposure with built-in L5 governance and L0-L6 permissions               │
│                                                                                                  │
│   (Library analogy: Fully staffed library system with strict L0-L6 authority boundaries, L5      │
│    mandatory governance, single mutation authority (UWG), and deterministic audit receipts)      │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════════════════════════════════
║ KEY DIFFERENCE SUMMARY                                                                           ║
════════════════════════════════════════════════════════════════════════════════════════════════════
│ TYPE        │ INTEGRATION PARADIGM      │ AGENT AWARENESS              │ GOVERNANCE / CONTROL        │
├─────────────┼───────────────────────────┼──────────────────────────────┼─────────────────────────────┤
│ pip install │ Static local binary       │ Blind (Just executes)        │ Unmanaged (OS level)        │
│ SDK         │ Hardcoded 1:1 API wrapper │ Requires explicit schema map │ App-level logic required    │
│ MCP         │ Dynamic 1:Many System Bus │ Self-discovering tools/state │ Standardized (L5) protocol  │
└─────────────┴───────────────────────────┴──────────────────────────────┴─────────────────────────────┘

════════════════════════════════ HIGH-SIGNAL TAKE ════════════════════════════════
pip = COMPILE-TIME → SDK = HARDCODED PIPELINE → MCP = AGENTIC SYSTEM BUS

The core value proposition: SDKs force the *developer* to write, map, and maintain
custom glue code so an agent can use a specific tool.

MCP flips this: it is a universal protocol layer. The *agent* dynamically discovers,
understands, and negotiates access to tools natively. It operates at the system
layer of your runtime, enabling governed, deterministic control flows (like your
Redis MCP read gateway) without writing bespoke 1:1 API wrappers for every capability.