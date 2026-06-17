==================================================================================
             UNIFIED MCP ARCHITECTURE & HIGH-SIGNAL SECURITY MODEL
==================================================================================
MENTAL MODEL: 5 Danger Doors (+1 Scope Rule) protect the Untrusted Boundary.
If each door has its own hard check, MCP is safe.
If one door borrows trust from another, MCP gets dangerous.

[ USER / HOST APPLICATION ]
(Claude Desktop, legacy editor, Custom App with LLM Agent)
              │
              ▼
   [ DISCOVERY & STARTUP STAGE ] ──────────────────────────────────────────┐
              │                                                            │
┏━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━┓                       ┏━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━┓
┃ DOOR 1: DISCOVERY & ROUTING    ┃                       ┃ DOOR 5: LOCAL EXECUTION          ┃
┃ "Where should I connect?"      ┃                       ┃ "Am I launching code locally?"   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫                       ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ BLOCK (SSRF Risk):             ┃                       ┃ REJECT (Compromise Risk):        ┃
┃ ✗ Private IPs & Localhost      ┃                       ┃ ✗ Silent background execution    ┃
┃ ✗ Link-local & Unsafe redirects┃                       ┃ ✗ Hidden startup commands        ┃
┃ ALLOW:                         ┃                       ┃ REQUIRE:                         ┃
┃ ✓ Strictly validated public    ┃                       ┃ ✓ Explicit approval of command   ┃
┃   endpoints and explicit hops  ┃                       ┃ ✓ Sandboxed execution & tight IPC┃
┗━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┛                       ┗━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┛
              │                                                            │
              └─────────────────────────┬──────────────────────────────────┘
                                        ▼
                             ┌────────────────────┐
                             │     MCP CLIENT     │
                             └──────────┬─────────┘
                                        │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ DOOR 2: CONSENT & BINDING ("Who exactly did the user approve?")               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ REJECT (Confused Deputy):          ┃ REQUIRE EXACT MATCH BINDING:             ┃
┃ ✗ Proxy uses static registration   ┃ ✓ Exact MCP Client ID                    ┃
┃ ✗ Reused/static consent cookies    ┃ ✓ Exact redirect_uri                     ┃
┃ ✗ Loose scope matching             ┃ ✓ Exact requested scopes & state         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                        │
════════════════════════════════════════╧════════════════════════════════════════
[ PROTOCOL BOUNDARY / TRANSPORT ]       │   (stdio / HTTP SSE)
                                        │
[ UNTRUSTED INPUT ]                     │   (URLs, IDs, Tokens, Sessions)
       Must NEVER auto-become...        │   ...Only explicit controls cross line
[ TRUSTED AUTHORITY ]                   ▼   (Approved Clients, Identities, Procs)
════════════════════════════════════════╤════════════════════════════════════════
                                        │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ DOOR 3: TOKEN TERMINATION ("Who is this token really for?")                   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ REJECT (Passthrough Collapse):     ┃ REQUIRE (Trust Termination):             ┃
┃ ✗ Relaying client token upstream   ┃ ✓ Downstream trusts THIS server's tokens ┃
┃ ✗ Blind pipe architecture          ┃ ✓ Token audience must be THIS server     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                        │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ DOOR 4: SESSION & IDENTITY ("Am I trusting a handle as an identity?")         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ REJECT (Session Hijack):           ┃ REQUIRE:                                 ┃
┃ ✗ session_id treated as Identity   ┃ ✓ Session is random, scoped, expiring    ┃
┃ ✗ Authz via session_id alone       ┃ ✓ Every request explicitly authorized    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                        │
                                        ▼
                             ┌────────────────────┐
                             │     MCP SERVER     │
                             └──────────┬─────────┘
                                        │
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━▼━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ DOOR 6: SCOPES & CAPABILITIES ("What blast radius is allowed?")               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ REJECT (Overbroad Blast Radius):   ┃ REQUIRE (Least Privilege):               ┃
┃ ✗ Asking for everything up front   ┃ ✓ Start narrow, elevate later            ┃
┃ ✗ Endless, unexpiring power        ┃ ✓ Ask again for sensitive tool actions   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                   ┌─────────┐    ┌─────────┐    ┌─────────┐
                   │ PROMPTS │    │RESOURCES│    │  TOOLS  │
                   │(Context)│    │ (Data)  │    │(Actions)│
                   └─────────┘    └─────────┘    └─────────┘